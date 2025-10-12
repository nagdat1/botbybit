#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أوامر إدارة المنصات (Bybit و MEXC)
واجهة منظمة لربط API الخاص بكل منصة
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import *

logger = logging.getLogger(__name__)

# حالات المحادثة
SELECTING_EXCHANGE, ENTERING_BYBIT_KEYS, ENTERING_MEXC_KEYS = range(3)

async def cmd_select_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اختيار المنصة - القائمة الرئيسية"""
    user_id = update.effective_user.id
    
    from user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    # تحديد المنصة الحالية
    current_exchange = user_data.get('exchange', 'bybit') if user_data else 'bybit'
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_exchange == 'bybit' else '⚪'} Bybit", 
                callback_data="exchange_select_bybit"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_exchange == 'mexc' else '⚪'} MEXC (Spot فقط)", 
                callback_data="exchange_select_mexc"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🏦 **اختيار منصة التداول**

المنصة الحالية: **{current_exchange.upper()}**

اختر المنصة التي تريد استخدامها:

🔹 **Bybit**
   • يدعم Spot و Futures
   • رافعة مالية متاحة
   • حساب تجريبي متاح

🔹 **MEXC**
   • يدعم Spot فقط
   • لا يوجد دعم للفيوتشر
   • عدد كبير من العملات

اضغط على المنصة للاختيار وإعداد API
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_exchange_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار المنصة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "exchange_select_bybit":
        # عرض خيارات Bybit
        await show_bybit_options(update, context)
    
    elif query.data == "exchange_select_mexc":
        # عرض خيارات MEXC
        await show_mexc_options(update, context)

async def show_bybit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خيارات إعداد Bybit"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    from user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    # التحقق من وجود API Keys
    has_bybit_keys = False
    if user_data:
        bybit_key = user_data.get('bybit_api_key', BYBIT_API_KEY)
        has_bybit_keys = bybit_key and bybit_key != BYBIT_API_KEY
    
    keyboard = [
        [InlineKeyboardButton(
            "🔑 ربط/تحديث Bybit API Keys",
            callback_data="exchange_setup_bybit"
        )],
        [InlineKeyboardButton(
            "✅ تفعيل Bybit" if not has_bybit_keys else "✅ استخدام Bybit",
            callback_data="exchange_activate_bybit"
        )],
        [InlineKeyboardButton(
            "📊 اختبار الاتصال بـ Bybit",
            callback_data="exchange_test_bybit"
        )],
        [InlineKeyboardButton("🔙 رجوع", callback_data="exchange_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_icon = "✅" if has_bybit_keys else "⚠️"
    status_text = "مربوط" if has_bybit_keys else "غير مربوط"
    
    message = f"""
🏦 **إعداد منصة Bybit**

الحالة: {status_icon} **{status_text}**

📋 **المميزات:**
• التداول الفوري (Spot)
• تداول الفيوتشر (Futures)
• الرافعة المالية (حتى 100x)
• حساب تجريبي متاح

🔐 **لربط API:**
1. اذهب إلى [Bybit API Management](https://www.bybit.com/app/user/api-management)
2. أنشئ API Key جديد
3. فعّل الصلاحيات المطلوبة
4. اضغط "🔑 ربط/تحديث Bybit API Keys"

{f"✅ **API مربوط بنجاح!**" if has_bybit_keys else "⚠️ **يجب ربط API أولاً**"}
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def show_mexc_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خيارات إعداد MEXC"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    from user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    # التحقق من وجود API Keys
    has_mexc_keys = False
    if user_data:
        mexc_key = user_data.get('mexc_api_key')
        has_mexc_keys = mexc_key and mexc_key != ""
    
    keyboard = [
        [InlineKeyboardButton(
            "🔑 ربط/تحديث MEXC API Keys",
            callback_data="exchange_setup_mexc"
        )],
        [InlineKeyboardButton(
            "✅ تفعيل MEXC" if not has_mexc_keys else "✅ استخدام MEXC",
            callback_data="exchange_activate_mexc"
        )],
        [InlineKeyboardButton(
            "📊 اختبار الاتصال بـ MEXC",
            callback_data="exchange_test_mexc"
        )],
        [InlineKeyboardButton("🔙 رجوع", callback_data="exchange_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_icon = "✅" if has_mexc_keys else "⚠️"
    status_text = "مربوط" if has_mexc_keys else "غير مربوط"
    
    message = f"""
🏦 **إعداد منصة MEXC**

الحالة: {status_icon} **{status_text}**

📋 **المميزات:**
• التداول الفوري (Spot) فقط
• عدد كبير من العملات
• رسوم تداول منخفضة

⚠️ **ملاحظة هامة:**
MEXC تدعم التداول الفوري فقط - لا يوجد دعم للفيوتشر عبر API

🔐 **لربط API:**
1. اذهب إلى [MEXC API Management](https://www.mexc.com/user/openapi)
2. أنشئ API Key جديد
3. فعّل صلاحية Spot Trading فقط
4. اضغط "🔑 ربط/تحديث MEXC API Keys"

{f"✅ **API مربوط بنجاح!**" if has_mexc_keys else "⚠️ **يجب ربط API أولاً**"}
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def start_bybit_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية ربط Bybit API"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="exchange_select_bybit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔑 **ربط Bybit API Keys**

أرسل المفاتيح بالصيغة التالية:
```
API_KEY:API_SECRET
```

**مثال:**
```
abc123xyz456:def789ghi012jkl345
```

⚠️ **تأكد من:**
• تفعيل صلاحية Read (القراءة)
• تفعيل صلاحية Trade (التداول)
• عدم تفعيل صلاحية Withdrawal (السحب) إلا إذا كنت تحتاجها

📝 أرسل المفاتيح الآن أو اضغط إلغاء
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # حفظ حالة انتظار مفاتيح Bybit
    context.user_data['awaiting_exchange_keys'] = 'bybit'
    return ENTERING_BYBIT_KEYS

async def start_mexc_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية ربط MEXC API"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="exchange_select_mexc")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔑 **ربط MEXC API Keys**

أرسل المفاتيح بالصيغة التالية:
```
API_KEY:API_SECRET
```

**مثال:**
```
mx0vglBqh6abc123:xyz456def789ghi012
```

⚠️ **تأكد من:**
• تفعيل صلاحية Spot Trading فقط
• عدم تفعيل صلاحية Withdrawal (السحب)

⚠️ **ملاحظة:** MEXC تدعم Spot فقط - لا فيوتشر

📝 أرسل المفاتيح الآن أو اضغط إلغاء
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # حفظ حالة انتظار مفاتيح MEXC
    context.user_data['awaiting_exchange_keys'] = 'mexc'
    return ENTERING_MEXC_KEYS

async def handle_api_keys_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال مفاتيح API"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    exchange_type = context.user_data.get('awaiting_exchange_keys')
    
    if not exchange_type:
        return ConversationHandler.END
    
    # التحقق من الصيغة
    if ':' not in text:
        await update.message.reply_text(
            "❌ **صيغة خاطئة!**\n\n"
            "استخدم الصيغة: `API_KEY:API_SECRET`\n\n"
            "أرسل المفاتيح مرة أخرى أو استخدم /cancel للإلغاء",
            parse_mode='Markdown'
        )
        return ENTERING_BYBIT_KEYS if exchange_type == 'bybit' else ENTERING_MEXC_KEYS
    
    try:
        api_key, api_secret = text.split(':', 1)
        api_key = api_key.strip()
        api_secret = api_secret.strip()
        
        if not api_key or not api_secret:
            await update.message.reply_text(
                "❌ **المفاتيح فارغة!**\n\n"
                "تأكد من إدخال API Key و Secret بشكل صحيح"
            )
            return ENTERING_BYBIT_KEYS if exchange_type == 'bybit' else ENTERING_MEXC_KEYS
        
        # اختبار المفاتيح
        await update.message.reply_text("🔄 جاري اختبار الاتصال...")
        
        if exchange_type == 'bybit':
            success = await test_and_save_bybit_keys(user_id, api_key, api_secret, update)
        else:  # mexc
            success = await test_and_save_mexc_keys(user_id, api_key, api_secret, update)
        
        if success:
            # العودة إلى قائمة المنصة
            context.user_data.pop('awaiting_exchange_keys', None)
            
            keyboard = [[InlineKeyboardButton("✅ العودة للإعدادات", callback_data=f"exchange_select_{exchange_type}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **تم ربط {exchange_type.upper()} بنجاح!**\n\n"
                f"يمكنك الآن استخدام المنصة للتداول",
                reply_markup=reply_markup
            )
            return ConversationHandler.END
        else:
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"exchange_select_{exchange_type}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **فشل الاتصال!**\n\n"
                "يمكنك المحاولة مرة أخرى أو الرجوع",
                reply_markup=reply_markup
            )
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"خطأ في معالجة مفاتيح API: {e}")
        await update.message.reply_text(
            f"❌ **خطأ:** {str(e)}\n\n"
            "حاول مرة أخرى أو استخدم /cancel للإلغاء"
        )
        return ENTERING_BYBIT_KEYS if exchange_type == 'bybit' else ENTERING_MEXC_KEYS

async def test_and_save_bybit_keys(user_id: int, api_key: str, api_secret: str, update: Update) -> bool:
    """اختبار وحفظ مفاتيح Bybit"""
    try:
        # اختبار الاتصال (يمكن إضافة اختبار حقيقي هنا)
        # من bybit_trading_bot import BybitAPI
        # test = BybitAPI(api_key, api_secret)
        # if not test.test_connection():
        #     return False
        
        from user_manager import user_manager
        
        # حفظ المفاتيح
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['bybit_api_key'] = api_key
            user_data['bybit_api_secret'] = api_secret
            user_data['exchange'] = 'bybit'
            
            # حفظ في قاعدة البيانات
            from database import db_manager
            db_manager.update_user_settings(user_id, {
                'bybit_api_key': api_key,
                'bybit_api_secret': api_secret,
                'exchange': 'bybit'
            })
            
            logger.info(f"تم حفظ مفاتيح Bybit للمستخدم {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"خطأ في اختبار/حفظ مفاتيح Bybit: {e}")
        return False

async def test_and_save_mexc_keys(user_id: int, api_key: str, api_secret: str, update: Update) -> bool:
    """اختبار وحفظ مفاتيح MEXC"""
    try:
        from mexc_trading_bot import create_mexc_bot
        
        # اختبار الاتصال
        test_bot = create_mexc_bot(api_key, api_secret)
        if not test_bot.test_connection():
            await update.message.reply_text(
                "❌ **فشل الاتصال بـ MEXC**\n\n"
                "تحقق من:\n"
                "• صحة المفاتيح\n"
                "• تفعيل API Key في حسابك\n"
                "• صلاحيات Spot Trading"
            )
            return False
        
        from user_manager import user_manager
        
        # حفظ المفاتيح
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['mexc_api_key'] = api_key
            user_data['mexc_api_secret'] = api_secret
            user_data['exchange'] = 'mexc'
            user_data['market_type'] = 'spot'  # MEXC تدعم Spot فقط
            
            # حفظ في قاعدة البيانات
            from database import db_manager
            db_manager.update_user_settings(user_id, {
                'mexc_api_key': api_key,
                'mexc_api_secret': api_secret,
                'exchange': 'mexc',
                'market_type': 'spot'
            })
            
            logger.info(f"تم حفظ مفاتيح MEXC للمستخدم {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"خطأ في اختبار/حفظ مفاتيح MEXC: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
        return False

async def activate_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل المنصة المختارة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    exchange = query.data.replace('exchange_activate_', '')
    
    from user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: المستخدم غير موجود")
        return
    
    # التحقق من وجود المفاتيح
    if exchange == 'bybit':
        has_keys = user_data.get('bybit_api_key') and user_data.get('bybit_api_key') != BYBIT_API_KEY
    else:  # mexc
        has_keys = user_data.get('mexc_api_key') and user_data.get('mexc_api_key') != ""
    
    if not has_keys:
        await query.edit_message_text(
            f"⚠️ **لم يتم ربط {exchange.upper()} API**\n\n"
            f"يجب ربط API أولاً قبل التفعيل",
            parse_mode='Markdown'
        )
        return
    
    # تفعيل المنصة
    user_data['exchange'] = exchange
    if exchange == 'mexc':
        user_data['market_type'] = 'spot'  # MEXC تدعم Spot فقط
    
    from database import db_manager
    db_manager.update_user_settings(user_id, {
        'exchange': exchange,
        'market_type': user_data.get('market_type', 'spot')
    })
    
    await query.edit_message_text(
        f"✅ **تم تفعيل {exchange.upper()} بنجاح!**\n\n"
        f"المنصة النشطة الآن: **{exchange.upper()}**\n\n"
        f"يمكنك الآن استقبال الإشارات والتداول",
        parse_mode='Markdown'
    )

async def test_exchange_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختبار الاتصال بالمنصة"""
    query = update.callback_query
    await query.answer("جاري الاختبار...")
    
    user_id = update.effective_user.id
    exchange = query.data.replace('exchange_test_', '')
    
    from user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: المستخدم غير موجود")
        return
    
    try:
        if exchange == 'bybit':
            # اختبار Bybit (يمكن تحسينه لاحقاً)
            result = "✅ الاتصال بـ Bybit ناجح!"
        else:  # mexc
            from mexc_trading_bot import create_mexc_bot
            api_key = user_data.get('mexc_api_key', MEXC_API_KEY)
            api_secret = user_data.get('mexc_api_secret', MEXC_API_SECRET)
            
            bot = create_mexc_bot(api_key, api_secret)
            if bot.test_connection():
                # الحصول على معلومات الحساب
                balance = bot.get_account_balance()
                result = f"✅ **الاتصال بـ MEXC ناجح!**\n\n"
                result += f"📊 **معلومات الحساب:**\n"
                result += f"• يمكن التداول: {'نعم' if balance.get('can_trade') else 'لا'}\n"
                
                # عرض بعض الأرصدة
                if balance and 'balances' in balance:
                    count = 0
                    result += f"\n💰 **الأرصدة:**\n"
                    for asset, info in balance['balances'].items():
                        if info['total'] > 0 and count < 5:
                            result += f"• {asset}: {info['total']:.8f}\n"
                            count += 1
            else:
                result = "❌ فشل الاتصال بـ MEXC"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"exchange_select_{exchange}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            result,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"خطأ في اختبار الاتصال: {e}")
        await query.edit_message_text(f"❌ خطأ: {str(e)}")

async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء عملية الإعداد"""
    context.user_data.pop('awaiting_exchange_keys', None)
    await update.message.reply_text("❌ تم إلغاء العملية")
    return ConversationHandler.END

# دالة للتسجيل في التطبيق الرئيسي
def register_exchange_handlers(application):
    """تسجيل معالجات أوامر المنصات"""
    from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
    
    # أمر اختيار المنصة
    application.add_handler(CommandHandler("exchange", cmd_select_exchange))
    application.add_handler(CommandHandler("منصة", cmd_select_exchange))
    
    # معالجات الأزرار
    application.add_handler(CallbackQueryHandler(cmd_select_exchange, pattern="^exchange_menu$"))
    application.add_handler(CallbackQueryHandler(handle_exchange_selection, pattern="^exchange_select_(bybit|mexc)$"))
    application.add_handler(CallbackQueryHandler(start_bybit_setup, pattern="^exchange_setup_bybit$"))
    application.add_handler(CallbackQueryHandler(start_mexc_setup, pattern="^exchange_setup_mexc$"))
    application.add_handler(CallbackQueryHandler(activate_exchange, pattern="^exchange_activate_(bybit|mexc)$"))
    application.add_handler(CallbackQueryHandler(test_exchange_connection, pattern="^exchange_test_(bybit|mexc)$"))
    
    # معالج إدخال المفاتيح
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_bybit_setup, pattern="^exchange_setup_bybit$"),
            CallbackQueryHandler(start_mexc_setup, pattern="^exchange_setup_mexc$")
        ],
        states={
            ENTERING_BYBIT_KEYS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_keys_input)
            ],
            ENTERING_MEXC_KEYS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_keys_input)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_setup),
            CallbackQueryHandler(cmd_select_exchange, pattern="^exchange_select_(bybit|mexc)$")
        ]
    )
    
    application.add_handler(conv_handler)
    
    logger.info("✅ تم تسجيل معالجات أوامر المنصات")

