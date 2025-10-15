#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منفذ الإشارات - تنفيذ إشارات التداول على الحسابات الحقيقية
"""

import logging
from typing import Dict, Optional
from real_account_manager import real_account_manager

logger = logging.getLogger(__name__)

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
                        # جلب السعر من MEXC أو منصات أخرى
                        logger.warning(f"⚠️ جلب السعر من {exchange} غير مدعوم حالياً")
                        return {
                            'success': False,
                            'message': f'Price fetching from {exchange} not implemented',
                            'error': 'PRICE_FETCH_NOT_SUPPORTED'
                        }
                except Exception as e:
                    logger.error(f"❌ خطأ في جلب السعر: {e}")
                    return {
                        'success': False,
                        'message': f'Error fetching price: {e}',
                        'error': 'PRICE_FETCH_ERROR'
                    }
            
            # معلومات التداول
            trade_amount = user_data.get('trade_amount', 100.0)
            leverage = user_data.get('leverage', 10)
            
            logger.info(f"💰 مبلغ التداول: {trade_amount}, الرافعة: {leverage}")
            
            # تنفيذ الإشارة حسب المنصة
            if exchange == 'bybit':
                return await SignalExecutor._execute_bybit_signal(
                    real_account, signal_data, market_type, 
                    trade_amount, leverage, user_id
                )
            elif exchange == 'mexc':
                return await SignalExecutor._execute_mexc_signal(
                    real_account, signal_data, trade_amount, user_id
                )
            else:
                return {
                    'success': False,
                    'message': f'Unsupported exchange: {exchange}',
                    'error': 'UNSUPPORTED_EXCHANGE'
                }
                
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
            action = signal_data.get('action', '').lower()
            symbol = signal_data.get('symbol', '')
            
            # تحديد الفئة
            category = 'linear' if market_type == 'futures' else 'spot'
            
            logger.info(f"📡 Bybit {category.upper()}: {action} {symbol}")
            
            # تحديد جهة الأمر
            if action in ['buy', 'long']:
                side = 'Buy'
            elif action in ['sell', 'short']:
                side = 'Sell'
            elif action == 'close':
                # إغلاق الصفقة المفتوحة
                positions = account.get_open_positions(category)
                
                # تحديد الجهة المراد إغلاقها
                close_side = signal_data.get('close_side', '').lower()
                
                if close_side:
                    # إغلاق جهة محددة (long أو short)
                    target_position = next(
                        (p for p in positions 
                         if p['symbol'] == symbol and p['side'].lower() == close_side),
                        None
                    )
                else:
                    # إغلاق أي صفقة مفتوحة على هذا الرمز
                    target_position = next((p for p in positions if p['symbol'] == symbol), None)
                
                if target_position:
                    result = account.close_position(category, symbol, target_position['side'])
                    if result:
                        logger.info(f"✅ تم إغلاق صفقة {symbol} {close_side.upper()} بنجاح")
                        return {
                            'success': True,
                            'message': f'Position closed: {symbol} {close_side.upper()}',
                            'order_id': result.get('order_id'),
                            'is_real': True
                        }
                
                close_msg = f'{close_side.upper()} ' if close_side else ''
                return {
                    'success': False,
                    'message': f'No open {close_msg}position found for {symbol}',
                    'error': 'NO_POSITION'
                }
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'error': 'INVALID_ACTION'
                }
            
            # حساب الكمية بناءً على مبلغ التداول
            if category == 'linear':
                # للفيوتشر مع الرافعة
                qty = (trade_amount * leverage) / float(signal_data.get('price', 1))
            else:
                # للسبوت بدون رافعة
                qty = trade_amount / float(signal_data.get('price', 1))
            
            # استخراج TP/SL إذا كانت موجودة
            take_profit = signal_data.get('take_profit')
            stop_loss = signal_data.get('stop_loss')
            
            if take_profit:
                take_profit = float(take_profit)
            if stop_loss:
                stop_loss = float(stop_loss)
            
            # وضع الأمر
            result = account.place_order(
                category=category,
                symbol=symbol,
                side=side,
                order_type='Market',
                qty=round(qty, 4),
                leverage=leverage if category == 'linear' else None,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
            
            if result:
                logger.info(f"✅ تم تنفيذ أمر {side} {symbol} على Bybit بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                
                return {
                    'success': True,
                    'message': f'Order placed: {side} {symbol}',
                    'order_id': result.get('order_id'),
                    'symbol': symbol,
                    'side': side,
                    'qty': qty,
                    'is_real': True
                }
            else:
                logger.error(f"❌ فشل تنفيذ أمر {side} {symbol} على Bybit")
                return {
                    'success': False,
                    'message': f'Failed to place order on Bybit',
                    'error': 'ORDER_FAILED'
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
            
            # حساب الكمية
            price = float(signal_data.get('price', 1))
            quantity = trade_amount / price
            
            # وضع الأمر
            result = account.place_order(
                symbol=symbol,
                side=side,
                quantity=round(quantity, 6),
                order_type='MARKET'
            )
            
            if result:
                logger.info(f"✅ تم تنفيذ أمر {side} {symbol} على MEXC بنجاح")
                logger.info(f"📋 تفاصيل الأمر: {result}")
                
                return {
                    'success': True,
                    'message': f'Order placed: {side} {symbol}',
                    'order_id': result.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'qty': quantity,
                    'is_real': True
                }
            else:
                logger.error(f"❌ فشل تنفيذ أمر {side} {symbol} على MEXC")
                return {
                    'success': False,
                    'message': f'Failed to place order on MEXC',
                    'error': 'ORDER_FAILED'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ إشارة MEXC: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': 'MEXC_ERROR'
            }


# مثيل عام
signal_executor = SignalExecutor()

