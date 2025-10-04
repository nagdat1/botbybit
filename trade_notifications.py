# -*- coding: utf-8 -*-
"""
نظام الإشعارات للصفقات
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class TradeNotifications:
    """نظام إشعارات الصفقات"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send_trade_notification(self, message: str) -> bool:
        """إرسال إشعار صفقة"""
        try:
            # استخدام البوت الموجود بدلاً من إنشاء واحد جديد
            from bybit_trading_bot import trading_bot
            await trading_bot.send_message_to_admin(message)
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الصفقة: {e}")
            return False
    
    async def send_trade_opened(self, trade_info: Dict) -> bool:
        """إشعار فتح صفقة جديدة"""
        try:
            symbol = trade_info['symbol']
            side = trade_info['side']
            entry_price = trade_info['entry_price']
            quantity = trade_info['quantity']
            
            side_emoji = "🟢" if side.upper() == 'BUY' else "🔴"
            side_text = "شراء" if side.upper() == 'BUY' else "بيع"
            
            message = f"""🚀 صفقة جديدة مفتوحة!

{side_emoji} **{symbol}** - {side_text}
💰 سعر الدخول: `{entry_price:.6f}`
📊 الكمية: `{quantity:.6f}`
⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`

📈 يمكنك الآن إدارة الصفقة من قائمة "الصفقات المفتوحة"
"""
            
            return await self.send_trade_notification(message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار فتح الصفقة: {e}")
            return False
    
    async def send_tp_executed(self, trade_id: str, percentage: float, trade_info: Dict) -> bool:
        """إشعار تنفيذ هدف الربح"""
        try:
            symbol = trade_info['symbol']
            price = trade_info['current_price']
            pnl = trade_info['pnl']
            
            message = f"""✅ تم تنفيذ هدف الربح!

📊 **{symbol}**
🎯 TP: `{percentage}%`
💰 السعر: `{price:.6f}`
💵 الربح: `{pnl:.2f} USDT`
⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`

🔄 الصفقة لا تزال مفتوحة للجزء المتبقي
"""
            
            return await self.send_trade_notification(message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار TP: {e}")
            return False
    
    async def send_sl_executed(self, trade_id: str, percentage: float, trade_info: Dict) -> bool:
        """إشعار تنفيذ وقف الخسارة"""
        try:
            symbol = trade_info['symbol']
            price = trade_info['current_price']
            pnl = trade_info['pnl']
            
            message = f"""⚠️ تم تنفيذ وقف الخسارة!

📊 **{symbol}**
🛑 SL: `{percentage}%`
💰 السعر: `{price:.6f}`
💸 الخسارة: `{pnl:.2f} USDT`
⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`

🔒 تم إغلاق الصفقة بالكامل
"""
            
            return await self.send_trade_notification(message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار SL: {e}")
            return False
    
    async def send_partial_close_executed(self, trade_id: str, percentage: float, trade_info: Dict) -> bool:
        """إشعار تنفيذ الإغلاق الجزئي"""
        try:
            symbol = trade_info['symbol']
            price = trade_info['current_price']
            pnl = trade_info['pnl']
            
            message = f"""✂️ تم تنفيذ الإغلاق الجزئي!

📊 **{symbol}**
📉 الإغلاق: `{percentage}%`
💰 السعر: `{price:.6f}`
💵 الربح/الخسارة: `{pnl:.2f} USDT`
⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`

🔄 الصفقة لا تزال مفتوحة للجزء المتبقي
"""
            
            return await self.send_trade_notification(message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الإغلاق الجزئي: {e}")
            return False
    
    async def send_trade_closed(self, trade_id: str, trade_info: Dict) -> bool:
        """إشعار إغلاق الصفقة بالكامل"""
        try:
            symbol = trade_info['symbol']
            price = trade_info['current_price']
            pnl = trade_info['pnl']
            
            message = f"""🔒 تم إغلاق الصفقة بالكامل!

📊 **{symbol}**
💰 السعر النهائي: `{price:.6f}`
💵 الربح/الخسارة النهائي: `{pnl:.2f} USDT`
⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`

✅ الصفقة مكتملة
"""
            
            return await self.send_trade_notification(message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار إغلاق الصفقة: {e}")
            return False