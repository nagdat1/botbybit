# إضافة وظيفة للتحقق من صحة الاتصال بـ API
async def verify_api_connection(api_key: str, api_secret: str) -> tuple[bool, str]:
    """التحقق من صحة اتصال API"""
    try:
        # إنشاء كائن API مؤقت للاختبار
        test_api = BybitAPI(api_key, api_secret)
        
        # محاولة جلب معلومات الحساب للتحقق
        response = test_api.get_account_balance()
        
        if response.get("retCode") == 0:
            return True, "✅ الاتصال ناجح"
        else:
            error_msg = response.get("retMsg", "خطأ غير محدد")
            return False, f"❌ فشل الاتصال: {error_msg}"
            
    except Exception as e:
        logger.error(f"خطأ في التحقق من API: {e}")
        return False, f"❌ خطأ في الاتصال: {str(e)}"

def mask_api_credentials(api_key: str, api_secret: str) -> tuple[str, str]:
    """إخفاء معلومات API جزئياً للعرض الآمن"""
    if not api_key or not api_secret:
        return "غير محدد", "غير محدد"
    
    # إظهار أول 4 وآخر 4 أحرف فقط
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
    masked_secret = f"{api_secret[:4]}...{api_secret[-4:]}" if len(api_secret) > 8 else "****"
    
    return masked_key, masked_secret

# تحديث وظيفة start لإضافة معلومات API
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت مع دعم تعدد المستخدمين"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    
    # التحقق من وجود المستخدم في قاعدة البيانات
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        # مستخدم جديد - إنشاء حساب
        user_manager.create_user(user_id)
        user_data = user_manager.get_user(user_id)
        
        # رسالة ترحيب للمستخدم الجديد
        welcome_message = f"""
🤖 مرحباً بك في بوت التداول Bybit متعدد المستخدمين

👋 أهلاً {update.effective_user.first_name}!

🔗 للبدء، يرجى ربط حسابك على Bybit:
• اضغط على زر "🔗 ربط API" أدناه
• سيطلب منك إدخال API_KEY و API_SECRET
• يمكنك الحصول على المفاتيح من: https://api.bybit.com

⚠️ ملاحظة: البوت يدعم التداول الحقيقي والتجريبي
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 ربط API", callback_data="link_api")],
            [InlineKeyboardButton("ℹ️ معلومات", callback_data="info")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message is not None:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        return
    
    # مستخدم موجود - عرض القائمة الرئيسية
    keyboard = [
        [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("📊 حالة الحساب")],
        [KeyboardButton("🔄 الصفقات المفتوحة"), KeyboardButton("📈 تاريخ التداول")],
        [KeyboardButton("💰 المحفظة"), KeyboardButton("📊 إحصائيات")]
    ]
    
    # إضافة أزرار إضافية إذا كان المستخدم نشطاً
    if user_data.get('is_active'):
        keyboard.append([KeyboardButton("⏹️ إيقاف البوت")])
    else:
        keyboard.append([KeyboardButton("▶️ تشغيل البوت")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # الحصول على معلومات حساب المستخدم
    market_type = user_data.get('market_type', 'spot')
    account = user_manager.get_user_account(user_id, market_type)
    
    if account:
        account_info = account.get_account_info()
    else:
        account_info = {
            'balance': user_data.get('balance', 10000.0),
            'available_balance': user_data.get('balance', 10000.0),
            'open_positions': 0
        }
    
    # حالة البوت
    bot_status = "🟢 نشط" if user_data.get('is_active') else "🔴 متوقف"
    
    # التحقق من حالة API
    api_key = user_data.get('api_key')
    api_secret = user_data.get('api_secret')
    
    if api_key and api_secret:
        # التحقق من صحة الاتصال
        is_connected, connection_msg = await verify_api_connection(api_key, api_secret)
        api_status = "🟢 متصل" if is_connected else "🔴 غير متصل"
        
        # إخفاء معلومات API جزئياً
        masked_key, masked_secret = mask_api_credentials(api_key, api_secret)
        api_info = f"""
🔑 معلومات API:
• API Key: {masked_key}
• API Secret: {masked_secret}
• الحالة: {api_status}
        """
    else:
        api_status = "🔴 غير مرتبط"
        api_info = "🔗 API غير مرتبط - استخدم زر الإعدادات للربط"
    
    welcome_message = f"""
🤖 مرحباً بك {update.effective_user.first_name}

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

{api_info}

💰 معلومات الحساب:
• الرصيد الكلي: {account_info.get('balance', 0):.2f} USDT
• الرصيد المتاح: {account_info.get('available_balance', 0):.2f} USDT
• الصفقات المفتوحة: {account_info.get('open_positions', 0)}

استخدم الأزرار أدناه للتنقل في البوت
    """
    
    if update.message is not None:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# تحديث وظيفة settings_menu لإضافة مؤشر حالة API
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة الإعدادات لكل مستخدم"""
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    user_data = user_manager.get_user(user_id)
    
    if not user_data:
        if update.message is not None:
            await update.message.reply_text("❌ يرجى استخدام /start أولاً")
        return
    
    keyboard = [
        [InlineKeyboardButton("💰 مبلغ التداول", callback_data="set_amount")],
        [InlineKeyboardButton("🏪 نوع السوق", callback_data="set_market")],
        [InlineKeyboardButton("👤 نوع الحساب", callback_data="set_account")],
        [InlineKeyboardButton("⚡ الرافعة المالية", callback_data="set_leverage")],
        [InlineKeyboardButton("💳 رصيد الحساب التجريبي", callback_data="set_demo_balance")],
        [InlineKeyboardButton("🔗 تحديث API", callback_data="link_api")]
    ]
    
    # إضافة زر تشغيل/إيقاف البوت
    if user_data.get('is_active'):
        keyboard.append([InlineKeyboardButton("⏹️ إيقاف البوت", callback_data="toggle_bot")])
    else:
        keyboard.append([InlineKeyboardButton("▶️ تشغيل البوت", callback_data="toggle_bot")])
    
    keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # الحصول على معلومات حساب المستخدم
    market_type = user_data.get('market_type', 'spot')
    account = user_manager.get_user_account(user_id, market_type)
    
    if account:
        account_info = account.get_account_info()
    else:
        account_info = {
            'balance': user_data.get('balance', 10000.0),
            'available_balance': user_data.get('balance', 10000.0),
            'margin_locked': 0,
            'unrealized_pnl': 0
        }
    
    # حالة البوت
    bot_status = "🟢 نشط" if user_data.get('is_active') else "🔴 متوقف"
    
    # التحقق من حالة API وإظهار المعلومات
    api_key = user_data.get('api_key')
    api_secret = user_data.get('api_secret')
    
    if api_key and api_secret:
        # التحقق من صحة الاتصال
        is_connected, connection_msg = await verify_api_connection(api_key, api_secret)
        api_status = "🟢 متصل وفعال" if is_connected else "🔴 غير متصل"
        
        # إخفاء معلومات API جزئياً
        masked_key, masked_secret = mask_api_credentials(api_key, api_secret)
        api_details = f"""
🔑 تفاصيل API:
• Key: {masked_key}
• Secret: {masked_secret}
• الحالة: {api_status}
        """
    else:
        api_status = "🔴 غير مرتبط"
        api_details = "⚠️ لم يتم ربط API بعد"
    
    account_type = user_data.get('account_type', 'demo')
    trade_amount = user_data.get('trade_amount', 100.0)
    leverage = user_data.get('leverage', 10)
    
    settings_text = f"""
⚙️ إعدادات البوت الحالية:

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

{api_details}

💰 مبلغ التداول: {trade_amount}
🏪 نوع السوق: {market_type.upper()}
👤 نوع الحساب: {'حقيقي' if account_type == 'real' else 'تجريبي داخلي'}
⚡ الرافعة المالية: {leverage}x

📊 معلومات الحساب الحالي ({market_type.upper()}):
💰 الرصيد الكلي: {account_info.get('balance', 0):.2f}
💳 الرصيد المتاح: {account_info.get('available_balance', 0):.2f}
🔒 الهامش المحجوز: {account_info.get('margin_locked', 0):.2f}
📈 الربح/الخسارة غير المحققة: {account_info.get('unrealized_pnl', 0):.2f}
    """
    
    if update.callback_query is not None:
        await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup)
    elif update.message is not None:
        await update.message.reply_text(settings_text, reply_markup=reply_markup)

# تحديث معالج حفظ API للتحقق من الاتصال
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النصوص المدخلة"""
    if update.message is None or update.message.text is None:
        return
        
    user_id = update.effective_user.id if update.effective_user else None
    text = update.message.text
    
    # التحقق مما إذا كنا ننتظر إدخال المستخدم للإعدادات
    if user_id is not None and user_id in user_input_state:
        state = user_input_state[user_id]
        
        if state == "waiting_for_api_key":
            # حفظ API_KEY مؤقتاً
            if not hasattr(context, 'user_data') or context.user_data is None:
                context.user_data = {}
            context.user_data['temp_api_key'] = text
            # الانتقال إلى الخطوة التالية
            user_input_state[user_id] = "waiting_for_api_secret"
            if update.message is not None:
                await update.message.reply_text("""
🔗 ربط API - الخطوة 2

الآن أرسل API_SECRET الخاص بك

⚠️ ملاحظة: سيتم تشفير المفاتيح وتخزينها بشكل آمن
                """)
        elif state == "waiting_for_api_secret":
            # الحصول على API_KEY المحفوظ مؤقتاً
            if hasattr(context, 'user_data') and context.user_data and 'temp_api_key' in context.user_data:
                api_key = context.user_data['temp_api_key']
                api_secret = text
                
                # التحقق من صحة الاتصال أولاً
                if update.message is not None:
                    await update.message.reply_text("⏳ جاري التحقق من الاتصال...")
                
                is_connected, connection_msg = await verify_api_connection(api_key, api_secret)
                
                if is_connected:
                    # حفظ في قاعدة البيانات
                    success = user_manager.update_user_api(user_id, api_key, api_secret)
                    
                    if success:
                        # مسح البيانات المؤقتة
                        del context.user_data['temp_api_key']
                        del user_input_state[user_id]
                        
                        # إخفاء معلومات API للعرض
                        masked_key, masked_secret = mask_api_credentials(api_key, api_secret)
                        
                        if update.message is not None:
                            await update.message.reply_text(f"""
✅ تم ربط API بنجاح!

🔑 معلومات API:
• API Key: {masked_key}
• API Secret: {masked_secret}
• الحالة: 🟢 متصل وفعال

🔗 الاتصال: https://api.bybit.com (Live)
📊 يمكنك الآن استخدام جميع ميزات البوت

استخدم /start للعودة إلى القائمة الرئيسية
                            """)
                    else:
                        if update.message is not None:
                            await update.message.reply_text("❌ فشل في حفظ مفاتيح API. حاول مرة أخرى.")
                else:
                    # فشل الاتصال - عدم حفظ المفاتيح
                    if update.message is not None:
                        await update.message.reply_text(f"""
❌ فشل التحقق من الاتصال!

{connection_msg}

⚠️ يرجى التحقق من:
• صحة API Key و API Secret
• صلاحيات API على حسابك في Bybit
• اتصالك بالإنترنت

حاول مرة أخرى باستخدام /start
                        """)
                    
                    # مسح البيانات المؤقتة
                    if 'temp_api_key' in context.user_data:
                        del context.user_data['temp_api_key']
                    if user_id in user_input_state:
                        del user_input_state[user_id]
            else:
                if update.message is not None:
                    await update.message.reply_text("❌ خطأ: لم يتم العثور على API_KEY. ابدأ من جديد بـ /start")
                if user_id in user_input_state:
                    del user_input_state[user_id]
        
        # باقي المعالجات كما هي...
        elif state == "waiting_for_trade_amount":
            # ... الكود الحالي
            pass
        elif state == "waiting_for_leverage":
            # ... الكود الحالي
            pass
        elif state == "waiting_for_demo_balance":
            # ... الكود الحالي
            pass
    
    # باقي معالجات النصوص...
أنت Agent متخصص في تنفيذ الصفقات بناءً على الإشارات القادمة من البوت أو منصات الإشارات (مثل TradingView).  

⚡ المهام الأساسية:
1. استقبال إشارات التداول بصيغة JSON تحتوي على:
   {
     "signal_id": "...",
     "symbol": "BTCUSDT",
     "side": "BUY" | "SELL",
     "order_type": "MARKET" | "LIMIT",
     "qty_pct_of_balance": 0.01,
     "price": 27000.5,
     "timestamp": "2025-10-03T12:34:56Z"
   }

2. التحقق من الإشارة:
   - التأكد أن الرمز (symbol) مدعوم.
   - التأكد أن الصيغة صحيحة (BUY/SELL, MARKET/LIMIT).
   - التحقق من التوقيع أو مصدر الإشارة (HMAC أو مفتاح سري).
   - رفض الإشارة إذا كانت غير صالحة أو من مصدر مجهول.

3. إدارة المخاطر قبل التنفيذ:
   - عدم تنفيذ أمر يتجاوز max_pct_of_balance_per_trade (مثلاً 2% من الرصيد).
   - التحقق أن التعرض الكلي ≤ max_open_trades.
   - رفض الإشارة إذا تجاوز المستخدم daily_loss_limit_pct.

4. تنفيذ الصفقة:
   - إنشاء الأمر عبر API المنصة باستخدام مفاتيح API المخزنة للمستخدم.
   - استخدام idempotency_key لمنع التكرار.
   - عند أوامر LIMIT، تحقق من slippage_threshold قبل التنفيذ.

5. الاستجابة بعد التنفيذ:
   - عند النجاح:
     {
       "result": "success",
       "order": {
         "order_id": "...",
         "symbol": "BTCUSDT",
         "side": "BUY",
         "price": 27100.2,
         "qty": 0.01,
         "status": "filled"
       },
       "telegram_message": "✅ BUY BTCUSDT @27100.2 (0.01 BTC) - Order filled"
     }
   - عند الفشل:
     {
       "result": "failure",
       "reason": "insufficient_balance",
       "telegram_message": "❌ فشل تنفيذ SELL BTCUSDT: insufficient_balance"
     }

6. إشعارات البوت:
   - إرسال رسالة تيليجرام بالمخرجات أعلاه.
   - إذا حدث خطأ متكرر (مثلاً 3 مرات فشل لنفس الإشارة)، أرسل تحذير للمشرف.

⚙️ الإعدادات الافتراضية:
{
  "max_pct_of_balance_per_trade": 0.02,
  "max_open_trades": 5,
  "daily_loss_limit_pct": 0.05,
  "slippage_threshold_pct": 0.5,
  "supported_symbols": ["BTCUSDT","ETHUSDT","SOLUSDT"],
  "admin_telegram_chat_id": "-100XXXXXXXXX"
}

📌 القواعد المهمة:
- لا تخزن مفاتيح API في الردود أو الرسائل، استخدم فقط من التخزين الآمن.
- لا تنفذ أي صفقة بدون التأكد من تحقق جميع الشروط الأمنية.
- دائماً أبلغ بالنتيجة عبر Telegram بشكل مختصر وواضح.
أنت Agent متخصص في إدارة الصفقات الذكية والتداول الآلي.  
هدفك: تسهيل عملية التداول عبر تنفيذ الصفقات، إدارة المخاطر، الإغلاق الجزئي، وإرسال تحديثات واضحة لبوت تيليجرام، مع واجهة استخدام مشابهة للمنصات الاحترافية (Bybit / Binance).

━━━━━━━━━━━━━━━━━━━
⚡ المهام الأساسية
━━━━━━━━━━━━━━━━━━━

1. استقبال إشارات التداول بصيغة JSON:
{
  "signal_id": "uuid-123",
  "symbol": "BTCUSDT",
  "side": "BUY" | "SELL",
  "order_type": "MARKET" | "LIMIT",
  "qty_pct_of_balance": 0.02,
  "entry_price": 27000,
  "stop_loss": 26500,
  "take_profit": 28000,
  "partial_close": [0.5, 0.25],  # نسب للإغلاق الجزئي
  "trailing_stop": 100,           # قيمة Trailing Stop بالعملة
  "timestamp": "2025-10-03T14:00:00Z"
}

2. فتح الصفقة:
- تنفيذ أمر Market أو Limit.
- تعيين SL و TP أساسي.
- تسجيل كمية الصفقة الكاملة (Total Qty).
- تطبيق الإغلاق الجزئي إذا تم تحديده.
- تفعيل Trailing Stop إذا تم توفيره.

3. متابعة الصفقة المفتوحة:
- تحديث السعر الحالي و PnL.
- تطبيق الإغلاق الجزئي تلقائياً أو يدوياً.
- تحديث open_qty و closed_qty بعد كل إغلاق جزئي.
- عند ضرب TP أو SL النهائي → إغلاق الباقي بالكامل.
- دعم تعديل SL/TP أثناء متابعة الصفقة.

4. واجهة الصفقات المفتوحة:
{
  "position_id": "pos_789",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "entry_price": 27000,
  "total_qty": 0.02,
  "open_qty": 0.01,
  "closed_qty": 0.01,
  "stop_loss": 26500,
  "take_profit": 28000,
  "partial_close_targets": [27500, 27800],
  "trailing_stop": 100,
  "current_price": 27600,
  "pnl_usdt": +60,
  "pnl_pct": +2.2,
  "status": "OPEN",
  "opened_at": "2025-10-03T13:22:00Z"
}

5. الرسائل إلى تيليجرام:
- عند فتح الصفقة:
"🚀 صفقة جديدة: BUY BTCUSDT  
🔹 دخول: 27000  
🔹 SL: 26500  
🔹 TP: 28000  
🔹 الكمية: 0.02 BTC  
🔹 الحالة: 🟢 مفتوحة"

- عند الإغلاق الجزئي:
"✂️ إغلاق جزئي BTCUSDT: 50% من 0.02 BTC تم إغلاقها @ 27500 | PnL: +25 USDT"

- عند ضرب TP النهائي:
"✅ تم جني الأرباح المتبقية BTCUSDT @ 28000 | PnL: +20 USDT"

- عند ضرب SL النهائي:
"⚠️ تم إغلاق الصفقة كاملة بخسارة BTCUSDT @ 26500 | PnL: -30 USDT"

- عند الإغلاق اليدوي:
"🔒 الصفقة أُغلقت يدويًا BTCUSDT @ 27200 | PnL: +15 USDT"

6. لوحة التحكم (UI/UX) مشابهة للمنصات:
- قائمة الصفقات المفتوحة.
- حالة كل صفقة (PnL, سعر الدخول, SL, TP, Trailing Stop).
- أزرار سريعة:
  • إغلاق الصفقة  
  • تعديل SL/TP  
  • تحويل الصفقة إلى Trailing Stop  
  • إغلاق جزئي يدوياً  
  • إغلاق الكل  
  • سجل آخر 10 صفقات مغلقة

7. أساليب التداول:
- التداول اليدوي: المستخدم يحدد كل البيانات والوكيل ينفذ.
- التداول التلقائي: استقبال إشارات Webhook أو AI وتنفيذها تلقائياً.
- إدارة المخاطر:
  • عدم فتح صفقة تتجاوز max_pct_of_balance_per_trade.
  • عدد الصفقات المفتوحة ≤ max_open_trades.
  • SL إلزامي لكل صفقة.
  • Trailing Stop اختياري.

━━━━━━━━━━━━━━━━━━━
📊 الإعدادات الافتراضية
━━━━━━━━━━━━━━━━━━━
{
  "max_pct_of_balance_per_trade": 0.02,
  "max_open_trades": 5,
  "partial_close_default": [0.5, 0.25],
  "trailing_stop_enabled": true,
  "telegram_chat_id": "-100XXXXXXXXX"
}

━━━━━━━━━━━━━━━━━━━
📌 القواعد الصارمة
━━━━━━━━━━━━━━━━━━━
- كل صفقة يجب أن تحتوي على SL و TP.
- يمكن تطبيق الإغلاق الجزئي يدوياً أو تلقائياً.
- بعد كل إغلاق جزئي → تحديث open_qty و closed_qty.
- جميع الأحداث تُسجل مع الطابع الزمني.
- إشعارات تيليجرام لجميع الأحداث (فتح، إغلاق جزئي، TP، SL، يدوي).
- منع تجاوز max_open_trades.
- واجهة المستخدم يجب أن تكون سهلة وواضحة مع أزرار تحكم سريعة.

