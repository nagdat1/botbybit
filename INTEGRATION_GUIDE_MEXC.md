# دليل دمج MEXC مع النظام الحالي

## 🔗 كيفية ربط MEXC API مع البوت

### الخطوة 1: إضافة مفاتيح API

أنشئ أو عدّل ملف `.env` في مجلد المشروع وأضف:

```env
# مفاتيح MEXC API
MEXC_API_KEY=
MEXC_API_SECRET=
```

### الخطوة 2: تعديل ملف web_server.py

يجب تعديل `web_server.py` لدعم MEXC. أضف الكود التالي:

#### في بداية الملف (بعد الاستيرادات):

```python
from mexc_trading_bot import create_mexc_bot
from config import MEXC_API_KEY, MEXC_API_SECRET
```

#### في دالة `personal_webhook` (حوالي السطر 143):

ابحث عن هذا الجزء:
```python
# معالجة الإشارة باستخدام نفس دالة البوت
def process_signal_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(self.trading_bot.process_signal(data))
```

واستبدله بـ:

```python
# معالجة الإشارة حسب المنصة المحددة
def process_signal_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # التحقق من المنصة المطلوبة
        exchange = data.get('exchange', 'BYBIT').upper()
        
        if exchange == 'MEXC':
            # معالجة إشارة MEXC
            loop.run_until_complete(self.process_mexc_signal(data, user_id))
        else:
            # معالجة إشارة Bybit (الافتراضي)
            loop.run_until_complete(self.trading_bot.process_signal(data))
```

#### أضف دالة جديدة في class WebServer:

```python
async def process_mexc_signal(self, signal_data: dict, user_id: int):
    """معالجة إشارة MEXC"""
    try:
        from user_manager import user_manager
        from telegram import Bot
        
        # الحصول على بيانات المستخدم
        user_data = user_manager.get_user(user_id)
        if not user_data:
            print(f"❌ المستخدم {user_id} غير موجود")
            return
        
        # التحقق من أن المستخدم يستخدم MEXC
        if user_data.get('exchange', 'bybit').lower() != 'mexc':
            print(f"⚠️ المستخدم {user_id} لا يستخدم MEXC")
            return
        
        # التحقق من أن نوع السوق هو spot فقط
        if user_data.get('market_type', 'spot') != 'spot':
            # إرسال رسالة تحذير
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ تحذير: MEXC تدعم التداول الفوري (Spot) فقط\nتم تغيير الإعدادات إلى Spot تلقائياً"
            )
            user_data['market_type'] = 'spot'
            user_manager.update_user_settings(user_id, {'market_type': 'spot'})
        
        # إنشاء بوت MEXC
        mexc_bot = create_mexc_bot(
            api_key=user_data.get('mexc_api_key', MEXC_API_KEY),
            api_secret=user_data.get('mexc_api_secret', MEXC_API_SECRET)
        )
        
        # استخراج معلومات الإشارة
        action = signal_data.get('action', 'buy').upper()
        symbol = signal_data.get('symbol', 'BTCUSDT')
        
        # الحصول على السعر الحالي
        current_price = mexc_bot.get_ticker_price(symbol)
        if not current_price:
            print(f"❌ فشل في الحصول على سعر {symbol}")
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text=f"❌ فشل في الحصول على سعر {symbol} من MEXC"
            )
            return
        
        # حساب الكمية بناءً على مبلغ التداول
        trade_amount = user_data.get('trade_amount', 100.0)
        
        if action == 'BUY':
            # للشراء: نحسب كم من العملة الأساسية يمكننا شراؤها
            quantity = trade_amount / current_price
            side = 'BUY'
        else:
            # للبيع: نحتاج إلى معرفة الرصيد المتاح
            balance = mexc_bot.get_account_balance()
            base_asset = symbol.replace('USDT', '').replace('USDC', '').replace('BUSD', '')
            
            if balance and base_asset in balance['balances']:
                quantity = min(
                    balance['balances'][base_asset]['free'],
                    trade_amount / current_price
                )
            else:
                print(f"❌ لا يوجد رصيد كافٍ من {base_asset}")
                bot = Bot(token=TELEGRAM_TOKEN)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"❌ لا يوجد رصيد كافٍ من {base_asset} للبيع"
                )
                return
            side = 'SELL'
        
        # تنفيذ الأمر
        print(f"📊 تنفيذ أمر MEXC: {side} {quantity:.8f} {symbol} @ ${current_price:,.2f}")
        
        order = mexc_bot.place_spot_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='MARKET'
        )
        
        if order:
            # إرسال إشعار بنجاح التنفيذ
            bot = Bot(token=TELEGRAM_TOKEN)
            message = f"""
✅ تم تنفيذ الأمر على MEXC

🏦 المنصة: MEXC
📊 الزوج: {symbol}
📈 النوع: {side}
💰 الكمية: {quantity:.8f}
💵 السعر: ${current_price:,.2f}
🆔 رقم الأمر: {order.get('order_id', 'N/A')}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            await bot.send_message(chat_id=user_id, text=message)
            print(f"✅ تم تنفيذ أمر MEXC بنجاح: {order}")
        else:
            print(f"❌ فشل تنفيذ أمر MEXC")
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text=f"❌ فشل تنفيذ الأمر على MEXC"
            )
    
    except Exception as e:
        print(f"❌ خطأ في معالجة إشارة MEXC: {e}")
        import traceback
        traceback.print_exc()
```

### الخطوة 3: تعديل قاعدة البيانات لدعم MEXC

في ملف `database.py`، أضف حقول MEXC إلى جدول المستخدمين:

```python
# في دالة create_tables أو init_database
cursor.execute('''
    ALTER TABLE users ADD COLUMN IF NOT EXISTS exchange TEXT DEFAULT 'bybit';
    ALTER TABLE users ADD COLUMN IF NOT EXISTS mexc_api_key TEXT;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS mexc_api_secret TEXT;
''')
```

### الخطوة 4: تعديل user_manager.py

أضف دعم لحفظ واسترجاع إعدادات MEXC:

```python
def update_user_exchange(self, user_id: int, exchange: str, api_key: str = None, api_secret: str = None):
    """تحديث منصة التداول للمستخدم"""
    if user_id in self.users:
        self.users[user_id]['exchange'] = exchange.lower()
        
        if exchange.lower() == 'mexc':
            if api_key:
                self.users[user_id]['mexc_api_key'] = api_key
            if api_secret:
                self.users[user_id]['mexc_api_secret'] = api_secret
            
            # MEXC تدعم Spot فقط
            self.users[user_id]['market_type'] = 'spot'
        
        # حفظ في قاعدة البيانات
        db_manager.update_user_settings(user_id, {
            'exchange': exchange.lower(),
            'mexc_api_key': api_key,
            'mexc_api_secret': api_secret,
            'market_type': self.users[user_id]['market_type']
        })
```

### الخطوة 5: إضافة أوامر Telegram لإعداد MEXC

في ملف `bybit_trading_bot.py` أو ملف منفصل للأوامر، أضف:

```python
async def cmd_set_mexc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر لإعداد MEXC"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("✅ استخدام MEXC", callback_data="exchange_mexc")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🏦 إعداد منصة MEXC

⚠️ ملاحظة هامة:
• MEXC تدعم التداول الفوري (Spot) فقط
• لا يوجد دعم لتداول الفيوتشر

📝 لاستخدام MEXC:
1. احصل على API Key من موقع MEXC
2. أرسل الأمر: /set_mexc_api
3. أدخل API Key و Secret

📚 للمزيد: راجع README_MEXC.md
"""
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def cmd_set_mexc_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر لإدخال مفاتيح MEXC API"""
    user_id = update.effective_user.id
    
    message = """
🔑 إعداد MEXC API Keys

أرسل المفاتيح بالصيغة التالية:
API_KEY:API_SECRET

مثال:
mx0vglBqh6abc123:abc123xyz456def789

⚠️ تأكد من:
• تفعيل صلاحية Spot Trading
• عدم تفعيل صلاحية Withdrawal
"""
    
    await update.message.reply_text(message)
    # حفظ حالة انتظار المفاتيح
    context.user_data['awaiting_mexc_keys'] = True

# معالج استقبال المفاتيح
async def handle_mexc_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة مفاتيح MEXC المدخلة"""
    if not context.user_data.get('awaiting_mexc_keys'):
        return
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    try:
        # تقسيم المفاتيح
        if ':' not in text:
            await update.message.reply_text("❌ صيغة خاطئة. استخدم: API_KEY:API_SECRET")
            return
        
        api_key, api_secret = text.split(':', 1)
        
        # اختبار المفاتيح
        from mexc_trading_bot import create_mexc_bot
        test_bot = create_mexc_bot(api_key, api_secret)
        
        if test_bot.test_connection():
            # حفظ المفاتيح
            user_manager.update_user_exchange(user_id, 'mexc', api_key, api_secret)
            
            await update.message.reply_text("""
✅ تم حفظ مفاتيح MEXC بنجاح!

🎉 يمكنك الآن:
• استقبال إشارات من TradingView
• التداول على MEXC (Spot فقط)

📊 استخدم /status لعرض الحالة
""")
            context.user_data['awaiting_mexc_keys'] = False
        else:
            await update.message.reply_text("""
❌ فشل الاتصال بـ MEXC

تحقق من:
• صحة المفاتيح
• تفعيل API Key في حسابك
• صلاحيات Spot Trading
""")
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

# تسجيل الأوامر
application.add_handler(CommandHandler("set_mexc", cmd_set_mexc))
application.add_handler(CommandHandler("set_mexc_api", cmd_set_mexc_api))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mexc_keys))
```

## 📋 ملخص الخطوات

1. ✅ أضف مفاتيح MEXC في ملف `.env`
2. ✅ عدّل `web_server.py` لإضافة دعم MEXC
3. ✅ عدّل `database.py` لإضافة حقول MEXC
4. ✅ عدّل `user_manager.py` لإدارة إعدادات MEXC
5. ✅ أضف أوامر Telegram لإعداد MEXC
6. ✅ اختبر باستخدام `python test_mexc_connection.py`

## 🧪 الاختبار

بعد التعديلات، اختبر النظام:

```bash
# اختبار الاتصال بـ MEXC
python test_mexc_connection.py

# اختبار إرسال إشارة
python test_send_signal.py
# اختر المنصة: 2 (MEXC)
```

## 📝 ملاحظات مهمة

- ⚠️ MEXC تدعم **Spot فقط** - لا فيوتشر
- 🔐 احفظ المفاتيح بشكل آمن
- 📊 تأكد من وجود رصيد كافٍ للتداول
- 🧪 اختبر بمبالغ صغيرة أولاً

## 🆘 المساعدة

إذا واجهت مشاكل، راجع:
- `README_MEXC.md` - دليل شامل
- `trading_bot.log` - سجل الأخطاء
- [MEXC API Docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/)

