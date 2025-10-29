#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from api.bybit_api import real_account_manager
from signals import signal_position_manager

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
                return {
                    'success': False,
                    'message': 'Real account not activated',
                    'error': 'ACCOUNT_NOT_FOUND'
                }
            
            # تحويل الإشارة إذا كانت بالتنسيق الجديد
            from signals.signal_converter import convert_simple_signal
            
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
            
            # إرسال رسالة فشل للمستخدم
            try:
                await SignalExecutor._send_error_notification(user_id, str(e), signal_data)
            except Exception as notify_error:
                logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
            
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
            
            # حساب الكمية الأصلية
            logger.info(f"💰 حساب الكمية:")
            logger.info(f"   المبلغ: ${trade_amount}")
            logger.info(f"   الرافعة: {leverage}x")
            logger.info(f"   السعر: ${price}")
            logger.info(f"   الكمية الأصلية: {qty:.8f}")
            
            # تطبيق التقريب الذكي مباشرة لضمان قبول المنصة
            logger.info(f"🧠 تطبيق التقريب الذكي المحسن...")
            final_qty = SignalExecutor._smart_quantity_rounding(
                qty, price, trade_amount, leverage, market_type, symbol
            )
            
            # فحص إضافي للرصيد (مستوحى من الملفات المرفقة)
            if final_qty < qty * 0.5:  # إذا كان التقريب قلل الكمية بأكثر من 50%
                logger.warning(f"⚠️ التقريب قلل الكمية بشكل كبير: {qty:.8f} → {final_qty:.8f}")
                
                # فحص الرصيد المتاح لضمان إمكانية التنفيذ
                try:
                    balance_info = account.get_wallet_balance('unified')
                    if balance_info and 'list' in balance_info:
                        usdt_balance = next((coin for coin in balance_info['list'] if coin['coin'] == 'USDT'), None)
                        if usdt_balance:
                            available_balance = float(usdt_balance.get('walletBalance', 0))
                            required_margin = (final_qty * price) / leverage if market_type == 'futures' else final_qty * price
                            
                            logger.info(f"💰 فحص الرصيد: متاح={available_balance:.2f}, مطلوب={required_margin:.2f}")
                            
                            if available_balance < required_margin:
                                logger.error(f"❌ رصيد غير كافي للكمية المقربة")
                                return {
                                    'success': False,
                                    'message': f'رصيد غير كافي. متاح: {available_balance:.2f} USDT، مطلوب: {required_margin:.2f} USDT',
                                    'error': 'INSUFFICIENT_BALANCE_AFTER_ROUNDING',
                                    'is_real': True,
                                    'available_balance': available_balance,
                                    'required_balance': required_margin
                                }
                except Exception as e:
                    logger.warning(f"⚠️ لم يتم فحص الرصيد: {e}")
            
            # حساب التأثير المالي
            if market_type == 'futures':
                original_amount = (qty * price) / leverage
                final_amount = (final_qty * price) / leverage
            else:
                original_amount = qty * price
                final_amount = final_qty * price
            
            impact_percentage = ((final_amount - original_amount) / original_amount) * 100 if original_amount > 0 else 0
            
            logger.info(f"✅ النتيجة النهائية:")
            logger.info(f"   الكمية النهائية: {final_qty:.8f}")
            logger.info(f"   المبلغ الأصلي: ${original_amount:.2f}")
            logger.info(f"   المبلغ النهائي: ${final_amount:.2f}")
            logger.info(f"   التأثير: {impact_percentage:+.2f}%")
            
            # استخدام الكمية المقربة
            qty = final_qty
            
            # إضافة معلومات إضافية للتتبع (مستوحى من الملفات المرفقة)
            signal_data['original_calculated_qty'] = (trade_amount * leverage) / price if market_type == 'futures' else trade_amount / price
            signal_data['final_rounded_qty'] = final_qty
            signal_data['quantity_adjustment_applied'] = abs(final_qty - signal_data['original_calculated_qty']) > 0.00000001
            signal_data['quantity_adjustment_percentage'] = impact_percentage
            
            # تتبع إذا تم التقريب لإرسال رسالة للمستخدم
            original_qty = (trade_amount * leverage) / price if market_type == 'futures' else trade_amount / price
            qty_was_adjusted = abs(final_qty - original_qty) > 0.00000001
            
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
                        
                        from signals.signal_position_manager import signal_position_manager
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
                
                # إرسال رسالة فشل للمستخدم (بدون محاولات إضافية)
                try:
                    error_message = f'Failed to place order on Bybit - no valid order_id'
                    if result and isinstance(result, dict) and 'error' in result:
                        error_message = result['error']
                    await SignalExecutor._send_error_notification(user_id, error_message, signal_data)
                except Exception as notify_error:
                    logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
                
                return {
                    'success': False,
                    'message': f'Failed to place order on Bybit - no valid order_id',
                    'error': 'ORDER_FAILED',
                    'result_details': result
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة Bybit: {e}")
            
            # إرسال رسالة فشل للمستخدم
            try:
                await SignalExecutor._send_error_notification(user_id, str(e), signal_data)
            except Exception as notify_error:
                logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
            
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
                    logger.error(f"⚠️ فشل وضع أمر Spot - استجابة فارغة")
                    # إرسال إشعار للمستخدم
                    try:
                        await SignalExecutor._send_error_notification(user_id, 'فشل وضع أمر Spot - استجابة فارغة', signal_data)
                    except Exception as notify_error:
                        logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
                    return {
                        'success': False,
                        'message': f'فشل وضع أمر Spot - استجابة فارغة',
                        'is_real': True,
                        'error': 'EMPTY_RESPONSE'
                    }
                
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"⚠️ خطأ في Spot API: {result['error']}")
                    # إرسال إشعار للمستخدم
                    try:
                        await SignalExecutor._send_error_notification(user_id, result['error'], signal_data)
                    except Exception as notify_error:
                        logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
                    return {
                        'success': False,
                        'message': f'خطأ في Spot API: {result["error"]}',
                        'is_real': True,
                        'error': 'API_ERROR',
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
                    logger.error(f"⚠️ فشل وضع أمر البيع - استجابة فارغة")
                    # إرسال إشعار للمستخدم
                    try:
                        await SignalExecutor._send_error_notification(user_id, 'فشل وضع أمر البيع - استجابة فارغة', signal_data)
                    except Exception as notify_error:
                        logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
                    return {
                        'success': False,
                        'message': f'فشل وضع أمر البيع - استجابة فارغة',
                        'is_real': True,
                        'error': 'EMPTY_RESPONSE'
                    }
                
                if isinstance(result, dict) and 'error' in result:
                    logger.error(f"⚠️ خطأ في Sell API: {result['error']}")
                    # إرسال إشعار للمستخدم
                    try:
                        await SignalExecutor._send_error_notification(user_id, result['error'], signal_data)
                    except Exception as notify_error:
                        logger.error(f"❌ فشل إرسال إشعار الخطأ: {notify_error}")
                    return {
                        'success': False,
                        'message': f'خطأ في API البيع: {result["error"]}',
                        'is_real': True,
                        'error': 'API_ERROR',
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
    def _log_quantity_adjustment_details(original_qty: float, final_qty: float, 
                                       trade_amount: float, symbol: str, 
                                       market_type: str, leverage: int) -> Dict:
        """
        تسجيل تفاصيل تعديل الكمية (مستوحى من الملفات المرفقة)
        
        Returns:
            معلومات مفصلة عن التعديل
        """
        try:
            adjustment_info = {
                'symbol': symbol,
                'market_type': market_type,
                'original_qty': original_qty,
                'final_qty': final_qty,
                'qty_change': final_qty - original_qty,
                'qty_change_percentage': ((final_qty - original_qty) / original_qty * 100) if original_qty > 0 else 0,
                'trade_amount': trade_amount,
                'leverage': leverage,
                'adjustment_applied': abs(final_qty - original_qty) > 0.00000001,
                'timestamp': datetime.now().isoformat()
            }
            
            # تصنيف نوع التعديل
            if adjustment_info['qty_change'] > 0:
                adjustment_info['adjustment_type'] = 'INCREASE'
                adjustment_info['adjustment_reason'] = 'Minimum quantity requirement'
            elif adjustment_info['qty_change'] < 0:
                adjustment_info['adjustment_type'] = 'DECREASE'
                adjustment_info['adjustment_reason'] = 'Smart rounding optimization'
            else:
                adjustment_info['adjustment_type'] = 'NONE'
                adjustment_info['adjustment_reason'] = 'No adjustment needed'
            
            # تقييم مستوى التأثير
            abs_change_pct = abs(adjustment_info['qty_change_percentage'])
            if abs_change_pct > 20:
                adjustment_info['impact_level'] = 'HIGH'
            elif abs_change_pct > 10:
                adjustment_info['impact_level'] = 'MEDIUM'
            elif abs_change_pct > 5:
                adjustment_info['impact_level'] = 'LOW'
            else:
                adjustment_info['impact_level'] = 'MINIMAL'
            
            logger.info(f"📊 تفاصيل تعديل الكمية لـ {symbol}:")
            logger.info(f"   النوع: {adjustment_info['adjustment_type']}")
            logger.info(f"   السبب: {adjustment_info['adjustment_reason']}")
            logger.info(f"   مستوى التأثير: {adjustment_info['impact_level']}")
            logger.info(f"   التغيير: {adjustment_info['qty_change']:+.8f} ({adjustment_info['qty_change_percentage']:+.2f}%)")
            
            return adjustment_info
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل تفاصيل تعديل الكمية: {e}")
            return {}

    @staticmethod
    def _validate_trading_parameters(qty: float, price: float, trade_amount: float, 
                                   leverage: int, symbol: str) -> tuple[bool, str]:
        """
        التحقق من صحة معاملات التداول (مستوحى من الملفات المرفقة)
        
        Returns:
            (صحيح/خطأ, رسالة الخطأ)
        """
        try:
            # فحص القيم الأساسية
            if qty <= 0:
                return False, f"كمية غير صحيحة: {qty}"
            
            if price <= 0:
                return False, f"سعر غير صحيح: {price}"
            
            if trade_amount <= 0:
                return False, f"مبلغ التداول غير صحيح: {trade_amount}"
            
            if leverage <= 0:
                return False, f"رافعة مالية غير صحيحة: {leverage}"
            
            if not symbol or len(symbol) < 6:
                return False, f"رمز العملة غير صحيح: {symbol}"
            
            # فحص القيم المنطقية
            notional_value = qty * price
            if notional_value < 1:  # أقل من دولار واحد
                return False, f"قيمة الصفقة صغيرة جداً: ${notional_value:.4f}"
            
            if notional_value > 1000000:  # أكثر من مليون دولار
                return False, f"قيمة الصفقة كبيرة جداً: ${notional_value:.2f}"
            
            return True, "المعاملات صحيحة"
            
        except Exception as e:
            return False, f"خطأ في التحقق من المعاملات: {e}"

    @staticmethod
    def _smart_quantity_rounding(qty: float, price: float, trade_amount: float,
                                leverage: int, market_type: str, symbol: str) -> float:
        """
        دالة التقريب التلقائي الذكية المحسنة
        
        تعمل بالطريقة التالية:
        1. تحدد مستوى الدقة المطلوب حسب حجم الكمية
        2. تبحث عن أقرب قيمة مقبولة من المنصة
        3. تتحقق من أن التأثير المالي مقبول
        4. ترجع أفضل كمية ممكنة
        
        Args:
            qty: الكمية الأصلية المحسوبة
            price: السعر الحالي
            trade_amount: المبلغ المراد تداوله
            leverage: الرافعة المالية
            market_type: نوع السوق (spot/futures)
            symbol: رمز العملة
            
        Returns:
            الكمية المقربة والمحسنة
        """
        try:
            # التحقق من صحة المعاملات أولاً
            is_valid, validation_message = SignalExecutor._validate_trading_parameters(
                qty, price, trade_amount, leverage, symbol
            )
            
            if not is_valid:
                logger.error(f"❌ معاملات غير صحيحة: {validation_message}")
                # في حالة الخطأ، نرجع كمية آمنة
                return max(0.001, qty)
            
            original_qty = qty
            
            # الخطوة 1: تحديد مستوى الدقة حسب حجم الكمية
            if qty >= 1000:
                decimal_places = 0  # أرقام كبيرة جداً
                step_size = 1.0
            elif qty >= 100:
                decimal_places = 1
                step_size = 0.1
            elif qty >= 10:
                decimal_places = 2
                step_size = 0.01
            elif qty >= 1:
                decimal_places = 3
                step_size = 0.001
            elif qty >= 0.1:
                decimal_places = 4
                step_size = 0.0001
            elif qty >= 0.01:
                decimal_places = 5
                step_size = 0.00001
            elif qty >= 0.001:
                decimal_places = 6
                step_size = 0.000001
            else:
                decimal_places = 8
                step_size = 0.00000001
            
            # الخطوة 2: التقريب الأساسي
            rounded_qty = round(qty, decimal_places)
            
            # الخطوة 3: تحديد الحد الأدنى بناءً على المبلغ المالي المحدد للصفقة
            # حساب القيمة المالية للكمية الحالية
            current_notional_value = rounded_qty * price
            
            # تحديد الحد الأدنى للقيمة المالية (بناءً على المبلغ المحدد)
            if trade_amount >= 1000:  # صفقات كبيرة
                min_notional_value = 5.0  # حد أدنى $5
                min_qty_step = 0.1
            elif trade_amount >= 500:  # صفقات متوسطة كبيرة
                min_notional_value = 2.0  # حد أدنى $2
                min_qty_step = 0.05
            elif trade_amount >= 100:  # صفقات متوسطة
                min_notional_value = 1.0  # حد أدنى $1
                min_qty_step = 0.01
            elif trade_amount >= 50:   # صفقات صغيرة متوسطة
                min_notional_value = 0.5  # حد أدنى $0.5
                min_qty_step = 0.005
            elif trade_amount >= 20:   # صفقات صغيرة
                min_notional_value = 0.2  # حد أدنى $0.2
                min_qty_step = 0.001
            else:  # صفقات صغيرة جداً
                min_notional_value = 0.1  # حد أدنى $0.1
                min_qty_step = 0.0005
            
            # حساب الحد الأدنى للكمية بناءً على القيمة المالية
            min_qty = min_notional_value / price
            
            logger.info(f"💰 تحديد الحد الأدنى بناءً على المبلغ:")
            logger.info(f"   مبلغ الصفقة: ${trade_amount}")
            logger.info(f"   الحد الأدنى للقيمة: ${min_notional_value}")
            logger.info(f"   الحد الأدنى للكمية: {min_qty:.8f}")
            logger.info(f"   القيمة الحالية: ${current_notional_value:.4f}")
            
            if rounded_qty < min_qty:
                old_qty = rounded_qty
                rounded_qty = min_qty
                logger.info(f"⚠️ تم رفع الكمية للحد الأدنى: {old_qty:.8f} → {min_qty}")
            
            # الخطوة 4: البحث عن أقرب كمية تحقق المبلغ المطلوب
            # نبحث عن كميات مختلفة تقترب من المبلغ المحدد
            candidates = []
            
            # القيمة المقربة الأساسية
            candidates.append(rounded_qty)
            
            # إنشاء كميات مرشحة بناءً على المبلغ المحدد
            # الهدف: العثور على كمية تعطي قيمة مالية قريبة من trade_amount
            target_notional = trade_amount * leverage if market_type == 'futures' else trade_amount
            
            # حساب الكمية المثالية للمبلغ المحدد
            ideal_qty_for_amount = target_notional / price
            
            # إضافة كميات مرشحة حول الكمية المثالية
            for percentage in [0.95, 0.98, 1.0, 1.02, 1.05, 1.1]:
                candidate_qty = ideal_qty_for_amount * percentage
                if candidate_qty >= min_qty:
                    candidates.append(candidate_qty)
            
            # إضافة كميات بناءً على خطوات صغيرة من الكمية الأصلية
            for i in range(1, 6):
                higher = rounded_qty + (min_qty_step * i)
                lower = rounded_qty - (min_qty_step * i)
                
                if lower >= min_qty:
                    candidates.append(lower)
                candidates.append(higher)
            
            # إضافة كميات تحقق قيماً مالية محددة قريبة من المبلغ المطلوب
            for target_value in [target_notional * 0.98, target_notional, target_notional * 1.02]:
                candidate_qty = target_value / price
                if candidate_qty >= min_qty:
                    candidates.append(candidate_qty)
            
            # الخطوة 5: اختيار أفضل كمية تحقق أقرب مبلغ للمبلغ المحدد
            best_qty = rounded_qty
            min_amount_deviation = float('inf')
            best_candidate_info = {}
            
            logger.info(f"🎯 البحث عن أفضل كمية للمبلغ المحدد: ${trade_amount}")
            
            for candidate in candidates:
                if candidate <= 0:
                    continue
                
                # حساب المبلغ الفعلي لهذه الكمية
                candidate_notional = candidate * price
                if market_type == 'futures':
                    actual_amount = candidate_notional / leverage
                else:
                    actual_amount = candidate_notional
                
                # حساب الانحراف عن المبلغ المحدد
                amount_deviation = abs(actual_amount - trade_amount)
                deviation_percentage = (amount_deviation / trade_amount) * 100 if trade_amount > 0 else 0
                
                # معايير اختيار أفضل كمية:
                # 1. أقل انحراف عن المبلغ المحدد
                # 2. ضمن حدود مقبولة (أقل من 10% انحراف)
                if (amount_deviation < min_amount_deviation and 
                    deviation_percentage <= 15):  # حد أقصى 15% انحراف
                    
                    min_amount_deviation = amount_deviation
                    best_qty = candidate
                    best_candidate_info = {
                        'quantity': candidate,
                        'actual_amount': actual_amount,
                        'target_amount': trade_amount,
                        'deviation': amount_deviation,
                        'deviation_percentage': deviation_percentage
                    }
            
            # تسجيل تفاصيل الاختيار
            if best_candidate_info:
                logger.info(f"✅ أفضل كمية محددة:")
                logger.info(f"   الكمية: {best_candidate_info['quantity']:.8f}")
                logger.info(f"   المبلغ المستهدف: ${best_candidate_info['target_amount']:.2f}")
                logger.info(f"   المبلغ الفعلي: ${best_candidate_info['actual_amount']:.2f}")
                logger.info(f"   الانحراف: ${best_candidate_info['deviation']:.2f} ({best_candidate_info['deviation_percentage']:.2f}%)")
            
            # الخطوة 6: تسجيل تفاصيل التعديل (مستوحى من الملفات المرفقة)
            adjustment_details = SignalExecutor._log_quantity_adjustment_details(
                original_qty, best_qty, trade_amount, symbol, market_type, leverage
            )
            
            # الخطوة 7: التحقق النهائي والتقرير المالي
            if abs(best_qty - original_qty) > 0.00000001:
                # حساب التأثير المالي الفعلي
                if market_type == 'futures':
                    effective_amount = (best_qty * price) / leverage
                else:
                    effective_amount = best_qty * price
                
                amount_deviation = effective_amount - trade_amount
                impact_percentage = (amount_deviation / trade_amount) * 100 if trade_amount > 0 else 0
                
                logger.info(f"🧠 التقريب الذكي المحسن (مبني على المبلغ):")
                logger.info(f"   الكمية الأصلية: {original_qty:.8f}")
                logger.info(f"   الكمية المحسنة: {best_qty:.8f}")
                logger.info(f"   المبلغ المستهدف: ${trade_amount:.2f}")
                logger.info(f"   المبلغ الفعلي: ${effective_amount:.2f}")
                logger.info(f"   انحراف المبلغ: ${amount_deviation:+.2f} ({impact_percentage:+.2f}%)")
                
                # نظام تحذيرات مبني على انحراف المبلغ
                abs_deviation = abs(amount_deviation)
                if abs_deviation > trade_amount * 0.2:  # أكثر من 20% من المبلغ
                    logger.error(f"🚨 انحراف مالي خطير: ${abs_deviation:.2f} - يتطلب مراجعة!")
                elif abs_deviation > trade_amount * 0.1:  # أكثر من 10% من المبلغ
                    logger.warning(f"⚠️ انحراف مالي كبير: ${abs_deviation:.2f} - انتبه!")
                elif abs_deviation > trade_amount * 0.05:  # أكثر من 5% من المبلغ
                    logger.warning(f"⚠️ انحراف مالي ملحوظ: ${abs_deviation:.2f}")
                else:
                    logger.info(f"✅ انحراف مالي مقبول: ${abs_deviation:.2f}")
            else:
                logger.info(f"✅ الكمية مثالية للمبلغ المحدد: {best_qty:.8f}")
            
            return best_qty
            
        except Exception as e:
            logger.error(f"❌ خطأ في التقريب الذكي: {e}")
            # في حالة الخطأ، نرجع التقريب البسيط
            return round(qty, 4)
    
    @staticmethod
    def _calculate_adjusted_quantity(qty: float, price: float, trade_amount: float, leverage: int) -> float:
        """
        حساب كمية معدلة عند فشل الصفقة بالتقريب الذكي (دالة قديمة للتوافق)
        
        Args:
            qty: الكمية الأصلية
            price: السعر الحالي
            trade_amount: المبلغ الأصلي
            leverage: الرافعة المالية
            
        Returns:
            الكمية المعدلة
        """
        # استخدام الدالة الجديدة المحسنة
        return SignalExecutor._smart_quantity_rounding(qty, price, trade_amount, leverage, 'futures', 'UNKNOWN')
    
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
                logger.info(f"📤 وضع أمر على Bybit: {side} {symbol} - كمية: {qty}")
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
                
                # إذا تم تعديل الكمية (في المحاولة الثانية)، أضف رسالة للمستخدم
                if qty_was_adjusted and result and isinstance(result, dict) and result.get('order_id'):
                    effective_amount = (qty * price) / leverage
                    logger.info(f"📢 تم تنفيذ الصفقة بكمية مصححة")
                    logger.info(f"   المبلغ المستهدف: ${trade_amount}")
                    logger.info(f"   المبلغ الفعلي: ${effective_amount:.2f}")
                    # سيتم إضافة هذه الرسالة في النتيجة
                    result['adjustment_message'] = f'تم تصحيح الكمية لتتوافق مع متطلبات المنصة'
                
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
            
            # التحقق النهائي من النجاح قبل الإرجاع
            if not result or not isinstance(result, dict) or not result.get('order_id'):
                logger.error(f"❌ فشل تنفيذ الصفقة - لا يوجد order_id")
                logger.error(f"   النتيجة: {result}")
                return {
                    'success': False,
                    'message': f'Order placement failed - no valid order_id',
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
    
    @staticmethod
    async def _send_error_notification(user_id: int, error_message: str, signal_data: Dict):
        """إرسال إشعار خطأ للمستخدم"""
        try:
            # استيراد الوحدات المطلوبة
            from config import TELEGRAM_TOKEN
            from telegram.ext import Application
            
            # إنشاء رسالة مفصلة
            symbol = signal_data.get('symbol', 'غير محدد')
            action = signal_data.get('action', 'غير محدد')
            
            # ترجمة رسائل الخطأ الشائعة
            if 'ab not enough' in error_message.lower():
                arabic_error = "❌ الرصيد غير كافي لتنفيذ الصفقة"
                suggestion = "💡 تأكد من وجود رصيد كافي في حسابك على Bybit"
            elif 'invalid price' in error_message.lower():
                arabic_error = "❌ السعر غير صحيح"
                suggestion = "💡 تحقق من صحة السعر المرسل في الإشارة"
            elif 'symbol not found' in error_message.lower():
                arabic_error = "❌ الرمز غير موجود"
                suggestion = "💡 تأكد من صحة رمز العملة (مثل BTCUSDT)"
            elif 'connection' in error_message.lower():
                arabic_error = "❌ مشكلة في الاتصال بالمنصة"
                suggestion = "💡 سيتم إعادة المحاولة تلقائياً"
            else:
                arabic_error = f"❌ خطأ في تنفيذ الصفقة: {error_message}"
                suggestion = "💡 تحقق من إعدادات حسابك وحاول مرة أخرى"
            
            # إنشاء رسالة بسيطة بدون markdown لتجنب أخطاء التنسيق
            notification_text = f"""فشل تنفيذ الصفقة

تفاصيل الإشارة:
الرمز: {symbol}
الإجراء: {action.upper()}

سبب الفشل:
{arabic_error}

{suggestion}

الإجراءات المقترحة:
- تحقق من رصيد حسابك على Bybit
- تأكد من صحة إعدادات API
- راجع إعدادات التداول

للمساعدة: تواصل مع الدعم الفني""".strip()
            
            # إرسال الرسالة بدون parse_mode لتجنب أخطاء التنسيق
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            await application.bot.send_message(
                chat_id=user_id,
                text=notification_text
            )
            
            logger.info(f"✅ تم إرسال إشعار فشل الصفقة للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"❌ فشل إرسال إشعار الخطأ للمستخدم {user_id}: {e}")


# مثيل عام
signal_executor = SignalExecutor()

