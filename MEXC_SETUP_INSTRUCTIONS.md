# MEXC API Setup Instructions

## المشكلة الحالية:
مفاتيح MEXC API غير موجودة في ملف .env

## الحل:

### 1. إنشاء ملف .env
أنشئ ملف جديد باسم `.env` في المجلد الرئيسي للمشروع

### 2. إضافة مفاتيح MEXC API
أضف السطور التالية إلى ملف .env:

```
# إعدادات MEXC API
MEXC_API_KEY=your_actual_mexc_api_key_here
MEXC_API_SECRET=your_actual_mexc_api_secret_here
```

### 3. الحصول على مفاتيح MEXC API
1. اذهب إلى موقع MEXC
2. سجل دخولك إلى حسابك
3. اذهب إلى API Management
4. أنشئ API Key جديد
5. تأكد من تفعيل صلاحيات "Spot Trading"
6. انسخ API Key و API Secret

### 4. مثال على ملف .env كامل:
```
# إعدادات تلغرام
TELEGRAM_TOKEN=7660340203:AAFSdms8_nVpHF7w6OyC0kWsNc4GJ_aIevw
ADMIN_USER_ID=8169000394

# إعدادات Bybit API
BYBIT_API_KEY=osH14PNXCGzrxQLT0T
BYBIT_API_SECRET=kpP2LHqNOc8Z2P1QjKB5Iw874x7Q2QXGfBHX

# إعدادات MEXC API
MEXC_API_KEY=your_actual_mexc_api_key_here
MEXC_API_SECRET=your_actual_mexc_api_secret_here

# إعدادات Webhook
WEBHOOK_PORT=5000
```

### 5. اختبار الاتصال
بعد إضافة المفاتيح، جرب اختبار الاتصال مرة أخرى

## ملاحظات مهمة:
- تأكد من أن API Key مفعل في حسابك
- تأكد من تفعيل صلاحيات "Spot Trading"
- لا تشارك مفاتيح API مع أي شخص
- احتفظ بنسخة احتياطية من المفاتيح في مكان آمن
