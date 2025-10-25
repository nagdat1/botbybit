#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
البوت الرئيسي الموحد - Unified Trading Bot
دمج جميع الوظائف الأساسية في ملف واحد منظم
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

# استيراد الإعدادات والوحدات الأساسية
from config import *
from database import db_manager
from user_manager import user_manager
from real_account_manager import BybitRealAccount, MEXCRealAccount

logger = logging.getLogger(__name__)

# ==================== الكلاسات الأساسية ====================

@dataclass
class TakeProfitLevel:
    """مستوى هدف الربح"""
    price: float
    percentage: float
    hit: bool = False
    hit_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.percentage <= 0 or self.percentage > 100:
            raise ValueError(f"نسبة الإغلاق يجب أن تكون بين 0 و 100، القيمة: {self.percentage}")

@dataclass
class StopLoss:
    """وقف الخسارة"""
    price: float
    initial_price: float
    is_trailing: bool = False
    trailing_distance: float = 0.0
    moved_to_breakeven: bool = False
    last_update: Optional[datetime] = None
    
    def update_trailing(self, current_price: float, side: str):
        """تحديث trailing stop"""
        if not self.is_trailing or self.trailing_distance <= 0:
            return False
        
        try:
            if side.lower() == "buy":
                new_stop = current_price * (1 - self.trailing_distance / 100)
                if new_stop > self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
            else:  # sell
                new_stop = current_price * (1 + self.trailing_distance / 100)
                if new_stop < self.price:
                    old_price = self.price
                    self.price = new_stop
                    self.last_update = datetime.now()
                    logger.info(f"تم تحديث Trailing Stop من {old_price:.6f} إلى {new_stop:.6f}")
                    return True
        except Exception as e:
            logger.error(f"خطأ في تحديث Trailing Stop: {e}")
        
        return False

@dataclass
class PositionManagement:
    """إدارة الصفقة المتقدمة"""
    position_id: str
    symbol: str
    side: str
    entry_price: float
    quantity: float
    market_type: str
    leverage: int = 1
    take_profits: List[TakeProfitLevel] = field(default_factory=list)
    stop_loss: Optional[StopLoss] = None
    realized_pnl: float = 0.0
    created_time: datetime = field(default_factory=datetime.now)
    
    def add_take_profit(self, price: float, percentage: float):
        """إضافة هدف ربح"""
        tp = TakeProfitLevel(price=price, percentage=percentage)
        self.take_profits.append(tp)
        logger.info(f"تم إضافة TP: {price:.6f} ({percentage}%)")
    
    def set_stop_loss(self, price: float, is_trailing: bool = False, trailing_distance: float = 0.0):
        """تعيين وقف الخسارة"""
        self.stop_loss = StopLoss(
            price=price,
            initial_price=price,
            is_trailing=is_trailing,
            trailing_distance=trailing_distance
        )
        logger.info(f"تم تعيين SL: {price:.6f} (Trailing: {is_trailing})")
        return True
    
    def check_take_profits(self, current_price: float) -> List[Dict]:
        """التحقق من أهداف الربح"""
        executions = []
        
        for tp in self.take_profits:
            if tp.hit:
                continue
            
            hit = False
            if self.side.lower() == "buy":
                hit = current_price >= tp.price
            else:
                hit = current_price <= tp.price
            
            if hit:
                tp.hit = True
                tp.hit_time = datetime.now()
                
                # حساب الربح المحقق
                if self.side.lower() == "buy":
                    pnl = (current_price - self.entry_price) * self.quantity * (tp.percentage / 100)
                else:
                    pnl = (self.entry_price - current_price) * self.quantity * (tp.percentage / 100)
                
                self.realized_pnl += pnl
                
                executions.append({
                    'type': 'take_profit',
                    'price': current_price,
                    'percentage': tp.percentage,
                    'pnl': pnl,
                    'time': tp.hit_time
                })
                
                logger.info(f"تم تحقيق TP: {tp.price:.6f} ({tp.percentage}%) - PnL: {pnl:.2f}")
        
        return executions
    
    def check_stop_loss(self, current_price: float) -> Optional[Dict]:
        """التحقق من وقف الخسارة"""
        if not self.stop_loss:
            return None
        
        # تحديث trailing stop إذا كان مفعلاً
        if self.stop_loss.is_trailing:
            self.stop_loss.update_trailing(current_price, self.side)
        
        hit = False
        if self.side.lower() == "buy":
            hit = current_price <= self.stop_loss.price
        else:
            hit = current_price >= self.stop_loss.price
        
        if hit:
            # حساب الخسارة
            if self.side.lower() == "buy":
                pnl = (current_price - self.entry_price) * self.quantity
            else:
                pnl = (self.entry_price - current_price) * self.quantity
            
            self.realized_pnl += pnl
            
            execution = {
                'type': 'stop_loss',
                'price': current_price,
                'pnl': pnl,
                'time': datetime.now()
            }
            
            logger.info(f"تم تفعيل SL: {self.stop_loss.price:.6f} - PnL: {pnl:.2f}")
            return execution
        
        return None

class TradeToolsManager:
    """مدير أدوات التداول المتقدمة"""
    
    def __init__(self):
        self.managed_positions: Dict[str, PositionManagement] = {}
        self.auto_apply_enabled = False
        self.default_tp_percentages: List[tuple] = []
        self.default_tp_close_percentages: List[float] = []
        self.default_sl_percentage: float = 0.0
        self.default_trailing_enabled = False
        self.default_trailing_distance: float = 2.0
        self.auto_breakeven_on_tp1 = True
    
    def create_managed_position(self, position_id: str, symbol: str, side: str,
                               entry_price: float, quantity: float, market_type: str,
                               leverage: int = 1) -> Optional[PositionManagement]:
        """إنشاء صفقة مدارة"""
        try:
            pm = PositionManagement(
                position_id=position_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                market_type=market_type,
                leverage=leverage
            )
            
            self.managed_positions[position_id] = pm
            logger.info(f"تم إنشاء إدارة الصفقة {position_id}")
            return pm
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء إدارة الصفقة: {e}")
            return None
    
    def get_managed_position(self, position_id: str) -> Optional[PositionManagement]:
        """الحصول على صفقة مدارة"""
        return self.managed_positions.get(position_id)
    
    def remove_managed_position(self, position_id: str) -> bool:
        """إزالة صفقة مدارة"""
        if position_id in self.managed_positions:
            del self.managed_positions[position_id]
            logger.info(f"تم إزالة إدارة الصفقة {position_id}")
            return True
        return False
    
    def update_all_positions(self, prices: Dict[str, float]) -> Dict[str, List[Dict]]:
        """تحديث جميع الصفقات المدارة"""
        results = {}
        
        for position_id, pm in list(self.managed_positions.items()):
            if pm.symbol in prices:
                current_price = prices[pm.symbol]
                
                # التحقق من الأهداف
                tp_executions = pm.check_take_profits(current_price)
                sl_execution = pm.check_stop_loss(current_price)
                
                if tp_executions or sl_execution:
                    results[position_id] = {
                        'take_profits': tp_executions,
                        'stop_loss': sl_execution,
                        'current_price': current_price,
                        'unrealized_pnl': self._calculate_unrealized_pnl(pm, current_price)
                    }
        
        return results
    
    def _calculate_unrealized_pnl(self, pm: PositionManagement, current_price: float) -> float:
        """حساب الربح/الخسارة غير المحققة"""
        if pm.side.lower() == "buy":
            return (current_price - pm.entry_price) * pm.quantity
        else:
            return (pm.entry_price - current_price) * pm.quantity

# ==================== البوت الرئيسي الموحد ====================

class UnifiedTradingBot:
    """البوت الرئيسي الموحد - يجمع جميع الوظائف"""
    
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
        self.user_id = None
        
        # قائمة الصفقات المفتوحة
        self.open_positions = {}
        
        # إدارة أدوات التداول
        self.trade_tools_manager = TradeToolsManager()
        
        # قائمة الأزواج المتاحة
        self.available_pairs = {
            'spot': [],
            'futures': [],
            'inverse': []
        }
        self.last_pairs_update = 0
        
        logger.info("تم تهيئة البوت الموحد بنجاح")
    
    async def process_signal(self, signal_data: dict):
        """معالجة إشارة التداول الموحدة"""
        try:
            self.signals_received += 1
            
            if not self.is_running:
                logger.info("البوت متوقف، تم تجاهل الإشارة")
                return
            
            # تحويل الإشارة إذا كانت بالتنسيق الجديد
            from signal_converter import convert_simple_signal, validate_simple_signal
            
            if 'signal' in signal_data and 'action' not in signal_data:
                logger.info(f"استقبال إشارة جديدة بالتنسيق البسيط: {signal_data}")
                
                is_valid, validation_message = validate_simple_signal(signal_data)
                if not is_valid:
                    logger.error(f"إشارة غير صحيحة: {validation_message}")
                    await self.send_message_to_admin(f"إشارة غير صحيحة\n\nالتفاصيل: {validation_message}")
                    return
                
                converted_signal = convert_simple_signal(signal_data, self.user_settings)
                if not converted_signal:
                    logger.error("فشل تحويل الإشارة")
                    await self.send_message_to_admin("فشل تحويل الإشارة")
                    return
                
                logger.info(f"تم تحويل الإشارة بنجاح: {converted_signal}")
                signal_data = converted_signal
            
            # استخراج البيانات
            symbol = signal_data.get('symbol', '').upper()
            action = signal_data.get('action', '').lower()
            
            if not symbol or not action:
                logger.error("بيانات الإشارة غير مكتملة")
                return
            
            # تحديث الأزواج المتاحة
            await self.update_available_pairs()
            
            # تحديد نوع السوق
            user_market_type = self.user_settings['market_type']
            bybit_category = "spot" if user_market_type == "spot" else "linear"
            market_type = user_market_type
            
            # التحقق من وجود الرمز في Bybit
            logger.info(f"التحقق من وجود الرمز {symbol} في Bybit {user_market_type.upper()}")
            
            symbol_exists_in_bybit = False
            if self.bybit_api:
                symbol_exists_in_bybit = self.bybit_api.check_symbol_exists(symbol, bybit_category)
                logger.info(f"نتيجة التحقق من Bybit API: {symbol_exists_in_bybit}")
            else:
                if user_market_type == "spot" and symbol in self.available_pairs.get('spot', []):
                    symbol_exists_in_bybit = True
                elif user_market_type == "futures" and (symbol in self.available_pairs.get('futures', []) or symbol in self.available_pairs.get('inverse', [])):
                    symbol_exists_in_bybit = True
                    if symbol in self.available_pairs.get('inverse', []):
                        bybit_category = "inverse"
            
            if not symbol_exists_in_bybit:
                available_pairs = self.available_pairs.get(user_market_type, [])
                if user_market_type == "futures":
                    available_pairs = self.available_pairs.get('futures', []) + self.available_pairs.get('inverse', [])
                
                pairs_list = ", ".join(available_pairs[:20])
                error_message = f"الرمز {symbol} غير موجود في منصة Bybit!\n\n🏪 نوع السوق: {user_market_type.upper()}\nأمثلة للأزواج المتاحة:\n{pairs_list}..."
                await self.send_message_to_admin(error_message)
                logger.warning(f"الرمز {symbol} غير موجود في Bybit {user_market_type}")
                return
            
            logger.info(f"الرمز {symbol} موجود في Bybit {user_market_type.upper()}")
            
            # الحصول على السعر الحالي
            if self.bybit_api:
                current_price = self.bybit_api.get_ticker_price(symbol, bybit_category)
                if current_price is None:
                    await self.send_message_to_admin(f"فشل في الحصول على سعر {symbol} من Bybit")
                    return
                logger.info(f"💲 سعر {symbol} الحالي: {current_price}")
            else:
                current_price = 100.0
                logger.warning("استخدام سعر وهمي للاختبار فقط")
            
            # تحديد نوع الحساب وتنفيذ الصفقة
            account_type = self.user_settings['account_type']
            
            if account_type == 'real':
                logger.info(f"🔴 تنفيذ صفقة حقيقية عبر Bybit API")
                await self.execute_real_trade(symbol, action, current_price, bybit_category)
            else:
                logger.info(f"🟢 تنفيذ صفقة تجريبية داخل البوت")
                await self.execute_demo_trade(symbol, action, current_price, bybit_category, market_type)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            await self.send_message_to_admin(f"خطأ في معالجة الإشارة: {e}")
    
    async def execute_real_trade(self, symbol: str, action: str, price: float, category: str):
        """تنفيذ صفقة حقيقية عبر Bybit API"""
        try:
            # الحصول على مفاتيح API الخاصة بالمستخدم
            if not self.user_id:
                await self.send_message_to_admin("❌ معرف المستخدم غير متاح")
                logger.error("معرف المستخدم غير متاح لتنفيذ الصفقة الحقيقية")
                return
            
            user_data = user_manager.get_user(self.user_id)
            if not user_data:
                await self.send_message_to_admin("❌ بيانات المستخدم غير متاحة")
                logger.error(f"بيانات المستخدم غير متاحة للمستخدم {self.user_id}")
                return
            
            api_key = user_data.get('bybit_api_key')
            api_secret = user_data.get('bybit_api_secret')
            
            if not api_key or not api_secret:
                await self.send_message_to_admin("❌ مفاتيح API غير متاحة للمستخدم")
                logger.error(f"مفاتيح API غير متاحة للمستخدم {self.user_id}")
                return
            
            # إنشاء اتصال API باستخدام مفاتيح المستخدم
            user_bybit_api = BybitRealAccount(api_key, api_secret)
            logger.info(f"🔑 استخدام مفاتيح API الخاصة بالمستخدم {self.user_id}")
            
            user_market_type = self.user_settings['market_type']
            side = "Buy" if action == "buy" else "Sell"
            
            logger.info(f"🔴 بدء تنفيذ صفقة حقيقية: {symbol} {side} في {user_market_type.upper()}")
            
            # حساب TP/SL التلقائي إذا كان مفعلاً
            tp_prices = []
            sl_price = None
            
            if self.trade_tools_manager.auto_apply_enabled:
                logger.info("🤖 الإعدادات التلقائية مفعلة - حساب TP/SL...")
                
                # حساب Take Profit
                if self.trade_tools_manager.default_tp_percentages:
                    for tp_percent, _ in self.trade_tools_manager.default_tp_percentages:
                        if action == "buy":
                            tp_price = price * (1 + tp_percent / 100)
                        else:
                            tp_price = price * (1 - tp_percent / 100)
                        tp_prices.append(tp_price)
                        logger.info(f"TP: {tp_percent}% = {tp_price:.6f}")
                
                # حساب Stop Loss
                if self.trade_tools_manager.default_sl_percentage:
                    sl_percent = self.trade_tools_manager.default_sl_percentage
                    if action == "buy":
                        sl_price = price * (1 - sl_percent / 100)
                    else:
                        sl_price = price * (1 + sl_percent / 100)
                    logger.info(f"🛑 SL: {sl_percent}% = {sl_price:.6f}")
            
            if user_market_type == 'futures':
                # صفقة فيوتشر حقيقية
                margin_amount = self.user_settings['trade_amount']
                leverage = self.user_settings['leverage']
                
                position_size = margin_amount * leverage
                qty = str(position_size / price)
                
                logger.info(f"⚡ فيوتشر: الهامش={margin_amount}, الرافعة={leverage}x, حجم الصفقة={position_size:.2f}")
                
                first_tp = str(tp_prices[0]) if tp_prices else None
                first_sl = str(sl_price) if sl_price else None
                
                response = user_bybit_api.place_order(
                    category=category,
                    symbol=symbol,
                    side=side,
                    order_type="Market",
                    qty=qty,
                    take_profit=first_tp,
                    stop_loss=first_sl
                )
                
                if response.get("retCode") == 0:
                    order_id = response.get("result", {}).get("orderId", "")
                    
                    message = f"تم تنفيذ صفقة فيوتشر حقيقية\n\n"
                    if self.user_id:
                        message += f"المستخدم: {self.user_id}\n"
                    message += f"الرمز: {symbol}\n"
                    message += f"النوع: {side}\n"
                    message += f"الهامش: {margin_amount}\n"
                    message += f"⚡ الرافعة: {leverage}x\n"
                    message += f"حجم الصفقة: {position_size:.2f}\n"
                    message += f"💲 السعر التقريبي: {price:.6f}\n"
                    message += f"🏪 السوق: FUTURES\n"
                    message += f"رقم الأمر: {order_id}\n"
                    
                    if first_tp:
                        message += f"\nTake Profit: {float(first_tp):.6f}"
                    if first_sl:
                        message += f"\n🛑 Stop Loss: {float(first_sl):.6f}"
                    
                    message += f"\n\nتحذير: هذه صفقة حقيقية على منصة Bybit!"
                    
                    await self.send_message_to_admin(message)
                    logger.info(f"تم تنفيذ صفقة فيوتشر حقيقية: {order_id}")
                else:
                    error_msg = response.get("retMsg", "خطأ غير محدد")
                    await self.send_message_to_admin(f"فشل في تنفيذ صفقة الفيوتشر: {error_msg}")
                    logger.error(f"فشل تنفيذ صفقة فيوتشر: {error_msg}")
                    
            else:  # spot
                # صفقة سبوت حقيقية
                amount = self.user_settings['trade_amount']
                qty = str(amount / price)
                
                logger.info(f"🏪 سبوت: المبلغ={amount}, الكمية={qty}")
                
                response = user_bybit_api.place_order(
                    category=category,
                    symbol=symbol,
                    side=side,
                    order_type="Market",
                    qty=qty
                )
                
                if response.get("retCode") == 0:
                    order_id = response.get("result", {}).get("orderId", "")
                    
                    message = f"تم تنفيذ صفقة سبوت حقيقية\n\n"
                    if self.user_id:
                        message += f"المستخدم: {self.user_id}\n"
                    message += f"الرمز: {symbol}\n"
                    message += f"النوع: {side}\n"
                    message += f"المبلغ: {amount}\n"
                    message += f"الكمية: {qty}\n"
                    message += f"💲 السعر التقريبي: {price:.6f}\n"
                    message += f"🏪 السوق: SPOT\n"
                    message += f"رقم الأمر: {order_id}\n"
                    message += f"\nتحذير: هذه صفقة حقيقية على منصة Bybit!"
                    
                    await self.send_message_to_admin(message)
                    logger.info(f"تم تنفيذ صفقة سبوت حقيقية: {order_id}")
                else:
                    error_msg = response.get("retMsg", "خطأ غير محدد")
                    await self.send_message_to_admin(f"فشل في تنفيذ صفقة السبوت: {error_msg}")
                    logger.error(f"فشل تنفيذ صفقة سبوت: {error_msg}")
                    
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة الحقيقية: {e}")
            await self.send_message_to_admin(f"خطأ في تنفيذ الصفقة الحقيقية: {e}")
    
    async def execute_demo_trade(self, symbol: str, action: str, price: float, category: str, market_type: str):
        """تنفيذ صفقة تجريبية داخل البوت"""
        try:
            logger.info(f"🟢 بدء تنفيذ صفقة تجريبية: {symbol} {action} في {market_type.upper()}")
            
            if market_type == 'futures':
                # صفقة فيوتشر تجريبية
                margin_amount = self.user_settings['trade_amount']
                leverage = self.user_settings['leverage']
                
                success, message = self.demo_account_futures.open_futures_position(
                    symbol=symbol,
                    side=action,
                    margin_amount=margin_amount,
                    entry_price=price,
                    leverage=leverage
                )
                
                if success:
                    logger.info(f"تم تنفيذ صفقة فيوتشر تجريبية: {symbol}")
                    await self.send_message_to_admin(f"✅ {message}")
                else:
                    logger.error(f"فشل تنفيذ صفقة فيوتشر تجريبية: {message}")
                    await self.send_message_to_admin(f"❌ {message}")
                    
            else:  # spot
                # صفقة سبوت تجريبية
                amount = self.user_settings['trade_amount']
                
                success, message = self.demo_account_spot.open_spot_position(
                    symbol=symbol,
                    side=action,
                    amount=amount,
                    price=price
                )
                
                if success:
                    logger.info(f"تم تنفيذ صفقة سبوت تجريبية: {symbol}")
                    await self.send_message_to_admin(f"✅ {message}")
                else:
                    logger.error(f"فشل تنفيذ صفقة سبوت تجريبية: {message}")
                    await self.send_message_to_admin(f"❌ {message}")
                    
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة التجريبية: {e}")
            await self.send_message_to_admin(f"خطأ في تنفيذ الصفقة التجريبية: {e}")
    
    async def update_available_pairs(self):
        """تحديث قائمة الأزواج المتاحة"""
        try:
            current_time = time.time()
            if current_time - self.last_pairs_update < 300:  # 5 دقائق
                return
            
            if self.bybit_api:
                # جلب الأزواج من Bybit API
                spot_pairs = self.bybit_api.get_spot_pairs()
                futures_pairs = self.bybit_api.get_futures_pairs()
                
                if spot_pairs:
                    self.available_pairs['spot'] = spot_pairs
                if futures_pairs:
                    self.available_pairs['futures'] = futures_pairs
                
                self.last_pairs_update = current_time
                logger.info(f"تم تحديث الأزواج المتاحة: Spot={len(self.available_pairs['spot'])}, Futures={len(self.available_pairs['futures'])}")
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الأزواج المتاحة: {e}")
    
    async def send_message_to_admin(self, message: str):
        """إرسال رسالة للمدير"""
        try:
            if ADMIN_USER_ID and TELEGRAM_TOKEN:
                from telegram import Bot
                bot = Bot(token=TELEGRAM_TOKEN)
                await bot.send_message(chat_id=ADMIN_USER_ID, text=message)
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة للمدير: {e}")

# ==================== إنشاء مثيل البوت الموحد ====================

# إنشاء مثيل البوت الموحد
unified_trading_bot = UnifiedTradingBot()

# تصدير البوت للاستخدام في الملفات الأخرى
trading_bot = unified_trading_bot

logger.info("تم إنشاء البوت الموحد بنجاح")
