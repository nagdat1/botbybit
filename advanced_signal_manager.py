#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الإشارات المتقدم - Advanced Signal Manager
يدعم نظام ID للإشارات وربط الإشارات بنفس ID
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AdvancedSignalManager:
    """مدير الإشارات المتقدم مع نظام ID"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # قاعدة بيانات الإشارات
        self.signals_db: Dict[str, Dict[str, Any]] = {}
        
        # قاعدة بيانات الصفقات المرتبطة
        self.position_signals_map: Dict[str, str] = {}  # position_id -> signal_id
        self.signal_positions_map: Dict[str, List[str]] = {}  # signal_id -> [position_ids]
        
        # قاعدة بيانات المستخدمين
        self.user_signals: Dict[int, List[str]] = {}
        
        self.logger.info("🎯 تم تهيئة مدير الإشارات المتقدم")
    
    def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة الإشارة مع نظام ID"""
        try:
            # استخراج البيانات الأساسية
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            
            # التحقق من صحة البيانات
            if not signal_type or not symbol:
                return {
                    'success': False,
                    'message': 'بيانات الإشارة غير مكتملة',
                    'error': 'incomplete_signal_data'
                }
            
            # معالجة ID الإشارة
            processed_signal_id = self._process_signal_id(signal_id, symbol, signal_type)
            
            # إنشاء سجل الإشارة
            signal_record = self._create_signal_record(
                signal_id=processed_signal_id,
                signal_type=signal_type,
                symbol=symbol,
                user_id=user_id,
                original_data=signal_data
            )
            
            # حفظ الإشارة
            self.signals_db[processed_signal_id] = signal_record
            
            # ربط الإشارة بالمستخدم
            if user_id not in self.user_signals:
                self.user_signals[user_id] = []
            self.user_signals[user_id].append(processed_signal_id)
            
            self.logger.info(f"✅ تم معالجة الإشارة: {processed_signal_id} للمستخدم {user_id}")
            
            return {
                'success': True,
                'message': 'تم معالجة الإشارة بنجاح',
                'signal_id': processed_signal_id,
                'signal_type': signal_type,
                'symbol': symbol,
                'user_id': user_id,
                'timestamp': signal_record['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': str(e)
            }
    
    def _process_signal_id(self, signal_id: Optional[str], symbol: str, signal_type: str) -> str:
        """معالجة ID الإشارة"""
        if signal_id:
            # استخدام ID المرسل
            processed_id = signal_id
            self.logger.info(f"🆔 استخدام ID مرسل: {processed_id}")
        else:
            # توليد ID عشوائي
            processed_id = f"{symbol}_{signal_type}_{uuid.uuid4().hex[:8].upper()}"
            self.logger.info(f"🎲 توليد ID عشوائي: {processed_id}")
        
        return processed_id
    
    def _create_signal_record(self, signal_id: str, signal_type: str, symbol: str, 
                            user_id: int, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء سجل الإشارة"""
        return {
            'signal_id': signal_id,
            'signal_type': signal_type,
            'symbol': symbol,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'original_data': original_data,
            'positions': [],  # قائمة الصفقات المرتبطة
            'execution_count': 0,
            'last_execution': None
        }
    
    def link_signal_to_position(self, signal_id: str, position_id: str) -> bool:
        """ربط إشارة بصفقة"""
        try:
            if signal_id not in self.signals_db:
                self.logger.warning(f"⚠️ الإشارة غير موجودة: {signal_id}")
                return False
            
            # ربط الصفقة بالإشارة
            self.position_signals_map[position_id] = signal_id
            
            # إضافة الصفقة لقائمة إشارة
            if signal_id not in self.signal_positions_map:
                self.signal_positions_map[signal_id] = []
            
            if position_id not in self.signal_positions_map[signal_id]:
                self.signal_positions_map[signal_id].append(position_id)
            
            # تحديث سجل الإشارة
            self.signals_db[signal_id]['positions'].append(position_id)
            self.signals_db[signal_id]['execution_count'] += 1
            self.signals_db[signal_id]['last_execution'] = datetime.now().isoformat()
            
            self.logger.info(f"🔗 تم ربط الإشارة {signal_id} بالصفقة {position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في ربط الإشارة بالصفقة: {e}")
            return False
    
    def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على إشارة بواسطة ID"""
        return self.signals_db.get(signal_id)
    
    def get_positions_by_signal_id(self, signal_id: str) -> List[str]:
        """الحصول على الصفقات المرتبطة بإشارة"""
        return self.signal_positions_map.get(signal_id, [])
    
    def get_signal_by_position_id(self, position_id: str) -> Optional[str]:
        """الحصول على إشارة مرتبطة بصفقة"""
        return self.position_signals_map.get(position_id)
    
    def get_user_signals(self, user_id: int) -> List[Dict[str, Any]]:
        """الحصول على إشارات المستخدم"""
        user_signal_ids = self.user_signals.get(user_id, [])
        return [self.signals_db.get(signal_id) for signal_id in user_signal_ids 
                if self.signals_db.get(signal_id)]
    
    def get_signal_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """الحصول على إحصائيات الإشارات"""
        if user_id:
            signals = self.get_user_signals(user_id)
        else:
            signals = list(self.signals_db.values())
        
        if not signals:
            return {
                'total_signals': 0,
                'signals_by_type': {},
                'signals_by_symbol': {},
                'execution_stats': {}
            }
        
        # إحصائيات حسب النوع
        signals_by_type = {}
        for signal in signals:
            signal_type = signal['signal_type']
            signals_by_type[signal_type] = signals_by_type.get(signal_type, 0) + 1
        
        # إحصائيات حسب الرمز
        signals_by_symbol = {}
        for signal in signals:
            symbol = signal['symbol']
            signals_by_symbol[symbol] = signals_by_symbol.get(symbol, 0) + 1
        
        # إحصائيات التنفيذ
        execution_stats = {
            'total_executions': sum(signal['execution_count'] for signal in signals),
            'average_executions_per_signal': sum(signal['execution_count'] for signal in signals) / len(signals),
            'signals_with_positions': len([s for s in signals if s['positions']])
        }
        
        return {
            'total_signals': len(signals),
            'signals_by_type': signals_by_type,
            'signals_by_symbol': signals_by_symbol,
            'execution_stats': execution_stats,
            'user_id': user_id
        }
    
    def update_signal_status(self, signal_id: str, status: str) -> bool:
        """تحديث حالة الإشارة"""
        try:
            if signal_id in self.signals_db:
                self.signals_db[signal_id]['status'] = status
                self.logger.info(f"✅ تم تحديث حالة الإشارة {signal_id} إلى {status}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث حالة الإشارة: {e}")
            return False
    
    def close_signal_positions(self, signal_id: str) -> Dict[str, Any]:
        """إغلاق جميع الصفقات المرتبطة بإشارة"""
        try:
            positions = self.get_positions_by_signal_id(signal_id)
            
            if not positions:
                return {
                    'success': False,
                    'message': 'لا توجد صفقات مرتبطة بهذه الإشارة',
                    'positions_closed': 0
                }
            
            # تحديث حالة الإشارة
            self.update_signal_status(signal_id, 'closed')
            
            self.logger.info(f"🔒 تم إغلاق {len(positions)} صفقة للإشارة {signal_id}")
            
            return {
                'success': True,
                'message': f'تم إغلاق {len(positions)} صفقة',
                'positions_closed': len(positions),
                'positions': positions
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إغلاق صفقات الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في إغلاق الصفقات: {str(e)}',
                'error': str(e)
            }


# مثيل عام لمدير الإشارات المتقدم
advanced_signal_manager = AdvancedSignalManager()


# دوال مساعدة للاستخدام السريع
def process_signal(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة الإشارة"""
    return advanced_signal_manager.process_signal(signal_data, user_id)


def link_signal_to_position(signal_id: str, position_id: str) -> bool:
    """ربط إشارة بصفقة"""
    return advanced_signal_manager.link_signal_to_position(signal_id, position_id)


def get_signal_statistics(user_id: Optional[int] = None) -> Dict[str, Any]:
    """الحصول على إحصائيات الإشارات"""
    return advanced_signal_manager.get_signal_statistics(user_id)


if __name__ == "__main__":
    # اختبار مدير الإشارات المتقدم
    print("=" * 80)
    print("اختبار مدير الإشارات المتقدم")
    print("=" * 80)
    
    # اختبار إشارة مع ID
    test_signal_with_id = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': 'TV_B01'
    }
    
    result1 = process_signal(test_signal_with_id, 12345)
    print(f"\n🧪 اختبار إشارة مع ID: {result1['success']}")
    if result1['success']:
        print(f"   ID الإشارة: {result1['signal_id']}")
    
    # اختبار إشارة بدون ID
    test_signal_without_id = {
        'signal': 'sell',
        'symbol': 'ETHUSDT'
    }
    
    result2 = process_signal(test_signal_without_id, 12345)
    print(f"\n🧪 اختبار إشارة بدون ID: {result2['success']}")
    if result2['success']:
        print(f"   ID الإشارة: {result2['signal_id']}")
    
    # اختبار ربط إشارة بصفقة
    if result1['success']:
        link_result = link_signal_to_position(result1['signal_id'], 'POS_001')
        print(f"\n🔗 اختبار ربط الإشارة بالصفقة: {link_result}")
    
    # اختبار الإحصائيات
    stats = get_signal_statistics(12345)
    print(f"\n📊 الإحصائيات: {stats}")
