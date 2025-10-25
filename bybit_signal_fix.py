#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشكلة فشل تنفيذ الإشارة على Bybit
"""

import logging
import asyncio
from typing import Dict, Optional
from real_account_manager import real_account_manager
from signal_executor import SignalExecutor

logger = logging.getLogger(__name__)

class BybitSignalFixer:
    """فئة لإصلاح مشاكل تنفيذ الإشارات على Bybit"""
    
    def __init__(self):
        self.min_order_amounts = {
            'BTCUSDT': {'min_qty': 0.001, 'min_notional': 5.0},
            'ETHUSDT': {'min_qty': 0.01, 'min_notional': 5.0},
            'ADAUSDT': {'min_qty': 1.0, 'min_notional': 5.0},
            'SOLUSDT': {'min_qty': 0.01, 'min_notional': 5.0},
            'DOGEUSDT': {'min_qty': 1.0, 'min_notional': 5.0}
        }
    
    async def fix_signal_execution(self, user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """إصلاح تنفيذ الإشارة مع معالجة شاملة للأخطاء"""
        try:
            logger.info(f"🔧 بدء إصلاح تنفيذ الإشارة للمستخدم {user_id}")
            logger.info(f"📊 بيانات الإشارة: {signal_data}")
            
            # التحقق من صحة البيانات الأساسية
            validation_result = self._validate_signal_data(signal_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': f'بيانات الإشارة غير صحيحة: {validation_result["error"]}',
                    'error': 'INVALID_SIGNAL_DATA'
                }
            
            # الحصول على الحساب الحقيقي
            real_account = real_account_manager.get_account(user_id)
            if not real_account:
                return {
                    'success': False,
                    'message': 'الحساب الحقيقي غير مفعّل - مفاتيح API مفقودة أو غير صحيحة',
                    'error': 'ACCOUNT_NOT_FOUND'
                }
            
            # فحص الرصيد المتاح
            balance_check = await self._check_account_balance(real_account, signal_data, user_data)
            if not balance_check['sufficient']:
                return {
                    'success': False,
                    'message': f'الرصيد غير كافي: {balance_check["message"]}',
                    'error': 'INSUFFICIENT_BALANCE',
                    'available_balance': balance_check.get('available_balance', 0),
                    'required_balance': balance_check.get('required_balance', 0)
                }
            
            # حساب الكمية الصحيحة
            quantity_result = self._calculate_correct_quantity(signal_data, user_data, balance_check)
            if not quantity_result['success']:
                return {
                    'success': False,
                    'message': f'خطأ في حساب الكمية: {quantity_result["error"]}',
                    'error': 'QUANTITY_CALCULATION_ERROR'
                }
            
            # تحديث بيانات الإشارة بالكمية الصحيحة
            signal_data['calculated_qty'] = quantity_result['qty']
            signal_data['calculated_price'] = quantity_result['price']
            
            # محاولة تنفيذ الإشارة مع إعادة المحاولة
            execution_result = await self._execute_with_retry(real_account, signal_data, user_data, user_id)
            
            if execution_result['success']:
                logger.info(f"✅ تم تنفيذ الإشارة بنجاح للمستخدم {user_id}")
                return execution_result
            else:
                logger.error(f"❌ فشل تنفيذ الإشارة للمستخدم {user_id}: {execution_result['message']}")
                return execution_result
                
        except Exception as e:
            logger.error(f"💥 خطأ عام في إصلاح تنفيذ الإشارة: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'خطأ عام: {str(e)}',
                'error': 'GENERAL_ERROR'
            }
    
    def _validate_signal_data(self, signal_data: Dict) -> Dict:
        """التحقق من صحة بيانات الإشارة"""
        try:
            required_fields = ['symbol', 'action', 'amount']
            for field in required_fields:
                if field not in signal_data or not signal_data[field]:
                    return {
                        'valid': False,
                        'error': f'حقل مطلوب مفقود: {field}'
                    }
            
            symbol = signal_data['symbol']
            if symbol not in self.min_order_amounts:
                logger.warning(f"رمز غير معروف: {symbol}، سيتم استخدام القيم الافتراضية")
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'خطأ في التحقق: {str(e)}'
            }
    
    async def _check_account_balance(self, account, signal_data: Dict, user_data: Dict) -> Dict:
        """فحص الرصيد المتاح"""
        try:
            symbol = signal_data['symbol']
            amount = float(signal_data.get('amount', 0))
            leverage = int(user_data.get('leverage', 1))
            market_type = user_data.get('market_type', 'futures')
            
            # تحديد نوع الحساب للفحص
            account_type = 'futures' if market_type == 'futures' else 'spot'
            
            # جلب الرصيد
            balance_info = account.get_wallet_balance(account_type)
            if not balance_info or 'coins' not in balance_info:
                return {
                    'sufficient': False,
                    'message': 'فشل في جلب معلومات الرصيد'
                }
            
            usdt_balance = 0
            if 'USDT' in balance_info['coins']:
                usdt_balance = float(balance_info['coins']['USDT'].get('equity', 0))
            
            logger.info(f"💰 الرصيد المتاح: {usdt_balance} USDT")
            
            # حساب المبلغ المطلوب
            if market_type == 'futures':
                required_amount = amount * leverage
            else:
                required_amount = amount
            
            # إضافة هامش أمان 10%
            required_amount_with_margin = required_amount * 1.1
            
            logger.info(f"💸 المبلغ المطلوب: {required_amount} USDT (مع هامش: {required_amount_with_margin})")
            
            if usdt_balance >= required_amount_with_margin:
                return {
                    'sufficient': True,
                    'available_balance': usdt_balance,
                    'required_balance': required_amount_with_margin,
                    'message': 'الرصيد كافي'
                }
            else:
                return {
                    'sufficient': False,
                    'available_balance': usdt_balance,
                    'required_balance': required_amount_with_margin,
                    'message': f'الرصيد غير كافي. متاح: {usdt_balance:.2f} USDT، مطلوب: {required_amount_with_margin:.2f} USDT'
                }
                
        except Exception as e:
            logger.error(f"خطأ في فحص الرصيد: {e}")
            return {
                'sufficient': False,
                'message': f'خطأ في فحص الرصيد: {str(e)}'
            }
    
    def _calculate_correct_quantity(self, signal_data: Dict, user_data: Dict, balance_check: Dict) -> Dict:
        """حساب الكمية الصحيحة مع مراعاة الحدود الدنيا"""
        try:
            symbol = signal_data['symbol']
            amount = float(signal_data.get('amount', 0))
            leverage = int(user_data.get('leverage', 1))
            market_type = user_data.get('market_type', 'futures')
            price = float(signal_data.get('price', 0))
            
            # جلب السعر إذا لم يكن موجوداً
            if price <= 0:
                logger.warning(f"السعر غير صحيح: {price}، سيتم استخدام سعر تقديري")
                # أسعار تقديرية للعملات الرئيسية
                estimated_prices = {
                    'BTCUSDT': 110000,
                    'ETHUSDT': 3500,
                    'ADAUSDT': 0.5,
                    'SOLUSDT': 100,
                    'DOGEUSDT': 0.08
                }
                price = estimated_prices.get(symbol, 100)
            
            # حساب الكمية الأساسية
            if market_type == 'futures':
                qty = (amount * leverage) / price
            else:
                qty = amount / price
            
            # تطبيق الحدود الدنيا
            min_info = self.min_order_amounts.get(symbol, {'min_qty': 0.001, 'min_notional': 5.0})
            min_qty = min_info['min_qty']
            min_notional = min_info['min_notional']
            
            # التحقق من الحد الأدنى للكمية
            if qty < min_qty:
                logger.warning(f"الكمية صغيرة جداً: {qty}، تم تعديلها إلى الحد الأدنى: {min_qty}")
                qty = min_qty
            
            # التحقق من الحد الأدنى للقيمة الاسمية
            notional_value = qty * price
            if notional_value < min_notional:
                logger.warning(f"القيمة الاسمية صغيرة جداً: {notional_value}، تم تعديل الكمية")
                qty = min_notional / price
            
            # تقريب الكمية حسب دقة الرمز
            if symbol in ['BTCUSDT', 'ETHUSDT']:
                qty = round(qty, 3)
            else:
                qty = round(qty, 2)
            
            logger.info(f"📊 حساب الكمية: ${amount} → {qty} {symbol.split('USDT')[0]} (السعر: ${price})")
            
            return {
                'success': True,
                'qty': qty,
                'price': price,
                'notional_value': qty * price
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب الكمية: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_with_retry(self, account, signal_data: Dict, user_data: Dict, user_id: int) -> Dict:
        """تنفيذ الإشارة مع إعادة المحاولة"""
        max_retries = 3
        retry_delay = 2  # ثواني
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 محاولة تنفيذ الإشارة {attempt + 1}/{max_retries}")
                
                # استخدام المنفذ الأصلي مع البيانات المصححة
                result = await SignalExecutor.execute_signal(user_id, signal_data, user_data)
                
                if result.get('success'):
                    logger.info(f"✅ نجح تنفيذ الإشارة في المحاولة {attempt + 1}")
                    return result
                else:
                    logger.warning(f"⚠️ فشل تنفيذ الإشارة في المحاولة {attempt + 1}: {result.get('message', '')}")
                    
                    # إذا لم تكن هذه المحاولة الأخيرة، انتظر قبل إعادة المحاولة
                    if attempt < max_retries - 1:
                        logger.info(f"⏳ انتظار {retry_delay} ثانية قبل إعادة المحاولة...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # زيادة وقت الانتظار تدريجياً
                
            except Exception as e:
                logger.error(f"💥 خطأ في المحاولة {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
        
        # إذا فشلت جميع المحاولات
        return {
            'success': False,
            'message': f'فشل تنفيذ الإشارة بعد {max_retries} محاولات',
            'error': 'MAX_RETRIES_EXCEEDED'
        }

# دالة مساعدة للاستخدام المباشر
async def fix_bybit_signal(user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
    """دالة مساعدة لإصلاح تنفيذ إشارة Bybit"""
    fixer = BybitSignalFixer()
    return await fixer.fix_signal_execution(user_id, signal_data, user_data)

if __name__ == "__main__":
    # اختبار الدالة
    test_signal = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': '4',
        'generated_id': False,
        'position_id': 'POS-4',
        'amount': 55.0,
        'price': 111190.3,
        'signal_id': '4',
        'has_signal_id': True
    }
    
    test_user_data = {
        'trade_amount': 55.0,
        'leverage': 1,
        'exchange': 'bybit',
        'account_type': 'real',
        'market_type': 'futures'
    }
    
    print("🔧 اختبار إصلاح تنفيذ الإشارة...")
    # result = asyncio.run(fix_bybit_signal(1, test_signal, test_user_data))
    # print(f"النتيجة: {result}")
