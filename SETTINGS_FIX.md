# إصلاح زر الفيوتشر والإعدادات

## المشكلة
كان زر الفيوتشر في الإعدادات لا يحفظ التغييرات بشكل دائم. عند الضغط على زر "futures" يتم تحديث الإعدادات في الذاكرة فقط (`trading_bot.user_settings`) ولا يتم حفظها في قاعدة البيانات، مما يؤدي إلى عودة الإعدادات إلى السوق السابق (spot) عند إعادة تشغيل البوت أو عند استقبال إشارة جديدة.

## الحل

### 1. تحديث دالة `update_user_settings` في `database.py`
تم تعديل الدالة لكي تقبل تحديثات جزئية (partial updates) بدلاً من تحديث جميع الحقول:

**قبل:**
- كانت الدالة تستخدم `settings.get(key, default_value)` مما يعني أنها تحدث جميع الحقول حتى لو لم يتم تمريرها
- إذا مررت فقط `{'market_type': 'futures'}`، كانت تحدث باقي الحقول بالقيم الافتراضية

**بعد:**
- الآن تحدث فقط الحقول الموجودة في `settings` dictionary
- يمكنك تمرير `{'market_type': 'futures'}` فقط وسيتم تحديث هذا الحقل فقط

### 2. إضافة حفظ الإعدادات عند الضغط على أزرار الإعدادات

تم تحديث الأماكن التالية في `bybit_trading_bot.py`:

#### أ) زر نوع السوق (Spot/Futures)
```python
elif data == "market_spot":
    trading_bot.user_settings['market_type'] = 'spot'
    # حفظ الإعدادات في قاعدة البيانات
    if user_id is not None:
        db_manager.update_user_settings(user_id, {'market_type': 'spot'})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['market_type'] = 'spot'
    await settings_menu(update, context)

elif data == "market_futures":
    trading_bot.user_settings['market_type'] = 'futures'
    # حفظ الإعدادات في قاعدة البيانات
    if user_id is not None:
        db_manager.update_user_settings(user_id, {'market_type': 'futures'})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['market_type'] = 'futures'
    await settings_menu(update, context)
```

#### ب) زر نوع الحساب (Real/Demo)
```python
elif data == "account_real":
    trading_bot.user_settings['account_type'] = 'real'
    # حفظ الإعدادات في قاعدة البيانات
    if user_id is not None:
        db_manager.update_user_settings(user_id, {'account_type': 'real'})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['account_type'] = 'real'
    await settings_menu(update, context)

elif data == "account_demo":
    trading_bot.user_settings['account_type'] = 'demo'
    # حفظ الإعدادات في قاعدة البيانات
    if user_id is not None:
        db_manager.update_user_settings(user_id, {'account_type': 'demo'})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['account_type'] = 'demo'
    await settings_menu(update, context)
```

#### ج) إدخال مبلغ التداول
```python
elif state == "waiting_for_trade_amount":
    amount = float(text)
    if amount > 0:
        trading_bot.user_settings['trade_amount'] = amount
        # حفظ في قاعدة البيانات
        db_manager.update_user_settings(user_id, {'trade_amount': amount})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['trade_amount'] = amount
        await update.message.reply_text(f"✅ تم تحديث مبلغ التداول إلى: {amount}")
```

#### د) إدخال الرافعة المالية
```python
elif state == "waiting_for_leverage":
    leverage = int(text)
    if 1 <= leverage <= 100:
        trading_bot.user_settings['leverage'] = leverage
        # حفظ في قاعدة البيانات
        db_manager.update_user_settings(user_id, {'leverage': leverage})
        # تحديث في user_manager
        user_data = user_manager.get_user(user_id)
        if user_data:
            user_data['leverage'] = leverage
        await update.message.reply_text(f"✅ تم تحديث الرافعة المالية إلى: {leverage}x")
```

#### هـ) تحديث رصيد الحساب التجريبي
```python
elif state == "waiting_for_demo_balance":
    balance = float(text)
    if balance >= 0:
        # تحديث رصيد الحساب التجريبي
        user_data = user_manager.get_user(user_id)
        if user_data:
            market_type = user_data.get('market_type', 'spot')
            # تحديث في حساب المستخدم
            account = user_manager.get_user_account(user_id, market_type)
            if account:
                account.update_balance(balance)
            # حفظ في قاعدة البيانات
            user_manager.update_user_balance(user_id, balance)
        await update.message.reply_text(f"✅ تم تحديث رصيد الحساب التجريبي إلى: {balance}")
```

## آلية العمل الجديدة

عند تغيير أي إعداد، يتم:

1. **تحديث في الذاكرة**: تحديث `trading_bot.user_settings`
2. **حفظ في قاعدة البيانات**: استدعاء `db_manager.update_user_settings()` أو `user_manager.update_user_balance()`
3. **تحديث في user_manager**: تحديث `user_data` في الذاكرة لضمان التوافق

هذا يضمن أن:
- ✅ يتم حفظ الإعدادات بشكل دائم
- ✅ تبقى الإعدادات بعد إعادة تشغيل البوت
- ✅ يستخدم كل مستخدم إعداداته الخاصة عند استقبال الإشارات
- ✅ يتم عرض الإعدادات الصحيحة في قائمة الإعدادات

## الملفات المعدلة

1. **`database.py`**: تحديث دالة `update_user_settings()` لدعم التحديثات الجزئية
2. **`bybit_trading_bot.py`**: إضافة حفظ الإعدادات في جميع نقاط التغيير

## الاختبار

للتأكد من أن الإصلاح يعمل:

1. افتح البوت في تلجرام
2. اذهب إلى ⚙️ الإعدادات
3. اختر 🏪 نوع السوق
4. اضغط على "futures"
5. تحقق من أن الإعدادات تعرض "FUTURES" في نوع السوق
6. أعد تشغيل البوت
7. افتح الإعدادات مرة أخرى - يجب أن تظل على "FUTURES"
8. أرسل إشارة تداول - يجب أن تُنفذ على سوق الفيوتشر

## تاريخ الإصلاح
- **التاريخ**: 2025-01-08
- **النسخة**: v1.0

