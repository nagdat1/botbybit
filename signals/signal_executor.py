#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
import sys
import os
from typing import Dict, Optional
from api.bybit_api import real_account_manager
from . import signal_position_manager

# إضافة مسار المشروع للاستيراد
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

# استيراد أداة التعديل الذكية
try:
    from api.quantity_adjuster import QuantityAdjuster
    QUANTITY_ADJUSTER_AVAILABLE = True
    logger.info("✅ تم تحميل أداة التعديل الذكية بنجاح")
except ImportError as e:
    QUANTITY_ADJUSTER_AVAILABLE = False
    logger.warning(f"⚠️ لم يتم العثور على أداة التعديل الذكية: {e}")
    
    # إنشاء فئة بديلة بسيطة
    class QuantityAdjuster:
        @staticmethod
        def smart_quantity_adjustment(qty, price, trade_amount, leverage, exchange):
            return round(qty, 4)
        
        @staticmethod
        def get_multiple_quantity_options(qty, price, exchange):
            return [round(qty, 4), round(qty * 1.001, 4), round(qty * 0.999, 4)]
        
        @staticmethod
        def validate_quantity(qty, price, exchange, market_type='futures'):
            return {'valid': True, 'errors': [], 'warnings': [], 'suggestions': []}

# استيراد دالة فحص المخاطر
try:
    from bybit_trading_bot import check_risk_management, reset_daily_loss_if_needed
except ImportError:
    # إذا لم تكن متوفرة، نعرف دوال فارغة
    def check_risk_management(user_id, trade_result):
        return {'should_stop': False, 'message': 'Risk management not available'}
    
    def reset_daily_loss_if_needed(user_id):
        pass

# استيراد النظام المحسن
try:
    from systems.simple_enhanced_system import SimpleEnhancedSystem
    ENHANCED_SYSTEM_AVAILABLE = True
except ImportError as e:
    ENHANCED_SYSTEM_AVAILABLE = False

# استيراد مدير معرفات الإشارات
try:
    from . import signal_id_manager
    get_position_id_from_signal = signal_id_manager.get_position_id_from_signal
    get_signal_id_manager = signal_id_manager.get_signal_id_manager
    SIGNAL_ID_MANAGER_AVAILABLE = True
except ImportError as e:
    SIGNAL_ID_MANAGER_AVAILABLE = False

class SignalExecutor:
    """منفذ الإشارات على الحسابات الحقيقية"""
    
    @staticmethod
    async def execute_signal(user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """
        تنفيذ إشارة تداول
        
        Args:
            user_id: معرف المستخدم
            signal_data: بيانات الإشارة (action, symbol, price, etc.)
            user_data: إعدادات المستخدم
            
        Returns:
            نتيجة التنفيذ
        """
        try:
            # استخدام النظام المحسن إذا كان متاحاً
            if ENHANCED_SYSTEM_AVAILABLE:
                try:
                    enhanced_system = SimpleEnhancedSystem()
                    logger.info("🚀 معالجة الإشارة باستخدام النظام المحسن في signal_executor...")
                    enhanced_result = enhanced_system.process_signal(user_id, signal_data)
                    logger.info(f"✅ نتيجة النظام المحسن في signal_executor: {enhanced_result}")
                    
                    # إذا نجح النظام المحسن، نستخدم النتيجة ولكن نتابع التنفيذ العادي
                    if enhanced_result.get('status') == 'success':
                        logger.info("✅ تم استخدام نتيجة النظام المحسن في signal_executor، نتابع التنفيذ العادي")
                        # نستخدم النتيجة المحسنة ولكن نتابع التنفيذ العادي
                        signal_data['enhanced_analysis'] = enhanced_result.get('analysis', {})
                        signal_data['enhanced_risk_assessment'] = enhanced_result.get('risk_assessment', {})
                        signal_data['enhanced_execution_plan'] = enhanced_result.get('execution_plan', {})
                    else:
                        logger.warning("⚠️ فشل النظام المحسن في signal_executor، نعود للنظام العادي")
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في النظام المحسن في signal_executor: {e}")
            
            account_type = user_data.get('account_type', 'demo')
            exchange = user_data.get('exchange', 'bybit')
            market_type = user_data.get('market_type', 'spot')
            
            logger.info(f"🎯 تنفيذ إشارة للمستخدم {user_id}: {signal_data.get('action')} {signal_data.get('symbol')}")
            logger.info(f"📊 نوع الحساب: {account_type}, المنصة: {exchange}, السوق: {market_type}")
            
            # إذا كان حساب تجريبي، إرجاع استجابة محاكاة
            if account_type == 'demo':
                logger.info(f"🟢 حساب تجريبي - سيتم المعالجة بواسطة البوت الأصلي")
                return {
                    'success': False,
                    'message': 'Demo account - handled by original bot',
                    'is_demo': True
                }
            
            # الحصول على الحساب الحقيقي
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                logger.error(f"❌ حساب حقيقي غير مفعّل للمستخدم {user_id}")
                
                # محاولة إعادة التهيئة من بيانات المستخدم
                logger.info(f"🔍 محاولة تهيئة الحساب الحقيقي للمستخدم {user_id}...")
                
                # تحديد المنصة المفضلة للمستخدم
                exchange = user_data.get('exchange', 'bybit').lower()
                logger.info(f"📊 منصة المستخدم: {exchange}")
                
                # جلب المفاتيح حسب المنصة
                if exchange == 'bybit':
                    api_key = user_data.get('bybit_api_key', '') or user_data.get('api_key', '')
                    api_secret = user_data.get('bybit_api_secret', '') or user_data.get('api_secret', '')
                elif exchange == 'bitget':
                    api_key = user_data.get('bitget_api_key', '') or user_data.get('api_key', '')
                    api_secret = user_data.get('bitget_api_secret', '') or user_data.get('api_secret', '')
                elif exchange == 'binance':
                    api_key = user_data.get('binance_api_key', '') or user_data.get('api_key', '')
                    api_secret = user_data.get('binance_api_secret', '') or user_data.get('api_secret', '')
                elif exchange == 'okx':
                    api_key = user_data.get('okx_api_key', '') or user_data.get('api_key', '')
                    api_secret = user_data.get('okx_api_secret', '') or user_data.get('api_secret', '')
                else:
                    # افتراضي: استخدام مفاتيح API العامة
                    api_key = user_data.get('api_key', '')
                    api_secret = user_data.get('api_secret', '')
                
                logger.info(f"🔑 محاولة استخدام مفاتيح API من قاعدة البيانات...")
                logger.info(f"   API Key موجود: {bool(api_key and len(api_key) > 10)}")
                logger.info(f"   API Secret موجود: {bool(api_secret and len(api_secret) > 10)}")
                
                if api_key and api_secret and len(api_key) > 10 and len(api_secret) > 10:
                    try:
                        logger.info(f"🔧 تهيئة الحساب الحقيقي للمستخدم {user_id}...")
                        real_account_manager.initialize_account(user_id, exchange, api_key, api_secret)
                        logger.info(f"✅ تم تهيئة الحساب للمستخدم {user_id}")
                        
                        # إعادة المحاولة للحصول على الحساب
                        real_account = real_account_manager.get_account(user_id)
                        logger.info(f"✅ تم تحميل الحساب بنجاح: {real_account is not None}")
                        
                        # 🔧 اختبار الاتصال فوراً بعد التهيئة
                        if real_account:
                            logger.info(f"🧪 اختبار الاتصال بالمنصة...")
                            test_result = real_account.get_wallet_balance(market_type)
                            if test_result is None or (isinstance(test_result, dict) and test_result.get('error')):
                                logger.error(f"❌ فشل اختبار الاتصال بالمنصة")
                                error_details = test_result if isinstance(test_result, dict) else {}
                                error_code = error_details.get('retCode', 'Unknown')
                                error_msg = error_details.get('retMsg', 'Connection test failed')
                                
                                return {
                                    'success': False,
                                    'message': f'فشل اختبار الاتصال بالمنصة: {error_msg} (Code: {error_code})',
                                    'error': 'CONNECTION_TEST_FAILED',
                                    'error_code': error_code,
                                    'help': 'Please check your API keys and permissions'
                                }
                            else:
                                logger.info(f"✅ نجح اختبار الاتصال بالمنصة")
                        
                    except Exception as init_e:
                        logger.error(f"❌ فشل تهيئة الحساب: {init_e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        error_msg = str(init_e)
                        
                        # تحديد نوع الخطأ وتوفير رسالة واضحة
                        if 'invalid' in error_msg.lower() or '401' in error_msg or '10001' in error_msg:
                            detailed_message = f"""
❌ فشل في تنفيذ صفقة الفيوتشر: API key is invalid.

📋 السبب المحتمل:
• المفاتيح غير صحيحة أو منتهية الصلاحية
• المفاتيح غير موجودة في قاعدة البيانات
• تفاصيل الخطأ: {error_msg}

💡 الحل:
1. اذهب إلى الإعدادات في البوت
2. اختر "إعدادات الحساب الحقيقي"
3. أدخل مفاتيح API الصحيحة من Bybit
4. تأكد من تفعيل جميع الصلاحيات اللازمة

🔑 للحصول على مفاتيح API من Bybit:
1. اذهب إلى https://www.bybit.com/
2. اذهب إلى Account & Security → API Management
3. أنشئ API Key جديد مع الصلاحيات التالية:
   - Trade (للتنفيذ)
   - Read (للقراءة)
   - Futures Trading (للإفتراضية)
"""
                            return {
                                'success': False,
                                'message': detailed_message.strip(),
                                'error': 'INVALID_API_KEY',
                                'help': 'Please update your API keys in settings with valid credentials'
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'فشل تهيئة الحساب: {init_e}',
                                'error': 'ACCOUNT_INIT_FAILED'
                            }
                else:
                    logger.error(f"❌ مفاتيح API غير موجودة للمستخدم {user_id}")
                    detailed_message = f"""
❌ مفاتيح API غير موجودة في قاعدة البيانات

🔍 التفاصيل:
• نوع الحساب: {account_type}
• المستخدم: {user_id}
• المفاتيح الموجودة: {bool(api_key)} / {bool(api_secret)}

💡 الحل:
1. اذهب إلى الإعدادات في البوت
2. اختر "إعدادات الحساب الحقيقي" أو "ربط الحساب"
3. أدخل مفاتيح Bybit API الخاصة بك
4. تأكد من تفعيل نوع الحساب على "Real" وليس "Demo"

⚠️ ملاحظة مهمة:
• يجب إدخال المفاتيح الصحيحة من Bybit
• تأكد من تفعيل جميع الصلاحيات اللازمة
• بعد إضافة المفاتيح، أعد المحاولة
"""
                    return {
                        'success': False,
                        'message': detailed_message.strip(),
                        'error': 'API_KEYS_NOT_FOUND',
                        'help': 'Please configure your API keys in settings'
                    }
            
            # التحقق مرة أخرى
            if not real_account:
                logger.error(f"❌ حساب حقيقي غير متاح للمستخدم {user_id}")
                return {
                    'success': False,
                    'message': 'Real account not available',
                    'error': 'ACCOUNT_NOT_AVAILABLE'
                }
            
            # تحويل الإشارة إذا كانت بالتنسيق الجديد
            from . import signal_converter
            convert_simple_signal = signal_converter.convert_simple_signal
            
            # التحقق من نوع الإشارة (جديدة أو قديمة)
            if 'signal' in signal_data and 'action' not in signal_data:
                logger.info(f"📡 تحويل إشارة جديدة: {signal_data}")
                converted_signal = convert_simple_signal(signal_data, user_data)
                
                if not converted_signal:
                    logger.error(f"❌ فشل تحويل الإشارة الجديدة")
                    return {
                        'success': False,
                        'message': 'Failed to convert signal',
                        'error': 'CONVERSION_FAILED'
                    }
                
                signal_data = converted_signal
                logger.info(f"✅ تم تحويل الإشارة: {signal_data}")
            
            # استخراج معلومات الإشارة
            action = signal_data.get('action', '').lower()
            symbol = signal_data.get('symbol', '')
            price = float(signal_data.get('price', 0)) if signal_data.get('price') else 0.0
            signal_id = signal_data.get('signal_id', '')
            has_signal_id = signal_data.get('has_signal_id', False)
            
            logger.info(f"🆔 معلومات الـ ID: {signal_id} (موجود: {has_signal_id})")
            
            # إذا لم يكن السعر موجود، جلبه من API
            if not price or price == 0.0:
                try:
                    logger.info(f"🔍 جلب السعر الحالي لـ {symbol}...")
                    
                    # جلب السعر من Bybit
                    category = 'linear' if market_type == 'futures' else 'spot'
                    ticker = real_account.get_ticker(category, symbol)
                    if ticker and 'lastPrice' in ticker:
                        price = float(ticker['lastPrice'])
                        logger.info(f"✅ السعر الحالي: {price}")
                    else:
                        logger.error(f"❌ فشل جلب السعر من Bybit")
                        return {
                            'success': False,
                            'message': f'Failed to get current price for {symbol}',
                            'error': 'PRICE_FETCH_FAILED'
                        }
                except Exception as e:
                    logger.error(f"❌ خطأ في جلب السعر: {e}")
                    return {
                        'success': False,
                        'message': f'Error fetching price: {e}',
                        'error': 'PRICE_FETCH_ERROR'
                    }
            
            # معلومات التداول من إعدادات المستخدم
            trade_amount = user_data.get('trade_amount', 100.0)
            leverage = user_data.get('leverage', 10)
            
            logger.info(f"=" * 80)
            logger.info(f"🔍 تحليل الإعدادات المستلمة:")
            logger.info(f"   trade_amount: {trade_amount} USDT")
            logger.info(f"   leverage: {leverage}x")
            logger.info(f"   market_type: {user_data.get('market_type')}")
            logger.info(f"   user_data كامل: {user_data}")
            logger.info(f"=" * 80)
            
            # تنفيذ الإشارة حسب المنصة
            if exchange == 'bybit':
                result = await SignalExecutor._execute_bybit_signal(
                    real_account, signal_data, market_type, 
                    trade_amount, leverage, user_id
                )
            else:
                result = {
                    'success': False,
                    'message': f'Unsupported exchange: {exchange}',
                    'error': 'UNSUPPORTED_EXCHANGE'
                }
            
            # فحص إدارة المخاطر بعد تنفيذ الصفقة
            if result.get('success', False):
                try:
                    # إعادة تعيين الخسارة اليومية إذا لزم الأمر
                    reset_daily_loss_if_needed(user_id)
                    
                    # فحص المخاطر
                    risk_check = check_risk_management(user_id, result)
                    
                    if risk_check.get('should_stop', False):
                        logger.warning(f"🚨 تم إيقاف البوت للمستخدم {user_id}: {risk_check.get('message', '')}")
                        result['risk_stopped'] = True
                        result['risk_message'] = risk_check.get('message', '')
                    else:
                        logger.info(f"✅ فحص المخاطر نجح للمستخدم {user_id}")
                        
                except Exception as e:
                    logger.error(f"❌ خطأ في فحص المخاطر: {e}")
                    # لا نوقف الصفقة بسبب خطأ في فحص المخاطر
            
            return result
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الإشارة: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': str(e),
                'error': 'EXECUTION_ERROR'
            }
    
    @staticmethod
    async def _execute_bybit_signal(account, signal_data: Dict, market_type: str,
                                   trade_amount: float, leverage: int, user_id: int) -> Dict:
        """تنفيذ إشارة على Bybit"""
        try:
            # استخدام النظام المحسن إذا كان متاحاً
            if ENHANCED_SYSTEM_AVAILABLE:
                try:
                    enhanced_system = SimpleEnhancedSystem()
                    logger.info("🚀 تحليل إشارة Bybit باستخدام النظام المحسن...")
                    enhanced_result = enhanced_system.process_signal(user_id, signal_data)
                    logger.info(f"✅ نتيجة النظام المحسن في Bybit: {enhanced_result}")
                    
                    # إذا نجح النظام المحسن، نستخدم النتيجة ولكن نتابع التنفيذ العادي
                    if enhanced_result.get('status') == 'success':
                        logger.info("✅ تم استخدام نتيجة النظام المحسن في Bybit، نتابع التنفيذ العادي")
                        # نستخدم النتيجة المحسنة ولكن نتابع التنفيذ العادي
                        signal_data['enhanced_analysis'] = enhanced_result.get('analysis', {})
                        signal_data['enhanced_risk_assessment'] = enhanced_result.get('risk_assessment', {})
                        signal_data['enhanced_execution_plan'] = enhanced_result.get('execution_plan', {})
                    else:
                        logger.warning("⚠️ فشل النظام المحسن في Bybit، نعود للنظام العادي")
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في النظام المحسن في Bybit: {e}")
            
            action = signal_data.get('action', '').lower()
            symbol = signal_data.get('symbol', '')
            
            # 🔧 إصلاح: تعريف has_signal_id و signal_id في بداية الدالة
            has_signal_id = signal_data.get('has_signal_id', False)
            signal_id = signal_data.get('signal_id', '')
            
            # تحديد الفئة
            category = 'linear' if market_type == 'futures' else 'spot'
            
            logger.info(f"📡 Bybit {category.upper()}: {action} {symbol}")
            logger.info(f"🆔 Signal ID: {signal_id} (has_signal_id: {has_signal_id})")
            
            # تحديد جهة الأمر
            if action in ['buy', 'long']:
                side = 'Buy'
            elif action in ['sell', 'short']:
                side = 'Sell'
            elif action == 'close':
                # إغلاق الصفقة المفتوحة بالكامل
                if has_signal_id and signal_id:
                    # إغلاق الصفقات المرتبطة بالـ ID
                    return await SignalExecutor._close_signal_positions(
                        signal_id, user_id, symbol, account, category
                    )
                else:
                    # إغلاق الصفقات بالطريقة التقليدية
                    positions = account.get_open_positions(category)
                    
                    # البحث عن أي صفقة مفتوحة على هذا الرمز
                    target_position = next((p for p in positions if p['symbol'] == symbol), None)
                    
                    if target_position:
                        result = account.close_position(category, symbol, target_position['side'])
                        if result:
                            logger.info(f"✅ تم إغلاق صفقة {symbol} بالكامل بنجاح")
                            return {
                                'success': True,
                                'message': f'Position closed: {symbol}',
                                'order_id': result.get('order_id'),
                                'is_real': True
                            }
                    
                    return {
                        'success': False,
                        'message': f'No open position found for {symbol}',
                        'error': 'NO_POSITION'
                    }
            elif action == 'partial_close':
                # إغلاق جزئي للصفقة
                percentage = float(signal_data.get('percentage', 50))
                
                # التحقق من صحة النسبة
                if percentage <= 0 or percentage > 100:
                    return {
                        'success': False,
                        'message': f'Invalid percentage: {percentage}%. Must be between 1 and 100',
                    'error': 'INVALID_PERCENTAGE'
                }
                
                if has_signal_id and signal_id:
                    # إغلاق جزئي للصفقات المرتبطة بالـ ID
                    return await SignalExecutor._partial_close_signal_positions(
                        signal_id, user_id, symbol, percentage, account, category
                    )
                else:
                    # إغلاق جزئي بالطريقة التقليدية
                    positions = account.get_open_positions(category)
                    
                    # البحث عن أي صفقة مفتوحة على هذا الرمز
                    target_position = next((p for p in positions if p['symbol'] == symbol), None)
                    
                    if target_position:
                        # حساب الكمية المراد إغلاقها
                        current_qty = float(target_position.get('size', 0))
                        close_qty = current_qty * (percentage / 100)
                        
                        try:
                            # تنفيذ إغلاق جزئي عبر وضع أمر معاكس
                            opposite_side = 'Sell' if target_position['side'] == 'Buy' else 'Buy'
                            
                            result = account.place_order(
                                category=category,
                                symbol=symbol,
                                side=opposite_side,
                                order_type='Market',
                                qty=round(close_qty, 4),
                                reduce_only=True  # مهم: للإغلاق فقط
                            )
                            
                            if result:
                                logger.info(f"✅ تم إغلاق {percentage}% من صفقة {symbol} بنجاح")
                                return {
                                    'success': True,
                                    'message': f'Partial close: {percentage}% of {symbol}',
                                    'order_id': result.get('order_id'),
                                    'percentage': percentage,
                                    'is_real': True
                                }
                            else:
                                return {
                                    'success': False,
                                    'message': f'Failed to execute partial close',
                                    'error': 'PARTIAL_CLOSE_FAILED'
                                }
                        except Exception as e:
                            logger.error(f"❌ خطأ في الإغلاق الجزئي: {e}")
                            return {
                                'success': False,
                                'message': f'Error in partial close: {str(e)}',
                                'error': 'PARTIAL_CLOSE_ERROR'
                            }
                    
                    return {
                        'success': False,
                        'message': f'No open position found for {symbol}',
                        'error': 'NO_POSITION'
                    }
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'error': 'INVALID_ACTION'
                }
            
            # حساب الكمية بناءً على مبلغ التداول ونوع السوق
            # حساب الكمية - كود خفي للتحويل الذكي مع فحص الرافعة المالية
            # استخدام السعر الحقيقي من API بدلاً من القيمة الافتراضية
            try:
                current_price = account.get_ticker_price(symbol)
                price = float(current_price)
                logger.info(f"✅ تم جلب السعر الحقيقي: {price} USDT")
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب السعر الحقيقي: {e}")
                price = float(signal_data.get('price', 1))
                logger.warning(f"⚠️ استخدام السعر الافتراضي: {price}")
            
            # التحقق من أن السعر صحيح
            if price <= 0:
                logger.error(f"⚠️ سعر غير صحيح: {price}")
                return {
                    'success': False,
                    'message': f'Invalid price: {price}',
                    'is_real': True
                }
            
            # حساب الكمية مع ضمان عدم وجود قيم صغيرة جداً
            logger.info(f"=" * 80)
            logger.info(f"🧮 حساب الكمية:")
            logger.info(f"   market_type: {market_type}")
            logger.info(f"   trade_amount: {trade_amount} USDT")
            logger.info(f"   leverage: {leverage}x")
            logger.info(f"   price: {price}")
            
            if market_type == 'futures':
                qty = (trade_amount * leverage) / price
                notional_value = trade_amount * leverage
                logger.info(f"   ✅ Futures: qty = ({trade_amount} × {leverage}) / {price} = {qty}")
                logger.info(f"   ✅ notional_value = {trade_amount} × {leverage} = {notional_value}")
            else:
                # للسبوت بدون رافعة
                qty = trade_amount / price
                notional_value = trade_amount
                logger.info(f"   ✅ Spot: qty = {trade_amount} / {price} = {qty}")
                logger.info(f"   ✅ notional_value = {trade_amount}")
            
            # 🔧 تطبيق التعديل الذكي للكمية مباشرة
            logger.info(f"🧠 تطبيق التعديل الذكي للكمية...")
            exchange_name = getattr(account, 'exchange_name', 'bybit') if hasattr(account, 'exchange_name') else 'bybit'
            original_qty = qty
            qty = SignalExecutor._calculate_adjusted_quantity(qty, price, trade_amount, leverage, exchange_name)
            
            if qty != original_qty:
                logger.info(f"🔧 تم تعديل الكمية: {original_qty:.8f} → {qty:.8f}")
                # إعادة حساب القيمة الإجمالية
                if market_type == 'futures':
                    notional_value = qty * price / leverage
                else:
                    notional_value = qty * price
                logger.info(f"   القيمة الإجمالية المحدثة: {notional_value:.2f} USDT")
            
            logger.info(f"=" * 80)
            
            # 🔍 فحص رواية للرافعة المالية والمبلغ (كود ذكي للتحقق)
            # حساب الحد الأدنى المسموح به للفيوتشرز
            min_notional_for_leverage = 10.0  # الحد الأدنى من USDT
            
            if market_type == 'futures':
                # التحقق من أن الرافعة مناسبة للمبلغ
                if notional_value < min_notional_for_leverage:
                    logger.error(f"❌ الرافعة المالية لا تناسب المبلغ!")
                    logger.error(f"   المبلغ مع الرافعة ({leverage}x): {notional_value} USDT")
                    logger.error(f"   الحد الأدنى المطلوب: {min_notional_for_leverage} USDT")
                    return {
                        'success': False,
                        'message': f'الرافعة المالية لا تناسب المبلغ. الحد الأدنى: {min_notional_for_leverage} USDT',
                        'is_real': True,
                        'minimum_required': min_notional_for_leverage,
                        'current_value': notional_value
                    }
                else:
                    logger.info(f"✅ الرافعة المالية مناسبة: {notional_value} USDT (الحد الأدنى: {min_notional_for_leverage} USDT)")
            
            # التحقق من الحد الأدنى للقيمة
            if notional_value < min_notional_for_leverage:
                logger.error(f"❌ المبلغ أقل من المسموح")
                logger.error(f"   القيمة الحالية: {notional_value} USDT")
                logger.error(f"   الحد الأدنى المطلوب: {min_notional_for_leverage} USDT")
                return {
                    'success': False,
                    'message': f'المبلغ أقل من المسموح. الحد الأدنى: {min_notional_for_leverage} USDT',
                    'is_real': True,
                    'minimum_required': min_notional_for_leverage,
                    'current_value': notional_value
                }
            
            # 🔧 ملاحظة: التقريب الآن يتم في place_order بناءً على قواعد Bybit
            # لذلك نحتفظ بالكمية كما هي ونترك place_order يقوم بالتقريب الصحيح
            qty_was_adjusted = False  # سيتم التقريب في place_order
            
            logger.info(f"🧠 تحويل خفي Bybit: ${trade_amount} → {qty} {symbol.split('USDT')[0]} (السعر: ${price}, الرافعة: {leverage})")
            logger.info(f"📊 المدخلات (طريقتك): amount = ${trade_amount}")
            logger.info(f"📤 المخرجات (طريقة المنصة): qty = {qty} {symbol.split('USDT')[0]}")
            logger.info(f"📊 تم تعديل الكمية: {qty_was_adjusted}")
            
            # استخراج TP/SL إذا كانت موجودة
            take_profit = signal_data.get('take_profit')
            stop_loss = signal_data.get('stop_loss')
            
            if take_profit:
                take_profit = float(take_profit)
            if stop_loss:
                stop_loss = float(stop_loss)
            
            # تطبيق المنطق الجديد حسب نوع السوق
            if category == 'spot':
                # منطق السبوت: معاملة كمحفظة حقيقية
                result = await SignalExecutor._handle_spot_order(
                    account, signal_data, side, qty, price, market_type, user_id
                )
            else:
                # منطق الفيوتشر: تجميع حسب ID
                result = await SignalExecutor._handle_futures_order(
                    account, signal_data, side, qty, leverage, take_profit, stop_loss, market_type, user_id, 
                    qty_was_adjusted, trade_amount, price
                )
            
            # التحقق الفعلي من نجاح الصفقة
            if result and isinstance(result, dict) and result.get('order_id'):
                order_id_real = result.get('order_id')
                logger.info(f"✅ تم تنفيذ أمر {side} {symbol} على Bybit بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                logger.info(f"🆔 Order ID الحقيقي: {order_id_real}")
                
                # التحقق الفعلي من وجود الصفقة على Bybit
                found_position = None
                try:
                    # جلب الصفقات المفتوحة من Bybit
                    positions = account.get_open_positions('linear')
                    logger.info(f"🔍 جلب الصفقات المفتوحة من Bybit...")
                    
                    # البحث عن الصفقة الجديدة
                    for pos in positions:
                        if pos.get('symbol') == symbol and pos.get('side') == side:
                            found_position = pos
                            logger.info(f"✅ تم العثور على الصفقة على Bybit: {pos}")
                            break
                    
                    if found_position:
                        logger.info(f"✅ تأكيد حقيقي: الصفقة موجودة على Bybit")
                    else:
                        logger.warning(f"⚠️ تحذير: الصفقة قد لا تكون موجودة على Bybit بعد")
                        
                except Exception as e:
                    logger.error(f"❌ خطأ في التحقق من الصفقة على Bybit: {e}")
                
                # حفظ الصفقة في قاعدة البيانات إذا كان هناك ID
                if has_signal_id and signal_id:
                    try:
                        position_data = {
                            'signal_id': signal_id,
                            'user_id': user_id,
                            'symbol': symbol,
                            'side': side,
                            'entry_price': price,
                            'quantity': qty,
                            'exchange': 'bybit',
                            'market_type': market_type,
                            'order_id': result.get('order_id', ''),
                            'status': 'OPEN',
                            'notes': f'Created from signal {signal_id}'
                        }
                        
                        signal_position_manager.create_position(
                            signal_id=signal_id,
                            user_id=user_id,
                            symbol=symbol,
                            side=side,
                            entry_price=price,
                            quantity=qty,
                            exchange='bybit',
                            market_type=market_type,
                            order_id=result.get('order_id', '')
                        )
                        
                        logger.info(f"🆔 تم حفظ الصفقة المرتبطة بالـ ID: {signal_id}")
                    except Exception as e:
                        logger.error(f"❌ خطأ في حفظ الصفقة المرتبطة بالـ ID: {e}")
                
                return {
                    'success': True,
                    'message': f'Order placed: {side} {symbol}',
                    'order_id': order_id_real,
                    'symbol': symbol,
                    'side': side,
                    'qty': qty,
                    'is_real': True,
                    'signal_id': signal_id if has_signal_id else None,
                    'verified_on_bybit': found_position is not None
                }
            else:
                logger.error(f"❌ فشل تنفيذ أمر {side} {symbol} على Bybit")
                logger.error(f"❌ النتيجة: {result}")
                return {
                    'success': False,
                    'message': f'Failed to place order on Bybit - no valid order_id',
                    'error': 'ORDER_FAILED',
                    'result_details': result
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة Bybit: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': 'BYBIT_ERROR'
            }
    
    @staticmethod
    async def _close_signal_positions(signal_id: str, user_id: int, symbol: str, 
                                    account, category: str) -> Dict:
        """إغلاق الصفقات المرتبطة بالـ ID"""
        try:
            logger.info(f"🆔 إغلاق الصفقات المرتبطة بالـ ID: {signal_id} - {symbol}")
            
            # البحث عن الصفقات المرتبطة بالـ ID
            positions = signal_position_manager.find_positions_for_close(signal_id, user_id, symbol)
            
            if not positions:
                logger.warning(f"⚠️ لم يتم العثور على صفقات مرتبطة بالـ ID: {signal_id}")
                return {
                    'success': False,
                    'message': f'No positions found for signal ID: {signal_id}',
                    'error': 'NO_SIGNAL_POSITIONS'
                }
            
            closed_count = 0
            failed_count = 0
            
            for position in positions:
                try:
                    # إغلاق الصفقة على المنصة
                    result = account.close_position(category, symbol, position['side'])
                    
                    if result:
                        # تحديث حالة الصفقة في قاعدة البيانات
                        signal_position_manager.close_position(signal_id, user_id, symbol)
                        closed_count += 1
                        logger.info(f"✅ تم إغلاق صفقة مرتبطة بالـ ID: {signal_id}")
                    else:
                        failed_count += 1
                        logger.error(f"❌ فشل إغلاق صفقة مرتبطة بالـ ID: {signal_id}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ خطأ في إغلاق صفقة مرتبطة بالـ ID: {e}")
            
            if closed_count > 0:
                return {
                    'success': True,
                    'message': f'Closed {closed_count} positions for signal ID: {signal_id}',
                    'closed_count': closed_count,
                    'failed_count': failed_count,
                    'signal_id': signal_id,
                    'is_real': True
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to close any positions for signal ID: {signal_id}',
                    'closed_count': closed_count,
                    'failed_count': failed_count,
                    'error': 'CLOSE_FAILED'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقات المرتبطة بالـ ID: {e}")
            return {
                'success': False,
                'message': f'Error closing signal positions: {str(e)}',
                'error': 'CLOSE_ERROR'
            }
    
    @staticmethod
    async def _partial_close_signal_positions(signal_id: str, user_id: int, symbol: str,
                                            percentage: float, account, category: str) -> Dict:
        """إغلاق جزئي للصفقات المرتبطة بالـ ID"""
        try:
            logger.info(f"🆔 إغلاق جزئي {percentage}% للصفقات المرتبطة بالـ ID: {signal_id} - {symbol}")
            
            # البحث عن الصفقات المرتبطة بالـ ID
            positions = signal_position_manager.find_positions_for_close(signal_id, user_id, symbol)
            
            if not positions:
                logger.warning(f"⚠️ لم يتم العثور على صفقات مرتبطة بالـ ID: {signal_id}")
                return {
                    'success': False,
                    'message': f'No positions found for signal ID: {signal_id}',
                    'error': 'NO_SIGNAL_POSITIONS'
                }
            
            closed_count = 0
            failed_count = 0
            
            for position in positions:
                try:
                    # حساب الكمية المراد إغلاقها
                    current_qty = float(position['quantity'])
                    close_qty = current_qty * (percentage / 100)
                    
                    # تنفيذ إغلاق جزئي عبر وضع أمر معاكس
                    opposite_side = 'Sell' if position['side'] == 'Buy' else 'Buy'
                    
                    result = account.place_order(
                        category=category,
                        symbol=symbol,
                        side=opposite_side,
                        order_type='Market',
                        qty=round(close_qty, 4),
                        reduce_only=True  # مهم: للإغلاق فقط
                    )
                    
                    if result:
                        # تحديث الكمية المتبقية في قاعدة البيانات
                        remaining_qty = current_qty - close_qty
                        updates = {
                            'quantity': remaining_qty,
                            'notes': f'Partial close {percentage}% - Remaining: {remaining_qty}'
                        }
                        signal_position_manager.update_position(signal_id, user_id, symbol, updates)
                        
                        closed_count += 1
                        logger.info(f"✅ تم إغلاق جزئي {percentage}% من صفقة مرتبطة بالـ ID: {signal_id}")
                    else:
                        failed_count += 1
                        logger.error(f"❌ فشل الإغلاق الجزئي لصفقة مرتبطة بالـ ID: {signal_id}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ خطأ في الإغلاق الجزئي لصفقة مرتبطة بالـ ID: {e}")
            
            if closed_count > 0:
                return {
                    'success': True,
                    'message': f'Partial close {percentage}% of {closed_count} positions for signal ID: {signal_id}',
                    'closed_count': closed_count,
                    'failed_count': failed_count,
                    'percentage': percentage,
                    'signal_id': signal_id,
                    'is_real': True
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to partial close any positions for signal ID: {signal_id}',
                    'closed_count': closed_count,
                    'failed_count': failed_count,
                    'error': 'PARTIAL_CLOSE_FAILED'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في الإغلاق الجزئي للصفقات المرتبطة بالـ ID: {e}")
            return {
                'success': False,
                'message': f'Error partial closing signal positions: {str(e)}',
                'error': 'PARTIAL_CLOSE_ERROR'
            }
    
    @staticmethod
    async def _handle_spot_order(account, signal_data: Dict, side: str, qty: float, 
                                price: float, market_type: str, user_id: int) -> Dict:
        """معالجة أمر السبوت كمحفظة حقيقية"""
        try:
            symbol = signal_data.get('symbol', '')
            has_signal_id = signal_data.get('has_signal_id', False)
            signal_id = signal_data.get('signal_id', '')
            
            # في السبوت: الشراء يزيد الكمية، البيع يقلل الكمية
            if side.lower() == 'buy':
                # شراء: إضافة كمية للمحفظة
                result = account.place_order(
                    category='spot',
                    symbol=symbol,
                    side=side,
                    order_type='Market',
                    qty=round(qty, 4)
                )
                
                # معالجة محسنة للأخطاء
                if result is None:
                    logger.error(f"⚠️ فشل وضع الأمر Spot - استجابة فارغة")
                    return {
                        'success': False,
                        'message': f'Spot order placement failed - empty response',
                        'is_real': True,
                        'error_details': 'Empty response from Bybit Spot API'
                    }
                
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"⚠️ خطأ في Spot API: {result['error']}")
                    return {
                        'success': False,
                        'message': f'Spot API Error: {result["error"]}',
                        'is_real': True,
                        'error_details': result
                    }
                
                logger.info(f"✅ تم تنفيذ أمر Spot {side} {symbol} على Bybit بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                
                if result and has_signal_id and signal_id:
                    # حفظ في قاعدة البيانات كمحفظة
                    position_data = {
                        'signal_id': signal_id,
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': 'buy',
                        'entry_price': price,
                        'quantity': qty,
                        'exchange': 'bybit',
                        'market_type': 'spot',
                        'order_id': result.get('order_id', ''),
                        'status': 'OPEN',
                        'notes': f'Spot portfolio - buy {qty} {symbol}'
                    }
                    
                    from systems.enhanced_portfolio_manager import portfolio_factory
                    portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
                    portfolio_manager.add_position(position_data)
                    
            else:  # sell
                # بيع: تقليل كمية من المحفظة
                # التحقق من وجود رصيد كافي
                positions = account.get_open_positions('spot')
                symbol_position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if not symbol_position:
                    return {
                        'success': False,
                        'message': f'No {symbol} balance available for selling',
                        'error': 'INSUFFICIENT_BALANCE'
                    }
                
                available_qty = float(symbol_position.get('size', 0))
                if available_qty < qty:
                    return {
                        'success': False,
                        'message': f'Insufficient balance. Available: {available_qty}, Requested: {qty}',
                        'error': 'INSUFFICIENT_BALANCE'
                    }
                
                # تنفيذ البيع
                result = account.place_order(
                    category='spot',
                    symbol=symbol,
                    side=side,
                    order_type='Market',
                    qty=round(qty, 4)
                )
                
                # معالجة محسنة للأخطاء
                if result is None:
                    logger.error(f"⚠️ فشل وضع أمر Sell - استجابة فارغة")
                    return {
                        'success': False,
                        'message': f'Sell order placement failed - empty response',
                        'is_real': True,
                        'error_details': 'Empty response from Bybit Sell API'
                    }
                
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"⚠️ خطأ في Sell API: {result['error']}")
                    return {
                        'success': False,
                        'message': f'Sell API Error: {result["error"]}',
                        'is_real': True,
                        'error_details': result
                    }
                
                logger.info(f"✅ تم تنفيذ أمر Sell {side} {symbol} على Bybit بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                
                if result and has_signal_id and signal_id:
                    # تحديث المحفظة
                    position_data = {
                        'signal_id': signal_id,
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': 'sell',
                        'entry_price': price,
                        'quantity': qty,
                        'exchange': 'bybit',
                        'market_type': 'spot',
                        'order_id': result.get('order_id', ''),
                        'status': 'OPEN',
                        'notes': f'Spot portfolio - sell {qty} {symbol}'
                    }
                    
                    from systems.enhanced_portfolio_manager import portfolio_factory
                    portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
                    portfolio_manager.add_position(position_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة أمر السبوت: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': 'SPOT_ORDER_ERROR'
            }
    
    @staticmethod
    def _calculate_adjusted_quantity(qty: float, price: float, trade_amount: float, leverage: int, exchange: str = 'bybit') -> float:
        """
        حساب كمية معدلة عند فشل الصفقة بالتقريب الذكي
        
        Args:
            qty: الكمية الأصلية
            price: السعر الحالي
            trade_amount: المبلغ الأصلي
            leverage: الرافعة المالية
            exchange: اسم المنصة
            
        Returns:
            الكمية المعدلة
        """
        try:
            if QUANTITY_ADJUSTER_AVAILABLE:
                logger.info(f"🧮 بدء التعديل الذكي للكمية:")
                logger.info(f"   المدخلات: qty={qty}, price={price}, amount={trade_amount}, leverage={leverage}, exchange={exchange}")
                
                # استخدام التعديل الذكي الجديد
                adjusted = QuantityAdjuster.smart_quantity_adjustment(
                    qty=qty,
                    price=price,
                    trade_amount=trade_amount,
                    leverage=leverage,
                    exchange=exchange
                )
                
                logger.info(f"✅ التقريب التلقائي المحسن: {qty:.8f} → {adjusted:.8f}")
                return adjusted
            else:
                raise ImportError("QuantityAdjuster not available")
            
        except (ImportError, Exception):
            logger.warning("⚠️ لم يتم العثور على أداة التعديل الذكية، استخدام الطريقة القديمة")
            # الطريقة القديمة كبديل
            if qty < 0.001:
                adjusted = round(qty, 5)
            elif qty < 0.01:
                adjusted = round(qty, 4)
            elif qty < 0.1:
                adjusted = round(qty, 3)
            elif qty < 1:
                adjusted = round(qty, 2)
            else:
                adjusted = round(qty, 1)
            
            logger.info(f"🧮 التقريب التلقائي (قديم): {qty:.8f} → {adjusted:.8f}")
            return adjusted
            
        except Exception as e:
            logger.error(f"❌ خطأ في التعديل الذكي: {e}")
            # العودة للطريقة القديمة في حالة الخطأ
            adjusted = round(qty, 4)
            logger.info(f"🧮 التقريب الاحتياطي: {qty:.8f} → {adjusted:.8f}")
            return adjusted
    
    @staticmethod
    async def _try_multiple_quantities(account, symbol: str, side: str, original_qty: float, 
                                     price: float, leverage: int, take_profit: float, 
                                     stop_loss: float, exchange: str = 'bybit') -> Optional[Dict]:
        """
        محاولة تنفيذ الطلب مع خيارات كمية متعددة
        
        Args:
            account: حساب التداول
            symbol: رمز العملة
            side: اتجاه التداول
            original_qty: الكمية الأصلية
            price: السعر
            leverage: الرافعة المالية
            take_profit: جني الأرباح
            stop_loss: وقف الخسارة
            exchange: اسم المنصة
            
        Returns:
            نتيجة الطلب الناجح أو None
        """
        try:
            if not QUANTITY_ADJUSTER_AVAILABLE:
                logger.warning("⚠️ أداة التعديل الذكية غير متاحة للمحاولات المتعددة")
                return None
            
            # الحصول على خيارات كمية متعددة
            quantity_options = QuantityAdjuster.get_multiple_quantity_options(
                original_qty, price, exchange
            )
            
            logger.info(f"🎯 محاولة {len(quantity_options)} خيارات كمية: {quantity_options}")
            
            for i, qty_option in enumerate(quantity_options):
                try:
                    logger.info(f"🔄 المحاولة {i+1}/{len(quantity_options)}: كمية = {qty_option}")
                    
                    # التحقق من صحة الكمية قبل المحاولة
                    validation = QuantityAdjuster.validate_quantity(qty_option, price, exchange)
                    if not validation['valid']:
                        logger.warning(f"⚠️ الكمية {qty_option} غير صالحة: {validation['errors']}")
                        continue
                    
                    # محاولة تنفيذ الطلب
                    result = await account.place_order(
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=qty_option,
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                    if result and not result.get('error'):
                        logger.info(f"✅ نجحت المحاولة {i+1} بالكمية {qty_option}")
                        result['adjustment_message'] = f'تم تعديل الكمية بعد محاولات متعددة: {original_qty:.6f} → {qty_option:.6f}'
                        result['final_qty'] = qty_option
                        result['attempts_made'] = i + 1
                        return result
                    else:
                        error_msg = result.get('message', 'Unknown error') if result else 'No result'
                        logger.warning(f"⚠️ المحاولة {i+1} فشلت: {error_msg}")
                        
                except Exception as attempt_error:
                    logger.warning(f"⚠️ خطأ في المحاولة {i+1}: {attempt_error}")
                    continue
            
            logger.error(f"❌ فشلت جميع المحاولات ({len(quantity_options)} محاولة)")
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في المحاولات المتعددة: {e}")
            return None
    
    @staticmethod
    async def _handle_futures_order(account, signal_data: Dict, side: str, qty: float,
                                   leverage: int, take_profit: float, stop_loss: float,
                                   market_type: str, user_id: int, qty_was_adjusted: bool = False,
                                   trade_amount: float = 0, price: float = 0) -> Dict:
        """معالجة أمر الفيوتشر مع تجميع حسب ID"""
        try:
            symbol = signal_data.get('symbol', '')
            has_signal_id = signal_data.get('has_signal_id', False)
            signal_id = signal_data.get('signal_id', '')
            
            # إنشاء ID عشوائي إذا لم يكن موجوداً
            if not signal_id:
                signal_id = SignalExecutor._generate_random_id(symbol)
                logger.info(f"تم إنشاء ID عشوائي للفيوتشر: {signal_id}")
            
            # البحث عن صفقة موجودة بنفس ID
            from users.database import db_manager
            existing_position = db_manager.get_position_by_signal_id(signal_id, user_id, symbol)
            
            if existing_position:
                # تجميع الصفقات بنفس ID
                if side.lower() == 'buy' and existing_position['side'].lower() == 'buy':
                    # تعزيز Long - زيادة الكمية
                    new_qty = existing_position['quantity'] + qty
                    result = account.place_order(
                        category='linear',
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 4),  # الكمية الإضافية فقط
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                elif side.lower() == 'sell' and existing_position['side'].lower() == 'sell':
                    # تعزيز Short - زيادة الكمية
                    new_qty = existing_position['quantity'] + qty
                    result = account.place_order(
                        category='linear',
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 4),  # الكمية الإضافية فقط
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                else:
                    # اتجاه معاكس - إنشاء صفقة منفصلة
                    result = account.place_order(
                        category='linear',
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 4),
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
            else:
                # صفقة جديدة - تنفيذ مباشر بالكمية المعدلة
                logger.info(f"=" * 80)
                logger.info(f"🚀 تنفيذ الصفقة:")
                logger.info(f"   qty: {qty}")
                logger.info(f"   leverage: {leverage}x")
                logger.info(f"=" * 80)
                
                # تنفيذ الصفقة مرة واحدة بالكمية المعدلة
                try:
                    result = account.place_order(
                        category='linear',
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 4),
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                    logger.info(f"🔍 نتيجة تنفيذ الصفقة: {result}")
                    
                    # 🔧 التحقق من وجود أخطاء في النتيجة
                    if result is None:
                        logger.error(f"❌ فشل في تنفيذ الصفقة - النتيجة فارغة")
                        return {
                            'success': False,
                            'message': 'Failed to execute order - empty response',
                            'error': 'ORDER_EXECUTION_EMPTY'
                        }
                    
                    if isinstance(result, dict) and result.get('error'):
                        logger.error(f"❌ خطأ في تنفيذ الصفقة - خطأ من API")
                        error_type = result.get('error_type', 'UNKNOWN')
                        error_msg = result.get('message', result.get('retMsg', 'Unknown error'))
                        error_code = result.get('retCode', '')
                        
                        # معالجة خاصة لأخطاء الكمية
                        if 'minimum' in error_msg.lower() or 'exceeds' in error_msg.lower() or 'limit' in error_msg.lower():
                            logger.warning(f"🔄 محاولة إعادة حساب الكمية بسبب خطأ الحد الأدنى")
                            
                            # إعادة حساب الكمية بطريقة أكثر دقة
                            # تحديد اسم المنصة من الحساب
                            exchange_name = getattr(account, 'exchange_name', 'bybit') if hasattr(account, 'exchange_name') else 'bybit'
                            adjusted_qty = SignalExecutor._calculate_adjusted_quantity(qty, price, trade_amount, leverage, exchange_name)
                            
                            if adjusted_qty != qty and adjusted_qty > 0:
                                logger.info(f"🔧 إعادة المحاولة بكمية معدلة: {qty} → {adjusted_qty}")
                                
                                # محاولة ثانية بالكمية المعدلة
                                try:
                                    result = await account.place_order(
                                        symbol=symbol,
                                        side=side,
                                        order_type='Market',
                                        qty=adjusted_qty,
                                        leverage=leverage,
                                        take_profit=take_profit,
                                        stop_loss=stop_loss
                                    )
                                    
                                    if result and not result.get('error'):
                                        logger.info(f"✅ نجحت المحاولة الثانية بالكمية المعدلة")
                                        result['adjustment_message'] = f'تم تعديل الكمية تلقائياً: {qty:.6f} → {adjusted_qty:.6f}'
                                        # تحديث qty للاستخدام في باقي الكود
                                        qty = adjusted_qty
                                        # استمرار التنفيذ العادي
                                    else:
                                        # محاولة مع خيارات كمية متعددة
                                        logger.warning(f"🔄 المحاولة الثانية فشلت، جرب خيارات متعددة")
                                        success = await SignalExecutor._try_multiple_quantities(
                                            account, symbol, side, qty, price, leverage, 
                                            take_profit, stop_loss, exchange_name
                                        )
                                        
                                        if success:
                                            result = success
                                            qty = success.get('final_qty', qty)
                                            logger.info(f"✅ نجحت إحدى المحاولات المتعددة")
                                        else:
                                            logger.error(f"❌ فشلت جميع المحاولات")
                                            return {
                                                'success': False,
                                                'message': f'فشل في تنفيذ الصفقة حتى بعد محاولات متعددة: {error_msg}',
                                                'error': 'ALL_QUANTITY_ATTEMPTS_FAILED',
                                                'original_qty': qty,
                                                'adjusted_qty': adjusted_qty
                                            }
                                except Exception as retry_error:
                                    logger.error(f"❌ خطأ في المحاولة الثانية: {retry_error}")
                                    return {
                                        'success': False,
                                        'message': f'فشل في إعادة المحاولة: {str(retry_error)}',
                                        'error': 'RETRY_FAILED'
                                    }
                            else:
                                return {
                                    'success': False,
                                    'message': f'لا يمكن تعديل الكمية لحل المشكلة: {error_msg}',
                                    'error': 'QUANTITY_CANNOT_BE_ADJUSTED',
                                    'original_qty': qty
                                }
                        
                        # تحديد رسالة خطأ مناسبة للأخطاء الأخرى
                        if error_type in ['INVALID_API_KEY', 'EMPTY_RESPONSE']:
                            return {
                                'success': False,
                                'message': f'API Error: {error_msg}',
                                'error': error_type,
                                'help': 'Please check your API keys and permissions in settings'
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'Order execution failed: {error_msg}',
                                'error': error_type,
                                'details': result
                            }
                    
                except Exception as order_error:
                    logger.error(f"❌ خطأ في تنفيذ الصفقة: {order_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    error_msg = str(order_error)
                    
                    # معالجة خطأ API key invalid
                    if 'invalid' in error_msg.lower() or 'API key' in error_msg or '10001' in error_msg:
                        return {
                            'success': False,
                            'message': 'API key is invalid. Please check your API credentials in settings.',
                            'error': 'INVALID_API_CREDENTIALS',
                            'help': 'Go to Settings > Real Account Setup and update your API keys'
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Failed to execute order: {error_msg}',
                            'error': 'ORDER_EXECUTION_FAILED'
                        }
                
                # إذا تم تعديل الكمية، أضف رسالة للمستخدم
                if qty_was_adjusted and result and isinstance(result, dict) and result.get('order_id'):
                    effective_amount = (qty * price) / leverage
                    logger.info(f"📢 تم تنفيذ الصفقة بالتقريب التلقائي")
                    logger.info(f"   المبلغ الأصلي: ${trade_amount}")
                    logger.info(f"   المبلغ الفعلي: ${effective_amount:.2f}")
                    # سيتم إضافة هذه الرسالة في النتيجة
                    result['adjustment_message'] = f'تم تنفيذ الصفقة بالتقريب التلقائي: ${trade_amount} → ${effective_amount:.2f}'
                
                # التحقق من وجود order_id
                if result and isinstance(result, dict) and result.get('order_id'):
                    logger.info(f"✅ تم إنشاء order_id بنجاح: {result.get('order_id')}")
                    logger.info(f"📋 تفاصيل الأمر الكاملة: {result}")
                else:
                    logger.error(f"❌ فشل تنفيذ الصفقة")
                    logger.error(f"   النتيجة: {result}")
                    return {
                        'success': False,
                        'message': f'Order placement failed',
                        'is_real': True,
                        'error_details': f'Failed result: {result}'
                    }
            
                # 🔧 التحقق من وجود أخطاء في النتيجة قبل معالجة order_id
                if result is None:
                    logger.error(f"❌ فشل تنفيذ الصفقة - النتيجة None")
                    return {
                        'success': False,
                        'message': 'Order placement failed - empty response',
                        'is_real': True,
                        'error_details': 'Empty result'
                    }
                
                # التحقق من وجود خطأ في النتيجة
                if isinstance(result, dict) and result.get('error'):
                    logger.error(f"❌ خطأ من API في نتيجة الصفقة:")
                    logger.error(f"   Details: {result}")
                    
                    error_type = result.get('error_type', 'UNKNOWN')
                    error_msg = result.get('message', result.get('retMsg', 'Unknown error'))
                    
                    return {
                        'success': False,
                        'message': f'Order placement failed: {error_msg}',
                        'is_real': True,
                        'error_details': result
                    }
                
                # التحقق النهائي من النجاح قبل الإرجاع
            if not result or not isinstance(result, dict) or not result.get('order_id'):
                logger.error(f"❌ فشل تنفيذ الصفقة - لا يوجد order_id")
                logger.error(f"   النتيجة: {result}")
                
                # تحليل نوع الخطأ
                error_msg = ""
                if isinstance(result, dict):
                    if result.get('error'):
                        error_msg = result.get('message', 'Unknown error')
                        error_type = result.get('error_type', 'UNKNOWN')
                    elif result.get('retCode') is not None:
                        # خطأ من Bybit API
                        ret_code = result.get('retCode')
                        ret_msg = result.get('retMsg', 'Unknown error')
                        
                        if ret_code == 10001:
                            error_msg = "API key is invalid"
                        elif ret_code == 10004:
                            error_msg = "Insufficient balance"
                        elif ret_code == 10005:
                            error_msg = "Permission denied"
                        else:
                            error_msg = f"Bybit error ({ret_code}): {ret_msg}"
                    else:
                        error_msg = str(result)
                else:
                    error_msg = str(result) if result else "Empty result"
                
                return {
                    'success': False,
                    'message': f'Order placement failed: {error_msg}',
                    'is_real': True,
                    'error_details': result if result else 'Empty result'
                }
            
            # حفظ الصفقة في قاعدة البيانات
            if result and has_signal_id:
                position_data = {
                    'signal_id': signal_id,
                    'user_id': user_id,
                    'symbol': symbol,
                    'side': side,
                    'entry_price': signal_data.get('price', 0),
                    'quantity': qty,
                    'exchange': 'bybit',
                    'market_type': 'futures',
                    'order_id': result.get('order_id', ''),
                    'status': 'OPEN',
                    'notes': f'Futures position - {side} {qty} {symbol} (ID: {signal_id})'
                }
                
                from systems.enhanced_portfolio_manager import portfolio_factory
                portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
                portfolio_manager.add_position(position_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة أمر الفيوتشر: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': 'FUTURES_ORDER_ERROR'
            }
    
    @staticmethod
    def _generate_random_id(symbol: str) -> str:
        """إنشاء ID عشوائي للصفقة"""
        import random
        import string
        from datetime import datetime
        
        # صيغة: SYMBOL-YYYYMMDD-HHMMSS-RAND4
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{symbol}-{timestamp}-{random_part}"


# مثيل عام
signal_executor = SignalExecutor()

