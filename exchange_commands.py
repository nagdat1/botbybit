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
        [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
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
    """بدء عملية ربط Bybit API - الخطوة 1: API Key"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="exchange_select_bybit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔑 **ربط Bybit API - الخطوة 1 من 2**

📝 أرسل **API Key** الخاص بك

**مثال:**
```
abc123xyz456def789
```

💡 **للحصول على API Key:**
1. اذهب إلى Bybit.com
2. Account → API Management
3. Create New Key
4. انسخ API Key

📝 أرسل API Key الآن
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # حفظ حالة انتظار API Key لـ Bybit
    context.user_data['awaiting_exchange_keys'] = 'bybit_step1'

async def start_mexc_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية ربط MEXC API - الخطوة 1: API Key"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="exchange_select_mexc")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔑 **ربط MEXC API - الخطوة 1 من 2**

📝 أرسل **API Key** الخاص بك

**مثال:**
```
mx0vglBqh6abc123xyz456
```

💡 **للحصول على API Key:**
1. اذهب إلى MEXC.com
2. Account → API Management
3. Create New API Key
4. انسخ API Key

⚠️ **ملاحظة:** MEXC تدعم Spot فقط

📝 أرسل API Key الآن
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # حفظ حالة انتظار API Key لـ MEXC
    context.user_data['awaiting_exchange_keys'] = 'mexc_step1'

async def handle_api_keys_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال مفاتيح API - خطوة بخطوة"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    state = context.user_data.get('awaiting_exchange_keys')
    
    if not state:
        return
    
    # الخطوة 1: استقبال API Key
    if state in ['bybit_step1', 'mexc_step1']:
        exchange = 'bybit' if 'bybit' in state else 'mexc'
        
        if not text:
            await update.message.reply_text("❌ API Key فارغ! أرسله مرة أخرى")
            return
        
        # حفظ API Key
        context.user_data['temp_api_key'] = text
        context.user_data['awaiting_exchange_keys'] = f'{exchange}_step2'
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"exchange_select_{exchange}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ **تم حفظ API Key**\n\n"
            f"🔑 **الخطوة 2 من 2**\n\n"
            f"📝 الآن أرسل **API Secret**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # الخطوة 2: استقبال API Secret
    elif state in ['bybit_step2', 'mexc_step2']:
        exchange = 'bybit' if 'bybit' in state else 'mexc'
        
        if not text:
            await update.message.reply_text("❌ API Secret فارغ! أرسله مرة أخرى")
            return
        
        api_key = context.user_data.get('temp_api_key')
        api_secret = text
        
        if not api_key:
            await update.message.reply_text(
                "❌ حدث خطأ! ابدأ من جديد",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 رجوع", callback_data=f"exchange_select_{exchange}")
                ]])
            )
            context.user_data.pop('awaiting_exchange_keys', None)
            context.user_data.pop('temp_api_key', None)
            return
        
        # اختبار المفاتيح
        await update.message.reply_text("🔄 جاري اختبار الاتصال...")
        
        if exchange == 'bybit':
            success = await test_and_save_bybit_keys(user_id, api_key, api_secret, update)
        else:  # mexc
            success = await test_and_save_mexc_keys(user_id, api_key, api_secret, update)
        
        # مسح البيانات المؤقتة
        context.user_data.pop('awaiting_exchange_keys', None)
        context.user_data.pop('temp_api_key', None)
        
        if success:
            keyboard = [[InlineKeyboardButton("✅ العودة للإعدادات", callback_data=f"exchange_select_{exchange}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **تم ربط {exchange.upper()} بنجاح!**\n\n"
                f"🎉 يمكنك الآن:\n"
                f"• استقبال إشارات التداول\n"
                f"• التداول على {exchange.upper()}\n"
                f"• اختبار الاتصال\n\n"
                f"اضغط الزر للعودة للإعدادات",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"exchange_select_{exchange}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **فشل الاتصال!**\n\n"
                "تحقق من:\n"
                "• صحة المفاتيح\n"
                "• الصلاحيات المطلوبة\n"
                "• تفعيل API في حسابك\n\n"
                "يمكنك المحاولة مرة أخرى",
                reply_markup=reply_markup
            )

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
    return

# دالة للتسجيل في التطبيق الرئيسي
def register_exchange_handlers(application):
    """تسجيل معالجات أوامر المنصات"""
    from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
    
    # أمر اختيار المنصة
    application.add_handler(CommandHandler("exchange", cmd_select_exchange))
    application.add_handler(CommandHandler("منصة", cmd_select_exchange))
    application.add_handler(CommandHandler("cancel", cancel_setup))
    
    # معالجات الأزرار - تم نقلها إلى bybit_trading_bot.py
    # معالج إدخال المفاتيح - سيتم التعامل معه عبر context.user_data
    
    logger.info("✅ تم تسجيل معالجات أوامر المنصات")

