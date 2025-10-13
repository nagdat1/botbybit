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
        
        نظام الإشارات:
        SPOT:
          - action: "buy" -> فتح صفقة شراء
          - action: "sell" -> إغلاق الصفقة
        
        FUTURES:
          - type: "LONG", action: "open" -> فتح Long
          - type: "LONG", action: "close" -> إغلاق Long
          - type: "SHORT", action: "open" -> فتح Short
          - type: "SHORT", action: "close" -> إغلاق Short
        
        Args:
            user_id: معرف المستخدم
            signal_data: بيانات الإشارة
            user_data: إعدادات المستخدم
            
        Returns:
            نتيجة التنفيذ
        """
        try:
            account_type = user_data.get('account_type', 'demo')
            exchange = user_data.get('exchange', 'bybit')
            market_type = user_data.get('market_type', 'spot')
            
            symbol = signal_data.get('symbol', '')
            action = signal_data.get('action', '').lower()
            signal_type = signal_data.get('type', '').upper()
            
            logger.info(f"🎯 إشارة للمستخدم {user_id}: {symbol} - Type: {signal_type or 'SPOT'}, Action: {action}")
            logger.info(f"📊 الحساب: {account_type}, المنصة: {exchange}, السوق المختار: {market_type}")
            
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
        """
        تنفيذ إشارة على Bybit حسب النظام الجديد
        
        SPOT: action = "buy" أو "sell"
        FUTURES: type = "LONG"/"SHORT", action = "open"/"close"
        """
        try:
            symbol = signal_data.get('symbol', '')
            action = signal_data.get('action', '').lower()
            signal_type = signal_data.get('type', '').upper()
            
            # تحديد نوع السوق من الإشارة
            if signal_type in ['LONG', 'SHORT']:
                # إشارة Futures
                category = 'linear'
                is_futures = True
                logger.info(f"📡 Bybit FUTURES: {signal_type} {action} {symbol}")
            else:
                # إشارة Spot
                category = 'spot'
                is_futures = False
                logger.info(f"📡 Bybit SPOT: {action} {symbol}")
            
            # معالجة إشارات SPOT
            if not is_futures:
                if action == 'buy':
                    # فتح صفقة شراء Spot
                    side = 'Buy'
                    
                    # حساب الكمية
                    price = float(signal_data.get('price', 0))
                    if price == 0:
                        # جلب السعر الحالي
                        logger.warning("⚠️ لم يتم توفير السعر، سيتم استخدام Market Order")
                        qty = trade_amount / 50000  # قيمة افتراضية
                    else:
                        qty = trade_amount / price
                    
                    result = account.place_order(
                        category=category,
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 6)
                    )
                    
                    if result:
                        logger.info(f"✅ تم فتح صفقة Spot BUY {symbol}")
                        return {
                            'success': True,
                            'message': f'SPOT BUY opened: {symbol}',
                            'order_id': result.get('order_id'),
                            'is_real': True
                        }
                
                elif action == 'sell':
                    # إغلاق صفقة Spot (بيع الرصيد)
                    positions = account.get_open_positions(category)
                    target_position = next((p for p in positions if p['symbol'] == symbol), None)
                    
                    if target_position:
                        result = account.close_position(category, symbol, 'Buy')
                        if result:
                            logger.info(f"✅ تم إغلاق صفقة Spot {symbol}")
                            return {
                                'success': True,
                                'message': f'SPOT SELL closed: {symbol}',
                                'order_id': result.get('order_id'),
                                'is_real': True
                            }
                    
                    return {
                        'success': False,
                        'message': f'No SPOT position found for {symbol}',
                        'error': 'NO_POSITION'
                    }
            
            # معالجة إشارات FUTURES
            else:
                if action == 'open':
                    # فتح صفقة Futures
                    side = 'Buy' if signal_type == 'LONG' else 'Sell'
                    
                    # حساب الكمية مع الرافعة
                    price = float(signal_data.get('price', 0))
                    if price == 0:
                        qty = (trade_amount * leverage) / 50000  # قيمة افتراضية
                    else:
                        qty = (trade_amount * leverage) / price
                    
                    # استخراج TP/SL
                    take_profit = float(signal_data.get('take_profit')) if signal_data.get('take_profit') else None
                    stop_loss = float(signal_data.get('stop_loss')) if signal_data.get('stop_loss') else None
                    
                    result = account.place_order(
                        category=category,
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=round(qty, 4),
                        leverage=leverage,
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    
                    if result:
                        logger.info(f"✅ تم فتح صفقة {signal_type} {symbol}")
                        return {
                            'success': True,
                            'message': f'{signal_type} opened: {symbol}',
                            'order_id': result.get('order_id'),
                            'is_real': True
                        }
                
                elif action == 'close':
                    # إغلاق صفقة Futures
                    positions = account.get_open_positions(category)
                    target_position = next((p for p in positions if p['symbol'] == symbol), None)
                    
                    if target_position:
                        result = account.close_position(category, symbol, target_position['side'])
                        if result:
                            logger.info(f"✅ تم إغلاق صفقة {signal_type} {symbol}")
                            return {
                                'success': True,
                                'message': f'{signal_type} closed: {symbol}',
                                'order_id': result.get('order_id'),
                                'is_real': True
                            }
                    
                    return {
                        'success': False,
                        'message': f'No {signal_type} position found for {symbol}',
                        'error': 'NO_POSITION'
                    }
            
            return {
                'success': False,
                'message': f'Invalid signal format',
                'error': 'INVALID_SIGNAL'
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

