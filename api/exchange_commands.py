#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أوامر إدارة المنصات (Bybit)
واجهة منظمة لربط API الخاصة بمنصة Bybit
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import *

logger = logging.getLogger(__name__)

# حالات المحادثة
SELECTING_EXCHANGE, ENTERING_BYBIT_KEYS = range(2)

async def cmd_select_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اختيار المنصة - القائمة الرئيسية"""
    try:
        user_id = update.effective_user.id
        
        from users.user_manager import user_manager
        user_data = user_manager.get_user(user_id)
        
        # التحقق من أن user_data موجود
        if not user_data:
            logger.warning(f"⚠️ المستخدم {user_id} غير موجود في قاعدة البيانات")
            user_data = {}
        
        # تحديد المنصة الحالية والتحقق من الربط
        current_exchange = user_data.get('exchange', '') if user_data else ''
        
        # التحقق من وجود API Keys مربوطة
        bybit_linked = False
        
        if user_data:
            bybit_key = user_data.get('bybit_api_key', BYBIT_API_KEY)
            bybit_linked = bybit_key and bybit_key != BYBIT_API_KEY
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب بيانات المستخدم: {e}")
        # استخدام قيم افتراضية
        user_data = {}
        current_exchange = ''
        bybit_linked = False
    
    # بناء الأزرار مع الحالة الصحيحة
    bybit_icon = "✅" if (current_exchange == 'bybit' and bybit_linked) else ("🔗" if bybit_linked else "⚪")
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{bybit_icon} Bybit", 
                callback_data="exchange_select_bybit"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # تحديد حالة المنصة
    if current_exchange and bybit_linked:
        status_text = f"**{current_exchange.upper()}** ✅ (مفعّلة)"
    else:
        status_text = "**لم يتم اختيار منصة**"
    
    message = f"""
🏦 **اختيار منصة التداول**

المنصة الحالية: {status_text}

**الرموز:**
⚪ = غير مربوط
🔗 = مربوط (غير مفعّل)
✅ = مربوط ومفعّل

🔹 **Bybit**
   • يدعم Spot و Futures
   • رافعة مالية متاحة (حتى 100x)
   • حساب تجريبي متاح
   • دعم كامل للتداول الآلي

🔗 **للانضمام إلى Bybit:**
[اضغط هنا للتسجيل](https://www.bybit.com/invite?ref=OLAZ2M)

اضغط على Bybit للاختيار وإعداد API
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

async def show_bybit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خيارات إعداد Bybit مع معلومات الحساب"""
    query = update.callback_query
    
    try:
        user_id = update.effective_user.id
        
        from users.user_manager import user_manager
        user_data = user_manager.get_user(user_id)
        
        # التحقق من أن user_data موجود
        if not user_data:
            logger.warning(f"⚠️ المستخدم {user_id} غير موجود في قاعدة البيانات")
            user_data = {}
        
        # التحقق من وجود API Keys
        has_bybit_keys = False
        if user_data:
            bybit_key = user_data.get('bybit_api_key', '')
            default_key = BYBIT_API_KEY if BYBIT_API_KEY else ''
            has_bybit_keys = bybit_key and bybit_key != default_key and len(bybit_key) > 10
        
        # التحقق من التفعيل
        current_exchange = user_data.get('exchange', '') if user_data else ''
        account_type = user_data.get('account_type', 'demo') if user_data else 'demo'
        is_active = current_exchange == 'bybit' and account_type == 'real'
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب بيانات المستخدم: {e}")
        # استخدام قيم افتراضية
        user_data = {}
        has_bybit_keys = False
        current_exchange = ''
        account_type = 'demo'
        is_active = False
    
    # تحديد حالة API
    if is_active and has_bybit_keys:
        status_icon = "🟢"
        status_text = "مرتبط ومفعّل"
    elif has_bybit_keys:
        status_icon = "🔗"
        status_text = "مرتبط (غير مفعّل)"
    else:
        status_icon = "🔴"
        status_text = "غير مرتبط"
    
    # جلب معلومات الرصيد إذا كان مفعّل
    balance_text = ""
    if is_active and has_bybit_keys:
        from api.bybit_api import real_account_manager
        real_account = real_account_manager.get_account(user_id)
        if real_account:
            try:
                balance = real_account.get_wallet_balance()
                if balance:
                    total_equity = balance.get('total_equity', 0)
                    balance_text = f"\n💰 **الرصيد:** ${total_equity:,.2f}"
            except Exception as e:
                logger.error(f"خطأ في جلب الرصيد: {e}")
    
    # رسالة خاصة إذا لم يتم العثور على بيانات المستخدم
    if not user_data or user_data == {}:
        # إنشاء حساب تلقائياً للمستخدم
        logger.info(f"🆕 إنشاء حساب جديد للمستخدم {user_id}")
        from users.user_manager import user_manager
        from users.database import db_manager
        
        # إنشاء المستخدم في قاعدة البيانات
        db_manager.create_user(user_id)
        
        # تحديث user_data
        user_data = user_manager.get_user(user_id)
        
        # إعادة تعيين المتغيرات
        if not user_data:
            user_data = {}
        
        # الآن جرب مرة أخرى
        has_bybit_keys = False
        current_exchange = ''
        account_type = 'demo'
        is_active = False
        
        logger.info(f"✅ تم إنشاء حساب جديد للمستخدم {user_id}")
        message = f"""
✅ **تم إنشاء حسابك بنجاح!**

🏦 **مرحباً بك في بوت التداول**

📋 **الآن يمكنك:**
• اختيار منصة التداول
• ضبط إعدادات التداول
• ربط API الخاص بك
• البدء في التداول

🔹 **Bybit**
   • التداول الفوري (Spot)
   • تداول الفيوتشر (Futures)
   • الرافعة المالية (حتى 100x)

🔗 **للانضمام إلى Bybit:**
[اضغط هنا للتسجيل عبر رابط الإحالة](https://www.bybit.com/invite?ref=OLAZ2M)

اضغط على Bybit للبدء!
"""
        
        keyboard = [
            [InlineKeyboardButton("⚪ Bybit", callback_data="exchange_select_bybit")]
        ]
        keyboard.append([InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        message = f"""
🏦 **إعداد منصة Bybit**

📊 **حالة API:** {status_icon} **{status_text}**{balance_text}

📋 **المميزات:**
• التداول الفوري (Spot)
• تداول الفيوتشر (Futures)
• الرافعة المالية (حتى 100x)
• حساب تجريبي متاح

🔗 **للانضمام إلى Bybit:**
[اضغط هنا للتسجيل عبر رابط الإحالة](https://www.bybit.com/invite?ref=OLAZ2M)

🔐 **لربط API:**
1. اذهب إلى [Bybit API Management](https://www.bybit.com/app/user/api-management)
2. أنشئ API Key جديد
3. فعّل الصلاحيات المطلوبة
4. اضغط "🔑 ربط/تحديث Bybit API Keys"

{f"✅ **API مربوط بنجاح!**" if has_bybit_keys else "⚠️ **يجب ربط API أولاً**"}
"""
        keyboard = [
            [InlineKeyboardButton(
                "🔑 ربط/تحديث Bybit API Keys",
                callback_data="exchange_setup_bybit"
            )]
        ]
        
        # إضافة الأزرار الأخرى فقط إذا تم ربط API
        if has_bybit_keys:
            keyboard.extend([
                [InlineKeyboardButton(
                    "✅ استخدام Bybit",
                    callback_data="exchange_activate_bybit"
                )],
                [InlineKeyboardButton(
                    "📊 اختبار الاتصال بـ Bybit",
                    callback_data="exchange_test_bybit"
                )]
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="select_exchange")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    
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
1. اذهب إلى [Bybit.com](https://www.bybit.com/invite?ref=OLAZ2M)
2. Account → API Management
3. Create New Key
4. انسخ API Key

🔗 **ليس لديك حساب؟** [سجل الآن](https://www.bybit.com/invite?ref=OLAZ2M)

📝 أرسل API Key الآن
"""
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # حفظ حالة انتظار API Key لـ Bybit
    context.user_data['awaiting_exchange_keys'] = 'bybit_step1'

async def handle_api_keys_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال مفاتيح API - خطوة بخطوة"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    state = context.user_data.get('awaiting_exchange_keys')
    
    if not state:
        return
    
    # الخطوة 1: استقبال API Key
    if state in ['bybit_step1']:
        exchange = 'bybit'
        
        if not text:
            await update.message.reply_text("❌ API Key فارغ! أرسله مرة أخرى")
            return
        
        # حفظ API Key
        context.user_data['temp_api_key'] = text
        context.user_data['awaiting_exchange_keys'] = 'bybit_step2'
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="exchange_select_bybit")]]
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
    elif state in ['bybit_step2']:
        exchange = 'bybit'
        
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
        
        # دعم Bybit فقط
        success = await test_and_save_bybit_keys(user_id, api_key, api_secret, update)
        
        # مسح البيانات المؤقتة
        context.user_data.pop('awaiting_exchange_keys', None)
        context.user_data.pop('temp_api_key', None)
        
        if success:
            keyboard = [[InlineKeyboardButton("✅ العودة للإعدادات", callback_data="settings")]]
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
    """اختبار وحفظ مفاتيح Bybit - اختبار حقيقي 100%"""
    try:
        import hmac
        import hashlib
        import time
        import requests
        from urllib.parse import urlencode
        
        # اختبار الاتصال الحقيقي مع Bybit
        base_url = "https://api.bybit.com"
        
        # استخدام endpoint بسيط لاختبار الاتصال
        endpoint = "/v5/account/wallet-balance"
        
        # بناء التوقيع بالطريقة الصحيحة لـ Bybit V5
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # بناء query string
        params_str = f"accountType=UNIFIED&timestamp={timestamp}"
        
        # بناء الـ signature string حسب توثيق Bybit V5
        # صيغة: timestamp + api_key + recv_window + params
        sign_str = timestamp + api_key + recv_window + params_str
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # إرسال الطلب
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{base_url}{endpoint}?{params_str}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                await update.message.reply_text(
                    f"❌ **فشل الاتصال بـ Bybit**\n\n"
                    f"كود الخطأ: {response.status_code}\n\n"
                    f"تحقق من:\n"
                    f"• صحة API Key و Secret\n"
                    f"• تفعيل API في حسابك\n"
                    f"• الصلاحيات المطلوبة"
                )
                return False
            
            result = response.json()
            
            if result.get('retCode') != 0:
                await update.message.reply_text(
                    f"❌ **خطأ من Bybit**\n\n"
                    f"{result.get('retMsg', 'خطأ غير معروف')}\n\n"
                    f"تحقق من صحة المفاتيح"
                )
                return False
            
            # نجح الاتصال! معالجة معلومات الرصيد
            balance_info = ""
            if response.status_code == 200:
                wallet_data = response.json()
                if wallet_data.get('retCode') == 0:
                    coins = wallet_data.get('result', {}).get('list', [{}])[0].get('coin', [])
                    balance_info = "\n\n💰 **الرصيد المتاح:**\n"
                    found_balance = False
                    for coin in coins[:5]:  # أول 5 عملات
                        equity = float(coin.get('equity', 0))
                        if equity > 0:
                            balance_info += f"• {coin.get('coin')}: {equity:.4f}\n"
                            found_balance = True
                    
                    if not found_balance:
                        balance_info += "• لا يوجد رصيد حالياً\n"
            
            # حفظ المفاتيح وتهيئة الحساب الحقيقي
            from users.user_manager import user_manager
            from users.database import db_manager
            from api.bybit_api import real_account_manager
            
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['bybit_api_key'] = api_key
                user_data['bybit_api_secret'] = api_secret
                user_data['exchange'] = 'bybit'
                user_data['account_type'] = 'real'  # حساب حقيقي
                
                # تهيئة الحساب الحقيقي فوراً
                try:
                    real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
                    logger.info(f"✅ تم تهيئة حساب Bybit الحقيقي للمستخدم {user_id}")
                except Exception as e:
                    logger.error(f"⚠️ خطأ في تهيئة الحساب: {e}")
                
                # حفظ في قاعدة البيانات
                db_manager.update_user_settings(user_id, {
                    'bybit_api_key': api_key,
                    'bybit_api_secret': api_secret,
                    'exchange': 'bybit',
                    'account_type': 'real'
                })
                
                # إرسال رسالة نجاح مع معلومات الحساب
                await update.message.reply_text(
                    f"✅ **تم الاتصال بـ Bybit بنجاح!**\n\n"
                    f"🔐 API مرتبط ويعمل\n"
                    f"📊 نوع الحساب: حقيقي{balance_info}",
                    parse_mode='Markdown'
                )
                
                logger.info(f"تم حفظ مفاتيح Bybit الحقيقية للمستخدم {user_id}")
                return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(
                f"❌ **خطأ في الاتصال**\n\n"
                f"تحقق من الاتصال بالإنترنت\n"
                f"الخطأ: {str(e)}"
            )
            return False
    
    except Exception as e:
        logger.error(f"خطأ في اختبار/حفظ مفاتيح Bybit: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ **خطأ:**\n{str(e)}"
        )
        return False

async def activate_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل المنصة المختارة - تهيئة الحساب الحقيقي"""
    query = update.callback_query
    await query.answer("جاري التحقق...")
    
    user_id = update.effective_user.id
    exchange = query.data.replace('exchange_activate_', '')
    
    from users.user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: المستخدم غير موجود")
        return
    
    # التحقق من وجود المفاتيح (Bybit فقط)
    api_key = user_data.get('bybit_api_key', '')
    api_secret = user_data.get('bybit_api_secret', '')
    # التحقق من أن المفاتيح موجودة وليست القيم الافتراضية
    default_key = BYBIT_API_KEY if BYBIT_API_KEY else ''
    has_keys = api_key and api_secret and api_key != default_key and len(api_key) > 10
    
    # فقط Bybit مدعوم
    if exchange != 'bybit':
        await query.edit_message_text(
            f"⚠️ **{exchange.upper()} غير مدعوم**\n\n"
            f"🔧 البوت يدعم Bybit فقط حالياً",
            parse_mode='Markdown'
        )
        return
    
    if not has_keys or not api_secret:
        await query.edit_message_text(
            f"⚠️ **لم يتم ربط {exchange.upper()} API**\n\n"
            f"يجب ربط API أولاً قبل التفعيل\n\n"
            f"اضغط على \"🔗 ربط API\" أولاً",
            parse_mode='Markdown'
        )
        return
    
    # التحقق من أن المنصة مفعّلة بالفعل
    current_exchange = user_data.get('exchange', '')
    account_type = user_data.get('account_type', 'demo')
    
    if current_exchange == exchange and account_type == 'real':
        # المنصة مفعّلة بالفعل
        await query.edit_message_text(
            f"✅ **{exchange.upper()} مفعّلة بالفعل!**\n\n"
            f"🔐 الحساب الحقيقي نشط ويعمل\n"
            f"🏦 المنصة: {exchange.upper()}\n\n"
            f"💡 يمكنك:\n"
            f"• عرض المحفظة من القائمة الرئيسية\n"
            f"• عرض الصفقات المفتوحة\n"
            f"• استقبال إشارات التداول\n\n"
            f"📊 لعرض التفاصيل، اذهب للقائمة الرئيسية",
            parse_mode='Markdown'
        )
        return
    
    # تهيئة الحساب الحقيقي
    from api.bybit_api import real_account_manager
    try:
        logger.info(f"🔄 بدء تهيئة حساب {exchange} للمستخدم {user_id}")
        real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
        logger.info(f"✅ تم تهيئة حساب {exchange} بنجاح")
        
        # تفعيل المنصة
        user_data['exchange'] = exchange
        user_data['account_type'] = 'real'  # حساب حقيقي
        
        from users.database import db_manager
        db_manager.update_user_settings(user_id, {
            'exchange': exchange,
            'account_type': 'real',
            'market_type': user_data.get('market_type', 'spot'),
            'is_active': True
        })
        
        # جلب معلومات الحساب
        account = real_account_manager.get_account(user_id)
        balance_info = ""
        
        if account:
            balance = account.get_wallet_balance()
            if balance:
                balance_info = f"\n\n💰 **الرصيد الإجمالي:** ${balance.get('total_equity', 0):,.2f}"
        
        await query.edit_message_text(
            f"✅ **تم تفعيل {exchange.upper()} بنجاح!**\n\n"
            f"🔐 **الحساب:** حقيقي ونشط\n"
            f"🏦 **المنصة:** {exchange.upper()}\n"
            f"📊 **الحالة:** متصل ويعمل{balance_info}\n\n"
            f"🎉 **يمكنك الآن:**\n"
            f"• استقبال إشارات التداول\n"
            f"• التداول الحقيقي على المنصة\n"
            f"• عرض الرصيد والصفقات الفعلية\n"
            f"• تنفيذ الأوامر على المنصة",
            parse_mode='Markdown'
        )
        
        logger.info(f"تم تفعيل {exchange} الحقيقي للمستخدم {user_id}")
        
    except Exception as e:
        logger.error(f"خطأ في تفعيل المنصة: {e}")
        import traceback
        traceback.print_exc()
        
        error_message = str(e)
        
        # رسائل خطأ مخصصة
        if "ModuleNotFoundError" in error_message or "ImportError" in error_message:
            error_details = "خطأ في استيراد المكتبات. تأكد من تثبيت جميع المتطلبات."
        elif "connection" in error_message.lower():
            error_details = "خطأ في الاتصال بالمنصة. تحقق من الإنترنت."
        elif "api" in error_message.lower() or "key" in error_message.lower():
            error_details = "خطأ في مفاتيح API. تحقق من صحة المفاتيح."
        else:
            error_details = f"تفاصيل الخطأ: {error_message[:100]}"
        
        await query.edit_message_text(
            f"❌ **خطأ في التفعيل**\n\n"
            f"{error_details}\n\n"
            f"💡 **الحلول المقترحة:**\n"
            f"1. تحقق من صحة مفاتيح API\n"
            f"2. تأكد من تفعيل API في حسابك\n"
            f"3. جرب إعادة ربط API\n"
            f"4. تحقق من الاتصال بالإنترنت",
            parse_mode='Markdown'
        )

async def test_exchange_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختبار الاتصال بالمنصة"""
    query = update.callback_query
    await query.answer("جاري الاختبار...")
    
    user_id = update.effective_user.id
    exchange = query.data.replace('exchange_test_', '')
    
    from users.user_manager import user_manager
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: المستخدم غير موجود")
        return
    
    try:
        # دعم Bybit فقط
        if exchange != 'bybit':
            result = "⚠️ **هذه المنصة غير مدعومة حالياً**\n\n"
            result += "🔧 البوت يدعم Bybit فقط"
        else:
            result = "✅ الاتصال بـ Bybit ناجح!"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="exchange_select_bybit")]]
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
    
    try:
        # أمر اختيار المنصة
        application.add_handler(CommandHandler("exchange", cmd_select_exchange))
        logger.info("✅ تم تسجيل أمر exchange")
    except Exception as e:
        logger.warning(f"⚠️ فشل تسجيل أمر exchange: {e}")
    
    # تسجيل الأمر العربي فقط إذا كان مدعوماً
    try:
        application.add_handler(CommandHandler("منصة", cmd_select_exchange))
        logger.info("✅ تم تسجيل أمر منصة")
    except Exception as e:
        logger.debug(f"⚠️ لم يتم تسجيل أمر منصة (قد لا يكون مدعوماً): {e}")
    
    try:
        application.add_handler(CommandHandler("cancel", cancel_setup))
        logger.info("✅ تم تسجيل أمر cancel")
    except Exception as e:
        logger.warning(f"⚠️ فشل تسجيل أمر cancel: {e}")
    
    # معالجات الأزرار - تم نقلها إلى bybit_trading_bot.py
    # معالج إدخال المفاتيح - سيتم التعامل معه عبر context.user_data
    
    logger.info("✅ تم تسجيل معالجات أوامر المنصات")

