# 🔧 دليل استكشاف الأخطاء وإصلاحها

## مشكلة: "فشل في حفظ البيانات" عند ربط API

### الأسباب المحتملة والحلول:

#### 1. **user_manager غير مُهيّأ (None)**
**الأعراض:**
- رسالة: "❌ فشل في حفظ البيانات"
- في الـ logs: "user_manager هو None"

**الحل:**
```python
# تأكد من أن bybit_trading_bot.py يحدّث user_manager في module users.user_manager
from users import user_manager as um_module
from users.user_manager import UserManager

user_manager = UserManager(TradingAccount, BybitAPI)
um_module.user_manager = user_manager  # هذا السطر مهم!
user_manager.load_all_users()
```

#### 2. **المستخدم غير موجود في قاعدة البيانات**
**الأعراض:**
- رسالة: "❌ فشل في حفظ البيانات"
- في الـ logs: "المستخدم غير موجود في قاعدة البيانات"

**الحل:**
- تم إصلاحه تلقائياً الآن! يتم إنشاء المستخدم تلقائياً قبل حفظ API Keys

#### 3. **خطأ في الاتصال بـ API**
**الأعراض:**
- رسالة: "❌ فشل الاتصال!"
- API Key أو Secret خاطئ

**الحل:**
1. تحقق من صحة API Key و API Secret
2. تأكد من تفعيل الصلاحيات المطلوبة:
   - ✅ Read (قراءة)
   - ✅ Trade (تداول)
   - ❌ Withdraw (سحب) - لا تفعّله!
3. تأكد من تفعيل API في حسابك

#### 4. **مشكلة في قاعدة البيانات**
**الأعراض:**
- رسالة: "❌ فشل في حفظ البيانات"
- في الـ logs: "خطأ في قاعدة البيانات"

**الحل:**
```bash
# حذف قاعدة البيانات وإعادة إنشائها
rm trading_bot.db
python bybit_trading_bot.py
```

## كيفية التحقق من الـ Logs:

### على Windows:
```powershell
Get-Content trading_bot.log -Tail 100
```

### على Linux/Mac:
```bash
tail -100 trading_bot.log
```

## الخطوات الصحيحة لربط API:

1. **ابدأ البوت**: `/start`
2. **اختر المنصة**: "اختيار منصة"
3. **اختر Bybit أو Bitget**
4. **اضغط "ربط API Keys"**
5. **أدخل API Key** (انسخه من موقع المنصة)
6. **أدخل API Secret** (انسخه من موقع المنصة)
7. **انتظر اختبار الاتصال** (يستغرق 3-5 ثواني)
8. **ستظهر رسالة نجاح** مع معلومات الرصيد

## التحقق من عمل النظام:

```python
# افتح Python console وجرب:
from users.database import db_manager

# تحقق من وجود المستخدم
user_id = YOUR_TELEGRAM_USER_ID
user = db_manager.get_user(user_id)
print(f"User: {user}")

# إذا كان None، أنشئه:
if not user:
    db_manager.create_user(user_id)
    user = db_manager.get_user(user_id)
    print(f"New User: {user}")
```

## أسئلة شائعة:

**س: هل يمكنني استخدام نفس API Key لأكثر من مستخدم؟**
ج: لا، كل مستخدم يجب أن يكون له API Key خاص به.

**س: هل البوت يدعم TestNet؟**
ج: نعم، يمكنك تفعيل TestNet من إعدادات المنصة.

**س: كيف أحذف API Keys المحفوظة؟**
ج: حالياً يجب حذفها من قاعدة البيانات يدوياً أو ربط مفاتيح جديدة.

## تواصل معنا:

إذا استمرت المشكلة، يرجى:
1. إرسال آخر 100 سطر من `trading_bot.log`
2. وصف الخطوات التي اتبعتها
3. نسخة من رسالة الخطأ الكاملة

