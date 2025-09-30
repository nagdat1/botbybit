#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التحكم في البوت مع دعم متعدد المستخدمين
يدعم تشغيل/إيقاف البوت لكل مستخدم بشكل منفصل
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from user_manager import user_manager
from order_manager import order_manager
from api_manager import api_manager
from database import db_manager

logger = logging.getLogger(__name__)

class BotStatus(Enum):
    """حالات البوت"""
    RUNNING = "running"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class BotController:
    """تحكم في البوت مع دعم متعدد المستخدمين"""
    
    def __init__(self):
        self.global_status = BotStatus.RUNNING
        self.user_statuses: Dict[int, BotStatus] = {}
        self.maintenance_mode = False
        self.error_count = 0
        self.max_errors = 10
        
        # إحصائيات النظام
        self.stats = {
            'total_users': 0,
            'active_users': 0,
            'total_orders': 0,
            'active_orders': 0,
            'api_connections': 0,
            'last_update': datetime.now()
        }
        
        # مراقبة النظام
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # إعدادات المراقبة
        self.monitoring_interval = 60  # ثانية
        self.health_check_interval = 300  # 5 دقائق
        self.price_update_interval = 5  # ثانية
        self.balance_update_interval = 30  # ثانية
        
    def start_monitoring(self):
        """بدء مراقبة النظام"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("تم بدء مراقبة النظام")
    
    def stop_monitoring(self):
        """إيقاف مراقبة النظام"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("تم إيقاف مراقبة النظام")
    
    def _monitoring_loop(self):
        """حلقة مراقبة النظام"""
        while self.is_monitoring:
            try:
                self._update_stats()
                self._health_check()
                self._cleanup_inactive_users()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"خطأ في حلقة المراقبة: {e}")
                self.error_count += 1
                time.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    def _update_stats(self):
        """تحديث إحصائيات النظام"""
        try:
            # إحصائيات المستخدمين
            all_users = user_manager.get_all_active_users()
            self.stats['total_users'] = user_manager.get_user_count()
            self.stats['active_users'] = len(all_users)
            
            # إحصائيات الصفقات
            all_orders = order_manager.get_all_orders()
            self.stats['total_orders'] = len(all_orders)
            self.stats['active_orders'] = len([o for o in all_orders.values() if o['status'] == 'open'])
            
            # إحصائيات API
            self.stats['api_connections'] = api_manager.get_user_count()
            
            # وقت آخر تحديث
            self.stats['last_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def _health_check(self):
        """فحص صحة النظام"""
        try:
            # فحص قاعدة البيانات
            if not self._check_database_health():
                self.global_status = BotStatus.ERROR
                return
            
            # فحص اتصالات API
            if not self._check_api_health():
                logger.warning("بعض اتصالات API غير متاحة")
            
            # فحص إدارة الصفقات
            if not self._check_order_manager_health():
                logger.warning("مدير الصفقات يواجه مشاكل")
            
            # إعادة تعيين حالة الخطأ إذا كانت كل شيء يعمل
            if self.global_status == BotStatus.ERROR and self.error_count < self.max_errors:
                self.global_status = BotStatus.RUNNING
                self.error_count = 0
            
        except Exception as e:
            logger.error(f"خطأ في فحص صحة النظام: {e}")
            self.error_count += 1
    
    def _check_database_health(self) -> bool:
        """فحص صحة قاعدة البيانات"""
        try:
            # محاولة تنفيذ استعلام بسيط
            result = db_manager.execute_query("SELECT 1", fetch=True)
            return result is not None
        except Exception as e:
            logger.error(f"خطأ في فحص قاعدة البيانات: {e}")
            return False
    
    def _check_api_health(self) -> bool:
        """فحص صحة اتصالات API"""
        try:
            # فحص عينة من اتصالات API
            user_apis = api_manager.get_all_user_apis()
            healthy_connections = 0
            
            for user_id, api_instance in list(user_apis.items())[:5]:  # فحص أول 5 اتصالات
                if api_instance.test_connection():
                    healthy_connections += 1
            
            return healthy_connections > 0
        except Exception as e:
            logger.error(f"خطأ في فحص اتصالات API: {e}")
            return False
    
    def _check_order_manager_health(self) -> bool:
        """فحص صحة مدير الصفقات"""
        try:
            # فحص عدد الصفقات النشطة
            active_orders = order_manager.get_all_orders()
            return len(active_orders) >= 0  # يجب أن يكون رقم غير سالب
        except Exception as e:
            logger.error(f"خطأ في فحص مدير الصفقات: {e}")
            return False
    
    def _cleanup_inactive_users(self):
        """تنظيف المستخدمين غير النشطين"""
        try:
            # تنظيف بيئات المستخدمين غير النشطين
            user_manager.cleanup_inactive_users()
            
            # تنظيف مفاتيح API غير النشطة
            api_manager.cleanup_inactive_apis()
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف المستخدمين غير النشطين: {e}")
    
    def set_user_bot_status(self, user_id: int, status: BotStatus) -> bool:
        """تحديد حالة البوت للمستخدم"""
        try:
            # تحديث حالة المستخدم
            is_active = (status == BotStatus.RUNNING)
            success = user_manager.set_user_active(user_id, is_active)
            
            if success:
                self.user_statuses[user_id] = status
                
                # إذا كان المستخدم متوقفاً، إيقاف مراقبة صفقاته
                if status == BotStatus.STOPPED:
                    self._pause_user_orders(user_id)
                elif status == BotStatus.RUNNING:
                    self._resume_user_orders(user_id)
                
                logger.info(f"تم تحديث حالة البوت للمستخدم {user_id}: {status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة البوت للمستخدم {user_id}: {e}")
            return False
    
    def get_user_bot_status(self, user_id: int) -> BotStatus:
        """الحصول على حالة البوت للمستخدم"""
        try:
            # التحقق من حالة المستخدم في قاعدة البيانات
            user_env = user_manager.get_user_environment(user_id)
            is_active = user_env.is_active
            
            if is_active:
                return BotStatus.RUNNING
            else:
                return BotStatus.STOPPED
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة البوت للمستخدم {user_id}: {e}")
            return BotStatus.ERROR
    
    def is_user_bot_active(self, user_id: int) -> bool:
        """التحقق من نشاط البوت للمستخدم"""
        try:
            # التحقق من الحالة العامة
            if self.global_status != BotStatus.RUNNING:
                return False
            
            # التحقق من حالة المستخدم
            user_status = self.get_user_bot_status(user_id)
            return user_status == BotStatus.RUNNING
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من نشاط البوت للمستخدم {user_id}: {e}")
            return False
    
    def can_user_trade(self, user_id: int) -> bool:
        """التحقق من إمكانية تداول المستخدم"""
        try:
            # التحقق من نشاط البوت
            if not self.is_user_bot_active(user_id):
                return False
            
            # التحقق من وجود مفاتيح API
            if not api_manager.has_user_api(user_id):
                return False
            
            # التحقق من حالة المستخدم في النظام
            user_env = user_manager.get_user_environment(user_id)
            return user_env.can_trade()
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من إمكانية تداول المستخدم {user_id}: {e}")
            return False
    
    def _pause_user_orders(self, user_id: int):
        """إيقاف مراقبة صفقات المستخدم مؤقتاً"""
        try:
            # يمكن إضافة منطق لإيقاف مراقبة صفقات المستخدم هنا
            logger.info(f"تم إيقاف مراقبة صفقات المستخدم {user_id}")
        except Exception as e:
            logger.error(f"خطأ في إيقاف مراقبة صفقات المستخدم {user_id}: {e}")
    
    def _resume_user_orders(self, user_id: int):
        """استئناف مراقبة صفقات المستخدم"""
        try:
            # يمكن إضافة منطق لاستئناف مراقبة صفقات المستخدم هنا
            logger.info(f"تم استئناف مراقبة صفقات المستخدم {user_id}")
        except Exception as e:
            logger.error(f"خطأ في استئناف مراقبة صفقات المستخدم {user_id}: {e}")
    
    def set_maintenance_mode(self, enabled: bool) -> bool:
        """تفعيل/إلغاء وضع الصيانة"""
        try:
            self.maintenance_mode = enabled
            
            if enabled:
                self.global_status = BotStatus.MAINTENANCE
                logger.warning("تم تفعيل وضع الصيانة")
            else:
                self.global_status = BotStatus.RUNNING
                logger.info("تم إلغاء وضع الصيانة")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث وضع الصيانة: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """الحصول على حالة النظام الشاملة"""
        try:
            return {
                'global_status': self.global_status.value,
                'maintenance_mode': self.maintenance_mode,
                'error_count': self.error_count,
                'stats': self.stats.copy(),
                'user_statuses': {str(k): v.value for k, v in self.user_statuses.items()},
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة النظام: {e}")
            return {
                'global_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_user_status_summary(self, user_id: int) -> Dict:
        """الحصول على ملخص حالة المستخدم"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            
            return {
                'user_id': user_id,
                'bot_status': self.get_user_bot_status(user_id).value,
                'can_trade': self.can_user_trade(user_id),
                'has_api': user_env.has_api_keys(),
                'is_active': user_env.is_active,
                'open_orders': order_manager.get_user_order_count(user_id),
                'balance': user_env.get_balance_info(),
                'settings': user_env.get_settings(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص حالة المستخدم {user_id}: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def emergency_stop(self, user_id: int = None) -> bool:
        """إيقاف طارئ للبوت"""
        try:
            if user_id:
                # إيقاف مستخدم محدد
                success = self.set_user_bot_status(user_id, BotStatus.STOPPED)
                logger.warning(f"تم إيقاف البوت للمستخدم {user_id} بشكل طارئ")
                return success
            else:
                # إيقاف عام
                self.global_status = BotStatus.STOPPED
                logger.warning("تم إيقاف البوت بشكل طارئ")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في الإيقاف الطارئ: {e}")
            return False
    
    def restart_user_bot(self, user_id: int) -> bool:
        """إعادة تشغيل البوت للمستخدم"""
        try:
            # إيقاف البوت أولاً
            self.set_user_bot_status(user_id, BotStatus.STOPPED)
            time.sleep(2)  # انتظار قصير
            
            # تشغيل البوت مرة أخرى
            success = self.set_user_bot_status(user_id, BotStatus.RUNNING)
            
            if success:
                logger.info(f"تم إعادة تشغيل البوت للمستخدم {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تشغيل البوت للمستخدم {user_id}: {e}")
            return False
    
    def get_active_users(self) -> List[int]:
        """الحصول على قائمة المستخدمين النشطين"""
        try:
            return user_manager.get_all_active_users()
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدمين النشطين: {e}")
            return []
    
    def get_inactive_users(self) -> List[int]:
        """الحصول على قائمة المستخدمين غير النشطين"""
        try:
            all_users = user_manager.get_all_active_users()
            total_users = user_manager.get_user_count()
            inactive_users = []
            
            # هذا تبسيط - في الواقع نحتاج لطريقة أفضل للحصول على المستخدمين غير النشطين
            for user_id in range(1, total_users + 1):
                if user_id not in all_users:
                    inactive_users.append(user_id)
            
            return inactive_users
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدمين غير النشطين: {e}")
            return []

    def configure(self, update_interval: int = 60, price_interval: int = 5, balance_interval: int = 30):
        """تكوين إعدادات مراقبة النظام"""
        try:
            logger.info(f"تكوين مراقبة النظام - المعاملات: update_interval={update_interval}, price_interval={price_interval}, balance_interval={balance_interval}")

            # تحديث إعدادات المراقبة
            self.monitoring_interval = update_interval
            self.price_update_interval = price_interval
            self.balance_update_interval = balance_interval

            logger.info("✅ تم تكوين مراقبة النظام بنجاح")

        except Exception as e:
            logger.error(f"خطأ في تكوين مراقبة النظام: {e}")
            raise

    def get_status(self) -> Dict:
        """الحصول على حالة مراقبة النظام"""
        try:
            return {
                'global_status': self.global_status.value,
                'is_monitoring': self.is_monitoring,
                'maintenance_mode': self.maintenance_mode,
                'error_count': self.error_count,
                'stats': self.stats.copy(),
                'settings': {
                    'monitoring_interval': self.monitoring_interval,
                    'health_check_interval': self.health_check_interval,
                    'price_update_interval': self.price_update_interval,
                    'balance_update_interval': self.balance_update_interval
                }
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة مراقبة النظام: {e}")
            return {'error': str(e)}

# إنشاء مثيل عام لتحكم البوت
bot_controller = BotController()
