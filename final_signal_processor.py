#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الإشارات النهائي - Final Signal Processor
يطبق جميع القواعد المطلوبة ومعالجة الإشارات حسب النوع
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class FinalSignalProcessor:
    """معالج الإشارات النهائي مع تطبيق جميع القواعد"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # إعدادات المعالج
        self.supported_signals = ['buy', 'sell', 'close', 'partial_close', 'long', 'short', 'close_long', 'close_short']
        self.supported_accounts = ['demo', 'real']
        self.supported_markets = ['spot', 'futures']
        self.supported_exchanges = ['bybit', 'mexc']
        
        self.logger.info("🎯 تم تهيئة معالج الإشارات النهائي")
    
    def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة الإشارة النهائية مع تطبيق جميع القواعد"""
        try:
            # التحقق من صحة الإشارة
            validation_result = self._validate_signal(signal_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message'],
                    'error': 'invalid_signal'
                }
            
            # استخراج البيانات
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            
            # تحديد نوع المعالجة
            processing_type = self._determine_processing_type(signal_type)
            
            # معالجة الإشارة حسب النوع
            if processing_type == 'open_position':
                result = self._process_open_position_signal(signal_data, user_id)
            elif processing_type == 'close_position':
                result = self._process_close_position_signal(signal_data, user_id)
            elif processing_type == 'partial_close':
                result = self._process_partial_close_signal(signal_data, user_id)
            else:
                return {
                    'success': False,
                    'message': f'نوع الإشارة غير مدعوم: {signal_type}',
                    'error': 'unsupported_signal_type'
                }
            
            # إضافة معلومات إضافية
            if result['success']:
                result.update({
                    'signal_id': signal_id,
                    'processing_type': processing_type,
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id
                })
            
            self.logger.info(f"✅ تم معالجة الإشارة النهائية: {signal_type} {symbol}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة النهائية: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': str(e)
            }
    
    def _validate_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة الإشارة"""
        try:
            # التحقق من وجود البيانات الأساسية
            if 'signal' not in signal_data:
                return {'valid': False, 'message': 'نوع الإشارة مطلوب'}
            
            if 'symbol' not in signal_data:
                return {'valid': False, 'message': 'رمز العملة مطلوب'}
            
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            
            # التحقق من نوع الإشارة
            if signal_type not in self.supported_signals:
                return {
                    'valid': False, 
                    'message': f'نوع الإشارة غير مدعوم: {signal_type}'
                }
            
            # التحقق من صحة الرمز
            if not symbol or len(symbol) < 6:
                return {'valid': False, 'message': 'رمز العملة غير صحيح'}
            
            # التحقق من ID الإشارة (اختياري)
            signal_id = signal_data.get('id')
            if signal_id and len(signal_id) < 3:
                return {'valid': False, 'message': 'ID الإشارة قصير جداً'}
            
            return {'valid': True, 'message': 'الإشارة صحيحة'}
            
        except Exception as e:
            return {'valid': False, 'message': f'خطأ في التحقق من الإشارة: {str(e)}'}
    
    def _determine_processing_type(self, signal_type: str) -> str:
        """تحديد نوع المعالجة"""
        if signal_type in ['buy', 'sell', 'long', 'short']:
            return 'open_position'
        elif signal_type in ['close', 'close_long', 'close_short']:
            return 'close_position'
        elif signal_type == 'partial_close':
            return 'partial_close'
        else:
            return 'unknown'
    
    def _process_open_position_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة إشارة فتح صفقة"""
        try:
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            
            # تحديد الجانب
            if signal_type in ['buy', 'long']:
                side = 'buy'
            else:
                side = 'sell'
            
            # إنشاء بيانات الصفقة
            position_data = {
                'signal_type': signal_type,
                'side': side,
                'symbol': symbol,
                'signal_id': signal_id,
                'user_id': user_id,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"📈 معالجة إشارة فتح صفقة: {side} {symbol}")
            
            return {
                'success': True,
                'message': f'تم معالجة إشارة فتح صفقة: {side} {symbol}',
                'action': 'open_position',
                'position_data': position_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة إشارة فتح الصفقة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة فتح الصفقة: {str(e)}',
                'error': str(e)
            }
    
    def _process_close_position_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة إشارة إغلاق صفقة"""
        try:
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            
            # تحديد نوع الإغلاق
            if signal_type in ['close_long']:
                close_type = 'close_long'
            elif signal_type in ['close_short']:
                close_type = 'close_short'
            else:
                close_type = 'close_all'
            
            # إنشاء بيانات الإغلاق
            close_data = {
                'signal_type': signal_type,
                'close_type': close_type,
                'symbol': symbol,
                'signal_id': signal_id,
                'user_id': user_id,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"📉 معالجة إشارة إغلاق صفقة: {close_type} {symbol}")
            
            return {
                'success': True,
                'message': f'تم معالجة إشارة إغلاق صفقة: {close_type} {symbol}',
                'action': 'close_position',
                'close_data': close_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة إشارة إغلاق الصفقة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة إغلاق الصفقة: {str(e)}',
                'error': str(e)
            }
    
    def _process_partial_close_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """معالجة إشارة الإغلاق الجزئي"""
        try:
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            percentage = signal_data.get('percentage', 50)  # افتراضي 50%
            
            # التحقق من النسبة
            if not isinstance(percentage, (int, float)) or percentage <= 0 or percentage > 100:
                return {
                    'success': False,
                    'message': 'نسبة الإغلاق الجزئي غير صحيحة (يجب أن تكون بين 1-100)',
                    'error': 'invalid_percentage'
                }
            
            # إنشاء بيانات الإغلاق الجزئي
            partial_close_data = {
                'signal_type': signal_type,
                'symbol': symbol,
                'signal_id': signal_id,
                'percentage': percentage,
                'user_id': user_id,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"📊 معالجة إشارة إغلاق جزئي: {percentage}% {symbol}")
            
            return {
                'success': True,
                'message': f'تم معالجة إشارة إغلاق جزئي: {percentage}% {symbol}',
                'action': 'partial_close',
                'partial_close_data': partial_close_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة إشارة الإغلاق الجزئي: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة الإغلاق الجزئي: {str(e)}',
                'error': str(e)
            }
    
    def apply_user_settings(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تطبيق إعدادات المستخدم على الإشارة"""
        try:
            # نسخ البيانات الأصلية
            processed_signal = signal_data.copy()
            
            # تطبيق الإعدادات
            processed_signal.update({
                'account_type': user_settings.get('account_type', 'demo'),
                'market_type': user_settings.get('market_type', 'spot'),
                'exchange': user_settings.get('exchange', 'bybit'),
                'trade_amount': user_settings.get('trade_amount', 100.0),
                'leverage': user_settings.get('leverage', 1),
                'link_by_id': user_settings.get('link_by_id', True)
            })
            
            self.logger.info("⚙️ تم تطبيق إعدادات المستخدم على الإشارة")
            
            return {
                'success': True,
                'message': 'تم تطبيق إعدادات المستخدم بنجاح',
                'processed_signal': processed_signal
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تطبيق إعدادات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في تطبيق إعدادات المستخدم: {str(e)}',
                'error': str(e)
            }
    
    def get_processing_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """الحصول على إحصائيات المعالجة"""
        # هذه الدالة يمكن توسيعها لتتبع الإحصائيات الفعلية
        return {
            'supported_signals': self.supported_signals,
            'supported_accounts': self.supported_accounts,
            'supported_markets': self.supported_markets,
            'supported_exchanges': self.supported_exchanges,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }


# مثيل عام لمعالج الإشارات النهائي
final_signal_processor = FinalSignalProcessor()


# دوال مساعدة للاستخدام السريع
def process_signal(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة الإشارة"""
    return final_signal_processor.process_signal(signal_data, user_id)


def apply_user_settings(signal_data: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
    """تطبيق إعدادات المستخدم"""
    return final_signal_processor.apply_user_settings(signal_data, user_settings)


if __name__ == "__main__":
    # اختبار معالج الإشارات النهائي
    print("=" * 80)
    print("اختبار معالج الإشارات النهائي")
    print("=" * 80)
    
    # اختبار إشارة شراء مع ID
    test_signal_buy = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': 'TV_B01'
    }
    
    result1 = process_signal(test_signal_buy, 12345)
    print(f"\n🧪 اختبار إشارة شراء مع ID: {result1['success']}")
    if result1['success']:
        print(f"   الإجراء: {result1['action']}")
        print(f"   ID الإشارة: {result1['signal_id']}")
    
    # اختبار إشارة إغلاق
    test_signal_close = {
        'signal': 'close',
        'symbol': 'BTCUSDT',
        'id': 'TV_C01'
    }
    
    result2 = process_signal(test_signal_close, 12345)
    print(f"\n🧪 اختبار إشارة إغلاق: {result2['success']}")
    if result2['success']:
        print(f"   الإجراء: {result2['action']}")
        print(f"   نوع الإغلاق: {result2['close_data']['close_type']}")
    
    # اختبار إشارة إغلاق جزئي
    test_signal_partial = {
        'signal': 'partial_close',
        'symbol': 'ETHUSDT',
        'id': 'TV_PC01',
        'percentage': 75
    }
    
    result3 = process_signal(test_signal_partial, 12345)
    print(f"\n🧪 اختبار إشارة إغلاق جزئي: {result3['success']}")
    if result3['success']:
        print(f"   الإجراء: {result3['action']}")
        print(f"   النسبة: {result3['partial_close_data']['percentage']}%")
    
    # اختبار إشارة غير صحيحة
    test_signal_invalid = {
        'signal': 'invalid_signal',
        'symbol': 'BTCUSDT'
    }
    
    result4 = process_signal(test_signal_invalid, 12345)
    print(f"\n🧪 اختبار إشارة غير صحيحة: {result4['success']}")
    if not result4['success']:
        print(f"   الخطأ: {result4['message']}")
    
    # اختبار الإحصائيات
    stats = final_signal_processor.get_processing_statistics(12345)
    print(f"\n📊 الإحصائيات: {stats}")
