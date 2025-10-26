#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
from typing import Dict, Optional
from real_account_manager import real_account_manager
from signal_position_manager import signal_position_manager

logger = logging.getLogger(__name__)

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
    from simple_enhanced_system import SimpleEnhancedSystem
    ENHANCED_SYSTEM_AVAILABLE = True
    print("✅ النظام المحسن متاح في signal_executor.py")
except ImportError as e:
    ENHANCED_SYSTEM_AVAILABLE = False
    print(f"⚠️ النظام المحسن غير متاح في signal_executor.py: {e}")

# استيراد مدير معرفات الإشارات
try:
    from signal_id_manager import get_position_id_from_signal, get_signal_id_manager
    SIGNAL_ID_MANAGER_AVAILABLE = True
    print("✅ مدير معرفات الإشارات متاح في signal_executor.py")
except ImportError as e:
    SIGNAL_ID_MANAGER_AVAILABLE = False
    print(f"⚠️ مدير معرفات الإشارات غير متاح في signal_executor.py: {e}")

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
                return {
                    'success': False,
                    'message': 'Real account not activated',
                    'error': 'ACCOUNT_NOT_FOUND'
                }
            
            # تحويل الإشارة إذا كانت بالتنسيق الجديد
            from signal_converter import convert_simple_signal
            
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
                    
                    if exchange == 'bybit':
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
                    else:
                        # جلب السعر من MEXC
                        logger.info(f"🔍 جلب السعر من MEXC لـ {symbol}...")
                        try:
                            price_result = real_account.get_ticker('spot', symbol)
                            if price_result and 'lastPrice' in price_result:
                                price = float(price_result['lastPrice'])
                                logger.info(f"✅ السعر الحالي من MEXC: {price}")
                            else:
                                logger.error(f"❌ فشل جلب السعر من MEXC")
                                return {
                                    'success': False,
                                    'message': f'Failed to get current price for {symbol} from MEXC',
                                    'error': 'PRICE_FETCH_FAILED'
                                }
                        except Exception as e:
                            logger.error(f"❌ خطأ في جلب السعر من MEXC: {e}")
                            return {
                                'success': False,
                                'message': f'Error fetching price from MEXC: {e}',
                                'error': 'PRICE_FETCH_ERROR'
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
            elif exchange == 'mexc':
                result = await SignalExecutor._execute_mexc_signal(
                    real_account, signal_data, trade_amount, user_id
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
            price = float(signal_data.get('price', 1))
            
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
            
            # ضمان الحد الأدنى للكمية (تجنب رفض المنصة)
            min_quantity = 0.0001  # الحد الأدنى المقبول
            if qty < min_quantity:
                logger.warning(f"⚠️ الكمية صغيرة جداً: {qty}, تم تعديلها إلى الحد الأدنى")
                qty = min_quantity
            
            # 🧠 كود ذكي عالمي: تقريب الكمية لأقرب قيمة صالحة لأي مبلغ/زوج/رافعة
            # يضمن أن المبلغ النهائي قريب من المبلغ المحدد تلقائياً
            
            # تحديد دقة التقريب حسب حجم الكمية (يعمل مع أي زوج وأي رافعة)
            if qty >= 1000:
                # للكميات الضخمة: تقريب لـ 0 خانات عشرية
                rounded_qty = round(qty)
            elif qty >= 100:
                # للكميات الكبيرة: تقريب لـ 1 خانة عشرية
                rounded_qty = round(qty, 1)
            elif qty >= 10:
                # للكميات المتوسطة: تقريب لـ 2 خانات عشرية
                rounded_qty = round(qty, 2)
            elif qty >= 1:
                # للكميات المتوسطة-الصغيرة: تقريب لـ 3 خانات عشرية
                rounded_qty = round(qty, 3)
            elif qty >= 0.1:
                # للكميات الصغيرة: تقريب لـ 4 خانات عشرية
                rounded_qty = round(qty, 4)
            elif qty >= 0.01:
                # للكميات الصغيرة جداً: تقريب لـ 5 خانات عشرية
                rounded_qty = round(qty, 5)
            elif qty >= 0.001:
                # للكميات الصغيرة جداً جداً (مثل BTC/ETH): تقريب لـ 6 خانات عشرية
                rounded_qty = round(qty, 6)
            else:
                # للكميات الضئيلة: تقريب لـ 8 خانات عشرية
                rounded_qty = round(qty, 8)
            
            # إذا تم التعديل، نحسب المبلغ الفعلي بعد التقريب
            logger.info(f"=" * 80)
            logger.info(f"🧠 تقريب ذكي عالمي:")
            logger.info(f"   الكمية الأصلية: {qty:.8f}")
            logger.info(f"   الكمية بعد التقريب: {rounded_qty:.8f}")
            
            if abs(rounded_qty - qty) > 0.00000001:
                # حساب المبلغ الفعلي بعد التقريب
                if market_type == 'futures':
                    effective_amount = (rounded_qty * price) / leverage
                else:
                    effective_amount = rounded_qty * price
                
                logger.info(f"   ✅ تم التقريب")
                logger.info(f"   📊 المبلغ الأصلي: ${trade_amount}")
                logger.info(f"   📊 المبلغ بعد التقريب: ${effective_amount:.2f}")
                logger.info(f"   📊 نسبة التقريب: {(effective_amount/trade_amount)*100:.1f}%")
                qty = rounded_qty
            else:
                # لا حاجة لتعديل - الكمية بالفعل مقربة بشكل صحيح
                logger.info(f"   ⚠️ لا حاجة للتقريب - الكمية بالفعل صحيحة")
                qty = rounded_qty
            
            logger.info(f"=" * 80)
            
            logger.info(f"🧠 تحويل خفي Bybit: ${trade_amount} → {qty} {symbol.split('USDT')[0]} (السعر: ${price}, الرافعة: {leverage})")
            logger.info(f"📊 المدخلات (طريقتك): amount = ${trade_amount}")
            logger.info(f"📤 المخرجات (طريقة المنصة): qty = {qty} {symbol.split('USDT')[0]}")
            
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
                    account, signal_data, side, qty, leverage, take_profit, stop_loss, market_type, user_id
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
    async def _execute_mexc_signal(account, signal_data: Dict, trade_amount: float, user_id: int) -> Dict:
        """تنفيذ إشارة على MEXC (Spot فقط)"""
        try:
            # استخدام النظام المحسن إذا كان متاحاً
            if ENHANCED_SYSTEM_AVAILABLE:
                try:
                    enhanced_system = SimpleEnhancedSystem()
                    logger.info("🚀 تحليل إشارة MEXC باستخدام النظام المحسن...")
                    enhanced_result = enhanced_system.process_signal(user_id, signal_data)
                    logger.info(f"✅ نتيجة النظام المحسن في MEXC: {enhanced_result}")
                    
                    # إذا نجح النظام المحسن، نستخدم النتيجة ولكن نتابع التنفيذ العادي
                    if enhanced_result.get('status') == 'success':
                        logger.info("✅ تم استخدام نتيجة النظام المحسن في MEXC، نتابع التنفيذ العادي")
                        # نستخدم النتيجة المحسنة ولكن نتابع التنفيذ العادي
                        signal_data['enhanced_analysis'] = enhanced_result.get('analysis', {})
                        signal_data['enhanced_risk_assessment'] = enhanced_result.get('risk_assessment', {})
                        signal_data['enhanced_execution_plan'] = enhanced_result.get('execution_plan', {})
                    else:
                        logger.warning("⚠️ فشل النظام المحسن في MEXC، نعود للنظام العادي")
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في النظام المحسن في MEXC: {e}")
            
            action = signal_data.get('action', '').lower()
            symbol = signal_data.get('symbol', '')
            
            logger.info(f"📡 MEXC SPOT: {action} {symbol}")
            
            # تحديد جهة الأمر
            if action in ['buy', 'long']:
                side = 'BUY'
            elif action in ['sell', 'short', 'close']:
                side = 'SELL'
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'error': 'INVALID_ACTION'
                }
            
            # حساب الكمية - كود خفي للتحويل الذكي
            price = float(signal_data.get('price', 1))
            
            # التحقق من أن السعر صحيح
            if price <= 0:
                logger.error(f"⚠️ سعر غير صحيح: {price}")
                return {
                    'success': False,
                    'message': f'Invalid price: {price}',
                    'is_real': True
                }
            
            # حساب الكمية مع ضمان عدم وجود قيم صغيرة جداً
            quantity = trade_amount / price
            
            # ضمان الحد الأدنى للكمية (تجنب رفض المنصة)
            min_quantity = 0.0001  # الحد الأدنى المقبول
            if quantity < min_quantity:
                logger.warning(f"⚠️ الكمية صغيرة جداً: {quantity}, تم تعديلها إلى الحد الأدنى")
                quantity = min_quantity
            
            # تقريب الكمية حسب دقة الرمز
            quantity = round(quantity, 6)
            
            logger.info(f"🧠 تحويل خفي: ${trade_amount} → {quantity} {symbol.split('USDT')[0]} (السعر: ${price})")
            logger.info(f"📊 المدخلات (طريقتك): amount = ${trade_amount}")
            logger.info(f"📤 المخرجات (طريقة المنصة): quantity = {quantity} {symbol.split('USDT')[0]}")
            
            # وضع الأمر
            logger.info(f"🔄 تنفيذ أمر MEXC: {side} {quantity} {symbol}")
            result = account.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type='MARKET'
            )
            
            # معالجة محسنة للأخطاء
            if result is None:
                logger.error(f"⚠️ فشل وضع الأمر - استجابة فارغة")
                return {
                    'success': False,
                    'message': f'Order placement failed - empty response',
                    'is_real': True,
                    'error_details': 'Empty response from MEXC API'
                }
            
            if isinstance(result, dict) and 'error' in result:
                logger.error(f"⚠️ خطأ في API: {result['error']}")
                return {
                    'success': False,
                    'message': f'API Error: {result["error"]}',
                    'is_real': True,
                    'error_details': result
                }
            
            # إذا وصلنا هنا، فالأمر نجح
            logger.info(f"✅ تم تنفيذ أمر {side} {symbol} على MEXC بنجاح")
            logger.info(f"📋 تفاصيل الأمر: {result}")
            
            # التحقق من وجود order_id في النتيجة
            order_id = result.get('order_id') or result.get('orderId')
            
            return {
                'success': True,
                'message': f'Order placed: {side} {symbol}',
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'qty': quantity,
                'is_real': True,
                'mexc_response': result  # إضافة الاستجابة الكاملة للتشخيص
            }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة MEXC: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': 'MEXC_ERROR'
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
                    
                    from enhanced_portfolio_manager import portfolio_factory
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
                    
                    from enhanced_portfolio_manager import portfolio_factory
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
    def _calculate_adjusted_quantity(qty: float, price: float, trade_amount: float, leverage: int) -> float:
        """
        حساب كمية معدلة عند فشل الصفقة بالتقريب الذكي
        
        Args:
            qty: الكمية الأصلية
            price: السعر الحالي
            trade_amount: المبلغ الأصلي
            leverage: الرافعة المالية
            
        Returns:
            الكمية المعدلة
        """
        # تقريب الكمية بناءً على حجمها
        if qty < 0.001:
            # أرقام صغيرة جداً: تقريب لـ 5 منازل عشرية
            adjusted = round(qty, 5)
        elif qty < 0.01:
            # أرقام صغيرة: تقريب لـ 4 منازل عشرية
            adjusted = round(qty, 4)
        elif qty < 0.1:
            # أرقام متوسطة: تقريب لـ 3 منازل عشرية
            adjusted = round(qty, 3)
        elif qty < 1:
            # أرقام كبيرة نسبياً: تقريب لـ 2 منزل عشري
            adjusted = round(qty, 2)
        else:
            # أرقام كبيرة جداً: تقريب لـ 1 منزل عشري
            adjusted = round(qty, 1)
        
        logger.info(f"🧮 التقريب التلقائي: {qty:.8f} → {adjusted:.8f}")
        return adjusted
    
    @staticmethod
    async def _handle_futures_order(account, signal_data: Dict, side: str, qty: float,
                                   leverage: int, take_profit: float, stop_loss: float,
                                   market_type: str, user_id: int) -> Dict:
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
            from database import db_manager
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
                # صفقة جديدة - مع آلية التقريب التلقائي
                logger.info(f"=" * 80)
                logger.info(f"🚀 المحاولة الأولى - الكمية الأصلية:")
                logger.info(f"   qty: {qty}")
                logger.info(f"=" * 80)
                
                # المحاولة الأولى بالكمية الأصلية
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
                
                logger.info(f"🔍 نتيجة المحاولة الأولى: {result}")
                
                # التحقق من الفشل
                if result is None or not isinstance(result, dict) or not result.get('order_id'):
                    logger.warning(f"⚠️ فشلت المحاولة الأولى - جاري المحاولة بالتقريب التلقائي...")
                    
                    # الحصول على السعر والمبلغ من signal_data
                    price = signal_data.get('price', 0)
                    trade_amount = signal_data.get('amount', 0)
                    
                    # محاولة ثانية مع تقريب الكمية
                    adjusted_qty = SignalExecutor._calculate_adjusted_quantity(qty, price, trade_amount, leverage)
                    
                    logger.info(f"=" * 80)
                    logger.info(f"🔄 المحاولة الثانية - الكمية المعدلة:")
                    logger.info(f"   qty_original: {qty}")
                    logger.info(f"   qty_adjusted: {adjusted_qty}")
                    logger.info(f"=" * 80)
                    
                    result = account.place_order(
                        category='linear',
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(adjusted_qty, 4),
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                    logger.info(f"🔍 نتيجة المحاولة الثانية: {result}")
                    
                    # إذا نجحت المحاولة الثانية، ارسل رسالة للمستخدم
                    if result and isinstance(result, dict) and result.get('order_id'):
                        effective_amount = (adjusted_qty * price) / leverage
                        logger.info(f"✅ نجحت المحاولة الثانية بالتقريب التلقائي")
                        logger.info(f"📢 رسالة للمستخدم: تم تنفيذ الصفقة بالتقريب التلقائي")
                        logger.info(f"   المبلغ الأصلي: ${trade_amount}")
                        logger.info(f"   المبلغ الفعلي: ${effective_amount:.2f}")
                        logger.info(f"   الكمية المعدلة: {adjusted_qty}")
                
                # التحقق من وجود order_id
                if result and isinstance(result, dict) and result.get('order_id'):
                    logger.info(f"✅ تم إنشاء order_id بنجاح: {result.get('order_id')}")
                    logger.info(f"📋 تفاصيل الأمر الكاملة: {result}")
                else:
                    logger.error(f"❌ فشلت جميع المحاولات")
                    logger.error(f"   النتيجة: {result}")
                    return {
                        'success': False,
                        'message': f'Order placement failed after auto-adjustment',
                        'is_real': True,
                        'error_details': f'Failed result: {result}'
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
                
                from enhanced_portfolio_manager import portfolio_factory
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

