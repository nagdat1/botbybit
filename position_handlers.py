from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def handle_position_buttons(trading_bot, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على أزرار التحكم بالصفقة"""
    query = update.callback_query
    if not query:
        return

    try:
        # تحليل بيانات الزر
        data = query.data.split('_')
        if len(data) != 3:
            await query.answer("⚠️ خطأ في البيانات")
            return

        action, position_id, percent = data
        percent = float(percent)

        # التحقق من وجود الصفقة
        position = trading_bot.open_positions.get(position_id)
        if not position:
            await query.answer("❌ الصفقة غير موجودة")
            return

        entry_price = position['entry_price']
        side = position['side']
        current_price = position.get('current_price', entry_price)

        if action == 'tp':
            # حساب هدف الربح
            target_price = entry_price * (1 + percent/100) if side.lower() == 'buy' else entry_price * (1 - percent/100)
            await trading_bot.update_tp_sl(position_id, take_profit=target_price)
            await query.answer(f"✅ تم تحديد هدف الربح: {target_price:.2f} ({percent}%)")

        elif action == 'sl':
            # حساب وقف الخسارة
            stop_price = entry_price * (1 - percent/100) if side.lower() == 'buy' else entry_price * (1 + percent/100)
            await trading_bot.update_tp_sl(position_id, stop_loss=stop_price)
            await query.answer(f"✅ تم تحديد وقف الخسارة: {stop_price:.2f} ({percent}%)")

        elif action == 'close':
            if percent == 100:
                # إغلاق كامل
                await trading_bot.close_position(position_id, current_price)
                await query.answer("✅ تم إغلاق الصفقة بالكامل")
            else:
                # إغلاق جزئي
                close_amount = position['quantity'] * (percent/100)
                await trading_bot.partial_close_position(position_id, close_amount, current_price)
                await query.answer(f"✅ تم إغلاق {percent}% من الصفقة")

        # تحديث عرض الصفقات
        await trading_bot.update_open_positions(update, context)

    except Exception as e:
        logger.error(f"خطأ في معالجة الزر: {e}")
        await query.answer("❌ حدث خطأ في المعالجة")

async def update_position_message(trading_bot, message_id: int, position_id: str):
    """تحديث رسالة عرض الصفقة"""
    try:
        position = trading_bot.open_positions.get(position_id)
        if not position:
            return

        # تحديث معلومات الصفقة
        text = generate_position_info(position)
        markup = generate_position_keyboard(position)

        await message_id.edit_text(text, reply_markup=markup)

    except Exception as e:
        logger.error(f"خطأ في تحديث رسالة الصفقة: {e}")

def generate_position_info(position: dict) -> str:
    """إنشاء نص معلومات الصفقة"""
    symbol = position['symbol']
    side = position['side'].upper()
    entry_price = position['entry_price']
    current_price = position.get('current_price', entry_price)
    pnl = position.get('unrealized_pnl', 0)
    
    text = f"""
💱 الرمز: {symbol}
📊 النوع: {side}
💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الربح/الخسارة: {pnl:+.2f}
"""
    
    # إضافة معلومات TP/SL إذا وجدت
    if position.get('take_profit'):
        text += f"💎 هدف الربح: {position['take_profit']:.6f}\n"
    if position.get('stop_loss'):
        text += f"🛑 وقف الخسارة: {position['stop_loss']:.6f}\n"
    
    return text