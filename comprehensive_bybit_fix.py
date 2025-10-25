#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح شامل لمشكلة فشل تنفيذ الإشارة على Bybit
"""

import logging
import asyncio
import json
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ComprehensiveBybitFix:
    """إصلاح شامل لمشاكل Bybit"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors_found = []
    
    async def diagnose_and_fix(self, user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """تشخيص وإصلاح شامل للمشكلة"""
        try:
            logger.info("🔍 بدء التشخيص الشامل لمشكلة Bybit...")
            
            # 1. تشخيص المشاكل المحتملة
            diagnosis = await self._comprehensive_diagnosis(user_id, signal_data, user_data)
            
            # 2. تطبيق الإصلاحات
            fixes = await self._apply_fixes(diagnosis, user_id, signal_data, user_data)
            
            # 3. اختبار الحل
            test_result = await self._test_solution(user_id, signal_data, user_data)
            
            return {
                'success': test_result['success'],
                'message': test_result['message'],
                'diagnosis': diagnosis,
                'fixes_applied': self.fixes_applied,
                'errors_found': self.errors_found,
                'test_result': test_result
            }
            
        except Exception as e:
            logger.error(f"💥 خطأ في التشخيص الشامل: {e}")
            return {
                'success': False,
                'message': f'خطأ في التشخيص: {str(e)}',
                'error': 'DIAGNOSIS_ERROR'
            }
    
    async def _comprehensive_diagnosis(self, user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """تشخيص شامل للمشاكل"""
        diagnosis = {
            'api_keys': False,
            'account_status': False,
            'balance_sufficient': False,
            'symbol_valid': False,
            'quantity_valid': False,
            'leverage_set': False,
            'api_connectivity': False,
            'permissions': False
        }
        
        try:
            # 1. فحص مفاتيح API
            from real_account_manager import real_account_manager
            real_account = real_account_manager.get_account(user_id)
            
            if real_account:
                diagnosis['api_keys'] = True
                logger.info("✅ مفاتيح API صحيحة")
            else:
                diagnosis['api_keys'] = False
                self.errors_found.append("مفاتيح API مفقودة أو غير صحيحة")
                logger.error("❌ مفاتيح API مفقودة")
            
            # 2. فحص حالة الحساب
            if real_account:
                try:
                    balance = real_account.get_wallet_balance('futures')
                    if balance:
                        diagnosis['account_status'] = True
                        logger.info("✅ الحساب نشط")
                    else:
                        diagnosis['account_status'] = False
                        self.errors_found.append("الحساب غير نشط")
                except Exception as e:
                    diagnosis['account_status'] = False
                    self.errors_found.append(f"خطأ في فحص الحساب: {e}")
            
            # 3. فحص الرصيد
            if real_account and diagnosis['account_status']:
                try:
                    balance = real_account.get_wallet_balance('futures')
                    if balance and 'coins' in balance and 'USDT' in balance['coins']:
                        usdt_balance = float(balance['coins']['USDT'].get('equity', 0))
                        required_amount = float(signal_data.get('amount', 0)) * int(user_data.get('leverage', 1))
                        
                        if usdt_balance >= required_amount * 1.1:  # هامش أمان 10%
                            diagnosis['balance_sufficient'] = True
                            logger.info(f"✅ الرصيد كافي: {usdt_balance} USDT")
                        else:
                            diagnosis['balance_sufficient'] = False
                            self.errors_found.append(f"الرصيد غير كافي: {usdt_balance} < {required_amount}")
                except Exception as e:
                    diagnosis['balance_sufficient'] = False
                    self.errors_found.append(f"خطأ في فحص الرصيد: {e}")
            
            # 4. فحص صحة الرمز
            symbol = signal_data.get('symbol', '')
            if symbol and symbol.endswith('USDT'):
                diagnosis['symbol_valid'] = True
                logger.info(f"✅ الرمز صحيح: {symbol}")
            else:
                diagnosis['symbol_valid'] = False
                self.errors_found.append(f"الرمز غير صحيح: {symbol}")
            
            # 5. فحص الكمية
            amount = float(signal_data.get('amount', 0))
            price = float(signal_data.get('price', 0))
            if amount > 0 and price > 0:
                qty = amount / price
                if qty >= 0.001:  # الحد الأدنى لـ BTCUSDT
                    diagnosis['quantity_valid'] = True
                    logger.info(f"✅ الكمية صحيحة: {qty}")
                else:
                    diagnosis['quantity_valid'] = False
                    self.errors_found.append(f"الكمية صغيرة جداً: {qty}")
            else:
                diagnosis['quantity_valid'] = False
                self.errors_found.append("الكمية أو السعر غير صحيح")
            
            # 6. فحص الاتصال بـ API
            if real_account:
                try:
                    ticker = real_account.get_ticker('linear', symbol)
                    if ticker:
                        diagnosis['api_connectivity'] = True
                        logger.info("✅ الاتصال بـ API يعمل")
                    else:
                        diagnosis['api_connectivity'] = False
                        self.errors_found.append("فشل في الاتصال بـ API")
                except Exception as e:
                    diagnosis['api_connectivity'] = False
                    self.errors_found.append(f"خطأ في الاتصال بـ API: {e}")
            
            logger.info(f"📊 نتائج التشخيص: {diagnosis}")
            logger.info(f"🚨 الأخطاء المكتشفة: {self.errors_found}")
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"خطأ في التشخيص: {e}")
            return diagnosis
    
    async def _apply_fixes(self, diagnosis: Dict, user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """تطبيق الإصلاحات المطلوبة"""
        fixes_applied = []
        
        try:
            from real_account_manager import real_account_manager
            real_account = real_account_manager.get_account(user_id)
            
            # إصلاح 1: إعادة تهيئة الحساب إذا لزم الأمر
            if not diagnosis['api_keys']:
                logger.info("🔧 إصلاح: إعادة تهيئة الحساب...")
                try:
                    api_key = user_data.get('bybit_api_key')
                    api_secret = user_data.get('bybit_api_secret')
                    if api_key and api_secret:
                        real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
                        fixes_applied.append("إعادة تهيئة الحساب")
                        logger.info("✅ تم إعادة تهيئة الحساب")
                except Exception as e:
                    logger.error(f"فشل في إعادة تهيئة الحساب: {e}")
            
            # إصلاح 2: تصحيح الكمية إذا كانت صغيرة جداً
            if not diagnosis['quantity_valid']:
                logger.info("🔧 إصلاح: تصحيح الكمية...")
                amount = float(signal_data.get('amount', 0))
                price = float(signal_data.get('price', 0))
                
                if amount > 0 and price > 0:
                    # ضمان الحد الأدنى للكمية
                    min_qty = 0.001
                    min_amount = min_qty * price
                    
                    if amount < min_amount:
                        signal_data['amount'] = min_amount
                        fixes_applied.append(f"تصحيح الكمية من {amount} إلى {min_amount}")
                        logger.info(f"✅ تم تصحيح الكمية إلى {min_amount}")
            
            # إصلاح 3: تعيين الرافعة المالية
            if not diagnosis['leverage_set']:
                logger.info("🔧 إصلاح: تعيين الرافعة المالية...")
                try:
                    symbol = signal_data.get('symbol', '')
                    leverage = int(user_data.get('leverage', 1))
                    
                    if real_account and symbol:
                        leverage_result = real_account.set_leverage('linear', symbol, leverage)
                        if leverage_result:
                            fixes_applied.append(f"تعيين الرافعة إلى {leverage}x")
                            logger.info(f"✅ تم تعيين الرافعة إلى {leverage}x")
                except Exception as e:
                    logger.error(f"فشل في تعيين الرافعة: {e}")
            
            # إصلاح 4: تحديث السعر إذا لم يكن موجوداً
            if not signal_data.get('price') or float(signal_data.get('price', 0)) <= 0:
                logger.info("🔧 إصلاح: جلب السعر الحالي...")
                try:
                    symbol = signal_data.get('symbol', '')
                    if real_account and symbol:
                        ticker = real_account.get_ticker('linear', symbol)
                        if ticker and 'lastPrice' in ticker:
                            current_price = float(ticker['lastPrice'])
                            signal_data['price'] = current_price
                            fixes_applied.append(f"تحديث السعر إلى {current_price}")
                            logger.info(f"✅ تم تحديث السعر إلى {current_price}")
                except Exception as e:
                    logger.error(f"فشل في جلب السعر: {e}")
            
            self.fixes_applied = fixes_applied
            logger.info(f"🔧 الإصلاحات المطبقة: {fixes_applied}")
            
            return {
                'success': len(fixes_applied) > 0,
                'fixes': fixes_applied
            }
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق الإصلاحات: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_solution(self, user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """اختبار الحل بعد تطبيق الإصلاحات"""
        try:
            logger.info("🧪 اختبار الحل...")
            
            # استخدام المنفذ الأصلي مع البيانات المصححة
            from signal_executor import SignalExecutor
            
            # إضافة معلومات إضافية للاختبار
            test_signal = signal_data.copy()
            test_signal['test_mode'] = True
            test_signal['fix_applied'] = True
            
            result = await SignalExecutor.execute_signal(user_id, test_signal, user_data)
            
            if result.get('success'):
                logger.info("✅ نجح اختبار الحل!")
                return {
                    'success': True,
                    'message': 'تم إصلاح المشكلة بنجاح',
                    'execution_result': result
                }
            else:
                logger.error(f"❌ فشل اختبار الحل: {result.get('message', '')}")
                return {
                    'success': False,
                    'message': f'فشل اختبار الحل: {result.get("message", "")}',
                    'execution_result': result
                }
                
        except Exception as e:
            logger.error(f"خطأ في اختبار الحل: {e}")
            return {
                'success': False,
                'message': f'خطأ في اختبار الحل: {str(e)}',
                'error': 'TEST_ERROR'
            }

# دالة رئيسية للإصلاح السريع
async def quick_fix_bybit_signal(user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
    """إصلاح سريع لمشكلة Bybit"""
    fixer = ComprehensiveBybitFix()
    return await fixer.diagnose_and_fix(user_id, signal_data, user_data)

# دالة للاستخدام مع البيانات المحددة في المشكلة
async def fix_btcusdt_signal() -> Dict:
    """إصلاح إشارة BTCUSDT المحددة"""
    
    # بيانات الإشارة من المشكلة
    signal_data = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': '4',
        'generated_id': False,
        'position_id': 'POS-4',
        'enhanced_analysis': {
            'signal_quality': 'high',
            'confidence_level': 0.85,
            'market_conditions': 'favorable',
            'recommendation': 'execute',
            'risk_level': 'medium',
            'asset_type': 'cryptocurrency',
            'volatility': 'high'
        },
        'enhanced_risk_assessment': {
            'risk_level': 'low',
            'max_position_size': 0.2,
            'stop_loss': 0.02,
            'take_profit': 0.04,
            'recommendation': 'proceed_with_caution'
        },
        'enhanced_execution_plan': {
            'strategy': 'TWAP',
            'timing': 'optimal',
            'price_optimization': True,
            'slippage_protection': True,
            'execution_priority': 'high',
            'execution_time': '5_minutes'
        },
        'price': 111190.3,
        'position_id': 'POS-4',
        'generated_id': False,
        'has_signal_id': True,
        'signal_id': '4',
        'amount': 55.0,
        'action': 'buy'
    }
    
    # بيانات المستخدم (يجب تحديثها حسب المستخدم الفعلي)
    user_data = {
        'trade_amount': 55.0,
        'leverage': 1,
        'exchange': 'bybit',
        'account_type': 'real',
        'market_type': 'futures',
        'bybit_api_key': 'YOUR_API_KEY',  # يجب استبدالها بالمفاتيح الفعلية
        'bybit_api_secret': 'YOUR_API_SECRET'  # يجب استبدالها بالمفاتيح الفعلية
    }
    
    logger.info("🔧 بدء إصلاح إشارة BTCUSDT...")
    result = await quick_fix_bybit_signal(1, signal_data, user_data)
    
    return result

if __name__ == "__main__":
    print("🔧 نظام إصلاح مشاكل Bybit")
    print("=" * 50)
    
    # تشغيل الإصلاح
    # result = asyncio.run(fix_btcusdt_signal())
    # print(f"النتيجة: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("✅ تم تحميل نظام الإصلاح بنجاح")
    print("📝 للاستخدام:")
    print("1. قم بتحديث مفاتيح API في user_data")
    print("2. استدعِ fix_btcusdt_signal() أو quick_fix_bybit_signal()")
    print("3. راجع النتائج في result")