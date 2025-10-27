# Users Module - إدارة المستخدمين
"""
هذا المجلد يحتوي على جميع ملفات إدارة المستخدمين
"""

from .database import DatabaseManager

# إنشاء instance من DatabaseManager
db_manager = DatabaseManager()

# إنشاء instance من UserManager (سيتم استيراده من user_manager module)
try:
    from .user_manager import UserManager
except ImportError:
    UserManager = None

__all__ = [
    'DatabaseManager',
    'db_manager',
    'UserManager'
]

