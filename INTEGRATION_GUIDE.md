# 🔌 دليل التكامل - ربط الأنظمة الجديدة

## 📋 نظرة عامة
هذا الدليل يوضح كيفية دمج الأنظمة الجديدة مع الكود الحالي في `bybit_trading_bot.py`.

---

## 1️⃣ الاستيرادات المطلوبة

أضف في بداية `bybit_trading_bot.py`:

```python
# استيراد الأنظمة الجديدة
from systems.position_fetcher import create_position_fetcher
from systems.position_display import create_position_display_manager
from systems.partial_close_handler import create_partial_close_handler
from systems.trade_history_display import create_trade_history_display
from systems.unified_position_manager import create_unified_position_manager
```

---

## 2️⃣ التهيئة في البوت

أضف بعد تهيئة `db_manager` و `signal_id_manager`:

```python
# في دالة main() أو __init__
class TradingBot:
    def __init__(self):
        # الموجود حالياً
        self.db_manager = DatabaseManager()
        self.signal_id_manager = get_signal_id_manager()
        
        # الجديد - إضافة
        self.position_fetcher = create_position_fetcher(
            self.db_manager, 
            self.signal_id_manager
        )
        
        self.position_display = create_position_display_manager()
        
        self.partial_close_handler = create_partial_close_handler(
            self.db_manager
        )
        
        self.trade_history_display = create_trade_history_display(
            self.db_manager
        )
        
        self.unified_position_manager = create_unified_position_manager(
            self.db_manager,
            self.signal_id_manager
        )
```

---

## 3️⃣ تحديث دالة عرض الصفقات المفتوحة

استبدل الدالة `open_positions()` الحالية:

```python
async def open_positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الصفقات المفتوحة بتنسيق احترافي"""
    user_id = update.effective_user.id
    
    try:
        # جلب بيانات المستخدم
        user_data = trading_bot.db_manager.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير مسجل")
            return
        
        account_type = user_data.get('account_type', 'demo')
        market_type = user_data.get('market_type', None)  # None = جلب الكل
        
        # تحديد API client حسب نوع الحساب
        api_client = None
        if account_type == 'real':
            api_client = trading_bot.bybit_api
        else:
            # للتجريبي نحتاج API فقط لجلب الأسعار
            api_client = trading_bot.bybit_api
        
        # جلب جميع الصفقات المفتوحة
        all_positions = trading_bot.position_fetcher.get_all_open_positions(
            user_id=user_id,
            account_type=account_type,
            api_client=api_client,
            market_type=market_type
        )
        
        # فصل حسب نوع السوق
        spot_positions, futures_positions = trading_bot.position_fetcher.separate_positions_by_market(all_positions)
        
        # تنسيق وعرض
        if market_type == 'spot':
            message, keyboard = trading_bot.position_display.format_spot_positions_message(
                spot_positions, account_type
            )
        elif market_type == 'futures':
            message, keyboard = trading_bot.position_display.format_futures_positions_message(
                futures_positions, account_type
            )
        else:
            # عرض الكل
            message, keyboard = trading_bot.position_display.format_all_positions_message(
                spot_positions, futures_positions, account_type
            )
        
        # إرسال الرسالة
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
    except Exception as e:
        logger.error(f"خطأ في عرض الصفقات المفتوحة: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض الصفقات")
```

---

## 4️⃣ دالة الإغلاق الجزئي

إضافة handler جديد:

```python
async def handle_partial_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإغلاق الجزئي"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
        # استخراج البيانات من callback_data
        # مثال: "partial_25_DEMO_TV001_abc123"
        parts = query.data.split('_')
        percent = float(parts[1])
        position_id = '_'.join(parts[2:])
        
        # تحديد API client
        user_data = trading_bot.db_manager.get_user(user_id)
        api_client = None
        if user_data.get('account_type') == 'real':
            api_client = trading_bot.bybit_api
        
        # تنفيذ الإغلاق الجزئي
        result = trading_bot.partial_close_handler.execute_partial_close(
            user_id=user_id,
            position_id=position_id,
            close_percent=percent,
            api_client=api_client
        )
        
        if result['success']:
            message = f"✅ {result['message']}\n\n"
            message += f"💰 P&L: {result['partial_pnl']:+.2f} USDT\n"
            message += f"📊 Close Price: {result['close_price']:.4f}\n"
            message += f"📉 Remaining: {result['remaining_quantity']:.4f}"
            
            await query.edit_message_text(message)
            
            # تحديث عرض الصفقات
            await asyncio.sleep(1)
            await open_positions(update, context)
        else:
            await query.edit_message_text(f"❌ {result['message']}")
        
    except Exception as e:
        logger.error(f"خطأ في الإغلاق الجزئي: {e}")
        await query.edit_message_text("❌ حدث خطأ في الإغلاق الجزئي")


# تسجيل Handler
application.add_handler(CallbackQueryHandler(handle_partial_close, pattern=r'^partial_\d+_'))
```

---

## 5️⃣ دالة سجل الصفقات

إضافة handler جديد:

```python
async def trade_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض سجل الصفقات مع فلاتر"""
    user_id = update.effective_user.id
    
    try:
        # الفلاتر الافتراضية
        filters = {
            'limit': 10
        }
        
        # إذا كان هناك فلاتر من context
        if context.user_data and 'history_filters' in context.user_data:
            filters.update(context.user_data['history_filters'])
        
        # جلب السجل
        trades = trading_bot.trade_history_display.get_trade_history(user_id, filters)
        
        # تنسيق وعرض
        message, keyboard = trading_bot.trade_history_display.format_trade_history_message(
            trades, filters
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                text=message,
                reply_markup=keyboard
            )
        
    except Exception as e:
        logger.error(f"خطأ في عرض سجل الصفقات: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض السجل")


async def handle_history_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج فلاتر سجل الصفقات"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
        # استخراج الفلتر من callback_data
        # مثال: "history_filter_status_closed"
        parts = query.data.split('_')
        filter_type = parts[2]  # status, account, market
        filter_value = parts[3]  # all, open, closed, etc.
        
        # تحديث الفلاتر
        if not context.user_data:
            context.user_data = {}
        
        if 'history_filters' not in context.user_data:
            context.user_data['history_filters'] = {}
        
        if filter_value == 'all':
            # إزالة الفلتر
            context.user_data['history_filters'].pop(filter_type, None)
        else:
            # إضافة الفلتر
            context.user_data['history_filters'][filter_type] = filter_value
        
        # إعادة عرض السجل
        await trade_history(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في معالج الفلاتر: {e}")
        await query.edit_message_text("❌ حدث خطأ في الفلترة")


# تسجيل Handlers
application.add_handler(CommandHandler("history", trade_history))
application.add_handler(CallbackQueryHandler(handle_history_filter, pattern=r'^history_filter_'))
application.add_handler(CallbackQueryHandler(trade_history, pattern=r'^history_refresh$'))
```

---

## 6️⃣ حفظ الصفقات عند الفتح/الإغلاق

### عند فتح صفقة جديدة:

```python
async def execute_signal(signal_data: Dict):
    """تنفيذ إشارة جديدة"""
    try:
        user_id = signal_data['user_id']
        user_data = trading_bot.db_manager.get_user(user_id)
        account_type = user_data.get('account_type', 'demo')
        
        # تنفيذ الأمر
        if account_type == 'real':
            order_result = trading_bot.bybit_api.place_order(...)
        else:
            order_result = trading_bot.demo_account.place_order(...)
        
        # حفظ في قاعدة البيانات
        trading_bot.unified_position_manager.save_position_on_open(
            user_id=user_id,
            signal_data=signal_data,
            order_result=order_result,
            account_type=account_type
        )
        
        return {'success': True, 'order_result': order_result}
        
    except Exception as e:
        logger.error(f"خطأ في تنفيذ الإشارة: {e}")
        return {'success': False, 'message': str(e)}
```

### عند إغلاق صفقة:

```python
async def close_position(position_id: str, user_id: int):
    """إغلاق صفقة"""
    try:
        user_data = trading_bot.db_manager.get_user(user_id)
        account_type = user_data.get('account_type', 'demo')
        
        # الحصول على الصفقة
        order = trading_bot.db_manager.get_order(position_id)
        
        # تنفيذ الإغلاق
        if account_type == 'real':
            close_result = trading_bot.bybit_api.close_position(...)
        else:
            close_result = trading_bot.demo_account.close_position(...)
        
        # حساب PnL
        close_price = close_result.get('close_price', 0)
        entry_price = order['entry_price']
        quantity = order['quantity']
        
        if order['side'].upper() == 'BUY':
            pnl_value = (close_price - entry_price) * quantity
        else:
            pnl_value = (entry_price - close_price) * quantity
        
        amount = entry_price * quantity
        pnl_percent = (pnl_value / amount) * 100 if amount > 0 else 0
        
        close_data = {
            'close_price': close_price,
            'pnl_value': pnl_value,
            'pnl_percent': pnl_percent
        }
        
        # حفظ بيانات الإغلاق
        trading_bot.unified_position_manager.save_position_on_close(
            user_id=user_id,
            position_id=position_id,
            close_data=close_data
        )
        
        return {'success': True, 'pnl': pnl_value}
        
    except Exception as e:
        logger.error(f"خطأ في إغلاق الصفقة: {e}")
        return {'success': False, 'message': str(e)}
```

---

## 7️⃣ إضافة زر "سجل الصفقات" للقائمة الرئيسية

في دالة إنشاء لوحة المفاتيح الرئيسية:

```python
def create_main_keyboard():
    """إنشاء لوحة المفاتيح الرئيسية"""
    keyboard = [
        [KeyboardButton("📊 الصفقات المفتوحة"), KeyboardButton("📜 سجل الصفقات")],
        [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("💰 الرصيد")],
        # ... باقي الأزرار
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# تسجيل Handler
application.add_handler(MessageHandler(filters.Regex("^📜 سجل الصفقات$"), trade_history))
```

---

## 8️⃣ إضافة زر "تحديث" في عرض الصفقات

```python
async def handle_refresh_positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحديث عرض الصفقات المفتوحة"""
    query = update.callback_query
    await query.answer("🔄 جاري التحديث...")
    
    # إعادة عرض الصفقات
    await open_positions(update, context)


# تسجيل Handler
application.add_handler(CallbackQueryHandler(handle_refresh_positions, pattern=r'^refresh_positions$'))
```

---

## 9️⃣ التحقق من التكامل الصحيح

بعد التطبيق، تأكد من:

1. ✅ الاستيرادات تعمل بدون أخطاء
2. ✅ التهيئة في `__init__` صحيحة
3. ✅ عرض الصفقات يعمل للحسابات التجريبية
4. ✅ عرض الصفقات يعمل للحسابات الحقيقية
5. ✅ الإغلاق الجزئي يعمل بشكل صحيح
6. ✅ سجل الصفقات يُعرض بشكل صحيح
7. ✅ الفلاتر تعمل
8. ✅ التقرير المفصل يُولّد بدقة

---

## 🔟 نصائح مهمة

### 1. معالجة الأخطاء
أضف معالجة أخطاء شاملة لكل handler:

```python
try:
    # الكود الرئيسي
    pass
except Exception as e:
    logger.error(f"خطأ: {e}", exc_info=True)
    await update.message.reply_text("❌ حدث خطأ")
```

### 2. Logging
فعّل logging مفصّل للتتبع:

```python
logger.info(f"✅ تم جلب {len(positions)} صفقة")
logger.error(f"❌ فشل: {e}")
```

### 3. التحديث التلقائي
يمكن إضافة job للتحديث التلقائي:

```python
from telegram.ext import JobQueue

def auto_update_positions(context):
    """تحديث تلقائي للصفقات كل دقيقة"""
    # تحديث البيانات...
    pass

# إضافة الجوب
job_queue = application.job_queue
job_queue.run_repeating(auto_update_positions, interval=60, first=10)
```

---

## ✅ الخلاصة

بعد اتباع هذا الدليل، ستحصل على:
- ✅ نظام جلب صفقات متطور
- ✅ واجهة عرض احترافية
- ✅ إغلاق جزئي كامل
- ✅ سجل صفقات مع فلاتر
- ✅ ربط خفي بين Signal ID و Position ID
- ✅ حفظ منظم في قاعدة البيانات

---

**ملاحظة:** تأكد من اختبار كل ميزة على حدة قبل النشر النهائي.

