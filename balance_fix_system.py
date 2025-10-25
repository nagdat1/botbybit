#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إصلاح مشكلة عدم كفاية الرصيد
يحسن التحقق من الرصيد قبل تنفيذ الأوامر
"""

import logging
from typing import Dict, Optional, Tuple
from real_account_manager import real_account_manager

logger = logging.getLogger(__name__)

class BalanceValidator:
    """مدقق الرصيد المحسن"""
    
    @staticmethod
    def validate_balance_before_order(
        account, 
        symbol: str, 
        side: str, 
        qty: float, 
        price: float, 
        market_type: str, 
        leverage: int = 1
    ) -> Tuple[bool, Dict]:
        """
        التحقق من الرصيد قبل تنفيذ الأمر
        
        Returns:
            (is_valid, validation_info)
        """
        try:
            logger.info(f"🔍 التحقق من الرصيد قبل الأمر: {side} {qty} {symbol} @ {price}")
            
            # تحديد نوع الحساب
            if market_type == 'futures':
                account_type = 'futures'
            else:
                account_type = 'spot'
            
            # جلب معلومات الرصيد
            balance_info = account.get_wallet_balance(account_type)
            
            if not balance_info:
                logger.error("❌ فشل جلب معلومات الرصيد")
                return False, {
                    'error': 'BALANCE_FETCH_FAILED',
                    'message': 'فشل جلب معلومات الرصيد من المنصة'
                }
            
            logger.info(f"📊 معلومات الرصيد: {balance_info}")
            
            # استخراج الرصيد المتاح
            if 'coins' in balance_info and 'USDT' in balance_info['coins']:
                available_usdt = balance_info['coins']['USDT']['equity']
                logger.info(f"💰 الرصيد المتاح: {available_usdt} USDT")
            else:
                logger.error("❌ لم يتم العثور على رصيد USDT")
                return False, {
                    'error': 'NO_USDT_BALANCE',
                    'message': 'لا يوجد رصيد USDT في الحساب'
                }
            
            # حساب المبلغ المطلوب
            if market_type == 'futures':
                # للفيوتشر: المبلغ المطلوب = (الكمية × السعر) / الرافعة
                required_margin = (qty * price) / leverage
            else:
                # للسبوت: المبلغ المطلوب = الكمية × السعر
                required_margin = qty * price
            
            # إضافة هامش أمان (5%)
            safety_margin = required_margin * 0.05
            total_required = required_margin + safety_margin
            
            logger.info(f"💸 المبلغ المطلوب: {required_margin:.2f} USDT")
            logger.info(f"🛡️ هامش الأمان: {safety_margin:.2f} USDT")
            logger.info(f"📈 الإجمالي المطلوب: {total_required:.2f} USDT")
            
            # التحقق من كفاية الرصيد
            if available_usdt >= total_required:
                logger.info("✅ الرصيد كافي للتنفيذ")
                return True, {
                    'available_balance': available_usdt,
                    'required_margin': required_margin,
                    'safety_margin': safety_margin,
                    'total_required': total_required,
                    'remaining_balance': available_usdt - total_required
                }
            else:
                logger.error(f"❌ الرصيد غير كافي: {available_usdt:.2f} < {total_required:.2f}")
                return False, {
                    'error': 'INSUFFICIENT_BALANCE',
                    'message': f'الرصيد غير كافي. متاح: {available_usdt:.2f} USDT، مطلوب: {total_required:.2f} USDT',
                    'available_balance': available_usdt,
                    'required_margin': required_margin,
                    'safety_margin': safety_margin,
                    'total_required': total_required,
                    'shortage': total_required - available_usdt
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من الرصيد: {e}")
            return False, {
                'error': 'VALIDATION_ERROR',
                'message': f'خطأ في التحقق من الرصيد: {str(e)}'
            }
    
    @staticmethod
    def suggest_optimal_quantity(
        account, 
        symbol: str, 
        side: str, 
        price: float, 
        market_type: str, 
        leverage: int = 1,
        max_percentage: float = 0.95
    ) -> Tuple[bool, float, Dict]:
        """
        اقتراح كمية مثلى بناءً على الرصيد المتاح
        
        Args:
            max_percentage: النسبة القصوى من الرصيد للاستخدام (0.95 = 95%)
        
        Returns:
            (success, optimal_qty, info)
        """
        try:
            logger.info(f"🎯 حساب الكمية المثلى لـ {symbol}")
            
            # تحديد نوع الحساب
            account_type = 'futures' if market_type == 'futures' else 'spot'
            
            # جلب الرصيد
            balance_info = account.get_wallet_balance(account_type)
            
            if not balance_info or 'coins' not in balance_info or 'USDT' not in balance_info['coins']:
                logger.error("❌ فشل جلب الرصيد")
                return False, 0.0, {'error': 'BALANCE_FETCH_FAILED'}
            
            available_usdt = balance_info['coins']['USDT']['equity']
            
            # حساب الكمية المثلى
            if market_type == 'futures':
                # للفيوتشر: الكمية = (الرصيد المتاح × النسبة × الرافعة) / السعر
                optimal_qty = (available_usdt * max_percentage * leverage) / price
            else:
                # للسبوت: الكمية = (الرصيد المتاح × النسبة) / السعر
                optimal_qty = (available_usdt * max_percentage) / price
            
            # ضمان الحد الأدنى
            min_qty = 0.001
            if optimal_qty < min_qty:
                logger.warning(f"⚠️ الكمية المحسوبة صغيرة جداً: {optimal_qty}")
                return False, 0.0, {
                    'error': 'QUANTITY_TOO_SMALL',
                    'message': f'الكمية المحسوبة صغيرة جداً: {optimal_qty:.6f}',
                    'available_balance': available_usdt,
                    'calculated_qty': optimal_qty,
                    'min_qty': min_qty
                }
            
            # تقريب الكمية
            optimal_qty = round(optimal_qty, 6)
            
            logger.info(f"✅ الكمية المثلى المقترحة: {optimal_qty} {symbol.split('USDT')[0]}")
            
            return True, optimal_qty, {
                'available_balance': available_usdt,
                'max_percentage': max_percentage,
                'optimal_qty': optimal_qty,
                'required_margin': (optimal_qty * price) / leverage if market_type == 'futures' else optimal_qty * price,
                'remaining_balance': available_usdt - ((optimal_qty * price) / leverage if market_type == 'futures' else optimal_qty * price)
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب الكمية المثلى: {e}")
            return False, 0.0, {'error': 'CALCULATION_ERROR', 'message': str(e)}


class EnhancedSignalExecutor:
    """منفذ الإشارات المحسن مع التحقق من الرصيد"""
    
    @staticmethod
    async def execute_signal_with_balance_check(
        user_id: int, 
        signal_data: Dict, 
        user_data: Dict
    ) -> Dict:
        """
        تنفيذ الإشارة مع التحقق المحسن من الرصيد
        """
        try:
            logger.info(f"🚀 تنفيذ إشارة محسنة للمستخدم {user_id}")
            
            # الحصول على الحساب الحقيقي
            real_account = real_account_manager.get_account(user_id)
            
            if not real_account:
                logger.error(f"❌ حساب حقيقي غير موجود للمستخدم {user_id}")
                return {
                    'success': False,
                    'message': 'Real account not found',
                    'error': 'ACCOUNT_NOT_FOUND'
                }
            
            # استخراج معلومات الإشارة
            action = signal_data.get('action', '').lower()
            symbol = signal_data.get('symbol', '')
            price = float(signal_data.get('price', 0)) if signal_data.get('price') else 0.0
            market_type = user_data.get('market_type', 'futures')
            leverage = user_data.get('leverage', 10)
            
            logger.info(f"📋 تفاصيل الإشارة: {action} {symbol} @ {price}")
            
            # جلب السعر إذا لم يكن موجوداً
            if not price or price == 0.0:
                try:
                    category = 'linear' if market_type == 'futures' else 'spot'
                    ticker = real_account.get_ticker(category, symbol)
                    if ticker and 'lastPrice' in ticker:
                        price = float(ticker['lastPrice'])
                        signal_data['price'] = price
                        logger.info(f"💰 السعر الحالي: {price}")
                    else:
                        return {
                            'success': False,
                            'message': f'Failed to get price for {symbol}',
                            'error': 'PRICE_FETCH_FAILED'
                        }
                except Exception as e:
                    logger.error(f"❌ خطأ في جلب السعر: {e}")
                    return {
                        'success': False,
                        'message': f'Error fetching price: {e}',
                        'error': 'PRICE_FETCH_ERROR'
                    }
            
            # حساب الكمية المطلوبة
            trade_amount = user_data.get('trade_amount', 100.0)
            
            if market_type == 'futures':
                qty = (trade_amount * leverage) / price
            else:
                qty = trade_amount / price
            
            # ضمان الحد الأدنى
            min_qty = 0.001
            if qty < min_qty:
                qty = min_qty
                logger.warning(f"⚠️ تم تعديل الكمية إلى الحد الأدنى: {qty}")
            
            qty = round(qty, 6)
            
            logger.info(f"📊 الكمية المحسوبة: {qty}")
            
            # التحقق من الرصيد
            is_valid, validation_info = BalanceValidator.validate_balance_before_order(
                real_account, symbol, action, qty, price, market_type, leverage
            )
            
            if not is_valid:
                logger.error(f"❌ فشل التحقق من الرصيد: {validation_info}")
                
                # محاولة اقتراح كمية مثلى
                success, optimal_qty, suggestion_info = BalanceValidator.suggest_optimal_quantity(
                    real_account, symbol, action, price, market_type, leverage
                )
                
                if success and optimal_qty > 0:
                    logger.info(f"💡 اقتراح كمية مثلى: {optimal_qty}")
                    
                    return {
                        'success': False,
                        'message': f'الرصيد غير كافي للكمية المطلوبة. الكمية المقترحة: {optimal_qty:.6f}',
                        'error': 'INSUFFICIENT_BALANCE',
                        'suggestion': {
                            'optimal_quantity': optimal_qty,
                            'reason': 'Balance too low for requested quantity',
                            'validation_info': validation_info,
                            'suggestion_info': suggestion_info
                        }
                    }
                else:
                    return {
                        'success': False,
                        'message': validation_info.get('message', 'الرصيد غير كافي'),
                        'error': validation_info.get('error', 'INSUFFICIENT_BALANCE'),
                        'validation_info': validation_info
                    }
            
            logger.info("✅ التحقق من الرصيد نجح، متابعة التنفيذ...")
            
            # تحديد جهة الأمر
            if action in ['buy', 'long']:
                side = 'Buy'
            elif action in ['sell', 'short']:
                side = 'Sell'
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'error': 'INVALID_ACTION'
                }
            
            # تنفيذ الأمر
            category = 'linear' if market_type == 'futures' else 'spot'
            
            result = real_account.place_order(
                category=category,
                symbol=symbol,
                side=side,
                order_type='Market',
                qty=qty,
                leverage=leverage if market_type == 'futures' else None
            )
            
            # معالجة النتيجة
            if result and not result.get('error'):
                logger.info(f"✅ تم تنفيذ الأمر بنجاح: {result}")
                return {
                    'success': True,
                    'message': f'Order placed successfully: {side} {qty} {symbol}',
                    'order_id': result.get('order_id'),
                    'symbol': symbol,
                    'side': side,
                    'qty': qty,
                    'price': price,
                    'validation_info': validation_info,
                    'is_real': True
                }
            else:
                logger.error(f"❌ فشل تنفيذ الأمر: {result}")
                return {
                    'success': False,
                    'message': f'Failed to place order: {result.get("error", "Unknown error")}',
                    'error': 'ORDER_FAILED',
                    'error_details': result,
                    'validation_info': validation_info
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الإشارة المحسنة: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error in enhanced signal execution: {str(e)}',
                'error': 'EXECUTION_ERROR'
            }


# مثيل عام
enhanced_signal_executor = EnhancedSignalExecutor()
balance_validator = BalanceValidator()
