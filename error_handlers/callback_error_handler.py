#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج أخطاء الأزرار Callback Errors Handler
يعالج جميع الأخطاء في الأزرار ويعرض رسائل واضحة للمستخدم
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class UnknownCommandHandler:
    """معالج للأوامر غير المعروفة"""
    
    @staticmethod
    async def handle_unknown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """معالجة أمر غير مدعوم"""
        query = update.callback_query
        user_id = update.effective_user.id if update.effective_user else None
        
        logger.warning(f"⚠️ أمر غير مدعوم: {callback_data} من المستخدم {user_id}")
        
        # إنشاء رسالة خطأ واضحة
        message = f"""
⚠️ **أمر غير مدعوم**

❌ `{callback_data}`

📝 **هذا الأمر غير متاح حالياً**
🔧 قد يكون:
• ميزة قيد التطوير
• تم إزالتها من الإصدار الحالي
• غير مدعوم في هذا السياق

💡 **يمكنك:**
• الرجوع للقائمة الرئيسية
• التحقق من الإعدادات
• تجربة أوامر أخرى

🆘 **للحصول على المساعدة:**
اضغط على /start للحصول على القائمة الرئيسية
"""
        
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
            [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"❌ فشل عرض رسالة الخطأ: {e}")
            try:
                await query.answer("⚠️ أمر غير مدعوم")
            except:
                pass


async def handle_callback_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception, callback_data: str = ""):
    """معالج الأخطاء الشامل للـ callbacks"""
    logger.error(f"❌ خطأ في معالجة callback: {callback_data or update.callback_query.data if update.callback_query else 'unknown'}")
    logger.error(f"📋 الخطأ الكامل: {str(error)}")
    logger.error(f"📊 نوع الخطأ: {type(error).__name__}")
    
    # طباعة تفاصيل الخطأ
    import traceback
    logger.error(f"📝 Traceback:\n{traceback.format_exc()}")
    
    query = update.callback_query
    user_id = update.effective_user.id if update.effective_user else None
    
    # إنشاء رسالة خطأ واضحة
    error_type = type(error).__name__
    error_message = str(error)
    
    # رسائل خطأ مخصصة حسب نوع الخطأ
    if "ImportError" in error_type or "ModuleNotFoundError" in error_type:
        user_message = """
❌ **خطأ في تحميل المكونات**

⚠️ **المشكلة:** عطل في استيراد المكتبات

🔧 **الحل:**
• تحقق من تثبيت جميع المتطلبات
• أعد تشغيل البوت
• تحقق من السجلات للحصول على تفاصيل أكثر
"""
    elif "ConnectionError" in error_type or "Timeout" in error_message:
        user_message = """
❌ **خطأ في الاتصال**

⚠️ **المشكلة:** فشل الاتصال بالخادم

🔧 **الحل:**
• تحقق من اتصالك بالإنترنت
• انتظر قليلاً ثم حاول مرة أخرى
• إذا استمرت المشكلة، تواصل مع الدعم
"""
    elif "KeyError" in error_type or "AttributeError" in error_type:
        user_message = """
❌ **خطأ في البيانات**

⚠️ **المشكلة:** البيانات المطلوبة غير متوفرة

🔧 **الحل:**
• حاول إعادة الإعدادات
• تحقق من البيانات المحفوظة
• أعد تشغيل البوت
"""
    else:
        user_message = f"""
❌ **حدث خطأ غير متوقع**

⚠️ **تفاصيل الخطأ:**
`{error_type}: {error_message[:100]}`

🔧 **ماذا يمكنك فعله:**
• حاول مرة أخرى بعد قليل
• تحقق من اتصالك بالإنترنت
• تواصل مع الدعم إذا استمرت المشكلة

📝 **لمعرفة المزيد:** راجع السجلات
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 حاول مرة أخرى", callback_data="settings")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            user_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"❌ فشل عرض رسالة الخطأ: {e}")
        try:
            await query.answer("❌ حدث خطأ")
        except:
            pass


async def handle_general_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    """معالج الأخطاء العام للبوت"""
    logger.error(f"❌ خطأ عام في البوت: {str(error)}")
    logger.error(f"📊 نوع الخطأ: {type(error).__name__}")
    
    # طباعة تفاصيل الخطأ
    import traceback
    logger.error(f"📝 Traceback:\n{traceback.format_exc()}")
    
    # إرسال رسالة للمستخدم
    try:
        if update.message:
            await update.message.reply_text(
                "❌ حدث خطأ غير متوقع\n\n"
                "🔧 يرجى المحاولة مرة أخرى بعد قليل",
                parse_mode='Markdown'
            )
        elif update.callback_query:
            await update.callback_query.answer("❌ حدث خطأ")
    except Exception as e:
        logger.error(f"❌ فشل إرسال رسالة الخطأ: {e}")

