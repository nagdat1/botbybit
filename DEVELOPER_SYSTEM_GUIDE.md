# 📖 دليل نظام المطورين

## نظرة عامة

تم تطوير نظام منفصل لإدارة المطورين بشكل مستقل عن نظام المستخدمين العاديين. يوفر هذا النظام صلاحيات خاصة للمطورين لإدارة البوت وإرسال الإشارات.

---

## 📁 الملفات الرئيسية

### 1. `developer_manager.py`
مدير المطورين الرئيسي الذي يحتوي على:
- إدارة حسابات المطورين
- إدارة المتابعين
- إرسال الإشارات للمتابعين
- إحصائيات المطورين

### 2. `developer_config.py`
ملف إعدادات المطورين يحتوي على:
- معلومات المطور الرئيسي
- قائمة المطورين الإضافيين
- صلاحيات المطورين
- رسائل النظام

### 3. `init_developers.py`
سكريبت تهيئة المطورين:
- يتم تشغيله عند بدء البوت لأول مرة
- ينشئ حسابات المطورين في قاعدة البيانات
- يحدث معلومات المطورين الموجودين

---

## 🗄️ قاعدة البيانات

### جداول المطورين

#### 1. جدول `developers`
```sql
CREATE TABLE developers (
    developer_id INTEGER PRIMARY KEY,
    developer_name TEXT NOT NULL,
    developer_key TEXT UNIQUE,
    webhook_url TEXT,
    is_active BOOLEAN DEFAULT 1,
    can_broadcast BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 2. جدول `developer_followers`
```sql
CREATE TABLE developer_followers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    developer_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (developer_id) REFERENCES developers (developer_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    UNIQUE(developer_id, user_id)
)
```

#### 3. جدول `developer_signals`
```sql
CREATE TABLE developer_signals (
    signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    developer_id INTEGER NOT NULL,
    signal_data TEXT NOT NULL,
    target_followers TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (developer_id) REFERENCES developers (developer_id)
)
```

---

## 🔧 كيفية الاستخدام

### 1. إضافة مطور جديد

قم بتعديل ملف `developer_config.py`:

```python
ADDITIONAL_DEVELOPERS = [
    {
        'developer_id': 123456789,
        'developer_name': 'اسم المطور',
        'developer_key': 'UNIQUE-KEY-HERE',
        'webhook_url': None,
        'is_active': True,
        'can_broadcast': True
    }
]
```

### 2. تهيئة المطورين

```bash
python init_developers.py
```

### 3. استخدام مدير المطورين في الكود

```python
from developer_manager import developer_manager

# التحقق من أن المستخدم مطور
if developer_manager.is_developer(user_id):
    print("هذا المستخدم مطور")

# الحصول على معلومات المطور
dev_info = developer_manager.get_developer(developer_id)

# إضافة متابع
developer_manager.add_follower(developer_id, user_id)

# إرسال إشارة للمتابعين
result = developer_manager.broadcast_signal_to_followers(
    developer_id=developer_id,
    signal_data={
        'symbol': 'BTCUSDT',
        'action': 'BUY',
        'price': 50000
    }
)
```

---

## 🔐 الصلاحيات

### صلاحيات المطورين
- ✅ إرسال إشارات لجميع المتابعين
- ✅ إدارة المستخدمين
- ✅ مشاهدة جميع الصفقات
- ✅ تعديل إعدادات البوت
- ✅ إرسال إشعارات جماعية
- ✅ مشاهدة الإحصائيات
- ✅ تصدير البيانات

### الفرق بين المطورين والمستخدمين

| الميزة | المطور | المستخدم العادي |
|--------|---------|------------------|
| إرسال إشارات للجميع | ✅ | ❌ |
| إدارة المستخدمين | ✅ | ❌ |
| مشاهدة صفقات الجميع | ✅ | ❌ (صفقاته فقط) |
| تعديل إعدادات البوت | ✅ | ❌ |
| استقبال الإشارات | ✅ | ✅ |
| التداول الشخصي | ✅ | ✅ |

---

## 📊 نظام المتابعة

### كيف يعمل نظام المتابعة؟

1. **المستخدم يتابع المطور**
   ```python
   developer_manager.add_follower(developer_id, user_id)
   ```

2. **المطور يرسل إشارة**
   ```python
   result = developer_manager.broadcast_signal_to_followers(
       developer_id=developer_id,
       signal_data=signal_data
   )
   ```

3. **الإشارة تصل لجميع المتابعين تلقائياً**

### إدارة المتابعين

```python
# الحصول على عدد المتابعين
count = developer_manager.get_follower_count(developer_id)

# الحصول على قائمة المتابعين
followers = developer_manager.get_followers(developer_id)

# التحقق من أن مستخدم يتابع المطور
is_following = developer_manager.is_following(developer_id, user_id)

# إزالة متابع
developer_manager.remove_follower(developer_id, user_id)
```

---

## 📈 الإحصائيات

### الحصول على إحصائيات المطور

```python
stats = developer_manager.get_developer_statistics(developer_id)

# النتيجة:
{
    'developer_id': 8169000394,
    'follower_count': 150,
    'is_active': True,
    'can_broadcast': True,
    'total_signals': 523
}
```

---

## 🔄 التكامل مع البوت الموجود

### في ملف `bybit_trading_bot.py` أو `app.py`

```python
from developer_manager import developer_manager
from user_manager import user_manager
import init_developers

# تهيئة المطورين عند بدء البوت
init_developers.init_developers()

# استخدام المديرين معاً
async def handle_user(user_id):
    # التحقق من نوع المستخدم
    if developer_manager.is_developer(user_id):
        # معالجة كمطور
        return show_developer_panel(user_id)
    elif user_manager.get_user(user_id):
        # معالجة كمستخدم عادي
        return show_user_menu(user_id)
    else:
        # مستخدم جديد
        return show_welcome_message(user_id)
```

---

## ⚠️ ملاحظات مهمة

1. **الفصل التام**: نظام المطورين منفصل تماماً عن نظام المستخدمين
2. **الأمان**: مفاتيح المطورين (`developer_key`) يجب أن تكون آمنة وفريدة
3. **الصلاحيات**: يمكن تخصيص صلاحيات كل مطور بشكل منفصل
4. **التهيئة**: يجب تشغيل `init_developers.py` مرة واحدة على الأقل
5. **قاعدة البيانات**: الجداول تُنشأ تلقائياً عند أول تشغيل

---

## 🚀 البدء السريع

### 1. تعديل إعدادات المطور الرئيسي

في ملف `.env` أو متغيرات البيئة:
```bash
ADMIN_USER_ID=8169000394
DEVELOPER_KEY=NAGDAT-KEY-2024-SECURE
```

### 2. تشغيل التهيئة

```bash
python init_developers.py
```

### 3. التحقق من النجاح

```python
from developer_manager import developer_manager

# عرض جميع المطورين
devs = developer_manager.get_all_active_developers()
print(f"عدد المطورين النشطين: {len(devs)}")
```

---

## 🔍 استكشاف الأخطاء

### المشكلة: المطور غير موجود
**الحل**: تأكد من تشغيل `init_developers.py`

### المشكلة: لا يمكن إرسال إشارات
**الحل**: تحقق من أن `can_broadcast = True` للمطور

### المشكلة: لا يوجد متابعين
**الحل**: تأكد من إضافة متابعين باستخدام `add_follower()`

---

## 📝 التوثيق الإضافي

راجع الملفات التالية لمزيد من المعلومات:
- `context.txt` - سياق المشروع الكامل
- `MULTI_USER_GUIDE.md` - دليل نظام المستخدمين المتعددين
- `database.py` - توثيق قاعدة البيانات

---

## 💡 أمثلة عملية

### مثال 1: إنشاء لوحة تحكم للمطور

```python
async def developer_panel(developer_id):
    if not developer_manager.is_developer(developer_id):
        return "ليس لديك صلاحية"
    
    stats = developer_manager.get_developer_statistics(developer_id)
    
    message = f"""
👨‍💻 لوحة تحكم المطور

📊 الإحصائيات:
• المتابعين: {stats['follower_count']}
• الإشارات المرسلة: {stats['total_signals']}
• الحالة: {'نشط' if stats['is_active'] else 'غير نشط'}
    """
    
    return message
```

### مثال 2: إرسال إشارة تداول

```python
async def send_trading_signal(developer_id, symbol, action, price):
    signal_data = {
        'symbol': symbol,
        'action': action,
        'price': price,
        'timestamp': datetime.now().isoformat()
    }
    
    result = developer_manager.broadcast_signal_to_followers(
        developer_id=developer_id,
        signal_data=signal_data
    )
    
    if result['success']:
        return f"✅ تم إرسال الإشارة إلى {result['follower_count']} متابع"
    else:
        return f"❌ فشل: {result['message']}"
```

---

## 🎯 الخلاصة

نظام المطورين يوفر:
- ✅ إدارة منفصلة للمطورين
- ✅ نظام متابعة قوي
- ✅ إرسال إشارات جماعية
- ✅ صلاحيات متقدمة
- ✅ إحصائيات تفصيلية
- ✅ سهولة التكامل

---

**تم التطوير بواسطة**: Nagdat  
**التاريخ**: 2024  
**الإصدار**: 1.0.0

