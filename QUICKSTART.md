# ⚡ دليل البدء السريع - Bybit Multi-User Trading Bot

## 🚀 التشغيل في 5 دقائق

### 1️⃣ متطلبات البدء

- حساب Telegram
- Python 3.9+ (للتشغيل المحلي)
- حساب Railway (للنشر السحابي)

---

## 💻 التشغيل المحلي (للتجربة)

```bash
# 1. استنساخ المشروع
git clone https://github.com/yourusername/botbybit.git
cd botbybit

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إعداد متغيرات البيئة
cp env.example .env
# عدل الملف .env وأضف:
# TELEGRAM_TOKEN=your_bot_token
# ADMIN_USER_ID=your_telegram_user_id

# 4. تشغيل البوت
python run_with_server.py
```

---

## ☁️ النشر على Railway (للإنتاج)

### الطريقة الأولى: عبر GitHub

1. **رفع المشروع إلى GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **النشر على Railway**
   - اذهب إلى https://railway.app
   - سجل الدخول بحساب GitHub
   - انقر "New Project" → "Deploy from GitHub repo"
   - اختر المستودع `botbybit`
   - انتظر حتى ينتهي النشر

3. **إعداد المتغيرات**
   - في لوحة التحكم على Railway
   - اذهب إلى Variables
   - أضف:
     - `TELEGRAM_TOKEN` = token من @BotFather
     - `ADMIN_USER_ID` = معرف Telegram الخاص بك

4. **إعادة النشر**
   - انقر "Deploy" في Railway
   - انتظر حتى يبدأ التشغيل

### الطريقة الثانية: عبر Railway CLI

```bash
# 1. تسجيل الدخول
railway login

# 2. تهيئة المشروع
railway init

# 3. إعداد المتغيرات
railway variables set TELEGRAM_TOKEN=your_token
railway variables set ADMIN_USER_ID=your_user_id

# 4. النشر
railway up
```

---

## 📱 بدء استخدام البوت

### خطوة 1: فتح البوت

1. ابحث عن بوتك على Telegram
2. أرسل `/start`
3. سترى رسالة ترحيب

### خطوة 2: ربط API (اختياري)

**للحساب التجريبي:**
- لا تحتاج لربط API
- يمكنك البدء فوراً

**للحساب الحقيقي:**
1. اضغط زر "🔗 ربط API"
2. احصل على مفاتيح من: https://api.bybit.com
3. أدخل API_KEY
4. أدخل API_SECRET

### خطوة 3: إعداد البوت

1. اضغط "⚙️ الإعدادات"
2. قم بتعيين:
   - 💰 مبلغ التداول: `100` USDT
   - 🏪 نوع السوق: `Spot` أو `Futures`
   - 👤 نوع الحساب: `تجريبي` أو `حقيقي`
   - ⚡ الرافعة: `10x` (للـ Futures)

### خطوة 4: تشغيل البوت

1. في قسم الإعدادات
2. اضغط "▶️ تشغيل البوت"
3. ✅ البوت الآن نشط!

---

## 🎯 اختبار سريع

### تجربة صفقة تجريبية

```python
# ستحتاج لإرسال إشارة من TradingView أو يدوياً

# مثال على إشارة JSON:
POST https://your-railway-url/webhook
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "action": "buy"
}
```

### عرض الصفقة

1. اضغط "🔄 الصفقات المفتوحة"
2. سترى الصفقة التجريبية
3. اضغط "❌ إغلاق" لإغلاقها

---

## 🔧 استكشاف المشاكل

### البوت لا يرد

```bash
# تحقق من الحالة على Railway
railway logs

# أو محلياً، تحقق من:
tail -f trading_bot.log
```

### خطأ في قاعدة البيانات

```bash
# حذف قاعدة البيانات وإعادة البدء
rm trading_bot.db
python run_with_server.py
```

### خطأ في ربط API

- تحقق من صحة المفاتيح
- تأكد من صلاحيات التداول في Bybit
- جرب إنشاء مفاتيح جديدة

---

## 📊 الخطوات التالية

1. **اقرأ الدليل الكامل**: راجع `MULTI_USER_GUIDE.md`
2. **اختبر الحساب التجريبي**: جرب استراتيجيات مختلفة
3. **أضف مستخدمين**: شارك البوت مع أصدقائك
4. **راقب الصفقات**: استخدم قائمة "💰 المحفظة"
5. **اضبط الإعدادات**: جرب أنواع أسواق مختلفة

---

## 💡 نصائح سريعة

✅ **أفضل الممارسات:**
- ابدأ بالحساب التجريبي
- استخدم مبالغ صغيرة في البداية
- راقب صفقاتك بانتظام
- أوقف البوت عند عدم الاستخدام

⚠️ **تحذيرات:**
- لا تشارك مفاتيح API
- لا تستخدم رافعة عالية في البداية
- احتفظ بنسخة احتياطية من قاعدة البيانات

---

## 📞 الدعم

- **الوثائق**: `MULTI_USER_GUIDE.md`
- **المشاكل**: افتح Issue على GitHub
- **التحديثات**: تابع المستودع

---

**بالتوفيق في التداول! 🚀💰**

