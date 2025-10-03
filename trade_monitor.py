# -*- coding: utf-8 -*-
"""
نظام تحديث أسعار الصفقات ومراقبة TP/SL
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TradeMonitor:
    """فئة لمراقبة الصفقات وتحديث الأسعار"""
    
    def __init__(self, trading_bot):
        self.trading_bot = trading_bot
        self.is_running = False
        self.update_interval = 5  # تحديث كل 5 ثواني
    
    async def start_monitoring(self):
        """بدء مراقبة الصفقات"""
        self.is_running = True
        while self.is_running:
            try:
                await self.update_positions()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"خطأ في مراقبة الصفقات: {e}")
                await asyncio.sleep(5)  # انتظار قبل المحاولة مرة أخرى
    
    def stop_monitoring(self):
        """إيقاف مراقبة الصفقات"""
        self.is_running = False
    
    async def update_positions(self):
        """تحديث أسعار الصفقات وفحص TP/SL"""
        try:
            # الحصول على جميع الصفقات النشطة
            active_positions = self.trading_bot.trade_manager.get_active_positions()
            if not active_positions:
                return
            
            # تجميع الرموز الفريدة
            symbols = set(pos['symbol'] for pos in active_positions.values())
            
            # الحصول على الأسعار الحالية
            prices = {}
            for symbol in symbols:
                if self.trading_bot.bybit_api:
                    # تحديد نوع السوق المناسب لكل رمز
                    category = "linear"  # أو "spot" حسب نوع الرمز
                    price = await self.trading_bot.bybit_api.get_ticker_price(symbol, category)
                    if price:
                        prices[symbol] = price
            
            if not prices:
                return
            
            # تحديث الصفقات وفحص TP/SL
            events = self.trading_bot.trade_manager.update_prices(prices)
            
            # معالجة الأحداث
            for event in events:
                position_id = event.get('position_id')
                event_type = event.get('type')
                
                if not position_id or not event_type:
                    continue
                
                position_info = self.trading_bot.trade_manager.get_position_status(position_id)
                if not position_info:
                    continue
                
                if event_type == 'take_profit':
                    # إغلاق الصفقة عند الوصول لهدف الربح
                    await self.handle_take_profit(position_id, position_info, event)
                
                elif event_type == 'stop_loss':
                    # إغلاق الصفقة عند ضرب وقف الخسارة
                    await self.handle_stop_loss(position_id, position_info, event)
                
                elif event_type == 'trailing_stop_update':
                    # تحديث مستوى Trailing Stop
                    await self.handle_trailing_stop_update(position_id, position_info, event)
                
                elif event_type == 'partial_close':
                    # تنفيذ الإغلاق الجزئي
                    await self.handle_partial_close(position_id, position_info, event)
        
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقات: {e}")
    
    async def handle_take_profit(self, position_id: str, position_info: Dict, event: Dict):
        """معالجة الوصول لهدف الربح"""
        try:
            # إغلاق الصفقة
            close_result = self.trading_bot.trade_manager.close_position(
                position_id=position_id,
                price=event['price']
            )
            
            if close_result['success']:
                # إرسال إشعار
                await self.trading_bot.trade_notifications.send_trade_close_notification(
                    position_info=position_info,
                    close_type='take_profit'
                )
        except Exception as e:
            logger.error(f"خطأ في معالجة Take Profit: {e}")
    
    async def handle_stop_loss(self, position_id: str, position_info: Dict, event: Dict):
        """معالجة ضرب وقف الخسارة"""
        try:
            # إغلاق الصفقة
            close_result = self.trading_bot.trade_manager.close_position(
                position_id=position_id,
                price=event['price']
            )
            
            if close_result['success']:
                # إرسال إشعار
                await self.trading_bot.trade_notifications.send_trade_close_notification(
                    position_info=position_info,
                    close_type='stop_loss'
                )
        except Exception as e:
            logger.error(f"خطأ في معالجة Stop Loss: {e}")
    
    async def handle_trailing_stop_update(self, position_id: str, position_info: Dict, event: Dict):
        """معالجة تحديث Trailing Stop"""
        try:
            # إرسال إشعار بالتحديث
            await self.trading_bot.trade_notifications.send_trade_update_notification(
                position_info=position_info,
                update_type='trailing_stop_update',
                details={
                    'new_stop': event['new_stop'],
                    'price': event['price']
                }
            )
        except Exception as e:
            logger.error(f"خطأ في معالجة تحديث Trailing Stop: {e}")
    
    async def handle_partial_close(self, position_id: str, position_info: Dict, event: Dict):
        """معالجة الإغلاق الجزئي"""
        try:
            # تنفيذ الإغلاق الجزئي
            close_result = self.trading_bot.trade_manager.partial_close(
                position_id=position_id,
                price=event['price'],
                close_percent=event['percent']
            )
            
            if close_result['success']:
                # إرسال إشعار
                await self.trading_bot.trade_notifications.send_trade_update_notification(
                    position_info=position_info,
                    update_type='partial_close',
                    details=close_result['close_record']
                )
        except Exception as e:
            logger.error(f"خطأ في معالجة الإغلاق الجزئي: {e}")