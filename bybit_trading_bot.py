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
from dataclasses import dataclass, field
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
    
    def get_open_positions(self, category: str = "spot", symbol: str = None) -> List[dict]:
        """جلب الصفقات المفتوحة من المنصة"""
        try:
            endpoint = "/v5/position/list"
            api_category = "linear" if category == "futures" else category
            
            params = {"category": api_category}
            if symbol:
                params["symbol"] = symbol
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                result = response.get("result", {})
                positions = result.get("list", [])
                # فلترة الصفقات المفتوحة فقط (حجم > 0)
                open_positions = [p for p in positions if float(p.get("size", 0)) > 0]
                logger.info(f"تم جلب {len(open_positions)} صفقة مفتوحة من المنصة")
                return open_positions
            
            logger.warning(f"فشل جلب الصفقات: {response.get('retMsg')}")
            return []
            
        except Exception as e:
            logger.error(f"خطأ في جلب الصفقات المفتوحة: {e}")
            return []
    
    def get_wallet_balance(self, account_type: str = "UNIFIED") -> dict:
        """جلب رصيد المحفظة"""
        try:
            endpoint = "/v5/account/wallet-balance"
            params = {"accountType": account_type}
            
            response = self._make_request("GET", endpoint, params)
            
            if response.get("retCode") == 0:
                return response.get("result", {})
            
            return {}
            
        except Exception as e:
            logger.error(f"خطأ في جلب الرصيد: {e}")
            return {}
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, price: Optional[str] = None, category: str = "spot", stop_loss: Optional[str] = None, take_profit: Optional[str] = None) -> dict:
        """وضع أمر تداول مع دعم TP/SL"""
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
            
            # إضافة Stop Loss و Take Profit إن وجدا
            if stop_loss:
                params["stopLoss"] = stop_loss
            if take_profit:
                params["takeProfit"] = take_profit
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في وضع الأمر: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def set_trading_stop(self, symbol: str, category: str = "linear", stop_loss: Optional[str] = None, take_profit: Optional[str] = None, trailing_stop: Optional[str] = None, position_idx: int = 0) -> dict:
        """تعيين Stop Loss / Take Profit / Trailing Stop لصفقة مفتوحة"""
        try:
            endpoint = "/v5/position/trading-stop"
            api_category = "linear" if category == "futures" else category
            
            params = {
                "category": api_category,
                "symbol": symbol,
                "positionIdx": position_idx  # 0 = One-Way Mode
            }
            
            if stop_loss:
                params["stopLoss"] = stop_loss
            if take_profit:
                params["takeProfit"] = take_profit
            if trailing_stop:
                params["trailingStop"] = trailing_stop
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في تعيين Trading Stop: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def close_position(self, symbol: str, category: str = "linear", qty: Optional[str] = None) -> dict:
        """إغلاق صفقة (كامل أو جزئي)"""
        try:
            # إذا لم يتم تحديد الكمية، سيتم إغلاق الصفقة بالكامل
            endpoint = "/v5/order/create"
            api_category = "linear" if category == "futures" else category
            
            # الحصول على معلومات الصفقة الحالية لمعرفة الاتجاه
            positions = self.get_open_positions(category, symbol)
            if not positions:
                return {"retCode": -1, "retMsg": "لا توجد صفقة مفتوحة"}
            
            position = positions[0]
            side = position.get("side", "")
            size = position.get("size", "0")
            
            # عكس الاتجاه للإغلاق
            close_side = "Sell" if side == "Buy" else "Buy"
            close_qty = qty if qty else size
            
            params = {
                "category": api_category,
                "symbol": symbol,
                "side": close_side,
                "orderType": "Market",
                "qty": close_qty,
                "reduceOnly": True  # مهم: للإغلاق فقط وليس فتح صفقة جديدة
            }
            
            response = self._make_request("POST", endpoint, params)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
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


# ==================== إدارة أدوات الصفقات المتقدمة ====================

@dataclass
class TakeProfitLevel:
    """مستوى هدف الربح"""
    price: float  # السعر المستهدف
    percentage: float  # نسبة الإغلاق (مثال: 50 = 50%)
    hit: bool = False  # تم تحقيق الهدف؟
    hit_time: Optional[datetime] = None  # وقت تحقيق الهدف
    
    def __post_init__(self):
        """التحقق من صحة البيانات"""
        if self.percentage <= 0 or self.percentage > 100:
            raise ValueError(f"نسبة الإغلاق يجب أن تكون بين 0 و 100، القيمة: {self.percentage}")


@dataclass
class StopLoss:
    """وقف الخسارة"""
    price: float  # سعر وقف الخسارة
    initial_price: float  # السعر الأصلي
    is_trailing: bool = False  # هل هو trailing stop؟
    trailing_distance: float = 0.0  # المسافة بالنسبة المئوية
    moved_to_breakeven: bool = False  # تم نقله للتعادل؟
    last_update: Optional[datetime] = None  # آخر تحديث
    
    def update_trailing(self, current_price: float, side: str):
        """تحديث trailing stop"""
        if not self.is_trailing or self.trailing_distance <= 0:
            return False
        
        try:
            if side.lower() == "buy":
                # في صفقة الشراء، الـ stop يرتفع مع السعر
                new_stop = current_price * (1 - self.trailing_distance / 100)
                if new_stop > self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"✅ تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
            else:  # sell
                # في صفقة البيع، الـ stop ينخفض مع السعر
                new_stop = current_price * (1 + self.trailing_distance / 100)
                if new_stop < self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"✅ تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
        except Exception as e:
            logger.error(f"خطأ في تحديث trailing stop: {e}")
        
        return False
    
    def move_to_breakeven(self, entry_price: float):
        """نقل وقف الخسارة إلى نقطة التعادل"""
        if not self.moved_to_breakeven:
            self.price = entry_price
            self.moved_to_breakeven = True
            self.last_update = datetime.now()
            logger.info(f"🔒 تم نقل Stop Loss إلى نقطة التعادل: {entry_price:.6f}")
            return True
        return False


@dataclass
class PositionManagement:
    """إدارة متقدمة للصفقة"""
    position_id: str
    symbol: str
    side: str  # buy or sell
    entry_price: float
    quantity: float  # الكمية الأصلية
    remaining_quantity: float  # الكمية المتبقية
    market_type: str  # spot or futures
    leverage: int = 1
    
    # أدوات الإدارة
    take_profits: List[TakeProfitLevel] = field(default_factory=list)
    stop_loss: Optional[StopLoss] = None
    
    # حالة الصفقة
    total_closed_percentage: float = 0.0
    realized_pnl: float = 0.0
    closed_parts: List[Dict] = field(default_factory=list)
    
    def add_take_profit(self, price: float, percentage: float) -> bool:
        """إضافة مستوى هدف ربح"""
        try:
            # التحقق من أن السعر في الاتجاه الصحيح
            if self.side.lower() == "buy" and price <= self.entry_price:
                logger.error(f"سعر TP يجب أن يكون أعلى من سعر الدخول في صفقة الشراء")
                return False
            elif self.side.lower() == "sell" and price >= self.entry_price:
                logger.error(f"سعر TP يجب أن يكون أقل من سعر الدخول في صفقة البيع")
                return False
            
            # التحقق من أن مجموع النسب لا يتجاوز 100%
            total_percentage = sum(tp.percentage for tp in self.take_profits if not tp.hit) + percentage
            if total_percentage > 100:
                logger.error(f"مجموع نسب TP يتجاوز 100% ({total_percentage}%)")
                return False
            
            tp = TakeProfitLevel(price=price, percentage=percentage)
            self.take_profits.append(tp)
            # ترتيب حسب السعر
            self.take_profits.sort(key=lambda x: x.price if self.side.lower() == "buy" else -x.price)
            logger.info(f"✅ تم إضافة TP: {price:.6f} ({percentage}%)")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة take profit: {e}")
            return False
    
    def set_stop_loss(self, price: float, is_trailing: bool = False, 
                     trailing_distance: float = 0.0) -> bool:
        """تعيين وقف الخسارة"""
        try:
            # التحقق من أن السعر في الاتجاه الصحيح
            if self.side.lower() == "buy" and price >= self.entry_price:
                logger.error(f"سعر SL يجب أن يكون أقل من سعر الدخول في صفقة الشراء")
                return False
            elif self.side.lower() == "sell" and price <= self.entry_price:
                logger.error(f"سعر SL يجب أن يكون أعلى من سعر الدخول في صفقة البيع")
                return False
            
            self.stop_loss = StopLoss(
                price=price,
                initial_price=price,
                is_trailing=is_trailing,
                trailing_distance=trailing_distance,
                last_update=datetime.now()
            )
            logger.info(f"✅ تم تعيين SL: {price:.6f} {'(Trailing)' if is_trailing else ''}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين stop loss: {e}")
            return False
    
    def check_and_execute_tp(self, current_price: float) -> List[Dict]:
        """التحقق من تحقيق أهداف الربح وتنفيذها"""
        executed = []
        
        for tp in self.take_profits:
            if tp.hit:
                continue
            
            # التحقق من تحقيق الهدف
            hit = False
            if self.side.lower() == "buy":
                hit = current_price >= tp.price
            else:  # sell
                hit = current_price <= tp.price
            
            if hit:
                # حساب الكمية المغلقة
                close_qty = (self.quantity * tp.percentage / 100)
                
                # حساب الربح
                if self.side.lower() == "buy":
                    pnl = (current_price - self.entry_price) * close_qty
                else:
                    pnl = (self.entry_price - current_price) * close_qty
                
                # تسجيل الإغلاق
                tp.hit = True
                tp.hit_time = datetime.now()
                self.total_closed_percentage += tp.percentage
                self.remaining_quantity -= close_qty
                self.realized_pnl += pnl
                
                close_info = {
                    'type': 'take_profit',
                    'price': current_price,
                    'tp_target': tp.price,
                    'percentage': tp.percentage,
                    'quantity': close_qty,
                    'pnl': pnl,
                    'time': tp.hit_time
                }
                self.closed_parts.append(close_info)
                executed.append(close_info)
                
                logger.info(f"🎯 تم تحقيق TP عند {current_price:.6f}: إغلاق {tp.percentage}% بربح {pnl:.2f}")
                
                # نقل SL للتعادل بعد أول هدف
                if len(executed) == 1 and self.stop_loss and not self.stop_loss.moved_to_breakeven:
                    self.stop_loss.move_to_breakeven(self.entry_price)
        
        return executed
    
    def check_stop_loss(self, current_price: float) -> Optional[Dict]:
        """التحقق من تفعيل وقف الخسارة"""
        if not self.stop_loss:
            return None
        
        # تحديث trailing stop إذا كان مفعلاً
        if self.stop_loss.is_trailing:
            self.stop_loss.update_trailing(current_price, self.side)
        
        # التحقق من تفعيل Stop Loss
        hit = False
        if self.side.lower() == "buy":
            hit = current_price <= self.stop_loss.price
        else:  # sell
            hit = current_price >= self.stop_loss.price
        
        if hit:
            # حساب الخسارة
            if self.side.lower() == "buy":
                pnl = (current_price - self.entry_price) * self.remaining_quantity
            else:
                pnl = (self.entry_price - current_price) * self.remaining_quantity
            
            self.realized_pnl += pnl
            
            sl_info = {
                'type': 'stop_loss',
                'price': current_price,
                'sl_target': self.stop_loss.price,
                'percentage': 100 - self.total_closed_percentage,
                'quantity': self.remaining_quantity,
                'pnl': pnl,
                'time': datetime.now(),
                'was_breakeven': self.stop_loss.moved_to_breakeven
            }
            
            logger.warning(f"🛑 تم تفعيل SL عند {current_price:.6f}: {pnl:.2f}")
            
            return sl_info
        
        return None
    
    def get_status_message(self, current_price: float) -> str:
        """الحصول على رسالة حالة الصفقة"""
        try:
            unrealized_pnl = 0.0
            if self.side.lower() == "buy":
                unrealized_pnl = (current_price - self.entry_price) * self.remaining_quantity
            else:
                unrealized_pnl = (self.entry_price - current_price) * self.remaining_quantity
            
            total_pnl = self.realized_pnl + unrealized_pnl
            
            message = f"📊 **إدارة الصفقة: {self.symbol}**\n\n"
            message += f"🔄 النوع: {self.side.upper()}\n"
            message += f"💲 سعر الدخول: {self.entry_price:.6f}\n"
            message += f"💲 السعر الحالي: {current_price:.6f}\n"
            message += f"📈 الكمية الأصلية: {self.quantity:.6f}\n"
            message += f"📉 المتبقي: {self.remaining_quantity:.6f} ({100 - self.total_closed_percentage:.1f}%)\n\n"
            
            # الأهداف
            message += "🎯 **أهداف الربح:**\n"
            for i, tp in enumerate(self.take_profits, 1):
                status = "✅" if tp.hit else "⏳"
                distance = ((tp.price - current_price) / current_price) * 100
                message += f"  {status} TP{i}: {tp.price:.6f} ({tp.percentage}%) - "
                message += f"{'تم تحقيقه' if tp.hit else f'{abs(distance):.2f}% متبقي'}\n"
            
            # وقف الخسارة
            if self.stop_loss:
                distance = ((current_price - self.stop_loss.price) / current_price) * 100
                sl_type = ""
                if self.stop_loss.is_trailing:
                    sl_type = " (Trailing)"
                if self.stop_loss.moved_to_breakeven:
                    sl_type += " [BE]"
                
                message += f"\n🛑 **Stop Loss:** {self.stop_loss.price:.6f}{sl_type}\n"
                message += f"   المسافة: {abs(distance):.2f}%\n"
            
            # الأرباح/الخسائر
            message += f"\n💰 **النتائج:**\n"
            message += f"  الربح المحقق: {self.realized_pnl:.2f}\n"
            message += f"  الربح غير المحقق: {unrealized_pnl:.2f}\n"
            message += f"  الإجمالي: {total_pnl:.2f}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء رسالة الحالة: {e}")
            return "❌ خطأ في عرض حالة الصفقة"
    
    def calculate_risk_reward_ratio(self) -> float:
        """حساب نسبة المخاطرة إلى العائد"""
        if not self.stop_loss or not self.take_profits:
            return 0.0
        
        try:
            # حساب المخاطرة
            if self.side.lower() == "buy":
                risk = self.entry_price - self.stop_loss.initial_price
            else:
                risk = self.stop_loss.initial_price - self.entry_price
            
            # حساب العائد المتوقع (متوسط جميع الأهداف)
            total_reward = 0.0
            for tp in self.take_profits:
                if self.side.lower() == "buy":
                    reward = tp.price - self.entry_price
                else:
                    reward = self.entry_price - tp.price
                total_reward += reward * (tp.percentage / 100)
            
            if risk > 0:
                rr_ratio = total_reward / risk
                return rr_ratio
            
        except Exception as e:
            logger.error(f"خطأ في حساب R:R: {e}")
        
        return 0.0


class TradeToolsManager:
    """مدير أدوات التداول"""
    
    def __init__(self):
        self.managed_positions: Dict[str, PositionManagement] = {}
        # الإعدادات الافتراضية التلقائية
        self.auto_apply_enabled: bool = False
        self.default_tp_percentages: List[float] = []
        self.default_tp_close_percentages: List[float] = []
        self.default_sl_percentage: float = 0
        self.default_trailing_enabled: bool = False
        self.default_trailing_distance: float = 2.0
        self.auto_breakeven_on_tp1: bool = True
        logger.info("✅ تم تهيئة TradeToolsManager")
    
    def create_managed_position(self, position_id: str, symbol: str, side: str,
                               entry_price: float, quantity: float, market_type: str,
                               leverage: int = 1) -> Optional[PositionManagement]:
        """إنشاء صفقة مدارة"""
        try:
            if position_id in self.managed_positions:
                logger.warning(f"الصفقة {position_id} موجودة بالفعل")
                return self.managed_positions[position_id]
            
            pm = PositionManagement(
                position_id=position_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                remaining_quantity=quantity,
                market_type=market_type,
                leverage=leverage
            )
            
            self.managed_positions[position_id] = pm
            logger.info(f"✅ تم إنشاء إدارة للصفقة {position_id}")
            return pm
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء صفقة مدارة: {e}")
            return None
    
    def get_managed_position(self, position_id: str) -> Optional[PositionManagement]:
        """الحصول على صفقة مدارة"""
        return self.managed_positions.get(position_id)
    
    def remove_managed_position(self, position_id: str) -> bool:
        """إزالة صفقة مدارة"""
        if position_id in self.managed_positions:
            del self.managed_positions[position_id]
            logger.info(f"✅ تم إزالة إدارة الصفقة {position_id}")
            return True
        return False
    
    def update_all_positions(self, prices: Dict[str, float]) -> Dict[str, List[Dict]]:
        """تحديث جميع الصفقات المدارة"""
        results = {}
        
        for position_id, pm in list(self.managed_positions.items()):
            if pm.symbol in prices:
                current_price = prices[pm.symbol]
                
                # التحقق من الأهداف
                tp_executions = pm.check_and_execute_tp(current_price)
                
                # التحقق من وقف الخسارة
                sl_execution = pm.check_stop_loss(current_price)
                
                if tp_executions or sl_execution:
                    results[position_id] = {
                        'take_profits': tp_executions,
                        'stop_loss': sl_execution
                    }
                
                # إزالة الصفقة إذا تم إغلاقها بالكامل
                if pm.remaining_quantity <= 0 or sl_execution:
                    self.remove_managed_position(position_id)
        
        return results
    
    def set_default_levels(self, position_id: str, tp_percentages: List[float] = None,
                          sl_percentage: float = 2.0, trailing: bool = False) -> bool:
        """تعيين مستويات افتراضية ذكية"""
        pm = self.get_managed_position(position_id)
        if not pm:
            return False
        
        try:
            # مستويات TP افتراضية
            if tp_percentages is None:
                tp_percentages = [1.5, 3.0, 5.0]  # أهداف بنسب متزايدة
            
            partial_percentages = [50, 30, 20]  # نسب الإغلاق
            
            for i, tp_pct in enumerate(tp_percentages):
                if i >= len(partial_percentages):
                    break
                
                if pm.side.lower() == "buy":
                    tp_price = pm.entry_price * (1 + tp_pct / 100)
                else:
                    tp_price = pm.entry_price * (1 - tp_pct / 100)
                
                pm.add_take_profit(tp_price, partial_percentages[i])
            
            # Stop Loss افتراضي
            if pm.side.lower() == "buy":
                sl_price = pm.entry_price * (1 - sl_percentage / 100)
            else:
                sl_price = pm.entry_price * (1 + sl_percentage / 100)
            
            pm.set_stop_loss(sl_price, is_trailing=trailing, trailing_distance=sl_percentage)
            
            logger.info(f"✅ تم تعيين مستويات افتراضية للصفقة {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين المستويات الافتراضية: {e}")
            return False
    
    def save_auto_settings(self, tp_percentages: List[float], tp_close_percentages: List[float],
                          sl_percentage: float, trailing_enabled: bool = False, 
                          trailing_distance: float = 2.0, breakeven_on_tp1: bool = True) -> bool:
        """حفظ الإعدادات الافتراضية للتطبيق التلقائي"""
        try:
            self.default_tp_percentages = tp_percentages.copy()
            self.default_tp_close_percentages = tp_close_percentages.copy()
            self.default_sl_percentage = sl_percentage
            self.default_trailing_enabled = trailing_enabled
            self.default_trailing_distance = trailing_distance
            self.auto_breakeven_on_tp1 = breakeven_on_tp1
            
            logger.info(f"✅ تم حفظ الإعدادات التلقائية: TP={tp_percentages}, SL={sl_percentage}%")
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ الإعدادات التلقائية: {e}")
            return False
    
    def enable_auto_apply(self):
        """تفعيل التطبيق التلقائي"""
        self.auto_apply_enabled = True
        logger.info("✅ تم تفعيل التطبيق التلقائي للإعدادات")
    
    def disable_auto_apply(self):
        """تعطيل التطبيق التلقائي"""
        self.auto_apply_enabled = False
        logger.info("⏸️ تم تعطيل التطبيق التلقائي للإعدادات")
    
    def apply_auto_settings_to_position(self, position_id: str, symbol: str, side: str,
                                       entry_price: float, quantity: float, 
                                       market_type: str, leverage: int = 1) -> bool:
        """تطبيق الإعدادات التلقائية على صفقة جديدة"""
        if not self.auto_apply_enabled:
            return False
        
        try:
            # إنشاء إدارة الصفقة
            pm = self.create_managed_position(position_id, symbol, side, entry_price, 
                                             quantity, market_type, leverage)
            if not pm:
                return False
            
            # تطبيق أهداف الربح
            if self.default_tp_percentages and self.default_tp_close_percentages:
                for i, tp_pct in enumerate(self.default_tp_percentages):
                    if i >= len(self.default_tp_close_percentages):
                        break
                    
                    if side.lower() == "buy":
                        tp_price = entry_price * (1 + tp_pct / 100)
                    else:
                        tp_price = entry_price * (1 - tp_pct / 100)
                    
                    pm.add_take_profit(tp_price, self.default_tp_close_percentages[i] / 100)
            
            # تطبيق Stop Loss
            if self.default_sl_percentage > 0:
                if side.lower() == "buy":
                    sl_price = entry_price * (1 - self.default_sl_percentage / 100)
                else:
                    sl_price = entry_price * (1 + self.default_sl_percentage / 100)
                
                pm.set_stop_loss(sl_price, 
                               is_trailing=self.default_trailing_enabled,
                               trailing_distance=self.default_trailing_distance)
            
            logger.info(f"✅ تم تطبيق الإعدادات التلقائية على الصفقة {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق الإعدادات التلقائية: {e}")
            return False
    
    def get_auto_settings_summary(self) -> str:
        """الحصول على ملخص الإعدادات التلقائية"""
        if not self.auto_apply_enabled:
            return "⏸️ **التطبيق التلقائي معطل**"
        
        summary = "✅ **التطبيق التلقائي مُفعّل**\n\n"
        
        if self.default_tp_percentages:
            summary += "🎯 **أهداف الربح:**\n"
            for i, (tp, close) in enumerate(zip(self.default_tp_percentages, 
                                               self.default_tp_close_percentages), 1):
                summary += f"• TP{i}: +{tp}% → إغلاق {close}%\n"
        else:
            summary += "🎯 **أهداف الربح:** غير محددة\n"
        
        summary += "\n"
        
        if self.default_sl_percentage > 0:
            sl_type = "⚡ Trailing" if self.default_trailing_enabled else "🛑 ثابت"
            summary += f"🛑 **Stop Loss:** {sl_type} عند -{self.default_sl_percentage}%\n"
            
            if self.default_trailing_enabled:
                summary += f"   المسافة: {self.default_trailing_distance}%\n"
        else:
            summary += "🛑 **Stop Loss:** غير محدد\n"
        
        if self.auto_breakeven_on_tp1:
            summary += "\n🔁 **نقل تلقائي للتعادل** عند تحقيق TP1"
        
        return summary


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
            # جمع جميع الصفقات من المصادر المختلفة
            all_positions = {}
            
            # إضافة الصفقات من trading_bot.open_positions
            all_positions.update(self.open_positions)
            
            # إضافة صفقات جميع المستخدمين من user_manager
            from user_manager import user_manager
            for user_id, user_positions in user_manager.user_positions.items():
                all_positions.update(user_positions)
            
            if not all_positions:
                return
            
            # جمع الرموز الفريدة من الصفقات المفتوحة مع نوع السوق
            symbols_to_update = {}  # {symbol: market_type}
            for position_info in all_positions.values():
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
                
                # تحديث صفقات المستخدمين في user_manager
                for user_id, user_positions in user_manager.user_positions.items():
                    for position_id, position_info in user_positions.items():
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
        """
        إرسال إشارة المطور لجميع المتابعين مع فتح صفقات تلقائية
        يدعم: market_type, leverage, amount من إعدادات الإشارة
        """
        try:
            # الحصول على قائمة المتابعين
            followers = developer_manager.get_followers(developer_id)
            
            if not followers:
                logger.info("لا يوجد متابعين لإرسال الإشارة")
                return
            
            logger.info(f"📡 إرسال إشارة المطور إلى {len(followers)} متابع")
            logger.info(f"📊 تفاصيل الإشارة: {signal_data}")
            
            # الحصول على السعر الحالي للرمز
            current_price = self.get_current_price(signal_data.get('symbol', 'BTCUSDT'))
            price = current_price.get('price', 0) if current_price else 0
            
            # إرسال الإشارة لكل متابع
            success_count = 0
            failed_count = 0
            
            for follower_id in followers:
                try:
                    logger.info(f"🔍 معالجة المتابع {follower_id}...")
                    
                    # التحقق من وجود المتابع ونشاطه
                    follower_data = user_manager.get_user(follower_id)
                    if not follower_data:
                        logger.warning(f"⚠️ المتابع {follower_id} غير موجود في user_manager")
                        # محاولة التحميل من قاعدة البيانات
                        from database import db_manager
                        follower_data = db_manager.get_user(follower_id)
                        if follower_data:
                            logger.info(f"✅ تم تحميل المتابع {follower_id} من قاعدة البيانات")
                        else:
                            logger.error(f"❌ المتابع {follower_id} غير موجود في قاعدة البيانات أيضاً")
                            failed_count += 1
                            continue
                    
                    logger.info(f"📊 المتابع {follower_id}: is_active={follower_data.get('is_active')}, market_type={follower_data.get('market_type')}")
                    
                    if not follower_data.get('is_active', False):
                        logger.warning(f"⏸️ المتابع {follower_id} غير نشط (is_active=False) - تم التخطي")
                        failed_count += 1
                        continue
                    
                    # إنشاء TradingBot مؤقت للمتابع
                    logger.info(f"🤖 إنشاء bot للمتابع {follower_id}...")
                    follower_bot = TradingBot()
                    follower_bot.user_id = follower_id
                    
                    # الحصول على إعدادات المتابع
                    follower_settings = user_manager.get_user_settings(follower_id)
                    if follower_settings:
                        logger.info(f"⚙️ إعدادات المتابع {follower_id}: {follower_settings}")
                        follower_bot.user_settings = follower_settings
                        
                        # تطبيق إعدادات الإشارة (تجاوز إعدادات المستخدم إذا كانت موجودة في الإشارة)
                        if 'market_type' in signal_data:
                            follower_bot.user_settings['market_type'] = signal_data['market_type']
                            logger.info(f"📊 تطبيق market_type من الإشارة: {signal_data['market_type']}")
                        
                        if 'leverage' in signal_data:
                            follower_bot.user_settings['leverage'] = signal_data['leverage']
                            logger.info(f"⚡ تطبيق leverage من الإشارة: {signal_data['leverage']}")
                        
                        if 'amount' in signal_data:
                            follower_bot.user_settings['trade_amount'] = signal_data['amount']
                            logger.info(f"💰 تطبيق trade_amount من الإشارة: {signal_data['amount']}")
                    else:
                        logger.warning(f"⚠️ لم يتم العثور على إعدادات للمتابع {follower_id}")
                    
                    # إضافة السعر للإشارة
                    enriched_signal = signal_data.copy()
                    enriched_signal['price'] = price
                    
                    logger.info(f"📡 إرسال الإشارة للمتابع {follower_id}: {enriched_signal}")
                    
                    # تنفيذ الإشارة على حساب المتابع
                    await follower_bot.process_signal(enriched_signal)
                    success_count += 1
                    logger.info(f"✅ تم تنفيذ الإشارة بنجاح للمتابع {follower_id} - Market: {follower_bot.user_settings.get('market_type', 'spot')}")
                    
                    # إرسال إشعار للمتابع
                    try:
                        from telegram import Bot
                        bot = Bot(token=TELEGRAM_TOKEN)
                        
                        market_emoji = "📈" if signal_data.get('market_type') == 'spot' else "🚀"
                        action_emoji = "🟢" if signal_data.get('action') == 'buy' else "🔴"
                        
                        notification_message = f"""
📡 إشارة جديدة من Nagdat!

{action_emoji} الإجراء: {signal_data.get('action', 'N/A').upper()}
💎 الرمز: {signal_data.get('symbol', 'N/A')}
💲 السعر: {price:.2f}
{market_emoji} السوق: {signal_data.get('market_type', 'spot').upper()}
💰 المبلغ: {signal_data.get('amount', 100)}
"""
                        if signal_data.get('market_type') == 'futures':
                            notification_message += f"⚡ الرافعة: {signal_data.get('leverage', 10)}x\n"
                        
                        notification_message += "\n⚡ تم تنفيذ الصفقة تلقائياً على حسابك!"
                        
                        await bot.send_message(
                            chat_id=follower_id,
                            text=notification_message
                        )
                    except Exception as notify_error:
                        logger.error(f"خطأ في إرسال الإشعار للمتابع {follower_id}: {notify_error}")
                        
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال الإشارة للمتابع {follower_id}: {e}")
                    failed_count += 1
            
            # إرسال تقرير مفصل للمطور
            market_emoji = "📈" if signal_data.get('market_type') == 'spot' else "🚀"
            
            message = f"""
📡 تم توزيع الإشارة

✅ نجح: {success_count} 
❌ فشل: {failed_count}
📊 الإجمالي: {len(followers)} متابع

📊 تفاصيل الإشارة:
💎 الرمز: {signal_data.get('symbol', 'N/A')}
{market_emoji} السوق: {signal_data.get('market_type', 'spot').upper()}
🔄 الإجراء: {signal_data.get('action', 'N/A').upper()}
💰 المبلغ: {signal_data.get('amount', 100)}
"""
            if signal_data.get('market_type') == 'futures':
                message += f"⚡ الرافعة: {signal_data.get('leverage', 10)}x\n"
            
            await self.send_message_to_admin(message)
            
            return {
                'success': True,
                'sent_to': success_count,
                'failed': failed_count,
                'total_followers': len(followers)
            }
            
        except Exception as e:
            logger.error(f"خطأ في broadcast_signal_to_followers: {e}")
            import traceback
            traceback.print_exc()
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
            
            # تحويل الإشارة إذا كانت بالتنسيق الجديد
            from signal_converter import convert_simple_signal, validate_simple_signal
            
            # التحقق من نوع الإشارة (جديدة أو قديمة)
            if 'signal' in signal_data and 'action' not in signal_data:
                logger.info(f"📡 استقبال إشارة جديدة بالتنسيق البسيط: {signal_data}")
                
                # التحقق من صحة الإشارة
                is_valid, validation_message = validate_simple_signal(signal_data)
                
                if not is_valid:
                    logger.error(f"❌ إشارة غير صحيحة: {validation_message}")
                    await self.send_message_to_admin(
                        f"❌ إشارة غير صحيحة\n\n"
                        f"📋 التفاصيل: {validation_message}\n"
                        f"📥 البيانات: {signal_data}"
                    )
                    return
                
                # تحويل الإشارة إلى التنسيق الداخلي
                converted_signal = convert_simple_signal(signal_data, self.user_settings)
                
                if not converted_signal:
                    logger.error(f"❌ فشل تحويل الإشارة")
                    await self.send_message_to_admin(
                        f"❌ فشل تحويل الإشارة\n\n"
                        f"📥 البيانات الأصلية: {signal_data}"
                    )
                    return
                
                logger.info(f"✅ تم تحويل الإشارة بنجاح: {converted_signal}")
                signal_data = converted_signal
            
            # حفظ بيانات الإشارة للاستخدام في execute_demo_trade
            self._current_signal_data = signal_data
            
            symbol = signal_data.get('symbol', '').upper()
            action = signal_data.get('action', '').lower()  # buy أو sell أو close
            
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
            
            # 🔍 التحقق من وجود الرمز في منصة Bybit
            logger.info(f"🔍 التحقق من وجود الرمز {symbol} في Bybit {user_market_type.upper()}")
            
            symbol_exists_in_bybit = False
            
            if self.bybit_api:
                # التحقق المباشر من Bybit API
                symbol_exists_in_bybit = self.bybit_api.check_symbol_exists(symbol, bybit_category)
                logger.info(f"نتيجة التحقق من Bybit API: {symbol_exists_in_bybit}")
            else:
                # إذا لم يكن API متاحاً، استخدم القائمة المحلية
                if user_market_type == "spot" and symbol in self.available_pairs.get('spot', []):
                    symbol_exists_in_bybit = True
                elif user_market_type == "futures" and (symbol in self.available_pairs.get('futures', []) or symbol in self.available_pairs.get('inverse', [])):
                    symbol_exists_in_bybit = True
                    if symbol in self.available_pairs.get('inverse', []):
                        bybit_category = "inverse"
            
            # إذا لم يكن الرمز موجوداً في Bybit
            if not symbol_exists_in_bybit:
                # جمع الأزواج المتاحة للنوع المحدد
                available_pairs = self.available_pairs.get(user_market_type, [])
                if user_market_type == "futures":
                    available_pairs = self.available_pairs.get('futures', []) + self.available_pairs.get('inverse', [])
                
                pairs_list = ", ".join(available_pairs[:20])
                error_message = f"❌ الرمز {symbol} غير موجود في منصة Bybit!\n\n"
                error_message += f"🏪 نوع السوق: {user_market_type.upper()}\n"
                error_message += f"📋 أمثلة للأزواج المتاحة:\n{pairs_list}..."
                await self.send_message_to_admin(error_message)
                logger.warning(f"الرمز {symbol} غير موجود في Bybit {user_market_type}")
                return
            
            logger.info(f"✅ الرمز {symbol} موجود في Bybit {user_market_type.upper()}")
            
            # الحصول على السعر الحالي
            if self.bybit_api:
                current_price = self.bybit_api.get_ticker_price(symbol, bybit_category)
                if current_price is None:
                    await self.send_message_to_admin(f"❌ فشل في الحصول على سعر {symbol} من Bybit")
                    return
                logger.info(f"💲 سعر {symbol} الحالي: {current_price}")
            else:
                # استخدام سعر وهمي للاختبار فقط (عند عدم وجود API)
                current_price = 100.0
                logger.warning("استخدام سعر وهمي - API غير متاح")
            
            # 🎯 تنفيذ الصفقة بناءً على نوع الحساب
            account_type = self.user_settings['account_type']
            
            if account_type == 'real':
                # حساب حقيقي - التنفيذ عبر Bybit API
                logger.info(f"🔴 تنفيذ صفقة حقيقية عبر Bybit API")
                await self.execute_real_trade(symbol, action, current_price, bybit_category)
            else:
                # حساب تجريبي - التنفيذ داخل البوت
                logger.info(f"🟢 تنفيذ صفقة تجريبية داخل البوت")
                await self.execute_demo_trade(symbol, action, current_price, bybit_category, market_type)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            await self.send_message_to_admin(f"❌ خطأ في معالجة الإشارة: {e}")
    
    async def execute_real_trade(self, symbol: str, action: str, price: float, category: str):
        """تنفيذ صفقة حقيقية عبر Bybit API مع تطبيق TP/SL التلقائي"""
        try:
            if not self.bybit_api:
                await self.send_message_to_admin("❌ API غير متاح للتداول الحقيقي")
                logger.error("محاولة تنفيذ صفقة حقيقية بدون API")
                return
            
            user_market_type = self.user_settings['market_type']
            side = "Buy" if action == "buy" else "Sell"
            
            logger.info(f"🔴 بدء تنفيذ صفقة حقيقية: {symbol} {side} في {user_market_type.upper()}")
            
            # 🎯 حساب TP/SL التلقائي إذا كان مفعلاً
            tp_prices = []
            sl_price = None
            
            if trade_tools_manager.auto_apply_enabled:
                logger.info("🤖 الإعدادات التلقائية مفعلة - حساب TP/SL...")
                
                # حساب Take Profit
                if trade_tools_manager.default_tp_percentages:
                    for tp_percent, _ in trade_tools_manager.default_tp_percentages:
                        if action == "buy":
                            tp_price = price * (1 + tp_percent / 100)
                        else:  # sell
                            tp_price = price * (1 - tp_percent / 100)
                        tp_prices.append(tp_price)
                        logger.info(f"   🎯 TP: {tp_percent}% = {tp_price:.6f}")
                
                # حساب Stop Loss
                if trade_tools_manager.default_sl_percentage:
                    sl_percent = trade_tools_manager.default_sl_percentage
                    if action == "buy":
                        sl_price = price * (1 - sl_percent / 100)
                    else:  # sell
                        sl_price = price * (1 + sl_percent / 100)
                    logger.info(f"   🛑 SL: {sl_percent}% = {sl_price:.6f}")
            
            if user_market_type == 'futures':
                # ⚡ صفقة فيوتشر حقيقية
                margin_amount = self.user_settings['trade_amount']
                leverage = self.user_settings['leverage']
                
                # حساب حجم الصفقة بناءً على الرافعة
                position_size = margin_amount * leverage
                qty = str(position_size / price)  # عدد العقود
                
                logger.info(f"⚡ فيوتشر: الهامش={margin_amount}, الرافعة={leverage}x, حجم الصفقة={position_size:.2f}")
                
                # فتح الصفقة مع أول TP/SL (إذا وجد)
                first_tp = str(tp_prices[0]) if tp_prices else None
                first_sl = str(sl_price) if sl_price else None
                
                response = self.bybit_api.place_order(
                    symbol=symbol,
                    side=side,
                    order_type="Market",
                    qty=qty,
                    category=category,
                    take_profit=first_tp,
                    stop_loss=first_sl
                )
                
                if response.get("retCode") == 0:
                    order_id = response.get("result", {}).get("orderId", "")
                    
                    # إذا كان هناك أكثر من TP، إضافة الباقي
                    if len(tp_prices) > 1:
                        logger.info(f"📝 إضافة {len(tp_prices)-1} أهداف ربح إضافية...")
                        # ملاحظة: Bybit يدعم TP/SL واحد فقط للفيوتشر
                        # يمكن استخدام أوامر محددة إضافية إذا لزم الأمر
                    
                    message = f"✅ تم تنفيذ صفقة فيوتشر حقيقية\n\n"
                    if self.user_id:
                        message += f"👤 المستخدم: {self.user_id}\n"
                    message += f"📊 الرمز: {symbol}\n"
                    message += f"🔄 النوع: {side}\n"
                    message += f"💰 الهامش: {margin_amount}\n"
                    message += f"⚡ الرافعة: {leverage}x\n"
                    message += f"📈 حجم الصفقة: {position_size:.2f}\n"
                    message += f"💲 السعر التقريبي: {price:.6f}\n"
                    message += f"🏪 السوق: FUTURES\n"
                    message += f"🆔 رقم الأمر: {order_id}\n"
                    
                    if first_tp:
                        message += f"\n🎯 Take Profit: {float(first_tp):.6f}"
                    if first_sl:
                        message += f"\n🛑 Stop Loss: {float(first_sl):.6f}"
                    
                    message += f"\n\n⚠️ تحذير: هذه صفقة حقيقية على منصة Bybit!"
                    
                    await self.send_message_to_admin(message)
                    logger.info(f"✅ تم تنفيذ صفقة فيوتشر حقيقية: {order_id}")
                else:
                    error_msg = response.get("retMsg", "خطأ غير محدد")
                    await self.send_message_to_admin(f"❌ فشل في تنفيذ صفقة الفيوتشر: {error_msg}")
                    logger.error(f"فشل تنفيذ صفقة فيوتشر: {error_msg}")
                    
            else:  # spot
                # 🏪 صفقة سبوت حقيقية
                amount = self.user_settings['trade_amount']
                qty = str(amount / price)  # كمية العملة
                
                logger.info(f"🏪 سبوت: المبلغ={amount}, الكمية={qty}")
                
                # Spot لا يدعم TP/SL مباشرة، يجب استخدام أوامر محددة
                response = self.bybit_api.place_order(
                    symbol=symbol,
                    side=side,
                    order_type="Market",
                    qty=qty,
                    category=category
                )
                
                if response.get("retCode") == 0:
                    order_id = response.get("result", {}).get("orderId", "")
                    
                    # إضافة أوامر TP/SL المحددة للسبوت إذا كانت موجودة
                    if tp_prices or sl_price:
                        logger.info("📝 إضافة أوامر TP/SL للسبوت...")
                        # يمكن إضافة أوامر Limit للسبوت هنا
                    
                    message = f"✅ تم تنفيذ صفقة سبوت حقيقية\n\n"
                    if self.user_id:
                        message += f"👤 المستخدم: {self.user_id}\n"
                    message += f"📊 الرمز: {symbol}\n"
                    message += f"🔄 النوع: {side}\n"
                    message += f"💰 المبلغ: {amount}\n"
                    message += f"📦 الكمية: {qty}\n"
                    message += f"💲 السعر التقريبي: {price:.6f}\n"
                    message += f"🏪 السوق: SPOT\n"
                    message += f"🆔 رقم الأمر: {order_id}\n"
                    
                    if tp_prices:
                        message += f"\n🎯 أهداف الربح محسوبة (يتطلب إضافة أوامر يدوية)"
                    if sl_price:
                        message += f"\n🛑 Stop Loss محسوب: {sl_price:.6f}"
                    
                    message += f"\n\n⚠️ تحذير: هذه صفقة حقيقية على منصة Bybit!"
                    
                    await self.send_message_to_admin(message)
                    logger.info(f"✅ تم تنفيذ صفقة سبوت حقيقية: {order_id}")
                else:
                    error_msg = response.get("retMsg", "خطأ غير محدد")
                    await self.send_message_to_admin(f"❌ فشل في تنفيذ صفقة السبوت: {error_msg}")
                    logger.error(f"فشل تنفيذ صفقة سبوت: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة الحقيقية: {e}")
            import traceback
            logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
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
                # استخدام صفقات المستخدم - التأكد من وجود القاموس
                if self.user_id not in user_manager.user_positions:
                    user_manager.user_positions[self.user_id] = {}
                    logger.info(f"تم إنشاء قاموس صفقات جديد للمستخدم {self.user_id}")
                user_positions = user_manager.user_positions[self.user_id]
                logger.info(f"استخدام حساب المستخدم {self.user_id} لنوع السوق {user_market_type}")
            else:
                # استخدام الحساب العام (للإشارات القديمة)
                if user_market_type == 'futures':
                    account = self.demo_account_futures
                else:
                    account = self.demo_account_spot
                user_positions = self.open_positions
                logger.info(f"استخدام الحساب العام لنوع السوق {user_market_type}")
            
            # معالجة إشارات الإغلاق (close, close_long, close_short)
            if action == 'close':
                logger.info(f"🔄 معالجة إشارة إغلاق للرمز {symbol}")
                
                # البحث عن الصفقات المفتوحة لهذا الرمز
                positions_to_close = []
                for pos_id, pos_info in user_positions.items():
                    if pos_info.get('symbol') == symbol:
                        # إغلاق جميع الصفقات على هذا الرمز
                        positions_to_close.append(pos_id)
                
                if not positions_to_close:
                    logger.warning(f"⚠️ لا توجد صفقات مفتوحة للرمز {symbol}")
                    await self.send_message_to_admin(
                        f"⚠️ لا توجد صفقات مفتوحة للإغلاق\n\n"
                        f"📊 الرمز: {symbol}\n"
                        f"🏪 السوق: {user_market_type.upper()}"
                    )
                    return
                
                # إغلاق الصفقات
                for pos_id in positions_to_close:
                    pos_info = user_positions[pos_id]
                    
                    if user_market_type == 'futures':
                        # إغلاق صفقة فيوتشر
                        position = account.positions.get(pos_id)
                        if position:
                            pnl = position.calculate_closing_pnl(price)
                            success, result = account.close_futures_position(pos_id, price)
                            
                            if success:
                                logger.info(f"✅ تم إغلاق صفقة الفيوتشر: {pos_id}")
                                
                                # إزالة من قائمة الصفقات
                                del user_positions[pos_id]
                                
                                # إرسال إشعار
                                message = f"✅ تم إغلاق صفقة فيوتشر\n\n"
                                if self.user_id:
                                    message += f"👤 المستخدم: {self.user_id}\n"
                                message += f"📊 الرمز: {symbol}\n"
                                message += f"🔄 النوع: {pos_info.get('side', '').upper()}\n"
                                message += f"💰 الربح/الخسارة: {pnl:.2f}\n"
                                message += f"💲 سعر الدخول: {pos_info.get('entry_price', 0):.6f}\n"
                                message += f"💲 سعر الإغلاق: {price:.6f}\n"
                                message += f"🆔 رقم الصفقة: {pos_id}\n"
                                
                                # معلومات الحساب
                                account_info = account.get_account_info()
                                message += f"\n💰 الرصيد الكلي: {account_info['balance']:.2f}"
                                message += f"\n💳 الرصيد المتاح: {account_info['available_balance']:.2f}"
                                
                                await self.send_message_to_admin(message)
                            else:
                                logger.error(f"❌ فشل إغلاق صفقة الفيوتشر: {result}")
                                await self.send_message_to_admin(f"❌ فشل إغلاق الصفقة: {result}")
                    else:
                        # إغلاق صفقة سبوت
                        success, result = account.close_spot_position(pos_id, price)
                        
                        if success:
                            pnl = result  # PnL
                            logger.info(f"✅ تم إغلاق صفقة السبوت: {pos_id}")
                            
                            # إزالة من قائمة الصفقات
                            del user_positions[pos_id]
                            
                            # إرسال إشعار
                            message = f"✅ تم إغلاق صفقة سبوت\n\n"
                            if self.user_id:
                                message += f"👤 المستخدم: {self.user_id}\n"
                            message += f"📊 الرمز: {symbol}\n"
                            message += f"🔄 النوع: {pos_info.get('side', '').upper()}\n"
                            message += f"💰 الربح/الخسارة: {pnl:.2f}\n"
                            message += f"💲 سعر الدخول: {pos_info.get('entry_price', 0):.6f}\n"
                            message += f"💲 سعر الإغلاق: {price:.6f}\n"
                            message += f"🆔 رقم الصفقة: {pos_id}\n"
                            
                            # معلومات الحساب
                            account_info = account.get_account_info()
                            message += f"\n💰 الرصيد: {account_info['balance']:.2f}"
                            
                            await self.send_message_to_admin(message)
                        else:
                            logger.error(f"❌ فشل إغلاق صفقة السبوت: {result}")
                            await self.send_message_to_admin(f"❌ فشل إغلاق الصفقة: {result}")
                
                return  # انتهى معالجة إشارة الإغلاق
            
            # معالجة إشارات الإغلاق الجزئي (partial_close)
            if action == 'partial_close':
                logger.info(f"📊 معالجة إشارة إغلاق جزئي للرمز {symbol}")
                
                # الحصول على النسبة المئوية
                percentage = float(self._current_signal_data.get('percentage', 50))
                
                # التحقق من صحة النسبة
                if percentage <= 0 or percentage > 100:
                    logger.error(f"❌ نسبة غير صحيحة: {percentage}%")
                    await self.send_message_to_admin(
                        f"❌ نسبة إغلاق جزئي غير صحيحة\n\n"
                        f"📊 النسبة: {percentage}%\n"
                        f"✅ النطاق المسموح: 1 - 100%"
                    )
                    return
                
                # البحث عن الصفقات المفتوحة لهذا الرمز
                positions_to_partial_close = []
                for pos_id, pos_info in user_positions.items():
                    if pos_info.get('symbol') == symbol:
                        # إغلاق جزئي لجميع الصفقات على هذا الرمز
                        positions_to_partial_close.append(pos_id)
                
                if not positions_to_partial_close:
                    logger.warning(f"⚠️ لا توجد صفقات مفتوحة للرمز {symbol}")
                    await self.send_message_to_admin(
                        f"⚠️ لا توجد صفقات للإغلاق الجزئي\n\n"
                        f"📊 الرمز: {symbol}\n"
                        f"🏪 السوق: {user_market_type.UPPER()}"
                    )
                    return
                
                # إغلاق جزئي للصفقات
                for pos_id in positions_to_partial_close:
                    pos_info = user_positions[pos_id]
                    
                    if user_market_type == 'futures':
                        # إغلاق جزئي لصفقة فيوتشر
                        position = account.positions.get(pos_id)
                        if position:
                            # حساب الكمية المراد إغلاقها
                            close_amount = position.position_size * (percentage / 100)
                            close_contracts = position.contracts * (percentage / 100)
                            
                            # حساب الربح/الخسارة للجزء المغلق
                            partial_pnl = position.calculate_closing_pnl(price) * (percentage / 100)
                            
                            # تحديث الصفقة
                            new_position_size = position.position_size * ((100 - percentage) / 100)
                            new_margin = position.margin_amount * ((100 - percentage) / 100)
                            new_contracts = position.contracts * ((100 - percentage) / 100)
                            
                            # تحديث معلومات الصفقة في الحساب
                            position.position_size = new_position_size
                            position.margin_amount = new_margin
                            position.contracts = new_contracts
                            
                            # تحرير الهامش المغلق وإضافة الربح/الخسارة
                            released_margin = position.margin_amount * (percentage / 100)
                            account.margin_locked -= (released_margin - partial_pnl)
                            account.balance += partial_pnl
                            
                            # تحديث معلومات الصفقة في user_positions
                            user_positions[pos_id]['position_size'] = new_position_size
                            user_positions[pos_id]['margin_amount'] = new_margin
                            user_positions[pos_id]['contracts'] = new_contracts
                            
                            # إرسال إشعار
                            message = f"📊 تم إغلاق جزئي لصفقة فيوتشر\n\n"
                            if self.user_id:
                                message += f"👤 المستخدم: {self.user_id}\n"
                            message += f"📊 الرمز: {symbol}\n"
                            message += f"🔄 النوع: {pos_info.get('side', '').UPPER()}\n"
                            message += f"📈 النسبة المغلقة: {percentage}%\n"
                            message += f"💰 الربح/الخسارة الجزئي: {partial_pnl:.2f}\n"
                            message += f"💲 سعر الدخول: {pos_info.get('entry_price', 0):.6f}\n"
                            message += f"💲 سعر الإغلاق: {price:.6f}\n"
                            message += f"\n📊 **الصفقة المتبقية:**\n"
                            message += f"📈 الحجم المتبقي: {new_position_size:.2f} USDT ({100-percentage}%)\n"
                            message += f"🔒 الهامش المتبقي: {new_margin:.2f} USDT\n"
                            message += f"📊 العقود المتبقية: {new_contracts:.6f}\n"
                            message += f"🆔 رقم الصفقة: {pos_id}\n"
                            
                            # معلومات الحساب
                            account_info = account.get_account_info()
                            message += f"\n💰 الرصيد الكلي: {account_info['balance']:.2f}"
                            message += f"\n💳 الرصيد المتاح: {account_info['available_balance']:.2f}"
                            
                            await self.send_message_to_admin(message)
                            logger.info(f"✅ تم الإغلاق الجزئي ({percentage}%) لصفقة {pos_id}")
                    else:
                        # الإغلاق الجزئي غير مدعوم حالياً في Spot
                        logger.warning(f"⚠️ الإغلاق الجزئي غير مدعوم في Spot حالياً")
                        await self.send_message_to_admin(
                            f"⚠️ الإغلاق الجزئي مدعوم فقط في Futures\n\n"
                            f"🏪 نوع السوق الحالي: {user_market_type.UPPER()}\n"
                            f"💡 للإغلاق الجزئي، استخدم نوع سوق FUTURES"
                        )
                
                return  # انتهى معالجة الإغلاق الجزئي
            
            # معالجة إشارات الفتح (buy, sell, long, short)
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
                        
                        # تطبيق الإعدادات التلقائية إن كانت مفعلة
                        if trade_tools_manager.auto_apply_enabled:
                            auto_applied = trade_tools_manager.apply_auto_settings_to_position(
                                position_id, symbol, action, price, position.position_size,
                                user_market_type, leverage
                            )
                            if auto_applied:
                                message += "\n\n🤖 تم تطبيق الإعدادات التلقائية!"
                        
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
                    
                    # تطبيق الإعدادات التلقائية إن كانت مفعلة
                    if trade_tools_manager.auto_apply_enabled:
                        auto_applied = trade_tools_manager.apply_auto_settings_to_position(
                            position_id, symbol, action, price, amount,
                            user_market_type, 1
                        )
                        if auto_applied:
                            message += "\n\n🤖 تم تطبيق الإعدادات التلقائية!"
                    
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

# إنشاء مدير أدوات التداول
trade_tools_manager = TradeToolsManager()

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
            logger.warning("API key أو secret فارغ")
            return False
        
        # إنشاء API مؤقت للتحقق
        temp_api = BybitAPI(api_key, api_secret)
        
        # محاولة الحصول على معلومات الحساب (دالة عادية وليست async)
        account_info = temp_api.get_account_balance()
        
        logger.info(f"نتيجة التحقق من API: {account_info}")
        
        # إذا تم الحصول على معلومات الحساب بنجاح
        if account_info and 'retCode' in account_info:
            if account_info['retCode'] == 0:
                logger.info("✅ API keys صحيحة")
                return True
            else:
                logger.warning(f"❌ API keys غير صحيحة: {account_info.get('retMsg', 'Unknown error')}")
                return False
        
        logger.warning("❌ فشل في التحقق من API - استجابة غير صالحة")
        return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في التحقق من API: {e}")
        import traceback
        traceback.print_exc()
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
        [KeyboardButton("🔄 تحديث"), KeyboardButton("👤 الوضع العادي")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message)

def parse_smart_signal_input(text: str) -> Optional[Dict]:
    """
    دالة ذكية لفهم مدخلات المطور للإشارات
    تدعم صيغ متعددة:
    - "BTCUSDT buy 100"
    - "ETH/USDT sell spot 50"  
    - "BTC short futures 100 10x"
    - "ETHUSDT long 200 spot"
    """
    import re
    
    # إزالة المسافات الزائدة وتحويل لأحرف صغيرة للمعالجة
    text = text.strip()
    text_lower = text.lower()
    
    # استخراج المعلومات
    result = {
        'symbol': None,
        'action': None,
        'amount': 100.0,  # قيمة افتراضية
        'market_type': 'spot',  # قيمة افتراضية
        'leverage': 10  # قيمة افتراضية للفيوتشر
    }
    
    # البحث عن رمز العملة (BTCUSDT, BTC/USDT, BTC-USDT, etc.)
    symbol_patterns = [
        r'([A-Z]{2,10}USDT)',  # BTCUSDT
        r'([A-Z]{2,10})/USDT',  # BTC/USDT
        r'([A-Z]{2,10})-USDT',  # BTC-USDT
        r'([A-Z]{2,10})\s+USDT',  # BTC USDT
    ]
    
    for pattern in symbol_patterns:
        match = re.search(pattern, text.upper())
        if match:
            symbol = match.group(1)
            # تنظيف الرمز وإضافة USDT إن لم يكن موجوداً
            if not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            result['symbol'] = symbol
            break
    
    # البحث عن الاتجاه (buy/sell/long/short)
    if any(word in text_lower for word in ['buy', 'long', 'شراء']):
        result['action'] = 'buy'
    elif any(word in text_lower for word in ['sell', 'short', 'بيع']):
        result['action'] = 'sell'
    
    # البحث عن نوع السوق (spot/futures)
    if any(word in text_lower for word in ['futures', 'future', 'فيوتشر']):
        result['market_type'] = 'futures'
    elif any(word in text_lower for word in ['spot', 'سبوت']):
        result['market_type'] = 'spot'
    
    # البحث عن المبلغ (رقم)
    amount_match = re.search(r'\b(\d+(?:\.\d+)?)\b', text)
    if amount_match:
        try:
            result['amount'] = float(amount_match.group(1))
        except:
            pass
    
    # البحث عن الرافعة المالية (10x, 20x, etc.)
    leverage_match = re.search(r'(\d+)x', text_lower)
    if leverage_match:
        try:
            result['leverage'] = int(leverage_match.group(1))
        except:
            pass
    
    # التحقق من اكتمال البيانات الأساسية
    if result['symbol'] and result['action']:
        return result
    
    return None

async def handle_send_signal_developer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إرسال إشارة من المطور - نظام إدخال مرحلي"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    
    if not developer_manager.can_broadcast_signals(user_id):
        if update.message:
            await update.message.reply_text("❌ ليس لديك صلاحية لإرسال إشارات")
        return
    
    # بدء عملية إرسال إشارة جديدة - الخطوة الأولى
    if user_id:
        # تهيئة بيانات الإشارة
        if 'dev_signal_data' not in context.user_data:
            context.user_data['dev_signal_data'] = {}
        context.user_data['dev_signal_data'] = {}  # إعادة تعيين
        
        # بدء من الخطوة 1: إدخال الرمز
        user_input_state[user_id] = "dev_guided_step1_symbol"
    
    # عرض الخطوة الأولى مباشرة
    message = """
📡 إرسال إشارة للمتابعين

📝 الخطوة 1 من 5

🔤 أدخل رمز العملة:

💡 أمثلة:
• BTCUSDT
• BTC
• ETH/USDT
• SOLUSDT

أرسل الرمز الآن 👇
    """
    
    keyboard = [
        [InlineKeyboardButton("❌ إلغاء", callback_data="developer_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup)

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
    else:
        # مستخدم موجود - إعادة تحميل الحساب الحقيقي إذا كان مفعّلاً
        account_type = user_data.get('account_type', 'demo')
        exchange = user_data.get('exchange', '')
        
        if account_type == 'real' and exchange:
            from real_account_manager import real_account_manager
            
            # التحقق من وجود المفاتيح
            if exchange == 'bybit':
                api_key = user_data.get('bybit_api_key', '')
                api_secret = user_data.get('bybit_api_secret', '')
            elif exchange == 'mexc':
                api_key = user_data.get('mexc_api_key', '')
                api_secret = user_data.get('mexc_api_secret', '')
            else:
                api_key = ''
                api_secret = ''
            
            # إعادة تهيئة الحساب إذا كانت المفاتيح موجودة
            if api_key and api_secret and len(api_key) > 10:
                try:
                    real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
                    logger.info(f"✅ تم إعادة تحميل حساب {exchange} للمستخدم {user_id}")
                except Exception as e:
                    logger.error(f"⚠️ خطأ في إعادة تحميل الحساب: {e}")
        
        # رسالة ترحيب للمستخدم الجديد
        welcome_message = f"""
🤖 مرحباً بك {update.effective_user.first_name}!

أهلاً وسهلاً بك في بوت المطور نجدت 🎉

🚀 **ما يفعله البوت:**
• تنفيذ إشارات التداول تلقائياً من TradingView
• دعم منصات متعددة (Bybit & MEXC)
• تداول ذكي مع إدارة مخاطر متقدمة
• إحصائيات مفصلة ومتابعة الصفقات

💡 **كيف يعمل:**
1. تربط حسابك على المنصة المفضلة
2. تحصل على رابط webhook شخصي
3. تستخدم الرابط في TradingView لإرسال الإشارات
4. البوت ينفذ التداولات تلقائياً!

🔗 **للبدء:**
اضغط على "⚙️ الإعدادات" لربط حسابك

📞 **إذا احتجت مساعدة من المطور:**
رابط التلجرام: [@nagdatbasheer](https://t.me/nagdatbasheer)

استخدم الأزرار أدناه للتنقل
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
    
    # التحقق الفعلي من حالة API
    if api_key and api_secret:
        is_valid = await check_api_connection(api_key, api_secret)
        api_status = get_api_status_indicator(api_key, api_secret, is_valid)
    else:
        api_status = get_api_status_indicator(api_key, api_secret, None)
    
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
🤖 مرحباً بك {update.effective_user.first_name}!

أهلاً وسهلاً بك في بوت المطور نجدت 🎉

📞 **إذا احتجت مساعدة من المطور:**
رابط التلجرام: [@nagdatbasheer](https://t.me/nagdatbasheer)

🚀 **عن البوت:**
هذا بوت تداول ذكي متطور مصمم لتنفيذ إشاراتك التداولية تلقائياً. يعمل مع منصات التداول الكبرى مثل Bybit و MEXC، ويوفر لك تجربة تداول سلسة وآمنة.

✨ **المميزات الرئيسية:**
• تنفيذ فوري للإشارات من TradingView
• دعم التداول الفوري والآجل
• إدارة مخاطر ذكية مع Stop Loss و Take Profit
• إحصائيات مفصلة ومتابعة مستمرة للصفقات
• واجهة سهلة الاستخدام باللغة العربية

💡 **كيفية الاستخدام:**
1. اربط حسابك المفضل من الإعدادات
2. احصل على رابط webhook شخصي
3. استخدم الرابط في TradingView لإرسال الإشارات
4. استمتع بالتداول التلقائي الذكي!

⚡ **زر متابعة Nagdat:**
يمكنك متابعة المطور Nagdat للحصول على إشارات تداول احترافية مباشرة! 
عند المتابعة، ستستقبل جميع إشاراته التداولية تلقائياً على حسابك.

استخدم الأزرار أدناه للتنقل في البوت
    """
    
    if update.message is not None:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def risk_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة إدارة المخاطر"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        if update.message is not None:
            await update.message.reply_text("❌ يرجى استخدام /start أولاً")
        return
    
    # الحصول على إعدادات إدارة المخاطر
    risk_settings = user_data.get('risk_management', {
        'enabled': True,
        'max_loss_percent': 10.0,  # الحد الأقصى للخسارة كنسبة مئوية
        'max_loss_amount': 1000.0,  # الحد الأقصى للخسارة بالمبلغ
        'stop_trading_on_loss': True,  # إيقاف التداول عند الوصول للحد
        'daily_loss_limit': 500.0,  # حد الخسارة اليومية
        'weekly_loss_limit': 2000.0  # حد الخسارة الأسبوعية
    })
    
    enabled_status = "✅" if risk_settings.get('enabled', True) else "❌"
    stop_status = "✅" if risk_settings.get('stop_trading_on_loss', True) else "❌"
    
    # بناء رسالة إدارة المخاطر
    risk_message = f"""
🛡️ **إدارة المخاطر**

📊 **الحالة الحالية:**
🛡️ إدارة المخاطر: {enabled_status}
⏹️ إيقاف التداول عند الخسارة: {stop_status}

💰 **حدود الخسارة:**
📉 الحد الأقصى للخسارة: {risk_settings.get('max_loss_percent', 10.0):.1f}%
💸 الحد الأقصى بالمبلغ: {risk_settings.get('max_loss_amount', 1000.0):.0f} USDT
📅 الحد اليومي: {risk_settings.get('daily_loss_limit', 500.0):.0f} USDT
📆 الحد الأسبوعي: {risk_settings.get('weekly_loss_limit', 2000.0):.0f} USDT

📊 **الإحصائيات الحالية:**
💸 الخسارة اليومية: {user_data.get('daily_loss', 0):.2f} USDT
📈 الخسارة الأسبوعية: {user_data.get('weekly_loss', 0):.2f} USDT
📉 إجمالي الخسارة: {user_data.get('total_loss', 0):.2f} USDT

🔍 **الفرق بين الخيارات:**

🛡️ **إدارة المخاطر:**
• عند التفعيل: مراقبة مستمرة للخسائر وفحص الحدود
• عند التعطيل: لا يوجد مراقبة أو فحص للحدود

⏹️ **إيقاف التداول عند الخسارة:**
• عند التفعيل: إيقاف البوت تلقائياً عند الوصول للحدود
• عند التعطيل: البوت يستمر حتى لو وصل للحدود

💡 **التوصيات:**
• 🟢 الأفضل: تفعيل الاثنين معاً للحماية الكاملة
• 🟡 مقبول: تفعيل إدارة المخاطر فقط (مراقبة بدون حماية)
• 🔴 خطير: تعطيل الاثنين (لا يوجد حماية)
    """
    
    # بناء الأزرار
    keyboard = [
        [InlineKeyboardButton(f"🛡️ تفعيل/إلغاء إدارة المخاطر", callback_data="toggle_risk_management")],
        [InlineKeyboardButton("📉 تعديل حد الخسارة المئوي", callback_data="set_max_loss_percent")],
        [InlineKeyboardButton("💸 تعديل حد الخسارة بالمبلغ", callback_data="set_max_loss_amount")],
        [InlineKeyboardButton("📅 تعديل الحد اليومي", callback_data="set_daily_loss_limit")],
        [InlineKeyboardButton("📆 تعديل الحد الأسبوعي", callback_data="set_weekly_loss_limit")],
        [InlineKeyboardButton(f"⏹️ إيقاف التداول عند الخسارة", callback_data="toggle_stop_trading")],
        [InlineKeyboardButton("📊 عرض إحصائيات المخاطر", callback_data="show_risk_stats")],
        [InlineKeyboardButton("🔄 إعادة تعيين الإحصائيات", callback_data="reset_risk_stats")],
        [InlineKeyboardButton("📖 شرح مفصل للخيارات", callback_data="risk_management_guide")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(risk_message, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                # الرسالة نفسها، لا نحتاج لتحديثها
                pass
            else:
                raise edit_error
    elif update.message:
        await update.message.reply_text(risk_message, reply_markup=reply_markup, parse_mode='Markdown')

async def auto_apply_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة إعدادات التطبيق التلقائي"""
    try:
        query = update.callback_query if update.callback_query else None
        
        if query:
            await query.answer()
        
        summary = trade_tools_manager.get_auto_settings_summary()
        
        message = f"""
⚙️ **إعدادات التطبيق التلقائي**

{summary}

💡 **ما هو التطبيق التلقائي؟**
عند التفعيل، كل صفقة جديدة تُفتح ستحصل تلقائياً على:
• أهداف الربح المحددة
• Stop Loss المحدد
• Trailing Stop (إن كان مفعلاً)

🎯 هذا يوفر عليك الوقت ويضمن حماية كل صفقاتك!
        """
        
        status_button = "⏸️ تعطيل" if trade_tools_manager.auto_apply_enabled else "✅ تفعيل"
        
        keyboard = [
            [InlineKeyboardButton(
                f"{status_button} التطبيق التلقائي", 
                callback_data="toggle_auto_apply"
            )],
            [InlineKeyboardButton("⚙️ تعديل الإعدادات", callback_data="edit_auto_settings")],
            [InlineKeyboardButton("🎲 إعداد سريع", callback_data="quick_auto_setup")],
            [InlineKeyboardButton("🗑️ حذف الإعدادات", callback_data="clear_auto_settings")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.message:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"خطأ في قائمة التطبيق التلقائي: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def toggle_auto_apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تبديل حالة التطبيق التلقائي"""
    try:
        query = update.callback_query
        await query.answer()
        
        if trade_tools_manager.auto_apply_enabled:
            trade_tools_manager.disable_auto_apply()
            message = "⏸️ تم تعطيل التطبيق التلقائي"
        else:
            # التحقق من وجود إعدادات محفوظة
            if not trade_tools_manager.default_tp_percentages and trade_tools_manager.default_sl_percentage == 0:
                await query.edit_message_text(
                    "⚠️ لا توجد إعدادات محفوظة!\n\n"
                    "يرجى تعديل الإعدادات أولاً قبل التفعيل.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⚙️ تعديل الإعدادات", callback_data="edit_auto_settings"),
                        InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")
                    ]])
                )
                return
            
            trade_tools_manager.enable_auto_apply()
            message = "✅ تم تفعيل التطبيق التلقائي!\n\nالآن كل صفقة جديدة ستحصل على الإعدادات المحفوظة"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"خطأ في تبديل التطبيق التلقائي: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

# ===== دوال إدارة المخاطر =====

async def toggle_risk_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تبديل حالة إدارة المخاطر"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        # الحصول على إعدادات إدارة المخاطر الحالية
        risk_settings = user_data.get('risk_management', {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        })
        
        # تبديل الحالة
        risk_settings['enabled'] = not risk_settings.get('enabled', True)
        
        # حفظ الإعدادات
        user_manager.update_user(user_id, {'risk_management': risk_settings})
        
        status = "✅ مفعل" if risk_settings.get('enabled', True) else "❌ معطل"
        message = f"🛡️ إدارة المخاطر: {status}"
        
        try:
            await query.edit_message_text(message)
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                # الرسالة نفسها، لا نحتاج لتحديثها
                pass
            else:
                raise edit_error
        
        await asyncio.sleep(1)
        await risk_management_menu(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في تبديل إدارة المخاطر: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_max_loss_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل حد الخسارة المئوي"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_input_state[user_id] = 'waiting_max_loss_percent'
        
        message = """
📉 **تعديل حد الخسارة المئوي**

أدخل النسبة المئوية للحد الأقصى للخسارة (1-50%):

مثال: 10 (يعني 10%)

⚠️ **تحذير:** عند الوصول لهذا الحد، سيتم إيقاف التداول تلقائياً (إذا كان إيقاف التداول مفعل)
        """
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في تعديل حد الخسارة المئوي: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_max_loss_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل حد الخسارة بالمبلغ"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_input_state[user_id] = 'waiting_max_loss_amount'
        
        message = """
💸 **تعديل حد الخسارة بالمبلغ**

أدخل المبلغ بالـ USDT للحد الأقصى للخسارة:

مثال: 1000 (يعني 1000 USDT)

⚠️ **تحذير:** عند الوصول لهذا الحد، سيتم إيقاف التداول تلقائياً (إذا كان إيقاف التداول مفعل)
        """
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في تعديل حد الخسارة بالمبلغ: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_daily_loss_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل حد الخسارة اليومية"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_input_state[user_id] = 'waiting_daily_loss_limit'
        
        message = """
📅 **تعديل حد الخسارة اليومية**

أدخل المبلغ بالـ USDT للحد الأقصى للخسارة اليومية:

مثال: 500 (يعني 500 USDT في اليوم)

⚠️ **تحذير:** عند الوصول لهذا الحد، سيتم إيقاف التداول تلقائياً (إذا كان إيقاف التداول مفعل)
        """
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في تعديل حد الخسارة اليومية: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_weekly_loss_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل حد الخسارة الأسبوعية"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_input_state[user_id] = 'waiting_weekly_loss_limit'
        
        message = """
📆 **تعديل حد الخسارة الأسبوعية**

أدخل المبلغ بالـ USDT للحد الأقصى للخسارة الأسبوعية:

مثال: 2000 (يعني 2000 USDT في الأسبوع)

⚠️ **تحذير:** عند الوصول لهذا الحد، سيتم إيقاف التداول تلقائياً (إذا كان إيقاف التداول مفعل)
        """
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في تعديل حد الخسارة الأسبوعية: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def toggle_stop_trading_on_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تبديل إيقاف التداول عند الخسارة"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        # الحصول على إعدادات إدارة المخاطر الحالية
        risk_settings = user_data.get('risk_management', {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        })
        
        # تبديل الحالة
        risk_settings['stop_trading_on_loss'] = not risk_settings.get('stop_trading_on_loss', True)
        
        # حفظ الإعدادات
        user_manager.update_user(user_id, {'risk_management': risk_settings})
        
        status = "✅ مفعل" if risk_settings.get('stop_trading_on_loss', True) else "❌ معطل"
        message = f"⏹️ إيقاف التداول عند الخسارة: {status}"
        
        try:
            await query.edit_message_text(message)
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                # الرسالة نفسها، لا نحتاج لتحديثها
                pass
            else:
                raise edit_error
        
        await asyncio.sleep(1)
        await risk_management_menu(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في تبديل إيقاف التداول: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def show_risk_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات المخاطر"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        # الحصول على إحصائيات المخاطر
        daily_loss = user_data.get('daily_loss', 0)
        weekly_loss = user_data.get('weekly_loss', 0)
        total_loss = user_data.get('total_loss', 0)
        
        # الحصول على إعدادات المخاطر
        risk_settings = user_data.get('risk_management', {})
        max_loss_percent = risk_settings.get('max_loss_percent', 10.0)
        max_loss_amount = risk_settings.get('max_loss_amount', 1000.0)
        daily_limit = risk_settings.get('daily_loss_limit', 500.0)
        weekly_limit = risk_settings.get('weekly_loss_limit', 2000.0)
        
        # حساب النسب المئوية
        daily_percent = (daily_loss / daily_limit * 100) if daily_limit > 0 else 0
        weekly_percent = (weekly_loss / weekly_limit * 100) if weekly_limit > 0 else 0
        
        # تحديد حالة الخطر
        daily_status = "🔴" if daily_percent >= 80 else "🟡" if daily_percent >= 50 else "🟢"
        weekly_status = "🔴" if weekly_percent >= 80 else "🟡" if weekly_percent >= 50 else "🟢"
        
        stats_message = f"""
📊 **إحصائيات المخاطر**

📅 **الخسارة اليومية:**
{daily_status} المبلغ: {daily_loss:.2f} USDT
📊 النسبة: {daily_percent:.1f}% من الحد ({daily_limit:.0f} USDT)

📆 **الخسارة الأسبوعية:**
{weekly_status} المبلغ: {weekly_loss:.2f} USDT
📊 النسبة: {weekly_percent:.1f}% من الحد ({weekly_limit:.0f} USDT)

📉 **إجمالي الخسارة:**
💸 المبلغ: {total_loss:.2f} USDT
📊 الحد المئوي: {max_loss_percent:.1f}%
💸 الحد بالمبلغ: {max_loss_amount:.0f} USDT

🎯 **التوصيات:**
{_get_risk_recommendations(daily_percent, weekly_percent, total_loss, max_loss_amount)}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data="show_risk_stats")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="risk_management_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(stats_message, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                # الرسالة نفسها، لا نحتاج لتحديثها
                pass
            else:
                raise edit_error
        
    except Exception as e:
        logger.error(f"خطأ في عرض إحصائيات المخاطر: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def reset_risk_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعادة تعيين إحصائيات المخاطر"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # إعادة تعيين الإحصائيات
        user_manager.update_user(user_id, {
            'daily_loss': 0,
            'weekly_loss': 0,
            'total_loss': 0,
            'last_reset_date': datetime.now().strftime('%Y-%m-%d')
        })
        
        message = "🔄 تم إعادة تعيين إحصائيات المخاطر بنجاح"
        
        try:
            await query.edit_message_text(message)
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                # الرسالة نفسها، لا نحتاج لتحديثها
                pass
            else:
                raise edit_error
        
        await asyncio.sleep(1)
        await risk_management_menu(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في إعادة تعيين إحصائيات المخاطر: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

def _get_risk_recommendations(daily_percent, weekly_percent, total_loss, max_loss_amount):
    """الحصول على توصيات المخاطر"""
    recommendations = []
    
    if daily_percent >= 80:
        recommendations.append("🚨 خطر عالي اليوم - توقف عن التداول")
    elif daily_percent >= 50:
        recommendations.append("⚠️ خطر متوسط اليوم - قلل من حجم التداول")
    
    if weekly_percent >= 80:
        recommendations.append("🚨 خطر عالي أسبوعياً - راجع استراتيجيتك")
    elif weekly_percent >= 50:
        recommendations.append("⚠️ خطر متوسط أسبوعياً - احذر من الخسائر")
    
    if total_loss >= max_loss_amount * 0.8:
        recommendations.append("🚨 قريب من الحد الأقصى - توقف فوراً")
    elif total_loss >= max_loss_amount * 0.5:
        recommendations.append("⚠️ وصلت لنصف الحد الأقصى - احذر")
    
    if not recommendations:
        recommendations.append("✅ الوضع آمن - استمر بحذر")
    
    return "\n".join(recommendations)

async def send_risk_management_menu(message, user_id: int):
    """إرسال قائمة إدارة المخاطر مباشرة"""
    try:
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            await message.reply_text("❌ يرجى استخدام /start أولاً")
            return
        
        # الحصول على إعدادات إدارة المخاطر
        risk_settings = user_data.get('risk_management', {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        })
        
        enabled_status = "✅" if risk_settings.get('enabled', True) else "❌"
        stop_status = "✅" if risk_settings.get('stop_trading_on_loss', True) else "❌"
        
        # بناء رسالة إدارة المخاطر
        risk_message = f"""
🛡️ **إدارة المخاطر**

📊 **الحالة الحالية:**
🛡️ إدارة المخاطر: {enabled_status}
⏹️ إيقاف التداول عند الخسارة: {stop_status}

💰 **حدود الخسارة:**
📉 الحد الأقصى للخسارة: {risk_settings.get('max_loss_percent', 10.0):.1f}%
💸 الحد الأقصى بالمبلغ: {risk_settings.get('max_loss_amount', 1000.0):.0f} USDT
📅 الحد اليومي: {risk_settings.get('daily_loss_limit', 500.0):.0f} USDT
📆 الحد الأسبوعي: {risk_settings.get('weekly_loss_limit', 2000.0):.0f} USDT

📊 **الإحصائيات الحالية:**
💸 الخسارة اليومية: {user_data.get('daily_loss', 0):.2f} USDT
📈 الخسارة الأسبوعية: {user_data.get('weekly_loss', 0):.2f} USDT
📉 إجمالي الخسارة: {user_data.get('total_loss', 0):.2f} USDT

🔍 **الفرق بين الخيارات:**

🛡️ **إدارة المخاطر:**
• عند التفعيل: مراقبة مستمرة للخسائر وفحص الحدود
• عند التعطيل: لا يوجد مراقبة أو فحص للحدود

⏹️ **إيقاف التداول عند الخسارة:**
• عند التفعيل: إيقاف البوت تلقائياً عند الوصول للحدود
• عند التعطيل: البوت يستمر حتى لو وصل للحدود

💡 **التوصيات:**
• 🟢 الأفضل: تفعيل الاثنين معاً للحماية الكاملة
• 🟡 مقبول: تفعيل إدارة المخاطر فقط (مراقبة بدون حماية)
• 🔴 خطير: تعطيل الاثنين (لا يوجد حماية)
        """
        
        # بناء الأزرار
        keyboard = [
            [InlineKeyboardButton(f"🛡️ تفعيل/إلغاء إدارة المخاطر", callback_data="toggle_risk_management")],
            [InlineKeyboardButton("📉 تعديل حد الخسارة المئوي", callback_data="set_max_loss_percent")],
            [InlineKeyboardButton("💸 تعديل حد الخسارة بالمبلغ", callback_data="set_max_loss_amount")],
            [InlineKeyboardButton("📅 تعديل الحد اليومي", callback_data="set_daily_loss_limit")],
            [InlineKeyboardButton("📆 تعديل الحد الأسبوعي", callback_data="set_weekly_loss_limit")],
            [InlineKeyboardButton(f"⏹️ إيقاف التداول عند الخسارة", callback_data="toggle_stop_trading")],
            [InlineKeyboardButton("📊 عرض إحصائيات المخاطر", callback_data="show_risk_stats")],
            [InlineKeyboardButton("🔄 إعادة تعيين الإحصائيات", callback_data="reset_risk_stats")],
            [InlineKeyboardButton("📖 شرح مفصل للخيارات", callback_data="risk_management_guide")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(risk_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في إرسال قائمة إدارة المخاطر: {e}")
        try:
            await message.reply_text(f"❌ خطأ في إرسال قائمة إدارة المخاطر: {e}")
        except Exception as reply_error:
            logger.error(f"خطأ في إرسال رسالة الخطأ: {reply_error}")

async def risk_management_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شرح مفصل لنظام إدارة المخاطر"""
    try:
        query = update.callback_query
        await query.answer()
        
        guide_message = """
📖 **دليل إدارة المخاطر المفصل**

🔍 **الفرق بين الخيارات:**

🛡️ **إدارة المخاطر (Risk Management):**
هذا هو النظام الكامل لإدارة المخاطر:

✅ **عند التفعيل:**
• مراقبة مستمرة للخسائر بعد كل صفقة
• فحص الحدود المحددة (يومية، أسبوعية، مئوية، بالمبلغ)
• حساب الإحصائيات وتحديثها تلقائياً
• إعادة تعيين الخسارة اليومية والأسبوعية تلقائياً
• إشعارات عند الوصول للحدود
• توصيات ذكية بناءً على الأداء

❌ **عند التعطيل:**
• لا يوجد مراقبة للخسائر
• لا يوجد فحص للحدود
• لا يوجد تحديث للإحصائيات
• لا يوجد إعادة تعيين تلقائية
• لا يوجد إشعارات أو توصيات
• النظام معطل بالكامل

⏹️ **إيقاف التداول عند الخسارة (Stop Trading on Loss):**
هذا هو جزء من نظام إدارة المخاطر:

✅ **عند التفعيل:**
• إيقاف البوت تلقائياً عند الوصول لأي حد
• منع تنفيذ صفقات جديدة
• إرسال إشعار للمستخدم
• حماية الرصيد من المزيد من الخسائر
• **ملاحظة مهمة:** الإيقاف يحدث فقط إذا كان هذا الخيار مفعل!

❌ **عند التعطيل:**
• البوت يستمر في التداول حتى لو وصل للحدود
• لا يوجد إيقاف تلقائي
• لا يوجد حماية من المزيد من الخسائر
• المخاطر عالية جداً
• **تحذير:** حتى لو وصلت للحدود، البوت لن يتوقف!

📊 **مثال عملي:**

السيناريو: الحد اليومي 500 USDT، الخسارة الحالية 450 USDT، صفقة جديدة خسارة 100 USDT

🟢 **إدارة المخاطر مفعلة + إيقاف التداول مفعل:**
• النظام يراقب الخسائر ✅
• يحسب الخسارة الجديدة: 450 + 100 = 550 USDT ✅
• يكتشف تجاوز الحد اليومي (550 > 500) ✅
• يوقف البوت تلقائياً ✅
• يرسل إشعار للمستخدم ✅
• يحمي الرصيد من المزيد من الخسائر ✅

🟡 **إدارة المخاطر مفعلة + إيقاف التداول معطل:**
• النظام يراقب الخسائر ✅
• يحسب الخسارة الجديدة: 450 + 100 = 550 USDT ✅
• يكتشف تجاوز الحد اليومي (550 > 500) ✅
• لكن البوت يستمر في التداول ❌
• لا يوجد حماية من المزيد من الخسائر ❌
• خطر عالي! ⚠️

🔴 **إدارة المخاطر معطلة:**
• لا يوجد مراقبة للخسائر ❌
• لا يوجد فحص للحدود ❌
• لا يوجد إيقاف تلقائي ❌
• لا يوجد حماية ❌
• لا يوجد إشعارات ❌
• خطر عالي جداً! 🚨

💡 **التوصيات:**

🟢 **الأفضل (آمن):**
• إدارة المخاطر: مفعل
• إيقاف التداول: مفعل
• النتيجة: حماية كاملة ومثالية

🟡 **مقبول (حذر):**
• إدارة المخاطر: مفعل
• إيقاف التداول: معطل
• النتيجة: مراقبة بدون حماية تلقائية

🔴 **خطير (غير موصى به):**
• إدارة المخاطر: معطل
• إيقاف التداول: معطل
• النتيجة: لا يوجد حماية على الإطلاق

🎯 **الخلاصة:**
إدارة المخاطر = النظام الكامل للمراقبة والتحليل
إيقاف التداول = الإجراء الوقائي عند الخطر

الأفضل هو تفعيل الاثنين معاً للحصول على حماية كاملة! 🛡️✨
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع إلى إدارة المخاطر", callback_data="risk_management_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(guide_message, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as edit_error:
            if "Message is not modified" in str(edit_error):
                pass
            else:
                raise edit_error
        
    except Exception as e:
        logger.error(f"خطأ في عرض دليل إدارة المخاطر: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

# ===== نظام إدارة المخاطر المتقدم =====

def check_risk_management(user_id: int, trade_result: dict) -> dict:
    """التحقق من إدارة المخاطر وإيقاف البوت عند الحاجة"""
    try:
        user_data = user_manager.get_user(user_id)
        if not user_data:
            return {'should_stop': False, 'message': 'No user data'}
        
        # الحصول على إعدادات إدارة المخاطر
        risk_settings = user_data.get('risk_management', {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        })
        
        if not risk_settings.get('enabled', True):
            return {'should_stop': False, 'message': 'Risk management disabled'}
        
        # حساب الخسارة من الصفقة
        trade_pnl = trade_result.get('pnl', 0)
        if trade_pnl >= 0:  # ربح، لا نحتاج للتحقق
            return {'should_stop': False, 'message': 'Profitable trade'}
        
        loss_amount = abs(trade_pnl)
        
        # تحديث إحصائيات الخسارة
        current_daily_loss = user_data.get('daily_loss', 0)
        current_weekly_loss = user_data.get('weekly_loss', 0)
        current_total_loss = user_data.get('total_loss', 0)
        
        new_daily_loss = current_daily_loss + loss_amount
        new_weekly_loss = current_weekly_loss + loss_amount
        new_total_loss = current_total_loss + loss_amount
        
        # التحقق من الحدود
        max_loss_percent = risk_settings.get('max_loss_percent', 10.0)
        max_loss_amount = risk_settings.get('max_loss_amount', 1000.0)
        daily_limit = risk_settings.get('daily_loss_limit', 500.0)
        weekly_limit = risk_settings.get('weekly_loss_limit', 2000.0)
        
        # حساب النسبة المئوية للخسارة من الرصيد
        account_type = user_data.get('account_type', 'demo')
        if account_type == 'demo':
            # للحساب التجريبي، نحصل على الرصيد من الحساب التجريبي
            spot_account = trading_bot.demo_account_spot
            futures_account = trading_bot.demo_account_futures
            spot_info = spot_account.get_account_info()
            futures_info = futures_account.get_account_info()
            total_balance = spot_info['balance'] + futures_info['balance']
        else:
            # للحساب الحقيقي، نحصل على الرصيد من المنصات المرتبطة
            total_balance = 0
            bybit_connected = user_data.get('bybit_api_connected', False)
            mexc_connected = user_data.get('mexc_api_connected', False)
            
            if bybit_connected:
                try:
                    bybit_account = user_manager.get_user_account(user_id, 'bybit')
                    if bybit_account:
                        bybit_info = bybit_account.get_account_info()
                        total_balance += bybit_info.get('balance', 0)
                except:
                    pass
            
            if mexc_connected:
                try:
                    mexc_account = user_manager.get_user_account(user_id, 'mexc')
                    if mexc_account:
                        mexc_info = mexc_account.get_account_info()
                        total_balance += mexc_info.get('balance', 0)
                except:
                    pass
        
        # حساب النسبة المئوية للخسارة
        loss_percent = (new_total_loss / total_balance * 100) if total_balance > 0 else 0
        
        # تحديد ما إذا كان يجب إيقاف البوت
        should_stop = False
        stop_reason = ""
        
        if risk_settings.get('stop_trading_on_loss', True):
            # التحقق من الحد اليومي
            if new_daily_loss >= daily_limit:
                should_stop = True
                stop_reason = f"تم الوصول للحد اليومي ({daily_limit} USDT)"
            
            # التحقق من الحد الأسبوعي
            elif new_weekly_loss >= weekly_limit:
                should_stop = True
                stop_reason = f"تم الوصول للحد الأسبوعي ({weekly_limit} USDT)"
            
            # التحقق من الحد المئوي
            elif loss_percent >= max_loss_percent:
                should_stop = True
                stop_reason = f"تم الوصول للحد المئوي ({max_loss_percent}%)"
            
            # التحقق من الحد بالمبلغ
            elif new_total_loss >= max_loss_amount:
                should_stop = True
                stop_reason = f"تم الوصول للحد بالمبلغ ({max_loss_amount} USDT)"
        
        # تحديث الإحصائيات في قاعدة البيانات
        user_manager.update_user(user_id, {
            'daily_loss': new_daily_loss,
            'weekly_loss': new_weekly_loss,
            'total_loss': new_total_loss,
            'last_loss_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # إيقاف البوت إذا لزم الأمر
        if should_stop:
            user_manager.update_user(user_id, {'is_active': False})
            
            # إرسال إشعار للمستخدم
            try:
                from config import TELEGRAM_TOKEN, ADMIN_USER_ID
                from telegram.ext import Application
                
                async def send_stop_notification():
                    try:
                        application = Application.builder().token(TELEGRAM_TOKEN).build()
                        await application.initialize()
                        
                        stop_message = f"""
🚨 **تم إيقاف البوت تلقائياً**

📊 **سبب الإيقاف:** {stop_reason}

💰 **إحصائيات الخسارة:**
📅 اليومية: {new_daily_loss:.2f} USDT
📆 الأسبوعية: {new_weekly_loss:.2f} USDT
📉 الإجمالية: {new_total_loss:.2f} USDT

🛡️ **حدود المخاطر:**
📅 الحد اليومي: {daily_limit:.0f} USDT
📆 الحد الأسبوعي: {weekly_limit:.0f} USDT
📊 الحد المئوي: {max_loss_percent:.1f}%
💸 الحد بالمبلغ: {max_loss_amount:.0f} USDT

⚠️ **لإعادة تشغيل البوت، اذهب إلى الإعدادات وافعل زر التشغيل**
                        """
                        
                        await application.bot.send_message(
                            chat_id=user_id,
                            text=stop_message,
                            parse_mode='Markdown'
                        )
                        
                        await application.shutdown()
                    except Exception as e:
                        logger.error(f"خطأ في إرسال إشعار الإيقاف: {e}")
                
                # تشغيل الإشعار في الخلفية
                import asyncio
                asyncio.create_task(send_stop_notification())
                
            except Exception as e:
                logger.error(f"خطأ في إعداد إشعار الإيقاف: {e}")
        
        return {
            'should_stop': should_stop,
            'message': stop_reason if should_stop else 'Risk check passed',
            'daily_loss': new_daily_loss,
            'weekly_loss': new_weekly_loss,
            'total_loss': new_total_loss,
            'loss_percent': loss_percent
        }
        
    except Exception as e:
        logger.error(f"خطأ في فحص إدارة المخاطر: {e}")
        return {'should_stop': False, 'message': f'Error: {e}'}

def reset_daily_loss_if_needed(user_id: int):
    """إعادة تعيين الخسارة اليومية إذا كان اليوم جديد"""
    try:
        user_data = user_manager.get_user(user_id)
        if not user_data:
            return
        
        last_reset_date = user_data.get('last_reset_date', '')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        if last_reset_date != current_date:
            # إعادة تعيين الخسارة اليومية
            user_manager.update_user(user_id, {
                'daily_loss': 0,
                'last_reset_date': current_date
            })
            
            # إعادة تعيين الخسارة الأسبوعية إذا كان الأسبوع جديد
            last_reset_week = user_data.get('last_reset_week', '')
            current_week = datetime.now().strftime('%Y-W%U')
            
            if last_reset_week != current_week:
                user_manager.update_user(user_id, {
                    'weekly_loss': 0,
                    'last_reset_week': current_week
                })
                
    except Exception as e:
        logger.error(f"خطأ في إعادة تعيين الخسارة اليومية: {e}")

async def quick_auto_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعداد سريع للإعدادات التلقائية"""
    try:
        query = update.callback_query
        await query.answer("⏳ جاري تطبيق الإعداد السريع...")
        
        # إعدادات ذكية افتراضية
        success = trade_tools_manager.save_auto_settings(
            tp_percentages=[1.5, 3.0, 5.0],
            tp_close_percentages=[50, 30, 20],
            sl_percentage=2.0,
            trailing_enabled=False,
            trailing_distance=2.0,
            breakeven_on_tp1=True
        )
        
        if success:
            trade_tools_manager.enable_auto_apply()
            
            message = """
✅ **تم تطبيق الإعداد السريع بنجاح!**

🎯 **أهداف الربح:**
• TP1: +1.5% → إغلاق 50%
• TP2: +3.0% → إغلاق 30%
• TP3: +5.0% → إغلاق 20%

🛑 **Stop Loss:** -2%

🔁 **نقل تلقائي للتعادل** عند تحقيق TP1

✅ **التطبيق التلقائي مُفعّل**

💡 الآن كل صفقة جديدة ستحصل على هذه الإعدادات تلقائياً!
            """
            
            keyboard = [[
                InlineKeyboardButton("⚙️ تعديل", callback_data="edit_auto_settings"),
                InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ فشل في تطبيق الإعداد السريع")
            
    except Exception as e:
        logger.error(f"خطأ في الإعداد السريع: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def edit_auto_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل الإعدادات التلقائية"""
    try:
        query = update.callback_query
        await query.answer()
        
        current_settings = ""
        if trade_tools_manager.default_tp_percentages:
            current_settings += "🎯 **الأهداف الحالية:**\n"
            for i, (tp, close) in enumerate(zip(trade_tools_manager.default_tp_percentages,
                                                trade_tools_manager.default_tp_close_percentages), 1):
                current_settings += f"• TP{i}: +{tp}% → {close}%\n"
        else:
            current_settings += "🎯 لا توجد أهداف محددة\n"
        
        current_settings += "\n"
        
        if trade_tools_manager.default_sl_percentage > 0:
            current_settings += f"🛑 **Stop Loss:** -{trade_tools_manager.default_sl_percentage}%\n"
            if trade_tools_manager.default_trailing_enabled:
                current_settings += f"⚡ **Trailing:** نعم ({trade_tools_manager.default_trailing_distance}%)\n"
        else:
            current_settings += "🛑 لا يوجد Stop Loss\n"
        
        message = f"""
⚙️ **تعديل الإعدادات التلقائية**

{current_settings}

اختر ما تريد تعديله:
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 تعديل أهداف الربح", callback_data="edit_auto_tp")],
            [InlineKeyboardButton("🛑 تعديل Stop Loss", callback_data="edit_auto_sl")],
            [InlineKeyboardButton("⚡ تفعيل/تعطيل Trailing", callback_data="toggle_auto_trailing")],
            [InlineKeyboardButton("🎲 إعداد سريع", callback_data="quick_auto_setup")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في تعديل الإعدادات: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def edit_auto_tp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل أهداف الربح التلقائية - واجهة تفاعلية"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id if update.effective_user else None
        if user_id:
            # حفظ الحالة مع بيانات مؤقتة
            if 'auto_tp_builder' not in context.user_data:
                context.user_data['auto_tp_builder'] = {
                    'targets': [],
                    'step': 'count'  # count, tp1, tp2, etc.
                }
            user_input_state[user_id] = "building_auto_tp_count"
        
        message = """
🎯 **إعداد أهداف الربح التلقائية**

**الخطوة 1 من 2:** كم هدف تريد إضافة؟

💡 **أمثلة:**
• `1` → هدف واحد فقط
• `2` → هدفين
• `3` → ثلاثة أهداف (موصى به)

📊 **الحد الأقصى:** 5 أهداف

أدخل الرقم:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("1️⃣", callback_data="auto_tp_targets_1"),
                InlineKeyboardButton("2️⃣", callback_data="auto_tp_targets_2"),
                InlineKeyboardButton("3️⃣", callback_data="auto_tp_targets_3")
            ],
            [
                InlineKeyboardButton("4️⃣", callback_data="auto_tp_targets_4"),
                InlineKeyboardButton("5️⃣", callback_data="auto_tp_targets_5")
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في edit_auto_tp: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_auto_tp_targets_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين عدد الأهداف"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج العدد
        count = int(query.data.replace("auto_tp_targets_", ""))
        
        # حفظ في context
        if 'auto_tp_builder' not in context.user_data:
            context.user_data['auto_tp_builder'] = {}
        
        context.user_data['auto_tp_builder']['count'] = count
        context.user_data['auto_tp_builder']['targets'] = []
        context.user_data['auto_tp_builder']['current_target'] = 1
        
        user_id = update.effective_user.id if update.effective_user else None
        if user_id:
            user_input_state[user_id] = f"building_auto_tp_target_1_percent"
        
        message = f"""
🎯 **هدف الربح رقم 1 من {count}**

**الخطوة 2:** أدخل نسبة الربح لهذا الهدف

💡 **أمثلة:**
• `1.5` → هدف عند +1.5%
• `2` → هدف عند +2%
• `3` → هدف عند +3%
• `5` → هدف عند +5%

📊 **نطاق مقترح:** 0.5% إلى 20%

أدخل النسبة:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("1%", callback_data="quick_tp_1"),
                InlineKeyboardButton("1.5%", callback_data="quick_tp_1.5"),
                InlineKeyboardButton("2%", callback_data="quick_tp_2")
            ],
            [
                InlineKeyboardButton("3%", callback_data="quick_tp_3"),
                InlineKeyboardButton("5%", callback_data="quick_tp_5"),
                InlineKeyboardButton("10%", callback_data="quick_tp_10")
            ],
            [InlineKeyboardButton("✏️ إدخال رقم مخصص", callback_data="custom_tp_percent_input")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في set_auto_tp_targets_count: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def process_tp_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE, tp_percent: float = None):
    """معالجة إدخال هدف TP"""
    try:
        user_id = update.effective_user.id if update.effective_user else None
        builder = context.user_data.get('auto_tp_builder', {})
        
        current_target = builder.get('current_target', 1)
        total_count = builder.get('count', 3)
        
        # إذا تم توفير النسبة (من زر سريع)
        if tp_percent is not None:
            if 'temp_tp_percent' not in builder:
                builder['temp_tp_percent'] = tp_percent
        
        # الانتقال لإدخال نسبة الإغلاق
        if user_id:
            user_input_state[user_id] = f"building_auto_tp_target_{current_target}_close"
        
        tp_pct = builder.get('temp_tp_percent', 0)
        
        message = f"""
🎯 **هدف الربح رقم {current_target} من {total_count}**

✅ **نسبة الربح:** +{tp_pct}%

**الآن:** أدخل نسبة الإغلاق عند هذا الهدف

💡 **أمثلة:**
• `25` → إغلاق 25% من الصفقة
• `33` → إغلاق 33% من الصفقة
• `50` → إغلاق نصف الصفقة
• `100` → إغلاق كامل الصفقة

📊 **نطاق مسموح:** 1% إلى 100%

أدخل النسبة:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("25%", callback_data="quick_close_25"),
                InlineKeyboardButton("33%", callback_data="quick_close_33"),
                InlineKeyboardButton("50%", callback_data="quick_close_50")
            ],
            [
                InlineKeyboardButton("75%", callback_data="quick_close_75"),
                InlineKeyboardButton("100%", callback_data="quick_close_100")
            ],
            [InlineKeyboardButton("✏️ إدخال رقم مخصص", callback_data="custom_close_percent_input")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.message:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في process_tp_target_input: {e}")

async def finalize_tp_target(update: Update, context: ContextTypes.DEFAULT_TYPE, close_percent: float = None):
    """إنهاء إدخال هدف واحد والانتقال للتالي أو الحفظ"""
    try:
        builder = context.user_data.get('auto_tp_builder', {})
        
        tp_pct = builder.get('temp_tp_percent', 0)
        if close_percent is None:
            close_percent = 50  # افتراضي
        
        # حفظ الهدف
        if 'targets' not in builder:
            builder['targets'] = []
        builder['targets'].append({'tp': tp_pct, 'close': close_percent})
        
        current_target = builder.get('current_target', 1)
        total_count = builder.get('count', 3)
        
        # عرض معاينة
        preview = "📋 **معاينة الأهداف المضافة:**\n\n"
        for i, target in enumerate(builder['targets'], 1):
            preview += f"• TP{i}: +{target['tp']}% → إغلاق {target['close']}%\n"
        
        if current_target < total_count:
            # الانتقال للهدف التالي
            builder['current_target'] = current_target + 1
            builder['temp_tp_percent'] = None
            
            user_id = update.effective_user.id if update.effective_user else None
            if user_id:
                user_input_state[user_id] = f"building_auto_tp_target_{current_target + 1}_percent"
            
            message = f"""
✅ **تم إضافة الهدف {current_target}!**

{preview}

➡️ **التالي:** هدف الربح رقم {current_target + 1} من {total_count}

أدخل نسبة الربح:
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("1%", callback_data="quick_tp_1"),
                    InlineKeyboardButton("1.5%", callback_data="quick_tp_1.5"),
                    InlineKeyboardButton("2%", callback_data="quick_tp_2")
                ],
                [
                    InlineKeyboardButton("3%", callback_data="quick_tp_3"),
                    InlineKeyboardButton("5%", callback_data="quick_tp_5"),
                    InlineKeyboardButton("10%", callback_data="quick_tp_10")
                ],
                [InlineKeyboardButton("✏️ إدخال رقم مخصص", callback_data="custom_tp_percent_input")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
            ]
        else:
            # حفظ نهائي
            tp_percentages = [t['tp'] for t in builder['targets']]
            tp_close_percentages = [t['close'] for t in builder['targets']]
            
            success = trade_tools_manager.save_auto_settings(
                tp_percentages=tp_percentages,
                tp_close_percentages=tp_close_percentages,
                sl_percentage=trade_tools_manager.default_sl_percentage,
                trailing_enabled=trade_tools_manager.default_trailing_enabled,
                trailing_distance=trade_tools_manager.default_trailing_distance,
                breakeven_on_tp1=True
            )
            
            if success:
                message = f"""
✅ **تم حفظ جميع الأهداف بنجاح!**

{preview}

💾 **تم الحفظ في الإعدادات التلقائية**

🤖 الآن كل صفقة جديدة ستحصل على هذه الأهداف تلقائياً!
                """
                
                keyboard = [[
                    InlineKeyboardButton("✅ تفعيل التطبيق التلقائي", callback_data="toggle_auto_apply"),
                    InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")
                ]]
            else:
                message = "❌ فشل في حفظ الإعدادات"
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")]]
            
            # مسح البيانات المؤقتة
            if 'auto_tp_builder' in context.user_data:
                del context.user_data['auto_tp_builder']
            user_id = update.effective_user.id if update.effective_user else None
            if user_id and user_id in user_input_state:
                del user_input_state[user_id]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.message:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في finalize_tp_target: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def edit_auto_sl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل Stop Loss التلقائي - واجهة تفاعلية"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id if update.effective_user else None
        if user_id:
            user_input_state[user_id] = "waiting_auto_sl_simple"
        
        current_sl = trade_tools_manager.default_sl_percentage
        
        message = f"""
🛑 **تعديل Stop Loss التلقائي**

{'✅ **الحالي:** -' + str(current_sl) + '%' if current_sl > 0 else '⏸️ **غير محدد حالياً**'}

**اختر نسبة Stop Loss:**

💡 **التوصيات:**
• **محافظ:** 1-2% (حماية قوية)
• **متوازن:** 2-3% (موصى به)
• **عدواني:** 3-5% (مجال أكبر)

أو أدخل نسبة مخصصة:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("1% 🛡️", callback_data="quick_sl_1"),
                InlineKeyboardButton("1.5% 🛡️", callback_data="quick_sl_1.5"),
                InlineKeyboardButton("2% ⭐", callback_data="quick_sl_2")
            ],
            [
                InlineKeyboardButton("2.5%", callback_data="quick_sl_2.5"),
                InlineKeyboardButton("3%", callback_data="quick_sl_3"),
                InlineKeyboardButton("5%", callback_data="quick_sl_5")
            ],
            [InlineKeyboardButton("✏️ إدخال مخصص", callback_data="custom_sl_input")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في edit_auto_sl: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def toggle_auto_trailing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تبديل حالة Trailing Stop التلقائي"""
    try:
        query = update.callback_query
        await query.answer()
        
        trade_tools_manager.default_trailing_enabled = not trade_tools_manager.default_trailing_enabled
        
        if trade_tools_manager.default_trailing_enabled:
            message = f"""
✅ **تم تفعيل Trailing Stop التلقائي**

⚡ المسافة: {trade_tools_manager.default_trailing_distance}%

💡 الآن كل صفقة جديدة ستحصل على Trailing Stop بدلاً من SL الثابت

⚠️ **تحذير:** Trailing Stop يتحرك مع السعر ولا يمكن أن ينخفض
            """
        else:
            message = """
⏸️ **تم تعطيل Trailing Stop التلقائي**

الصفقات الجديدة ستحصل على Stop Loss ثابت
            """
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في toggle trailing: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def clear_auto_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف جميع الإعدادات التلقائية"""
    try:
        query = update.callback_query
        await query.answer()
        
        # حذف جميع الإعدادات
        trade_tools_manager.default_tp_percentages = []
        trade_tools_manager.default_tp_close_percentages = []
        trade_tools_manager.default_sl_percentage = 0
        trade_tools_manager.default_trailing_enabled = False
        trade_tools_manager.disable_auto_apply()
        
        message = """
✅ **تم حذف جميع الإعدادات التلقائية**

⏸️ تم تعطيل التطبيق التلقائي

💡 يمكنك إعداد إعدادات جديدة في أي وقت
        """
        
        keyboard = [[
            InlineKeyboardButton("🎲 إعداد جديد", callback_data="quick_auto_setup"),
            InlineKeyboardButton("🔙 رجوع", callback_data="auto_apply_menu")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في حذف الإعدادات: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

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
    
    auto_status = "✅" if trade_tools_manager.auto_apply_enabled else "⏸️"
    
    # الحصول على نوع السوق ونوع الحساب الحالي
    market_type = user_data.get('market_type', 'spot')
    account_type = user_data.get('account_type', 'demo')
    
    # بناء القائمة الأساسية
    keyboard = [
        [InlineKeyboardButton("🏦 اختيار المنصة (Bybit/MEXC)", callback_data="select_exchange")],
        [InlineKeyboardButton("💰 مبلغ التداول", callback_data="set_amount")],
        [InlineKeyboardButton("🏪 نوع السوق", callback_data="set_market")],
        [InlineKeyboardButton("👤 نوع الحساب", callback_data="set_account")]
    ]
    
    # إضافة زر الرافعة المالية فقط إذا كان السوق Futures
    if market_type == 'futures':
        keyboard.append([InlineKeyboardButton("⚡ الرافعة المالية", callback_data="set_leverage")])
    
    # إضافة زر رصيد الحساب التجريبي فقط إذا كان نوع الحساب تجريبي
    if account_type == 'demo':
        keyboard.append([InlineKeyboardButton("💳 رصيد الحساب التجريبي", callback_data="set_demo_balance")])
    
    # إضافة باقي الأزرار
    keyboard.extend([
        [InlineKeyboardButton(f"🤖 تطبيق تلقائي TP/SL {auto_status}", callback_data="auto_apply_menu")],
        [InlineKeyboardButton("🛡️ إدارة المخاطر", callback_data="risk_management_menu")],
        [InlineKeyboardButton("🔗 رابط الإشارات", callback_data="webhook_url")]
    ])
    
    # إضافة زر تشغيل/إيقاف البوت
    if user_data.get('is_active'):
        keyboard.append([InlineKeyboardButton("⏹️ إيقاف البوت", callback_data="toggle_bot")])
    else:
        keyboard.append([InlineKeyboardButton("▶️ تشغيل البوت", callback_data="toggle_bot")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # الحصول على معلومات حساب المستخدم
    market_type = user_data.get('market_type', 'spot')
    
    # 🔍 التحقق من نوع الحساب وجلب البيانات المناسبة
    if account_type == 'real':
        # 🔴 حساب حقيقي - جلب البيانات من المنصة عبر real_account_manager
        exchange = user_data.get('exchange', 'bybit')
        logger.info(f"🔴 جلب بيانات الحساب الحقيقي من {exchange.upper()} للمستخدم {user_id}")
        
        try:
            from real_account_manager import real_account_manager
            
            real_account = real_account_manager.get_account(user_id)
            
            if real_account:
                # تمرير نوع السوق لجلب الرصيد الصحيح (spot أو futures)
                balance = real_account.get_wallet_balance(market_type)
                
                if balance:
                    account_info = {
                        'balance': balance.get('total_equity', 0),
                        'available_balance': balance.get('available_balance', 0),
                        'margin_locked': balance.get('total_wallet_balance', 0) - balance.get('available_balance', 0),
                        'unrealized_pnl': balance.get('unrealized_pnl', 0)
                    }
                    
                    logger.info(f"✅ تم جلب بيانات المحفظة من {exchange} ({market_type}): الرصيد={account_info['balance']:.2f}, المتاح={account_info['available_balance']:.2f}")
                else:
                    logger.warning(f"⚠️ فشل جلب بيانات المحفظة من {exchange}")
                    account_info = {
                        'balance': 0.0,
                        'available_balance': 0.0,
                        'margin_locked': 0.0,
                        'unrealized_pnl': 0.0
                    }
            else:
                logger.warning(f"⚠️ الحساب الحقيقي غير مهيأ للمستخدم {user_id}")
                account_info = {
                    'balance': 0.0,
                    'available_balance': 0.0,
                    'margin_locked': 0.0,
                    'unrealized_pnl': 0.0
                }
        except Exception as e:
            logger.error(f"❌ خطأ في جلب بيانات المحفظة: {e}")
            import traceback
            traceback.print_exc()
            account_info = {
                'balance': 0.0,
                'available_balance': 0.0,
                'margin_locked': 0.0,
                'unrealized_pnl': 0.0
            }
    else:
        # 🟢 حساب تجريبي - جلب البيانات من الحساب المحلي
        logger.info(f"🟢 عرض بيانات الحساب التجريبي للمستخدم {user_id}")
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
    
    # التحقق من حالة API حسب المنصة
    exchange = user_data.get('exchange', 'bybit')
    
    if exchange == 'bybit':
        api_key = user_data.get('bybit_api_key', '')
        api_secret = user_data.get('bybit_api_secret', '')
        from config import BYBIT_API_KEY
        default_key = BYBIT_API_KEY if BYBIT_API_KEY else ''
        is_linked = api_key and api_key != default_key and len(api_key) > 10
    elif exchange == 'mexc':
        api_key = user_data.get('mexc_api_key', '')
        api_secret = user_data.get('mexc_api_secret', '')
        is_linked = api_key and api_key != '' and len(api_key) > 10
    else:
        is_linked = False
    
    # تحديد حالة API
    if account_type == 'real' and is_linked:
        api_status = f"🟢 مرتبط ({exchange.upper()})"
    elif is_linked:
        api_status = f"🔗 مرتبط ({exchange.upper()}) - غير مفعّل"
    else:
        api_status = "🔴 غير مرتبط"
    
    trade_amount = user_data.get('trade_amount', 100.0)
    leverage = user_data.get('leverage', 10)
    
    # بناء نص الإعدادات بشكل ديناميكي
    settings_text = f"""
⚙️ إعدادات البوت الحالية:

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

💰 مبلغ التداول: {trade_amount}
🏪 نوع السوق: {market_type.upper()}
👤 نوع الحساب: {'حقيقي' if account_type == 'real' else 'تجريبي داخلي'}"""
    
    # إضافة معلومات الرافعة المالية فقط للفيوتشر
    if market_type == 'futures':
        settings_text += f"\n⚡ الرافعة المالية: {leverage}x"
    
    settings_text += f"""

📊 معلومات الحساب الحالي ({market_type.upper()}):
💰 الرصيد الكلي: {account_info.get('balance', 0):.2f}
💳 الرصيد المتاح: {account_info.get('available_balance', 0):.2f}"""
    
    # إضافة معلومات الهامش المحجوز فقط للفيوتشر
    if market_type == 'futures':
        settings_text += f"\n🔒 الهامش المحجوز: {account_info.get('margin_locked', 0):.2f}"
        settings_text += f"\n📈 الربح/الخسارة غير المحققة: {account_info.get('unrealized_pnl', 0):.2f}"
    
    settings_text += "\n    "
    
    if update.callback_query is not None:
        await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup)
    elif update.message is not None:
        await update.message.reply_text(settings_text, reply_markup=reply_markup)

async def account_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة الحساب الفنية والاتصال"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ لم يتم العثور على بيانات المستخدم")
        return
    
    try:
        # التحقق من نوع الحساب
        account_type = user_data.get('account_type', 'demo')
        market_type = user_data.get('market_type', 'spot')
        
        # بناء رسالة حالة الحساب
        status_message = "📊 **حالة الحساب الفنية**\n\n"
        
        # معلومات الحساب الأساسية
        status_message += f"""
🔐 **معلومات الحساب:**
👤 نوع الحساب: {account_type.upper()}
🏪 نوع السوق: {market_type.upper()}"""
        
        # إضافة الرافعة المالية فقط للفيوتشر
        if market_type.lower() == 'futures':
            status_message += f"""
🔢 الرافعة المالية: {trading_bot.user_settings['leverage']}x"""
        
        status_message += f"""
💰 مبلغ التداول: {trading_bot.user_settings['trade_amount']} USDT
        """
        
        # حالة الاتصال
        if account_type == 'real':
            status_message += "\n🔗 **حالة الاتصال:**\n"
            
            # التحقق من المنصات المرتبطة
            bybit_connected = user_data.get('bybit_api_connected', False)
            mexc_connected = user_data.get('mexc_api_connected', False)
            
            if bybit_connected:
                status_message += "🏦 Bybit: 🟢 متصل ✅\n"
            else:
                status_message += "🏦 Bybit: 🔴 غير متصل ❌\n"
            
            if mexc_connected:
                status_message += "🏦 MEXC: 🟢 متصل ✅\n"
            else:
                status_message += "🏦 MEXC: 🔴 غير متصل ❌\n"
            
            # معلومات API
            if bybit_connected or mexc_connected:
                status_message += f"""
📡 **معلومات API:**
🔑 API Keys: {'🟢 مفعلة' if user_data.get('api_connected', False) else '🔴 معطلة'}
🔒 الصلاحيات: Trading Enabled
🌐 البيئة: Production
⏰ آخر تحديث: {user_data.get('last_api_check', 'لم يتم التحقق')}
                """
            else:
                status_message += "\n⚠️ **لا توجد منصات مرتبطة**\n"
                status_message += "اذهب إلى الإعدادات لربط حسابك الحقيقي\n"
        else:
            status_message += f"""
🔗 **حالة الاتصال:**
🟢 الحساب التجريبي: نشط ✅
📊 البيانات: محلية
🔄 التحديث: فوري
⏰ آخر نشاط: {user_data.get('last_activity', 'الآن')}
            """
        
        # إعدادات التداول المتقدمة
        # فحص إعدادات إدارة المخاطر من بيانات المستخدم
        risk_settings = user_data.get('risk_management', {
            'enabled': True,
            'max_loss_percent': 10.0,
            'max_loss_amount': 1000.0,
            'stop_trading_on_loss': True,
            'daily_loss_limit': 500.0,
            'weekly_loss_limit': 2000.0
        })
        
        risk_management_status = "مفعل" if risk_settings.get('enabled', True) else "معطل"
        
        status_message += f"""

⚙️ **إعدادات التداول المتقدمة:**
🎯 Stop Loss: {trading_bot.user_settings.get('stop_loss', 'غير محدد')}%
🎯 Take Profit: {trading_bot.user_settings.get('take_profit', 'غير محدد')}%
🔄 Auto Close: {'مفعل' if trading_bot.user_settings.get('auto_close', False) else 'معطل'}
📊 Risk Management: {risk_management_status}
        """
        
        # معلومات النظام
        status_message += f"""

🖥️ **معلومات النظام:**
🤖 البوت: نشط ✅
📡 Webhook: {user_data.get('webhook_url', 'غير محدد')}
🔄 آخر إشارة: {user_data.get('last_signal_time', 'لم يتم استقبال إشارات')}
📊 إجمالي الإشارات: {user_data.get('total_signals', 0)}
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض حالة الحساب: {e}")
        await update.message.reply_text("❌ خطأ في عرض حالة الحساب")

async def open_positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الصفقات المفتوحة مع معلومات مفصلة للفيوتشر والسبوت"""
    try:
        # الحصول على معرف المستخدم
        user_id = update.effective_user.id if update.effective_user else None
        
        # جمع جميع الصفقات المفتوحة من المصادر المختلفة
        all_positions = {}
        
        # 🔍 التحقق من نوع الحساب
        user_settings = user_manager.get_user_settings(user_id) if user_id else None
        account_type = user_settings.get('account_type', 'demo') if user_settings else 'demo'
        market_type = user_settings.get('market_type', 'spot') if user_settings else 'spot'
        
        logger.info(f"👤 المستخدم {user_id}: الحساب={account_type}, السوق={market_type}")
        
        if account_type == 'real':
            # 🔴 حساب حقيقي - جلب الصفقات من المنصة
            from real_account_manager import real_account_manager
            
            real_account = real_account_manager.get_account(user_id)
            user_data = user_manager.get_user(user_id)
            exchange = user_data.get('exchange', 'bybit') if user_data else 'bybit'
            
            logger.info(f"🔴 جلب الصفقات الحقيقية من منصة {exchange.upper()}...")
            
            try:
                platform_positions = []
                
                if real_account:
                    if exchange == 'bybit' and hasattr(real_account, 'get_open_positions'):
                        # تحديد الفئة بناءً على نوع السوق
                        category = "linear" if market_type == 'futures' else "spot"
                        platform_positions = real_account.get_open_positions(category)
                    elif exchange == 'mexc' and hasattr(real_account, 'get_open_orders'):
                        # MEXC تدعم Spot فقط - جلب الأوامر المفتوحة
                        platform_positions = real_account.get_open_orders()
                
                if platform_positions:
                    logger.info(f"✅ تم جلب {len(platform_positions)} صفقة من المنصة")
                    
                    # تحويل الصفقات من صيغة المنصة إلى صيغة البوت
                    for idx, pos in enumerate(platform_positions):
                        position_id = f"real_{pos.get('symbol')}_{idx}"
                        
                        all_positions[position_id] = {
                            'symbol': pos.get('symbol'),
                            'entry_price': float(pos.get('entry_price', pos.get('avgPrice', pos.get('price', 0)))),
                            'side': pos.get('side', 'Buy').lower(),
                            'account_type': market_type,
                            'leverage': int(pos.get('leverage', 1)),
                            'exchange': exchange,
                            'position_size': float(pos.get('size', 0)),
                            'current_price': float(pos.get('mark_price', pos.get('markPrice', pos.get('avgPrice', 0)))),
                            'pnl_percent': float(pos.get('unrealized_pnl', pos.get('unrealisedPnl', 0))),
                            'liquidation_price': float(pos.get('liquidation_price', pos.get('liqPrice', 0))) if market_type == 'futures' else 0,
                            'is_real_position': True  # علامة للتمييز
                        }
                        
                        logger.info(f"📊 صفقة حقيقية: {pos.get('symbol')} - {pos.get('side')}")
                else:
                    logger.info("لا توجد صفقات مفتوحة على المنصة")
                    
            except Exception as e:
                logger.error(f"❌ خطأ في جلب الصفقات من المنصة: {e}")
                await update.message.reply_text(f"⚠️ تعذر جلب الصفقات من المنصة: {e}\n\nسيتم عرض الصفقات المحلية فقط.")
        
        else:
            # 🟢 حساب تجريبي - جلب الصفقات من داخل البوت
            logger.info("🟢 عرض الصفقات التجريبية من داخل البوت...")
            
            # إضافة صفقات المستخدم من user_manager
            if user_id and user_id in user_manager.user_positions:
                user_positions = user_manager.user_positions[user_id]
                all_positions.update(user_positions)
                logger.info(f"تم العثور على {len(user_positions)} صفقة تجريبية للمستخدم {user_id}")
            
            # إضافة الصفقات من trading_bot.open_positions (للإشارات القديمة)
            all_positions.update(trading_bot.open_positions)
        
        logger.info(f"📊 إجمالي الصفقات المعروضة: {len(all_positions)} صفقة")
        
        # تحديث الأسعار الحالية أولاً
        await trading_bot.update_open_positions_prices()
        
        if not all_positions:
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
        
        for position_id, position_info in all_positions.items():
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
        import traceback
        logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
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
        
        # إضافة أزرار إدارة الصفقة
        pnl_display = f"({pnl_value:+.2f})" if current_price else ""
        spot_keyboard.append([
            InlineKeyboardButton(f"⚙️ إدارة {symbol}", callback_data=f"manage_{position_id}"),
            InlineKeyboardButton(f"❌ إغلاق {pnl_display}", callback_data=f"close_{position_id}")
        ])
    
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
        
        # إضافة أزرار إدارة الصفقة
        pnl_display = f"({unrealized_pnl:+.2f})" if current_price else ""
        futures_keyboard.append([
            InlineKeyboardButton(f"⚙️ إدارة {symbol}", callback_data=f"manage_{position_id}"),
            InlineKeyboardButton(f"❌ إغلاق {pnl_display}", callback_data=f"close_{position_id}")
        ])
    
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

async def apply_tool_to_real_position(position_info: dict, tool_type: str, **kwargs) -> tuple[bool, str]:
    """تطبيق أداة على صفقة حقيقية عبر Bybit API"""
    try:
        if not trading_bot.bybit_api:
            return False, "❌ API غير متاح"
        
        symbol = position_info['symbol']
        category = position_info.get('category', 'linear')
        is_real = position_info.get('is_real_position', False)
        
        if not is_real:
            # صفقة تجريبية - لا حاجة لتطبيق عبر API
            return True, "✅ تم التطبيق محلياً (صفقة تجريبية)"
        
        logger.info(f"🔴 تطبيق {tool_type} على صفقة حقيقية: {symbol}")
        
        if tool_type == "set_tp":
            # تطبيق Take Profit
            tp_price = kwargs.get('tp_price')
            response = trading_bot.bybit_api.set_trading_stop(
                symbol=symbol,
                category=category,
                take_profit=str(tp_price)
            )
            
        elif tool_type == "set_sl":
            # تطبيق Stop Loss
            sl_price = kwargs.get('sl_price')
            response = trading_bot.bybit_api.set_trading_stop(
                symbol=symbol,
                category=category,
                stop_loss=str(sl_price)
            )
            
        elif tool_type == "set_trailing":
            # تطبيق Trailing Stop
            trailing_distance = kwargs.get('trailing_distance')
            response = trading_bot.bybit_api.set_trading_stop(
                symbol=symbol,
                category=category,
                trailing_stop=str(trailing_distance)
            )
            
        elif tool_type == "partial_close":
            # إغلاق جزئي
            close_percentage = kwargs.get('percentage', 50)
            position_size = position_info.get('position_size', 0)
            close_qty = str((position_size * close_percentage) / 100)
            
            response = trading_bot.bybit_api.close_position(
                symbol=symbol,
                category=category,
                qty=close_qty
            )
            
        elif tool_type == "full_close":
            # إغلاق كامل
            response = trading_bot.bybit_api.close_position(
                symbol=symbol,
                category=category
            )
        
        else:
            return False, f"❌ أداة غير مدعومة: {tool_type}"
        
        # التحقق من النتيجة
        if response.get("retCode") == 0:
            logger.info(f"✅ تم تطبيق {tool_type} بنجاح على {symbol}")
            return True, f"✅ تم تطبيق {tool_type} على المنصة بنجاح"
        else:
            error_msg = response.get("retMsg", "خطأ غير محدد")
            logger.error(f"❌ فشل تطبيق {tool_type}: {error_msg}")
            return False, f"❌ فشل: {error_msg}"
            
    except Exception as e:
        logger.error(f"خطأ في apply_tool_to_real_position: {e}")
        return False, f"❌ خطأ: {e}"

async def manage_position_tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أدوات إدارة الصفقة (TP/SL/Partial Close) - يعمل مع الصفقات الحقيقية والتجريبية"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج position_id من callback_data
        position_id = query.data.replace("manage_", "")
        
        # الحصول على معرف المستخدم
        user_id = update.effective_user.id if update.effective_user else None
        
        # البحث عن الصفقة
        position_info = None
        if user_id and user_id in user_manager.user_positions:
            position_info = user_manager.user_positions[user_id].get(position_id)
        
        if not position_info:
            position_info = trading_bot.open_positions.get(position_id)
        
        if not position_info:
            await query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
        # التحقق من نوع الصفقة
        is_real = position_info.get('is_real_position', False)
        account_indicator = "🔴 حساب حقيقي" if is_real else "🟢 حساب تجريبي"
        
        symbol = position_info['symbol']
        side = position_info['side']
        entry_price = position_info['entry_price']
        current_price = position_info.get('current_price', entry_price)
        
        # التحقق من وجود إدارة للصفقة
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos:
            # إنشاء إدارة جديدة للصفقة
            quantity = position_info.get('amount', position_info.get('margin_amount', 100))
            market_type = position_info.get('account_type', 'spot')
            leverage = position_info.get('leverage', 1)
            
            managed_pos = trade_tools_manager.create_managed_position(
                position_id=position_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                market_type=market_type,
                leverage=leverage
            )
        
        if managed_pos:
            status_message = managed_pos.get_status_message(current_price)
            rr_ratio = managed_pos.calculate_risk_reward_ratio()
            
            if rr_ratio > 0:
                status_message += f"\n⚖️ نسبة المخاطرة/العائد: 1:{rr_ratio:.2f}"
        else:
            status_message = f"📊 **إدارة الصفقة: {symbol}**\n\n"
            status_message += f"🔄 النوع: {side.upper()}\n"
            status_message += f"💲 سعر الدخول: {entry_price:.6f}\n"
            status_message += f"💲 السعر الحالي: {current_price:.6f}\n"
        
        # إضافة مؤشر نوع الحساب
        status_message = f"{account_indicator}\n\n" + status_message
        
        # حالة الأدوات النشطة
        has_tp = managed_pos and len(managed_pos.take_profits) > 0
        has_sl = managed_pos and managed_pos.stop_loss is not None
        is_trailing = managed_pos and managed_pos.stop_loss and managed_pos.stop_loss.is_trailing
        is_breakeven = managed_pos and managed_pos.stop_loss and managed_pos.stop_loss.moved_to_breakeven
        
        # إنشاء أزرار الإدارة مع الحالات
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🎯 أهداف الربح {'✅' if has_tp else '➕'}", 
                    callback_data=f"setTP_menu_{position_id}"
                ),
                InlineKeyboardButton(
                    f"🛑 وقف الخسارة {'✅' if has_sl else '➕'}", 
                    callback_data=f"setSL_menu_{position_id}"
                )
            ],
            [
                InlineKeyboardButton("📊 إغلاق جزئي مخصص", callback_data=f"partial_custom_{position_id}")
            ],
            [
                InlineKeyboardButton(
                    f"🔁 نقل للتعادل {'🔒' if is_breakeven else '⏸️'}", 
                    callback_data=f"moveBE_{position_id}"
                ),
                InlineKeyboardButton(
                    f"⚡ Trailing Stop {'✅' if is_trailing else '⏸️'}", 
                    callback_data=f"trailing_menu_{position_id}"
                )
            ],
            [
                InlineKeyboardButton("🎲 إعداد سريع (ذكي)", callback_data=f"quick_setup_{position_id}"),
                InlineKeyboardButton("ℹ️ دليل الأدوات", callback_data=f"tools_guide_{position_id}")
            ],
            [
                InlineKeyboardButton("❌ إغلاق كامل", callback_data=f"close_{position_id}"),
                InlineKeyboardButton("🔙 رجوع", callback_data="show_positions")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(status_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض أدوات إدارة الصفقة: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def show_tools_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض دليل استخدام الأدوات"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("tools_guide_", "")
        
        guide_text = """
📚 **دليل أدوات إدارة الصفقات**

🎯 **أهداف الربح (Take Profit)**
تحديد مستويات أسعار لإغلاق أجزاء من الصفقة تلقائياً عند الربح
• يمكن إضافة عدة أهداف بنسب مختلفة
• مثال: TP1 عند +2% إغلاق 50%

🛑 **وقف الخسارة (Stop Loss)**
حماية رأس المال بإغلاق الصفقة عند خسارة محددة
• ⚠️ تحذير: Trailing Stop يُلغي SL الثابت تلقائياً
• ينصح بتعيينه عند -2% من سعر الدخول

📊 **الإغلاق الجزئي**
إغلاق نسبة معينة من الصفقة يدوياً
• يمكن إدخال أي نسبة من 1% إلى 100%
• مفيد لتأمين الأرباح مع استمرار الصفقة

🔁 **نقل للتعادل (Break-Even)**
نقل SL إلى سعر الدخول لحماية من الخسارة
• يحدث تلقائياً عند تحقيق أول هدف
• يمكن تفعيله يدوياً في أي وقت

⚡ **Trailing Stop (الإيقاف المتحرك)**
SL يتحرك تلقائياً مع السعر في اتجاه الربح
• ⚠️ تفعيله يُلغي SL الثابت
• يحمي الأرباح المتراكمة
• المسافة الافتراضية: 2%

🎲 **الإعداد السريع**
تطبيق إعدادات ذكية متوازنة:
• 3 أهداف: 1.5%, 3%, 5%
• نسب الإغلاق: 50%, 30%, 20%
• Stop Loss: -2%
• نقل تلقائي للتعادل عند TP1

💡 **نصائح ذكية:**
1. لا تستخدم Trailing Stop و SL الثابت معاً
2. نقل SL للتعادل بعد تحقيق ربح معقول
3. نسبة R:R المثالية: 1:2 أو أكثر
        """
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(guide_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض الدليل: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_tp_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة تعيين أهداف الربح"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("setTP_menu_", "")
        
        message = """
🎯 **تعيين أهداف الربح**

اختر طريقة التعيين:

**تلقائي:** أهداف ذكية جاهزة
• TP1: +1.5% (إغلاق 50%)
• TP2: +3.0% (إغلاق 30%)  
• TP3: +5.0% (إغلاق 20%)

**مخصص:** أدخل نسبة الربح ونسبة الإغلاق بنفسك
        """
        
        keyboard = [
            [InlineKeyboardButton("🎲 تلقائي (ذكي)", callback_data=f"autoTP_{position_id}")],
            [InlineKeyboardButton("✏️ إدخال مخصص", callback_data=f"customTP_{position_id}")],
            [InlineKeyboardButton("🗑️ حذف جميع الأهداف", callback_data=f"clearTP_{position_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في قائمة TP: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_sl_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة تعيين وقف الخسارة"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("setSL_menu_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        has_trailing = managed_pos and managed_pos.stop_loss and managed_pos.stop_loss.is_trailing
        
        message = f"""
🛑 **تعيين وقف الخسارة**

{'⚡ **Trailing Stop نشط حالياً**' if has_trailing else ''}

**تلقائي:** SL ثابت عند -2% من سعر الدخول

**مخصص:** أدخل نسبة الخسارة المقبولة

⚠️ **تحذير:** تفعيل Trailing Stop سيُلغي SL الثابت تلقائياً
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 تلقائي (-2%)", callback_data=f"autoSL_{position_id}")],
            [InlineKeyboardButton("✏️ إدخال مخصص", callback_data=f"customSL_{position_id}")],
            [InlineKeyboardButton("🗑️ حذف Stop Loss", callback_data=f"clearSL_{position_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في قائمة SL: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def trailing_stop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة Trailing Stop"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("trailing_menu_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        is_active = managed_pos and managed_pos.stop_loss and managed_pos.stop_loss.is_trailing
        
        message = f"""
⚡ **Trailing Stop (الإيقاف المتحرك)**

الحالة: {'✅ **نشط**' if is_active else '⏸️ **غير نشط**'}

**كيف يعمل؟**
يتحرك SL تلقائياً مع السعر في اتجاه الربح، ولا ينخفض أبداً

**المسافة:** النسبة بين السعر الحالي و SL

⚠️ **تحذير:** تفعيله سيُلغي Stop Loss الثابت

**مثال:** 
سعر الدخول: 100$
المسافة: 2%
السعر: 110$ → SL: 107.8$
السعر: 120$ → SL: 117.6$
        """
        
        keyboard = [
            [InlineKeyboardButton("⚡ تفعيل (2%)", callback_data=f"trailing_{position_id}")],
            [InlineKeyboardButton("✏️ مسافة مخصصة", callback_data=f"customTrailing_{position_id}")],
            [InlineKeyboardButton("⏸️ تعطيل", callback_data=f"stopTrailing_{position_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"manage_{position_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في قائمة Trailing: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def custom_partial_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال نسبة مخصصة للإغلاق الجزئي"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("partial_custom_", "")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_id:
            user_input_state[user_id] = f"waiting_partial_percentage_{position_id}"
        
        message = """
📊 **إغلاق جزئي مخصص**

أدخل النسبة المئوية التي تريد إغلاقها من الصفقة:

**مثال:**
• 25 (لإغلاق 25%)
• 50 (لإغلاق 50%)
• 17.5 (لإغلاق 17.5%)

**النطاق المسموح:** من 1 إلى 100

💡 **نصيحة:** ابق على الأقل 20% من الصفقة مفتوحة للاستفادة من الحركة
        """
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"manage_{position_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في custom partial: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def quick_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعداد سريع ذكي لجميع الأدوات"""
    try:
        query = update.callback_query
        await query.answer("⏳ جاري تطبيق الإعداد الذكي...")
        
        position_id = query.data.replace("quick_setup_", "")
        
        # تطبيق الإعدادات الذكية
        success = trade_tools_manager.set_default_levels(
            position_id, 
            tp_percentages=[1.5, 3.0, 5.0],
            sl_percentage=2.0,
            trailing=False
        )
        
        if success:
            message = """
✅ **تم تطبيق الإعداد الذكي بنجاح!**

🎯 **أهداف الربح:**
• TP1: +1.5% → إغلاق 50%
• TP2: +3.0% → إغلاق 30%
• TP3: +5.0% → إغلاق 20%

🛑 **Stop Loss:** -2%

🔁 **نقل تلقائي للتعادل** عند تحقيق TP1

⚖️ **نسبة المخاطرة/العائد:** 1:2.5

💡 هذه إعدادات متوازنة توفر حماية جيدة مع إمكانية ربح معقولة
            """
            
            keyboard = [[
                InlineKeyboardButton("⚙️ تعديل", callback_data=f"manage_{position_id}"),
                InlineKeyboardButton("✅ تم", callback_data="show_positions")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ فشل في تطبيق الإعداد السريع")
            
    except Exception as e:
        logger.error(f"خطأ في quick setup: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def custom_tp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال Take Profit مخصص"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("customTP_", "")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_id:
            user_input_state[user_id] = f"waiting_custom_tp_{position_id}"
        
        message = """
🎯 **إدخال هدف ربح مخصص**

أدخل البيانات بالصيغة التالية:
`نسبة_الربح نسبة_الإغلاق`

**أمثلة:**
• `3 50` → هدف عند +3% إغلاق 50%
• `5.5 30` → هدف عند +5.5% إغلاق 30%
• `10 100` → هدف عند +10% إغلاق كامل

**نصيحة:** يمكنك إدخال عدة أهداف، كل واحد في رسالة منفصلة
        """
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"setTP_menu_{position_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في custom TP input: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def custom_sl_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال Stop Loss مخصص"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("customSL_", "")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_id:
            user_input_state[user_id] = f"waiting_custom_sl_{position_id}"
        
        message = """
🛑 **إدخال Stop Loss مخصص**

أدخل نسبة الخسارة المقبولة كرقم:

**أمثلة:**
• `2` → SL عند -2%
• `3.5` → SL عند -3.5%
• `1` → SL عند -1% (محافظ)
• `5` → SL عند -5% (عدواني)

⚠️ **تحذير:** نسبة أقل = حماية أفضل، لكن احتمالية خروج مبكر أعلى
        """
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"setSL_menu_{position_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في custom SL input: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def custom_trailing_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إدخال مسافة Trailing Stop مخصصة"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("customTrailing_", "")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_id:
            user_input_state[user_id] = f"waiting_custom_trailing_{position_id}"
        
        message = """
⚡ **إدخال مسافة Trailing Stop مخصصة**

أدخل المسافة كنسبة مئوية:

**أمثلة:**
• `1.5` → مسافة 1.5%
• `2` → مسافة 2% (موصى به)
• `3` → مسافة 3%

💡 **ملاحظة:**
- مسافة أصغر = حماية أسرع للأرباح
- مسافة أكبر = حرية أكثر للسعر
- الافتراضي: 2%

⚠️ **تحذير:** سيُلغي Stop Loss الثابت
        """
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"trailing_menu_{position_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في custom trailing input: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def clear_take_profits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف جميع أهداف الربح"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("clearTP_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos:
            await query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
        managed_pos.take_profits.clear()
        
        await query.edit_message_text(
            "✅ تم حذف جميع أهداف الربح",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data=f"setTP_menu_{position_id}")
            ]])
        )
        
    except Exception as e:
        logger.error(f"خطأ في حذف TP: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def clear_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف Stop Loss"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("clearSL_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos:
            await query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
        managed_pos.stop_loss = None
        
        await query.edit_message_text(
            "✅ تم حذف Stop Loss\n\n⚠️ تحذير: الصفقة الآن بدون حماية!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data=f"setSL_menu_{position_id}")
            ]])
        )
        
    except Exception as e:
        logger.error(f"خطأ في حذف SL: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def stop_trailing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف Trailing Stop"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("stopTrailing_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos or not managed_pos.stop_loss:
            await query.edit_message_text("❌ لا يوجد Stop Loss نشط")
            return
        
        if not managed_pos.stop_loss.is_trailing:
            await query.edit_message_text("ℹ️ Trailing Stop غير مفعل")
            return
        
        # تحويله إلى SL ثابت
        managed_pos.stop_loss.is_trailing = False
        managed_pos.stop_loss.trailing_distance = 0
        
        await query.edit_message_text(
            f"✅ تم تعطيل Trailing Stop\n\n"
            f"🛑 Stop Loss الحالي ثابت عند: {managed_pos.stop_loss.price:.6f}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data=f"trailing_menu_{position_id}")
            ]])
        )
        
    except Exception as e:
        logger.error(f"خطأ في إيقاف trailing: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_auto_tp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين أهداف تلقائية ذكية"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("autoTP_", "")
        
        success = trade_tools_manager.set_default_levels(position_id, tp_percentages=[1.5, 3.0, 5.0])
        
        if success:
            await query.edit_message_text(
                "✅ تم تعيين أهداف تلقائية:\n\n"
                "🎯 TP1: 1.5% (إغلاق 50%)\n"
                "🎯 TP2: 3.0% (إغلاق 30%)\n"
                "🎯 TP3: 5.0% (إغلاق 20%)\n\n"
                "سيتم نقل Stop Loss للتعادل عند تحقيق TP1",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 عودة للإدارة", callback_data=f"manage_{position_id}")
                ]])
            )
        else:
            await query.edit_message_text("❌ فشل في تعيين الأهداف التلقائية")
            
    except Exception as e:
        logger.error(f"خطأ في تعيين الأهداف التلقائية: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def set_auto_sl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعيين ستوب لوز تلقائي بنسبة 2%"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("autoSL_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos:
            await query.edit_message_text("❌ الصفقة غير موجودة في النظام المدار")
            return
        
        # تعيين SL بنسبة 2%
        if managed_pos.side.lower() == "buy":
            sl_price = managed_pos.entry_price * 0.98  # -2%
        else:
            sl_price = managed_pos.entry_price * 1.02  # +2%
        
        success = managed_pos.set_stop_loss(sl_price, is_trailing=False)
        
        if success:
            await query.edit_message_text(
                f"✅ تم تعيين Stop Loss:\n\n"
                f"🛑 السعر: {sl_price:.6f}\n"
                f"📉 المخاطرة: 2% من رأس المال\n\n"
                f"💡 نصيحة: سيتم نقله للتعادل عند تحقيق أول هدف",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 عودة للإدارة", callback_data=f"manage_{position_id}")
                ]])
            )
        else:
            await query.edit_message_text("❌ فشل في تعيين Stop Loss")
            
    except Exception as e:
        logger.error(f"خطأ في تعيين Stop Loss التلقائي: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def partial_close_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إغلاق جزئي للصفقة"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج النسبة و position_id
        parts = query.data.split("_")
        
        # التحقق من صيغة callback_data
        if parts[1] == "custom":
            # هذا زر الإدخال المخصص، وليس للإغلاق المباشر
            return
        
        percentage = int(parts[1])
        position_id = "_".join(parts[2:])
        
        # الحصول على معرف المستخدم
        user_id = update.effective_user.id if update.effective_user else None
        
        # البحث عن الصفقة
        position_info = None
        is_user_position = False
        
        if user_id and user_id in user_manager.user_positions:
            if position_id in user_manager.user_positions[user_id]:
                position_info = user_manager.user_positions[user_id][position_id]
                is_user_position = True
        
        if not position_info:
            position_info = trading_bot.open_positions.get(position_id)
        
        if not position_info:
            await query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
        # التحقق من نوع الصفقة
        is_real = position_info.get('is_real_position', False)
        
        if is_real:
            # 🔴 صفقة حقيقية - تطبيق الإغلاق عبر API
            success, msg = await apply_tool_to_real_position(
                position_info,
                "partial_close",
                percentage=percentage
            )
            
            if success:
                await query.edit_message_text(f"✅ تم إغلاق {percentage}% من الصفقة على المنصة\n\n{msg}")
            else:
                await query.edit_message_text(f"❌ فشل الإغلاق الجزئي\n\n{msg}")
            return
        
        # 🟢 صفقة تجريبية - الإغلاق داخل البوت
        # الحصول على الحساب المناسب
        market_type = position_info.get('account_type', 'spot')
        if is_user_position and user_id:
            account = user_manager.get_user_account(user_id, market_type)
        else:
            account = trading_bot.demo_account_futures if market_type == 'futures' else trading_bot.demo_account_spot
        
        # حساب كمية الإغلاق
        current_price = position_info.get('current_price', position_info['entry_price'])
        original_amount = position_info.get('amount', position_info.get('margin_amount', 0))
        close_amount = original_amount * (percentage / 100)
        
        # حساب الربح/الخسارة
        entry_price = position_info['entry_price']
        side = position_info['side']
        
        if side.lower() == "buy":
            pnl = (current_price - entry_price) * (close_amount / entry_price)
        else:
            pnl = (entry_price - current_price) * (close_amount / entry_price)
        
        # تحديث الصفقة
        position_info['amount'] = original_amount - close_amount
        
        # تحديث الرصيد
        if market_type == 'spot':
            account.balance += close_amount + pnl
        else:  # futures
            account.balance += pnl
            account.margin_locked -= close_amount
        
        pnl_emoji = "🟢💰" if pnl >= 0 else "🔴💸"
        message = f"""
{pnl_emoji} تم إغلاق {percentage}% من الصفقة (تجريبي)

📊 الرمز: {position_info['symbol']}
🔄 النوع: {side.upper()}
💲 سعر الإغلاق: {current_price:.6f}
💰 المبلغ المغلق: {close_amount:.2f}
{pnl_emoji} الربح/الخسارة: {pnl:+.2f}

📈 المتبقي: {position_info['amount']:.2f} ({100-percentage}%)
💰 الرصيد الجديد: {account.balance:.2f}
        """
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع للإدارة", callback_data=f"manage_{position_id}"),
                InlineKeyboardButton("📊 الصفقات المفتوحة", callback_data="show_positions")
            ]])
        )
        
    except Exception as e:
        logger.error(f"خطأ في الإغلاق الجزئي: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def move_sl_to_breakeven(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نقل Stop Loss إلى نقطة التعادل"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("moveBE_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos or not managed_pos.stop_loss:
            await query.edit_message_text("❌ لا يوجد Stop Loss مُعيّن لهذه الصفقة")
            return
        
        if managed_pos.stop_loss.moved_to_breakeven:
            await query.edit_message_text("ℹ️ Stop Loss منقول للتعادل بالفعل")
            return
        
        success = managed_pos.stop_loss.move_to_breakeven(managed_pos.entry_price)
        
        if success:
            await query.edit_message_text(
                f"✅ تم نقل Stop Loss إلى التعادل!\n\n"
                f"🔒 السعر الجديد: {managed_pos.entry_price:.6f}\n"
                f"✨ الآن الصفقة محمية من الخسارة",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 عودة للإدارة", callback_data=f"manage_{position_id}")
                ]])
            )
        else:
            await query.edit_message_text("❌ فشل في نقل Stop Loss")
            
    except Exception as e:
        logger.error(f"خطأ في نقل SL للتعادل: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def enable_trailing_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل Trailing Stop"""
    try:
        query = update.callback_query
        await query.answer()
        
        position_id = query.data.replace("trailing_", "")
        managed_pos = trade_tools_manager.get_managed_position(position_id)
        
        if not managed_pos:
            await query.edit_message_text("❌ الصفقة غير موجودة في النظام المدار")
            return
        
        # تعيين trailing stop بمسافة 2%
        if not managed_pos.stop_loss:
            if managed_pos.side.lower() == "buy":
                sl_price = managed_pos.entry_price * 0.98
            else:
                sl_price = managed_pos.entry_price * 1.02
            
            managed_pos.set_stop_loss(sl_price, is_trailing=True, trailing_distance=2.0)
        else:
            managed_pos.stop_loss.is_trailing = True
            managed_pos.stop_loss.trailing_distance = 2.0
        
        await query.edit_message_text(
            f"✅ تم تفعيل Trailing Stop!\n\n"
            f"⚡ المسافة: 2%\n"
            f"🔒 السعر الحالي: {managed_pos.stop_loss.price:.6f}\n\n"
            f"💡 سيتحرك Stop Loss تلقائياً مع تحرك السعر لصالحك",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 عودة للإدارة", callback_data=f"manage_{position_id}")
            ]])
        )
            
    except Exception as e:
        logger.error(f"خطأ في تفعيل Trailing Stop: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text(f"❌ خطأ: {e}")

async def close_position(position_id: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إغلاق صفقة مع دعم محسن للفيوتشر"""
    try:
        # الحصول على معرف المستخدم
        user_id = update.effective_user.id if update.effective_user else None
        
        # البحث عن الصفقة في صفقات المستخدم أو الصفقات العامة
        position_info = None
        is_user_position = False
        
        if user_id and user_id in user_manager.user_positions:
            if position_id in user_manager.user_positions[user_id]:
                position_info = user_manager.user_positions[user_id][position_id]
                is_user_position = True
                logger.info(f"تم العثور على الصفقة {position_id} في صفقات المستخدم {user_id}")
        
        if not position_info and position_id in trading_bot.open_positions:
            position_info = trading_bot.open_positions[position_id]
            logger.info(f"تم العثور على الصفقة {position_id} في الصفقات العامة")
        
        if not position_info:
            if update.callback_query is not None:
                await update.callback_query.edit_message_text("❌ الصفقة غير موجودة")
            return
        
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
            # تحديد الحساب الصحيح - استخدام حساب المستخدم إذا كانت صفقة مستخدم
            if is_user_position and user_id:
                account = user_manager.get_user_account(user_id, market_type)
            else:
                if market_type == 'spot':
                    account = trading_bot.demo_account_spot
                else:
                    account = trading_bot.demo_account_futures
            
            # إغلاق الصفقة
            if market_type == 'spot':
                success, result = account.close_spot_position(position_id, current_price)
            else:
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
                
                # حذف الصفقة من القائمة المناسبة
                if is_user_position and user_id and user_id in user_manager.user_positions:
                    if position_id in user_manager.user_positions[user_id]:
                        del user_manager.user_positions[user_id][position_id]
                        logger.info(f"تم حذف الصفقة {position_id} من صفقات المستخدم {user_id}")
                
                if position_id in trading_bot.open_positions:
                    del trading_bot.open_positions[position_id]
                    logger.info(f"تم حذف الصفقة {position_id} من الصفقات العامة")
                
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
        user_id = update.effective_user.id
        user_data = user_manager.get_user(user_id)
        
        account_type = user_data.get('account_type', 'demo') if user_data else 'demo'
        exchange = user_data.get('exchange', 'bybit') if user_data else 'bybit'
        market_type = user_data.get('market_type', 'spot') if user_data else 'spot'
        
        all_history = []
        
        # إذا كان حساب حقيقي، جلب التاريخ من المنصة
        if account_type == 'real':
            from real_account_manager import real_account_manager
            
            real_account = real_account_manager.get_account(user_id)
            
            if real_account and hasattr(real_account, 'get_order_history'):
                try:
                    category = 'linear' if market_type == 'futures' else 'spot'
                    orders = real_account.get_order_history(category, limit=20)
                    
                    # تحويل الأوامر إلى صيغة التاريخ
                    for order in orders:
                        if order.get('status') in ['Filled', 'PartiallyFilled']:
                            all_history.append({
                                'symbol': order.get('symbol'),
                                'side': order.get('side'),
                                'entry_price': order.get('avg_price', order.get('price', 0)),
                                'closing_price': order.get('avg_price', order.get('price', 0)),
                                'pnl': 0,  # يحتاج حساب من الصفقات المغلقة
                                'market_type': market_type,
                                'timestamp': datetime.fromtimestamp(int(order.get('created_time', 0)) / 1000) if order.get('created_time') else datetime.now(),
                                'position_size': order.get('qty', 0),
                                'is_real': True
                            })
                    
                    logger.info(f"✅ تم جلب {len(all_history)} أمر من {exchange}")
                except Exception as e:
                    logger.error(f"❌ خطأ في جلب تاريخ الأوامر: {e}")
        else:
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
    """عرض نظرة عامة ذكية على المحفظة مع دعم متعدد المنصات"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ لم يتم العثور على بيانات المستخدم")
        return
    
    try:
        # التحقق من نوع الحساب
        account_type = user_data.get('account_type', 'demo')
        market_type = user_data.get('market_type', 'spot')
        
        wallet_message = "💰 **المحفظة الذكية**\n\n"
        
        if account_type == 'demo':
            # عرض الحساب التجريبي
            wallet_message += "🟢 **الحساب التجريبي**\n"
            
            # الحصول على بيانات الحسابات التجريبية
            spot_account = trading_bot.demo_account_spot
            futures_account = trading_bot.demo_account_futures
            
            spot_info = spot_account.get_account_info()
            futures_info = futures_account.get_account_info()
            
            # حساب الإجماليات
            total_balance = spot_info['balance'] + futures_info['balance']
            total_available = spot_info.get('available_balance', spot_info['balance']) + futures_info.get('available_balance', futures_info['balance'])
            total_margin_locked = spot_info.get('margin_locked', 0) + futures_info.get('margin_locked', 0)
            total_equity = spot_info.get('equity', spot_info['balance']) + futures_info.get('equity', futures_info['balance'])
            total_pnl = spot_info['unrealized_pnl'] + futures_info['unrealized_pnl']
            total_open_positions = spot_info['open_positions'] + futures_info['open_positions']
            
            # حساب إحصائيات التداول
            total_trades = spot_info['total_trades'] + futures_info['total_trades']
            total_winning_trades = spot_info['winning_trades'] + futures_info['winning_trades']
            total_losing_trades = spot_info['losing_trades'] + futures_info['losing_trades']
            total_win_rate = round((total_winning_trades / max(total_trades, 1)) * 100, 2)
            
            # تحديد حالة PnL
            if total_pnl > 0:
                total_pnl_arrow = "📈"
                total_pnl_status = "ربح"
            elif total_pnl < 0:
                total_pnl_arrow = "📉"
                total_pnl_status = "خسارة"
            else:
                total_pnl_arrow = "➖"
                total_pnl_status = "متعادل"
            
            wallet_message += f"""
📊 **الرصيد التجريبي:**
💳 الرصيد الكلي: {total_balance:.2f} USDT
💳 الرصيد المتاح: {total_available:.2f} USDT
🔒 الهامش المحجوز: {total_margin_locked:.2f} USDT
💼 القيمة الصافية: {total_equity:.2f} USDT
{total_pnl_arrow} إجمالي PnL: {total_pnl:.2f} USDT - {total_pnl_status}

📈 **إحصائيات التداول:**
🔄 الصفقات المفتوحة: {total_open_positions}
📊 إجمالي الصفقات: {total_trades}
✅ الصفقات الرابحة: {total_winning_trades}
❌ الصفقات الخاسرة: {total_losing_trades}
🎯 معدل النجاح: {total_win_rate}%

🏪 **تفاصيل الحسابات:**
• السبوت: {spot_info['balance']:.2f} USDT
• الفيوتشر: {futures_info['balance']:.2f} USDT
            """
            
        else:
            # عرض الحساب الحقيقي
            wallet_message += "🔴 **الحساب الحقيقي**\n"
            
            # التحقق من المنصات المرتبطة
            bybit_connected = user_data.get('bybit_api_connected', False)
            mexc_connected = user_data.get('mexc_api_connected', False)
            
            total_real_balance = 0
            total_real_available = 0
            total_real_pnl = 0
            total_real_positions = 0
            
            if bybit_connected:
                try:
                    # الحصول على بيانات Bybit
                    bybit_account = user_manager.get_user_account(user_id, 'bybit')
                    if bybit_account:
                        bybit_info = bybit_account.get_account_info()
                        total_real_balance += bybit_info.get('balance', 0)
                        total_real_available += bybit_info.get('available_balance', 0)
                        total_real_pnl += bybit_info.get('unrealized_pnl', 0)
                        total_real_positions += bybit_info.get('open_positions', 0)
                        
                        wallet_message += f"""
🏦 **Bybit:**
💳 الرصيد: {bybit_info.get('balance', 0):.2f} USDT
💳 المتاح: {bybit_info.get('available_balance', 0):.2f} USDT
📈 PnL: {bybit_info.get('unrealized_pnl', 0):.2f} USDT
🔄 الصفقات: {bybit_info.get('open_positions', 0)}
                        """
                except Exception as e:
                    logger.error(f"خطأ في جلب بيانات Bybit: {e}")
                    wallet_message += "\n🏦 **Bybit:** ❌ خطأ في الاتصال\n"
            
            if mexc_connected:
                try:
                    # الحصول على بيانات MEXC
                    mexc_account = user_manager.get_user_account(user_id, 'mexc')
                    if mexc_account:
                        mexc_info = mexc_account.get_account_info()
                        total_real_balance += mexc_info.get('balance', 0)
                        total_real_available += mexc_info.get('available_balance', 0)
                        total_real_pnl += mexc_info.get('unrealized_pnl', 0)
                        total_real_positions += mexc_info.get('open_positions', 0)
                        
                        wallet_message += f"""
🏦 **MEXC:**
💳 الرصيد: {mexc_info.get('balance', 0):.2f} USDT
💳 المتاح: {mexc_info.get('available_balance', 0):.2f} USDT
📈 PnL: {mexc_info.get('unrealized_pnl', 0):.2f} USDT
🔄 الصفقات: {mexc_info.get('open_positions', 0)}
                        """
                except Exception as e:
                    logger.error(f"خطأ في جلب بيانات MEXC: {e}")
                    wallet_message += "\n🏦 **MEXC:** ❌ خطأ في الاتصال\n"
            
            if not bybit_connected and not mexc_connected:
                wallet_message += "\n⚠️ **لا توجد منصات مرتبطة**\n"
                wallet_message += "اذهب إلى الإعدادات لربط حسابك الحقيقي\n"
            else:
                # عرض الإجمالي
                if total_real_pnl > 0:
                    total_pnl_arrow = "📈"
                    total_pnl_status = "ربح"
                elif total_real_pnl < 0:
                    total_pnl_arrow = "📉"
                    total_pnl_status = "خسارة"
                else:
                    total_pnl_arrow = "➖"
                    total_pnl_status = "متعادل"
                
                wallet_message += f"""
📊 **الإجمالي:**
💳 الرصيد الكلي: {total_real_balance:.2f} USDT
💳 الرصيد المتاح: {total_real_available:.2f} USDT
{total_pnl_arrow} إجمالي PnL: {total_real_pnl:.2f} USDT - {total_pnl_status}
🔄 الصفقات المفتوحة: {total_real_positions}
                """
        
        # إضافة معلومات إضافية
        wallet_message += f"""

⚙️ **إعدادات التداول:**
🏪 نوع السوق: {market_type.upper()}
💰 مبلغ التداول: {trading_bot.user_settings['trade_amount']} USDT
🔢 الرافعة المالية: {trading_bot.user_settings['leverage']}x
🎯 Stop Loss: {trading_bot.user_settings.get('stop_loss', 'غير محدد')}%
🎯 Take Profit: {trading_bot.user_settings.get('take_profit', 'غير محدد')}%

📅 **معلومات الحساب:**
👤 نوع الحساب: {account_type.upper()}
🔗 حالة API: {'🟢 مرتبط' if user_data.get('api_connected', False) else '🔴 غير مرتبط'}
📡 آخر إشارة: {user_data.get('last_signal_time', 'لم يتم استقبال إشارات')}
        """
        
        await update.message.reply_text(wallet_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض المحفظة: {e}")
        await update.message.reply_text("❌ خطأ في عرض معلومات المحفظة")

async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض تحليل الأداء والربحية المتقدم"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ لم يتم العثور على بيانات المستخدم")
        return
    
    try:
        # الحصول على معلومات الحساب التجريبي
        spot_account = trading_bot.demo_account_spot
        futures_account = trading_bot.demo_account_futures
        
        spot_info = spot_account.get_account_info()
        futures_info = futures_account.get_account_info()
        
        # حساب الإجماليات
        total_balance = spot_info['balance'] + futures_info['balance']
        total_available = spot_info.get('available_balance', spot_info['balance']) + futures_info.get('available_balance', futures_info['balance'])
        total_margin_locked = spot_info.get('margin_locked', 0) + futures_info.get('margin_locked', 0)
        total_equity = spot_info.get('equity', spot_info['balance']) + futures_info.get('equity', futures_info['balance'])
        total_pnl = spot_info['unrealized_pnl'] + futures_info['unrealized_pnl']
        total_open_positions = spot_info['open_positions'] + futures_info['open_positions']
        
        # حساب إحصائيات التداول
        total_trades = spot_info['total_trades'] + futures_info['total_trades']
        total_winning_trades = spot_info['winning_trades'] + futures_info['winning_trades']
        total_losing_trades = spot_info['losing_trades'] + futures_info['losing_trades']
        total_win_rate = round((total_winning_trades / max(total_trades, 1)) * 100, 2)
        
        # حساب إحصائيات إضافية
        profit_loss_ratio = 0
        if total_losing_trades > 0:
            profit_loss_ratio = total_winning_trades / total_losing_trades
        
        # حساب متوسط الربح/الخسارة
        avg_profit = 0
        avg_loss = 0
        if total_winning_trades > 0:
            avg_profit = total_pnl / total_winning_trades
        if total_losing_trades > 0:
            avg_loss = abs(total_pnl) / total_losing_trades
        
        # حساب مؤشرات الأداء المتقدمة
        sharpe_ratio = 0
        if total_trades > 0:
            sharpe_ratio = (total_win_rate - 50) / max(total_trades, 1)
        
        # تحديد مستوى الأداء
        if total_win_rate >= 70:
            performance_level = "🏆 ممتاز"
            performance_color = "🟢"
        elif total_win_rate >= 60:
            performance_level = "🥇 جيد جداً"
            performance_color = "🟡"
        elif total_win_rate >= 50:
            performance_level = "🥈 متوسط"
            performance_color = "🟠"
        else:
            performance_level = "🥉 يحتاج تحسين"
            performance_color = "🔴"
        
        # بناء رسالة التحليل
        analysis_message = f"""
📊 **تحليل الأداء والربحية**

{performance_color} **مستوى الأداء:** {performance_level}
🎯 معدل النجاح: {total_win_rate:.1f}%

📈 **إحصائيات الأداء:**
🔄 الصفقات المفتوحة: {total_open_positions}
📊 إجمالي الصفقات: {total_trades}
✅ الصفقات الرابحة: {total_winning_trades}
❌ الصفقات الخاسرة: {total_losing_trades}

📊 **تحليل الربحية:**
📈 متوسط الربح: {avg_profit:.2f} USDT
📉 متوسط الخسارة: {avg_loss:.2f} USDT
⚖️ نسبة الربح/الخسارة: {profit_loss_ratio:.2f}
📊 مؤشر شارب: {sharpe_ratio:.2f}

💰 **الرصيد الحالي:**
💳 الرصيد الكلي: {total_balance:.2f} USDT
💳 الرصيد المتاح: {total_available:.2f} USDT
🔒 الهامش المحجوز: {total_margin_locked:.2f} USDT
💼 القيمة الصافية: {total_equity:.2f} USDT

📊 **تحليل السوق:**
🏪 السبوت: {spot_info['balance']:.2f} USDT
🏪 الفيوتشر: {futures_info['balance']:.2f} USDT
📈 PnL السبوت: {spot_info['unrealized_pnl']:.2f} USDT
📈 PnL الفيوتشر: {futures_info['unrealized_pnl']:.2f} USDT

🎯 **التوصيات:**
{_get_trading_recommendations(total_win_rate, total_trades, profit_loss_ratio)}
        """
        
        await update.message.reply_text(analysis_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض تحليل الأداء: {e}")
        await update.message.reply_text("❌ خطأ في عرض تحليل الأداء")

def _get_trading_recommendations(win_rate, total_trades, profit_loss_ratio):
    """الحصول على توصيات التداول"""
    recommendations = []
    
    if total_trades < 10:
        recommendations.append("📊 تحتاج المزيد من الصفقات لتقييم دقيق")
    elif win_rate < 40:
        recommendations.append("⚠️ معدل النجاح منخفض - راجع استراتيجيتك")
    elif win_rate > 70:
        recommendations.append("🎉 أداء ممتاز - استمر في استراتيجيتك")
    
    if profit_loss_ratio < 1:
        recommendations.append("⚖️ نسبة الربح/الخسارة منخفضة - حسّن إدارة المخاطر")
    elif profit_loss_ratio > 2:
        recommendations.append("💎 نسبة ممتازة - استراتيجية فعالة")
    
    if not recommendations:
        recommendations.append("📈 أداء متوازن - استمر في التطوير")
    
    return "\n".join(recommendations)

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
    
    logger.info(f"📥 Callback received: {data} from user {user_id}")
    
    # معالجة زر اختيار المنصة
    if data == "select_exchange":
        from exchange_commands import cmd_select_exchange
        await cmd_select_exchange(update, context)
        return
    
    # معالجة أزرار اختيار المنصات
    if data == "exchange_select_bybit":
        from exchange_commands import show_bybit_options
        await show_bybit_options(update, context)
        return
    
    if data == "exchange_select_mexc":
        from exchange_commands import show_mexc_options
        await show_mexc_options(update, context)
        return
    
    if data == "exchange_setup_bybit":
        from exchange_commands import start_bybit_setup
        await start_bybit_setup(update, context)
        return
    
    if data == "exchange_setup_mexc":
        from exchange_commands import start_mexc_setup
        await start_mexc_setup(update, context)
        return
    
    if data == "exchange_activate_bybit" or data == "exchange_activate_mexc":
        from exchange_commands import activate_exchange
        await activate_exchange(update, context)
        return
    
    if data == "exchange_test_bybit" or data == "exchange_test_mexc":
        from exchange_commands import test_exchange_connection
        await test_exchange_connection(update, context)
        return
    
    if data == "exchange_menu":
        from exchange_commands import cmd_select_exchange
        await cmd_select_exchange(update, context)
        return
    
    # معالجة أزرار إدارة الصفقات (TP/SL/Close)
    if data.startswith("set_tp_") or data.startswith("set_sl_") or data.startswith("set_tpsl_"):
        from position_manager import position_manager
        symbol = data.split("_", 2)[2]
        
        if data.startswith("set_tp_"):
            await position_manager.set_take_profit(update, context, symbol)
        elif data.startswith("set_sl_"):
            await position_manager.set_stop_loss(update, context, symbol)
        return
    
    if data.startswith("close_position_"):
        from position_manager import position_manager
        symbol = data.replace("close_position_", "")
        user_id = update.effective_user.id
        
        # تأكيد الإغلاق
        keyboard = [
            [InlineKeyboardButton("✅ نعم، أغلق الصفقة", callback_data=f"confirm_close_{symbol}")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="open_positions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚠️ **تأكيد إغلاق الصفقة**\n\n"
            f"هل أنت متأكد من إغلاق صفقة {symbol}؟\n\n"
            f"سيتم تنفيذ الإغلاق على المنصة الحقيقية!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    if data.startswith("confirm_close_"):
        from position_manager import position_manager
        symbol = data.replace("confirm_close_", "")
        user_id = update.effective_user.id
        
        await query.answer("جاري الإغلاق...")
        
        result = await position_manager.close_position(user_id, symbol)
        
        if result:
            await query.edit_message_text(
                f"✅ **تم إغلاق الصفقة بنجاح!**\n\n"
                f"💎 الرمز: {symbol}\n"
                f"⚡ تم التنفيذ على المنصة الحقيقية",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ **فشل إغلاق الصفقة**\n\n"
                f"حاول مرة أخرى أو تحقق من الاتصال",
                parse_mode='Markdown'
            )
        return
    
    # معالجة زر الربط API
    if data == "link_api":
        if user_id is not None:
            user_input_state[user_id] = "waiting_for_api_key"
        if update.callback_query is not None:
            await update.callback_query.edit_message_text("""
🔗 ربط API - الخطوة 1 من 2

📝 أرسل API_KEY الخاص بك من Bybit

⚠️ تأكد من:
• عدم مشاركة المفاتيح مع أي شخص
• إنشاء مفاتيح API محدودة الصلاحيات
• تفعيل صلاحيات القراءة والكتابة والتداول

📌 للحصول على المفاتيح:
1. افتح https://www.bybit.com
2. اذهب إلى Account & Security
3. API Management
4. Create New Key
5. فعّل صلاحيات: Read, Write, Trade

🔐 المفاتيح ستُحفظ بشكل آمن ومشفر
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
    elif data == "refresh_positions" or data == "show_positions":
        await open_positions(update, context)
    elif data == "webhook_help":
        await show_webhook_help(update, context)
    elif data == "back_to_main":
        await start(update, context)
    elif data == "auto_apply_menu":
        await auto_apply_settings_menu(update, context)
    elif data == "risk_management_menu":
        await risk_management_menu(update, context)
    elif data == "toggle_risk_management":
        await toggle_risk_management(update, context)
    elif data == "set_max_loss_percent":
        await set_max_loss_percent(update, context)
    elif data == "set_max_loss_amount":
        await set_max_loss_amount(update, context)
    elif data == "set_daily_loss_limit":
        await set_daily_loss_limit(update, context)
    elif data == "set_weekly_loss_limit":
        await set_weekly_loss_limit(update, context)
    elif data == "toggle_stop_trading":
        await toggle_stop_trading_on_loss(update, context)
    elif data == "show_risk_stats":
        await show_risk_statistics(update, context)
    elif data == "reset_risk_stats":
        await reset_risk_statistics(update, context)
    elif data == "risk_management_guide":
        await risk_management_guide(update, context)
    elif data == "toggle_auto_apply":
        await toggle_auto_apply(update, context)
    elif data == "quick_auto_setup":
        await quick_auto_setup(update, context)
    elif data == "edit_auto_settings":
        logger.info(f"🔧 معالجة زر: edit_auto_settings")
        await edit_auto_settings(update, context)
    elif data == "edit_auto_tp":
        logger.info(f"🔧 معالجة زر: edit_auto_tp")
        await edit_auto_tp(update, context)
    elif data == "edit_auto_sl":
        logger.info(f"🔧 معالجة زر: edit_auto_sl")
        await edit_auto_sl(update, context)
    elif data == "toggle_auto_trailing":
        logger.info(f"🔧 معالجة زر: toggle_auto_trailing")
        await toggle_auto_trailing(update, context)
    elif data == "clear_auto_settings":
        logger.info(f"🔧 معالجة زر: clear_auto_settings")
        await clear_auto_settings(update, context)
    elif data.startswith("auto_tp_targets_"):
        await set_auto_tp_targets_count(update, context)
    elif data.startswith("quick_tp_"):
        tp_value = float(query.data.replace("quick_tp_", ""))
        if 'auto_tp_builder' not in context.user_data:
            context.user_data['auto_tp_builder'] = {}
        context.user_data['auto_tp_builder']['temp_tp_percent'] = tp_value
        await process_tp_target_input(update, context, tp_value)
    elif data.startswith("quick_close_"):
        close_value = float(query.data.replace("quick_close_", ""))
        await finalize_tp_target(update, context, close_value)
    elif data.startswith("quick_sl_"):
        sl_value = float(query.data.replace("quick_sl_", ""))
        success = trade_tools_manager.save_auto_settings(
            tp_percentages=trade_tools_manager.default_tp_percentages,
            tp_close_percentages=trade_tools_manager.default_tp_close_percentages,
            sl_percentage=sl_value,
            trailing_enabled=trade_tools_manager.default_trailing_enabled,
            trailing_distance=trade_tools_manager.default_trailing_distance,
            breakeven_on_tp1=True
        )
        if success:
            await query.edit_message_text(
                f"✅ **تم حفظ Stop Loss!**\n\n🛑 النسبة: -{sl_value}%",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")]]),
                parse_mode='Markdown'
            )
    elif data == "custom_sl_input":
        user_id = update.effective_user.id if update.effective_user else None
        if user_id:
            user_input_state[user_id] = "waiting_auto_sl_input"
        await query.edit_message_text(
            "🛑 **إدخال Stop Loss مخصص**\n\nأدخل النسبة كرقم (مثال: 2.5):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="edit_auto_sl")]]),
            parse_mode='Markdown'
        )
    elif data == "custom_tp_percent_input":
        user_id = update.effective_user.id if update.effective_user else None
        builder = context.user_data.get('auto_tp_builder', {})
        current_target = builder.get('current_target', 1)
        total_count = builder.get('count', 3)
        
        if user_id:
            user_input_state[user_id] = f"building_auto_tp_target_{current_target}_percent"
        
        await query.edit_message_text(
            f"🎯 **هدف الربح رقم {current_target} من {total_count}**\n\n"
            f"✏️ **إدخال مخصص**\n\n"
            f"أدخل نسبة الربح كرقم:\n\n"
            f"**أمثلة:**\n"
            f"• `2.5` → هدف عند +2.5%\n"
            f"• `7` → هدف عند +7%\n"
            f"• `15.5` → هدف عند +15.5%\n\n"
            f"📊 **النطاق:** 0.1% إلى 100%",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_tp")]]),
            parse_mode='Markdown'
        )
    elif data == "custom_close_percent_input":
        user_id = update.effective_user.id if update.effective_user else None
        builder = context.user_data.get('auto_tp_builder', {})
        current_target = builder.get('current_target', 1)
        total_count = builder.get('count', 3)
        tp_pct = builder.get('temp_tp_percent', 0)
        
        if user_id:
            user_input_state[user_id] = f"building_auto_tp_target_{current_target}_close"
        
        await query.edit_message_text(
            f"🎯 **هدف الربح رقم {current_target} من {total_count}**\n\n"
            f"✅ **نسبة الربح:** +{tp_pct}%\n\n"
            f"✏️ **إدخال مخصص**\n\n"
            f"أدخل نسبة الإغلاق كرقم:\n\n"
            f"**أمثلة:**\n"
            f"• `40` → إغلاق 40%\n"
            f"• `60` → إغلاق 60%\n"
            f"• `85.5` → إغلاق 85.5%\n\n"
            f"📊 **النطاق:** 1% إلى 100%",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_tp")]]),
            parse_mode='Markdown'
        )
    elif data.startswith("manage_"):
        await manage_position_tools(update, context)
    elif data.startswith("tools_guide_"):
        await show_tools_guide(update, context)
    elif data.startswith("setTP_menu_"):
        await set_tp_menu(update, context)
    elif data.startswith("setSL_menu_"):
        await set_sl_menu(update, context)
    elif data.startswith("trailing_menu_"):
        await trailing_stop_menu(update, context)
    elif data.startswith("partial_custom_"):
        await custom_partial_close(update, context)
    elif data.startswith("quick_setup_"):
        await quick_setup(update, context)
    elif data.startswith("customTP_"):
        await custom_tp_input(update, context)
    elif data.startswith("customSL_"):
        await custom_sl_input(update, context)
    elif data.startswith("customTrailing_"):
        await custom_trailing_input(update, context)
    elif data.startswith("clearTP_"):
        await clear_take_profits(update, context)
    elif data.startswith("clearSL_"):
        await clear_stop_loss(update, context)
    elif data.startswith("stopTrailing_"):
        await stop_trailing(update, context)
    elif data.startswith("autoTP_"):
        await set_auto_tp(update, context)
    elif data.startswith("autoSL_"):
        await set_auto_sl(update, context)
    elif data.startswith("partial_"):
        await partial_close_position(update, context)
    elif data.startswith("moveBE_"):
        await move_sl_to_breakeven(update, context)
    elif data.startswith("trailing_") and not data.startswith("trailing_menu_"):
        await enable_trailing_stop(update, context)
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
        # حفظ الإعدادات في قاعدة البيانات
        if user_id is not None:
            db_manager.update_user_settings(user_id, {'market_type': 'spot'})
            # تحديث في user_manager
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['market_type'] = 'spot'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "market_futures":
        trading_bot.user_settings['market_type'] = 'futures'
        # حفظ الإعدادات في قاعدة البيانات
        if user_id is not None:
            db_manager.update_user_settings(user_id, {'market_type': 'futures'})
            # تحديث في user_manager
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['market_type'] = 'futures'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "account_real":
        trading_bot.user_settings['account_type'] = 'real'
        # حفظ الإعدادات في قاعدة البيانات
        if user_id is not None:
            db_manager.update_user_settings(user_id, {'account_type': 'real'})
            # تحديث في user_manager
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['account_type'] = 'real'
        # إعادة تعيين حالة إدخال المستخدم
        if user_id is not None and user_id in user_input_state:
            del user_input_state[user_id]
        await settings_menu(update, context)
    elif data == "account_demo":
        trading_bot.user_settings['account_type'] = 'demo'
        # حفظ الإعدادات في قاعدة البيانات
        if user_id is not None:
            db_manager.update_user_settings(user_id, {'account_type': 'demo'})
            # تحديث في user_manager
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['account_type'] = 'demo'
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

📋 كيفية الاستخدام في TradingView:

1️⃣ افتح استراتيجيتك في TradingView
2️⃣ اذهب إلى Settings → Notifications
3️⃣ أضف Webhook URL
4️⃣ الصق رابطك الشخصي
5️⃣ في Message، استخدم الصيغة التالية:

📌 الصيغة المطلوبة (مثال):
```
{{
    "symbol": "BTCUSDT",
    "action": "buy"
}}
```

💡 الإجراءات المدعومة:
• `buy` - شراء
• `sell` - بيع  
• `close` - إغلاق الصفقة

💡 نصائح:
• استخدم رابطك الشخصي للحصول على تجربة أفضل
• يمكنك نسخ الرابط بالضغط عليه
• الرابط يعمل مع TradingView و أي منصة إشارات أخرى

🔐 الأمان:
• لا تشارك رابطك الشخصي مع أحد
• يمكن تعطيل حسابك من الإعدادات إذا لزم الأمر في قسم روابط الاستخدام
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
    elif data == "dev_action_buy" or data == "dev_action_sell":
        # الخطوة 2: حفظ الاتجاه
        action = "buy" if data == "dev_action_buy" else "sell"
        context.user_data['dev_signal_data']['action'] = action
        
        # الانتقال للخطوة 3
        if user_id:
            user_input_state[user_id] = "dev_guided_step3_amount"
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
                f"✅ الاتجاه: {action.upper()}\n\n"
                f"📝 الخطوة 3 من 5\n\n"
                f"💰 أدخل المبلغ (بالدولار):\n"
                f"مثال: 100"
            )
    elif data == "dev_market_spot" or data == "dev_market_futures":
        # الخطوة 4: حفظ نوع السوق
        market_type = "spot" if data == "dev_market_spot" else "futures"
        context.user_data['dev_signal_data']['market_type'] = market_type
        
        if market_type == "futures":
            # إذا كان فيوتشر، اطلب الرافعة
            if user_id:
                user_input_state[user_id] = "dev_guided_step5_leverage"
            
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    f"✅ نوع السوق: {market_type.upper()}\n\n"
                    f"📝 الخطوة 5 من 5\n\n"
                    f"⚡ أدخل الرافعة المالية (1-100):\n"
                    f"مثال: 10"
                )
        else:
            # إذا كان سبوت، عرض الملخص مباشرة
            signal_data = context.user_data['dev_signal_data']
            signal_data['leverage'] = 1  # لا رافعة في السبوت
            
            confirm_message = f"""
✅ تم تجهيز الإشارة!

📊 الملخص:
💎 الرمز: {signal_data['symbol']}
{'🟢' if signal_data['action'] == 'buy' else '🔴'} الاتجاه: {signal_data['action'].upper()}
💰 المبلغ: {signal_data['amount']}
🏪 السوق: {signal_data['market_type'].upper()}

❓ هل تريد إرسال هذه الإشارة للمتابعين؟
"""
            
            keyboard = [
                [InlineKeyboardButton("✅ نعم، إرسال", callback_data="dev_confirm_signal")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="developer_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if user_id and user_id in user_input_state:
                del user_input_state[user_id]
            
            if update.callback_query:
                await update.callback_query.message.edit_text(confirm_message, reply_markup=reply_markup)
    elif data == "dev_confirm_signal":
        # تأكيد إرسال الإشارة
        if 'dev_signal_data' in context.user_data:
            signal_data = context.user_data['dev_signal_data']
            
            # الحصول على قائمة المتابعين قبل الإرسال
            followers = developer_manager.get_followers(user_id)
            
            if not followers:
                if update.callback_query:
                    await update.callback_query.message.edit_text(
                        "❌ لا يوجد متابعين لإرسال الإشارة إليهم\n\n"
                        "يجب أن يكون لديك متابعين نشطين أولاً."
                    )
                return
            
            # إرسال الإشارة للمتابعين مع فتح صفقات تلقائية
            try:
                # استخدام trading_bot instance
                result = await trading_bot.broadcast_signal_to_followers(signal_data, user_id)
                
                # رسالة نجاح مع تفاصيل النتيجة
                success_count = result.get('sent_to', 0) if isinstance(result, dict) else 0
                failed_count = result.get('failed', 0) if isinstance(result, dict) else 0
                
                success_message = f"""
✅ تم إرسال الإشارة بنجاح!

📊 التفاصيل:
💎 الرمز: {signal_data['symbol']}
📊 الاتجاه: {signal_data['action'].upper()}
💰 المبلغ: {signal_data['amount']}
🏪 السوق: {signal_data['market_type'].upper()}
"""
                if signal_data['market_type'] == 'futures':
                    success_message += f"⚡ الرافعة: {signal_data['leverage']}x\n"
                
                success_message += f"""
📈 النتائج:
✅ نجح: {success_count} متابع
❌ فشل: {failed_count} متابع
📊 الإجمالي: {len(followers)} متابع

💡 تم فتح الصفقات تلقائياً على حسابات المتابعين النشطين!
"""
                
                # حذف البيانات المؤقتة
                del context.user_data['dev_signal_data']
                if user_id and user_id in user_input_state:
                    del user_input_state[user_id]
                
                if update.callback_query:
                    await update.callback_query.message.edit_text(success_message)
                    
            except Exception as e:
                logger.error(f"خطأ في إرسال الإشارة: {e}")
                import traceback
                traceback.print_exc()
                
                if update.callback_query:
                    await update.callback_query.message.edit_text(
                        f"❌ حدث خطأ في إرسال الإشارة:\n\n{str(e)}\n\n"
                        "يرجى المحاولة مرة أخرى."
                    )
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
        logger.warning(f"⚠️ Unsupported button: {data}")
        if update.callback_query is not None:
            await update.callback_query.edit_message_text(f"❌ زر غير مدعوم: {data}\n\nيرجى الإبلاغ عن هذا الخطأ")

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
    
    # معالجة إدخال مفاتيح المنصات (Bybit/MEXC)
    if context.user_data.get('awaiting_exchange_keys'):
        from exchange_commands import handle_api_keys_input
        await handle_api_keys_input(update, context)
        return
    
    # معالجة إدخال TP/SL
    if context.user_data.get('awaiting_tp_price'):
        try:
            price = float(text)
            symbol = context.user_data.get('pending_tp_symbol')
            
            from position_manager import position_manager
            result = await position_manager.apply_tp_sl(user_id, symbol, take_profit=price)
            
            if result:
                await update.message.reply_text(
                    f"✅ **تم تعيين Take Profit بنجاح!**\n\n"
                    f"💎 الرمز: {symbol}\n"
                    f"🎯 السعر المستهدف: ${price:,.2f}\n"
                    f"⚡ تم التطبيق على المنصة الحقيقية",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ فشل تعيين Take Profit")
            
            # مسح الحالة
            context.user_data.pop('awaiting_tp_price', None)
            context.user_data.pop('pending_tp_symbol', None)
            return
        except ValueError:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
            return
    
    if context.user_data.get('awaiting_sl_price'):
        try:
            price = float(text)
            symbol = context.user_data.get('pending_sl_symbol')
            
            from position_manager import position_manager
            result = await position_manager.apply_tp_sl(user_id, symbol, stop_loss=price)
            
            if result:
                await update.message.reply_text(
                    f"✅ **تم تعيين Stop Loss بنجاح!**\n\n"
                    f"💎 الرمز: {symbol}\n"
                    f"🛡️ سعر وقف الخسارة: ${price:,.2f}\n"
                    f"⚡ تم التطبيق على المنصة الحقيقية",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ فشل تعيين Stop Loss")
            
            # مسح الحالة
            context.user_data.pop('awaiting_sl_price', None)
            context.user_data.pop('pending_sl_symbol', None)
            return
        except ValueError:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
            return
    
    # التحقق مما إذا كنا ننتظر إدخال المستخدم للإعدادات
    if user_id is not None and user_id in user_input_state:
        state = user_input_state[user_id]
        
        # معالجة الإدخال الموجه - الخطوة 1: الرمز
        if state == "dev_guided_step1_symbol":
            # حفظ الرمز
            symbol = text.upper().replace('/', '').replace('-', '').strip()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            if 'dev_signal_data' not in context.user_data:
                context.user_data['dev_signal_data'] = {}
            context.user_data['dev_signal_data']['symbol'] = symbol
            
            # الانتقال للخطوة 2
            user_input_state[user_id] = "dev_guided_step2_action"
            
            keyboard = [
                [InlineKeyboardButton("🟢 شراء (Buy)", callback_data="dev_action_buy")],
                [InlineKeyboardButton("🔴 بيع (Sell)", callback_data="dev_action_sell")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ الرمز: {symbol}\n\n"
                f"📝 الخطوة 2 من 5\n\n"
                f"📊 اختر الاتجاه:",
                reply_markup=reply_markup
            )
            return
        
        # معالجة الإدخال الموجه - الخطوة 3: المبلغ
        elif state == "dev_guided_step3_amount":
            try:
                amount = float(text)
                if amount <= 0:
                    await update.message.reply_text("❌ المبلغ يجب أن يكون أكبر من صفر")
                    return
                
                context.user_data['dev_signal_data']['amount'] = amount
                
                # الانتقال للخطوة 4
                user_input_state[user_id] = "dev_guided_step4_market"
                
                keyboard = [
                    [InlineKeyboardButton("📈 Spot", callback_data="dev_market_spot")],
                    [InlineKeyboardButton("🚀 Futures", callback_data="dev_market_futures")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ المبلغ: {amount}\n\n"
                    f"📝 الخطوة 4 من 5\n\n"
                    f"🏪 اختر نوع السوق:",
                    reply_markup=reply_markup
                )
                return
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
                return
        
        # معالجة الإدخال الموجه - الخطوة 5: الرافعة (للفيوتشر فقط)
        elif state == "dev_guided_step5_leverage":
            try:
                leverage = int(text)
                if leverage < 1 or leverage > 100:
                    await update.message.reply_text("❌ الرافعة يجب أن تكون بين 1 و 100")
                    return
                
                context.user_data['dev_signal_data']['leverage'] = leverage
                
                # عرض ملخص نهائي
                signal_data = context.user_data['dev_signal_data']
                
                confirm_message = f"""
✅ تم تجهيز الإشارة!

📊 الملخص:
💎 الرمز: {signal_data['symbol']}
{'🟢' if signal_data['action'] == 'buy' else '🔴'} الاتجاه: {signal_data['action'].upper()}
💰 المبلغ: {signal_data['amount']}
🏪 السوق: {signal_data['market_type'].upper()}
⚡ الرافعة: {leverage}x

❓ هل تريد إرسال هذه الإشارة للمتابعين؟
"""
                
                keyboard = [
                    [InlineKeyboardButton("✅ نعم، إرسال الآن", callback_data="dev_confirm_signal")],
                    [InlineKeyboardButton("❌ إلغاء", callback_data="developer_panel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                del user_input_state[user_id]
                await update.message.reply_text(confirm_message, reply_markup=reply_markup)
                return
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح بين 1 و 100")
                return
        
        # معالجة إرسال الإشعار الجماعي من المطور
        elif state == "waiting_for_broadcast_message":
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
🔗 ربط API - الخطوة 2 من 2

✅ تم حفظ API_KEY بنجاح!

📝 الآن أرسل API_SECRET الخاص بك

⚠️ ملاحظات مهمة:
• سيتم التحقق من صحة المفاتيح تلقائياً
• المفاتيح ستُشفر وتُحفظ بشكل آمن
• لن يتمكن أحد من رؤية مفاتيحك

🔐 جاري انتظار API_SECRET...
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
                            try:
                                await checking_message.delete()
                            except:
                                pass
                            
                            await update.message.reply_text("""
✅ تم ربط API بنجاح!

🎉 مبروك! تم التحقق من صحة المفاتيح

🟢 الاتصال: متصل بـ Bybit
🔗 الخادم: https://api.bybit.com
📊 الوضع: حساب حقيقي (Live)
🔐 الأمان: المفاتيح مشفرة ومحمية

✨ يمكنك الآن:
• تنفيذ صفقات حقيقية
• متابعة حسابك مباشرة
• استخدام جميع ميزات البوت

📱 استخدم /start للعودة إلى القائمة الرئيسية
                            """)
                    else:
                        if update.message is not None:
                            try:
                                await checking_message.delete()
                            except:
                                pass
                            await update.message.reply_text("""
❌ فشل في حفظ مفاتيح API!

🔴 حدث خطأ أثناء حفظ المفاتيح في قاعدة البيانات

💡 الحلول المقترحة:
• حاول مرة أخرى بعد قليل
• تأكد من اتصالك بالإنترنت
• تواصل مع الدعم إذا استمرت المشكلة

📱 استخدم /start للمحاولة مرة أخرى
                            """)
                else:
                    # المفاتيح غير صحيحة
                    if update.message is not None:
                        try:
                            await checking_message.delete()
                        except:
                            pass
                        await update.message.reply_text("""
❌ فشل التحقق من API keys!

🔴 الأسباب المحتملة:
• API_KEY أو API_SECRET غير صحيحة
• المفاتيح منتهية الصلاحية
• لم يتم تفعيل API في حساب Bybit
• صلاحيات API غير كافية (يجب تفعيل: Read, Write, Trade)
• قيود IP (تأكد من عدم تفعيل IP Whitelist أو أضف IP الخادم)

💡 الحلول:
1. تحقق من نسخ المفاتيح بشكل صحيح (بدون مسافات)
2. تأكد من تفعيل الصلاحيات المطلوبة
3. جرب إنشاء مفاتيح جديدة

🔗 إدارة API: https://www.bybit.com/app/user/api-management

📱 استخدم /start للمحاولة مرة أخرى
                        """)
                        # مسح البيانات المؤقتة
                        if 'temp_api_key' in context.user_data:
                            del context.user_data['temp_api_key']
                        if user_id in user_input_state:
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
                    # حفظ في قاعدة البيانات
                    db_manager.update_user_settings(user_id, {'trade_amount': amount})
                    # تحديث في user_manager
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        user_data['trade_amount'] = amount
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
                    # حفظ في قاعدة البيانات
                    db_manager.update_user_settings(user_id, {'leverage': leverage})
                    # تحديث في user_manager
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        user_data['leverage'] = leverage
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
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        market_type = user_data.get('market_type', 'spot')
                        # تحديث في حساب المستخدم
                        account = user_manager.get_user_account(user_id, market_type)
                        if account:
                            account.update_balance(balance)
                        # حفظ في قاعدة البيانات
                        user_manager.update_user_balance(user_id, balance)
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
        
        # معالجة إدخال إعدادات إدارة المخاطر
        elif state == "waiting_max_loss_percent":
            try:
                percent = float(text)
                if 1 <= percent <= 50:
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        risk_settings = user_data.get('risk_management', {})
                        risk_settings['max_loss_percent'] = percent
                        user_manager.update_user(user_id, {'risk_management': risk_settings})
                    
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث حد الخسارة المئوي إلى: {percent}%")
                        # إرسال قائمة إدارة المخاطر مباشرة
                        await send_risk_management_menu(update.message, user_id)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال نسبة بين 1 و 50")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        elif state == "waiting_max_loss_amount":
            try:
                amount = float(text)
                if amount > 0:
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        risk_settings = user_data.get('risk_management', {})
                        risk_settings['max_loss_amount'] = amount
                        user_manager.update_user(user_id, {'risk_management': risk_settings})
                    
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث حد الخسارة بالمبلغ إلى: {amount} USDT")
                        # إرسال قائمة إدارة المخاطر مباشرة
                        await send_risk_management_menu(update.message, user_id)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال مبلغ أكبر من صفر")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        elif state == "waiting_daily_loss_limit":
            try:
                limit = float(text)
                if limit > 0:
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        risk_settings = user_data.get('risk_management', {})
                        risk_settings['daily_loss_limit'] = limit
                        user_manager.update_user(user_id, {'risk_management': risk_settings})
                    
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث حد الخسارة اليومية إلى: {limit} USDT")
                        # إرسال قائمة إدارة المخاطر مباشرة
                        await send_risk_management_menu(update.message, user_id)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال مبلغ أكبر من صفر")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        elif state == "waiting_weekly_loss_limit":
            try:
                limit = float(text)
                if limit > 0:
                    user_data = user_manager.get_user(user_id)
                    if user_data:
                        risk_settings = user_data.get('risk_management', {})
                        risk_settings['weekly_loss_limit'] = limit
                        user_manager.update_user(user_id, {'risk_management': risk_settings})
                    
                    del user_input_state[user_id]
                    if update.message is not None:
                        await update.message.reply_text(f"✅ تم تحديث حد الخسارة الأسبوعية إلى: {limit} USDT")
                        # إرسال قائمة إدارة المخاطر مباشرة
                        await send_risk_management_menu(update.message, user_id)
                else:
                    if update.message is not None:
                        await update.message.reply_text("❌ يرجى إدخال مبلغ أكبر من صفر")
            except ValueError:
                if update.message is not None:
                    await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال نسبة الإغلاق الجزئي المخصصة
        elif state.startswith("waiting_partial_percentage_"):
            try:
                percentage = float(text)
                if 1 <= percentage <= 100:
                    position_id = state.replace("waiting_partial_percentage_", "")
                    del user_input_state[user_id]
                    
                    # استدعاء دالة الإغلاق الجزئي مع النسبة المخصصة
                    # تحويل إلى callback query وهمي
                    from telegram import InlineKeyboardButton
                    
                    # البحث عن الصفقة
                    position_info = None
                    if user_id in user_manager.user_positions:
                        position_info = user_manager.user_positions[user_id].get(position_id)
                    if not position_info:
                        position_info = trading_bot.open_positions.get(position_id)
                    
                    if not position_info:
                        await update.message.reply_text("❌ الصفقة غير موجودة")
                        return
                    
                    # معالجة الإغلاق
                    market_type = position_info.get('account_type', 'spot')
                    is_user_position = user_id in user_manager.user_positions and position_id in user_manager.user_positions[user_id]
                    
                    if is_user_position:
                        account = user_manager.get_user_account(user_id, market_type)
                    else:
                        account = trading_bot.demo_account_futures if market_type == 'futures' else trading_bot.demo_account_spot
                    
                    current_price = position_info.get('current_price', position_info['entry_price'])
                    original_amount = position_info.get('amount', position_info.get('margin_amount', 0))
                    close_amount = original_amount * (percentage / 100)
                    
                    entry_price = position_info['entry_price']
                    side = position_info['side']
                    
                    if side.lower() == "buy":
                        pnl = (current_price - entry_price) * (close_amount / entry_price)
                    else:
                        pnl = (entry_price - current_price) * (close_amount / entry_price)
                    
                    position_info['amount'] = original_amount - close_amount
                    
                    if market_type == 'spot':
                        account.balance += close_amount + pnl
                    else:
                        account.balance += pnl
                        account.margin_locked -= close_amount
                    
                    pnl_emoji = "🟢💰" if pnl >= 0 else "🔴💸"
                    message = f"""
{pnl_emoji} تم إغلاق {percentage}% من الصفقة

📊 الرمز: {position_info['symbol']}
🔄 النوع: {side.upper()}
💲 سعر الإغلاق: {current_price:.6f}
💰 المبلغ المغلق: {close_amount:.2f}
{pnl_emoji} الربح/الخسارة: {pnl:+.2f}

📈 المتبقي: {position_info['amount']:.2f} ({100-percentage}%)
💰 الرصيد الجديد: {account.balance:.2f}
                    """
                    
                    keyboard = [[
                        InlineKeyboardButton("🔙 رجوع للإدارة", callback_data=f"manage_{position_id}"),
                        InlineKeyboardButton("📊 الصفقات المفتوحة", callback_data="show_positions")
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup)
                else:
                    await update.message.reply_text("❌ النسبة يجب أن تكون بين 1 و 100")
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال Take Profit مخصص
        elif state.startswith("waiting_custom_tp_"):
            try:
                position_id = state.replace("waiting_custom_tp_", "")
                parts = text.split()
                
                if len(parts) != 2:
                    await update.message.reply_text("❌ الصيغة غير صحيحة. استخدم: `نسبة_الربح نسبة_الإغلاق`\nمثال: `3 50`")
                    return
                
                tp_percentage = float(parts[0])
                close_percentage = float(parts[1])
                
                if tp_percentage <= 0 or tp_percentage > 100:
                    await update.message.reply_text("❌ نسبة الربح يجب أن تكون بين 0.1 و 100")
                    return
                
                if close_percentage <= 0 or close_percentage > 100:
                    await update.message.reply_text("❌ نسبة الإغلاق يجب أن تكون بين 1 و 100")
                    return
                
                managed_pos = trade_tools_manager.get_managed_position(position_id)
                if not managed_pos:
                    await update.message.reply_text("❌ الصفقة غير موجودة")
                    return
                
                # حساب سعر الهدف
                if managed_pos.side.lower() == "buy":
                    tp_price = managed_pos.entry_price * (1 + tp_percentage / 100)
                else:
                    tp_price = managed_pos.entry_price * (1 - tp_percentage / 100)
                
                success = managed_pos.add_take_profit(tp_price, close_percentage / 100)
                
                if success:
                    del user_input_state[user_id]
                    
                    keyboard = [[
                        InlineKeyboardButton("➕ إضافة هدف آخر", callback_data=f"customTP_{position_id}"),
                        InlineKeyboardButton("🔙 رجوع", callback_data=f"setTP_menu_{position_id}")
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"✅ تم إضافة هدف الربح!\n\n"
                        f"🎯 السعر: {tp_price:.6f} (+{tp_percentage}%)\n"
                        f"📊 نسبة الإغلاق: {close_percentage}%",
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text("❌ فشل في إضافة الهدف")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال أرقام صحيحة")
        
        # معالجة إدخال Stop Loss مخصص
        elif state.startswith("waiting_custom_sl_"):
            try:
                position_id = state.replace("waiting_custom_sl_", "")
                sl_percentage = float(text)
                
                if sl_percentage <= 0 or sl_percentage > 50:
                    await update.message.reply_text("❌ نسبة Stop Loss يجب أن تكون بين 0.1 و 50")
                    return
                
                managed_pos = trade_tools_manager.get_managed_position(position_id)
                if not managed_pos:
                    await update.message.reply_text("❌ الصفقة غير موجودة")
                    return
                
                # حساب سعر SL
                if managed_pos.side.lower() == "buy":
                    sl_price = managed_pos.entry_price * (1 - sl_percentage / 100)
                else:
                    sl_price = managed_pos.entry_price * (1 + sl_percentage / 100)
                
                # التحقق من Trailing Stop نشط
                if managed_pos.stop_loss and managed_pos.stop_loss.is_trailing:
                    keyboard = [[
                        InlineKeyboardButton("نعم، إلغاء Trailing", callback_data=f"confirmSL_{position_id}_{sl_percentage}"),
                        InlineKeyboardButton("❌ إلغاء", callback_data=f"setSL_menu_{position_id}")
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "⚠️ **تحذير:** Trailing Stop نشط حالياً\n\n"
                        "تعيين SL ثابت سيُلغي Trailing Stop. هل تريد المتابعة؟",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    return
                
                success = managed_pos.set_stop_loss(sl_price, is_trailing=False)
                
                if success:
                    del user_input_state[user_id]
                    
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"setSL_menu_{position_id}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"✅ تم تعيين Stop Loss!\n\n"
                        f"🛑 السعر: {sl_price:.6f} (-{sl_percentage}%)\n"
                        f"📉 المخاطرة: {sl_percentage}% من رأس المال",
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text("❌ فشل في تعيين Stop Loss")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال مسافة Trailing Stop مخصصة
        elif state.startswith("waiting_custom_trailing_"):
            try:
                position_id = state.replace("waiting_custom_trailing_", "")
                trailing_distance = float(text)
                
                if trailing_distance <= 0 or trailing_distance > 20:
                    await update.message.reply_text("❌ المسافة يجب أن تكون بين 0.1 و 20")
                    return
                
                managed_pos = trade_tools_manager.get_managed_position(position_id)
                if not managed_pos:
                    await update.message.reply_text("❌ الصفقة غير موجودة")
                    return
                
                # تعيين trailing stop
                if not managed_pos.stop_loss:
                    if managed_pos.side.lower() == "buy":
                        sl_price = managed_pos.entry_price * (1 - trailing_distance / 100)
                    else:
                        sl_price = managed_pos.entry_price * (1 + trailing_distance / 100)
                    
                    managed_pos.set_stop_loss(sl_price, is_trailing=True, trailing_distance=trailing_distance)
                else:
                    # إلغاء SL الثابت إذا كان موجود
                    managed_pos.stop_loss.is_trailing = True
                    managed_pos.stop_loss.trailing_distance = trailing_distance
                
                del user_input_state[user_id]
                
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"trailing_menu_{position_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ تم تفعيل Trailing Stop!\n\n"
                    f"⚡ المسافة: {trailing_distance}%\n"
                    f"🔒 السعر الحالي: {managed_pos.stop_loss.price:.6f}\n\n"
                    f"💡 سيتحرك SL تلقائياً مع تحرك السعر لصالحك",
                    reply_markup=reply_markup
                )
                
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال أهداف الربح التلقائية
        elif state == "waiting_auto_tp_input":
            try:
                lines = text.strip().split('\n')
                tp_percentages = []
                tp_close_percentages = []
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) != 2:
                        await update.message.reply_text("❌ الصيغة غير صحيحة. كل سطر يجب أن يحتوي على: نسبة_الربح نسبة_الإغلاق")
                        return
                    
                    tp_pct = float(parts[0])
                    close_pct = float(parts[1])
                    
                    if tp_pct <= 0 or tp_pct > 100:
                        await update.message.reply_text("❌ نسبة الربح يجب أن تكون بين 0.1 و 100")
                        return
                    
                    if close_pct <= 0 or close_pct > 100:
                        await update.message.reply_text("❌ نسبة الإغلاق يجب أن تكون بين 1 و 100")
                        return
                    
                    tp_percentages.append(tp_pct)
                    tp_close_percentages.append(close_pct)
                
                if len(tp_percentages) > 5:
                    await update.message.reply_text("❌ الحد الأقصى 5 أهداف")
                    return
                
                # حفظ الإعدادات
                success = trade_tools_manager.save_auto_settings(
                    tp_percentages=tp_percentages,
                    tp_close_percentages=tp_close_percentages,
                    sl_percentage=trade_tools_manager.default_sl_percentage,
                    trailing_enabled=trade_tools_manager.default_trailing_enabled,
                    trailing_distance=trade_tools_manager.default_trailing_distance,
                    breakeven_on_tp1=True
                )
                
                if success:
                    del user_input_state[user_id]
                    
                    message = "✅ **تم حفظ أهداف الربح!**\n\n🎯 **الأهداف:**\n"
                    for i, (tp, close) in enumerate(zip(tp_percentages, tp_close_percentages), 1):
                        message += f"• TP{i}: +{tp}% → إغلاق {close}%\n"
                    
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ فشل في حفظ الإعدادات")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال أرقام صحيحة")
        
        # معالجة إدخال Stop Loss التلقائي
        elif state == "waiting_auto_sl_input":
            try:
                sl_percentage = float(text)
                
                if sl_percentage <= 0 or sl_percentage > 50:
                    await update.message.reply_text("❌ نسبة Stop Loss يجب أن تكون بين 0.1 و 50")
                    return
                
                # حفظ الإعدادات
                success = trade_tools_manager.save_auto_settings(
                    tp_percentages=trade_tools_manager.default_tp_percentages,
                    tp_close_percentages=trade_tools_manager.default_tp_close_percentages,
                    sl_percentage=sl_percentage,
                    trailing_enabled=trade_tools_manager.default_trailing_enabled,
                    trailing_distance=trade_tools_manager.default_trailing_distance,
                    breakeven_on_tp1=True
                )
                
                if success:
                    del user_input_state[user_id]
                    
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="edit_auto_settings")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"✅ **تم حفظ Stop Loss!**\n\n"
                        f"🛑 النسبة: -{sl_percentage}%",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ فشل في حفظ الإعدادات")
                    
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال نسبة TP في بناء الأهداف
        elif state.startswith("building_auto_tp_target_") and state.endswith("_percent"):
            try:
                tp_percent = float(text)
                
                if tp_percent <= 0 or tp_percent > 100:
                    await update.message.reply_text("❌ النسبة يجب أن تكون بين 0.1 و 100")
                    return
                
                # حفظ وانتقال لإدخال نسبة الإغلاق
                if 'auto_tp_builder' not in context.user_data:
                    context.user_data['auto_tp_builder'] = {}
                context.user_data['auto_tp_builder']['temp_tp_percent'] = tp_percent
                
                await process_tp_target_input(update, context, tp_percent)
                
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح")
        
        # معالجة إدخال نسبة الإغلاق في بناء الأهداف
        elif state.startswith("building_auto_tp_target_") and state.endswith("_close"):
            try:
                close_percent = float(text)
                
                if close_percent <= 0 or close_percent > 100:
                    await update.message.reply_text("❌ النسبة يجب أن تكون بين 1 و 100")
                    return
                
                await finalize_tp_target(update, context, close_percent)
                
            except ValueError:
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
    elif text == "📊 إحصائيات":
        await show_user_statistics(update, context)
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

async def show_webhook_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الشرح المفصل لكيفية استخدام Webhook"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # إنشاء رابط webhook الشخصي
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        webhook_url = f"{railway_url}/personal/{user_id}/webhook"
    elif render_url:
        webhook_url = f"{render_url}/personal/{user_id}/webhook"
    else:
        port = PORT
        webhook_url = f"http://localhost:{port}/personal/{user_id}/webhook"
    
    help_message = f"""
📖 **الشرح المفصل لاستخدام Webhook**

━━━━━━━━━━━━━━━━━━━━━━

🔗 **رابط Webhook الخاص بك:**
```
{webhook_url}
```

━━━━━━━━━━━━━━━━━━━━━━

**🎯 ما هو Webhook؟**

Webhook هو رابط خاص بك يستقبل الإشارات من TradingView أو أي منصة أخرى ويرسلها مباشرة إلى البوت لتنفيذها.

━━━━━━━━━━━━━━━━━━━━━━

**📱 كيفية الإعداد في TradingView:**

**الخطوة 1️⃣: إنشاء Alert**
• افتح الشارت في TradingView
• اضغط على زر "Alert" (🔔)
• اختر الشرط المناسب لاستراتيجيتك

**الخطوة 2️⃣: إعداد Webhook**
• في إعدادات Alert، اختر "Webhook URL"
• انسخ رابط Webhook أعلاه والصقه

**الخطوة 3️⃣: كتابة الإشارة**
في حقل "Message"، اكتب الإشارة بتنسيق JSON:

━━━━━━━━━━━━━━━━━━━━━━

**📋 أمثلة الإشارات:**

**🟢 شراء:**
```json
{{
    "signal": "buy",
    "symbol": "BTCUSDT",
    "id": "TV_B01"
}}
```

**🔴 بيع:**
```json
{{
    "signal": "sell",
    "symbol": "BTCUSDT",
    "id": "TV_S01"
}}
```

**⚪ إغلاق كامل:**
```json
{{
    "signal": "close",
    "symbol": "BTCUSDT",
    "id": "TV_C01"
}}
```

**🟡 إغلاق جزئي (50%):**
```json
{{
    "signal": "partial_close",
    "symbol": "BTCUSDT",
    "percentage": 50,
    "id": "TV_PC01"
}}
```

━━━━━━━━━━━━━━━━━━━━━━

**✅ ما الذي يحدث؟**

1. **TradingView** يرسل الإشارة للرابط
2. **البوت** يستقبل الإشارة تلقائياً
3. **النظام الذكي** يضيف:
   • السعر الحالي (من Bybit)
   • المبلغ (من إعداداتك)
   • الرافعة (من إعداداتك)
4. **التنفيذ** يتم فوراً
5. **الإشعار** يصلك على التلجرام

━━━━━━━━━━━━━━━━━━━━━━

**⚠️ ملاحظات أمان:**

🔒 **احتفظ بالرابط سرياً**
• لا تشاركه مع أحد
• كل شخص لديه الرابط يمكنه إرسال إشارات

🛡️ **التحكم في الوصول**
• يمكنك تعطيل حسابك من الإعدادات
• سيتوقف استقبال الإشارات عند التعطيل

━━━━━━━━━━━━━━━━━━━━━━

**💡 نصائح:**

✅ **للاختبار:**
• استخدم الحساب التجريبي أولاً
• جرب جميع أنواع الإشارات
• تأكد من استلام الإشعارات

✅ **للإنتاج:**
• تحقق من إعداداتك (المبلغ، الرافعة)
• راقب الإشارات في البداية
• استخدم Stop Loss دائماً

━━━━━━━━━━━━━━━━━━━━━━

**📚 للمزيد:**
استخدم أمر /help للحصول على المساعدة

━━━━━━━━━━━━━━━━━━━━━━

✨ **جاهز للبدء؟**
انسخ رابط Webhook واستخدمه في TradingView!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            help_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

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
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()