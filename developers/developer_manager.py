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
    
    # دوال إدارة المستخدمين (للمطورين فقط)
    def delete_user_data(self, developer_id: int, user_id: int) -> Dict[str, Any]:
        """حذف بيانات مستخدم محدد (للمطورين فقط)"""
        try:
            # التحقق من صلاحية المطور
            if not self.is_developer(developer_id):
                return {
                    'success': False,
                    'message': 'ليس لديك صلاحيات مطور'
                }
            
            if not self.is_developer_active(developer_id):
                return {
                    'success': False,
                    'message': 'حساب المطور غير نشط'
                }
            
            # حذف المستخدم من قاعدة البيانات
            success = db_manager.delete_user(user_id)
            
            if success:
                # إزالة من ذاكرة user_manager
                from users.user_manager import user_manager
                user_manager.remove_user_from_cache(user_id)
                
                logger.info(f"🗑️ المطور {developer_id} حذف المستخدم {user_id}")
                return {
                    'success': True,
                    'message': f'تم حذف المستخدم {user_id} وجميع بياناته بنجاح'
                }
            else:
                return {
                    'success': False,
                    'message': f'فشل حذف المستخدم {user_id} أو أنه غير موجود'
                }
            
        except Exception as e:
            logger.error(f"❌ خطأ في حذف المستخدم {user_id} بواسطة المطور {developer_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ: {str(e)}'
            }
    
    def get_user_count(self, developer_id: int) -> int:
        """الحصول على عدد المستخدمين (للمطورين فقط)"""
        try:
            # التحقق من صلاحية المطور
            if not self.is_developer(developer_id):
                return 0
            
            all_users = db_manager.get_all_active_users()
            return len(all_users)
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على عدد المستخدمين: {e}")
            return 0
    
    def list_all_users(self, developer_id: int) -> List[Dict]:
        """الحصول على قائمة جميع المستخدمين (للمطورين فقط)"""
        try:
            # التحقق من صلاحية المطور
            if not self.is_developer(developer_id):
                return []
            
            if not self.is_developer_active(developer_id):
                return []
            
            all_users = db_manager.get_all_active_users()
            
            # إرجاع معلومات مختصرة لكل مستخدم
            users_list = []
            for user in all_users:
                users_list.append({
                    'user_id': user.get('user_id'),
                    'balance': user.get('balance', 0),
                    'account_type': user.get('account_type', 'demo'),
                    'market_type': user.get('market_type', 'spot'),
                    'is_active': user.get('is_active', False),
                    'created_at': user.get('created_at', ''),
                    'total_loss': user.get('total_loss', 0)
                })
            
            return users_list
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على قائمة المستخدمين: {e}")
            return []
    
    def reset_all_users_data(self, developer_id: int) -> Dict[str, Any]:
        """إعادة تعيين بيانات جميع المستخدمين وحذف الذاكرة (للمطورين فقط)"""
        try:
            # التحقق من صلاحية المطور
            if not self.is_developer(developer_id):
                return {
                    'success': False,
                    'message': 'ليس لديك صلاحيات مطور'
                }
            
            if not self.is_developer_active(developer_id):
                return {
                    'success': False,
                    'message': 'حساب المطور غير نشط'
                }
            
            # إنشاء ملف إعادة التعيين الإجباري
            import os
            reset_file = "FORCE_RESET.flag"
            try:
                with open(reset_file, 'w') as f:
                    f.write(f"FORCE_RESET_DATABASE_ON_STARTUP\nCreated by developer {developer_id} at {datetime.now()}")
                logger.warning(f"🔥 تم إنشاء ملف إعادة التعيين الإجباري: {reset_file}")
            except Exception as e:
                logger.error(f"❌ فشل إنشاء ملف إعادة التعيين: {e}")
            
            try:
                # حذف جميع البيانات من الذاكرة (cache) أولاً
                from users.user_manager import user_manager
                
                # حذف جميع المستخدمين من الذاكرة
                user_manager.users.clear()
                user_manager.user_accounts.clear()
                user_manager.user_apis.clear()
                user_manager.user_positions.clear()
                
                logger.info("🗑️ تم حذف جميع البيانات من الذاكرة")
                
                # حذف جميع الحسابات الحقيقية من real_account_manager
                try:
                    from api.bybit_api import real_account_manager
                    real_account_manager.accounts.clear()
                    logger.info("🗑️ تم حذف جميع الحسابات الحقيقية من real_account_manager")
                except Exception as e:
                    logger.warning(f"⚠️ لم يتم حذف الحسابات الحقيقية: {e}")
                
                # إعادة تعيين بيانات جميع المستخدمين في قاعدة البيانات (حذف ملف قواعد البيانات بالكامل!)
                user_count = db_manager.reset_all_users_data()
                
                if user_count > 0:
                    # إعادة تحميل بيانات المستخدمين من قاعدة البيانات الجديدة
                    user_manager.load_all_users()
                    
                    logger.warning(f"🔄 المطور {developer_id} أعاد تعيين المشروع بالكامل ({user_count} مستخدم)")
                    return {
                        'success': True,
                        'message': f'تم إعادة تعيين المشروع بالكامل\n• {user_count} مستخدم\n• حذف ملف قاعدة البيانات\n• حذف الذاكرة\n• إعادة الإعدادات للافتراضي',
                        'user_count': user_count
                    }
                else:
                    return {
                        'success': False,
                        'message': 'لا يوجد مستخدمين لإعادة التعيين'
                    }
                
            except Exception as e:
                logger.error(f"❌ خطأ في إعادة تعيين بيانات جميع المستخدمين: {e}")
                return {
                    'success': False,
                    'message': f'خطأ: {str(e)}'
                }
        except Exception as e:
            logger.error(f"❌ خطأ في reset_all_users_data: {e}")
            return {
                'success': False,
                'message': f'خطأ: {str(e)}'
            }

# إنشاء مثيل عام لمدير المطورين
developer_manager = DeveloperManager()

