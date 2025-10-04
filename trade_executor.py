#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تنفيذ أوامر الصفقات
يدعم تنفيذ TP, SL, الإغلاق الجزئي والكامل
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

class TradeExecutor:
    """منفذ أوامر الصفقات"""
    
    def __init__(self, trading_bot=None):
        self.trading_bot = trading_bot
        self.active_orders = {}  # تتبع الأوامر النشطة
    
    def _find_position_in_accounts(self, position_id: str) -> tuple:
        """البحث عن الصفقة في الحسابات التجريبية"""
        try:
            if not self.trading_bot:
                logger.warning("البوت غير متاح للبحث عن الصفقة")
                return None, None
            
            logger.info(f"البحث عن الصفقة في الحسابات: {position_id}")
            
            # البحث في حساب السبوت
            if hasattr(self.trading_bot, 'demo_account_spot') and self.trading_bot.demo_account_spot:
                if hasattr(self.trading_bot.demo_account_spot, 'positions'):
                    if position_id in self.trading_bot.demo_account_spot.positions:
                        logger.info(f"تم العثور على الصفقة في حساب السبوت: {position_id}")
                        return self.trading_bot.demo_account_spot, 'spot'
            
            # البحث في حساب الفيوتشر
            if hasattr(self.trading_bot, 'demo_account_futures') and self.trading_bot.demo_account_futures:
                if hasattr(self.trading_bot.demo_account_futures, 'positions'):
                    if position_id in self.trading_bot.demo_account_futures.positions:
                        logger.info(f"تم العثور على الصفقة في حساب الفيوتشر: {position_id}")
                        return self.trading_bot.demo_account_futures, 'futures'
            
            logger.warning(f"لم يتم العثور على الصفقة في أي حساب: {position_id}")
            return None, None
        except Exception as e:
            logger.error(f"خطأ في البحث عن الصفقة: {e}")
            return None, None
        
    async def set_take_profit(self, position_id: str, percent: float) -> Dict:
        """وضع هدف الربح (Take Profit)"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {'success': False, 'error': 'البوت غير متاح'}
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return {'success': False, 'error': 'الصفقة غير موجودة'}
            
            # حساب سعر TP
            entry_price = position_info.get('entry_price', 0)
            side = position_info.get('side', 'buy')
            
            if entry_price == 0:
                return {'success': False, 'error': 'سعر الدخول غير صحيح'}
            
            # حساب سعر TP بناءً على اتجاه الصفقة
            if side.lower() == "buy":
                tp_price = entry_price * (1 + percent / 100)
            else:
                tp_price = entry_price * (1 - percent / 100)
            
            # حفظ أمر TP
            tp_order = {
                'type': 'TP',
                'position_id': position_id,
                'percent': percent,
                'target_price': tp_price,
                'created_at': datetime.now(),
                'status': 'ACTIVE'
            }
            
            self.active_orders[f"tp_{position_id}_{percent}"] = tp_order
            
            # إذا كان التداول حقيقي، وضع الأمر في المنصة
            if self.trading_bot.user_settings.get('account_type') == 'real':
                success = await self._place_real_tp_order(position_info, tp_price)
                if not success:
                    return {'success': False, 'error': 'فشل في وضع أمر TP في المنصة'}
            
            return {
                'success': True,
                'data': {
                    'order_id': f"tp_{position_id}_{percent}",
                    'target_price': tp_price,
                    'percent': percent,
                    'created_at': tp_order['created_at']
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في وضع TP: {e}")
            return {'success': False, 'error': str(e)}
    
    async def set_stop_loss(self, position_id: str, percent: float) -> Dict:
        """وضع وقف الخسارة (Stop Loss)"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {'success': False, 'error': 'البوت غير متاح'}
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return {'success': False, 'error': 'الصفقة غير موجودة'}
            
            # حساب سعر SL
            entry_price = position_info.get('entry_price', 0)
            side = position_info.get('side', 'buy')
            
            if entry_price == 0:
                return {'success': False, 'error': 'سعر الدخول غير صحيح'}
            
            # حساب سعر SL بناءً على اتجاه الصفقة
            if side.lower() == "buy":
                sl_price = entry_price * (1 - percent / 100)
            else:
                sl_price = entry_price * (1 + percent / 100)
            
            # حفظ أمر SL
            sl_order = {
                'type': 'SL',
                'position_id': position_id,
                'percent': percent,
                'target_price': sl_price,
                'created_at': datetime.now(),
                'status': 'ACTIVE'
            }
            
            self.active_orders[f"sl_{position_id}_{percent}"] = sl_order
            
            # إذا كان التداول حقيقي، وضع الأمر في المنصة
            if self.trading_bot.user_settings.get('account_type') == 'real':
                success = await self._place_real_sl_order(position_info, sl_price)
                if not success:
                    return {'success': False, 'error': 'فشل في وضع أمر SL في المنصة'}
            
            return {
                'success': True,
                'data': {
                    'order_id': f"sl_{position_id}_{percent}",
                    'target_price': sl_price,
                    'percent': percent,
                    'created_at': sl_order['created_at']
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في وضع SL: {e}")
            return {'success': False, 'error': str(e)}
    
    async def partial_close(self, position_id: str, percent: float) -> Dict:
        """إغلاق جزئي للصفقة"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {'success': False, 'error': 'البوت غير متاح'}
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return {'success': False, 'error': 'الصفقة غير موجودة'}
            
            # التحقق من صحة النسبة
            if percent <= 0 or percent >= 100:
                return {'success': False, 'error': 'النسبة يجب أن تكون بين 0 و 100'}
            
            # الحصول على السعر الحالي
            current_price = position_info.get('current_price', position_info.get('entry_price'))
            if not current_price:
                return {'success': False, 'error': 'السعر الحالي غير متاح'}
            
            # حساب الربح/الخسارة الجزئي
            entry_price = position_info.get('entry_price', 0)
            side = position_info.get('side', 'buy')
            margin_amount = position_info.get('margin_amount', position_info.get('amount', 100))
            
            # حساب PnL الجزئي
            partial_amount = margin_amount * (percent / 100)
            
            if side.lower() == "buy":
                partial_pnl = (current_price - entry_price) / entry_price * partial_amount
            else:
                partial_pnl = (entry_price - current_price) / entry_price * partial_amount
            
            # تنفيذ الإغلاق الجزئي
            if self.trading_bot.user_settings.get('account_type') == 'real':
                # تنفيذ حقيقي
                success = await self._execute_real_partial_close(position_info, percent, current_price)
                if not success:
                    return {'success': False, 'error': 'فشل في تنفيذ الإغلاق الجزئي في المنصة'}
            else:
                # تنفيذ تجريبي
                success = await self._execute_demo_partial_close(position_info, percent, current_price, partial_pnl)
                if not success:
                    return {'success': False, 'error': 'فشل في تنفيذ الإغلاق الجزئي التجريبي'}
            
            return {
                'success': True,
                'data': {
                    'partial_percent': percent,
                    'partial_amount': partial_amount,
                    'partial_pnl': partial_pnl,
                    'current_price': current_price,
                    'executed_at': datetime.now()
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الإغلاق الجزئي: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close_position(self, position_id: str) -> Dict:
        """إغلاق الصفقة بالكامل"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return {'success': False, 'error': 'البوت غير متاح'}
            
            position_info = self.trading_bot.open_positions.get(position_id)
            if not position_info:
                return {'success': False, 'error': 'الصفقة غير موجودة'}
            
            # الحصول على السعر الحالي
            current_price = position_info.get('current_price', position_info.get('entry_price'))
            if not current_price:
                return {'success': False, 'error': 'السعر الحالي غير متاح'}
            
            # حساب الربح/الخسارة النهائي
            entry_price = position_info.get('entry_price', 0)
            side = position_info.get('side', 'buy')
            margin_amount = position_info.get('margin_amount', position_info.get('amount', 100))
            
            # حساب PnL الكامل
            if side.lower() == "buy":
                total_pnl = (current_price - entry_price) / entry_price * margin_amount
            else:
                total_pnl = (entry_price - current_price) / entry_price * margin_amount
            
            # تنفيذ الإغلاق الكامل
            if self.trading_bot.user_settings.get('account_type') == 'real':
                # تنفيذ حقيقي
                success = await self._execute_real_close(position_info, current_price)
                if not success:
                    return {'success': False, 'error': 'فشل في إغلاق الصفقة في المنصة'}
            else:
                # تنفيذ تجريبي
                success = await self._execute_demo_close(position_info, current_price, total_pnl)
                if not success:
                    return {'success': False, 'error': 'فشل في إغلاق الصفقة التجريبية'}
            
            # حذف الأوامر النشطة للصفقة
            self._cleanup_position_orders(position_id)
            
            return {
                'success': True,
                'data': {
                    'total_pnl': total_pnl,
                    'closing_price': current_price,
                    'closed_at': datetime.now()
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _place_real_tp_order(self, position_info: Dict, tp_price: float) -> bool:
        """وضع أمر TP حقيقي في المنصة"""
        try:
            if not self.trading_bot.bybit_api:
                return False
            
            symbol = position_info.get('symbol')
            side = position_info.get('side')
            quantity = str(position_info.get('margin_amount', 100))
            category = position_info.get('category', 'spot')
            
            # تحويل الاتجاه للعكس (لإغلاق الصفقة)
            opposite_side = "Sell" if side.lower() == "buy" else "Buy"
            
            # وضع أمر Limit للـ TP
            response = self.trading_bot.bybit_api.place_order(
                symbol=symbol,
                side=opposite_side,
                order_type="Limit",
                qty=quantity,
                price=str(tp_price),
                category=category
            )
            
            return response.get("retCode") == 0
            
        except Exception as e:
            logger.error(f"خطأ في وضع أمر TP حقيقي: {e}")
            return False
    
    async def _place_real_sl_order(self, position_info: Dict, sl_price: float) -> bool:
        """وضع أمر SL حقيقي في المنصة"""
        try:
            if not self.trading_bot.bybit_api:
                return False
            
            symbol = position_info.get('symbol')
            side = position_info.get('side')
            quantity = str(position_info.get('margin_amount', 100))
            category = position_info.get('category', 'spot')
            
            # تحويل الاتجاه للعكس (لإغلاق الصفقة)
            opposite_side = "Sell" if side.lower() == "buy" else "Buy"
            
            # وضع أمر Stop للـ SL
            response = self.trading_bot.bybit_api.place_order(
                symbol=symbol,
                side=opposite_side,
                order_type="Stop",
                qty=quantity,
                price=str(sl_price),
                category=category
            )
            
            return response.get("retCode") == 0
            
        except Exception as e:
            logger.error(f"خطأ في وضع أمر SL حقيقي: {e}")
            return False
    
    async def _execute_real_partial_close(self, position_info: Dict, percent: float, current_price: float) -> bool:
        """تنفيذ إغلاق جزئي حقيقي"""
        try:
            if not self.trading_bot.bybit_api:
                return False
            
            symbol = position_info.get('symbol')
            side = position_info.get('side')
            total_quantity = position_info.get('margin_amount', 100)
            partial_quantity = total_quantity * (percent / 100)
            category = position_info.get('category', 'spot')
            
            # تحويل الاتجاه للعكس (لإغلاق الصفقة)
            opposite_side = "Sell" if side.lower() == "buy" else "Buy"
            
            # وضع أمر Market للإغلاق الجزئي
            response = self.trading_bot.bybit_api.place_order(
                symbol=symbol,
                side=opposite_side,
                order_type="Market",
                qty=str(partial_quantity),
                category=category
            )
            
            if response.get("retCode") == 0:
                # تحديث معلومات الصفقة
                remaining_percent = 100 - percent
                position_info['margin_amount'] = total_quantity * (remaining_percent / 100)
                position_info['amount'] = position_info['margin_amount']  # للسبوت
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي الحقيقي: {e}")
            return False
    
    async def _execute_demo_partial_close(self, position_info: Dict, percent: float, current_price: float, partial_pnl: float) -> bool:
        """تنفيذ إغلاق جزئي تجريبي"""
        try:
            # تحديد الحساب التجريبي الصحيح
            market_type = position_info.get('account_type', 'spot')
            
            if market_type == 'futures':
                account = self.trading_bot.demo_account_futures
            else:
                account = self.trading_bot.demo_account_spot
            
            # حساب المبلغ الجزئي
            total_amount = position_info.get('margin_amount', position_info.get('amount', 100))
            partial_amount = total_amount * (percent / 100)
            
            # تحديث الرصيد
            account.balance += partial_pnl
            
            # تحديث معلومات الصفقة
            remaining_percent = 100 - percent
            position_info['margin_amount'] = total_amount * (remaining_percent / 100)
            position_info['amount'] = position_info['margin_amount']
            
            # تحديث الهامش المحجوز للفيوتشر
            if market_type == 'futures':
                account.margin_locked -= partial_amount
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي التجريبي: {e}")
            return False
    
    async def _execute_real_close(self, position_info: Dict, current_price: float) -> bool:
        """تنفيذ إغلاق حقيقي"""
        try:
            if not self.trading_bot.bybit_api:
                return False
            
            symbol = position_info.get('symbol')
            side = position_info.get('side')
            quantity = str(position_info.get('margin_amount', 100))
            category = position_info.get('category', 'spot')
            
            # تحويل الاتجاه للعكس (لإغلاق الصفقة)
            opposite_side = "Sell" if side.lower() == "buy" else "Buy"
            
            # وضع أمر Market للإغلاق الكامل
            response = self.trading_bot.bybit_api.place_order(
                symbol=symbol,
                side=opposite_side,
                order_type="Market",
                qty=quantity,
                category=category
            )
            
            if response.get("retCode") == 0:
                # حذف الصفقة من القائمة
                if hasattr(self.trading_bot, 'open_positions'):
                    position_id = None
                    for pid, info in self.trading_bot.open_positions.items():
                        if info == position_info:
                            position_id = pid
                            break
                    
                    if position_id:
                        del self.trading_bot.open_positions[position_id]
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الحقيقي: {e}")
            return False
    
    async def _execute_demo_close(self, position_info: Dict, current_price: float, total_pnl: float) -> bool:
        """تنفيذ إغلاق تجريبي"""
        try:
            # الحصول على position_id من البيانات
            position_id = position_info.get('position_id')
            if not position_id:
                logger.error("position_id غير متاح في بيانات الصفقة")
                return False
            
            logger.info(f"تنفيذ إغلاق تجريبي للصفقة: {position_id}")
            
            # البحث عن الصفقة في الحسابات
            account, market_type = self._find_position_in_accounts(position_id)
            
            if not account:
                logger.error(f"لم يتم العثور على الصفقة {position_id} في الحسابات")
                return False
            
            logger.info(f"تم العثور على الصفقة في حساب {market_type}")
            
            # إغلاق الصفقة حسب نوع السوق
            if market_type == 'futures':
                success, result = account.close_futures_position(position_id, current_price)
            else:
                success, result = account.close_spot_position(position_id, current_price)
            
            if success:
                logger.info(f"تم إغلاق الصفقة {position_id} بنجاح")
                
                # حذف الصفقة من القائمة العامة
                if hasattr(self.trading_bot, 'open_positions'):
                    if position_id in self.trading_bot.open_positions:
                        del self.trading_bot.open_positions[position_id]
                        logger.info(f"تم حذف الصفقة {position_id} من القائمة العامة")
                
                return True
            else:
                logger.error(f"فشل في إغلاق الصفقة {position_id}: {result}")
                return False
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق التجريبي: {e}")
            return False
    
    def _cleanup_position_orders(self, position_id: str):
        """تنظيف الأوامر النشطة للصفقة"""
        try:
            orders_to_remove = []
            for order_id, order in self.active_orders.items():
                if order.get('position_id') == position_id:
                    orders_to_remove.append(order_id)
            
            for order_id in orders_to_remove:
                del self.active_orders[order_id]
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف أوامر الصفقة: {e}")
    
    def get_active_orders(self, position_id: str = None) -> Dict:
        """الحصول على الأوامر النشطة"""
        try:
            if position_id:
                return {k: v for k, v in self.active_orders.items() 
                       if v.get('position_id') == position_id}
            return self.active_orders
        except Exception as e:
            logger.error(f"خطأ في الحصول على الأوامر النشطة: {e}")
            return {}
    
    async def check_tp_sl_triggers(self):
        """فحص وتحقق من أوامر TP و SL"""
        try:
            if not self.trading_bot or not hasattr(self.trading_bot, 'open_positions'):
                return
            
            # تحديث أسعار الصفقات المفتوحة أولاً
            await self.trading_bot.update_open_positions_prices()
            
            triggered_orders = []
            
            for order_id, order in self.active_orders.items():
                if order.get('status') != 'ACTIVE':
                    continue
                
                position_id = order.get('position_id')
                position_info = self.trading_bot.open_positions.get(position_id)
                
                if not position_info:
                    continue
                
                current_price = position_info.get('current_price', 0)
                target_price = order.get('target_price', 0)
                order_type = order.get('type')
                
                if not current_price or not target_price:
                    continue
                
                # فحص TP
                if order_type == 'TP':
                    position_side = position_info.get('side', 'buy')
                    
                    if position_side.lower() == 'buy' and current_price >= target_price:
                        # TP للصفقة الشرائية تم تفعيله
                        triggered_orders.append(order_id)
                    elif position_side.lower() == 'sell' and current_price <= target_price:
                        # TP للصفقة البيعية تم تفعيله
                        triggered_orders.append(order_id)
                
                # فحص SL
                elif order_type == 'SL':
                    position_side = position_info.get('side', 'buy')
                    
                    if position_side.lower() == 'buy' and current_price <= target_price:
                        # SL للصفقة الشرائية تم تفعيله
                        triggered_orders.append(order_id)
                    elif position_side.lower() == 'sell' and current_price >= target_price:
                        # SL للصفقة البيعية تم تفعيله
                        triggered_orders.append(order_id)
            
            # تنفيذ الأوامر المفعلة
            for order_id in triggered_orders:
                order = self.active_orders[order_id]
                position_id = order.get('position_id')
                order_type = order.get('type')
                
                if order_type == 'TP':
                    # تنفيذ TP
                    result = await self.set_take_profit(position_id, order.get('percent'))
                    if result['success']:
                        logger.info(f"تم تنفيذ TP للصفقة {position_id}")
                        order['status'] = 'EXECUTED'
                
                elif order_type == 'SL':
                    # تنفيذ SL (إغلاق كامل)
                    result = await self.close_position(position_id)
                    if result['success']:
                        logger.info(f"تم تنفيذ SL للصفقة {position_id}")
                        order['status'] = 'EXECUTED'
                        
        except Exception as e:
            logger.error(f"خطأ في فحص أوامر TP/SL: {e}")

# إنشاء مثيل عام لمنفذ الأوامر
trade_executor = TradeExecutor()