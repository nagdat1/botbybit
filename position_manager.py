#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الصفقات - إدارة TP/SL للحسابات الحقيقية
"""

import logging
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class PositionManager:
    """إدارة الصفقات المفتوحة مع TP/SL"""
    
    @staticmethod
    async def show_position_controls(update: Update, context: ContextTypes.DEFAULT_TYPE, position_id: str):
        """عرض أدوات التحكم بالصفقة"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        from user_manager import user_manager
        user_data = user_manager.get_user(user_id)
        
        account_type = user_data.get('account_type', 'demo')
        exchange = user_data.get('exchange', 'bybit')
        
        # جلب معلومات الصفقة
        from real_account_manager import real_account_manager
        
        if account_type == 'real':
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                await query.answer(" الحساب غير مهيأ")
                return
            
            # جلب الصفقات المفتوحة
            market_type = user_data.get('market_type', 'spot')
            category = 'linear' if market_type == 'futures' else 'spot'
            
            positions = real_account.get_open_positions(category)
            position = next((p for p in positions if f"real_{p['symbol']}" in position_id), None)
            
            if not position:
                await query.answer(" الصفقة غير موجودة")
                return
            
            # بناء لوحة التحكم
            keyboard = [
                [InlineKeyboardButton(" تعيين TP", callback_data=f"set_tp_{position['symbol']}")],
                [InlineKeyboardButton("🛡️ تعيين SL", callback_data=f"set_sl_{position['symbol']}")],
                [InlineKeyboardButton(" تعيين TP/SL معاً", callback_data=f"set_tpsl_{position['symbol']}")],
                [InlineKeyboardButton(" إغلاق الصفقة", callback_data=f"close_position_{position['symbol']}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="open_positions")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # معلومات الصفقة
            pnl = position.get('unrealized_pnl', 0)
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"
            
            message = f"""
 **إدارة الصفقة**

💎 **الرمز:** {position['symbol']}
 **الاتجاه:** {position['side']}
 **الحجم:** {position['size']}
💵 **سعر الدخول:** ${position['entry_price']:,.2f}
 **السعر الحالي:** ${position['mark_price']:,.2f}
{pnl_emoji} **الربح/الخسارة:** ${pnl:,.2f}

 **Take Profit:** {f"${position['take_profit']:,.2f}" if position.get('take_profit') else "غير محدد"}
🛡️ **Stop Loss:** {f"${position['stop_loss']:,.2f}" if position.get('stop_loss') else "غير محدد"}

⚡ **المنصة:** {exchange.upper()} (حقيقي)
            """
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.answer(" هذه الميزة متاحة للحسابات الحقيقية فقط")
    
    @staticmethod
    async def set_take_profit(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """تعيين Take Profit"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # حفظ الرمز في السياق
        context.user_data['pending_tp_symbol'] = symbol
        context.user_data['awaiting_tp_price'] = True
        
        await query.edit_message_text(
            f" **تعيين Take Profit لـ {symbol}**\n\n"
            f"أرسل السعر المستهدف:\n"
            f"مثال: 50000\n\n"
            f"أو اضغط /cancel للإلغاء",
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def set_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """تعيين Stop Loss"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # حفظ الرمز في السياق
        context.user_data['pending_sl_symbol'] = symbol
        context.user_data['awaiting_sl_price'] = True
        
        await query.edit_message_text(
            f"🛡️ **تعيين Stop Loss لـ {symbol}**\n\n"
            f"أرسل سعر وقف الخسارة:\n"
            f"مثال: 45000\n\n"
            f"أو اضغط /cancel للإلغاء",
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def apply_tp_sl(user_id: int, symbol: str, take_profit: float = None, stop_loss: float = None) -> bool:
        """تطبيق TP/SL على الصفقة الحقيقية"""
        try:
            from user_manager import user_manager
            from real_account_manager import real_account_manager
            
            user_data = user_manager.get_user(user_id)
            account_type = user_data.get('account_type', 'demo')
            
            if account_type != 'real':
                return False
            
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                return False
            
            # تطبيق TP/SL على المنصة
            market_type = user_data.get('market_type', 'spot')
            category = 'linear' if market_type == 'futures' else 'spot'
            
            # تحديد position_idx (0 للـ one-way mode)
            position_idx = 0
            
            result = real_account.set_trading_stop(
                category=category,
                symbol=symbol,
                position_idx=position_idx,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
            
            if result:
                logger.info(f" تم تطبيق TP/SL على {symbol} للمستخدم {user_id}")
                return True
            else:
                logger.error(f" فشل تطبيق TP/SL على {symbol}")
                return False
                
        except Exception as e:
            logger.error(f" خطأ في تطبيق TP/SL: {e}")
            return False
    
    @staticmethod
    async def close_position(user_id: int, symbol: str) -> bool:
        """إغلاق صفقة على المنصة الحقيقية"""
        try:
            from user_manager import user_manager
            from real_account_manager import real_account_manager
            
            user_data = user_manager.get_user(user_id)
            account_type = user_data.get('account_type', 'demo')
            
            if account_type != 'real':
                return False
            
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                return False
            
            # إغلاق الصفقة
            market_type = user_data.get('market_type', 'spot')
            category = 'linear' if market_type == 'futures' else 'spot'
            
            # الحصول على معلومات الصفقة لمعرفة الجهة
            positions = real_account.get_open_positions(category)
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                return False
            
            result = real_account.close_position(category, symbol, position['side'])
            
            if result:
                logger.info(f" تم إغلاق صفقة {symbol} للمستخدم {user_id}")
                return True
            else:
                logger.error(f" فشل إغلاق صفقة {symbol}")
                return False
                
        except Exception as e:
            logger.error(f" خطأ في إغلاق الصفقة: {e}")
            return False


# مثيل عام
position_manager = PositionManager()

