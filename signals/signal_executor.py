#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from api.bybit_api import real_account_manager
from signals.signal_position_manager import signal_position_manager

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

# استيراد المدير الموحد للصفقات
try:
    from systems.unified_position_manager import UnifiedPositionManager
    from users.database import db_manager
    UNIFIED_POSITION_MANAGER_AVAILABLE = True
    logger.info("✅ تم تحميل المدير الموحد للصفقات")
except ImportError as e:
    UNIFIED_POSITION_MANAGER_AVAILABLE = False
    logger.warning(f"⚠️ المدير الموحد للصفقات غير متاح: {e}")

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
            logger.info(f"🔍 استخراج الإعدادات من user_data:")
            logger.info(f"=" * 80)
            logger.info(f"📊 الإعدادات الأساسية:")
            logger.info(f"   ✅ trade_amount: {trade_amount} USDT (من user_data.get('trade_amount', 100.0))")
            logger.info(f"   ✅ leverage: {leverage}x (من user_data.get('leverage', 10))")
            logger.info(f"   ✅ market_type: {user_data.get('market_type', 'غير محدد')}")
            logger.info(f"   ✅ account_type: {user_data.get('account_type', 'غير محدد')}")
            logger.info(f"   ✅ exchange: {user_data.get('exchange', 'غير محدد')}")
            logger.info(f"")
            logger.info(f"📋 user_data الكامل:")
            for key, value in user_data.items():
                if key not in ['api_key', 'api_secret', 'bybit_api_key', 'bybit_api_secret']:
                    logger.info(f"   - {key}: {value}")
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
            logger.info(f"=" * 80)
            logger.info(f"💰 بدء حساب الكمية بناءً على الإعدادات")
            logger.info(f"=" * 80)
            
            try:
                logger.info(f"🔍 جلب السعر الحالي من المنصة...")
                current_price = account.get_ticker_price(symbol)
                price = float(current_price)
                logger.info(f"✅ تم جلب السعر الحقيقي من المنصة: {price} USDT")
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب السعر الحقيقي: {e}")
                price = float(signal_data.get('price', 1))
                logger.warning(f"⚠️ استخدام السعر الافتراضي من الإشارة: {price}")
            
            # التحقق من أن السعر صحيح
            if price <= 0:
                logger.error(f"❌ سعر غير صحيح: {price}")
                return {
                    'success': False,
                    'message': f'Invalid price: {price}',
                    'is_real': True
                }
            
            # حساب الكمية مع ضمان عدم وجود قيم صغيرة جداً
            logger.info(f"")
            logger.info(f"🧮 حساب الكمية باستخدام الإعدادات:")
            logger.info(f"   📊 المدخلات:")
            logger.info(f"      - market_type: {market_type}")
            logger.info(f"      - trade_amount: {trade_amount} USDT (من إعدادات المستخدم)")
            logger.info(f"      - leverage: {leverage}x (من إعدادات المستخدم)")
            logger.info(f"      - price: {price} USDT (السعر الحالي)")
            
            if market_type == 'futures':
                qty = (trade_amount * leverage) / price
                notional_value = trade_amount * leverage
                logger.info(f"")
                logger.info(f"   📈 حساب Futures:")
                logger.info(f"      - الصيغة: qty = (trade_amount × leverage) / price")
                logger.info(f"      - الحساب: qty = ({trade_amount} × {leverage}) / {price}")
                logger.info(f"      - النتيجة: qty = {qty}")
                logger.info(f"      - القيمة الاسمية: {notional_value} USDT")
            else:
                # للسبوت بدون رافعة
                qty = trade_amount / price
                notional_value = trade_amount
                logger.info(f"")
                logger.info(f"   📊 حساب Spot:")
                logger.info(f"      - الصيغة: qty = trade_amount / price")
                logger.info(f"      - الحساب: qty = {trade_amount} / {price}")
                logger.info(f"      - النتيجة: qty = {qty}")
                logger.info(f"      - القيمة الاسمية: {notional_value} USDT")
            
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
                qty, price, trade_amount, leverage, market_type, symbol, account
            )
            
            # فحص إضافي للرصيد (مستوحى من الملفات المرفقة)
            if final_qty < qty * 0.5:  # إذا كان التقريب قلل الكمية بأكثر من 50%
                logger.warning(f"⚠️ التقريب قلل الكمية بشكل كبير: {qty:.8f} → {final_qty:.8f}")
                
                # فحص الرصيد المتاح لضمان إمكانية التنفيذ
                try:
                    balance_info = account.get_wallet_balance('unified')
                    if balance_info and 'coins' in balance_info:
                        # إصلاح: استخدام 'coins' بدلاً من 'list'
                        usdt_coin = balance_info['coins'].get('USDT')
                        if usdt_coin:
                            available_balance = float(usdt_coin.get('available', 0))
                            if available_balance == 0:
                                # إذا لم يكن available، استخدم wallet_balance
                                available_balance = float(usdt_coin.get('wallet_balance', 0))
                            
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
            
            # فحص شامل للرصيد قبل تنفيذ الصفقة
            try:
                balance_info = account.get_wallet_balance('unified')
                if balance_info and 'coins' in balance_info:
                    usdt_coin = balance_info['coins'].get('USDT')
                    if usdt_coin:
                        available_balance = float(usdt_coin.get('available', 0))
                        if available_balance == 0:
                            available_balance = float(usdt_coin.get('wallet_balance', 0))
                        
                        # حساب الهامش المطلوب
                        required_margin = (qty * price) / leverage if market_type == 'futures' else qty * price
                        
                        # إضافة هامش أمان 5% لتجنب مشاكل التقريب
                        required_margin_with_buffer = required_margin * 1.05
                        
                        logger.info(f"💰 فحص الرصيد النهائي: متاح={available_balance:.2f} USDT، مطلوب={required_margin_with_buffer:.2f} USDT (مع هامش أمان 5%)")
                        
                        if available_balance < required_margin_with_buffer:
                            logger.error(f"❌ رصيد غير كافي لتنفيذ الصفقة")
                            return {
                                'success': False,
                                'message': f'رصيد غير كافي. متاح: {available_balance:.2f} USDT، مطلوب: {required_margin_with_buffer:.2f} USDT (بما في ذلك هامش الأمان)',
                                'error': 'INSUFFICIENT_BALANCE',
                                'is_real': True,
                                'available_balance': available_balance,
                                'required_balance': required_margin_with_buffer
                            }
                        else:
                            logger.info(f"✅ الرصيد كافي للتنفيذ")
                else:
                    logger.warning(f"⚠️ لم يتم الحصول على معلومات الرصيد - سيتم المتابعة")
            except Exception as e:
                logger.warning(f"⚠️ خطأ في فحص الرصيد النهائي: {e} - سيتم المتابعة")
            
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
                # إرسال إشعار نجاح الإغلاق
                try:
                    await SignalExecutor._send_close_notification(user_id, signal_id, symbol, closed_count, 'full')
                except Exception as e:
                    logger.error(f"❌ فشل إرسال إشعار الإغلاق: {e}")
                
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
                # إرسال إشعار نجاح الإغلاق الجزئي
                try:
                    await SignalExecutor._send_close_notification(user_id, signal_id, symbol, closed_count, 'partial', percentage)
                except Exception as e:
                    logger.error(f"❌ فشل إرسال إشعار الإغلاق الجزئي: {e}")
                
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
                
                # حفظ صفقة السبوت في قاعدة البيانات - دائماً
                if result and result.get('order_id'):
                    try:
                        from users.database import db_manager
                        
                        order_data = {
                            'order_id': result.get('order_id', SignalExecutor._generate_random_id(symbol)),
                            'user_id': user_id,
                            'symbol': symbol,
                            'side': side,
                            'entry_price': price,
                            'quantity': qty,
                            'status': 'OPEN',
                            'market_type': 'spot',
                            'leverage': 1,
                            'notes': f'Spot order - {side} {qty} {symbol}'
                        }
                        
                        db_manager.create_order(order_data)
                        logger.info(f"✅ تم حفظ صفقة سبوت في قاعدة البيانات")
                        
                        # إذا كان لديه signal_id، حفظه أيضاً في signal_positions
                        if has_signal_id and signal_id:
                            from systems.enhanced_portfolio_manager import portfolio_factory
                            portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
                            
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
                            
                            portfolio_manager.add_position(position_data)
                            logger.info(f"✅ تم حفظ الصفقة في signal_positions أيضاً")
                    except Exception as e:
                        logger.error(f"❌ فشل حفظ صفقة سبوت: {e}")
                    
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
                                leverage: int, market_type: str, symbol: str, account=None) -> float:
        """
        دالة التقريب الذكي المحسنة - تبحث عن أقرب كمية مسموحة للمبلغ المحدد
        
        المنطق:
        1. جلب معلومات الرمز من Bybit (الحد الأدنى وخطوة الكمية)
        2. إنشاء قائمة بالكميات المسموحة حول الكمية المحسوبة
        3. اختيار الكمية الأقرب للمبلغ المحدد (سواء أكبر أو أصغر)
        4. إذا لم توجد كمية أقل، نختار الأكبر
        
        مثال:
        - المبلغ: 10 USDT
        - الكميات المسموحة: 9, 12, 15
        - النتيجة: 9 (الأقرب للـ 10)
        
        Args:
            qty: الكمية الأصلية المحسوبة
            price: السعر الحالي
            trade_amount: المبلغ المراد تداوله
            leverage: الرافعة المالية
            market_type: نوع السوق (spot/futures)
            symbol: رمز العملة
            account: حساب Bybit للحصول على معلومات الرمز
            
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
                return max(0.001, qty)
            
            original_qty = qty
            target_amount = trade_amount  # المبلغ المستهدف
            
            # جلب معلومات الرمز من Bybit API
            instrument_min_qty = None
            instrument_qty_step = None
            
            if account:
                try:
                    category = 'linear' if market_type == 'futures' else 'spot'
                    instrument_info = account.get_instrument_info(symbol, category)
                    
                    if instrument_info:
                        instrument_min_qty = instrument_info['min_order_qty']
                        instrument_qty_step = instrument_info['qty_step']
                        
                        logger.info(f"📋 معلومات الرمز من Bybit:")
                        logger.info(f"   الحد الأدنى للكمية: {instrument_min_qty}")
                        logger.info(f"   خطوة الكمية: {instrument_qty_step}")
                except Exception as e:
                    logger.warning(f"⚠️ فشل جلب معلومات الرمز: {e}")
            
            # إذا لم نحصل على معلومات من API، استخدم قيم افتراضية
            if not instrument_min_qty or not instrument_qty_step:
                logger.warning(f"⚠️ استخدام قيم افتراضية للتقريب")
                instrument_min_qty = 0.001
                instrument_qty_step = 0.001
            
            logger.info(f"🎯 بدء التقريب الذكي:")
            logger.info(f"   المبلغ المستهدف: {target_amount} USDT")
            logger.info(f"   الكمية المحسوبة: {original_qty}")
            logger.info(f"   السعر: {price} USDT")
            logger.info(f"   الحد الأدنى: {instrument_min_qty}")
            logger.info(f"   خطوة الكمية: {instrument_qty_step}")
            
            # الخطوة 1: إنشاء قائمة بالكميات المسموحة حول الكمية المحسوبة
            # نبدأ من الحد الأدنى ونزيد بخطوات حتى نصل لكميات أكبر من المحسوبة
            allowed_quantities = []
            
            # البدء من الحد الأدنى
            current_qty = instrument_min_qty
            max_iterations = 1000  # حد أقصى للتكرار لتجنب حلقة لا نهائية
            iteration = 0
            
            # إنشاء كميات من الحد الأدنى حتى 3 أضعاف الكمية المحسوبة
            max_qty = original_qty * 3
            
            while current_qty <= max_qty and iteration < max_iterations:
                allowed_quantities.append(current_qty)
                current_qty += instrument_qty_step
                iteration += 1
            
            # إضافة الكمية المحسوبة نفسها إذا لم تكن موجودة
            if original_qty not in allowed_quantities:
                allowed_quantities.append(original_qty)
            
            # ترتيب القائمة
            allowed_quantities.sort()
            
            logger.info(f"📊 تم إنشاء {len(allowed_quantities)} كمية مسموحة")
            if len(allowed_quantities) > 0:
                logger.info(f"   أول 5 كميات: {allowed_quantities[:5]}")
                logger.info(f"   آخر 5 كميات: {allowed_quantities[-5:]}")
            
            # الخطوة 2: البحث عن الكمية الأقرب للمبلغ المستهدف
            # نحسب المبلغ الفعلي لكل كمية ونقارنه بالمبلغ المستهدف
            
            best_qty = None
            min_deviation = float('inf')
            candidates_info = []
            
            for candidate_qty in allowed_quantities:
                # حساب المبلغ الفعلي لهذه الكمية
                if market_type == 'futures':
                    actual_amount = (candidate_qty * price) / leverage
                else:
                    actual_amount = candidate_qty * price
                
                # حساب الانحراف عن المبلغ المستهدف
                deviation = abs(actual_amount - target_amount)
                
                candidates_info.append({
                    'qty': candidate_qty,
                    'amount': actual_amount,
                    'deviation': deviation,
                    'is_lower': actual_amount < target_amount,
                    'is_higher': actual_amount > target_amount
                })
                
                # اختيار الأقرب
                if deviation < min_deviation:
                    min_deviation = deviation
                    best_qty = candidate_qty
            
            # إذا لم نجد كمية مناسبة، استخدم الحد الأدنى
            if best_qty is None:
                logger.warning(f"⚠️ لم يتم العثور على كمية مناسبة - استخدام الحد الأدنى")
                best_qty = instrument_min_qty
            
            # عرض أفضل 5 خيارات
            candidates_info.sort(key=lambda x: x['deviation'])
            logger.info(f"🔍 أفضل 5 كميات قريبة من المبلغ المستهدف ({target_amount} USDT):")
            for i, candidate in enumerate(candidates_info[:5], 1):
                status = "أقل ⬇️" if candidate['is_lower'] else "أكبر ⬆️"
                logger.info(f"   {i}. كمية: {candidate['qty']:.8f} → مبلغ: {candidate['amount']:.2f} USDT ({status}) - انحراف: {candidate['deviation']:.2f}")
            
            # حساب المبلغ الفعلي للكمية المختارة
            if market_type == 'futures':
                final_amount = (best_qty * price) / leverage
            else:
                final_amount = best_qty * price
            
            amount_deviation = final_amount - target_amount
            deviation_percentage = (amount_deviation / target_amount) * 100 if target_amount > 0 else 0
            
            logger.info(f"")
            logger.info(f"✅ الكمية المختارة:")
            logger.info(f"   الكمية: {best_qty:.8f}")
            logger.info(f"   المبلغ المستهدف: {target_amount:.2f} USDT")
            logger.info(f"   المبلغ الفعلي: {final_amount:.2f} USDT")
            logger.info(f"   الانحراف: {amount_deviation:+.2f} USDT ({deviation_percentage:+.2f}%)")
            
            # تحذير إذا كان الانحراف كبيراً
            if abs(deviation_percentage) > 20:
                logger.warning(f"⚠️ الانحراف كبير ({deviation_percentage:+.2f}%) - قد تحتاج لتعديل المبلغ")
            elif abs(deviation_percentage) > 10:
                logger.warning(f"⚠️ انحراف ملحوظ ({deviation_percentage:+.2f}%)")
            else:
                logger.info(f"✅ الانحراف مقبول ({deviation_percentage:+.2f}%)")
            
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
        """
        معالجة أمر الفيوتشر مع تجميع حسب ID
        
        Returns:
            dict: يحتوي على order_id إذا نجح، أو error إذا فشل
        """
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
                # فحص الرصيد قبل تجميع الصفقات
                try:
                    # الحصول على السعر الحالي
                    current_price = price if price > 0 else signal_data.get('price', 0)
                    if not current_price or current_price == 0:
                        # جلب السعر من API
                        ticker = account.get_ticker('linear' if market_type == 'futures' else 'spot', symbol)
                        if ticker and 'lastPrice' in ticker:
                            current_price = float(ticker['lastPrice'])
                    
                    if current_price and current_price > 0:
                        balance_info = account.get_wallet_balance('unified')
                        if balance_info and 'coins' in balance_info:
                            usdt_coin = balance_info['coins'].get('USDT')
                            if usdt_coin:
                                available_balance = float(usdt_coin.get('available', 0))
                                if available_balance == 0:
                                    available_balance = float(usdt_coin.get('wallet_balance', 0))
                                
                                # حساب الهامش المطلوب للكمية الإضافية
                                additional_margin = (qty * current_price) / leverage if leverage > 0 else qty * current_price
                                required_margin_with_buffer = additional_margin * 1.05  # هامش أمان 5%
                                
                                logger.info(f"💰 فحص الرصيد قبل تجميع الصفقة: متاح={available_balance:.2f} USDT، مطلوب={required_margin_with_buffer:.2f} USDT")
                                
                                if available_balance < required_margin_with_buffer:
                                    logger.error(f"❌ رصيد غير كافي لإضافة كمية جديدة للصفقة")
                                    return {
                                        'success': False,
                                        'message': f'رصيد غير كافي لإضافة كمية جديدة. متاح: {available_balance:.2f} USDT، مطلوب: {required_margin_with_buffer:.2f} USDT',
                                        'error': 'INSUFFICIENT_BALANCE_FOR_POSITION_ADDITION',
                                        'is_real': True
                                    }
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في فحص الرصيد قبل تجميع الصفقة: {e} - سيتم المتابعة")
                
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
            
            # حفظ الصفقة في قاعدة البيانات - دائماً، حتى بدون signal_id
            if result and result.get('order_id'):
                logger.info(f"📝 حفظ صفقة الفيوتشر في قاعدة البيانات...")
                try:
                    from users.database import db_manager
                    
                    # حساب margin amount للفيوتشر
                    price = signal_data.get('price', 0)
                    margin_amount = (qty * price) / leverage if leverage > 0 else 0
                    
                    order_data = {
                        'order_id': result.get('order_id', SignalExecutor._generate_random_id(symbol)),
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': side,
                        'entry_price': price,
                        'quantity': qty,
                        'leverage': leverage,
                        'status': 'OPEN',
                        'market_type': market_type,
                        'margin_amount': margin_amount,
                        'sl': stop_loss if stop_loss else 0.0,
                        'tps': [take_profit] if take_profit else [],
                        'notes': f'Futures order - {side} {qty} {symbol}'
                    }
                    
                    db_manager.create_order(order_data)
                    logger.info(f"✅ تم حفظ صفقة فيوتشر في قاعدة البيانات")
                    
                    # إذا كان لديه signal_id، حفظه أيضاً في signal_positions
                    if has_signal_id and signal_id:
                        try:
                            from systems.enhanced_portfolio_manager import portfolio_factory
                            portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
                            
                            position_data = {
                                'signal_id': signal_id,
                                'user_id': user_id,
                                'symbol': symbol,
                                'side': side,
                                'entry_price': price,
                                'quantity': qty,
                                'exchange': 'bybit',
                                'market_type': 'futures',
                                'order_id': result.get('order_id', ''),
                                'status': 'OPEN',
                                'notes': f'Futures position - {side} {qty} {symbol} (ID: {signal_id})'
                            }
                            
                            portfolio_manager.add_position(position_data)
                            logger.info(f"✅ تم حفظ الصفقة في signal_positions أيضاً")
                        except Exception as e:
                            logger.warning(f"⚠️ فشل حفظ في signal_positions: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ فشل حفظ الصفقة في قاعدة البيانات: {e}")
            
            # إرجاع النتيجة الناجحة (الصفقة تمت بنجاح على Bybit)
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
            if 'ab not enough' in error_message.lower() or 'insufficient balance' in error_message.lower():
                arabic_error = "❌ الرصيد غير كافي لتنفيذ الصفقة"
                suggestion = "💡 تأكد من وجود رصيد كافي في حسابك على Bybit"
            elif 'invalid price' in error_message.lower():
                arabic_error = "❌ السعر غير صحيح"
                suggestion = "💡 تحقق من صحة السعر المرسل في الإشارة"
            elif 'qty invalid' in error_message.lower() or 'invalid quantity' in error_message.lower():
                arabic_error = "❌ الكمية غير صحيحة"
                suggestion = f"💡 الكمية أقل من الحد الأدنى المسموح به لهذا الرمز\n💡 جرّب زيادة مبلغ التداول من الإعدادات"
            elif 'symbol not found' in error_message.lower():
                arabic_error = "❌ الرمز غير موجود"
                suggestion = "💡 تأكد من صحة رمز العملة (مثل BTCUSDT)"
            elif 'leverage not modified' in error_message.lower():
                arabic_error = "✅ الرافعة المالية مُعيّنة بالفعل"
                suggestion = "💡 هذا تحذير عادي وليس خطأ"
            elif 'connection' in error_message.lower():
                arabic_error = "❌ مشكلة في الاتصال بالمنصة"
                suggestion = "💡 سيتم إعادة المحاولة تلقائياً"
            elif 'no valid order_id' in error_message.lower():
                arabic_error = "❌ فشل إنشاء الأمر على المنصة"
                suggestion = "💡 تحقق من:\n  - صحة مفاتيح API\n  - الرصيد المتاح\n  - مبلغ التداول والكمية"
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

    @staticmethod
    async def _send_close_notification(user_id: int, signal_id: str, symbol: str, 
                                     closed_count: int, close_type: str, percentage: float = None):
        """إرسال إشعار نجاح الإغلاق"""
        try:
            from telegram.ext import Application
            from config import TELEGRAM_TOKEN
            
            # تحديد نوع الإغلاق
            if close_type == 'partial':
                close_text = f"إغلاق جزئي {percentage}%"
                action_emoji = "🟡"
            else:
                close_text = "إغلاق كامل"
                action_emoji = "🔴"
            
            # إنشاء رسالة الإشعار
            notification_text = f"""
{action_emoji} **تم تنفيذ {close_text} بنجاح!**

📊 **تفاصيل العملية:**
• الرمز: {symbol}
• Signal ID: {signal_id}
• عدد الصفقات: {closed_count}
• نوع الإغلاق: {close_text}

✅ **حالة التنفيذ:** نجح
🕐 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 تم تنفيذ العملية على حسابك الحقيقي في Bybit""".strip()
            
            # إرسال الإشعار
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            await application.bot.send_message(
                chat_id=user_id,
                text=notification_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ تم إرسال إشعار {close_type} للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"❌ فشل إرسال إشعار الإغلاق للمستخدم {user_id}: {e}")


# مثيل عام
signal_executor = SignalExecutor()

