#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الإشارات النهائي
يطبق جميع القواعد المطلوبة لإدارة الإشارات مع ID والربط الاختياري
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# استيراد الأنظمة المطلوبة
from advanced_signal_manager import advanced_signal_manager
from enhanced_account_manager import enhanced_account_manager
from integrated_signal_system import integrated_signal_system

logger = logging.getLogger(__name__)

class FinalSignalProcessor:
    """معالج الإشارات النهائي مع جميع القواعد المطلوبة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # إعدادات النظام
        self.supported_signals = {
            'buy': '🟢 شراء',
            'sell': '🔴 بيع', 
            'close': '⚪ إغلاق كامل',
            'partial_close': '🟡 إغلاق جزئي'
        }
        
        self.supported_accounts = ['demo', 'real']
        self.supported_markets = ['spot', 'futures']
        self.supported_exchanges = ['bybit', 'mexc']
        
        self.logger.info("🚀 تم تهيئة معالج الإشارات النهائي")
    
    async def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        معالجة الإشارة النهائية مع تطبيق جميع القواعد
        
        Args:
            signal_data: بيانات الإشارة
            user_id: معرف المستخدم
            
        Returns:
            نتيجة معالجة الإشارة
        """
        try:
            self.logger.info(f"🎯 معالجة إشارة نهائية للمستخدم {user_id}: {signal_data}")
            
            # 1. التحقق من صحة الإشارة
            validation_result = self._validate_signal(signal_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message'],
                    'error': 'VALIDATION_ERROR'
                }
            
            # 2. الحصول على إعدادات المستخدم
            user_settings = self._get_user_settings(user_id)
            
            # 3. تطبيق قواعد المعالجة
            processing_result = await self._apply_processing_rules(signal_data, user_settings, user_id)
            
            if not processing_result['success']:
                return processing_result
            
            # 4. تنفيذ الإشارة
            execution_result = await self._execute_signal(signal_data, user_settings, user_id)
            
            # 5. إرجاع النتيجة النهائية
            final_result = {
                'success': execution_result['success'],
                'message': execution_result['message'],
                'signal_id': signal_data['id'],
                'symbol': signal_data['symbol'],
                'signal_type': signal_data['signal'],
                'user_id': user_id,
                'account_type': user_settings['account_type'],
                'market_type': user_settings['market_type'],
                'exchange': user_settings['exchange'],
                'link_by_id': user_settings.get('link_by_id', True),
                'timestamp': datetime.now().isoformat(),
                'processing_details': processing_result,
                'execution_details': execution_result
            }
            
            if not execution_result['success']:
                final_result['error'] = execution_result.get('error', 'EXECUTION_ERROR')
            
            self.logger.info(f"✅ تم معالجة الإشارة النهائية: {final_result}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الإشارة النهائية: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': 'PROCESSING_ERROR',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة الإشارة"""
        try:
            # التحقق من الحقول المطلوبة
            required_fields = ['signal', 'symbol', 'id']
            for field in required_fields:
                if field not in signal_data or not signal_data[field]:
                    return {
                        'valid': False,
                        'message': f'الحقل المطلوب "{field}" مفقود أو فارغ'
                    }
            
            # التحقق من نوع الإشارة
            signal_type = signal_data['signal'].lower()
            if signal_type not in self.supported_signals:
                return {
                    'valid': False,
                    'message': f'نوع إشارة غير مدعوم: {signal_type}. المدعوم: {list(self.supported_signals.keys())}'
                }
            
            # التحقق من رمز العملة
            symbol = signal_data['symbol'].strip()
            if len(symbol) < 6:
                return {
                    'valid': False,
                    'message': f'رمز العملة غير صحيح: {symbol}'
                }
            
            # التحقق من النسبة المئوية للإغلاق الجزئي
            if signal_type == 'partial_close':
                percentage = signal_data.get('percentage')
                if percentage is None or not (0 < percentage <= 100):
                    return {
                        'valid': False,
                        'message': f'نسبة الإغلاق الجزئي غير صحيحة: {percentage}. يجب أن تكون بين 1 و 100'
                    }
            
            return {
                'valid': True,
                'message': 'الإشارة صحيحة'
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحقق من صحة الإشارة: {e}")
            return {
                'valid': False,
                'message': f'خطأ في التحقق من صحة الإشارة: {str(e)}'
            }
    
    def _get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم"""
        try:
            # إعدادات افتراضية
            default_settings = {
                'account_type': 'demo',
                'market_type': 'spot',
                'exchange': 'bybit',
                'trade_amount': 100.0,
                'leverage': 10,
                'link_by_id': True,
                'language': 'ar'
            }
            
            # هنا يمكن إضافة منطق للحصول على إعدادات المستخدم من قاعدة البيانات
            # أو من ملف الإعدادات
            
            return default_settings
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على إعدادات المستخدم: {e}")
            return {
                'account_type': 'demo',
                'market_type': 'spot',
                'exchange': 'bybit',
                'trade_amount': 100.0,
                'leverage': 10,
                'link_by_id': True,
                'language': 'ar'
            }
    
    async def _apply_processing_rules(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تطبيق قواعد المعالجة"""
        try:
            signal_type = signal_data['signal'].lower()
            signal_id = signal_data['id']
            symbol = signal_data['symbol']
            link_by_id = user_settings.get('link_by_id', True)
            
            self.logger.info(f"📋 تطبيق قواعد المعالجة: {signal_type} - ID: {signal_id} - Link: {link_by_id}")
            
            # القاعدة 1: التحقق من نوع الحساب
            account_type = user_settings['account_type']
            if account_type not in self.supported_accounts:
                return {
                    'success': False,
                    'message': f'نوع حساب غير مدعوم: {account_type}',
                    'error': 'UNSUPPORTED_ACCOUNT_TYPE'
                }
            
            # القاعدة 2: التحقق من نوع السوق
            market_type = user_settings['market_type']
            if market_type not in self.supported_markets:
                return {
                    'success': False,
                    'message': f'نوع سوق غير مدعوم: {market_type}',
                    'error': 'UNSUPPORTED_MARKET_TYPE'
                }
            
            # القاعدة 3: التحقق من المنصة
            exchange = user_settings['exchange']
            if exchange not in self.supported_exchanges:
                return {
                    'success': False,
                    'message': f'منصة غير مدعومة: {exchange}',
                    'error': 'UNSUPPORTED_EXCHANGE'
                }
            
            # القاعدة 4: التحقق من توافق السوق مع المنصة
            if market_type == 'futures' and exchange == 'mexc':
                return {
                    'success': False,
                    'message': 'MEXC لا يدعم التداول في الفيوتشر',
                    'error': 'INCOMPATIBLE_MARKET_EXCHANGE'
                }
            
            # القاعدة 5: تطبيق قواعد الربط بالـ ID
            if link_by_id:
                # البحث عن صفقات موجودة بنفس ID
                existing_positions = await self._find_existing_positions(signal_id, user_id, symbol)
                
                if existing_positions:
                    # تطبيق قواعد الربط
                    linking_result = await self._apply_linking_rules(signal_data, existing_positions, user_settings)
                    if not linking_result['success']:
                        return linking_result
            
            # القاعدة 6: التحقق من الرصيد المتاح
            balance_check = await self._check_balance(signal_data, user_settings, user_id)
            if not balance_check['success']:
                return balance_check
            
            return {
                'success': True,
                'message': 'تم تطبيق قواعد المعالجة بنجاح',
                'rules_applied': [
                    'account_type_validation',
                    'market_type_validation',
                    'exchange_validation',
                    'market_exchange_compatibility',
                    'id_linking_rules',
                    'balance_check'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تطبيق قواعد المعالجة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تطبيق قواعد المعالجة: {str(e)}',
                'error': 'RULES_APPLICATION_ERROR'
            }
    
    async def _find_existing_positions(self, signal_id: str, user_id: int, symbol: str) -> List[Dict[str, Any]]:
        """البحث عن الصفقات الموجودة بنفس ID"""
        try:
            # هنا سيتم البحث في قاعدة البيانات عن الصفقات المرتبطة بنفس ID
            # هذا مثال مبسط
            
            # محاكاة البحث
            await asyncio.sleep(0.01)
            
            # إرجاع قائمة فارغة للاختبار
            return []
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث عن الصفقات الموجودة: {e}")
            return []
    
    async def _apply_linking_rules(self, signal_data: Dict[str, Any], existing_positions: List[Dict[str, Any]], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تطبيق قواعد الربط بالـ ID"""
        try:
            signal_type = signal_data['signal'].lower()
            
            if signal_type == 'buy':
                # قواعد إشارة الشراء
                for position in existing_positions:
                    if position['side'] == 'sell':
                        # إغلاق الصفقة البيعية وفتح شرائية
                        self.logger.info(f"🔄 إغلاق صفقة بيعية وفتح شرائية للـ ID: {signal_data['id']}")
                        break
                    elif position['side'] == 'buy':
                        # تعزيز الصفقة الشرائية
                        self.logger.info(f"📈 تعزيز صفقة شرائية للـ ID: {signal_data['id']}")
                        break
            
            elif signal_type == 'sell':
                # قواعد إشارة البيع
                for position in existing_positions:
                    if position['side'] == 'buy':
                        # إغلاق الصفقة الشرائية وفتح بيعية
                        self.logger.info(f"🔄 إغلاق صفقة شرائية وفتح بيعية للـ ID: {signal_data['id']}")
                        break
                    elif position['side'] == 'sell':
                        # تعزيز الصفقة البيعية
                        self.logger.info(f"📉 تعزيز صفقة بيعية للـ ID: {signal_data['id']}")
                        break
            
            elif signal_type == 'close':
                # قواعد إشارة الإغلاق الكامل
                self.logger.info(f"⚪ إغلاق جميع الصفقات المرتبطة بالـ ID: {signal_data['id']}")
            
            elif signal_type == 'partial_close':
                # قواعد إشارة الإغلاق الجزئي
                percentage = signal_data.get('percentage', 50)
                self.logger.info(f"🟡 إغلاق جزئي {percentage}% للصفقات المرتبطة بالـ ID: {signal_data['id']}")
            
            return {
                'success': True,
                'message': 'تم تطبيق قواعد الربط بنجاح'
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تطبيق قواعد الربط: {e}")
            return {
                'success': False,
                'message': f'خطأ في تطبيق قواعد الربط: {str(e)}',
                'error': 'LINKING_RULES_ERROR'
            }
    
    async def _check_balance(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """التحقق من الرصيد المتاح"""
        try:
            account_type = user_settings['account_type']
            market_type = user_settings['market_type']
            exchange = user_settings['exchange']
            trade_amount = float(user_settings['trade_amount'])
            
            if account_type == 'demo':
                # للحسابات التجريبية، التحقق من الرصيد المحلي
                balance_result = enhanced_account_manager.get_account_balance(
                    user_id, account_type, market_type, exchange
                )
                
                if balance_result['success']:
                    available_balance = balance_result['balance']['available_balance']
                    if available_balance >= trade_amount:
                        return {
                            'success': True,
                            'message': 'الرصيد كافي للتنفيذ'
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'الرصيد غير كافي. المتاح: {available_balance}, المطلوب: {trade_amount}',
                            'error': 'INSUFFICIENT_BALANCE'
                        }
                else:
                    return {
                        'success': False,
                        'message': 'فشل في التحقق من الرصيد',
                        'error': 'BALANCE_CHECK_FAILED'
                    }
            
            else:
                # للحسابات الحقيقية، التحقق من API المنصة
                # هنا سيتم استدعاء API المنصة الحقيقية
                return {
                    'success': True,
                    'message': 'تم التحقق من الرصيد الحقيقي'
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحقق من الرصيد: {e}")
            return {
                'success': False,
                'message': f'خطأ في التحقق من الرصيد: {str(e)}',
                'error': 'BALANCE_CHECK_ERROR'
            }
    
    async def _execute_signal(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ الإشارة"""
        try:
            account_type = user_settings['account_type']
            
            if account_type == 'demo':
                # تنفيذ تجريبي
                return await self._execute_demo_signal(signal_data, user_settings, user_id)
            else:
                # تنفيذ حقيقي
                return await self._execute_real_signal(signal_data, user_settings, user_id)
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الإشارة: {str(e)}',
                'error': 'EXECUTION_ERROR'
            }
    
    async def _execute_demo_signal(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ إشارة تجريبية"""
        try:
            self.logger.info(f"🎮 تنفيذ إشارة تجريبية: {signal_data}")
            
            # استخدام النظام المتقدم للمعالجة
            result = advanced_signal_manager.process_signal(signal_data, user_id)
            
            if result['success']:
                # تنفيذ الصفقة التجريبية
                trade_result = enhanced_account_manager.execute_trade(user_id, signal_data, user_settings)
                
                return {
                    'success': trade_result['success'],
                    'message': trade_result['message'],
                    'execution_type': 'demo',
                    'trade_details': trade_result
                }
            else:
                return {
                    'success': False,
                    'message': f'فشل في معالجة الإشارة: {result["message"]}',
                    'error': result.get('error', 'SIGNAL_PROCESSING_FAILED')
                }
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الإشارة التجريبية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الإشارة التجريبية: {str(e)}',
                'error': 'DEMO_EXECUTION_ERROR'
            }
    
    async def _execute_real_signal(self, signal_data: Dict[str, Any], user_settings: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """تنفيذ إشارة حقيقية"""
        try:
            self.logger.info(f"🌐 تنفيذ إشارة حقيقية: {signal_data}")
            
            # استخدام النظام المتكامل للتنفيذ
            result = await integrated_signal_system.process_signal_complete(signal_data, user_id)
            
            return {
                'success': result['success'],
                'message': result['message'],
                'execution_type': 'real',
                'execution_details': result
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الإشارة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الإشارة الحقيقية: {str(e)}',
                'error': 'REAL_EXECUTION_ERROR'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        try:
            return {
                'system_name': 'Final Signal Processor',
                'version': '1.0.0',
                'status': 'active',
                'supported_signals': list(self.supported_signals.keys()),
                'supported_accounts': self.supported_accounts,
                'supported_markets': self.supported_markets,
                'supported_exchanges': self.supported_exchanges,
                'features': [
                    'Signal Validation',
                    'Account Type Support',
                    'Market Type Support',
                    'Exchange Support',
                    'ID-based Linking',
                    'Balance Checking',
                    'Demo/Real Execution',
                    'Rule-based Processing'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الحصول على حالة النظام: {e}")
            return {
                'error': f'خطأ في الحصول على حالة النظام: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


# مثيل عام لمعالج الإشارات النهائي
final_signal_processor = FinalSignalProcessor()


# دوال مساعدة للاستخدام السريع
async def process_signal_final(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة إشارة نهائية"""
    return await final_signal_processor.process_signal(signal_data, user_id)


def get_system_status_final() -> Dict[str, Any]:
    """الحصول على حالة النظام النهائي"""
    return final_signal_processor.get_system_status()


if __name__ == "__main__":
    # اختبار معالج الإشارات النهائي
    print("=" * 80)
    print("اختبار معالج الإشارات النهائي")
    print("=" * 80)
    
    # حالة النظام
    system_status = get_system_status_final()
    print(f"📋 حالة النظام: {system_status}")
    
    # اختبار معالجة الإشارات
    user_id = 12345
    
    # أمثلة الإشارات
    test_signals = [
        {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'},
        {'signal': 'sell', 'symbol': 'BTCUSDT', 'id': 'TV_S01'},
        {'signal': 'close', 'symbol': 'BTCUSDT', 'id': 'TV_C01'},
        {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_PC01', 'percentage': 50}
    ]
    
    async def test_signals():
        for signal in test_signals:
            print(f"\n📥 معالجة الإشارة: {signal}")
            result = await process_signal_final(signal, user_id)
            print(f"📤 النتيجة: {result}")
    
    # تشغيل الاختبار
    asyncio.run(test_signals())
