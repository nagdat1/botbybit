# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات أولاً (لتحسين بناء Docker layers)
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# إنشاء مستخدم غير root للأمان
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# فتح المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
