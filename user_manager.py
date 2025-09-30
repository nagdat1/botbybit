#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة المستخدمين مع بيئات منفصلة
يدعم كل مستخدم بيئة خاصة بالكامل
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import db_manager

logger = logging.getLogger(__name__)

class UserEnvironment:
    """بيئة المستخدم المنفصلة"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_data = None
        self.user_stats = None
        self.open_orders = []
        self.trade_history = []
        self.is_active = True
        self.last_update = datetime.now()
        
        # تحميل بيانات المستخدم
        self.load_user_data()
    
    def load_user_data(self):
        """تحميل بيانات المستخدم من قاعدة البيانات"""
        try:
            self.user_data = db_manager.get_user(self.user_id)
            self.user_stats = db_manager.get_user_stats(self.user_id)
            self.open_orders = db_manager.get_user_orders(self.user_id, 'open')
            self.trade_history = db_manager.get_trade_history(self.user_id, 50)
            
            if self.user_data:
                self.is_active = self.user_data.get('is_active', True)
            
            logger.info(f"تم تحميل بيانات المستخدم: {self.user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات المستخدم {self.user_id}: {e}")
    
    def refresh_data(self):
        """تحديث بيانات المستخدم"""
        self.load_user_data()
        self.last_update = datetime.now()
    
    def get_settings(self) -> Dict:
        """الحصول على إعدادات المستخدم"""
        if self.user_data:
            return self.user_data.get('settings', {})
        return {}
    
    def update_settings(self, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم"""
        try:
            current_settings = self.get_settings()
            current_settings.update(settings)
            
            success = db_manager.update_user_settings(self.user_id, current_settings)
            if success:
                self.refresh_data()
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم {self.user_id}: {e}")
            return False
    
    def set_active(self, is_active: bool) -> bool:
        """تحديث حالة نشاط المستخدم"""
        try:
            success = db_manager.set_user_active(self.user_id, is_active)
            if success:
                self.is_active = is_active
                self.refresh_data()
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة نشاط المستخدم {self.user_id}: {e}")
            return False
    
    def has_api_keys(self) -> bool:
        """التحقق من وجود مفاتيح API"""
        if self.user_data:
            api_key = self.user_data.get('api_key')
            api_secret = self.user_data.get('api_secret')
            return bool(api_key and api_secret)
        return False
    
    def get_api_keys(self) -> tuple:
        """الحصول على مفاتيح API"""
        if self.user_data:
            return (
                self.user_data.get('api_key', ''),
                self.user_data.get('api_secret', '')
            )
        return ('', '')
    
    def set_api_keys(self, api_key: str, api_secret: str) -> bool:
        """تحديث مفاتيح API"""
        try:
            success = db_manager.update_user_api(self.user_id, api_key, api_secret)
            if success:
                self.refresh_data()
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مفاتيح API للمستخدم {self.user_id}: {e}")
            return False
    
    def get_balance_info(self) -> Dict:
        """الحصول على معلومات الرصيد"""
        if self.user_stats:
            return {
                'balance': self.user_stats.get('balance', 10000),
                'available_balance': self.user_stats.get('available_balance', 10000),
                'margin_locked': self.user_stats.get('margin_locked', 0),
                'total_pnl': self.user_stats.get('total_pnl', 0)
            }
        return {
            'balance': 10000,
            'available_balance': 10000,
            'margin_locked': 0,
            'total_pnl': 0
        }
    
    def get_trading_stats(self) -> Dict:
        """الحصول على إحصائيات التداول"""
        if self.user_stats:
            return {
                'total_trades': self.user_stats.get('total_trades', 0),
                'winning_trades': self.user_stats.get('winning_trades', 0),
                'losing_trades': self.user_stats.get('losing_trades', 0),
                'win_rate': self.user_stats.get('win_rate', 0)
            }
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0
        }
    
    def get_open_orders(self) -> List[Dict]:
        """الحصول على الصفقات المفتوحة"""
        return self.open_orders
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ التداول"""
        return self.trade_history[:limit]
    
    def can_trade(self) -> bool:
        """التحقق من إمكانية التداول"""
        return self.is_active and self.has_api_keys()
    
    def get_user_info(self) -> Dict:
        """الحصول على معلومات المستخدم الشاملة"""
        return {
            'user_id': self.user_id,
            'user_data': self.user_data,
            'user_stats': self.user_stats,
            'settings': self.get_settings(),
            'balance_info': self.get_balance_info(),
            'trading_stats': self.get_trading_stats(),
            'open_orders': self.open_orders,
            'is_active': self.is_active,
            'has_api_keys': self.has_api_keys(),
            'can_trade': self.can_trade(),
            'last_update': self.last_update
        }

class UserManager:
    """مدير المستخدمين مع دعم البيئات المنفصلة"""
    
    def __init__(self):
        self.user_environments: Dict[int, UserEnvironment] = {}
        self.user_input_states: Dict[int, str] = {}
    
    def get_user_environment(self, user_id: int) -> UserEnvironment:
        """الحصول على بيئة المستخدم أو إنشاؤها"""
        if user_id not in self.user_environments:
            # إنشاء بيئة جديدة للمستخدم
            self.user_environments[user_id] = UserEnvironment(user_id)
            
            # إضافة المستخدم إلى قاعدة البيانات إذا لم يكن موجوداً
            if not self.user_environments[user_id].user_data:
                db_manager.add_user(user_id)
                self.user_environments[user_id].refresh_data()
        
        return self.user_environments[user_id]
    
    def refresh_user_environment(self, user_id: int):
        """تحديث بيئة المستخدم"""
        if user_id in self.user_environments:
            self.user_environments[user_id].refresh_data()
    
    def set_user_input_state(self, user_id: int, state: str):
        """تحديد حالة إدخال المستخدم"""
        self.user_input_states[user_id] = state
    
    def get_user_input_state(self, user_id: int) -> Optional[str]:
        """الحصول على حالة إدخال المستخدم"""
        return self.user_input_states.get(user_id)
    
    def clear_user_input_state(self, user_id: int):
        """مسح حالة إدخال المستخدم"""
        if user_id in self.user_input_states:
            del self.user_input_states[user_id]
    
    def is_user_active(self, user_id: int) -> bool:
        """التحقق من نشاط المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.is_active
    
    def can_user_trade(self, user_id: int) -> bool:
        """التحقق من إمكانية تداول المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.can_trade()
    
    def get_user_settings(self, user_id: int) -> Dict:
        """الحصول على إعدادات المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_settings()
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.update_settings(settings)
    
    def set_user_active(self, user_id: int, is_active: bool) -> bool:
        """تحديث حالة نشاط المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.set_active(is_active)
    
    def set_user_api_keys(self, user_id: int, api_key: str, api_secret: str) -> bool:
        """تحديث مفاتيح API للمستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.set_api_keys(api_key, api_secret)
    
    def get_user_balance(self, user_id: int) -> Dict:
        """الحصول على رصيد المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_balance_info()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """الحصول على إحصائيات المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_trading_stats()
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        """الحصول على صفقات المستخدم المفتوحة"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_open_orders()
    
    def get_user_trade_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ تداول المستخدم"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_trade_history(limit)
    
    def get_user_info(self, user_id: int) -> Dict:
        """الحصول على معلومات المستخدم الشاملة"""
        user_env = self.get_user_environment(user_id)
        return user_env.get_user_info()
    
    def cleanup_inactive_users(self, max_age_hours: int = 24):
        """تنظيف بيئات المستخدمين غير النشطين"""
        try:
            current_time = datetime.now()
            users_to_remove = []
            
            for user_id, user_env in self.user_environments.items():
                age_hours = (current_time - user_env.last_update).total_seconds() / 3600
                if age_hours > max_age_hours:
                    users_to_remove.append(user_id)
            
            for user_id in users_to_remove:
                del self.user_environments[user_id]
                logger.info(f"تم تنظيف بيئة المستخدم غير النشط: {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف المستخدمين غير النشطين: {e}")
    
    def get_all_active_users(self) -> List[int]:
        """الحصول على قائمة جميع المستخدمين النشطين"""
        active_users = []
        for user_id, user_env in self.user_environments.items():
            if user_env.is_active:
                active_users.append(user_id)
        return active_users
    
    def get_user_count(self) -> int:
        """الحصول على عدد المستخدمين"""
        return len(self.user_environments)
    
    def is_user_authorized(self, user_id: int) -> bool:
        """التحقق من صلاحية المستخدم"""
        # يمكن إضافة منطق إضافي للصلاحيات هنا
        return True

    def configure(self, require_verification: bool = True, session_timeout: int = 86400,
                  max_accounts: int = 3, demo_balance: float = 10000):
        """تكوين إعدادات إدارة المستخدمين"""
        try:
            logger.info(f"تكوين إدارة المستخدمين - المعاملات: require_verification={require_verification}, session_timeout={session_timeout}, max_accounts={max_accounts}, demo_balance={demo_balance}")

            # حفظ الإعدادات في مدير المستخدمين
            self.require_verification = require_verification
            self.session_timeout = session_timeout
            self.max_accounts = max_accounts
            self.demo_balance = demo_balance

            logger.info("✅ تم تكوين إدارة المستخدمين بنجاح")

        except Exception as e:
            logger.error(f"خطأ في تكوين إدارة المستخدمين: {e}")
            raise

    def get_status(self) -> Dict:
        """الحصول على حالة إدارة المستخدمين"""
        try:
            return {
                'total_users': self.get_user_count(),
                'active_users': len(self.get_all_active_users()),
                'user_environments_count': len(self.user_environments),
                'settings': {
                    'require_verification': getattr(self, 'require_verification', True),
                    'session_timeout': getattr(self, 'session_timeout', 86400),
                    'max_accounts': getattr(self, 'max_accounts', 3),
                    'demo_balance': getattr(self, 'demo_balance', 10000)
                }
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة إدارة المستخدمين: {e}")
            return {'error': str(e)}

# إنشاء مثيل عام لمدير المستخدمين
user_manager = UserManager()
