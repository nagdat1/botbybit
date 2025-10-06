# ⚡ دليل البدء السريع - نظام المطورين

## 🎯 3 خطوات فقط للبدء!

---

## 📝 الخطوة 1: التهيئة

شغّل السكريبت التالي لإنشاء حساب المطور:

```bash
python init_developers.py
```

**النتيجة المتوقعة:**
```
🚀 بدء تهيئة المطورين...
✅ تم إنشاء المطور Nagdat بنجاح
✅ تم تهيئة المطورين بنجاح
```

---

## 🧪 الخطوة 2: الاختبار

اختبر أن النظام يعمل:

```python
python -c "
from developer_manager import developer_manager
devs = developer_manager.get_all_active_developers()
print(f'✅ عدد المطورين: {len(devs)}')
if devs:
    print(f'✅ المطور الأول: {devs[0][\"developer_name\"]}')
"
```

**النتيجة المتوقعة:**
```
✅ عدد المطورين: 1
✅ المطور الأول: Nagdat
```

---

## 🔗 الخطوة 3: التكامل مع البوت

في ملف البوت الرئيسي (مثل `app.py` أو `bybit_trading_bot.py`):

### أ) استيراد المدير

```python
from developer_manager import developer_manager
from developer_config import is_developer
```

### ب) تهيئة المطورين عند البدء

```python
import init_developers

# في دالة البدء
def startup():
    # تهيئة المطورين
    init_developers.init_developers()
    
    # ... باقي الكود
```

### ج) معالجة أمر /start

```python
async def start_command(update, context):
    user_id = update.effective_user.id
    
    # التحقق من نوع المستخدم
    if developer_manager.is_developer(user_id):
        # عرض لوحة المطور
        await show_developer_panel(update, context)
    else:
        # عرض قائمة المستخدم العادي
        await show_user_menu(update, context)
```

### د) إضافة زر متابعة المطور للمستخدمين

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_user_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 حسابي", callback_data="account")],
        [InlineKeyboardButton("💼 الصفقات", callback_data="positions")],
        [InlineKeyboardButton("⚡ متابعة إشارات Nagdat", callback_data="follow_nagdat")],
    ]
    return InlineKeyboardMarkup(keyboard)
```

### هـ) معالجة المتابعة

```python
async def handle_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "follow_nagdat":
        developer_id = 8169000394  # ID المطور Nagdat
        
        # إضافة المتابع
        success = developer_manager.add_follower(developer_id, user_id)
        
        if success:
            await query.answer("✅ تم متابعة المطور بنجاح!")
        else:
            await query.answer("⚠️ أنت تتابع المطور بالفعل")
```

---

## 🎨 مثال كامل

إليك مثال كامل لكيفية دمج النظام:

```python
# في أعلى الملف
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from developer_manager import developer_manager
from developer_config import is_developer
import init_developers

# دالة البدء
async def start(update, context):
    user_id = update.effective_user.id
    
    if developer_manager.is_developer(user_id):
        text = "👨‍💻 مرحباً بك في لوحة التحكم للمطورين"
        keyboard = [
            [InlineKeyboardButton("📡 إرسال إشارة", callback_data="broadcast")],
            [InlineKeyboardButton("👥 المتابعين", callback_data="followers")],
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
        ]
    else:
        text = "🤖 مرحباً بك في بوت التداول"
        keyboard = [
            [InlineKeyboardButton("📊 حسابي", callback_data="account")],
            [InlineKeyboardButton("⚡ متابعة إشارات Nagdat", callback_data="follow")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# دالة معالجة الأزرار
async def button_handler(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "follow":
        developer_id = 8169000394
        success = developer_manager.add_follower(developer_id, user_id)
        if success:
            await query.answer("✅ تم المتابعة!")
        else:
            await query.answer("⚠️ تتابع بالفعل")
    
    elif query.data == "broadcast":
        if developer_manager.is_developer(user_id):
            # عرض نموذج إرسال الإشارة
            await query.message.reply_text("إرسال إشارة...")
    
    elif query.data == "followers":
        if developer_manager.is_developer(user_id):
            count = developer_manager.get_follower_count(user_id)
            await query.message.reply_text(f"👥 عدد المتابعين: {count}")

# في الدالة الرئيسية
def main():
    # تهيئة المطورين
    init_developers.init_developers()
    
    # إنشاء البوت
    app = Application.builder().token("YOUR_TOKEN").build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

## 📡 إرسال إشارة للمتابعين

```python
# في معالج إرسال الإشارة
async def send_signal(developer_id, signal_data):
    result = developer_manager.broadcast_signal_to_followers(
        developer_id=developer_id,
        signal_data={
            'symbol': 'BTCUSDT',
            'action': 'BUY',
            'price': 50000,
            'amount': 100
        }
    )
    
    if result['success']:
        print(f"✅ تم إرسال الإشارة إلى {result['follower_count']} متابع")
        return result['sent_to']  # قائمة IDs المتابعين
    else:
        print(f"❌ فشل: {result['message']}")
        return []
```

---

## 🎓 خطوات إضافية (اختيارية)

### 1. إضافة مطور آخر

في `developer_config.py`:

```python
ADDITIONAL_DEVELOPERS = [
    {
        'developer_id': 123456789,
        'developer_name': 'مطور آخر',
        'developer_key': 'KEY-123',
        'webhook_url': None,
        'is_active': True,
        'can_broadcast': True
    }
]
```

ثم شغّل:
```bash
python init_developers.py
```

### 2. تخصيص الرسائل

عدّل `developer_config.py`:

```python
DEVELOPER_MESSAGES = {
    'welcome_developer': "رسالة ترحيب مخصصة...",
    # ... إلخ
}
```

### 3. تعديل الصلاحيات

في `developer_config.py`:

```python
DEVELOPER_PERMISSIONS = {
    'can_broadcast_signals': True,
    'can_manage_users': True,
    # ... إلخ
}
```

---

## ✅ قائمة التحقق النهائية

- [x] تشغيل `init_developers.py`
- [x] اختبار وجود المطور في قاعدة البيانات
- [x] إضافة الاستيراد في ملف البوت
- [x] إضافة معالج /start مع التمييز
- [x] إضافة زر المتابعة للمستخدمين
- [x] اختبار المتابعة
- [x] اختبار إرسال إشارة

---

## 🚀 جاهز!

الآن نظام المطورين يعمل بالكامل ومتكامل مع البوت!

للحصول على شرح مفصّل، راجع:
- 📕 [`DEVELOPER_SYSTEM_GUIDE.md`](DEVELOPER_SYSTEM_GUIDE.md)
- 💡 [`developer_example.py`](developer_example.py)

---

**محدث في:** 2024  
**بواسطة:** Nagdat

