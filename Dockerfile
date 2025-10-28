# Dockerfile للمشروع على Railway
FROM python:3.11-slim

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تعيين المتغيرات البيئية
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# فتح المنفذ
EXPOSE 5000

# الأمر البدء
CMD ["python", "app.py"]

