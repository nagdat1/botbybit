#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المطورين - إدارة منفصلة لحسابات المطورين وصلاحياتهم
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from users.database import db_manager

logger = logging.getLogger(__name__)

class DeveloperManager:
    """مدير المطورين مع صلاحيات خاصة"""
    
    def __init__(self):
        self.developers: Dict[int, Dict] = {}  # تخزين مؤقت لبيانات المطورين
        self.developer_followers: Dict[int, List[int]] = {}  # المتابعين لكل مطور
        
        # تحميل المطورين من قاعدة البيانات
        self.load_all_developers()
    
    def load_all_developers(self):
        """تحميل جميع المطورين من قاعدة البيانات"""
        try:
            developers_data = db_manager.get_all_developers()
            
            for dev_data in developers_data:
                dev_id = dev_data['developer_id']
                self.developers[dev_id] = dev_data
                
                # تحميل المتابعين
                followers = db_manager.get_developer_followers(dev_id)
                self.developer_followers[dev_id] = followers
            
            logger.info(f"تم تحميل {len(self.developers)} مطور")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل المطورين: {e}")
    
    def create_developer(self, developer_id: int, developer_name: str, 
                        developer_key: str = None, webhook_url: str = None) -> bool:
        """إنشاء حساب مطور جديد"""
        try:
            # إنشاء في قاعدة البيانات
            success = db_manager.create_developer(
                developer_id=developer_id,
                developer_name=developer_name,
                developer_key=developer_key,
                webhook_url=webhook_url
            )
            
            if success:
                # تحميل بيانات المطور الجديد
                dev_data = db_manager.get_developer(developer_id)
                
                if dev_data:
                    self.developers[developer_id] = dev_data
                    self.developer_followers[developer_id] = []
                    
                    logger.info(f"تم إنشاء مطور جديد: {developer_id} - {developer_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المطور {developer_id}: {e}")
            return False
    
    def get_developer(self, developer_id: int) -> Optional[Dict]:
        """الحصول على بيانات المطور"""
        return self.developers.get(developer_id)
    
    def is_developer(self, user_id: int) -> bool:
        """التحقق من أن المستخدم مطور"""
        return user_id in self.developers
    
    def is_developer_active(self, developer_id: int) -> bool:
        """التحقق من أن المطور نشط"""
        dev_data = self.get_developer(developer_id)
        return dev_data and dev_data.get('is_active', False)
    
    def can_broadcast_signals(self, developer_id: int) -> bool:
        """التحقق من صلاحية المطور لإرسال إشارات عامة"""
        dev_data = self.get_developer(developer_id)
        return (dev_data and 
                dev_data.get('is_active', False) and 
                dev_data.get('can_broadcast', False))
    
    def update_developer_info(self, developer_id: int, updates: Dict) -> bool:
        """تحديث معلومات المطور"""
        try:
            success = db_manager.update_developer(developer_id, updates)
            
            if success:
                # تحديث في الذاكرة
                if developer_id in self.developers:
                    for key, value in updates.items():
                        self.developers[developer_id][key] = value
                
                logger.info(f"تم تحديث معلومات المطور {developer_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث معلومات المطور {developer_id}: {e}")
            return False
    
    def toggle_developer_active(self, developer_id: int) -> bool:
        """تبديل حالة تشغيل/إيقاف المطور"""
        try:
            success = db_manager.toggle_developer_active(developer_id)
            
            if success:
                # تحديث في الذاكرة
                if developer_id in self.developers:
                    current_status = self.developers[developer_id]['is_active']
                    self.developers[developer_id]['is_active'] = not current_status
                    
                    logger.info(f"تم تبديل حالة المطور {developer_id} إلى: {not current_status}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تبديل حالة المطور {developer_id}: {e}")
            return False
    
    def add_follower(self, developer_id: int, user_id: int) -> bool:
        """إضافة متابع للمطور"""
        try:
            success = db_manager.add_developer_follower(developer_id, user_id)
            
            if success:
                # تحديث في الذاكرة
                if developer_id not in self.developer_followers:
                    self.developer_followers[developer_id] = []
                
                if user_id not in self.developer_followers[developer_id]:
                    self.developer_followers[developer_id].append(user_id)
                
                logger.info(f"تم إضافة المستخدم {user_id} كمتابع للمطور {developer_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إضافة متابع للمطور {developer_id}: {e}")
            return False
    
    def remove_follower(self, developer_id: int, user_id: int) -> bool:
        """إزالة متابع من المطور"""
        try:
            success = db_manager.remove_developer_follower(developer_id, user_id)
            
            if success:
                # تحديث في الذاكرة
                if developer_id in self.developer_followers:
                    if user_id in self.developer_followers[developer_id]:
                        self.developer_followers[developer_id].remove(user_id)
                
                logger.info(f"تم إزالة المستخدم {user_id} من متابعي المطور {developer_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إزالة متابع من المطور {developer_id}: {e}")
            return False
    
    def get_followers(self, developer_id: int) -> List[int]:
        """الحصول على قائمة متابعي المطور"""
        return self.developer_followers.get(developer_id, [])
    
    def get_follower_count(self, developer_id: int) -> int:
        """الحصول على عدد متابعي المطور"""
        return len(self.get_followers(developer_id))
    
    def is_following(self, developer_id: int, user_id: int) -> bool:
        """التحقق من أن المستخدم يتابع المطور"""
        followers = self.get_followers(developer_id)
        return user_id in followers
    
    def broadcast_signal_to_followers(self, developer_id: int, signal_data: Dict) -> Dict[str, Any]:
        """بث إشارة من المطور لجميع متابعيه"""
        try:
            # التحقق من صلاحية البث
            if not self.can_broadcast_signals(developer_id):
                return {
                    'success': False,
                    'message': 'ليس لديك صلاحية لإرسال إشارات',
                    'sent_to': []
                }
            
            # الحصول على المتابعين
            followers = self.get_followers(developer_id)
            
            if not followers:
                return {
                    'success': False,
                    'message': 'لا يوجد متابعين لإرسال الإشارة إليهم',
                    'sent_to': []
                }
            
            # حفظ الإشارة في قاعدة البيانات
            signal_id = db_manager.create_developer_signal(
                developer_id=developer_id,
                signal_data=signal_data,
                target_followers=followers
            )
            
            if signal_id:
                logger.info(f"تم بث إشارة من المطور {developer_id} إلى {len(followers)} متابع")
                return {
                    'success': True,
                    'message': f'تم إرسال الإشارة إلى {len(followers)} متابع',
                    'signal_id': signal_id,
                    'sent_to': followers,
                    'follower_count': len(followers)
                }
            
            return {
                'success': False,
                'message': 'فشل في حفظ الإشارة',
                'sent_to': []
            }
            
        except Exception as e:
            logger.error(f"خطأ في بث إشارة من المطور {developer_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ: {str(e)}',
                'sent_to': []
            }
    
    def get_developer_statistics(self, developer_id: int) -> Dict:
        """الحصول على إحصائيات المطور"""
        try:
            return {
                'developer_id': developer_id,
                'follower_count': self.get_follower_count(developer_id),
                'is_active': self.is_developer_active(developer_id),
                'can_broadcast': self.can_broadcast_signals(developer_id),
                'total_signals': db_manager.get_developer_signal_count(developer_id)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات المطور {developer_id}: {e}")
            return {}
    
    def get_all_active_developers(self) -> List[Dict]:
        """الحصول على جميع المطورين النشطين"""
        return [dev_data for dev_id, dev_data in self.developers.items() 
                if dev_data.get('is_active', False)]
    
    def validate_developer_key(self, developer_id: int, developer_key: str) -> bool:
        """التحقق من صحة مفتاح المطور"""
        dev_data = self.get_developer(developer_id)
        if not dev_data:
            return False
        
        stored_key = dev_data.get('developer_key')
        return stored_key and stored_key == developer_key
    
    def get_developer_webhook_url(self, developer_id: int) -> Optional[str]:
        """الحصول على رابط webhook الخاص بالمطور"""
        dev_data = self.get_developer(developer_id)
        if dev_data:
            return dev_data.get('webhook_url')
        return None

# إنشاء مثيل عام لمدير المطورين
developer_manager = DeveloperManager()

