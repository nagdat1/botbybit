#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تيليغرام للتداول على منصة Bybit
يدعم التداول الحقيقي والتجريبي الداخلي مع حسابات الفيوتشر المطورة
"""

import logging
import asyncio
import json
import time
import threading
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Any, Union
import hashlib
import hmac
import requests
from urllib.parse import urlencode

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import threading

# استيراد الإعدادات من ملف منفصل
from config import *

# استيراد إدارة المستخدمين وقاعدة البيانات
from database import db_manager
from user_manager import user_manager

# استيراد نظام المطورين
from developer_manager import developer_manager
import init_developers

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    handlers=[
        logging.FileHandler(LOGGING_SETTINGS['log_file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FuturesPosition:
    """فئة لإدارة صفقات الفيوتشر"""
    
    def __init__(self, symbol: str, side: str, margin_amount: float, entry_price: float, leverage: int, position_id: str):
        self.position_id = position_id
        self.symbol = symbol
        self.side = side.lower()  # buy أو sell
        self.leverage = leverage
        self.entry_price = entry_price
        self.margin_amount = margin_amount  # الهامش المحجوز
        self.position_size = margin_amount * leverage  # حجم الصفقة الفعلي
        self.contracts = self.position_size / entry_price  # عدد العقود
        self.timestamp = datetime.now()
        self.unrealized_pnl = 0.0
        self.maintenance_margin_rate = 0.005  # 0.5% كمعدل افتراضي
        self.liquidation_price = self.calculate_liquidation_price()
        
    def calculate_liquidation_price(self) -> float:
        """حساب سعر التصفية باستخدام الصيغ الصحيحة مثل المنصات"""
        try:
            # استخدام الصيغة الصحيحة لـ Bybit
            # Liquidation Price = Entry Price * (1 - (1/leverage) + maintenance_margin_rate) for Long
            # Liquidation Price = Entry Price * (1 + (1/leverage) - maintenance_margin_rate) for Short
            
            if self.side == "buy":
                # للصفقات الشرائية (Long)
                # الصيغة: Entry * (1 - (1/leverage) + maintenance_margin_rate)
                liquidation_price = self.entry_price * (1 - (1/self.leverage) + self.maintenance_margin_rate)
            else:
                # للصفقات البيعية (Short)  
                # الصيغة: Entry * (1 + (1/leverage) - maintenance_margin_rate)
                liquidation_price = self.entry_price * (1 + (1/self.leverage) - self.maintenance_margin_rate)
            
            # التأكد من أن السعر موجب
            return max(liquidation_price, 0.000001)
            
        except Exception as e:
            logger.error(f"خطأ في حساب سعر التصفية: {e}")
            # في حالة الخطأ، استخدام حسابات تقريبية آمنة
            if self.side == "buy":
                return self.entry_price * (1 - (1/self.leverage) * 0.8)  # 80% من الهامش
            else:
                return self.entry_price * (1 + (1/self.leverage) * 0.8)  # 80% من الهامش
    
    def update_pnl(self, current_price: float) -> float:
        """تحديث الربح/الخسارة غير المحققة"""
        try:
            if self.side == "buy":
                # للصفقات الشرائية
                self.unrealized_pnl = (current_price - self.entry_price) * self.contracts
            else:
                # للصفقات البيعية
                self.unrealized_pnl = (self.entry_price - current_price) * self.contracts
            
            return self.unrealized_pnl
            
        except Exception as e:
            logger.error(f"خطأ في تحديث PnL: {e}")
            return 0.0
    
    def calculate_closing_pnl(self, closing_price: float) -> float:
        """حساب الربح/الخسارة المحققة عند الإغلاق"""
        try:
            if self.side == "buy":
                realized_pnl = (closing_price - self.entry_price) * self.contracts
            else:
                realized_pnl = (self.entry_price - closing_price) * self.contracts
            
            return realized_pnl
            
        except Exception as e:
            logger.error(f"خطأ في حساب PnL المحقق: {e}")
            return 0.0
    
    def check_liquidation(self, current_price: float) -> bool:
        """فحص ما إذا كانت الصفقة تحتاج للتصفية"""
        try:
            if self.side == "buy":
                return current_price <= self.liquidation_price
            else:
                return current_price >= self.liquidation_price
        except Exception as e:
            logger.error(f"خطأ في فحص التصفية: {e}")
            return False
    
    def get_position_info(self) -> Dict:
        """الحصول على معلومات الصفقة"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'leverage': self.leverage,
            'entry_price': self.entry_price,
            'margin_amount': self.margin_amount,
            'position_size': self.position_size,
            'contracts': self.contracts,
            'liquidation_price': self.liquidation_price,
            'unrealized_pnl': self.unrealized_pnl,
            'timestamp': self.timestamp
        }

class TradingAccount:
    """فئة لإدارة الحسابات التجريبية الداخلية مع دعم محسن للفيوتشر"""
    
    def __init__(self, initial_balance: float = 10000.0, account_type: str = "spot"):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.account_type = account_type
        self.positions: Dict[str, Union[FuturesPosition, Dict]] = {}
        self.trade_history: List[Dict] = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.margin_locked = 0.0  # الهامش المحجوز
        
    def get_available_balance(self) -> float:
        """الحصول على الرصيد المتاح (الرصيد الكلي - الهامش المحجوز)"""
        return self.balance - self.margin_locked
    
    def open_futures_position(self, symbol: str, side: str, margin_amount: float, price: float, leverage: int = 1) -> tuple[bool, str]:
        """فتح صفقة فيوتشر جديدة"""
        try:
            available_balance = self.get_available_balance()
            
            if available_balance < margin_amount:
                return False, f"الرصيد غير كافي. متاح: {available_balance:.2f}, مطلوب: {margin_amount:.2f}"
            
            # إنشاء معرف فريد لل صفقة
            position_id = f"{symbol}_{int(time.time() * 1000000)}"
            
            # إنشاء صفقة جديدة
            position = FuturesPosition(
                symbol=symbol,
                side=side,
                margin_amount=margin_amount,
                entry_price=price,
                leverage=leverage,
                position_id=position_id
            )
            
            # حجز الهامش
            self.margin_locked += margin_amount
            self.positions[position_id] = position
            
            logger.info(f"تم فتح صفقة فيوتشر: {symbol} {side} {margin_amount} برافعة {leverage}x, ID: {position_id}")
            return True, position_id
            
        except Exception as e:
            logger.error(f"خطأ في فتح صفقة الفيوتشر: {e}")
            return False, str(e)
    
    def open_spot_position(self, symbol: str, side: str, amount: float, price: float) -> tuple[bool, str]:
        """فتح صفقة سبوت"""
        try:
            if self.get_available_balance() < amount:
                return False, "الرصيد غير كافي"
            
            position_id = f"{symbol}_{int(time.time() * 1000000)}"
            
            # في السبوت، نشتري الأصل مباشرة
            contracts = amount / price
            
            # حجز المبلغ كاملاً
            self.balance -= amount
            
            # حفظ معلومات الصفقة
            position_info = {
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'leverage': 1,
                'market_type': 'spot',
                'timestamp': datetime.now(),
                'contracts': contracts,
                'unrealized_pnl': 0.0
            }
            
            self.positions[position_id] = position_info
            
            logger.info(f"تم فتح صفقة سبوت: {symbol} {side} {amount}, ID: {position_id}")
            return True, position_id
            
        except Exception as e:
            logger.error(f"خطأ في فتح صفقة السبوت: {e}")
            return False, str(e)
    
    def close_futures_position(self, position_id: str, closing_price: float) -> tuple[bool, dict]:
        """إغلاق صفقة فيوتشر"""
        try:
            if position_id not in self.positions:
                return False, {"error": "ال صفقة غير موجودة"}
            
            position = self.positions[position_id]
            
            if not isinstance(position, FuturesPosition):
                return False, {"error": "ال صفقة ليست صفقة فيوتشر"}
            
            # حساب الربح/الخسارة المحققة
            realized_pnl = position.calculate_closing_pnl(closing_price)
            
            # إرجاع الهامش + الربح/الخسارة
            self.margin_locked -= position.margin_amount
            self.balance += position.margin_amount + realized_pnl
            
            # تسجيل الصفقة في التاريخ
            trade_record = {
                'symbol': position.symbol,
                'side': position.side,
                'entry_price': position.entry_price,
                'closing_price': closing_price,
                'margin_amount': position.margin_amount,
                'position_size': position.position_size,
                'leverage': position.leverage,
                'market_type': 'futures',
                'contracts': position.contracts,
                'pnl': realized_pnl,
                'liquidation_price': position.liquidation_price,
                'timestamp': position.timestamp,
                'close_timestamp': datetime.now()
            }
            
            self.trade_history.append(trade_record)
            self.total_trades += 1
            
            if realized_pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            # حذف الصفقة
            del self.positions[position_id]
            
            logger.info(f"تم إغلاق صفقة فيوتشر: {position.symbol} PnL: {realized_pnl:.2f}")
            return True, trade_record
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق صفقة الفيوتشر: {e}")
            return False, {"error": str(e)}
    
    def close_spot_position(self, position_id: str, closing_price: float) -> tuple[bool, dict]:
        """إغلاق صفقة سبوت"""
        try:
            if position_id not in self.positions:
                return False, {"error": "ال صفقة غير موجودة"}
            
            position = self.positions[position_id]
            
            if isinstance(position, FuturesPosition):
                return False, {"error": "ال صفقة ليست صفقة سبوت"}
            
            entry_price = position['price']
            amount = position['amount']
            side = position['side']
            contracts = position.get('contracts', amount / entry_price)
            
            # حساب الربح/الخسارة
            if side.lower() == "buy":
                # بيع الأصل المشترى
                self.balance += contracts * closing_price
                pnl = contracts * closing_price - amount
            else:
                # تغطية البيع (نادر في السبوت)
                pnl = (entry_price - closing_price) * contracts
                self.balance += amount + pnl
            
            # تسجيل الصفقة
            trade_record = {
                'symbol': position['symbol'],
                'side': side,
                'entry_price': entry_price,
                'closing_price': closing_price,
                'amount': amount,
                'leverage': 1,
                'market_type': 'spot',
                'contracts': contracts,
                'pnl': pnl,
                'timestamp': position['timestamp'],
                'close_timestamp': datetime.now()
            }
            
            self.trade_history.append(trade_record)
            self.total_trades += 1
            
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            del self.positions[position_id]
            
            logger.info(f"تم إغلاق صفقة سبوت: {position['symbol']} PnL: {pnl:.2f}")
            return True, trade_record
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق صفقة السبوت: {e}")
            return False, {"error": str(e)}
    
    def update_positions_pnl(self, prices: Dict[str, float]):
        """تحديث الربح/الخسارة غير المحققة لجميع الصفقات"""
        try:
            for position_id, position in self.positions.items():
                if isinstance(position, FuturesPosition):
                    # صفقة فيوتشر
                    current_price = prices.get(position.symbol)
                    if current_price:
                        position.update_pnl(current_price)
                        
                        # فحص التصفية
                        if position.check_liquidation(current_price):
                            logger.warning(f"تحذير: صفقة {position.symbol} قريبة من التصفية!")
                elif isinstance(position, dict) and position.get('market_type') == 'spot':
                    # صفقة سبوت
                    current_price = prices.get(position['symbol'])
                    if current_price:
                        entry_price = position['price']
                        amount = position.get('amount', 0)
                        side = position['side']
                        
                        # حساب العقود بناءً على المبلغ والسعر
                        contracts = amount / entry_price if entry_price > 0 else 0
                        position['contracts'] = contracts
                        
                        if side.lower() == "buy":
                            unrealized_pnl = (current_price - entry_price) * contracts
                        else:
                            unrealized_pnl = (entry_price - current_price) * contracts
                        
                        position['unrealized_pnl'] = unrealized_pnl
                        position['current_price'] = current_price  # حفظ السعر الحالي
                        
        except Exception as e:
            logger.error(f"خطأ في تحديث PnL: {e}")
    
    def get_total_unrealized_pnl(self) -> float:
        """الحصول على مجموع الربح/الخسارة غير المحققة"""
        total_pnl = 0.0
        for position in self.positions.values():
            if isinstance(position, FuturesPosition):
                total_pnl += position.unrealized_pnl
            elif isinstance(position, dict):
                total_pnl += position.get('unrealized_pnl', 0.0)
        return total_pnl
    
    def get_margin_ratio(self) -> float:
        """حساب نسبة الهامش"""
        try:
            if self.margin_locked == 0:
                return float('inf')
            
            equity = self.balance + self.get_total_unrealized_pnl()
            return equity / self.margin_locked
        except:
            return float('inf')
    
    def update_balance(self, new_balance: float):
        """تحديث رصيد الحساب"""
        self.balance = new_balance
        self.initial_balance = new_balance
        
    def reset_account(self):
        """إعادة تعيين الحساب"""
        self.balance = self.initial_balance
        self.positions = {}
        self.trade_history = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.margin_locked = 0.0
    
    def get_account_info(self) -> Dict:
        """الحصول على معلومات الحساب"""
        total_unrealized_pnl = self.get_total_unrealized_pnl()
        available_balance = self.get_available_balance()
        equity = self.balance + total_unrealized_pnl
        margin_ratio = self.get_margin_ratio()
        
        return {
            'balance': round(self.balance, 2),
            'available_balance': round(available_balance, 2),
            'margin_locked': round(self.margin_locked, 2),
            'equity': round(equity, 2),
            'initial_balance': self.initial_balance,
            'unrealized_pnl': round(total_unrealized_pnl, 2),
            'margin_ratio': round(margin_ratio, 2) if margin_ratio != float('inf') else '∞',
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round((self.winning_trades / max(self.total_trades, 1)) * 100, 2),
            'open_positions': len(self.positions)
        }

class BybitAPI:
    """فئة للتعامل مع Bybit API"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bybit.com"
        
    def _generate_signature(self, params: dict, timestamp: str) -> str:
        """إنشاء التوقيع للطلبات"""
        param_str = timestamp + self.api_key + "5000" + urlencode(sorted(params.items()))
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        """إرسال طلب إلى API"""
        try:
            url = f"{self.base_url}{endpoint}"
            timestamp = str(int(time.time() * 1000))
            
            if params is None:
                params = {}
            
            signature = self._generate_signature(params, timestamp)
            
            headers = {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-SIGN": signature,
                "X-BAPI-SIGN-TYPE": "2",
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": "5000",
                "Content-Type": "application/json"
            }
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=params, headers=headers, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"خطأ في طلب API: {e}")
            return {"retCode": -1, "retMsg": str(e)}
        except Exception as e:
            logger.error(f"خطأ غير متوقع في API: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_all_symbols(self, category: str = "spot") -> List[dict]:
        """الحصول على جميع الرموز المتاحة"""
        try:
            endpoint = "/v5/market/instruments-info"
            # تحويل futures إلى linear للتوافق مع Bybit API
            api_category = "linear" if category == "futures" else category
            params = {"category": api_category}
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                result = response.get("result", {})
                symbols = result.get("list", [])
                return symbols
            
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الرموز: {e}")
            return []
    
    def get_ticker_price(self, symbol: str, category: str = "spot") -> Optional[float]:
        """الحصول على سعر الرمز الحالي"""
        try:
            endpoint = "/v5/market/tickers"
            # تحويل futures إلى linear للتوافق مع Bybit API
            api_category = "linear" if category == "futures" else category
            params = {"category": api_category, "symbol": symbol}
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                result = response.get("result", {})
                ticker_list = result.get("list", [])
                if ticker_list:
                    return float(ticker_list[0].get("lastPrice", 0))
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر: {e}")
            return None
    
    def check_symbol_exists(self, symbol: str, category: str = "spot") -> bool:
        """التحقق من وجود الرمز في المنصة"""
        try:
            price = self.get_ticker_price(symbol, category)
            return price is not None and price > 0
        except Exception as e:
            logger.error(f"خطأ في التحقق من الرمز: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, price: Optional[str] = None, category: str = "spot") -> dict:
        """وضع أمر تداول"""
        try:
            endpoint = "/v5/order/create"
            
            params = {
                "category": category,
                "symbol": symbol,
                "side": side.capitalize(),
                "orderType": order_type,
                "qty": qty
            }
            
            if price and order_type.lower() == "limit":
                params["price"] = price
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في وضع الأمر: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_account_balance(self, account_type: str = "UNIFIED") -> dict:
        """الحصول على رصيد الحساب"""
        try:
            endpoint = "/v5/account/wallet-balance"
            params = {"accountType": account_type}
            
            response = self._make_request("GET", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الرصيد: {e}")
            return {"retCode": -1, "retMsg": str(e)}

class TradingBot:
    """فئة البوت الرئيسية مع دعم محسن للفيوتشر"""
    
    def __init__(self):
        # إعداد API
        self.bybit_api = None
        if BYBIT_API_KEY and BYBIT_API_SECRET:
            self.bybit_api = BybitAPI(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # إعداد الحسابات التجريبية
        self.demo_account_spot = TradingAccount(
            initial_balance=DEMO_ACCOUNT_SETTINGS['initial_balance_spot'],
            account_type='spot'
        )
        self.demo_account_futures = TradingAccount(
            initial_balance=DEMO_ACCOUNT_SETTINGS['initial_balance_futures'],
            account_type='futures'
        )
        
        # حالة البوت
        self.is_running = True
        self.signals_received = 0
        
        # إعدادات المستخدم
        self.user_settings = DEFAULT_SETTINGS.copy()
        self.user_id = None  # معرّف المستخدم الحالي (يُستخدم للإشارات الشخصية)
        
        # قائمة الصفقات المفتوحة (مرتبطة بحسابات المستخدم)
        self.open_positions = {}  # {position_id: position_info}
        
        # قائمة الأزواج المتاحة (cache)
        self.available_pairs = {
            'spot': [],
            'futures': [],
            'inverse': []
        }
        self.last_pairs_update = 0
        
    def get_current_account(self):
        """الحصول على الحساب الحالي حسب نوع السوق"""
        if self.user_settings['market_type'] == 'spot':
            return self.demo_account_spot
        else:
            return self.demo_account_futures
    
    async def update_available_pairs(self, force_update=False):
        """تحديث قائمة الأزواج المتاحة"""
        try:
            current_time = time.time()
            # تحديث كل 30 دقيقة
            if not force_update and (current_time - self.last_pairs_update) < 1800:
                return
            
            if not self.bybit_api:
                logger.error("API غير متاح")
                return
                
            # جلب أزواج السبوت
            spot_symbols = self.bybit_api.get_all_symbols("spot")
            self.available_pairs['spot'] = [s['symbol'] for s in spot_symbols if s.get('status') == 'Trading']
            
            # جلب أزواج الفيوتشر
            futures_symbols = self.bybit_api.get_all_symbols("linear")
            self.available_pairs['futures'] = [s['symbol'] for s in futures_symbols if s.get('status') == 'Trading']
            
            # جلب أزواج inverse
            inverse_symbols = self.bybit_api.get_all_symbols("inverse")
            self.available_pairs['inverse'] = [s['symbol'] for s in inverse_symbols if s.get('status') == 'Trading']
            
            self.last_pairs_update = current_time
            logger.info(f"تم تحديث الأزواج: Spot={len(self.available_pairs['spot'])}, Futures={len(self.available_pairs['futures'])}, Inverse={len(self.available_pairs['inverse'])}")
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الأزواج: {e}")
    
    async def update_open_positions_prices(self):
        """تحديث أسعار الصفقات المفتوحة"""
        try:
            if not self.open_positions:
                return
            
            # جمع الرموز الفريدة من الصفقات المفتوحة مع نوع السوق
            symbols_to_update = {}  # {symbol: market_type}
            for position_info in self.open_positions.values():
                symbol = position_info['symbol']
                market_type = position_info.get('account_type', 'spot')
                symbols_to_update[symbol] = market_type
            
            # الحصول على الأسعار الحالية
            current_prices = {}
            for symbol, market_type in symbols_to_update.items():
                if self.bybit_api:
                    category = "linear" if market_type == "futures" else "spot"
                    price = self.bybit_api.get_ticker_price(symbol, category)
                    if price:
                        current_prices[symbol] = price
            
            # تحديث الصفقات في الحسابات التجريبية
            if current_prices:
                # تحديث صفقات السبوت
                spot_prices = {k: v for k, v in current_prices.items() 
                              if symbols_to_update.get(k) == 'spot'}
                if spot_prices:
                    self.demo_account_spot.update_positions_pnl(spot_prices)
                
                # تحديث صفقات الفيوتشر
                futures_prices = {k: v for k, v in current_prices.items() 
                                 if symbols_to_update.get(k) == 'futures'}
                if futures_prices:
                    self.demo_account_futures.update_positions_pnl(futures_prices)
                
                # تحديث الصفقات في القائمة العامة
                for position_id, position_info in self.open_positions.items():
                    symbol = position_info['symbol']
                    if symbol in current_prices:
                        position_info['current_price'] = current_prices[symbol]
                        
                        # حساب الربح/الخسارة
                        entry_price = position_info['entry_price']
                        current_price = current_prices[symbol]
                        side = position_info['side']
                        
                        if side.lower() == "buy":
                            pnl_percent = ((current_price - entry_price) / entry_price) * 100
                        else:
                            pnl_percent = ((entry_price - current_price) / entry_price) * 100
                        
                        position_info['pnl_percent'] = pnl_percent
                        
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الصفقات: {e}")
    
    def get_available_pairs_message(self, category=None, brief=False, limit=50):
        """الحصول على رسالة الأزواج المتاحة"""
        try:
            if category is None:
                category = self.user_settings['market_type']
                
            # تحويل من futures إلى linear
            api_category = category
            
            pairs = self.available_pairs.get(api_category, [])
            
            if not pairs:
                return f"❌ لا توجد أزواج متاحة في {category.upper()}"
            
            if brief:
                # رسالة موجزة بأهم الأزواج فقط
                top_pairs = pairs[:20]
                pairs_text = ", ".join(top_pairs)
                return f"💱 أهم أزواج {category.upper()}:\n{pairs_text}\n\n📊 المجموع: {len(pairs)} زوج متاح"
            else:
                # رسالة مفصلة
                pairs_to_show = pairs[:limit]
                pairs_text = ""
                for i, pair in enumerate(pairs_to_show, 1):
                    pairs_text += f"{i}. {pair}\n"
                    if i % 20 == 0:  # فاصل كل 20 زوج
                        pairs_text += "\n"
                
                title = f"📊 أزواج {category.upper()} المتاحة"
                message = f"{title}\n{'='*30}\n\n{pairs_text}"
                
                if len(pairs) > limit:
                    message += f"\n... و {len(pairs) - limit} أزواج أخرى"
                
                message += f"\n\n📈 إجمالي الأزواج: {len(pairs)}"
                return message
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على الأزواج: {e}")
            return "❌ خطأ في الحصول على الأزواج"
    
    async def broadcast_signal_to_followers(self, signal_data: dict, developer_id: int):
        """إرسال إشارة المطور لجميع المتابعين"""
        try:
            # الحصول على قائمة المتابعين
            followers = developer_manager.get_followers(developer_id)
            
            if not followers:
                logger.info("لا يوجد متابعين لإرسال الإشارة")
                return
            
            logger.info(f"📡 إرسال إشارة المطور إلى {len(followers)} متابع")
            
            # إرسال الإشارة لكل متابع
            success_count = 0
            for follower_id in followers:
                try:
                    # التحقق من وجود المتابع في UserManager
                    if not user_manager.get_user(follower_id):
                        logger.warning(f"⚠️ المتابع {follower_id} غير موجود")
                        continue
                    
                    # إنشاء TradingBot مؤقت للمتابع
                    follower_bot = TradingBot()
                    follower_bot.user_id = follower_id
                    
                    # الحصول على إعدادات المتابع
                    follower_settings = user_manager.get_user_settings(follower_id)
                    if follower_settings:
                        follower_bot.user_settings = follower_settings
                    
                    # تنفيذ الإشارة على حساب المتابع
                    await follower_bot.process_signal(signal_data.copy())
                    success_count += 1
                    logger.info(f"✅ تم إرسال الإشارة للمتابع {follower_id}")
                    
                    # إرسال إشعار للمتابع
                    try:
                        from telegram import Bot
                        bot = Bot(token=TELEGRAM_TOKEN)
                        notification_message = f"""
📡 إشارة جديدة من Nagdat!

📊 الرمز: {signal_data.get('symbol', 'N/A')}
🔄 الإجراء: {signal_data.get('action', 'N/A').upper()}
💲 السعر: {signal_data.get('price', 'N/A')}

⚡ تم تنفيذ الصفقة تلقائياً على حسابك!
                        """
                        await bot.send_message(
                            chat_id=follower_id,
                            text=notification_message
                        )
                    except Exception as notify_error:
                        logger.error(f"خطأ في إرسال الإشعار للمتابع {follower_id}: {notify_error}")
                        
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال الإشارة للمتابع {follower_id}: {e}")
            
            # إرسال تقرير للمطور
            message = f"""
📡 تم توزيع الإشارة

✅ تم الإرسال: {success_count} من {len(followers)}
📊 التفاصيل:
• الرمز: {signal_data.get('symbol', 'N/A')}
• الإجراء: {signal_data.get('action', 'N/A').upper()}
            """
            await self.send_message_to_admin(message)
            
            return {
                'success': True,
                'sent_to': success_count,
                'total_followers': len(followers)
            }
            
        except Exception as e:
            logger.error(f"خطأ في broadcast_signal_to_followers: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_signal(self, signal_data: dict):
        """معالجة إشارة التداول مع دعم محسن للفيوتشر"""
        try:
            self.signals_received += 1
            
            if not self.is_running:
                logger.info("البوت متوقف، تم تجاهل الإشارة")
                return
            
            symbol = signal_data.get('symbol', '').upper()
            action = signal_data.get('action', '').lower()  # buy أو sell
            
            if not symbol or not action:
                logger.error("بيانات الإشارة غير مكتملة")
                return
            
            # 🔥 ميزة جديدة: إذا كان المستخدم هو مطور وفعّل التوزيع التلقائي
            # سيتم إرسال الإشارة لجميع المتابعين
            if developer_manager.is_developer(self.user_id):
                # التحقق من تفعيل التوزيع التلقائي من قاعدة البيانات
                auto_broadcast_enabled = db_manager.get_auto_broadcast_status(self.user_id)
                
                if auto_broadcast_enabled:
                    try:
                        logger.info(f"📡 التوزيع التلقائي مفعّل للمطور {self.user_id}")
                        
                        # حفظ الإشارة في قاعدة البيانات أولاً
                        signal_saved = db_manager.create_developer_signal(
                            developer_id=self.user_id,
                            signal_data=signal_data
                        )
                        
                        if signal_saved:
                            # إرسال للمتابعين
                            await self.broadcast_signal_to_followers(signal_data, self.user_id)
                        else:
                            logger.error("فشل في حفظ إشارة المطور")
                            
                    except Exception as e:
                        logger.error(f"خطأ في معالجة إشارة المطور: {e}")
                else:
                    logger.info(f"التوزيع التلقائي غير مفعّل للمطور {self.user_id}")
            
            # تحديث الأزواج إذا لزم الأمر
            await self.update_available_pairs()
            
            # تحديد نوع السوق بناءً على إعدادات المستخدم
            user_market_type = self.user_settings['market_type']
            bybit_category = "spot" if user_market_type == "spot" else "linear"
            market_type = user_market_type
            
            # التحقق من وجود الرمز في الفئة المحددة من قبل المستخدم
            symbol_found = False
            
            if user_market_type == "spot" and symbol in self.available_pairs.get('spot', []):
                symbol_found = True
            elif user_market_type == "futures" and (symbol in self.available_pairs.get('futures', []) or symbol in self.available_pairs.get('inverse', [])):
                symbol_found = True
                # تحديد الفئة الصحيحة للفيوتشر
                if symbol in self.available_pairs.get('inverse', []):
                    bybit_category = "inverse"
            
            if not symbol_found:
                # جمع الأزواج المتاحة للنوع المحدد
                available_pairs = self.available_pairs.get(user_market_type, [])
                if user_market_type == "futures":
                    # إضافة أزواج inverse أيضاً للفيوتشر
                    available_pairs = self.available_pairs.get('futures', []) + self.available_pairs.get('inverse', [])
                
                # عرض أول 20 زوج
                pairs_list = ", ".join(available_pairs[:20])
                error_message = f"❌ الرمز {symbol} غير موجود في نوع السوق المحدد ({user_market_type.upper()})!\n\n📋 الأزواج المتاحة:\n{pairs_list}"
                await self.send_message_to_admin(error_message)
                return
            
            # الحصول على السعر الحالي
            if self.bybit_api:
                current_price = self.bybit_api.get_ticker_price(symbol, bybit_category)
                if current_price is None:
                    await self.send_message_to_admin(f"❌ فشل في الحصول على سعر {symbol}")
                    return
            else:
                # استخدام سعر وهمي للاختبار
                current_price = 100.0
            
            # تنفيذ الصفقة حسب نوع الحساب
            if self.user_settings['account_type'] == 'real':
                await self.execute_real_trade(symbol, action, current_price, bybit_category)
            else:
                await self.execute_demo_trade(symbol, action, current_price, bybit_category, market_type)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            await self.send_message_to_admin(f"❌ خطأ في معالجة الإشارة: {e}")
    
    async def execute_real_trade(self, symbol: str, action: str, price: float, category: str):
        """تنفيذ صفقة حقيقية"""
        try:
            if not self.bybit_api:
                await self.send_message_to_admin("❌ API غير متاح للتداول الحقيقي")
                return
                
            amount = str(self.user_settings['trade_amount'])
            side = "Buy" if action == "buy" else "Sell"
            
            response = self.bybit_api.place_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=amount,
                category=category
            )
            
            if response.get("retCode") == 0:
                order_id = response.get("result", {}).get("orderId", "")
                message = f"✅ تم تنفيذ أمر {action.upper()} للرمز {symbol}\n"
                message += f"💰 المبلغ: {amount}\n"
                message += f"💲 السعر: {price:.6f}\n"
                message += f"🏪 السوق: {category.upper()}\n"
                message += f"🆔 رقم الأمر: {order_id}"
                
                await self.send_message_to_admin(message)
            else:
                error_msg = response.get("retMsg", "خطأ غير محدد")
                await self.send_message_to_admin(f"❌ فشل في تنفيذ الأمر: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة الحقيقية: {e}")
            await self.send_message_to_admin(f"❌ خطأ في تنفيذ الصفقة الحقيقية: {e}")
    
    async def execute_demo_trade(self, symbol: str, action: str, price: float, category: str, market_type: str):
        """تنفيذ صفقة تجريبية داخلية مع دعم محسن للفيوتشر"""
        try:
            # اختيار الحساب الصحيح بناءً على إعدادات المستخدم وليس على نوع السوق المكتشف
            user_market_type = self.user_settings['market_type']
            logger.info(f"تنفيذ صفقة تجريبية: الرمز={symbol}, النوع={action}, نوع السوق={user_market_type}, user_id={self.user_id}")
            
            # تحديد الحساب والصفقات بناءً على نوع المستخدم
            if self.user_id:
                # استخدام حساب المستخدم من user_manager
                from user_manager import user_manager
                account = user_manager.get_user_account(self.user_id, user_market_type)
                if not account:
                    logger.error(f"لم يتم العثور على حساب للمستخدم {self.user_id}")
                    await self.send_message_to_user(self.user_id, f"❌ خطأ: لم يتم العثور على حساب {user_market_type}")
                    return
                # استخدام صفقات المستخدم
                user_positions = user_manager.user_positions.get(self.user_id, {})
                logger.info(f"استخدام حساب المستخدم {self.user_id} لنوع السوق {user_market_type}")
            else:
                # استخدام الحساب العام (للإشارات القديمة)
                if user_market_type == 'futures':
                    account = self.demo_account_futures
                else:
                    account = self.demo_account_spot
                user_positions = self.open_positions
                logger.info(f"استخدام الحساب العام لنوع السوق {user_market_type}")
            
            if user_market_type == 'futures':
                margin_amount = self.user_settings['trade_amount']  # مبلغ الهامش
                leverage = self.user_settings['leverage']
                
                success, result = account.open_futures_position(
                    symbol=symbol,
                    side=action,
                    margin_amount=margin_amount,
                    price=price,
                    leverage=leverage
                )
                
                if success:
                    position_id = result
                    position = account.positions[position_id]
                    
                    # التأكد من أن position هو FuturesPosition
                    if isinstance(position, FuturesPosition):
                        # حفظ معلومات الصفقة في قائمة المستخدم
                        user_positions[position_id] = {
                            'symbol': symbol,
                            'entry_price': price,
                            'side': action,
                            'account_type': user_market_type,
                            'leverage': leverage,
                            'category': category,
                            'margin_amount': margin_amount,
                            'position_size': position.position_size,
                            'liquidation_price': position.liquidation_price,
                            'contracts': position.contracts,
                            'current_price': price,
                            'pnl_percent': 0.0
                        }
                        
                        logger.info(f"تم فتح صفقة فيوتشر: ID={position_id}, الرمز={symbol}, user_id={self.user_id}")
                        
                        message = f"📈 تم فتح صفقة فيوتشر تجريبية\n"
                        if self.user_id:
                            message += f"👤 المستخدم: {self.user_id}\n"
                        message += f"📊 الرمز: {symbol}\n"
                        message += f"🔄 النوع: {action.upper()}\n"
                        message += f"💰 الهامش المحجوز: {margin_amount}\n"
                        message += f"📈 حجم الصفقة: {position.position_size:.2f}\n"
                        message += f"💲 سعر الدخول: {price:.6f}\n"
                        message += f"⚡ الرافعة: {leverage}x\n"
                        message += f"⚠️ سعر التصفية: {position.liquidation_price:.6f}\n"
                        message += f"📊 عدد العقود: {position.contracts:.6f}\n"
                        message += f"🆔 رقم الصفقة: {position_id}\n"
                        
                        # إضافة معلومات الحساب
                        account_info = account.get_account_info()
                        message += f"\n💰 الرصيد الكلي: {account_info['balance']:.2f}"
                        message += f"\n💳 الرصيد المتاح: {account_info['available_balance']:.2f}"
                        message += f"\n🔒 الهامش المحجوز: {account_info['margin_locked']:.2f}"
                        
                        await self.send_message_to_admin(message)
                    else:
                        await self.send_message_to_admin("❌ فشل في فتح صفقة الفيوتشر: نوع الصفقة غير صحيح")
                else:
                    await self.send_message_to_admin(f"❌ فشل في فتح صفقة الفيوتشر: {result}")
                    
            else:  # spot
                amount = self.user_settings['trade_amount']
                
                success, result = account.open_spot_position(
                    symbol=symbol,
                    side=action,
                    amount=amount,
                    price=price
                )
                
                if success:
                    position_id = result
                    
                    user_positions[position_id] = {
                        'symbol': symbol,
                        'entry_price': price,
                        'side': action,
                        'account_type': user_market_type,
                        'leverage': 1,
                        'category': category,
                        'amount': amount,
                        'current_price': price,
                        'pnl_percent': 0.0
                    }
                    
                    logger.info(f"تم فتح صفقة سبوت: ID={position_id}, الرمز={symbol}, user_id={self.user_id}")
                    
                    message = f"📈 تم فتح صفقة سبوت تجريبية\n"
                    if self.user_id:
                        message += f"👤 المستخدم: {self.user_id}\n"
                    message += f"📊 الرمز: {symbol}\n"
                    message += f"🔄 النوع: {action.upper()}\n"
                    message += f"💰 المبلغ: {amount}\n"
                    message += f"💲 سعر الدخول: {price:.6f}\n"
                    message += f"🏪 السوق: SPOT\n"
                    message += f"🆔 رقم الصفقة: {position_id}\n"
                    
                    # إضافة معلومات الحساب
                    account_info = account.get_account_info()
                    message += f"\n💰 الرصيد: {account_info['balance']:.2f}"
                    
                    await self.send_message_to_admin(message)
                else:
                    await self.send_message_to_admin(f"❌ فشل في فتح الصفقة التجريبية: {result}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة التجريبية: {e}")
            await self.send_message_to_admin(f"❌ خطأ في تنفيذ الصفقة التجريبية: {e}")
    
    async def send_message_to_admin(self, message: str):
        """إرسال رسالة للمدير أو المستخدم الحالي"""
        try:
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            # إرسال للمستخدم الحالي إذا كان محدداً، وإلا للأدمن
            chat_id = self.user_id if self.user_id else ADMIN_USER_ID
            await application.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة: {e}")
    
    async def send_message_to_user(self, user_id: int, message: str):
        """إرسال رسالة لمستخدم محدد"""
        try:
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            await application.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة للمستخدم {user_id}: {e}")

# إنشاء البوت العام
trading_bot = TradingBot()

# تهيئة مدير المستخدمين مع الفئات اللازمة
import user_manager as um_module
um_module.user_manager = um_module.UserManager(TradingAccount, BybitAPI)
user_manager = um_module.user_manager

# تحميل المستخدمين من قاعدة البيانات
user_manager.load_all_users()

# تهيئة نظام المطورين
try:
    # تشغيل init_developers
    init_developers.init_developers()
    logger.info("✅ تم تهيئة نظام المطورين بنجاح")
    
    # إعادة تحميل المطورين
    developer_manager.load_all_developers()
    
    # التأكد من إضافة المطور الرئيسي (ADMIN_USER_ID)
    dev_exists = db_manager.get_developer(ADMIN_USER_ID)
    
    if not dev_exists:
        logger.warning(f"⚠️ المطور الرئيسي غير موجود، سيتم إضافته الآن...")
        success = db_manager.create_developer(
            developer_id=ADMIN_USER_ID,
            developer_name="Nagdat",
            developer_key="NAGDAT-KEY-2024",
            webhook_url=None
        )
        if success:
            # إعادة تحميل المطورين
            developer_manager.load_all_developers()
            logger.info(f"✅ تم إضافة المطور الرئيسي: {ADMIN_USER_ID}")
        else:
            logger.error(f"❌ فشل في إضافة المطور الرئيسي")
    else:
        logger.info(f"✅ المطور الرئيسي موجود: {ADMIN_USER_ID}")
        
except Exception as e:
    logger.error(f"❌ خطأ في تهيئة نظام المطورين: {e}")
    import traceback
    traceback.print_exc()
    
    # محاولة إنشاء المطور مباشرة إذا فشل كل شيء
    try:
        logger.info("محاولة إنشاء المطور مباشرة...")
        db_manager.create_developer(
            developer_id=ADMIN_USER_ID,
            developer_name="Nagdat",
            developer_key="NAGDAT-KEY-2024",
            webhook_url=None
        )
        developer_manager.load_all_developers()
        logger.info("✅ تم إنشاء المطور بنجاح (المحاولة الثانية)")
    except Exception as e2:
        logger.error(f"❌ فشلت المحاولة الثانية: {e2}")

# تعيين لتتبع حالة إدخال المستخدم
user_input_state = {}

# ==================== وظائف التحقق من API ====================

async def check_api_connection(api_key: str, api_secret: str) -> bool:
    """التحقق من صحة API keys"""
    try:
        if not api_key or not api_secret:
            return False
        
        # إنشاء API مؤقت للتحقق
        temp_api = BybitAPI(api_key, api_secret)
        
        # محاولة الحصول على معلومات الحساب
        account_info = await temp_api.get_account_balance()
        
        # إذا تم الحصول على معلومات الحساب بنجاح
        if account_info and 'retCode' in account_info:
            return account_info['retCode'] == 0
        
        return False
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من API: {e}")
        return False

def get_api_status_indicator(api_key: str, api_secret: str, is_valid: bool = None) -> str:
    """الحصول على مؤشر بصري لحالة API"""
    if not api_key or not api_secret:
        return "🔴 غير مرتبط"
    
    if is_valid is None:
        return "🟡 جاري التحقق..."
    elif is_valid:
        return "🟢 مرتبط وصحيح"
    else:
        return "🔴 مرتبط ولكن غير صحيح"

# ==================== وظائف المطورين ====================

async def show_developer_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض لوحة تحكم المطور"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    developer_id = user_id
    
    # محاولة الحصول على معلومات المطور
    try:
        dev_info = developer_manager.get_developer(developer_id)
        
        if not dev_info:
            # إضافة المطور تلقائياً
            logger.info(f"إضافة المطور {developer_id} تلقائياً...")
            try:
                success = db_manager.create_developer(
                    developer_id=developer_id,
                    developer_name=update.effective_user.first_name or "Nagdat",
                    developer_key=f"DEV-KEY-{developer_id}",
                    webhook_url=None
                )
                
                if success:
                    # إعادة تحميل معلومات المطور
                    developer_manager.load_all_developers()
                    dev_info = developer_manager.get_developer(developer_id)
                    logger.info(f"✅ تم إضافة المطور {developer_id} بنجاح")
            except Exception as e:
                logger.error(f"خطأ في إنشاء المطور: {e}")
        
        # الحصول على إحصائيات المطور (مع قيم افتراضية)
        try:
            stats = developer_manager.get_developer_statistics(developer_id)
        except:
            stats = {
                'follower_count': 0,
                'total_signals': 0,
                'is_active': True,
                'can_broadcast': True
            }
        
    except Exception as e:
        logger.error(f"خطأ في show_developer_panel: {e}")
        # استخدام قيم افتراضية
        dev_info = {'developer_name': 'Nagdat'}
        stats = {
            'follower_count': 0,
            'total_signals': 0,
            'is_active': True,
            'can_broadcast': True
        }
    
    # الحصول على عدد المستخدمين
    all_users = user_manager.get_all_active_users()
    total_users = len(all_users)
    
    # الحصول على حالة التوزيع التلقائي
    auto_broadcast = db_manager.get_auto_broadcast_status(developer_id)
    
    # بناء رسالة الإحصائيات
    message = f"""
👨‍💻 لوحة تحكم المطور - {dev_info['developer_name']}

📊 إحصائيات سريعة:
• 👥 إجمالي المستخدمين: {total_users}
• ⚡ متابعي Nagdat: {stats['follower_count']}
• 📡 الإشارات المرسلة: {stats['total_signals']}
• 🟢 الحالة: {'نشط' if stats['is_active'] else '🔴 غير نشط'}
• ✅ صلاحية البث: {'مفعلة' if stats['can_broadcast'] else '❌ معطلة'}
• 📡 التوزيع التلقائي: {'✅ مُفعّل' if auto_broadcast else '❌ مُعطّل'}

استخدم الأزرار أدناه للتحكم الكامل في البوت:
    """
    
    # إنشاء الأزرار
    keyboard = [
        [KeyboardButton("📡 إرسال إشارة"), KeyboardButton("👥 المتابعين")],
        [KeyboardButton("📊 إحصائيات المطور"), KeyboardButton("👥 إدارة المستخدمين")],
        [KeyboardButton("📱 إشعار جماعي"), KeyboardButton("⚙️ إعدادات المطور")],
        [KeyboardButton("🔄 تحديث"), KeyboardButton("👤 الوضع العادي")],
        [KeyboardButton("🔙 الرجوع لحساب المطور")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message)

async def handle_send_signal_developer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إرسال إشارة من المطور"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    
    if not developer_manager.can_broadcast_signals(user_id):
        if update.message:
            await update.message.reply_text("❌ ليس لديك صلاحية لإرسال إشارات")
        return
    
    # عرض نموذج إرسال الإشارة
    message = """
📡 إرسال إشارة للمتابعين

أرسل الإشارة بالصيغة التالية:

<code>SYMBOL:ACTION:PRICE</code>

مثال:
<code>BTCUSDT:BUY:50000</code>

أو استخدم الأزرار أدناه:
    """
    
    keyboard = [
        [InlineKeyboardButton("📈 BUY Bitcoin", callback_data="dev_signal_BTCUSDT_BUY")],
        [InlineKeyboardButton("📉 SELL Bitcoin", callback_data="dev_signal_BTCUSDT_SELL")],
        [InlineKeyboardButton("📈 BUY Ethereum", callback_data="dev_signal_ETHUSDT_BUY")],
        [InlineKeyboardButton("📉 SELL Ethereum", callback_data="dev_signal_ETHUSDT_SELL")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def handle_show_followers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المتابعين"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    followers = developer_manager.get_followers(user_id)
    
    if not followers:
        if update.message:
            await update.message.reply_text("📭 لا يوجد متابعين حالياً")
        return
    
    message = f"👥 قائمة المتابعين ({len(followers)} متابع)\n\n"
    
    # إنشاء أزرار لكل متابع مع خيار الإزالة
    keyboard = []
    
    for i, follower_id in enumerate(followers[:20], 1):  # عرض أول 20 متابع
        user = user_manager.get_user(follower_id)
        if user:
            status = "🟢" if user.get('is_active') else "🔴"
            message += f"{i}. {status} User ID: {follower_id}\n"
            # إضافة زر لإزالة هذا المتابع
            keyboard.append([InlineKeyboardButton(
                f"❌ إزالة {follower_id}", 
                callback_data=f"dev_remove_follower_{follower_id}"
            )])
        else:
            message += f"{i}. ⚪ User ID: {follower_id}\n"
    
    if len(followers) > 20:
        message += f"\n... و {len(followers) - 20} متابع آخرين"
    
    keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data="dev_show_followers")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup)

async def handle_developer_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات المطور المفصلة"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    stats = developer_manager.get_developer_statistics(user_id)
    dev_info = developer_manager.get_developer(user_id)
    
    # إحصائيات المستخدمين
    all_users = user_manager.get_all_active_users()
    total_users = len(db_manager.get_all_developers()) + len(all_users)
    active_users = len(all_users)
    
    message = f"""
📊 إحصائيات مفصلة - {dev_info['developer_name']}

👥 إحصائيات المتابعة:
• إجمالي المتابعين: {stats['follower_count']}
• المتابعين النشطين: {len([u for u in all_users if u['user_id'] in developer_manager.get_followers(user_id)])}

📡 إحصائيات الإشارات:
• إجمالي الإشارات المرسلة: {stats['total_signals']}
• متوسط الإشارات اليومية: {stats['total_signals'] / 30:.1f}

👤 إحصائيات المستخدمين:
• إجمالي المستخدمين: {total_users}
• المستخدمين النشطين: {active_users}
• معدل التفاعل: {(stats['follower_count'] / max(total_users, 1)) * 100:.1f}%

⚙️ حالة النظام:
• حالة المطور: {'🟢 نشط' if stats['is_active'] else '🔴 غير نشط'}
• صلاحية البث: {'✅ مفعلة' if stats['can_broadcast'] else '❌ معطلة'}
• آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 تحديث", callback_data="dev_stats")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)

# ==================== نهاية وظائف المطورين ====================

# وظائف البوت (نفس الوظائف السابقة مع تحديثات طفيفة)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت مع دعم تعدد المستخدمين"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو المطور
    # استخدام ADMIN_USER_ID مباشرة من config.py
    is_admin = (user_id == ADMIN_USER_ID)
    
    # إذا كان المستخدم هو ADMIN، عرض القائمة الرئيسية مع زر المطور
    if is_admin:
        # عرض القائمة الرئيسية للمطور مع زر الرجوع لحساب المطور
        keyboard = [
            [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("📊 حالة الحساب")],
            [KeyboardButton("🔄 الصفقات المفتوحة"), KeyboardButton("📈 تاريخ التداول")],
            [KeyboardButton("💰 المحفظة"), KeyboardButton("📊 إحصائيات")],
            [KeyboardButton("🔙 الرجوع لحساب المطور")]
        ]
        
        # إضافة أزرار إضافية إذا كان المطور نشطاً
        user_data = user_manager.get_user(user_id)
        if user_data and user_data.get('is_active'):
            keyboard.append([KeyboardButton("⏹️ إيقاف البوت")])
        else:
            keyboard.append([KeyboardButton("▶️ تشغيل البوت")])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # إنشاء رابط webhook الشخصي للمطور
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if railway_url:
            if not railway_url.startswith('http'):
                railway_url = f"https://{railway_url}"
            personal_webhook_url = f"{railway_url}/personal/{user_id}/webhook"
        elif render_url:
            personal_webhook_url = f"{render_url}/personal/{user_id}/webhook"
        else:
            port = PORT
            personal_webhook_url = f"http://localhost:{port}/personal/{user_id}/webhook"
        
        # رسالة ترحيب للمطور
        welcome_message = f"""
🤖 مرحباً بك {update.effective_user.first_name} - المطور

👨‍💻 أنت في الوضع العادي للمطور
🔙 يمكنك العودة إلى لوحة تحكم المطور في أي وقت

🔗 رابط الإشارات الخاص بك:
`{personal_webhook_url}`

استخدم الأزرار أدناه للتنقل
        """
        
        if update.message is not None:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # التحقق من وجود المستخدم في قاعدة البيانات
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        # مستخدم جديد - إنشاء حساب
        user_manager.create_user(user_id)
        user_data = user_manager.get_user(user_id)
        
        # رسالة ترحيب للمستخدم الجديد
        welcome_message = f"""
🤖 مرحباً بك في بوت التداول Bybit متعدد المستخدمين

👋 أهلاً {update.effective_user.first_name}!

🔗 للبدء، يرجى ربط حسابك على Bybit:
• اضغط على زر "🔗 ربط API" أدناه
• سيطلب منك إدخال API_KEY و API_SECRET
• يمكنك الحصول على المفاتيح من: https://api.bybit.com

⚠️ ملاحظة: البوت يدعم التداول الحقيقي والتجريبي
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 ربط API", callback_data="link_api")],
            [InlineKeyboardButton("ℹ️ معلومات", callback_data="info")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message is not None:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        return
    
    # مستخدم موجود - عرض القائمة الرئيسية
    keyboard = [
        [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("📊 حالة الحساب")],
        [KeyboardButton("🔄 الصفقات المفتوحة"), KeyboardButton("📈 تاريخ التداول")],
        [KeyboardButton("💰 المحفظة"), KeyboardButton("📊 إحصائيات")]
    ]
    
    # إضافة زر متابعة Nagdat
    is_following = developer_manager.is_following(ADMIN_USER_ID, user_id)
    if is_following:
        keyboard.append([KeyboardButton("⚡ متابع لـ Nagdat ✅")])
    else:
        keyboard.append([KeyboardButton("⚡ متابعة Nagdat")])
    
    # إضافة أزرار إضافية إذا كان المستخدم نشطاً
    if user_data.get('is_active'):
        keyboard.append([KeyboardButton("▶️ تشغيل البوت")])
    else:
        keyboard.append([KeyboardButton("▶️ تشغيل البوت")])
    
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # الحصول على معلومات حساب المستخدم
    market_type = user_data.get('market_type', 'spot')
    account = user_manager.get_user_account(user_id, market_type)
    
    if account:
        account_info = account.get_account_info()
    else:
        account_info = {
            'balance': user_data.get('balance', 10000.0),
            'available_balance': user_data.get('balance', 10000.0),
            'open_positions': 0
        }
    
    # حالة البوت
    bot_status = "🟢 نشط" if user_data.get('is_active') else "🔴 متوقف"
    
    # التحقق من حالة API مع مؤشر بصري محسن
    api_key = user_data.get('api_key')
    api_secret = user_data.get('api_secret')
    api_status = get_api_status_indicator(api_key, api_secret)
    
    # إنشاء رابط webhook الشخصي للمستخدم
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        personal_webhook_url = f"{railway_url}/personal/{user_id}/webhook"
    elif render_url:
        personal_webhook_url = f"{render_url}/personal/{user_id}/webhook"
    else:
        port = PORT
        personal_webhook_url = f"http://localhost:{port}/personal/{user_id}/webhook"
    
    welcome_message = f"""
🤖 مرحباً بك {update.effective_user.first_name}

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

💰 معلومات الحساب:
• الرصيد الكلي: {account_info.get('balance', 0):.2f} USDT
• الرصيد المتاح: {account_info.get('available_balance', 0):.2f} USDT
• الصفقات المفتوحة: {account_info.get('open_positions', 0)}

🔗 رابط الإشارات الخاص بك:
`{personal_webhook_url}`

📋 استخدم هذا الرابط في TradingView أو أي منصة إشارات

استخدم الأزرار أدناه للتنقل في البوت
    """
    
    if update.message is not None:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة الإعدادات لكل مستخدم"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        if update.message is not None:
            await update.message.reply_text("❌ يرجى استخدام /start أولاً")
        return
    
    keyboard = [
        [InlineKeyboardButton("💰 مبلغ التداول", callback_data="set_amount")],
        [InlineKeyboardButton("🏪 نوع السوق", callback_data="set_market")],
        [InlineKeyboardButton("👤 نوع الحساب", callback_data="set_account")],
        [InlineKeyboardButton("⚡ الرافعة المالية", callback_data="set_leverage")],
        [InlineKeyboardButton("💳 رصيد الحساب التجريبي", callback_data="set_demo_balance")],
        [InlineKeyboardButton("🔗 رابط الإشارات", callback_data="webhook_url")],
        [InlineKeyboardButton("🔗 تحديث API", callback_data="link_api")],
        [InlineKeyboardButton("🔍 فحص API", callback_data="check_api")]
    ]
    
    # إضافة زر تشغيل/إيقاف البوت
    if user_data.get('is_active'):
        keyboard.append([InlineKeyboardButton("⏹️ إيقاف البوت", callback_data="toggle_bot")])
    else:
        keyboard.append([InlineKeyboardButton("▶️ تشغيل البوت", callback_data="toggle_bot")])
    
    keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # الحصول على معلومات حساب المستخدم
    market_type = user_data.get('market_type', 'spot')
    account = user_manager.get_user_account(user_id, market_type)
    
    if account:
        account_info = account.get_account_info()
    else:
        account_info = {
            'balance': user_data.get('balance', 10000.0),
            'available_balance': user_data.get('balance', 10000.0),
            'margin_locked': 0,
            'unrealized_pnl': 0
        }
    
    # حالة البوت
    bot_status = "🟢 نشط" if user_data.get('is_active') else "🔴 متوقف"
    
    # التحقق من حالة API مع مؤشر بصري محسن
    api_key = user_data.get('api_key')
    api_secret = user_data.get('api_secret')
    api_status = get_api_status_indicator(api_key, api_secret)
    account_type = user_data.get('account_type', 'demo')
    trade_amount = user_data.get('trade_amount', 100.0)
    leverage = user_data.get('leverage', 10)
    
    settings_text = f"""
⚙️ إعدادات البوت الحالية:

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

💰 مبلغ التداول: {trade_amount}
🏪 نوع السوق: {market_type.upper()}
👤 نوع الحساب: {'حقيقي' if account_type == 'real' else 'تجريبي داخلي'}
⚡ الرافعة المالية: {leverage}x

📊 معلومات الحساب الحالي ({market_type.upper()}):
💰 الرصيد الكلي: {account_info.get('balance', 0):.2f}
💳 الرصيد المتاح: {account_info.get('available_balance', 0):.2f}
🔒 الهامش المحجوز: {account_info.get('margin_locked', 0):.2f}
📈 الربح/الخسارة غير المحققة: {account_info.get('unrealized_pnl', 0):.2f}
    """
    
    if update.callback_query is not None:
        await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup)
    elif update.message is not None:
        await update.message.reply_text(settings_text, reply_markup=reply_markup)

async def account_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة الحساب مع معلومات مفصلة للفيوتشر"""
    try:
        if trading_bot.user_settings['account_type'] == 'real':
            # الحصول على معلومات الحساب الحقيقي
            if trading_bot.bybit_api:
                balance_response = trading_bot.bybit_api.get_account_balance()
                
                if balance_response.get("retCode") == 0:
                    balance_info = balance_response.get("result", {}).get("list", [])
                    if balance_info:
                        total_equity = balance_info[0].get("totalEquity", "0")
                        available_balance = balance_info[0].get("availableBalance", "0")
                        
                        status_text = f"""
📊 حالة الحساب الحقيقي:

💰 إجمالي الأسهم: {total_equity}
💳 الرصيد المتاح: {available_balance}
🏪 نوع السوق: {trading_bot.user_settings['market_type'].upper()}
                        """
                    else:
                        status_text = "❌ لا توجد معلومات رصيد متاحة"
                else:
                    error_msg = balance_response.get("retMsg", "خطأ غير محدد")
                    status_text = f"❌ خطأ في الحصول على الرصيد: {error_msg}"
            else:
                status_text = "❌ API غير متاح للحساب الحقيقي"
        else:
            # الحصول على معلومات الحساب التجريبي الداخلي
            account = trading_bot.get_current_account()
            account_info = account.get_account_info()
            
            market_type = trading_bot.user_settings['market_type']
            
            if market_type == 'futures':
                status_text = f"""
📊 حالة الحساب التجريبي - فيوتشر:

💰 الرصيد الكلي: {account_info['balance']:.2f}
💳 الرصيد المتاح: {account_info['available_balance']:.2f}
🔒 الهامش المحجوز: {account_info['margin_locked']:.2f}
💼 القيمة الصافية: {account_info['equity']:.2f}
📈 الربح/الخسارة غير المحققة: {account_info['unrealized_pnl']:.2f}
📊 نسبة الهامش: {account_info['margin_ratio']}
🔄 الصفقات المفتوحة: {account_info['open_positions']}

📈 إحصائيات التداول:
📊 إجمالي الصفقات: {account_info['total_trades']}
✅ الصفقات الرابحة: {account_info['winning_trades']}
❌ الصفقات الخاسرة: {account_info['losing_trades']}
🎯 معدل النجاح: {account_info['win_rate']}%
🏪 نوع السوق: FUTURES
⚡ الرافعة المالية: {trading_bot.user_settings['leverage']}x
                """
            else:
                status_text = f"""
📊 حالة الحساب التجريبي - سبوت:

💰 الرصيد الحالي: {account_info['balance']:.2f}
💳 الرصيد الأولي: {account_info['initial_balance']:.2f}
📈 الربح/الخسارة غير المحققة: {account_info['unrealized_pnl']:.2f}
📊 إجمالي الصفقات: {account_info['total_trades']}
✅ الصفقات الرابحة: {account_info['winning_trades']}
❌ الصفقات الخاسرة: {account_info['losing_trades']}
🎯 معدل النجاح: {account_info['win_rate']}%
🔄 الصفقات المفتوحة: {account_info['open_positions']}
🏪 نوع السوق: SPOT
                """
        
        if update.message is not None:
            await update.message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f"خطأ في عرض حالة الحساب: {e}")
        if update.message is not None:
            await update.message.reply_text(f"❌ خطأ في عرض حالة الحساب: {e}")

async def open_positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الصفقات المفتوحة مع معلومات مفصلة للفيوتشر والسبوت"""
    try:
        logger.info(f"عرض الصفقات المفتوحة: {len(trading_bot.open_positions)} صفقة مفتوحة")
        
        # تحديث الأسعار الحالية أولاً
        await trading_bot.update_open_positions_prices()
        
        if not trading_bot.open_positions:
            message_text = "🔄 لا توجد صفقات مفتوحة حالياً"
            if update.callback_query is not None:
                # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
                if update.callback_query.message.text != message_text:
                    await update.callback_query.edit_message_text(message_text)
            elif update.message is not None:
                await update.message.reply_text(message_text)
            return
        
        # فصل الصفقات حسب النوع
        spot_positions = {}
        futures_positions = {}
        
        for position_id, position_info in trading_bot.open_positions.items():
            market_type = position_info.get('account_type', 'spot')
            logger.info(f"الصفقة {position_id}: نوع السوق = {market_type}")
            if market_type == 'spot':
                spot_positions[position_id] = position_info
            else:
                futures_positions[position_id] = position_info
        
        logger.info(f"الصفقات السبوت: {len(spot_positions)}, الصفقات الفيوتشر: {len(futures_positions)}")
        
        # إرسال رسالة منفصلة لكل نوع
        if spot_positions:
            await send_spot_positions_message(update, spot_positions)
        
        if futures_positions:
            await send_futures_positions_message(update, futures_positions)
        
        # إذا لم تكن هناك صفقات من أي نوع
        if not spot_positions and not futures_positions:
            message_text = "🔄 لا توجد صفقات مفتوحة حالياً"
            if update.callback_query is not None:
                # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
                if update.callback_query.message.text != message_text:
                    await update.callback_query.edit_message_text(message_text)
            elif update.message is not None:
                await update.message.reply_text(message_text)
        
    except Exception as e:
        logger.error(f"خطأ في عرض الصفقات المفتوحة: {e}")
        error_message = f"❌ خطأ في عرض الصفقات المفتوحة: {e}"
        if update.callback_query is not None:
            # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
            if update.callback_query.message.text != error_message:
                try:
                    await update.callback_query.edit_message_text(error_message)
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        # تجاهل الخطأ إذا لم يتغير المحتوى
                        pass
                    else:
                        raise
        elif update.message is not None:
            await update.message.reply_text(error_message)

async def send_spot_positions_message(update: Update, spot_positions: dict):
    """إرسال رسالة صفقات السبوت مع عرض زر إغلاق وسعر الربح/الخسارة"""
    if not spot_positions:
        message_text = "🔄 لا توجد صفقات سبوت مفتوحة حالياً"
        if update.callback_query is not None:
            # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
            if update.callback_query.message.text != message_text:
                await update.callback_query.edit_message_text(message_text)
        elif update.message is not None:
            await update.message.reply_text(message_text)
        return
        
    spot_text = "🔄 الصفقات المفتوحة - سبوت:\n\n"
    spot_keyboard = []
    
    for position_id, position_info in spot_positions.items():
        symbol = position_info['symbol']
        entry_price = position_info['entry_price']
        side = position_info['side']
        amount = position_info.get('amount', position_info.get('margin_amount', 0))
        
        # الحصول على السعر الحالي من البيانات المحدثة
        current_price = position_info.get('current_price')
        pnl_percent = position_info.get('pnl_percent', 0.0)
        
        # إذا لم يكن السعر محدث، جربه من API
        if not current_price and trading_bot.bybit_api:
            category = "spot"
            current_price = trading_bot.bybit_api.get_ticker_price(symbol, category)
        
        # حساب الربح/الخسارة
        pnl_value = 0.0
        
        if current_price:
            # حساب الربح/الخسارة
            contracts = amount / entry_price if entry_price > 0 else 0
            if side.lower() == "buy":
                pnl_value = (current_price - entry_price) * contracts
            else:
                pnl_value = (entry_price - current_price) * contracts
            
            if amount > 0:
                pnl_percent = (pnl_value / amount) * 100
            
            # تحديد مؤشرات الربح/الخسارة
            pnl_emoji = "🟢💰" if pnl_value >= 0 else "🔴💸"
            pnl_status = "رابح" if pnl_value >= 0 else "خاسر"
            arrow = "⬆️" if pnl_value >= 0 else "⬇️"
            
            spot_text += f"""
{pnl_emoji} {symbol}
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 المبلغ: {amount:.2f}
{arrow} الربح/الخسارة: {pnl_value:.2f} ({pnl_percent:.2f}%) - {pnl_status}
🆔 رقم الصفقة: {position_id}
            """
        else:
            spot_text += f"""
📊 {symbol}
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: غير متاح
💰 المبلغ: {amount:.2f}
🆔 رقم الصفقة: {position_id}
            """
        
        # إضافة زر إغلاق الصفقة مع عرض الربح/الخسارة
        pnl_display = f"({pnl_value:+.2f})" if current_price else ""
        close_button_text = f"❌ إغلاق {symbol} {pnl_display}"
        spot_keyboard.append([InlineKeyboardButton(close_button_text, callback_data=f"close_{position_id}")])
    
    spot_keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions")])
    spot_reply_markup = InlineKeyboardMarkup(spot_keyboard)
    
    if update.callback_query is not None:
        # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
        if update.callback_query.message.text != spot_text or update.callback_query.message.reply_markup != spot_reply_markup:
            try:
                await update.callback_query.edit_message_text(spot_text, reply_markup=spot_reply_markup)
            except Exception as e:
                if "Message is not modified" in str(e):
                    # تجاهل الخطأ إذا لم يتغير المحتوى
                    pass
                else:
                    raise
    elif update.message is not None:
        await update.message.reply_text(spot_text, reply_markup=spot_reply_markup)

async def send_futures_positions_message(update: Update, futures_positions: dict):
    """إرسال رسالة صفقات الفيوتشر مع معلومات مفصلة وزر إغلاق وسعر الربح/الخسارة"""
    if not futures_positions:
        message_text = "🔄 لا توجد صفقات فيوتشر مفتوحة حالياً"
        if update.callback_query is not None:
            # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
            if update.callback_query.message.text != message_text:
                await update.callback_query.edit_message_text(message_text)
        elif update.message is not None:
            await update.message.reply_text(message_text)
        return
        
    futures_text = "🔄 الصفقات المفتوحة - فيوتشر:\n\n"
    futures_keyboard = []
    
    account = trading_bot.demo_account_futures
    
    for position_id, position_info in futures_positions.items():
        symbol = position_info['symbol']
        entry_price = position_info['entry_price']
        side = position_info['side']
        leverage = position_info.get('leverage', 1)
        margin_amount = position_info.get('margin_amount', 0)
        position_size = position_info.get('position_size', 0)
        liquidation_price = position_info.get('liquidation_price', 0)
        
        # الحصول على الصفقة من الحساب للحصول على معلومات مفصلة
        actual_position = account.positions.get(position_id)
        
        # الحصول على السعر الحالي من البيانات المحدثة
        current_price = position_info.get('current_price')
        pnl_percent = position_info.get('pnl_percent', 0.0)
        
        # إذا لم يكن السعر محدث، جربه من API
        if not current_price and trading_bot.bybit_api:
            category = "linear"
            current_price = trading_bot.bybit_api.get_ticker_price(symbol, category)
        
        # حساب الربح/الخسارة
        unrealized_pnl = 0.0
        
        if current_price and isinstance(actual_position, FuturesPosition):
            # تحديث PnL
            unrealized_pnl = actual_position.update_pnl(current_price)
            if margin_amount > 0:
                pnl_percent = (unrealized_pnl / margin_amount) * 100
            
            # فحص التصفية - تحذير فقط عند الاقتراب 1%
            liquidation_warning = ""
            if actual_position.check_liquidation(current_price):
                liquidation_warning = "🚨 خطر التصفية! "
            else:
                # حساب المسافة من سعر التصفية
                if actual_position.side == "buy":
                    distance_percent = ((current_price - actual_position.liquidation_price) / current_price) * 100
                else:
                    distance_percent = ((actual_position.liquidation_price - current_price) / current_price) * 100
                
                # تحذير فقط إذا كان قريب 1% أو أقل
                if distance_percent <= 1.0:
                    liquidation_warning = "⚠️ قريب من التصفية! "
            
            # تحديد مؤشرات الربح/الخسارة
            pnl_emoji = "🟢💰" if unrealized_pnl >= 0 else "🔴💸"
            pnl_status = "رابح" if unrealized_pnl >= 0 else "خاسر"
            arrow = "⬆️" if unrealized_pnl >= 0 else "⬇️"
            
            futures_text += f"""
{liquidation_warning}{pnl_emoji} {symbol}
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الهامش المحجوز: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
{arrow} الربح/الخسارة: {unrealized_pnl:.2f} ({pnl_percent:.2f}%) - {pnl_status}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {actual_position.liquidation_price:.6f}
📊 عدد العقود: {actual_position.contracts:.6f}
🆔 رقم الصفقة: {position_id}
            """
        else:
            futures_text += f"""
📊 {symbol}
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: غير متاح
💰 الهامش المحجوز: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {liquidation_price:.6f}
🆔 رقم الصفقة: {position_id}
            """
        
        # إضافة زر إغلاق الصفقة مع عرض الربح/الخسارة
        pnl_display = f"({unrealized_pnl:+.2f})" if current_price else ""
        close_button_text = f"❌ إغلاق {symbol} {pnl_display}"
        futures_keyboard.append([InlineKeyboardButton(close_button_text, callback_data=f"close_{position_id}")])
    
    futures_keyboard.append([InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions")])
    futures_reply_markup = InlineKeyboardMarkup(futures_keyboard)
    
    if update.callback_query is not None:
        # التحقق مما إذا كان المحتوى مختلفاً قبل التحديث
        try:
            if update.callback_query.message.text != futures_text or update.callback_query.message.reply_markup != futures_reply_markup:
                await update.callback_query.edit_message_text(futures_text, reply_markup=futures_reply_markup)
        except Exception as e:
            if "Message is not modified" in str(e):
                # تجاهل الخطأ إذا لم يتغير المحتوى
                pass
            else:
                raise
    elif update.message is not None:
        await update.message.reply_text(futures_text, reply_markup=futures_reply_markup)

async def close_position(position_id: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إغلاق صفقة مع دعم محسن للفيوتشر"""
    try:
        if position_id not in trading_bot.open_positions:
            if update.callback_query is not None:
                await update.callback_query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
        position_info = trading_bot.open_positions[position_id]
        symbol = position_info['symbol']
        category = position_info.get('category', 'spot')
        market_type = position_info.get('account_type', 'spot')
        
        # الحصول على السعر الحالي
        current_price = position_info.get('current_price')
        if not current_price and trading_bot.bybit_api:
            current_price = trading_bot.bybit_api.get_ticker_price(symbol, category)
        
        if current_price is None:
            # استخدام سعر وهمي للاختبار
            current_price = position_info['entry_price'] * 1.01  # ربح 1%
        
        if trading_bot.user_settings['account_type'] == 'demo':
            # تحديد الحساب الصحيح
            if market_type == 'spot':
                account = trading_bot.demo_account_spot
                success, result = account.close_spot_position(position_id, current_price)
            else:
                account = trading_bot.demo_account_futures
                success, result = account.close_futures_position(position_id, current_price)
                
            if success:
                trade_record = result
                
                if isinstance(trade_record, dict) and 'pnl' in trade_record:
                    pnl = float(trade_record['pnl'])
                    
                    # مؤشرات بصرية واضحة للربح والخسارة
                    if pnl > 0:
                        pnl_emoji = "🟢💰✅"
                        status_text = "رابحة"
                        arrow = "⬆️💚"
                        visual_indicator = "🟩🟩🟩🟩🟩"
                    else:
                        pnl_emoji = "🔴💸❌"
                        status_text = "خاسرة"
                        arrow = "⬇️💔"
                        visual_indicator = "🟥🟥🟥🟥🟥"
                    
                    if market_type == 'futures':
                        margin_amount = trade_record.get('margin_amount', 0)
                        position_size = trade_record.get('position_size', 0)
                        leverage = trade_record.get('leverage', 1)
                        liquidation_price = trade_record.get('liquidation_price', 0)
                        pnl_percent = (pnl / margin_amount) * 100 if margin_amount > 0 else 0
                        
                        message = f"""
✅ تم إغلاق صفقة الفيوتشر
{pnl_emoji} {symbol}
{visual_indicator}
🔄 النوع: {position_info['side'].upper()}
💲 سعر الدخول: {position_info['entry_price']:.6f}
💲 سعر الإغلاق: {current_price:.6f}
💰 الهامش المحجوز: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
{arrow} الربح/الخسارة: {pnl:.2f} ({pnl_percent:.2f}%) - {status_text}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية كان: {liquidation_price:.6f}
📊 عدد العقود: {trade_record.get('contracts', 0):.6f}

💰 رصيد الحساب الجديد: {account.balance:.2f}
💳 الرصيد المتاح: {account.get_available_balance():.2f}
🔒 الهامش المحجوز: {account.margin_locked:.2f}
📈 إجمالي الصفقات: {account.total_trades}
✅ الصفقات الرابحة: {account.winning_trades}
❌ الصفقات الخاسرة: {account.losing_trades}
🎯 معدل النجاح: {account.get_account_info()['win_rate']}%
                        """
                    else:
                        message = f"""
✅ تم إغلاق الصفقة التجريبية
{pnl_emoji} {symbol}
{visual_indicator}
🔄 النوع: {position_info['side'].upper()}
💲 سعر الدخول: {position_info['entry_price']:.6f}
💲 سعر الإغلاق: {current_price:.6f}
{arrow} الربح/الخسارة: {pnl:.2f} ({status_text})

💰 رصيد الحساب الجديد: {account.balance:.2f}
📈 إجمالي الصفقات: {account.total_trades}
✅ الصفقات الرابحة: {account.winning_trades}
❌ الصفقات الخاسرة: {account.losing_trades}
🎯 معدل النجاح: {account.get_account_info()['win_rate']}%
                        """
                    
                    if update.callback_query is not None:
                        await update.callback_query.edit_message_text(message)
                else:
                    # إذا لم يكن trade_record dict أو لم يحتوي على 'pnl'
                    message = f"""
✅ تم إغلاق الصفقة التجريبية
📊 {symbol}
🔄 النوع: {position_info['side'].upper()}
💲 سعر الدخول: {position_info['entry_price']:.6f}
💲 سعر الإغلاق: {current_price:.6f}

💰 رصيد الحساب الجديد: {account.balance:.2f}
                    """
                    
                    if update.callback_query is not None:
                        await update.callback_query.edit_message_text(message)
                
                # حذف الصفقة من القائمة العامة
                if position_id in trading_bot.open_positions:
                    del trading_bot.open_positions[position_id]
                
            else:
                if update.callback_query is not None:
                    await update.callback_query.edit_message_text(f"❌ فشل في إغلاق الصفقة: {result}")
        else:
            # إغلاق الصفقة الحقيقية (يتطلب تنفيذ API إضافي)
            if update.callback_query is not None:
                await update.callback_query.edit_message_text("⚠️ إغلاق الصفقات الحقيقية يتطلب تنفيذاً يدوياً حالياً")
        
    except Exception as e:
        logger.error(f"خطأ في إغلاق الصفقة: {e}")
        if update.callback_query is not None:
            await update.callback_query.edit_message_text(f"❌ خطأ في إغلاق الصفقة: {e}")

async def trade_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض تاريخ التداول مع تفاصيل محسنة للفيوتشر"""
    try:
        # الحصول على تاريخ الصفقات من الحسابات التجريبية
        spot_history = trading_bot.demo_account_spot.trade_history
        futures_history = trading_bot.demo_account_futures.trade_history
        
        # دمج التاريخ
        all_history = spot_history + futures_history
        
        # فرز حسب التاريخ (الأحدث أولاً)
        all_history.sort(key=lambda x: x.get('close_timestamp', x.get('timestamp', datetime.min)), reverse=True)
        
        if not all_history:
            if update.message is not None:
                await update.message.reply_text("📋 لا يوجد تاريخ صفقات حتى الآن")
            return
        
        # عرض أول 10 صفقات
        history_text = "📋 تاريخ التداول (آخر 10 صفقات):\n\n"
        for i, trade in enumerate(all_history[:10], 1):
            symbol = trade.get('symbol', 'N/A')
            side = trade.get('side', 'N/A')
            entry_price = trade.get('entry_price', 0)
            closing_price = trade.get('closing_price', entry_price)
            pnl = trade.get('pnl', 0)
            market_type = trade.get('market_type', 'spot')
            timestamp = trade.get('close_timestamp', trade.get('timestamp', datetime.now()))
            
            # معلومات إضافية للفيوتشر
            margin_amount = trade.get('margin_amount', 0)
            position_size = trade.get('position_size', 0)
            leverage = trade.get('leverage', 1)
            liquidation_price = trade.get('liquidation_price', 0)
            
            # تنسيق التاريخ
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(timestamp)
            
            # تحديد مؤشرات الربح/الخسارة
            pnl_emoji = "🟢💰" if pnl > 0 else "🔴💸"
            status_text = "رابحة" if pnl > 0 else "خاسرة"
            arrow = "⬆️💚" if pnl > 0 else "⬇️💔"
            visual_indicator = "🟩🟩🟩🟩🟩" if pnl > 0 else "🟥🟥🟥🟥🟥"
            
            if market_type == 'futures':
                pnl_percent = (pnl / margin_amount) * 100 if margin_amount > 0 else 0
                
                history_text += f"""
{pnl_emoji} {symbol} (FUTURES)
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 سعر الإغلاق: {closing_price:.6f}
💰 الهامش: {margin_amount:.2f}
📈 حجم الصفقة: {position_size:.2f}
{arrow} الربح/الخسارة: {pnl:.2f} ({pnl_percent:.2f}%) - {status_text}
⚡ الرافعة: {leverage}x
⚠️ سعر التصفية: {liquidation_price:.6f}
{visual_indicator}

exampleInputEmail: {time_str}

---
                """
            else:
                history_text += f"""
{pnl_emoji} {symbol} (SPOT)
🔄 النوع: {side.upper()}
💲 سعر الدخول: {entry_price:.6f}
💲 سعر الإغلاق: {closing_price:.6f}
{arrow} الربح/الخسارة: {pnl:.2f} ({status_text})
{visual_indicator}

exampleInputEmail: {time_str}

---
                """
        
        if update.message is not None:
            await update.message.reply_text(history_text)
            
    except Exception as e:
        logger.error(f"خطأ في عرض تاريخ التداول: {e}")
        if update.message is not None:
            await update.message.reply_text(f"❌ خطأ في عرض تاريخ التداول: {e}")

async def wallet_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات المحفظة مع تفاصيل الفيوتشر"""
    try:
        # الحصول على معلومات الحسابات التجريبية
        spot_account = trading_bot.demo_account_spot
        futures_account = trading_bot.demo_account_futures
        
        spot_info = spot_account.get_account_info()
        futures_info = futures_account.get_account_info()
        
        # حساب الإجمالي
        total_balance = spot_info['balance'] + futures_info['balance']
        total_available = spot_info.get('available_balance', spot_info['balance']) + futures_info.get('available_balance', futures_info['balance'])
        total_margin_locked = spot_info.get('margin_locked', 0) + futures_info.get('margin_locked', 0)
        total_equity = spot_info.get('equity', spot_info['balance']) + futures_info.get('equity', futures_info['balance'])
        total_pnl = spot_info['unrealized_pnl'] + futures_info['unrealized_pnl']
        total_trades = spot_info['total_trades'] + futures_info['total_trades']
        total_open_positions = spot_info['open_positions'] + futures_info['open_positions']
        
        # تحديد مؤشرات الربح/الخسارة
        total_pnl_emoji = "🟢💰" if total_pnl >= 0 else "🔴💸"
        total_pnl_arrow = "⬆️💚" if total_pnl >= 0 else "⬇️💔"
        total_pnl_status = "رابحة" if total_pnl >= 0 else "خاسرة"
        
        spot_pnl_emoji = "🟢💰" if spot_info['unrealized_pnl'] >= 0 else "🔴💸"
        futures_pnl_emoji = "🟢💰" if futures_info['unrealized_pnl'] >= 0 else "🔴💸"
        
        # حساب معدل النجاح الإجمالي
        total_winning_trades = spot_info['winning_trades'] + futures_info['winning_trades']
        total_losing_trades = spot_info['losing_trades'] + futures_info['losing_trades']
        total_win_rate = round((total_winning_trades / max(total_trades, 1)) * 100, 2)
        
        wallet_message = f"""
💰 معلومات المحفظة الشاملة

📊 ملخص الحسابات:
{spot_pnl_emoji} السبوت: {spot_info['balance']:.2f}
   💳 المتاح: {spot_info.get('available_balance', spot_info['balance']):.2f}
   📈 PnL: {spot_info['unrealized_pnl']:.2f}

{futures_pnl_emoji} الفيوتشر: {futures_info['balance']:.2f}
   💳 المتاح: {futures_info.get('available_balance', futures_info['balance']):.2f}
   🔒 الهامش المحجوز: {futures_info.get('margin_locked', 0):.2f}
   💼 القيمة الصافية: {futures_info.get('equity', futures_info['balance']):.2f}
   📈 PnL: {futures_info['unrealized_pnl']:.2f}
   📊 نسبة الهامش: {futures_info.get('margin_ratio', '∞')}

📈 الإجمالي:
{total_pnl_emoji} الرصيد الكلي: {total_balance:.2f}
💳 الرصيد المتاح: {total_available:.2f}
🔒 الهامش المحجوز: {total_margin_locked:.2f}
💼 القيمة الصافية: {total_equity:.2f}
{total_pnl_arrow} إجمالي PnL: {total_pnl:.2f} - {total_pnl_status}

📊 إحصائيات التداول:
🔄 الصفقات المفتوحة: {total_open_positions}
📈 إجمالي الصفقات: {total_trades}
✅ الصفقات الرابحة: {total_winning_trades}
❌ الصفقات الخاسرة: {total_losing_trades}
🎯 معدل النجاح: {total_win_rate}%

⚡ إعدادات التداول الحالية:
🏪 نوع السوق: {trading_bot.user_settings['market_type'].upper()}
💰 مبلغ التداول: {trading_bot.user_settings['trade_amount']}
🔢 الرافعة المالية: {trading_bot.user_settings['leverage']}x
        """
        
        if update.message is not None:
            await update.message.reply_text(wallet_message)
            
    except Exception as e:
        logger.error(f"خطأ في عرض المحفظة: {e}")
        if update.message is not None:
            await update.message.reply_text(f"❌ خطأ في عرض المحفظة: {e}")

# باقي الوظائف تبقى كما هي مع بعض التحديثات...
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار المضغوطة"""
    if update.callback_query is None:
        return
        
    query = update.callback_query
    await query.answer()
    
    if query.data is None:
        return
        
    user_id = update.effective_user.id if update.effective_user else None
    data = query.data
    
    # معالجة زر الربط API
    if data == "link_api":
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_api_key"
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("""
🔗 ربط API - الخطوة 1

أرسل API_KEY الخاص بك من Bybit

⚠️ تأكد من:
• عدم مشاركة المفاتيح مع أي شخص
• إنشاء مفاتيح API محدودة الصلاحيات
• يمكنك الحصول على المفاتيح من: https://api.bybit.com
            """)
    elif data == "check_api":
        # فحص حالة API
        if user_id is not None:
            user_data = user_manager.get_user(user_id)
            if user_data and user_data.get('api_key') and user_data.get('api_secret'):
                # عرض رسالة فحص
                if update.callback_query is not None:
                    await update.callback_query.edit_message_text("🔄 جاري فحص API...")
                
                # التحقق من صحة API
                is_valid = await check_api_connection(user_data['api_key'], user_data['api_secret'])
                
                if is_valid:
                    status_message = """
✅ API يعمل بشكل صحيح!

🟢 الاتصال: نشط
🔗 الخادم: https://api.bybit.com
📊 الصلاحيات: مفعلة
🔐 الحالة: آمن

يمكنك استخدام جميع ميزات البوت
                    """
                else:
                    status_message = """
❌ مشكلة في API!

🔴 الاتصال: فشل
🔗 الخادم: https://api.bybit.com
📊 الصلاحيات: غير مفعلة أو خطأ في المفاتيح
🔐 الحالة: غير آمن

يرجى تحديث API keys
                    """
                
                keyboard = [
                    [InlineKeyboardButton("🔗 تحديث API", callback_data="link_api")],
                    [InlineKeyboardButton("🔙 العودة", callback_data="settings")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if update.callback_query is not None:
                    await update.callback_query.message.edit_text(status_message, reply_markup=reply_markup)
            else:
                # لا توجد API keys
                keyboard = [
                    [InlineKeyboardButton("🔗 ربط API", callback_data="link_api")],
                    [InlineKeyboardButton("🔙 العودة", callback_data="settings")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if update.callback_query is not None:
                    await update.callback_query.message.edit_text("""
❌ لا توجد API keys!

🔴 يجب ربط API أولاً
🔗 اضغط على "ربط API" للبدء

⚠️ بدون API keys، البوت يعمل في الوضع التجريبي فقط
                    """, reply_markup=reply_markup)
    # معالجة زر تشغيل/إيقاف البوت
    elif data == "toggle_bot":
        if user_id is not None:
            success = user_manager.toggle_user_active(user_id)
            if success:
                user_data = user_manager.get_user(user_id)
                is_active = user_data.get('is_active', False)
                status_text = "✅ تم تشغيل البوت بنجاح" if is_active else "⏹️ تم إيقاف البوت"
                if update.callback_query is not None:
                    await update.callback_query.edit_message_text(status_text)
                # العودة إلى قائمة الإعدادات
                await asyncio.sleep(1)
                await settings_menu(update, context)
            else:
                if update.callback_query is not None:
                    await update.callback_query.edit_message_text("❌ فشل في تبديل حالة البوت")
    elif data == "info":
        info_text = """
ℹ️ معلومات البوت

هذا بوت تداول متعدد المستخدمين يدعم:
• التداول الآلي على Bybit
• إدارة الصفقات (TP/SL/Partial Close)
• دعم Spot و Futures
• حسابات منفصلة لكل مستخدم
• اتصال آمن عبر Bybit Live API

🔗 الموقع الرسمي: https://bybit.com
📧 للدعم: استخدم أمر /start
        """
        if update.callback_query is not None:
            await update.callback_query.edit_message_text(info_text)
    elif data == "main_menu":
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await start(update, context)
    elif data == "settings":
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data.startswith("close_"):
        position_id = data.replace("close_", "")
        await close_position(position_id, update, context)
    elif data == "refresh_positions":
        await open_positions(update, context)
    elif data == "set_amount":
        # تنفيذ إعداد مبلغ التداول
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_trade_amount"
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("💰 أدخل مبلغ التداول الجديد:")
    elif data == "set_market":
        # تنفيذ إعداد نوع السوق
        keyboard = [
            [InlineKeyboardButton("-spot", callback_data="market_spot")],
            [InlineKeyboardButton("futures", callback_data="market_futures")],
            [InlineKeyboardButton("🔙 العودة", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("اختر نوع السوق:", reply_markup=reply_markup)
    elif data == "set_account":
        # تنفيذ إعداد نوع الحساب
        keyboard = [
            [InlineKeyboardButton("حقيقي", callback_data="account_real")],
            [InlineKeyboardButton("تجريبي داخلي", callback_data="account_demo")],
            [InlineKeyboardButton("🔙 العودة", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("اختر نوع الحساب:", reply_markup=reply_markup)
    elif data == "set_leverage":
        # تنفيذ إعداد الرافعة المالية
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_leverage"
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("⚡ أدخل قيمة الرافعة المالية الجديدة (1-100):")
    elif data == "set_demo_balance":
        # تنفيذ إعداد رصيد الحساب التجريبي
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_demo_balance"
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("💳 أدخل الرصيد الجديد للحساب التجريبي:")
    elif data == "market_spot":
        trading_bot.user_settings['market_type'] = 'spot'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "market_futures":
        trading_bot.user_settings['market_type'] = 'futures'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "account_real":
        trading_bot.user_settings['account_type'] = 'real'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "account_demo":
        trading_bot.user_settings['account_type'] = 'demo'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "back_to_settings":
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "webhook_url":
        # عرض رابط الإشارات الشخصي للمستخدم
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        
        if railway_url:
            if not railway_url.startswith('http'):
                railway_url = f"https://{railway_url}"
            personal_webhook_url = f"{railway_url}/personal/{user_id}/webhook"
            old_webhook_url = f"{railway_url}/webhook"
        elif render_url:
            personal_webhook_url = f"{render_url}/personal/{user_id}/webhook"
            old_webhook_url = f"{render_url}/webhook"
        else:
            port = PORT
            personal_webhook_url = f"http://localhost:{port}/personal/{user_id}/webhook"
            old_webhook_url = f"http://localhost:{port}/webhook"
        
        message = f"""
🔗 روابط استقبال الإشارات

📡 رابطك الشخصي (موصى به):
`{personal_webhook_url}`

• يستخدم إعداداتك الخاصة
• صفقات منفصلة لحسابك فقط
• آمن ومخصص لك

━━━━━━━━━━━━━━━━━━━━━━

🌐 الرابط العام (قديم):
`{old_webhook_url}`

• يستخدم الإعدادات الافتراضية
• مشترك بين جميع المستخدمين

━━━━━━━━━━━━━━━━━━━━━━

📋 كيفية الاستخدام في TradingView:

1️⃣ افتح استراتيجيتك في TradingView
2️⃣ اذهب إلى Settings → Notifications
3️⃣ أضف Webhook URL
4️⃣ الصق رابطك الشخصي
5️⃣ في Message، استخدم أحد الصيغتين:

📌 الصيغة البسيطة (موصى بها):
```
{{"symbol": "{{"{{ticker}}"}}", "action": "{{"{{strategy.order.action}}"}}}}
```

📌 الصيغة مع السعر (اختياري):
```
{{"symbol": "{{"{{ticker}}"}}", "action": "{{"{{strategy.order.action}}"}}", "price": {{"{{close}}"}}}}
```

💡 الإجراءات المدعومة:
• `buy` - شراء
• `sell` - بيع  
• `close` - إغلاق الصفقة

💡 نصائح:
• استخدم رابطك الشخصي للحصول على تجربة أفضل
• السعر اختياري - إذا لم تحدده سيستخدم السعر الحالي
• يمكنك نسخ الرابط بالضغط عليه
• الرابط يعمل مع TradingView و أي منصة إشارات أخرى

🔐 الأمان:
• لا تشارك رابطك الشخصي مع أحد
• يمكن تعطيل حسابك من الإعدادات إذا لزم الأمر
        """
        
        keyboard = [
            [InlineKeyboardButton("📖 شرح مفصل", callback_data="webhook_help")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query is not None:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    # معالجة أزرار المطور
    elif data == "developer_panel":
        await show_developer_panel(update, context)
    elif data == "dev_show_followers":
        await handle_show_followers(update, context)
    elif data == "dev_stats":
        await handle_developer_stats(update, context)
    elif data.startswith("dev_signal_"):
        # معالجة إرسال إشارة سريعة
        parts = data.replace("dev_signal_", "").split("_")
        if len(parts) == 2 and user_id:
            symbol, action = parts
            # الحصول على السعر الحالي
            try:
                price_data = trading_bot.get_current_price(symbol)
                price = price_data.get('price', 0)
                
                # إرسال الإشارة
                signal_data = {
                    'symbol': symbol,
                    'action': action,
                    'price': price,
                    'amount': 100
                }
                
                result = developer_manager.broadcast_signal_to_followers(
                    developer_id=user_id,
                    signal_data=signal_data
                )
                
                if result['success']:
                    message = f"""
✅ تم إرسال الإشارة بنجاح!

📊 التفاصيل:
• الرمز: {symbol}
• الإجراء: {action}
• السعر: {price}
• عدد المستلمين: {result['follower_count']}
                    """
                    await update.callback_query.answer("✅ تم الإرسال!")
                    await update.callback_query.message.reply_text(message)
                else:
                    await update.callback_query.answer(f"❌ {result['message']}")
            except Exception as e:
                logger.error(f"خطأ في إرسال الإشارة: {e}")
                await update.callback_query.answer("❌ خطأ في الإرسال")
    elif data == "dev_toggle_active":
        if user_id:
            success = developer_manager.toggle_developer_active(user_id)
            if success:
                await update.callback_query.answer("✅ تم التبديل")
                stats = developer_manager.get_developer_statistics(user_id)
                message = f"""
⚙️ إعدادات المطور

حالة النظام: {'🟢 نشط' if stats['is_active'] else '🔴 غير نشط'}
صلاحية البث: {'✅ مفعلة' if stats['can_broadcast'] else '❌ معطلة'}
                """
                keyboard = [
                    [InlineKeyboardButton("تبديل الحالة", callback_data="dev_toggle_active")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
            else:
                await update.callback_query.answer("❌ فشل التبديل")
    elif data.startswith("dev_remove_follower_"):
        # معالجة إزالة متابع
        follower_id_str = data.replace("dev_remove_follower_", "")
        try:
            follower_id = int(follower_id_str)
            if user_id:
                success = developer_manager.remove_follower(user_id, follower_id)
                if success:
                    await update.callback_query.answer(f"✅ تم إزالة المتابع {follower_id}")
                    # تحديث قائمة المتابعين
                    await handle_show_followers(update, context)
                else:
                    await update.callback_query.answer("❌ فشل في الإزالة")
        except ValueError:
            await update.callback_query.answer("❌ خطأ في ID المتابع")
    elif data == "dev_toggle_auto_broadcast":
        # تبديل حالة التوزيع التلقائي
        if user_id:
            # تبديل الحالة في قاعدة البيانات
            success = db_manager.toggle_auto_broadcast(user_id)
            
            if success:
                # الحصول على الحالة الجديدة
                new_state = db_manager.get_auto_broadcast_status(user_id)
                stats = developer_manager.get_developer_statistics(user_id)
                
                message = f"""
⚙️ إعدادات المطور

🔧 الإعدادات الحالية:
• حالة النظام: {'🟢 نشط' if stats['is_active'] else '🔴 غير نشط'}
• صلاحية البث: {'✅ مفعلة' if stats['can_broadcast'] else '❌ معطلة'}
• 📡 التوزيع التلقائي للإشارات: {'✅ مُفعّل' if new_state else '❌ مُعطّل'}

💡 التوزيع التلقائي:
عند التفعيل، أي صفقة تفتحها على حسابك ستُرسل تلقائياً لجميع متابعيك!
                """
                
                keyboard = [
                    [InlineKeyboardButton("تبديل الحالة", callback_data="dev_toggle_active")],
                    [InlineKeyboardButton(
                        f"{'❌ تعطيل' if new_state else '✅ تفعيل'} التوزيع التلقائي", 
                        callback_data="dev_toggle_auto_broadcast"
                    )],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
                await update.callback_query.answer(f"✅ التوزيع التلقائي: {'مُفعّل' if new_state else 'مُعطّل'}")
            else:
                await update.callback_query.answer("❌ فشل في تبديل الحالة")
    elif data == "dev_refresh_users":
        # تحديث قائمة المستخدمين
        if user_id:
            all_users_data = db_manager.get_all_developers() + user_manager.get_all_active_users()
            active_users = user_manager.get_all_active_users()
            followers = developer_manager.get_followers(user_id)
            
            message = f"""
👥 إحصائيات المستخدمين

📊 الأعداد:
• إجمالي المستخدمين: {len(all_users_data)}
• المستخدمين النشطين: {len(active_users)}
• متابعي Nagdat: {len(followers)} 👥

📋 قائمة المستخدمين النشطين:
            """
            
            for i, uid in enumerate(active_users[:15], 1):
                is_follower = uid in followers
                follower_icon = "⚡" if is_follower else "⚪"
                message += f"{i}. {follower_icon} User ID: {uid}\n"
            
            if len(active_users) > 15:
                message += f"\n... و {len(active_users) - 15} مستخدم آخرين"
            
            message += "\n\n⚡ = يتابع Nagdat"
            
            keyboard = [
                [InlineKeyboardButton("👥 عرض المتابعين", callback_data="dev_show_followers")],
                [InlineKeyboardButton("🔄 تحديث", callback_data="dev_refresh_users")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
            await update.callback_query.answer("✅ تم التحديث")
    
    else:
        # معالجة أي أزرار أخرى غير محددة
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("❌ زر غير مدعوم")

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النصوص المدخلة"""
    if update.message is None or update.message.text is None:
        return
        
    user_id = update.effective_user.id if update.effective_user else None
    text = update.message.text
    
    # معالجة أزرار المطور
    if user_id and developer_manager.is_developer(user_id):
        if text == "📡 إرسال إشارة":
            await handle_send_signal_developer(update, context)
            return
        elif text == "👥 المتابعين":
            await handle_show_followers(update, context)
            return
        elif text == "📊 إحصائيات المطور":
            await handle_developer_stats(update, context)
            return
        elif text == "👥 إدارة المستخدمين":
            # عرض قائمة المستخدمين
            all_users_data = db_manager.get_all_developers() + user_manager.get_all_active_users()
            active_users = user_manager.get_all_active_users()
            followers = developer_manager.get_followers(user_id)
            
            message = f"""
👥 إحصائيات المستخدمين

📊 الأعداد:
• إجمالي المستخدمين: {len(all_users_data)}
• المستخدمين النشطين: {len(active_users)}
• متابعي Nagdat: {len(followers)} 👥

📋 قائمة المستخدمين النشطين:
            """
            
            for i, uid in enumerate(active_users[:15], 1):
                is_follower = uid in followers
                follower_icon = "⚡" if is_follower else "⚪"
                message += f"{i}. {follower_icon} User ID: {uid}\n"
            
            if len(active_users) > 15:
                message += f"\n... و {len(active_users) - 15} مستخدم آخرين"
            
            message += "\n\n⚡ = يتابع Nagdat"
            
            keyboard = [
                [InlineKeyboardButton("👥 عرض المتابعين", callback_data="dev_show_followers")],
                [InlineKeyboardButton("🔄 تحديث", callback_data="dev_refresh_users")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup)
            return
        elif text == "📱 إشعار جماعي":
            await update.message.reply_text("📱 أرسل الإشعار الذي تريد إرساله لجميع المستخدمين:")
            if user_id:
                user_input_state[user_id] = "waiting_for_broadcast_message"
            return
        elif text == "⚙️ إعدادات المطور":
            stats = developer_manager.get_developer_statistics(user_id)
            
            # الحصول على حالة التوزيع التلقائي من قاعدة البيانات
            auto_broadcast = db_manager.get_auto_broadcast_status(user_id)
            
            message = f"""
⚙️ إعدادات المطور

🔧 الإعدادات الحالية:
• حالة النظام: {'🟢 نشط' if stats['is_active'] else '🔴 غير نشط'}
• صلاحية البث: {'✅ مفعلة' if stats['can_broadcast'] else '❌ معطلة'}
• 📡 التوزيع التلقائي للإشارات: {'✅ مُفعّل' if auto_broadcast else '❌ مُعطّل'}

💡 التوزيع التلقائي:
عند التفعيل، أي صفقة تفتحها على حسابك ستُرسل تلقائياً لجميع متابعيك!
            """
            keyboard = [
                [InlineKeyboardButton("تبديل الحالة", callback_data="dev_toggle_active")],
                [InlineKeyboardButton(
                    f"{'❌ تعطيل' if auto_broadcast else '✅ تفعيل'} التوزيع التلقائي", 
                    callback_data="dev_toggle_auto_broadcast"
                )],
                [InlineKeyboardButton("🔙 رجوع", callback_data="developer_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup)
            return
        elif text == "🔄 تحديث":
            await show_developer_panel(update, context)
            return
        elif text == "👤 الوضع العادي":
            # إزالة مؤقتاً حالة المطور للاطلاع على واجهة المستخدم العادي
            await update.message.reply_text("🔄 العودة للوضع العادي...\nاستخدم /start للعودة لوضع المطور")
            # لا نغير أي شيء، فقط نعرض القائمة العادية
            user_data = user_manager.get_user(user_id)
            if not user_data:
                user_manager.create_user(user_id)
            
            # عرض القائمة العادية مع زر مخفي للمطور للعودة لوضع المطور
            keyboard = [
                [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("📊 حالة الحساب")],
                [KeyboardButton("🔄 الصفقات المفتوحة"), KeyboardButton("📈 تاريخ التداول")],
                [KeyboardButton("💰 المحفظة"), KeyboardButton("📊 إحصائيات")]
            ]
            
            # إضافة زر مخفي للمطور للعودة لوضع المطور (يظهر فقط للمطورين)
            if developer_manager.is_developer(user_id):
                keyboard.append([KeyboardButton("🔙 الرجوع لحساب المطور")])
            
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("👤 الوضع العادي", reply_markup=reply_markup)
            return
        elif text == "🔙 الرجوع لحساب المطور":
            # التحقق من أن المستخدم مطور قبل الرجوع لوضع المطور
            if developer_manager.is_developer(user_id):
                await show_developer_panel(update, context)
            else:
                await update.message.reply_text("❌ ليس لديك صلاحية للوصول لوضع المطور")
            return
    
    # معالجة أزرار المستخدمين العاديين
    if user_id and not developer_manager.is_developer(user_id):
        if text == "⚡ متابعة Nagdat" or text == "⚡ متابع لـ Nagdat ✅":
            # تبديل حالة المتابعة
            is_following = developer_manager.is_following(ADMIN_USER_ID, user_id)
            
            if is_following:
                # إلغاء المتابعة
                success = developer_manager.remove_follower(ADMIN_USER_ID, user_id)
                if success:
                    message = """
❌ تم إلغاء متابعة Nagdat

لن تستقبل إشاراته بعد الآن.
للمتابعة مرة أخرى، اضغط على الزر في القائمة الرئيسية.
                    """
                    await update.message.reply_text(message)
                    # تحديث القائمة
                    await start(update, context)
                else:
                    await update.message.reply_text("❌ فشل في إلغاء المتابعة")
            else:
                # إضافة متابعة
                success = developer_manager.add_follower(ADMIN_USER_ID, user_id)
                if success:
                    message = """
✅ تم متابعة Nagdat بنجاح!

الآن ستستقبل جميع إشارات التداول التي يرسلها Nagdat تلقائياً!

📡 ستصلك الإشارات فور إرسالها
🔔 تأكد من تفعيل الإشعارات
⚙️ يمكنك إلغاء المتابعة في أي وقت
                    """
                    await update.message.reply_text(message)
                    # تحديث القائمة
                    await start(update, context)
                else:
                    await update.message.reply_text("❌ فشل في المتابعة")
            return
    
    # التحقق مما إذا كنا ننتظر إدخال المستخدم للإعدادات
    if user_id is not None and user_id in user_input_state:
        state = user_input_state[user_id]
        
        # معالجة إرسال الإشعار الجماعي من المطور
        if state == "waiting_for_broadcast_message":
            if developer_manager.is_developer(user_id):
                broadcast_message = f"""
📢 إشعار من المطور

{text}
                """
                # إرسال لجميع المستخدمين النشطين
                all_users = user_manager.get_all_active_users()
                success_count = 0
                
                for uid in all_users:
                    try:
                        application = Application.builder().token(TELEGRAM_TOKEN).build()
                        await application.bot.send_message(chat_id=uid, text=broadcast_message)
                        success_count += 1
                    except Exception as e:
                        logger.error(f"خطأ في إرسال الإشعار للمستخدم {uid}: {e}")
                
                del user_input_state[user_id]
                await update.message.reply_text(f"✅ تم إرسال الإشعار إلى {success_count} مستخدم من أصل {len(all_users)}")
                return
            else:
                del user_input_state[user_id]
                await update.message.reply_text("❌ ليس لديك صلاحية")
                return
        
        if state == "waiting_for_api_key":
            # حفظ API_KEY مؤقتاً
            if not hasattr(context, 'user_data') or context.user_data is None:
                context.user_data = {}
            context.user_data['temp_api_key'] = text
            # الانتقال إلى الخطوة التالية
            user_input_state[user_id] = "waiting_for_api_secret"
            if update.message is not None:
                await update.message.reply_text("""
🔗 ربط API - الخطوة 2

الآن أرسل API_SECRET الخاص بك

⚠️ ملاحظة: سيتم تشفير المفاتيح وتخزينها بشكل آمن
                """)
        elif state == "waiting_for_api_secret":
            # الحصول على API_KEY المحفوظ مؤقتاً
            if hasattr(context, 'user_data') and context.user_data and 'temp_api_key' in context.user_data:
                api_key = context.user_data['temp_api_key']
                api_secret = text
                
                # التحقق من صحة API keys قبل الحفظ
                if update.message is not None:
                    checking_message = await update.message.reply_text("🔄 جاري التحقق من صحة API keys...")
                
                # التحقق من صحة المفاتيح
                is_valid = await check_api_connection(api_key, api_secret)
                
                if is_valid:
                    # حفظ المفاتيح في قاعدة البيانات
                    success = user_manager.update_user_api(user_id, api_key, api_secret)
                    
                    if success:
                        # مسح البيانات المؤقتة
                        del context.user_data['temp_api_key']
                        del user_input_state[user_id]
                        
                        # حذف رسالة التحقق
                        if update.message is not None:
                            await checking_message.delete()
                            await update.message.reply_text("""
✅ تم ربط API بنجاح!

🟢 الاتصال: https://api.bybit.com (Live)
📊 يمكنك الآن استخدام جميع ميزات البوت
🔐 المفاتيح آمنة ومشفرة

استخدم /start للعودة إلى القائمة الرئيسية
                            """)
                    else:
                        if update.message is not None:
                            await checking_message.delete()
                            await update.message.reply_text("❌ فشل في حفظ مفاتيح API. حاول مرة أخرى.")
                else:
                    # المفاتيح غير صحيحة
                    if update.message is not None:
                        await checking_message.delete()
                        await update.message.reply_text("""
❌ API keys غير صحيحة!

🔴 تأكد من:
• صحة API_KEY
• صحة API_SECRET  
• تفعيل API في حساب Bybit
• صلاحيات API (قراءة/كتابة)

🔗 للحصول على مفاتيح جديدة: https://api.bybit.com

استخدم /start للمحاولة مرة أخرى
                        """)
                        # مسح البيانات المؤقتة
                        del context.user_data['temp_api_key']
                        del user_input_state[user_id]
            else:
                if update.message is not None:
                    await update.message.reply_text("❌ خطأ: لم يتم العثور على API_KEY. ابدأ من جديد بـ /start")
                if user_id in user_input_state:
                    del user_input_state[user_id]
        elif state == "waiting_for_trade_amount":
            try:
                amount = float(text)
                if amount > 0:
                    trading_bot.user_settings['trade_amount'] = amount
                    # إعادة تعيين حالة إدخال المستخدم
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث مبلغ التداول إلى: {amount}")
                        await settings_menu(update, context)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال مبلغ أكبر من صفر")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                    
        elif state == "waiting_for_leverage":
            try:
                leverage = int(text)
                if 1 <= leverage <= 100:
                    trading_bot.user_settings['leverage'] = leverage
                    # إعادة تعيين حالة إدخال المستخدم
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث الرافعة المالية إلى: {leverage}x")
                        await settings_menu(update, context)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال قيمة بين 1 و 100")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                    
        elif state == "waiting_for_demo_balance":
            try:
                balance = float(text)
                if balance >= 0:
                    # تحديث رصيد الحساب التجريبي
                    if trading_bot.user_settings['market_type'] == 'futures':
                        trading_bot.demo_account_futures.update_balance(balance)
                    else:
                        trading_bot.demo_account_spot.update_balance(balance)
                    # إعادة تعيين حالة إدخال المستخدم
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث رصيد الحساب التجريبي إلى: {balance}")
                        await settings_menu(update, context)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال رصيد غير سالب")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        else:
            # إعادة تعيين حالة إدخال المستخدم للحالات غير المتوقعة
            if user_id is not None and user_id in user_input_state:
                del user_input_state[user_id]
    
    elif text == "⚙️ الإعدادات":
        await settings_menu(update, context)
    elif text == "📊 حالة الحساب":
        await account_status(update, context)
    elif text == "🔄 الصفقات المفتوحة" or "الصفقات المفتوحة" in text or "🔄" in text:
        await open_positions(update, context)
    elif text == "📈 تاريخ التداول":
        await trade_history(update, context)
    elif text == "💰 المحفظة":
        await wallet_overview(update, context)
    elif text == "▶️ تشغيل البوت":
        trading_bot.is_running = True
        if update.message is not None:
            await update.message.reply_text("✅ تم تشغيل البوت")
    elif text == "⏹️ إيقاف البوت":
        trading_bot.is_running = False
        if update.message is not None:
            await update.message.reply_text("⏹️ تم إيقاف البوت")
    elif text == "📊 إحصائيات الإشارات":
        # عرض إحصائيات الإشارات
        message = f"""
📊 إحصائيات الإشارات:

📈 إشارات مستلمة: {trading_bot.signals_received}
✅ صفقات مفتوحة: {len(trading_bot.open_positions)}
        """
        if update.message is not None:
            await update.message.reply_text(message)
    elif text == "🔄 تحديث الأزواج":
        try:
            await trading_bot.update_available_pairs()
            if update.message is not None:
                await update.message.reply_text("✅ تم تحديث قائمة الأزواج المتاحة")
        except Exception as e:
            if update.message is not None:
                await update.message.reply_text(f"❌ فشل في تحديث الأزواج: {e}")
    elif text == "💳 تعديل الرصيد":
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_demo_balance"
        if update.message is not None:
            await update.message.reply_text("💳 أدخل الرصيد الجديد:")
    elif text.replace('.', '', 1).isdigit():  # التحقق مما إذا كان النص رقمًا
        # معالجة إدخال الأرقام (للإعدادات)
        try:
            number = float(text)
            # هنا يمكننا تنفيذ منطق لتحديث الإعدادات بناءً على السياق
            # مثلاً، إذا كنا ننتظر إدخال مبلغ التداول أو رصيد الحساب
            if update.message is not None:
                await update.message.reply_text(f"✅ تم استلام الرقم: {number}")
        except ValueError:
            if update.message is not None:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
    else:
        # معالجة أي نصوص أخرى
        # تصحيح المشكلة مع زر الصفقات المفتوحة - إضافة تصحيح إضافي
        if "الصفقات المفتوحة" in text or "🔄" in text:
            await open_positions(update, context)
        elif update.message is not None:
            # تصحيح مؤقت لإظهار النص الفعلي لتتبع المشكلة
            await update.message.reply_text(f"❌ أمر غير مدعوم: '{text}'")

# دالة لمعالجة الإشارات الخارجية
async def process_external_signal(symbol: str, action: str):
    """معالجة إشارة خارجية"""
    signal_data = {
        'symbol': symbol,
        'action': action
    }
    await trading_bot.process_signal(signal_data)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """الدالة الرئيسية"""
    # إعداد Telegram bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(error_handler)
    
    # تحديث الأزواج عند البدء
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trading_bot.update_available_pairs())
    except Exception as e:
        logger.error(f"خطأ في تحديث الأزواج: {e}")
    
    # بدء التحديث الدوري للأسعار
    def start_price_updates():
        """بدء التحديث الدوري للأسعار"""
        def update_prices():
            while True:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(trading_bot.update_open_positions_prices())
                    loop.close()
                    time.sleep(30)  # تحديث كل 30 ثانية
                except Exception as e:
                    logger.error(f"خطأ في التحديث الدوري: {e}")
                    time.sleep(60)  # انتظار دقيقة في حالة الخطأ
        
        threading.Thread(target=update_prices, daemon=True).start()
    
    # بدء التحديث الدوري
    start_price_updates()
    
    # تشغيل البوت
    logger.info("بدء تشغيل البوت...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()