#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعدادات المطورين
يحتوي على معلومات المطورين المعتمدين وصلاحياتهم
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# معلومات المطور الرئيسي (Nagdat)
MAIN_DEVELOPER = {
    'developer_id': int(os.getenv('ADMIN_USER_ID', "8169000394")),
    'developer_name': 'Nagdat',
    'developer_key': os.getenv('DEVELOPER_KEY', 'NAGDAT-KEY-2024-SECURE'),
    'webhook_url': None,  # سيتم تحديثه تلقائياً
    'is_active': True,
    'can_broadcast': True
}

# قائمة المطورين الإضافيين (يمكن إضافة مطورين آخرين)
ADDITIONAL_DEVELOPERS = [
    # مثال:
    # {
    #     'developer_id': 123456789,
    #     'developer_name': 'Developer Name',
    #     'developer_key': 'UNIQUE-KEY-HERE',
    #     'webhook_url': None,
    #     'is_active': True,
    #     'can_broadcast': True
    # }
]

# صلاحيات المطورين
DEVELOPER_PERMISSIONS = {
    'can_broadcast_signals': True,          # إرسال إشارات للمتابعين
    'can_manage_users': True,               # إدارة المستخدمين
    'can_view_all_positions': True,         # مشاهدة جميع الصفقات
    'can_modify_settings': True,            # تعديل إعدادات البوت
    'can_send_notifications': True,         # إرسال إشعارات جماعية
    'can_view_statistics': True,            # مشاهدة الإحصائيات
    'can_export_data': True                 # تصدير البيانات
}

# إعدادات إشارات المطورين
DEVELOPER_SIGNAL_SETTINGS = {
    'auto_execute': True,                   # تنفيذ تلقائي للإشارات
    'require_confirmation': False,          # يتطلب تأكيد من المستخدم
    'default_trade_amount': 100.0,          # المبلغ الافتراضي للتداول
    'max_signals_per_day': 50,              # الحد الأقصى للإشارات يومياً
    'signal_expiry_minutes': 5              # انتهاء صلاحية الإشارة (بالدقائق)
}

# رسائل المطورين
DEVELOPER_MESSAGES = {
    'welcome_developer': """
👨‍💻 مرحباً بك في لوحة التحكم للمطورين

أنت الآن في وضع المطور، لديك الصلاحيات التالية:
• 📡 إرسال إشارات لجميع المتابعين
• 👥 إدارة المستخدمين
• 📊 مشاهدة الإحصائيات
• ⚙️ تعديل إعدادات البوت
• 📱 إرسال إشعارات جماعية

استخدم الأزرار أدناه للتنقل في لوحة التحكم
    """,
    
    'signal_broadcast_success': """
✅ تم إرسال الإشارة بنجاح

📊 الإحصائيات:
• عدد المتابعين: {follower_count}
• تم الإرسال إلى: {sent_count}
• الرمز: {symbol}
• الإجراء: {action}
    """,
    
    'no_followers': "⚠️ لا يوجد متابعين حالياً لإرسال الإشارات إليهم",
    
    'permission_denied': "❌ ليس لديك صلاحية لتنفيذ هذا الإجراء",
    
    'follower_added': "✅ تم إضافة المستخدم {user_id} إلى قائمة المتابعين",
    
    'follower_removed': "✅ تم إزالة المستخدم {user_id} من قائمة المتابعين",
    
    'stats_header': """
📊 إحصائيات المطور

👤 المطور: {developer_name}
👥 عدد المتابعين: {follower_count}
📡 إجمالي الإشارات: {total_signals}
✅ الحالة: {'نشط' if is_active else 'غير نشط'}
📤 صلاحية البث: {'مفعلة' if can_broadcast else 'معطلة'}
    """
}

# قائمة الأوامر الخاصة بالمطورين
DEVELOPER_COMMANDS = {
    'broadcast': 'إرسال إشارة لجميع المتابعين',
    'stats': 'عرض الإحصائيات',
    'followers': 'إدارة المتابعين',
    'users': 'إدارة المستخدمين',
    'settings': 'إعدادات البوت',
    'notify': 'إرسال إشعار جماعي',
    'export': 'تصدير البيانات'
}

def get_all_developers():
    """الحصول على قائمة جميع المطورين"""
    all_developers = [MAIN_DEVELOPER]
    all_developers.extend(ADDITIONAL_DEVELOPERS)
    return all_developers

def is_developer(user_id: int) -> bool:
    """التحقق من أن المستخدم مطور"""
    all_devs = get_all_developers()
    return any(dev['developer_id'] == user_id for dev in all_devs)

def get_developer_by_id(developer_id: int):
    """الحصول على معلومات المطور حسب ID"""
    all_devs = get_all_developers()
    for dev in all_devs:
        if dev['developer_id'] == developer_id:
            return dev
    return None

