#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الحماية والأمان للبوت
يدعم حماية المستخدمين من التداخل والوصول غير المصرح به
"""

import logging
import hashlib
import hmac
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import json

from user_manager import user_manager
from database import db_manager

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """مستويات الأمان"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """أنواع التهديدات"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMITING = "rate_limiting"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_ABUSE = "api_abuse"
    DATA_BREACH = "data_breach"
    SYSTEM_ABUSE = "system_abuse"

class SecurityManager:
    """مدير الأمان والحماية"""
    
    def __init__(self):
        self.user_sessions: Dict[int, Dict] = {}
        self.failed_attempts: Dict[int, List[datetime]] = {}
        self.blocked_users: Set[int] = set()
        self.suspicious_activities: Dict[int, List[Dict]] = {}
        
        # إعدادات الأمان
        self.max_failed_attempts = 5
        self.block_duration = 3600  # ساعة واحدة
        self.session_timeout = 7200  # ساعتان
        self.rate_limit_window = 60  # دقيقة واحدة
        self.max_requests_per_minute = 30
        
        # مراقبة الأمان
        self.security_monitor_thread = None
        self.is_monitoring = False
        
        # إحصائيات الأمان
        self.security_stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'failed_attempts': 0,
            'suspicious_activities': 0,
            'last_update': datetime.now()
        }
        
        # قفل للعمليات المتزامنة
        self.lock = threading.Lock()
    
    def start_security_monitoring(self):
        """بدء مراقبة الأمان"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.security_monitor_thread = threading.Thread(
                target=self._security_monitoring_loop, daemon=True
            )
            self.security_monitor_thread.start()
            logger.info("تم بدء مراقبة الأمان")
    
    def stop_security_monitoring(self):
        """إيقاف مراقبة الأمان"""
        self.is_monitoring = False
        if self.security_monitor_thread:
            self.security_monitor_thread.join(timeout=5)
        logger.info("تم إيقاف مراقبة الأمان")
    
    def _security_monitoring_loop(self):
        """حلقة مراقبة الأمان"""
        while self.is_monitoring:
            try:
                self._cleanup_expired_sessions()
                self._cleanup_failed_attempts()
                self._analyze_suspicious_activities()
                self._update_security_stats()
                time.sleep(60)  # فحص كل دقيقة
            except Exception as e:
                logger.error(f"خطأ في حلقة مراقبة الأمان: {e}")
                time.sleep(60)
    
    def authenticate_user(self, user_id: int, request_type: str = "general") -> Tuple[bool, str]:
        """مصادقة المستخدم"""
        try:
            with self.lock:
                # التحقق من المستخدمين المحظورين
                if user_id in self.blocked_users:
                    self._log_security_event(
                        user_id, ThreatType.UNAUTHORIZED_ACCESS, 
                        SecurityLevel.HIGH, "محاولة وصول من مستخدم محظور"
                    )
                    return False, "المستخدم محظور مؤقتاً"
                
                # التحقق من المحاولات الفاشلة
                if self._check_failed_attempts(user_id):
                    self._block_user(user_id)
                    return False, "تم حظر المستخدم بسبب المحاولات الفاشلة المتكررة"
                
                # التحقق من حد المعدل
                if not self._check_rate_limit(user_id):
                    self._log_security_event(
                        user_id, ThreatType.RATE_LIMITING, 
                        SecurityLevel.MEDIUM, "تجاوز حد المعدل"
                    )
                    return False, "تم تجاوز حد الطلبات المسموح"
                
                # إنشاء/تحديث الجلسة
                self._create_or_update_session(user_id, request_type)
                
                # تسجيل الطلب الناجح
                self.security_stats['total_requests'] += 1
                
                return True, "مصادقة ناجحة"
                
        except Exception as e:
            logger.error(f"خطأ في مصادقة المستخدم {user_id}: {e}")
            return False, "خطأ في المصادقة"
    
    def _check_failed_attempts(self, user_id: int) -> bool:
        """فحص المحاولات الفاشلة"""
        try:
            if user_id not in self.failed_attempts:
                return False
            
            # إزالة المحاولات القديمة (أكثر من ساعة)
            current_time = datetime.now()
            self.failed_attempts[user_id] = [
                attempt for attempt in self.failed_attempts[user_id]
                if (current_time - attempt).total_seconds() < self.block_duration
            ]
            
            # فحص عدد المحاولات
            return len(self.failed_attempts[user_id]) >= self.max_failed_attempts
            
        except Exception as e:
            logger.error(f"خطأ في فحص المحاولات الفاشلة: {e}")
            return False
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """فحص حد المعدل"""
        try:
            if user_id not in self.user_sessions:
                return True
            
            session = self.user_sessions[user_id]
            current_time = datetime.now()
            
            # إزالة الطلبات القديمة
            session['requests'] = [
                req_time for req_time in session['requests']
                if (current_time - req_time).total_seconds() < self.rate_limit_window
            ]
            
            # فحص عدد الطلبات
            return len(session['requests']) < self.max_requests_per_minute
            
        except Exception as e:
            logger.error(f"خطأ في فحص حد المعدل: {e}")
            return True
    
    def _create_or_update_session(self, user_id: int, request_type: str):
        """إنشاء أو تحديث جلسة المستخدم"""
        try:
            current_time = datetime.now()
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    'created_at': current_time,
                    'last_activity': current_time,
                    'requests': [],
                    'request_types': [],
                    'session_id': self._generate_session_id(user_id)
                }
            
            session = self.user_sessions[user_id]
            session['last_activity'] = current_time
            session['requests'].append(current_time)
            session['request_types'].append(request_type)
            
            # الاحتفاظ بآخر 100 طلب فقط
            if len(session['requests']) > 100:
                session['requests'] = session['requests'][-100:]
                session['request_types'] = session['request_types'][-100:]
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء/تحديث الجلسة: {e}")
    
    def _generate_session_id(self, user_id: int) -> str:
        """إنشاء معرف جلسة فريد"""
        try:
            timestamp = str(int(time.time()))
            data = f"{user_id}_{timestamp}_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}"
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        except Exception as e:
            logger.error(f"خطأ في إنشاء معرف الجلسة: {e}")
            return f"session_{user_id}_{int(time.time())}"
    
    def record_failed_attempt(self, user_id: int, reason: str = "unknown"):
        """تسجيل محاولة فاشلة"""
        try:
            with self.lock:
                if user_id not in self.failed_attempts:
                    self.failed_attempts[user_id] = []
                
                self.failed_attempts[user_id].append(datetime.now())
                self.security_stats['failed_attempts'] += 1
                
                # تسجيل الحدث الأمني
                self._log_security_event(
                    user_id, ThreatType.UNAUTHORIZED_ACCESS, 
                    SecurityLevel.MEDIUM, f"محاولة فاشلة: {reason}"
                )
                
                logger.warning(f"محاولة فاشلة للمستخدم {user_id}: {reason}")
                
        except Exception as e:
            logger.error(f"خطأ في تسجيل المحاولة الفاشلة: {e}")
    
    def _block_user(self, user_id: int, duration: int = None):
        """حظر المستخدم"""
        try:
            with self.lock:
                self.blocked_users.add(user_id)
                
                if duration is None:
                    duration = self.block_duration
                
                # جدولة إلغاء الحظر
                threading.Timer(
                    duration, 
                    lambda: self._unblock_user(user_id)
                ).start()
                
                self._log_security_event(
                    user_id, ThreatType.UNAUTHORIZED_ACCESS, 
                    SecurityLevel.HIGH, f"تم حظر المستخدم لمدة {duration} ثانية"
                )
                
                logger.warning(f"تم حظر المستخدم {user_id} لمدة {duration} ثانية")
                
        except Exception as e:
            logger.error(f"خطأ في حظر المستخدم: {e}")
    
    def _unblock_user(self, user_id: int):
        """إلغاء حظر المستخدم"""
        try:
            with self.lock:
                if user_id in self.blocked_users:
                    self.blocked_users.remove(user_id)
                    
                    # مسح المحاولات الفاشلة
                    if user_id in self.failed_attempts:
                        del self.failed_attempts[user_id]
                    
                    logger.info(f"تم إلغاء حظر المستخدم {user_id}")
                    
        except Exception as e:
            logger.error(f"خطأ في إلغاء حظر المستخدم: {e}")
    
    def is_user_blocked(self, user_id: int) -> bool:
        """التحقق من حظر المستخدم"""
        return user_id in self.blocked_users
    
    def detect_suspicious_activity(self, user_id: int, activity_type: str, details: Dict) -> bool:
        """كشف الأنشطة المشبوهة"""
        try:
            suspicious = False
            threat_level = SecurityLevel.LOW
            
            # فحص الأنشطة المشبوهة المختلفة
            if activity_type == "rapid_requests":
                if self._check_rapid_requests(user_id):
                    suspicious = True
                    threat_level = SecurityLevel.MEDIUM
            
            elif activity_type == "unusual_trading":
                if self._check_unusual_trading(user_id, details):
                    suspicious = True
                    threat_level = SecurityLevel.HIGH
            
            elif activity_type == "api_abuse":
                if self._check_api_abuse(user_id, details):
                    suspicious = True
                    threat_level = SecurityLevel.CRITICAL
            
            elif activity_type == "data_access":
                if self._check_data_access(user_id, details):
                    suspicious = True
                    threat_level = SecurityLevel.HIGH
            
            # تسجيل النشاط المشبوه
            if suspicious:
                self._log_suspicious_activity(user_id, activity_type, threat_level, details)
                self.security_stats['suspicious_activities'] += 1
                
                # اتخاذ إجراءات إضافية حسب مستوى التهديد
                if threat_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                    self._take_security_action(user_id, threat_level, activity_type)
            
            return suspicious
            
        except Exception as e:
            logger.error(f"خطأ في كشف النشاط المشبوه: {e}")
            return False
    
    def _check_rapid_requests(self, user_id: int) -> bool:
        """فحص الطلبات السريعة"""
        try:
            if user_id not in self.user_sessions:
                return False
            
            session = self.user_sessions[user_id]
            requests = session['requests']
            
            if len(requests) < 10:
                return False
            
            # فحص الطلبات في آخر دقيقة
            current_time = datetime.now()
            recent_requests = [
                req for req in requests
                if (current_time - req).total_seconds() < 60
            ]
            
            return len(recent_requests) > 20  # أكثر من 20 طلب في الدقيقة
            
        except Exception as e:
            logger.error(f"خطأ في فحص الطلبات السريعة: {e}")
            return False
    
    def _check_unusual_trading(self, user_id: int, details: Dict) -> bool:
        """فحص التداول غير العادي"""
        try:
            # فحص حجم التداول
            trade_amount = details.get('amount', 0)
            user_env = user_manager.get_user_environment(user_id)
            balance = user_env.get_balance_info()['balance']
            
            # إذا كان حجم التداول أكثر من 50% من الرصيد
            if trade_amount > balance * 0.5:
                return True
            
            # فحص تكرار التداول
            if user_id not in self.user_sessions:
                return False
            
            session = self.user_sessions[user_id]
            request_types = session['request_types']
            
            # فحص عدد أوامر التداول في آخر 10 دقائق
            current_time = datetime.now()
            recent_trades = [
                req_type for i, req_type in enumerate(request_types)
                if req_type in ['buy', 'sell'] and 
                (current_time - session['requests'][i]).total_seconds() < 600
            ]
            
            return len(recent_trades) > 10  # أكثر من 10 صفقات في 10 دقائق
            
        except Exception as e:
            logger.error(f"خطأ في فحص التداول غير العادي: {e}")
            return False
    
    def _check_api_abuse(self, user_id: int, details: Dict) -> bool:
        """فحص إساءة استخدام API"""
        try:
            # فحص عدد طلبات API
            api_requests = details.get('api_requests', 0)
            time_window = details.get('time_window', 60)  # دقيقة واحدة
            
            # أكثر من 100 طلب API في الدقيقة
            if api_requests > 100:
                return True
            
            # فحص أنواع الطلبات
            request_types = details.get('request_types', [])
            if len(set(request_types)) > 20:  # أكثر من 20 نوع طلب مختلف
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص إساءة استخدام API: {e}")
            return False
    
    def _check_data_access(self, user_id: int, details: Dict) -> bool:
        """فحص الوصول للبيانات"""
        try:
            # فحص محاولات الوصول لبيانات مستخدمين آخرين
            accessed_user_id = details.get('accessed_user_id')
            if accessed_user_id and accessed_user_id != user_id:
                return True
            
            # فحص محاولات الوصول لبيانات حساسة
            sensitive_data = details.get('sensitive_data', False)
            if sensitive_data:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص الوصول للبيانات: {e}")
            return False
    
    def _log_suspicious_activity(self, user_id: int, activity_type: str, 
                               threat_level: SecurityLevel, details: Dict):
        """تسجيل النشاط المشبوه"""
        try:
            if user_id not in self.suspicious_activities:
                self.suspicious_activities[user_id] = []
            
            activity_record = {
                'activity_type': activity_type,
                'threat_level': threat_level.value,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            self.suspicious_activities[user_id].append(activity_record)
            
            # الاحتفاظ بآخر 50 نشاط فقط
            if len(self.suspicious_activities[user_id]) > 50:
                self.suspicious_activities[user_id] = self.suspicious_activities[user_id][-50:]
            
            logger.warning(f"نشاط مشبوه للمستخدم {user_id}: {activity_type} - {threat_level.value}")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل النشاط المشبوه: {e}")
    
    def _log_security_event(self, user_id: int, threat_type: ThreatType, 
                          security_level: SecurityLevel, description: str):
        """تسجيل الحدث الأمني"""
        try:
            event = {
                'user_id': user_id,
                'threat_type': threat_type.value,
                'security_level': security_level.value,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.warning(f"حدث أمني: {json.dumps(event, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الحدث الأمني: {e}")
    
    def _take_security_action(self, user_id: int, threat_level: SecurityLevel, activity_type: str):
        """اتخاذ إجراء أمني"""
        try:
            if threat_level == SecurityLevel.CRITICAL:
                # حظر فوري
                self._block_user(user_id, 7200)  # حظر لمدة ساعتين
                logger.critical(f"حظر فوري للمستخدم {user_id} بسبب {activity_type}")
                
            elif threat_level == SecurityLevel.HIGH:
                # حظر مؤقت
                self._block_user(user_id, 1800)  # حظر لمدة 30 دقيقة
                logger.warning(f"حظر مؤقت للمستخدم {user_id} بسبب {activity_type}")
            
        except Exception as e:
            logger.error(f"خطأ في اتخاذ الإجراء الأمني: {e}")
    
    def _cleanup_expired_sessions(self):
        """تنظيف الجلسات المنتهية الصلاحية"""
        try:
            current_time = datetime.now()
            expired_users = []
            
            for user_id, session in self.user_sessions.items():
                if (current_time - session['last_activity']).total_seconds() > self.session_timeout:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del self.user_sessions[user_id]
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف الجلسات المنتهية: {e}")
    
    def _cleanup_failed_attempts(self):
        """تنظيف المحاولات الفاشلة القديمة"""
        try:
            current_time = datetime.now()
            
            for user_id in list(self.failed_attempts.keys()):
                self.failed_attempts[user_id] = [
                    attempt for attempt in self.failed_attempts[user_id]
                    if (current_time - attempt).total_seconds() < self.block_duration
                ]
                
                if not self.failed_attempts[user_id]:
                    del self.failed_attempts[user_id]
                    
        except Exception as e:
            logger.error(f"خطأ في تنظيف المحاولات الفاشلة: {e}")
    
    def _analyze_suspicious_activities(self):
        """تحليل الأنشطة المشبوهة"""
        try:
            for user_id, activities in self.suspicious_activities.items():
                if len(activities) > 10:  # أكثر من 10 أنشطة مشبوهة
                    self._take_security_action(user_id, SecurityLevel.HIGH, "repeated_suspicious_activity")
                    
        except Exception as e:
            logger.error(f"خطأ في تحليل الأنشطة المشبوهة: {e}")
    
    def _update_security_stats(self):
        """تحديث إحصائيات الأمان"""
        try:
            self.security_stats['last_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إحصائيات الأمان: {e}")
    
    def get_security_report(self, user_id: int = None) -> Dict:
        """الحصول على تقرير الأمان"""
        try:
            if user_id:
                # تقرير مستخدم محدد
                return {
                    'user_id': user_id,
                    'is_blocked': self.is_user_blocked(user_id),
                    'failed_attempts': len(self.failed_attempts.get(user_id, [])),
                    'suspicious_activities': len(self.suspicious_activities.get(user_id, [])),
                    'session_active': user_id in self.user_sessions,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # تقرير عام
                return {
                    'security_stats': self.security_stats.copy(),
                    'blocked_users_count': len(self.blocked_users),
                    'active_sessions': len(self.user_sessions),
                    'users_with_failed_attempts': len(self.failed_attempts),
                    'users_with_suspicious_activities': len(self.suspicious_activities),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على تقرير الأمان: {e}")
            return {'error': str(e)}
    
    def validate_user_access(self, user_id: int, resource: str) -> bool:
        """التحقق من صلاحية الوصول للمورد"""
        try:
            # التحقق من المصادقة الأساسية
            authenticated, _ = self.authenticate_user(user_id, f"access_{resource}")
            if not authenticated:
                return False
            
            # التحقق من حظر المستخدم
            if self.is_user_blocked(user_id):
                return False
            
            # التحقق من صلاحيات الوصول للمورد
            if resource == "user_data":
                return True  # المستخدم يمكنه الوصول لبياناته فقط
            elif resource == "admin_functions":
                return False  # يحتاج صلاحيات إدارية
            elif resource == "trading":
                return user_manager.can_user_trade(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحية الوصول: {e}")
            return False

# إنشاء مثيل عام لمدير الأمان
security_manager = SecurityManager()
