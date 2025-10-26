#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير معرفات الإشارات - ربط ID الإشارة برقم الصفقة
"""

import uuid
import random
import string
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SignalIDManager:
    """مدير معرفات الإشارات وربطها برقم الصفقة"""
    
    def __init__(self):
        self.signal_to_position_map: Dict[str, str] = {}
        self.position_to_signal_map: Dict[str, str] = {}
        
    def generate_random_id(self, symbol: str = "UNKNOWN") -> str:
        """توليد ID عشوائي للإشارة"""
        try:
            # الصيغة: SYMBOL-YYYYMMDD-HHMMSS-RAND4
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            signal_id = f"{symbol}-{date_str}-{time_str}-{random_suffix}"
            logger.info(f"🆔 تم توليد ID عشوائي: {signal_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"خطأ في توليد ID عشوائي: {e}")
            # استخدام UUID كبديل
            return f"{symbol}-{str(uuid.uuid4())[:8].upper()}"
    
    def generate_position_id(self, signal_id: str) -> str:
        """توليد رقم صفقة مرتبط بـ ID الإشارة"""
        try:
            # الصيغة: POS-SIGNAL_ID
            position_id = f"POS-{signal_id}"
            logger.info(f"📍 تم توليد رقم صفقة: {position_id} للإشارة: {signal_id}")
            return position_id
            
        except Exception as e:
            logger.error(f"خطأ في توليد رقم صفقة: {e}")
            return f"POS-{str(uuid.uuid4())[:8].upper()}"
    
    def link_signal_to_position(self, signal_id: str, position_id: str) -> bool:
        """ربط ID الإشارة برقم الصفقة"""
        try:
            self.signal_to_position_map[signal_id] = position_id
            self.position_to_signal_map[position_id] = signal_id
            logger.info(f"🔗 تم ربط الإشارة {signal_id} بالصفقة {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في ربط الإشارة بالصفقة: {e}")
            return False
    
    def get_position_id_from_signal(self, signal_id: str) -> Optional[str]:
        """الحصول على رقم الصفقة من ID الإشارة"""
        try:
            position_id = self.signal_to_position_map.get(signal_id)
            if position_id:
                logger.info(f"📍 تم العثور على رقم الصفقة {position_id} للإشارة {signal_id}")
            else:
                logger.warning(f"⚠️ لم يتم العثور على رقم صفقة للإشارة {signal_id}")
            return position_id
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على رقم الصفقة: {e}")
            return None
    
    def get_signal_id_from_position(self, position_id: str) -> Optional[str]:
        """الحصول على ID الإشارة من رقم الصفقة"""
        try:
            signal_id = self.position_to_signal_map.get(position_id)
            if signal_id:
                logger.info(f"🆔 تم العثور على ID الإشارة {signal_id} للصفقة {position_id}")
            else:
                logger.warning(f"⚠️ لم يتم العثور على ID إشارة للصفقة {position_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ID الإشارة: {e}")
            return None
    
    def process_signal_id(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة ID الإشارة وإضافة رقم الصفقة"""
        try:
            signal_id = signal_data.get('id')
            symbol = signal_data.get('symbol', 'UNKNOWN')
            
            # إذا لم يتم اختيار ID، قم بتوليد ID عشوائي
            if not signal_id:
                signal_id = self.generate_random_id(symbol)
                signal_data['id'] = signal_id
                signal_data['generated_id'] = True
                logger.info(f"🆔 تم توليد ID عشوائي للإشارة: {signal_id}")
            else:
                signal_data['generated_id'] = False
                logger.info(f"🆔 تم استخدام ID محدد للإشارة: {signal_id}")
            
            # توليد رقم الصفقة المرتبط بـ ID الإشارة
            position_id = self.generate_position_id(signal_id)
            signal_data['position_id'] = position_id
            
            # ربط ID الإشارة برقم الصفقة
            self.link_signal_to_position(signal_id, position_id)
            
            logger.info(f"✅ تم معالجة ID الإشارة: {signal_id} -> رقم الصفقة: {position_id}")
            return signal_data
            
        except Exception as e:
            logger.error(f"خطأ في معالجة ID الإشارة: {e}")
            # في حالة الخطأ، استخدم ID افتراضي
            signal_data['id'] = self.generate_random_id(signal_data.get('symbol', 'UNKNOWN'))
            signal_data['position_id'] = self.generate_position_id(signal_data['id'])
            return signal_data
    
    def get_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """الحصول على جميع الربط بين الإشارات والصفقات"""
        return {
            'signal_to_position': self.signal_to_position_map.copy(),
            'position_to_signal': self.position_to_signal_map.copy()
        }
    
    def clear_mappings(self):
        """مسح جميع الربط بين الإشارات والصفقات"""
        self.signal_to_position_map.clear()
        self.position_to_signal_map.clear()
        logger.info("🧹 تم مسح جميع الربط بين الإشارات والصفقات")

# إنشاء مثيل عام لمدير معرفات الإشارات
signal_id_manager = SignalIDManager()

def get_signal_id_manager() -> SignalIDManager:
    """الحصول على مثيل مدير معرفات الإشارات"""
    return signal_id_manager

def process_signal_id(signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """دالة مساعدة لمعالجة ID الإشارة"""
    return signal_id_manager.process_signal_id(signal_data)

def generate_random_signal_id(symbol: str = "UNKNOWN") -> str:
    """دالة مساعدة لتوليد ID عشوائي للإشارة"""
    return signal_id_manager.generate_random_id(symbol)

def link_signal_to_position(signal_id: str, position_id: str) -> bool:
    """دالة مساعدة لربط ID الإشارة برقم الصفقة"""
    return signal_id_manager.link_signal_to_position(signal_id, position_id)

def get_position_id_from_signal(signal_id: str) -> Optional[str]:
    """دالة مساعدة للحصول على رقم الصفقة من ID الإشارة"""
    return signal_id_manager.get_position_id_from_signal(signal_id)

def get_signal_id_from_position(position_id: str) -> Optional[str]:
    """دالة مساعدة للحصول على ID الإشارة من رقم الصفقة"""
    return signal_id_manager.get_signal_id_from_position(position_id)
