# -*- coding: utf-8 -*-
"""
مدير أخطاء التداول
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class TradeErrorManager:
    """مدير أخطاء التداول"""
    
    def __init__(self):
        self.error_history: Dict[str, List[Dict]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.last_error_time: Dict[str, datetime] = {}
        self.error_thresholds = {
            'max_errors_per_hour': 10,
            'max_consecutive_errors': 5,
            'error_cooldown_minutes': 5
        }
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None) -> bool:
        """تسجيل خطأ"""
        try:
            current_time = datetime.now()
            
            # تسجيل الخطأ
            error_record = {
                'timestamp': current_time.isoformat(),
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {}
            }
            
            self.error_history[error_type].append(error_record)
            self.error_counts[error_type] += 1
            self.last_error_time[error_type] = current_time
            
            # الاحتفاظ بآخر 100 خطأ لكل نوع
            if len(self.error_history[error_type]) > 100:
                self.error_history[error_type] = self.error_history[error_type][-100:]
            
            logger.error(f"خطأ مسجل: {error_type} - {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الخطأ: {e}")
            return False
    
    def should_throttle_error(self, error_type: str) -> bool:
        """التحقق من ضرورة تقليل تكرار الخطأ"""
        try:
            current_time = datetime.now()
            
            # التحقق من التبريد
            if error_type in self.last_error_time:
                time_diff = current_time - self.last_error_time[error_type]
                if time_diff.total_seconds() < self.error_thresholds['error_cooldown_minutes'] * 60:
                    return True
            
            # التحقق من عدد الأخطاء في الساعة الماضية
            hour_ago = current_time - timedelta(hours=1)
            recent_errors = [
                error for error in self.error_history[error_type]
                if datetime.fromisoformat(error['timestamp']) > hour_ago
            ]
            
            if len(recent_errors) >= self.error_thresholds['max_errors_per_hour']:
                return True
            
            # التحقق من الأخطاء المتتالية
            consecutive_errors = 0
            for error in reversed(self.error_history[error_type][-10:]):  # آخر 10 أخطاء
                if datetime.fromisoformat(error['timestamp']) > hour_ago:
                    consecutive_errors += 1
                else:
                    break
            
            if consecutive_errors >= self.error_thresholds['max_consecutive_errors']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من تقليل التكرار: {e}")
            return False
    
    def get_error_summary(self, error_type: str = None) -> Dict:
        """الحصول على ملخص الأخطاء"""
        try:
            if error_type:
                # ملخص لنوع خطأ محدد
                errors = self.error_history[error_type]
                recent_errors = [
                    error for error in errors
                    if datetime.fromisoformat(error['timestamp']) > datetime.now() - timedelta(hours=24)
                ]
                
                return {
                    'error_type': error_type,
                    'total_errors': len(errors),
                    'recent_errors_24h': len(recent_errors),
                    'last_error': errors[-1] if errors else None,
                    'is_throttled': self.should_throttle_error(error_type)
                }
            else:
                # ملخص لجميع الأخطاء
                summary = {}
                for error_type_key in self.error_history.keys():
                    summary[error_type_key] = self.get_error_summary(error_type_key)
                
                return {
                    'total_error_types': len(self.error_history),
                    'error_types': summary,
                    'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص الأخطاء: {e}")
            return {}
    
    def clear_old_errors(self, days: int = 7) -> int:
        """مسح الأخطاء القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleared_count = 0
            
            for error_type in list(self.error_history.keys()):
                original_count = len(self.error_history[error_type])
                self.error_history[error_type] = [
                    error for error in self.error_history[error_type]
                    if datetime.fromisoformat(error['timestamp']) > cutoff_date
                ]
                cleared_count += original_count - len(self.error_history[error_type])
                
                # حذف نوع الخطأ إذا لم تعد هناك أخطاء
                if not self.error_history[error_type]:
                    del self.error_history[error_type]
                    if error_type in self.error_counts:
                        del self.error_counts[error_type]
                    if error_type in self.last_error_time:
                        del self.last_error_time[error_type]
            
            logger.info(f"تم مسح {cleared_count} خطأ قديم")
            return cleared_count
            
        except Exception as e:
            logger.error(f"خطأ في مسح الأخطاء القديمة: {e}")
            return 0
    
    def reset_error_counters(self) -> bool:
        """إعادة تعيين عدادات الأخطاء"""
        try:
            self.error_counts.clear()
            self.last_error_time.clear()
            logger.info("تم إعادة تعيين عدادات الأخطاء")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين العدادات: {e}")
            return False