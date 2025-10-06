# 🚂 نشر سريع على Railway - خطوة بخطوة

## ⚡ النشر في 5 دقائق

### الخطوة 1: رفع على GitHub ☁️

```bash
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/botbybit.git
git push -u origin main
```

### الخطوة 2: النشر على Railway 🚀

1. **اذهب إلى** [railway.app](https://railway.app)
2. **اضغط** "Start a New Project"
3. **اختر** "Deploy from GitHub repo"
4. **اختر** repository الخاص بك
5. **انتظر** حتى ينتهي النشر الأولي

### الخطوة 3: إضافة المتغيرات 🔐

في لوحة Railway، اذهب إلى **Variables** وأضف:

```
TELEGRAM_TOKEN=7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw
ADMIN_USER_ID=8169000394
DEVELOPER_SECRET_KEY=YOUR_SECRET_KEY
```

### الخطوة 4: الحصول على الدومين 🌐

1. في **Settings** → **Networking**
2. اضغط **"Generate Domain"**
3. انسخ الرابط (مثل: `your-app.railway.app`)

### الخطوة 5: إضافة رابط Webhook 🔗

في **Variables**، أضف:

```
BASE_WEBHOOK_URL=https://your-app.railway.app
```

اضغط **"Redeploy"** لتطبيق التغييرات

---

## ✅ التحقق من النجاح

### 1. افتح في المتصفح:
```
https://your-app.railway.app/health
```

يجب أن ترى:
```json
{"status": "healthy", "service": "Bybit Trading Bot"}
```

### 2. افتح البوت في Telegram
```
/start
```

يجب أن يرد فوراً! 🎉

---

## 🆘 مشاكل شائعة وحلولها

### ❌ البوت لا يستجيب؟
```
✅ تحقق من TELEGRAM_TOKEN في Variables
✅ افحص Logs في Railway للأخطاء
✅ أعد النشر (Redeploy)
```

### ❌ "Application failed"؟
```
✅ تأكد من إضافة جميع المتغيرات
✅ تحقق من أن requirements.txt موجود
✅ راجع Logs للتفاصيل
```

### ❌ Webhook لا يعمل؟
```
✅ تأكد من BASE_WEBHOOK_URL صحيح
✅ يجب أن يبدأ بـ https://
✅ لا تنس الـ Redeploy بعد التعديل
```

---

## 📊 مراقبة البوت

### في Railway Dashboard:

**Metrics** 📈
- CPU Usage
- Memory Usage  
- Network Traffic

**Logs** 📝
- شاهد ما يحدث في الوقت الفعلي
- ابحث عن الأخطاء

**Deployments** 🚀
- تاريخ النشر
- إعادة النشر السريع

---

## 💰 التكلفة

### خطة Trial (مجانية)
```
✅ $5 رصيد مجاني شهرياً
✅ 500 ساعة تشغيل
✅ كافية لبوت صغير-متوسط
```

### خطة Developer ($5)
```
✅ $5 رصيد + إضافي حسب الاستخدام
✅ مناسبة لبوت نشط
✅ دعم أفضل
```

**💡 نصيحة:** راقب استهلاكك في Usage tab

---

## 🔄 التحديث التلقائي

Railway ينشر تلقائياً عند:
```
git push origin main
```

كل تحديث على GitHub = نشر تلقائي! 🎉

---

## 🎯 Checklist سريع

قبل أن تنشر:

- [x] رفعت على GitHub ✅
- [x] أضفت TELEGRAM_TOKEN ✅
- [x] أضفت ADMIN_USER_ID ✅
- [x] أضفت BASE_WEBHOOK_URL ✅
- [x] اختبرت /health ✅
- [x] اختبرت البوت في Telegram ✅

---

## 📞 المساعدة

### واجهت مشكلة؟

**Railway Support:**
- [docs.railway.app](https://docs.railway.app)
- [Discord](https://discord.gg/railway)

**مشاكل البوت:**
- Telegram: @Nagdat
- GitHub: [Issues](https://github.com/nagdat/botbybit/issues)

---

## 🎉 مبروك!

بوتك الآن يعمل 24/7 على السحابة! 🚀

### الخطوات التالية:

1. اختبر جميع الميزات ✅
2. شارك البوت مع أصدقائك 📢
3. راقب الأداء 📊
4. طور وحسّن باستمرار 🔧

---

**💡 نصيحة ذهبية:**

> افتح Logs في Railway Tab واتركه مفتوحاً أثناء الاختبار لترى ما يحدث في الوقت الفعلي!

---

صُنع بـ ❤️ بواسطة Nagdat

**⚡ Deploy Now!** → [railway.app](https://railway.app)

