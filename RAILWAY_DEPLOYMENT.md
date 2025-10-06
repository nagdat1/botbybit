# 🚂 دليل النشر على Railway

## 🌟 نظرة عامة

Railway هي منصة سحابية سهلة لنشر التطبيقات. هذا الدليل يشرح كيفية نشر Bybit Trading Bot على Railway.

---

## ✅ المتطلبات الأساسية

- [x] حساب GitHub
- [x] حساب Railway ([railway.app](https://railway.app))
- [x] Telegram Bot Token
- [x] المشروع جاهز على GitHub

---

## 🚀 خطوات النشر

### 1️⃣ إعداد GitHub Repository

```bash
# إذا لم تكن قد رفعت المشروع على GitHub بعد:

# تهيئة Git
git init

# إضافة الملفات
git add .

# أول commit
git commit -m "Initial commit: Bybit Trading Bot"

# ربط بـ GitHub
git remote add origin https://github.com/YOUR_USERNAME/botbybit.git

# رفع المشروع
git branch -M main
git push -u origin main
```

### 2️⃣ إنشاء مشروع على Railway

#### الطريقة 1: من GitHub (موصى بها)

1. اذهب إلى [railway.app](https://railway.app)
2. اضغط "Login" واختر "Login with GitHub"
3. بعد تسجيل الدخول، اضغط "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر repository "botbybit"
6. انتظر حتى يبدأ النشر

#### الطريقة 2: من Template

1. في Railway، اضغط "New Project"
2. اختر "Empty Project"
3. اضغط على المشروع
4. اضغط "Connect to GitHub"
5. اختر repository

### 3️⃣ إعداد المتغيرات البيئية

في لوحة Railway:

1. اضغط على المشروع
2. اذهب إلى "Variables" في القائمة اليسرى
3. أضف المتغيرات التالية:

```env
# ضروري - Telegram Bot Token
TELEGRAM_TOKEN=7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw

# ضروري - User ID للمطور
ADMIN_USER_ID=8169000394

# ضروري - مفتاح سري للمطور
DEVELOPER_SECRET_KEY=NAGDAT-SECRET-KEY-2024

# سيتم ملؤه تلقائياً في الخطوة التالية
BASE_WEBHOOK_URL=https://your-app.railway.app

# اختياري - إعدادات إضافية
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
LOG_LEVEL=INFO
```

### 4️⃣ الحصول على رابط التطبيق

1. في لوحة Railway، اذهب إلى "Settings"
2. في قسم "Networking"، اضغط "Generate Domain"
3. سيظهر رابط مثل: `your-app.railway.app`
4. انسخ الرابط

### 5️⃣ تحديث BASE_WEBHOOK_URL

1. عد إلى "Variables"
2. عدّل `BASE_WEBHOOK_URL`
3. ضع: `https://your-app.railway.app`
4. احفظ التغييرات

### 6️⃣ إعادة النشر

1. اذهب إلى "Deployments"
2. اضغط على آخر نشر
3. اضغط "Redeploy"
4. انتظر حتى ينتهي النشر

---

## ✅ التحقق من النشر الناجح

### 1. فحص الصحة (Health Check)

افتح في المتصفح:
```
https://your-app.railway.app/health
```

يجب أن ترى:
```json
{
  "status": "healthy",
  "service": "Bybit Trading Bot Webhook Server"
}
```

### 2. فحص السجلات (Logs)

في Railway:
1. اضغط على "Logs" في القائمة اليسرى
2. يجب أن ترى:

```
🚀 Starting Bybit Trading Bot...
✅ Handlers setup completed
✅ Bot initialized successfully
🌐 Starting webhook server...
🚀 Starting bot polling...
╔══════════════════════════════════════════╗
║   🤖 Bybit Trading Bot Started! 🚀      ║
╠══════════════════════════════════════════╣
║   Developer: Nagdat                      ║
║   Mode: Production                       ║
║   Status: ✅ Active                      ║
╚══════════════════════════════════════════╝
```

### 3. اختبار البوت

1. افتح البوت في Telegram
2. أرسل `/start`
3. يجب أن يرد فوراً

---

## 🔧 الإعدادات المتقدمة

### تفعيل Auto-Deploy

عند كل push لـ GitHub:

1. في Railway → Settings
2. فعّل "Automatic Deployments"
3. اختر Branch: `main`

الآن كل تحديث على GitHub سيتم نشره تلقائياً!

### إضافة قاعدة بيانات PostgreSQL (اختياري)

إذا أردت استخدام PostgreSQL بدلاً من SQLite:

1. في Railway، اضغط "New"
2. اختر "Database" → "PostgreSQL"
3. ستحصل على `DATABASE_URL` تلقائياً
4. عدّل `database.py` لاستخدام PostgreSQL

### مراقبة الموارد

في Railway:
- **Metrics**: شاهد CPU و RAM و Network
- **Usage**: راقب استهلاك الموارد
- **Logs**: تابع سجلات البوت

---

## 💰 التكلفة والخطط

### Railway Pricing

#### خطة مجانية (Trial)
- **$5 رصيد مجاني** شهرياً
- **500 ساعة تشغيل** شهرياً
- يكفي لبوت صغير

#### خطة Developer ($5/شهر)
- **$5 رصيد** + $0.01 لكل ساعة إضافية
- مناسب لبوت نشط

#### خطة Pro ($20/شهر)
- **$20 رصيد** + $0.01 لكل ساعة
- للبوتات الكبيرة

### تقدير الاستهلاك

بوت متوسط الاستخدام:
```
RAM: ~200 MB
CPU: 0.1 vCPU
Network: 1 GB/شهر

التكلفة المقدرة: $2-5/شهر
```

---

## 🔍 حل المشاكل

### المشكلة: البوت لا يستجيب

**الحل:**
```bash
# افحص Logs في Railway
# ابحث عن أخطاء مثل:
- "Invalid token"
- "Connection refused"
- "Module not found"

# إعادة النشر:
Deployments → Latest → Redeploy
```

### المشكلة: "Application failed to respond"

**الأسباب المحتملة:**
1. `TELEGRAM_TOKEN` خاطئ
2. المنافذ غير صحيحة
3. أخطاء في الكود

**الحل:**
```bash
# تحقق من Variables
# تأكد من أن Procfile صحيح
# افحص Logs للتفاصيل
```

### المشكلة: قاعدة البيانات مفقودة بعد إعادة النشر

**الحل:**
```bash
# SQLite يُحذف مع كل نشر
# استخدم Railway Volume:

1. في Railway → Settings
2. أضف Volume
3. Mount Path: /app/data
4. عدّل config.py:
   DATABASE_PATH = "/app/data/botbybit.db"
```

### المشكلة: الموارد نفدت

**الحل:**
```bash
# راقب Metrics
# قلل استهلاك الموارد:
- زد PRICE_UPDATE_INTERVAL في config.py
- قلل CACHE_DURATION
- حدد عدد المستخدمين النشطين
```

---

## 📊 مراقبة الأداء

### مؤشرات الأداء الرئيسية (KPIs)

```python
# في Railway Logs:
✅ Uptime: 99.9%
📈 Response Time: <1s
💾 Memory: 150-250 MB
🔄 Requests/min: 5-20
```

### تنبيهات

إعداد تنبيهات في Railway:
1. Settings → Alerts
2. أضف تنبيه عند:
   - High Memory Usage (>80%)
   - High CPU Usage (>80%)
   - Deployment Failed

---

## 🚀 التحسينات للإنتاج

### 1. استخدام Environment Groups

```bash
# في Railway، أنشئ Environment Groups:
- Production (live)
- Staging (testing)
- Development (dev)
```

### 2. إعداد Custom Domain (اختياري)

```bash
# في Railway → Settings → Domains
1. أضف نطاقك: bot.yourdomain.com
2. أضف DNS Records في مزود النطاق
3. انتظر التفعيل
```

### 3. Continuous Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          # Railway CLI commands
```

---

## 📚 الموارد الإضافية

### روابط مفيدة

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub](https://github.com/railwayapp)

### أدوات مساعدة

```bash
# Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# ربط المشروع
railway link

# عرض Logs
railway logs

# تشغيل محلياً
railway run python main.py
```

---

## ✅ Checklist النشر

قبل النشر النهائي، تأكد من:

- [ ] رفع المشروع على GitHub
- [ ] إضافة جميع المتغيرات البيئية
- [ ] تعيين `BASE_WEBHOOK_URL` الصحيح
- [ ] تفعيل Domain في Railway
- [ ] اختبار `/health` endpoint
- [ ] اختبار البوت في Telegram
- [ ] فحص Logs للأخطاء
- [ ] إعداد Monitoring
- [ ] إعداد Alerts
- [ ] توثيق الإعدادات

---

## 🎉 مبروك!

بوتك الآن يعمل على Railway! 🚀

### الخطوات التالية:

1. ✅ اختبر جميع الميزات
2. ✅ راقب الأداء
3. ✅ شارك البوت مع المستخدمين
4. ✅ اجمع ملاحظات
5. ✅ حسّن وطوّر

---

## 💬 الدعم

هل واجهت مشكلة؟

- **GitHub Issues**: [Create Issue](https://github.com/nagdat/botbybit/issues)
- **Telegram**: @Nagdat
- **Railway Support**: [help.railway.app](https://help.railway.app)

---

**نصيحة احترافية:**

> راقب استهلاك الموارد أسبوعياً وحسّن الكود باستمرار للحفاظ على التكاليف منخفضة والأداء عالياً!

---

صُنع بـ ❤️ بواسطة Nagdat

