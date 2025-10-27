#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Messages and Responses for Bot Buttons
جميع الرسائل والردود الخاصة بأزرار البوت
"""

# ==================== رسائل الترحيب ====================

WELCOME_MESSAGES = {
    "developer": """
🤖 مرحباً بك {name} - المطور

👨‍💻 أنت في الوضع العادي للمطور
🔙 يمكنك العودة إلى لوحة تحكم المطور في أي وقت

🔗 رابط الإشارات الخاص بك:
`{webhook_url}`

استخدم الأزرار أدناه للتنقل
    """,
    
    "user": """
🤖 مرحباً بك {name}!

أهلاً وسهلاً بك في بوت المطور نجدت 🎉

🚀 **ما يفعله البوت:**
• تنفيذ إشارات التداول تلقائياً من TradingView
• دعم منصة Bybit
• تداول ذكي مع إدارة مخاطر متقدمة
• إحصائيات مفصلة ومتابعة الصفقات

💡 **كيف يعمل:**
1. تربط حسابك على المنصة المفضلة
2. تحصل على رابط webhook شخصي
3. تستخدم الرابط في TradingView لإرسال الإشارات
4. البوت ينفذ الصفقات تلقائياً! 🎯

🎁 **ميزات خاصة:**
• مزامنة تلقائية مع إشارات Nagdat (اختياري)
• إدارة مخاطر ذكية
• إحصائيات مفصلة
• دعم كامل لـ Spot و Futures
    """
}

# ==================== رسائل الإعدادات ====================

SETTINGS_MESSAGES = {
    "main": """
⚙️ إعدادات البوت الحالية:

📊 حالة البوت: {bot_status}
🔗 حالة API: {api_status}

💰 مبلغ التداول: {trade_amount}
🏪 نوع السوق: {market_type}
👤 نوع الحساب: {account_type}
    """,
    
    "api_linked": "🟢 مرتبط ({exchange})",
    "api_unlinked": "🔴 غير مرتبط",
    "api_partial": "🔗 مرتبط ({exchange}) - غير مفعّل"
}

# ==================== رسائل الحساب ====================

ACCOUNT_MESSAGES = {
    "status": """
📊 حالة حسابك:

💰 الرصيد الكلي: {total_balance:.2f} USDT
💵 الرصيد المتاح: {available_balance:.2f} USDT
🔒 الرصيد المحجوز: {locked_balance:.2f} USDT

📈 الصفقات المفتوحة: {open_positions}
✅ الصفقات المغلقة: {closed_positions}
📊 إجمالي الربح/الخسارة: {total_pnl:+.2f} USDT

🔗 الحساب: {account_type}
🏪 السوق: {market_type}
    """,
    
    "wallet": """
💰 محفظتك

💵 الرصيد الكلي: {balance:.2f} USDT
📊 الصفقات النشطة: {active_positions}
💸 إجمالي الربح/الخسارة: {total_pnl:+.2f} USDT
    """,
    
    "statistics": """
📊 إحصائيات التداول:

📈 إجمالي الصفقات: {total_trades}
✅ صفقات رابحة: {winning_trades}
❌ صفقات خاسرة: {losing_trades}
📊 نسبة النجاح: {win_rate:.1f}%

💰 إجمالي الربح/الخسارة: {total_pnl:+.2f} USDT
📈 أفضل صفقة: {best_trade:+.2f} USDT
📉 أسوأ صفقة: {worst_trade:+.2f} USDT
    """
}

# ==================== رسائل الصفقات ====================

TRADE_MESSAGES = {
    "futures_opened": """
✅ تم تنفيذ صفقة فيوتشر حقيقية

👤 المستخدم: {user_id}
📊 الرمز: {symbol}
🔄 النوع: {side}
💰 الهامش: {margin_amount}
⚡ الرافعة: {leverage}x
📈 حجم الصفقة: {position_size:.2f}
💲 السعر التقريبي: {price:.6f}
🏪 السوق: FUTURES
🆔 رقم الأمر: {order_id}

🎯 Take Profit: {take_profit:.6f}
🛑 Stop Loss: {stop_loss:.6f}
    """,
    
    "spot_opened": """
✅ تم تنفيذ صفقة سبوت حقيقية

👤 المستخدم: {user_id}
📊 الرمز: {symbol}
🔄 النوع: {side}
💰 المبلغ: {amount}
💲 السعر: {price:.6f}
🏪 السوق: SPOT
🆔 رقم الأمر: {order_id}
    """,
    
    "position_managed": """
📊 **إدارة الصفقة: {symbol}**

💲 سعر الدخول: {entry_price:.6f}
💲 السعر الحالي: {current_price:.6f}
💰 الحجم: {size}
🔄 النوع: {side.upper()}

{profit_loss_display}
    """,
    
    "position_closed": """
✅ تم إغلاق الصفقة

📊 الرمز: {symbol}
💰 الربح/الخسارة: {pnl:+.2f} USDT
📈 نسبة الربح: {pnl_percent:+.2f}%
    """
}

# ==================== رسائل الأخطاء ====================

ERROR_MESSAGES = {
    "symbol_not_found": "❌ الرمز {symbol} غير موجود في منصة Bybit!",
    "insufficient_balance": "❌ الرصيد غير كافي لفتح الصفقة",
    "invalid_amount": "❌ يرجى إدخال رقم صحيح",
    "position_not_found": "❌ الصفقة غير موجودة",
    "no_open_positions": "📭 لا توجد صفقات مفتوحة حالياً",
    "trade_failed": "❌ فشل في تنفيذ الصفقة: {error}",
    "unauthorized": "❌ ليس لديك صلاحية للوصول إلى هذا المورد"
}

# ==================== رسائل نجاح العملية ====================

SUCCESS_MESSAGES = {
    "settings_updated": "✅ تم تحديث الإعدادات بنجاح",
    "amount_updated": "✅ تم تحديث مبلغ التداول إلى: {amount}",
    "leverage_updated": "✅ تم تحديث الرافعة المالية إلى: {leverage}x",
    "api_connected": "✅ تم ربط API بنجاح!",
    "position_closed": "✅ تم إغلاق الصفقة بنجاح",
    "settings_saved": "✅ تم حفظ الإعدادات"
}

# ==================== رسائل التحذير ====================

WARNING_MESSAGES = {
    "liquidation_risk": "⚠️ تحذير: قريب من سعر التصفية!",
    "high_leverage": "⚠️ الرافعة عالية جداً! احذر من الخطر",
    "low_balance": "⚠️ الرصيد منخفض! فكر في إضافة أموال"
}

# ==================== رسائل إدارة المخاطر ====================

RISK_MANAGEMENT_MESSAGES = {
    "menu": """
🛡️ إدارة المخاطر

📊 الإحصائيات الحالية:
• الخسارة اليومية: {daily_loss:.2f} USDT
• الخسارة الأسبوعية: {weekly_loss:.2f} USDT
• إجمالي الخسارة: {total_loss:.2f} USDT

⚙️ الإعدادات:
• إدارة المخاطر: {risk_enabled}
• حد الخسارة النسبي: {max_loss_percent}%
• حد الخسارة بالمبلغ: {max_loss_amount} USDT
• حد الخسارة اليومية: {daily_limit} USDT
• حد الخسارة الأسبوعية: {weekly_limit} USDT
    """,
    
    "enabled": """
✅ تم تفعيل إدارة المخاطر

🛡️ سيتم حماية حسابك من الخسائر الكبيرة
    """,
    
    "disabled": """
⏸️ تم تعطيل إدارة المخاطر

⚠️ احذر: حسابك معرض للخسائر الكبيرة
    """,
    
    "limit_reached": """
🚨 تم الوصول إلى حد الخسارة!

⏹️ تم إيقاف التداول تلقائياً لحماية حسابك
    """
}

# ==================== رسائل المطور ====================

DEVELOPER_MESSAGES = {
    "panel": """
👨‍💻 لوحة تحكم المطور - {name}

📊 إحصائيات سريعة:
• 👥 إجمالي المستخدمين: {total_users}
• 👥 المتابعين: {followers}
• 📡 الإشارات المرسلة: {signals_sent}
• 💰 إجمالي حجم التداول: {total_volume} USDT

⚙️ الحالة:
• النظام: 🟢 نشط
• البث: {'✅ مفعل' if broadcast_enabled else '❌ معطل'}
• آخر تحديث: {last_update}
    """,
    
    "no_followers": "📭 لا يوجد متابعين حالياً",
    "signal_sent": """
✅ تم إرسال الإشارة بنجاح

📊 تم الإرسال إلى {count} متابع
    """,
    "unauthorized": "❌ ليس لديك صلاحية للوصول إلى هذا المورد"
}

# ==================== رسائل المساعدة ====================

HELP_MESSAGES = {
    "main": """
📖 **مساعدة البوت**

🤖 **الأوامر:**
• `/start` - بدء البوت
• `/help` - عرض هذه الرسالة
• `/settings` - إعدادات البوت

🎯 **الميزات:**
• ⚙️ الإعدادات - تعديل إعدادات التداول
• 📊 حالة الحساب - عرض حالة حسابك
• 🔄 الصفقات المفتوحة - عرض الصفقات النشطة
• 📈 تاريخ التداول - سجل التداولات

💡 **نصيحة:** استخدم الأزرار للتنقل بين القوائم
    """,
    
    "webhook": """
📖 **كيفية استخدام Webhook**

🔗 **رابط Webhook الخاص بك:**
```
{webhook_url}
```

**🎯 ما هو Webhook؟**
Webhook هو رابط خاص بك يستقبل الإشارات من TradingView.

**📱 كيفية الإعداد:**
1. افتح TradingView
2. أنشئ Alert جديد
3. اختر "Webhook URL"
4. انسخ الرابط أعلاه

**📋 تنسيق الإشارة:**
```json
{{
    "signal": "buy",
    "symbol": "BTCUSDT"
}}
```
    """
}

# ==================== دوال مساعدة ====================

def get_welcome_message(user_type: str, **kwargs) -> str:
    """الحصول على رسالة ترحيب"""
    template = WELCOME_MESSAGES.get(user_type, WELCOME_MESSAGES["user"])
    return template.format(**kwargs)

def get_error_message(error_type: str, **kwargs) -> str:
    """الحصول على رسالة خطأ"""
    template = ERROR_MESSAGES.get(error_type, "❌ حدث خطأ")
    return template.format(**kwargs)

def get_success_message(message_type: str, **kwargs) -> str:
    """الحصول على رسالة نجاح"""
    template = SUCCESS_MESSAGES.get(message_type, "✅ تم بنجاح")
    return template.format(**kwargs)

__all__ = [
    'WELCOME_MESSAGES',
    'SETTINGS_MESSAGES',
    'ACCOUNT_MESSAGES',
    'TRADE_MESSAGES',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'WARNING_MESSAGES',
    'RISK_MANAGEMENT_MESSAGES',
    'DEVELOPER_MESSAGES',
    'HELP_MESSAGES',
    'get_welcome_message',
    'get_error_message',
    'get_success_message'
]

