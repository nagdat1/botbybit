#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
from typing import Dict, Optional
from real_account_manager import real_account_manager
from signal_manager import signal_manager
from database import db_manager

logger = logging.getLogger(__name__)

class SignalExecutor:
    """منفذ الإشارات على الحسابات الحقيقية"""
    
    @staticmethod
    async def execute_signal(user_id: int, signal_data: Dict, user_data: Dict) -> Dict:
        """
        تنفيذ إشارة تداول مع نظام الإشارات المتقدم
        
        Args:
            user_id: معرف المستخدم
            signal_data: بيانات الإشارة (signal, symbol, price, etc.)
            user_data: إعدادات المستخدم
            
        Returns:
            نتيجة التنفيذ
        """
        try:
            # معالجة الإشارة بواسطة SignalManager
            signal_result = signal_manager.process_signal(user_id, signal_data)
            
            if not signal_result.get('should_execute'):
                # الإشارة تم تجاهلها أو فشلت في التحقق
                logger.warning(f"⚠️ لن يتم تنفيذ الإشارة: {signal_result.get('message')}")
                return signal_result
            
            signal_id = signal_result.get('signal_id')
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '')
            
            logger.info(f"🎯 تنفيذ إشارة للمستخدم {user_id}: {signal_type} {symbol} [ID: {signal_id}]")
            
            account_type = user_data.get('account_type', 'demo')
            exchange = user_data.get('exchange', 'bybit')
            
            logger.info(f"📊 نوع الحساب: {account_type}, المنصة: {exchange}")
            
            # إذا كان حساب تجريبي، إرجاع استجابة محاكاة
            if account_type == 'demo':
                logger.info(f"🟢 حساب تجريبي - سيتم المعالجة بواسطة البوت الأصلي")
                return {
                    'success': False,
                    'message': 'Demo account - handled by original bot',
                    'is_demo': True,
                    'signal_id': signal_id
                }
            
            # الحصول على الحساب الحقيقي
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                logger.error(f"❌ حساب حقيقي غير مفعّل للمستخدم {user_id}")
                signal_manager.mark_signal_failed(signal_id, user_id, 'Real account not activated')
                return {
                    'success': False,
                    'message': 'Real account not activated',
                    'error': 'ACCOUNT_NOT_FOUND',
                    'signal_id': signal_id
                }
            
            # معلومات التداول
            trade_amount = user_data.get('trade_amount', 100.0)
            leverage = user_data.get('leverage', 10)
            
            logger.info(f"💰 مبلغ التداول: {trade_amount}, الرافعة: {leverage}")
            
            # تنفيذ الإشارة حسب المنصة
            if exchange == 'bybit':
                result = await SignalExecutor._execute_bybit_signal(
                    real_account, signal_data, signal_result,
                    trade_amount, leverage, user_id
                )
            elif exchange == 'mexc':
                result = await SignalExecutor._execute_mexc_signal(
                    real_account, signal_data, signal_result,
                    trade_amount, user_id
                )
            else:
                signal_manager.mark_signal_failed(signal_id, user_id, f'Unsupported exchange: {exchange}')
                return {
                    'success': False,
                    'message': f'Unsupported exchange: {exchange}',
                    'error': 'UNSUPPORTED_EXCHANGE',
                    'signal_id': signal_id
                }
            
            # إضافة signal_id للنتيجة
            result['signal_id'] = signal_id
            return result
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الإشارة: {e}")
            import traceback
            traceback.print_exc()
            
            # تحديث حالة الإشارة كفاشلة
            if 'signal_id' in locals():
                signal_manager.mark_signal_failed(signal_id, user_id, str(e))
            
            return {
                'success': False,
                'message': str(e),
                'error': 'EXECUTION_ERROR'
            }
    
    @staticmethod
    async def _execute_bybit_signal(account, signal_data: Dict, signal_result: Dict,
                                   trade_amount: float, leverage: int, user_id: int) -> Dict:
        """تنفيذ إشارة على Bybit مع نظام الإشارات المتقدم"""
        try:
            signal_id = signal_result.get('signal_id')
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '')
            action = signal_result.get('action')  # 'open' أو 'close'
            market_type = signal_result.get('market_type')  # 'spot' أو 'futures'
            side = signal_result.get('side')  # 'Buy' أو 'Sell'
            
            # تحديد الفئة
            category = 'linear' if market_type == 'futures' else 'spot'
            
            logger.info(f"📡 Bybit {category.upper()}: {signal_type} {symbol} [ID: {signal_id}]")
            
            if action == 'close':
                # إغلاق صفقة - البحث عن أي صفقة مفتوحة للرمز المحدد
                positions = account.get_open_positions(category)
                target_position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if target_position:
                    result = account.close_position(category, symbol, target_position['side'])
                    if result:
                        signal_manager.update_signal_with_order(
                            signal_id, user_id, result.get('order_id'), 'closed'
                        )
                        
                        logger.info(f"✅ تم إغلاق صفقة {symbol} بنجاح")
                        return {
                            'success': True,
                            'message': f'Position closed: {symbol}',
                            'order_id': result.get('order_id'),
                            'is_real': True
                        }
                
                signal_manager.mark_signal_failed(signal_id, user_id, 'No open position found')
                return {
                    'success': False,
                    'message': f'No open position found for {symbol}',
                    'error': 'NO_POSITION'
                }
            
            elif action == 'open':
                # فتح صفقة جديدة
                # البوت يقوم بتنفيذ أمر سوق Market Order مباشرة بمبلغ محدد
                # لا حاجة لحساب الكمية، المنصة تتعامل مع ذلك تلقائياً
                
                # استخراج TP/SL إذا كانت موجودة
                take_profit = signal_data.get('take_profit')
                stop_loss = signal_data.get('stop_loss')
                
                if take_profit:
                    take_profit = float(take_profit)
                if stop_loss:
                    stop_loss = float(stop_loss)
                
                # وضع الأمر - سيتم حساب الكمية من قبل المنصة بناءً على السعر الحالي
                result = account.place_order(
                    category=category,
                    symbol=symbol,
                    side=side,
                    order_type='Market',
                    qty=trade_amount,  # المبلغ بالدولار
                    leverage=leverage if category == 'linear' else None,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
                
                if result:
                    order_id = result.get('order_id')
                    executed_qty = result.get('qty', trade_amount)
                    executed_price = result.get('price', 0)
                    
                    # حفظ الصفقة في قاعدة البيانات
                    order_data = {
                        'order_id': order_id,
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': signal_type,  # buy, long, short
                        'entry_price': executed_price,
                        'quantity': executed_qty,
                        'signal_id': signal_id,
                        'signal_type': signal_type,
                        'market_type': market_type,
                        'status': 'OPEN'
                    }
                    
                    db_manager.create_order(order_data)
                    
                    # تحديث الإشارة
                    signal_manager.update_signal_with_order(signal_id, user_id, order_id, 'executed')
                    
                    logger.info(f"✅ تم تنفيذ أمر {signal_type} {symbol} على Bybit بنجاح [Order: {order_id}]")
                    
                    return {
                        'success': True,
                        'message': f'Order placed: {signal_type} {symbol}',
                        'order_id': order_id,
                        'symbol': symbol,
                        'side': signal_type,
                        'qty': executed_qty,
                        'price': executed_price,
                        'is_real': True
                    }
                else:
                    signal_manager.mark_signal_failed(signal_id, user_id, 'Failed to place order')
                    logger.error(f"❌ فشل تنفيذ أمر {signal_type} {symbol} على Bybit")
                    return {
                        'success': False,
                        'message': f'Failed to place order on Bybit',
                        'error': 'ORDER_FAILED'
                    }
            
            else:
                signal_manager.mark_signal_failed(signal_id, user_id, f'Invalid action: {action}')
                return {
                    'success': False,
                    'message': f'Invalid action: {action}',
                    'error': 'INVALID_ACTION'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة Bybit: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': str(e),
                'error': 'BYBIT_ERROR'
            }
    
    @staticmethod
    async def _execute_mexc_signal(account, signal_data: Dict, signal_result: Dict,
                                   trade_amount: float, user_id: int) -> Dict:
        """تنفيذ إشارة على MEXC (Spot فقط) مع نظام الإشارات المتقدم"""
        try:
            signal_id = signal_result.get('signal_id')
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '')
            action = signal_result.get('action')
            side_type = signal_result.get('side')
            
            logger.info(f"📡 MEXC SPOT: {signal_type} {symbol} [ID: {signal_id}]")
            
            # تحديد جهة الأمر لـ MEXC
            if side_type == 'Buy':
                side = 'BUY'
            else:
                side = 'SELL'
            
            # وضع الأمر - MEXC Market Order
            result = account.place_order(
                symbol=symbol,
                side=side,
                quantity=trade_amount,  # المبلغ بالدولار
                order_type='MARKET'
            )
            
            if result:
                order_id = result.get('orderId')
                executed_qty = result.get('executedQty', trade_amount)
                executed_price = result.get('price', 0)
                
                if action == 'open':
                    # حفظ الصفقة في قاعدة البيانات
                    order_data = {
                        'order_id': str(order_id),
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': signal_type,
                        'entry_price': executed_price,
                        'quantity': executed_qty,
                        'signal_id': signal_id,
                        'signal_type': signal_type,
                        'market_type': 'spot',
                        'status': 'OPEN'
                    }
                    
                    db_manager.create_order(order_data)
                    signal_manager.update_signal_with_order(signal_id, user_id, str(order_id), 'executed')
                
                elif action == 'close':
                    # تحديث الإشارة
                    signal_manager.update_signal_with_order(signal_id, user_id, str(order_id), 'closed')
                
                logger.info(f"✅ تم تنفيذ أمر {signal_type} {symbol} على MEXC بنجاح [Order: {order_id}]")
                
                return {
                    'success': True,
                    'message': f'Order placed: {signal_type} {symbol}',
                    'order_id': str(order_id),
                    'symbol': symbol,
                    'side': signal_type,
                    'qty': executed_qty,
                    'price': executed_price,
                    'is_real': True
                }
            else:
                signal_manager.mark_signal_failed(signal_id, user_id, 'Failed to place order')
                logger.error(f"❌ فشل تنفيذ أمر {signal_type} {symbol} على MEXC")
                return {
                    'success': False,
                    'message': f'Failed to place order on MEXC',
                    'error': 'ORDER_FAILED'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة MEXC: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': str(e),
                'error': 'MEXC_ERROR'
            }


# مثيل عام
signal_executor = SignalExecutor()

