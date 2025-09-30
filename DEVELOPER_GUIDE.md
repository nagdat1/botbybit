# دليل المطورين - بوت التداول المتكامل

## 🏗️ بنية المشروع

### الملفات الرئيسية

#### 1. run_with_server.py (ملف التشغيل الرئيسي)
**الوصف**: نقطة البداية للنظام المتكامل، يجمع بين النظام القديم والجديد
```python
class IntegratedTradingBot:
    """البوت المتكامل الذي يجمع النظام القديم والجديد"""
    
    async def initialize(self):
        """تهيئة النظام المتكامل"""
        await self._initialize_new_system()  # النظام الجديد
        await self._initialize_old_system()  # النظام القديم
        await self._initialize_web_server()  # سيرفر الويب
```

**المسؤوليات**:
- تهيئة جميع الأنظمة
- معالجة أوامر التليجرام
- إدارة السيرفر الويب
- توحيد الواجهة بين النظامين

#### 2. user_manager.py (إدارة المستخدمين)
**الوصف**: نظام إدارة المستخدمين مع بيئات منفصلة
```python
class UserEnvironment:
    """بيئة المستخدم المنفصلة"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_data = None
        self.open_orders = []
        self.is_active = True
```

**المسؤوليات**:
- إدارة بيئة منفصلة لكل مستخدم
- حفظ الإعدادات والمفاتيح
- تتبع الصفقات والإحصائيات

#### 3. api_manager.py (إدارة API)
**الوصف**: إدارة اتصالات Bybit API لكل مستخدم
```python
class APIManager:
    """مدير API مع دعم متعدد المستخدمين"""
    
    def get_user_api(self, user_id: int) -> BybitAPI:
        """الحصول على API للمستخدم"""
```

**المسؤوليات**:
- إدارة مفاتيح API لكل مستخدم
- التحقق من صحة المفاتيح
- تنفيذ الطلبات إلى Bybit

#### 4. order_manager.py (إدارة الصفقات)
**الوصف**: إدارة الصفقات مع TP/SL متقدم
```python
class OrderManager:
    """مدير الصفقات مع TP/SL متقدم"""
    
    def create_order(self, user_id, symbol, side, quantity, price):
        """إنشاء صفقة جديدة"""
```

**المسؤوليات**:
- إنشاء وإدارة الصفقات
- مراقبة أسعار TP/SL
- الإغلاق الجزئي والكامل

#### 5. security_manager.py (إدارة الأمان)
**الوصف**: نظام حماية شامل
```python
class SecurityManager:
    """مدير الأمان والحماية"""
    
    def authenticate_user(self, user_id, action):
        """التحقق من صلاحية المستخدم"""
```

**المسؤوليات**:
- التحقق من صلاحيات المستخدمين
- حماية من معدل الطلبات الزائد
- كشف الأنشطة المشبوهة

#### 6. ui_manager.py (إدارة الواجهة)
**الوصف**: إدارة واجهات المستخدم والرسائل
```python
class UIManager:
    """مدير الواجهات والرسائل"""
    
    def get_main_menu_keyboard(self, user_id):
        """الحصول على لوحة المفاتيح الرئيسية"""
```

**المسؤوليات**:
- إنشاء لوحات المفاتيح
- تنسيق الرسائل
- إدارة حالة المستخدم

#### 7. database.py (قاعدة البيانات)
**الوصف**: إدارة قاعدة بيانات SQLite
```python
class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
```

**المسؤوليات**:
- إدارة جداول قاعدة البيانات
- حفظ واسترجاع البيانات
- إحصائيات المستخدمين

#### 8. web_server.py (السيرفر الويب)
**الوصف**: سيرفر Flask لاستقبال webhooks
```python
class WebServer:
    """سيرفر الويب لاستقبال الإشارات"""
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """استقبال إشارات TradingView"""
```

**المسؤوليات**:
- استقبال webhooks من TradingView
- عرض لوحة تحكم ويب
- مراقبة حالة النظام

#### 9. bybit_trading_bot.py (النظام القديم)
**الوصف**: البوت القديم للتوافق
```python
class TradingBot:
    """فئة البوت الرئيسية مع دعم محسن للفيوتشر"""
    
    def get_current_account(self):
        """الحصول على الحساب الحالي"""
```

**المسؤوليات**:
- دعم النظام القديم
- إدارة حسابات تجريبية
- التوافق مع الإشارات الخارجية

## 🔄 تدفق العمل

### 1. تدفق تهيئة النظام
```
run_with_server.py (main)
    ├── IntegratedTradingBot.initialize()
    │   ├── _initialize_new_system()
    │   │   ├── database.init_database()
    │   │   ├── security_manager.start_monitoring()
    │   │   ├── bot_controller.start_monitoring()
    │   │   └── order_manager.start_price_monitoring()
    │   ├── _initialize_old_system()
    │   │   └── bybit_trading_bot.TradingBot()
    │   └── _initialize_web_server()
    │       └── web_server.WebServer()
    └── start_telegram_bot()
        └── _setup_integrated_handlers()
```

### 2. تدفق معالجة أمر /start
```
User sends /start
    ├── _handle_start()
    │   ├── security_manager.authenticate_user()
    │   ├── user_manager.get_user_environment()
    │   │   └── db_manager.add_user() (if new)
    │   └── _show_integrated_menu()
    │       ├── ui_manager.get_main_menu_keyboard()
    │       └── send welcome message
```

### 3. تدفق معالجة أمر /buy
```
User sends /buy BTCUSDT 0.001
    ├── _handle_buy()
    │   ├── security_manager.authenticate_user()
    │   ├── user_manager.is_user_active()
    │   ├── api_manager.has_user_api()
    │   ├── api_manager.get_user_price()
    │   └── commands.handle_buy()
    │       ├── _execute_trade()
    │       │   └── order_manager.create_order()
    │       │       ├── db_manager.create_order()
    │       │       └── db_manager.update_user_stats()
    │       └── send confirmation message
```

### 4. تدفق استقبال Webhook
```
TradingView sends webhook
    ├── web_server.webhook()
    │   ├── Parse JSON signal
    │   ├── security_manager.check_rate_limit()
    │   ├── user_manager.get_user_environment()
    │   └── order_manager.process_signal()
    │       ├── api_manager.get_user_price()
    │       ├── order_manager.create_order()
    │       └── send telegram notification
```

## 🔧 إضافة ميزة جديدة

### مثال: إضافة أمر /stats لعرض إحصائيات مفصلة

#### 1. إضافة الدالة في commands.py
```python
async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /stats"""
    try:
        user_id = update.effective_user.id
        
        # الحصول على البيانات
        user_env = user_manager.get_user_environment(user_id)
        stats = user_env.get_trading_stats()
        balance = user_env.get_balance_info()
        
        # تنسيق الرسالة
        stats_text = f"""
📊 إحصائيات مفصلة

💰 الرصيد: {balance['balance']:.2f} USDT
📈 إجمالي الصفقات: {stats['total_trades']}
✅ الصفقات الرابحة: {stats['winning_trades']}
❌ الصفقات الخاسرة: {stats['losing_trades']}
🎯 معدل النجاح: {stats['win_rate']:.1f}%
        """
        
        await update.message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"خطأ في معالجة /stats: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض الإحصائيات")
```

#### 2. إضافة المعالج في run_with_server.py
```python
def _setup_integrated_handlers(self, application):
    # ... المعالجات الموجودة
    application.add_handler(CommandHandler("stats", self._handle_stats))

async def _handle_stats(self, update, context):
    """معالجة أمر /stats المتكامل"""
    from commands import command_handler
    await command_handler.handle_stats(update, context)
```

#### 3. إضافة زر في ui_manager.py
```python
def get_main_menu_keyboard(self, user_id):
    keyboard = [
        # ... الأزرار الموجودة
        [KeyboardButton("📊 الإحصائيات المفصلة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
```

## 🧪 الاختبار

### 1. اختبار محلي
```bash
# تشغيل البوت محلياً
python run_with_server.py

# الاختبار عبر التليجرام
/start
/balance
/buy BTCUSDT 0.001
```

### 2. اختبار Webhook
```bash
# إرسال webhook محلي
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

### 3. اختبار على Railway
```bash
# بعد النشر على Railway
curl -X POST https://your-app.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "action": "buy"}'
```

## 🐛 تصحيح الأخطاء

### 1. فحص السجلات
```python
# قراءة ملف السجل
tail -f trading_bot.log

# البحث عن أخطاء محددة
grep "ERROR" trading_bot.log
```

### 2. استخدام Debugger
```python
import pdb

# إضافة نقطة توقف
pdb.set_trace()
```

### 3. التحقق من قاعدة البيانات
```python
import sqlite3

conn = sqlite3.connect('trading_bot.db')
cursor = conn.cursor()

# عرض المستخدمين
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

# عرض الصفقات
cursor.execute("SELECT * FROM orders WHERE status='open'")
print(cursor.fetchall())
```

## 📚 موارد إضافية

### وثائق Bybit API
- [Bybit API Documentation](https://bybit-exchange.github.io/docs/v5/intro)
- [Authentication Guide](https://bybit-exchange.github.io/docs/v5/guide#authentication)

### وثائق Python Telegram Bot
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)

### Flask Documentation
- [Flask Quickstart](https://flask.palletsprojects.com/en/2.3.x/quickstart/)

## 🔒 الأمان

### Best Practices
1. **لا تشارك مفاتيح API**: احتفظ بها آمنة
2. **استخدم متغيرات البيئة**: لا تضع المفاتيح في الكود
3. **فعّل Rate Limiting**: لحماية من الطلبات الزائدة
4. **راجع السجلات**: بانتظام للتحقق من الأنشطة

## 🤝 المساهمة

### كيفية المساهمة
1. Fork المشروع
2. أنشئ branch: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. افتح Pull Request

### معايير الكود
- استخدم PEP 8 للتنسيق
- أضف docstrings للدوال
- اكتب unit tests
- وثّق التغييرات في CHANGELOG.md

---

**آخر تحديث**: 30 سبتمبر 2025
