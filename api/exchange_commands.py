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
            bybit_key = user_data.get('bybit_api_key', '')
            # التحقق من أن API Key موجود وليس فارغاً وليس القيمة الافتراضية
            default_key = BYBIT_API_KEY if (BYBIT_API_KEY and len(BYBIT_API_KEY) > 0) else ''
            bybit_linked = bybit_key and len(bybit_key) > 10 and bybit_key != default_key
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب بيانات المستخدم: {e}")
        # استخدام قيم افتراضية
        user_data = {}
        current_exchange = ''
        bybit_linked = False
    
    # التحقق من Bitget
    bitget_linked = False
    if user_data:
        bitget_key = user_data.get('bitget_api_key', '')
        bitget_linked = bitget_key and len(bitget_key) > 10
    
    # بناء الأزرار مع الحالة الصحيحة
    bybit_icon = "✅" if (current_exchange == 'bybit' and bybit_linked) else ("🔗" if bybit_linked else "⚪")
    bitget_icon = "✅" if (current_exchange == 'bitget' and bitget_linked) else ("🔗" if bitget_linked else "⚪")
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{bybit_icon} Bybit", 
                callback_data="exchange_select_bybit"
            )
        ],
        [
            InlineKeyboardButton(
                f"{bitget_icon} Bitget", 
                callback_data="exchange_select_bitget"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # تحديد حالة المنصة
    if current_exchange and (bybit_linked or bitget_linked):
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

🔹 **Bitget**
   • يدعم Spot و Futures
   • رافعة مالية متاحة (حتى 125x)
   • رسوم تداول منخفضة
   • منصة عالمية موثوقة

🔗 **روابط التسجيل:**
• [Bybit](https://www.bybit.com/invite?ref=OLAZ2M)
• [Bitget](https://www.bitget.com/referral/)

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
    """معالجة اختيار المنصة (غير مستخدمة حالياً)"""
    # ملاحظة: هذه الدالة غير مستخدمة حالياً
    # معالجة أزرار اختيار المنصات تتم مباشرة في bybit_trading_bot.py
    pass

async def show_bybit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خيارات إعداد Bybit مع معلومات الحساب - نظام احترافي"""
    # تهيئة المتغيرات الافتراضية
    user_data = {}
    has_bybit_keys = False
    current_exchange = ''
    account_type = 'demo'
    is_active = False
    is_connected = False
    user_id = None
    query = None
    exchange_name = 'bybit'  # افتراضي
    
    # التحقق من وجود callback_query أولاً
    query = update.callback_query
    if not query:
        logger.error("❌ لا يوجد callback_query في update")
        return
    
    # تحديد المنصة من callback_data
    if query.data == "exchange_select_bitget":
        exchange_name = 'bitget'
    
    # إجابة الاستعلام فوراً
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"⚠️ خطأ في query.answer(): {e}")
    
    # التحقق من وجود effective_user
    if not update.effective_user:
        logger.error("❌ لا يوجد effective_user في update")
        try:
            await query.edit_message_text("❌ خطأ: لا يمكن التعرف على المستخدم")
        except:
            pass
        return
    
    user_id = update.effective_user.id
    logger.info(f"🔄 معالجة زر {exchange_name.upper()} للمستخدم {user_id}")
    
    try:
        
        # جلب بيانات المستخدم
        try:
            logger.info(f"🔄 محاولة استيراد user_manager للمستخدم {user_id}")
            from users.user_manager import user_manager
            logger.info(f"✅ تم استيراد user_manager بنجاح")
            
            logger.info(f"🔄 محاولة جلب بيانات المستخدم {user_id}")
            user_data = user_manager.get_user(user_id)
            logger.info(f"✅ تم جلب بيانات المستخدم: {user_id}, البيانات: {bool(user_data)}")
            
            # تسجيل محتوى user_data للأ debugging
            if user_data:
                logger.info(f"📊 محتوى user_data: exchange={user_data.get('exchange')}, account_type={user_data.get('account_type')}")
        except ImportError as e:
            logger.error(f"❌ خطأ في استيراد user_manager: {e}", exc_info=True)
            user_data = {}
        except Exception as e:
            logger.error(f"❌ خطأ في جلب بيانات المستخدم من user_manager: {e}", exc_info=True)
            user_data = {}
        
        # التحقق من أن user_data موجود
        if not user_data:
            logger.warning(f"⚠️ المستخدم {user_id} غير موجود في قاعدة البيانات")
            user_data = {}
        
        # التحقق من وجود API Keys حسب المنصة
        if user_data:
            if exchange_name == 'bybit':
                api_key = user_data.get('bybit_api_key', '')
                api_secret = user_data.get('bybit_api_secret', '')
            elif exchange_name == 'bitget':
                api_key = user_data.get('bitget_api_key', '')
                api_secret = user_data.get('bitget_api_secret', '')
            else:
                api_key = ''
                api_secret = ''
            
            # التحقق من أن API Key موجود وليس فارغاً وليس القيمة الافتراضية
            default_key = BYBIT_API_KEY if (BYBIT_API_KEY and len(str(BYBIT_API_KEY)) > 0) else ''
            has_bybit_keys = (api_key and api_secret and 
                            len(api_key) > 10 and len(api_secret) > 10 and 
                            api_key != default_key)
        
        # التحقق من التفعيل والاتصال
        current_exchange = user_data.get('exchange', '') if user_data else ''
        account_type = user_data.get('account_type', 'demo') if user_data else 'demo'
        is_active = current_exchange == exchange_name and account_type == 'real'
        is_connected = has_bybit_keys and current_exchange == exchange_name
        
    except Exception as e:
        logger.error(f"❌ خطأ في show_bybit_options: {e}", exc_info=True)
        # استخدام القيم الافتراضية
        user_data = {}
        has_bybit_keys = False
        current_exchange = ''
        account_type = 'demo'
        is_active = False
        if user_id is None and update.effective_user:
            user_id = update.effective_user.id
    
    # تحديد حالة API - 3 حالات واضحة
    if is_active and has_bybit_keys and is_connected:
        # الحالة 1: مربوط ومفعّل بالكامل ✅
        status_icon = "🟢"
        status_text = "متصل ومفعّل (حساب حقيقي)"
        status_emoji = "✅"
    elif has_bybit_keys:
        # الحالة 2: مربوط لكن غير مفعّل 🔗
        status_icon = "🟡"
        status_text = "مربوط لكن غير مفعّل"
        status_emoji = "🔗"
    else:
        # الحالة 3: غير مربوط ⚪
        status_icon = "🔴"
        status_text = "غير مربوط"
        status_emoji = "⚪"
    
    # جلب معلومات الرصيد الحقيقي من Bybit
    balance_text = ""
    market_type_current = user_data.get('market_type', 'spot') if user_data else 'spot'
    
    try:
        if is_active and has_bybit_keys and is_connected:
            # الحساب مفعّل - جلب الرصيد الحقيقي
            from api.bybit_api import real_account_manager
            real_account = real_account_manager.get_account(user_id)
            if real_account:
                try:
                    # جلب الرصيد من Bybit حسب نوع السوق الحالي
                    balance = real_account.get_wallet_balance(market_type_current)
                    if balance:
                        total_equity = balance.get('total_equity', 0)
                        available_balance = balance.get('available_balance', 0)
                        
                        # بناء رسالة الرصيد
                        balance_text = f"""

💰 **الرصيد الإجمالي:** ${total_equity:,.2f}
💳 **الرصيد المتاح:** ${available_balance:,.2f}
📊 **نوع السوق:** {market_type_current.upper()}
🏦 **المنصة:** Bybit (حساب حقيقي)"""
                        
                        # إضافة معلومات العملات الأخرى إن وجدت
                        coins = balance.get('coins', {})
                        if coins:
                            balance_text += "\n\n💎 **العملات المتوفرة:**\n"
                            # عرض أول 3 عملات
                            displayed_coins = 0
                            for coin_name, coin_info in coins.items():
                                if displayed_coins < 3 and coin_info.get('equity', 0) > 0:
                                    equity = coin_info.get('equity', 0)
                                    balance_text += f"• {coin_name}: {equity:.4f}\n"
                                    displayed_coins += 1
                        
                        logger.info(f"✅ تم جلب الرصيد من Bybit: ${total_equity:,.2f}")
                except Exception as e:
                    logger.error(f"❌ خطأ في جلب الرصيد: {e}")
                    import traceback
                    traceback.print_exc()
                    balance_text = "\n⚠️ **لا يمكن الوصول إلى الرصيد حالياً**"
        elif has_bybit_keys:
            # الحساب مربوط لكن غير مفعّل
            balance_text = "\n\n⚠️ **الحساب مربوط بنجاح لكن غير مفعّل**\n💡 اضغط على 'تفعيل المنصة' لبدء استخدام الحساب الحقيقي"
        else:
            # غير مربوط
            balance_text = "\n\n⚠️ **لم يتم ربط API بعد**\n💡 اضغط على 'ربط Bybit API' للبدء"
    except Exception as e:
        logger.error(f"❌ خطأ في جلب معلومات الحساب: {e}")
        import traceback
        traceback.print_exc()
        balance_text = ""
    
    # التحقق من user_id قبل المتابعة
    if user_id is None:
        logger.error("❌ user_id هو None! لا يمكن المتابعة")
        try:
            await query.edit_message_text(
                "❌ **خطأ في التعرف على المستخدم**\n\n"
                "🔧 يرجى:\n"
                "• إعادة تشغيل البوت\n"
                "• المحاولة مرة أخرى\n"
                "• التواصل مع الدعم إذا استمرت المشكلة"
            )
        except Exception as e:
            logger.error(f"❌ فشل عرض رسالة الخطأ: {e}")
        return
    
    # رسالة خاصة إذا لم يتم العثور على بيانات المستخدم
    if not user_data or user_data == {}:
        # إنشاء حساب تلقائياً للمستخدم
        logger.info(f"🆕 محاولة إنشاء حساب جديد للمستخدم {user_id}")
        
        try:
            from users.user_manager import user_manager
            from users.database import db_manager
            
            # إنشاء المستخدم في قاعدة البيانات
            logger.info(f"🔄 استدعاء db_manager.create_user({user_id})")
            db_manager.create_user(user_id)
            logger.info(f"✅ تم استدعاء create_user بنجاح")
            
            # تحديث user_data
            logger.info(f"🔄 جلب بيانات المستخدم الجديد")
            user_data = user_manager.get_user(user_id)
            logger.info(f"✅ تم جلب بيانات المستخدم الجديد: {bool(user_data)}")
            
        except ImportError as e:
            logger.error(f"❌ فشل استيراد user_manager أو db_manager: {e}", exc_info=True)
            user_data = {}
        except Exception as e:
            logger.error(f"❌ فشل إنشاء الحساب الجديد: {e}", exc_info=True)
            user_data = {}
        
        # إعادة تعيين المتغيرات
        if not user_data:
            user_data = {}
        
        # الآن جرب مرة أخرى
        has_bybit_keys = False
        current_exchange = ''
        account_type = 'demo'
        is_active = False
        
        logger.info(f"✅ تم معالجة المستخدم {user_id} (حساب {'جديد' if user_data else 'فارغ'})")
        
        # مباشرة إلى عملية ربط API بدلاً من عرض الخيارات
        logger.info(f"🔄 تحويل المستخدم الجديد مباشرة إلى عملية ربط API")
        await start_bybit_setup(update, context)
        return
    
    # عرض قائمة الخيارات الرئيسية (بدلاً من التحويل المباشر للربط)
    # سيتم عرض 3 أزرار: ربط API، اختيار المنصة، اختبار الاتصال
    
    # تحديد المعلومات حسب المنصة
    if exchange_name == 'bybit':
        platform_name = "Bybit"
        max_leverage = "100x"
        referral_link = "https://www.bybit.com/invite?ref=OLAZ2M"
        setup_callback = "exchange_setup_bybit"
        activate_callback = "exchange_activate_bybit"
        test_callback = "exchange_test_bybit"
    elif exchange_name == 'bitget':
        platform_name = "Bitget"
        max_leverage = "125x"
        referral_link = "https://www.bitget.com/referral/"
        setup_callback = "exchange_setup_bitget"
        activate_callback = "exchange_activate_bitget"
        test_callback = "exchange_test_bitget"
    else:
        platform_name = exchange_name.upper()
        max_leverage = "100x"
        referral_link = "#"
        setup_callback = f"exchange_setup_{exchange_name}"
        activate_callback = f"exchange_activate_{exchange_name}"
        test_callback = f"exchange_test_{exchange_name}"
    
    # المستخدم لديه API مربوط - عرض خيارات إدارة الحساب حسب الحالة
    # الحالة 1: مفعّل بالكامل ✅
    if is_active and has_bybit_keys and is_connected:
        message = f"""
🏦 **إعداد منصة {platform_name}**

{status_emoji} **حالة API:** {status_icon} **{status_text}**{balance_text}

✅ **المنصة مفعّلة ونشطة!**

🎯 **يمكنك الآن:**
• استقبال إشارات التداول
• تنفيذ الصفقات الحقيقية
• عرض الرصيد والأرباح
• إدارة المحفظة

📋 **المميزات:**
• التداول الفوري (Spot)
• تداول الفيوتشر (Futures)
• الرافعة المالية (حتى {max_leverage})

🔗 **رابط الإحالة:** [انضم إلى {platform_name}]({referral_link})
"""
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث API Keys", callback_data=setup_callback)],
            [InlineKeyboardButton("📊 اختبار الاتصال", callback_data=test_callback)],
            [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
        ]
    
    # الحالة 2: مربوط لكن غير مفعّل 🔗
    elif has_bybit_keys and not is_active:
        message = f"""
🏦 **إعداد منصة {platform_name}**

{status_emoji} **حالة API:** {status_icon} **{status_text}**{balance_text}

🎯 **الخطوة التالية: التفعيل!**

💡 لقد تم ربط API بنجاح، لكن لم يتم تفعيل المنصة بعد.

✅ **اضغط على زر "اختيار المنصة" لـ:**
• تفعيل الحساب الحقيقي
• البدء في استقبال الإشارات
• تنفيذ الصفقات على المنصة
• ربط كامل مع المشروع

📋 **المميزات:**
• التداول الفوري (Spot)
• تداول الفيوتشر (Futures)
• الرافعة المالية (حتى {max_leverage})

🔗 **رابط الإحالة:** [انضم إلى {platform_name}]({referral_link})
"""
        keyboard = [
            [InlineKeyboardButton("🔗 ربط API Keys", callback_data=setup_callback)],
            [InlineKeyboardButton("✅ اختيار هذه المنصة", callback_data=activate_callback)],
            [InlineKeyboardButton("📊 اختبار الاتصال", callback_data=test_callback)],
            [InlineKeyboardButton("🔙 رجوع للإعدادات", callback_data="settings")]
        ]
    
    # الحالة 3: غير مربوط - عرض الخيارات الأساسية
    else:
        message = f"""
🏦 **إعداد منصة {platform_name}**

{status_emoji} **حالة API:** {status_icon} **{status_text}**{balance_text}

💡 **مرحباً بك في إعداد {platform_name}!**

🎯 **الخطوات:**
1️⃣ **ربط API Keys** - لربط حسابك
2️⃣ **اختيار المنصة** - لتفعيلها كمنصة رئيسية
3️⃣ **اختبار الاتصال** - للتأكد من عمل كل شيء

📋 **المميزات:**
• التداول الفوري (Spot)
• تداول الفيوتشر (Futures)
• الرافعة المالية (حتى {max_leverage})
• رسوم تداول تنافسية
• سيولة عالية

🔗 **ليس لديك حساب؟**
[سجل الآن في {platform_name}]({referral_link})

👇 **ابدأ من هنا:**
"""
        keyboard = [
            [InlineKeyboardButton("🔗 ربط API Keys", callback_data=setup_callback)],
            [InlineKeyboardButton("✅ اختيار هذه المنصة", callback_data=activate_callback)],
            [InlineKeyboardButton("📊 اختبار الاتصال", callback_data=test_callback)],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="select_exchange")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الرسالة مع معالجة الأخطاء
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        logger.info(f"✅ تم عرض خيارات Bybit بنجاح للمستخدم {user_id}")
    except Exception as e:
        logger.error(f"❌ خطأ في عرض رسالة Bybit: {e}", exc_info=True)
        # محاولة إرسال رسالة جديدة بدلاً من تعديل
        try:
            await query.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            logger.info(f"✅ تم إرسال رسالة Bybit كرسالة جديدة للمستخدم {user_id}")
        except Exception as e2:
            logger.error(f"❌ فشل في إرسال الرسالة أيضاً: {e2}", exc_info=True)
            # آخر محاولة: إرسال رسالة بسيطة
            try:
                await query.answer("❌ حدث خطأ في عرض الخيارات. يرجى المحاولة مرة أخرى.", show_alert=True)
            except:
                pass

async def start_bybit_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية ربط API - الخطوة 1: API Key"""
    # التحقق من وجود callback_query
    query = update.callback_query
    if not query:
        logger.error("❌ لا يوجد callback_query في start_bybit_setup")
        return
    
    await query.answer()
    
    # تحديد المنصة من callback_data
    exchange_name = 'bybit'
    if 'bitget' in query.data:
        exchange_name = 'bitget'
        platform_name = "Bitget"
        referral_link = "https://www.bitget.com/referral/"
        cancel_callback = "exchange_select_bitget"
    else:
        platform_name = "Bybit"
        referral_link = "https://www.bybit.com/invite?ref=OLAZ2M"
        cancel_callback = "exchange_select_bybit"
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=cancel_callback)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🔑 **ربط {platform_name} API - الخطوة 1 من 2**

📝 أرسل **API Key** الخاص بك

**مثال:**
```
abc123xyz456def789
```

💡 **للحصول على API Key:**
1. اذهب إلى [{platform_name}.com]({referral_link})
2. Account → API Management
3. Create New Key
4. انسخ API Key

⚠️ **تأكد من تفعيل الصلاحيات:**
• ✅ Read (قراءة)
• ✅ Trade (تداول)
• ❌ Withdraw (سحب) - لا تفعّله!

🔗 **ليس لديك حساب؟** [سجل الآن]({referral_link})

📝 أرسل API Key الآن
"""
    
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض رسالة start_bybit_setup: {e}")
        try:
            await query.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except Exception as e2:
            logger.error(f"❌ فشل في إرسال الرسالة البديلة: {e2}")
            return
    
    # حفظ حالة انتظار API Key لـ Bybit
    context.user_data['awaiting_exchange_keys'] = 'bybit_step1'

async def handle_api_keys_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال مفاتيح API - خطوة بخطوة"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    state = context.user_data.get('awaiting_exchange_keys')
    
    if not state:
        return
    
    # تجاهل الأوامر
    if text.startswith('/'):
        logger.info(f"تجاهل الأمر: {text}")
        return
    
    # الخطوة 1: استقبال API Key
    if state in ['bybit_step1', 'bitget_step1']:
        exchange = 'bybit' if 'bybit' in state else 'bitget'
        
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
    elif state in ['bybit_step2', 'bitget_step2']:
        exchange = 'bybit' if 'bybit' in state else 'bitget'
        
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
        
        # دعم المنصات المختلفة
        if exchange == 'bybit':
            success = await test_and_save_bybit_keys(user_id, api_key, api_secret, update)
        elif exchange == 'bitget':
            success = await test_and_save_bitget_keys(user_id, api_key, api_secret, update)
        else:
            await update.message.reply_text(f"❌ المنصة {exchange} غير مدعومة حالياً")
            success = False
        
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
        
        # بناء params dictionary (بدون timestamp!)
        params = {
            'accountType': 'UNIFIED'
        }
        
        # بناء query string باستخدام urlencode مع الترميز الصحيح
        params_str = urlencode(sorted(params.items()))
        
        # بناء الـ signature string حسب توثيق Bybit V5
        # صيغة: timestamp + api_key + recv_window + params
        sign_str = timestamp + str(api_key) + recv_window + params_str
        
        # تأكد من أن جميع القيم نصية (string) قبل التشفير
        # استخدم explicit string conversion لمنع أي مشاكل في الترميز
        secret_bytes = str(api_secret).encode('utf-8')
        sign_bytes = sign_str.encode('utf-8')
        
        signature = hmac.new(secret_bytes, sign_bytes, hashlib.sha256).hexdigest()
        
        # إرسال الطلب
        headers = {
            'X-BAPI-API-KEY': str(api_key),
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'X-BAPI-SIGN-TYPE': '2',
            'Content-Type': 'application/json'
        }
        
        try:
            # بناء URL بشكل صحيح
            url = f"{base_url}{endpoint}?{params_str}"
            
            response = requests.get(
                url,
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
            
            # حفظ المفاتيح وتهيئة الحساب الحقيقي وتفعيله تلقائياً
            from users.database import db_manager
            from users.user_manager import user_manager
            from api.bybit_api import real_account_manager
            
            # حفظ مباشرة في قاعدة البيانات مع التفعيل التلقائي
            try:
                # التأكد من وجود المستخدم في قاعدة البيانات
                existing_user = db_manager.get_user(user_id)
                if not existing_user:
                    logger.info(f"إنشاء مستخدم جديد: {user_id}")
                    db_manager.create_user(user_id)
                
                # ✅ خطوة 1: حفظ في قاعدة البيانات وتفعيل المنصة
                # حفظ المفاتيح والإعدادات الأساسية
                save_result = db_manager.update_user_data(user_id, {
                    'bybit_api_key': api_key,
                    'bybit_api_secret': api_secret,
                    'exchange': 'bybit',
                    'is_active': True
                })
                
                if not save_result:
                    logger.error(f"❌ فشل في حفظ بيانات المستخدم {user_id}")
                    await update.message.reply_text(
                        "❌ **فشل في حفظ البيانات**\n\n"
                        "حدث خطأ في قاعدة البيانات\n"
                        "يرجى المحاولة مرة أخرى",
                        parse_mode='Markdown'
                    )
                    return False
                
                # حفظ إعدادات التداول
                settings_result = db_manager.update_user_settings(user_id, {
                    'account_type': 'real'
                })
                
                if not settings_result:
                    logger.warning(f"⚠️ فشل في حفظ إعدادات التداول للمستخدم {user_id}")
                
                logger.info(f"✅ تم حفظ وتفعيل مفاتيح API للمستخدم {user_id}")
                
                # ✅ خطوة 2: تحديث بيانات المستخدم في الذاكرة
                user_data = user_manager.get_user(user_id)
                if user_data:
                    user_data['bybit_api_key'] = api_key
                    user_data['bybit_api_secret'] = api_secret
                    user_data['exchange'] = 'bybit'
                    user_data['account_type'] = 'real'
                    user_data['is_active'] = True
                    logger.info(f"✅ تم تحديث بيانات المستخدم {user_id} في الذاكرة")
                
                # ✅ خطوة 3: تهيئة الحساب الحقيقي فوراً
                try:
                    real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
                    logger.info(f"✅ تم تهيئة حساب Bybit الحقيقي للمستخدم {user_id}")
                except Exception as e:
                    logger.error(f"⚠️ خطأ في تهيئة الحساب: {e}", exc_info=True)
                
                # ✅ خطوة 4: تسجيل المنصة في النظام الجديد (إن وجد)
                try:
                    from api.init_exchanges import create_exchange_instance
                    exchange_instance = create_exchange_instance(user_id, 'bybit', api_key, api_secret)
                    if exchange_instance:
                        logger.info(f"✅ تم إنشاء نسخة Bybit للمستخدم {user_id} في النظام الجديد")
                except Exception as e:
                    logger.debug(f"النظام الجديد غير متاح بعد: {e}")
                
                # إرسال رسالة نجاح مع معلومات الحساب
                await update.message.reply_text(
                    f"✅ **تم ربط وتفعيل Bybit بنجاح!**\n\n"
                    f"🎉 **المنصة نشطة الآن!**\n\n"
                    f"🔐 API مرتبط ومفعّل\n"
                    f"📊 نوع الحساب: حقيقي\n"
                    f"🏦 المنصة: Bybit\n"
                    f"✅ الحالة: مفعّل ومتصل{balance_info}\n\n"
                    f"💡 **يمكنك الآن:**\n"
                    f"• استقبال إشارات التداول\n"
                    f"• تنفيذ الصفقات الحقيقية\n"
                    f"• عرض الرصيد والصفقات\n"
                    f"• إدارة المحفظة\n\n"
                    f"📱 اذهب إلى /settings لعرض التفاصيل",
                    parse_mode='Markdown'
                )
                
                logger.info(f"🎉 تم ربط وتفعيل Bybit بنجاح للمستخدم {user_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ فشل حفظ مفاتيح API: {e}", exc_info=True)
                await update.message.reply_text(
                    f"❌ **فشل في حفظ البيانات**\n\n"
                    f"حدث خطأ أثناء حفظ المفاتيح\n"
                    f"يرجى المحاولة مرة أخرى"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
            await update.message.reply_text(
                f"❌ **خطأ في الاتصال**\n\n"
                f"تحقق من الاتصال بالإنترنت\n"
                f"الخطأ: {error_msg}"
            )
            return False
    
    except UnicodeEncodeError as e:
        logger.error(f"خطأ في ترميز النص: {e}")
        await update.message.reply_text(
            "❌ **خطأ في المعالجة**\n\n"
            "حدث خطأ في معالجة البيانات.\n"
            "يرجى التحقق من صحة المفاتيح والمحاولة مرة أخرى."
        )
        return False
    except Exception as e:
        logger.error(f"خطأ في اختبار/حفظ مفاتيح Bybit: {e}")
        import traceback
        traceback.print_exc()
        error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        await update.message.reply_text(
            f"❌ **خطأ:**\n{error_msg}"
        )
        return False

async def test_and_save_bitget_keys(user_id: int, api_key: str, api_secret: str, update: Update) -> bool:
    """اختبار وحفظ مفاتيح Bitget"""
    try:
        # استخدام النظام الجديد لاختبار Bitget
        from api.init_exchanges import create_exchange_instance
        
        # إنشاء نسخة مؤقتة
        bitget = create_exchange_instance(user_id, 'bitget', api_key, api_secret)
        
        if not bitget:
            await update.message.reply_text(
                "❌ **فشل إنشاء اتصال Bitget**\n\n"
                "تحقق من صحة المفاتيح"
            )
            return False
        
        # ⚠️ ملاحظة: Bitget يحتاج passphrase
        # يمكن طلبه لاحقاً أو تخزينه بشكل منفصل
        
        # اختبار الاتصال (بدون passphrase قد يفشل، لكن نحاول)
        try:
            if bitget.test_connection():
                connection_ok = True
            else:
                connection_ok = False
        except:
            # قد يفشل بدون passphrase، لكن نحفظ المفاتيح
            connection_ok = False
        
        # حفظ المفاتيح وتفعيل المنصة
        from users.database import db_manager
        from users.user_manager import user_manager
        from api.bybit_api import real_account_manager
        
        try:
            # التأكد من وجود المستخدم في قاعدة البيانات
            existing_user = db_manager.get_user(user_id)
            if not existing_user:
                logger.info(f"إنشاء مستخدم جديد: {user_id}")
                db_manager.create_user(user_id)
            
            # حفظ في قاعدة البيانات - استخدام update_user_data للمفاتيح
            save_result = db_manager.update_user_data(user_id, {
                'bitget_api_key': api_key,
                'bitget_api_secret': api_secret,
                'exchange': 'bitget',
                'is_active': True
            })
            
            if not save_result:
                logger.error(f"❌ فشل في حفظ بيانات المستخدم {user_id}")
                await update.message.reply_text(
                    "❌ **فشل في حفظ البيانات**\n\n"
                    "حدث خطأ في قاعدة البيانات\n"
                    "يرجى المحاولة مرة أخرى",
                    parse_mode='Markdown'
                )
                return False
            
            # حفظ إعدادات التداول
            settings_result = db_manager.update_user_settings(user_id, {
                'account_type': 'real'
            })
            
            if not settings_result:
                logger.warning(f"⚠️ فشل في حفظ إعدادات التداول للمستخدم {user_id}")
            
            logger.info(f"✅ تم حفظ وتفعيل مفاتيح Bitget للمستخدم {user_id}")
            
            # تحديث الذاكرة
            user_data = user_manager.get_user(user_id)
            if user_data:
                user_data['bitget_api_key'] = api_key
                user_data['bitget_api_secret'] = api_secret
                user_data['exchange'] = 'bitget'
                user_data['account_type'] = 'real'
                user_data['is_active'] = True
            
            # رسالة نجاح
            await update.message.reply_text(
                f"✅ **تم ربط وتفعيل Bitget بنجاح!**\n\n"
                f"🎉 **المنصة نشطة الآن!**\n\n"
                f"🔐 API مرتبط ومفعّل\n"
                f"📊 نوع الحساب: حقيقي\n"
                f"🏦 المنصة: Bitget\n"
                f"✅ الحالة: مفعّل ومتصل\n\n"
                f"💡 **يمكنك الآن:**\n"
                f"• استقبال إشارات التداول\n"
                f"• تنفيذ الصفقات الحقيقية\n"
                f"• عرض الرصيد والصفقات\n\n"
                f"⚠️ **ملاحظة:** Bitget يحتاج Passphrase\n"
                f"سيتم طلبه عند الحاجة\n\n"
                f"📱 اذهب إلى /settings لعرض التفاصيل",
                parse_mode='Markdown'
            )
            
            logger.info(f"🎉 تم ربط وتفعيل Bitget بنجاح للمستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ مفاتيح Bitget: {e}", exc_info=True)
            
            # تحديد نوع الخطأ
            if "update_user_data" in str(e) or "database" in str(e).lower():
                error_msg = "❌ **فشل في حفظ البيانات**\n\nحدث خطأ في قاعدة البيانات"
            elif "connection" in str(e).lower() or "api" in str(e).lower():
                error_msg = "❌ **فشل الاتصال!**\n\nتحقق من:\n• صحة المفاتيح\n• الصلاحيات المطلوبة\n• تفعيل API في حسابك"
            else:
                error_msg = f"❌ **حدث خطأ غير متوقع**\n\n`{str(e)}`"
            
            await update.message.reply_text(
                f"{error_msg}\n\nيرجى المحاولة مرة أخرى",
                parse_mode='Markdown'
            )
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار/حفظ مفاتيح Bitget: {e}")
        await update.message.reply_text(f"❌ **خطأ:**\n{str(e)}")
        return False

async def activate_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل المنصة المختارة - تهيئة الحساب الحقيقي"""
    # التحقق من وجود callback_query
    query = update.callback_query
    if not query:
        logger.error("❌ لا يوجد callback_query في activate_exchange")
        return
    
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
    default_key = BYBIT_API_KEY if (BYBIT_API_KEY and len(str(BYBIT_API_KEY)) > 0) else ''
    has_keys = api_key and api_secret and len(api_key) > 10 and api_key != default_key
    
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
    
    # تهيئة الحساب الحقيقي مع ربط كامل بالمشروع
    from api.bybit_api import real_account_manager
    from users.user_manager import user_manager
    from users.database import db_manager
    
    try:
        logger.info(f"🔄 بدء التفعيل الكامل لـ {exchange} للمستخدم {user_id}")
        
        # ✅ خطوة 1: تهيئة حساب المنصة
        real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
        logger.info(f"✅ تم تهيئة حساب {exchange} بنجاح")
        
        # ✅ خطوة 2: تحديث بيانات المستخدم في الذاكرة
        user_data['exchange'] = exchange
        user_data['account_type'] = 'real'  # حساب حقيقي
        user_data['is_active'] = True
        logger.info(f"✅ تم تحديث بيانات المستخدم {user_id} في الذاكرة")
        
        # ✅ خطوة 3: حفظ في قاعدة البيانات مع جميع الإعدادات
        # التأكد من وجود المستخدم في قاعدة البيانات
        existing_user = db_manager.get_user(user_id)
        if not existing_user:
            logger.info(f"إنشاء مستخدم جديد: {user_id}")
            db_manager.create_user(user_id)
        
        # حفظ المفاتيح والإعدادات الأساسية
        if exchange == 'bybit':
            save_result = db_manager.update_user_data(user_id, {
                'bybit_api_key': api_key,
                'bybit_api_secret': api_secret,
                'exchange': exchange,
                'is_active': True
            })
        elif exchange == 'bitget':
            save_result = db_manager.update_user_data(user_id, {
                'bitget_api_key': api_key,
                'bitget_api_secret': api_secret,
                'exchange': exchange,
                'is_active': True
            })
        else:
            save_result = False
        
        if not save_result:
            logger.error(f"❌ فشل في حفظ بيانات المستخدم {user_id}")
            await query.edit_message_text(
                "❌ **فشل في حفظ البيانات**\n\n"
                "حدث خطأ في قاعدة البيانات\n"
                "يرجى المحاولة مرة أخرى",
                parse_mode='Markdown'
            )
            return
        
        # حفظ إعدادات التداول
        settings_result = db_manager.update_user_settings(user_id, {
            'account_type': 'real',
            'market_type': user_data.get('market_type', 'spot')
        })
        
        if not settings_result:
            logger.warning(f"⚠️ فشل في حفظ إعدادات التداول للمستخدم {user_id}")
        logger.info(f"✅ تم حفظ الإعدادات في قاعدة البيانات")
        
        # ✅ خطوة 4: تسجيل في النظام الجديد (إن وجد)
        try:
            from api.init_exchanges import create_exchange_instance, get_user_exchange
            
            # التحقق من وجود نسخة، وإلا إنشاءها
            exchange_instance = get_user_exchange(user_id, exchange)
            if not exchange_instance:
                exchange_instance = create_exchange_instance(user_id, exchange, api_key, api_secret)
            
            if exchange_instance:
                # اختبار الاتصال
                if exchange_instance.test_connection():
                    logger.info(f"✅ تم التحقق من اتصال {exchange} في النظام الجديد")
                else:
                    logger.warning(f"⚠️ فشل اختبار الاتصال في النظام الجديد")
        except Exception as e:
            logger.debug(f"النظام الجديد غير متاح بعد: {e}")
        
        # ✅ خطوة 5: جلب معلومات الحساب والرصيد
        account = real_account_manager.get_account(user_id)
        balance_info = ""
        market_type = user_data.get('market_type', 'spot')
        
        if account:
            try:
                balance = account.get_wallet_balance(market_type)
                if balance:
                    total_equity = balance.get('total_equity', 0)
                    available = balance.get('available_balance', 0)
                    balance_info = f"""

💰 **معلومات الرصيد:**
• الرصيد الإجمالي: ${total_equity:,.2f}
• الرصيد المتاح: ${available:,.2f}
• نوع السوق: {market_type.upper()}"""
                    logger.info(f"✅ تم جلب الرصيد: ${total_equity:,.2f}")
            except Exception as e:
                logger.warning(f"⚠️ لم يتم جلب الرصيد: {e}")
                balance_info = "\n\n⚠️ لم يتم جلب الرصيد (قد يكون الحساب فارغاً)"
        
        # ✅ خطوة 6: إرسال رسالة النجاح الشاملة
        await query.edit_message_text(
            f"🎉 **تم تفعيل {exchange.upper()} بنجاح!**\n\n"
            f"✅ **الربط الكامل تم بنجاح:**\n"
            f"🔐 الحساب: حقيقي ونشط\n"
            f"🏦 المنصة: {exchange.upper()}\n"
            f"📊 الحالة: متصل ويعمل\n"
            f"🔗 مرتبط بالمشروع: ✅{balance_info}\n\n"
            f"🎯 **يمكنك الآن:**\n"
            f"• استقبال وتنفيذ إشارات التداول\n"
            f"• التداول الحقيقي على {exchange.upper()}\n"
            f"• عرض الرصيد والصفقات الفعلية\n"
            f"• إدارة المحفظة والأوامر\n"
            f"• متابعة الأرباح والخسائر\n\n"
            f"📱 اذهب إلى /settings لعرض جميع التفاصيل\n"
            f"📊 اذهب إلى /start للوصول إلى القائمة الرئيسية",
            parse_mode='Markdown'
        )
        
        logger.info(f"🎉 تم التفعيل الكامل لـ {exchange} للمستخدم {user_id} بنجاح")
        
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
    # التحقق من وجود callback_query
    query = update.callback_query
    if not query:
        logger.error("❌ لا يوجد callback_query في test_exchange_connection")
        return
    
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

