#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الإغلاق الجزئي للصفقات - دعم Spot و Futures
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PartialCloseHandler:
    """معالج الإغلاق الجزئي للصفقات"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def calculate_partial_close_quantity(self, position_info: Dict, close_percent: float) -> Dict[str, float]:
        """حساب الكمية المراد إغلاقها جزئياً"""
        try:
            market_type = position_info.get('market_type', 'spot')
            quantity = position_info.get('quantity', 0)
            
            # حساب الكمية المراد إغلاقها
            close_quantity = quantity * (close_percent / 100.0)
            remaining_quantity = quantity - close_quantity
            
            result = {
                'close_quantity': close_quantity,
                'remaining_quantity': remaining_quantity,
                'close_percent': close_percent
            }
            
            if market_type == 'futures':
                # للفيوتشر، نحتاج أيضاً لحساب الهامش المتبقي
                margin_amount = position_info.get('margin_amount', 0)
                remaining_margin = margin_amount * (remaining_quantity / quantity) if quantity > 0 else 0
                close_margin = margin_amount - remaining_margin
                
                result['close_margin'] = close_margin
                result['remaining_margin'] = remaining_margin
            
            logger.info(f"✅ حساب الإغلاق الجزئي: {close_percent}% = {close_quantity} من {quantity}")
            return result
            
        except Exception as e:
            logger.error(f"خطأ في حساب الكمية المراد إغلاقها: {e}")
            return {}
    
    def execute_partial_close_spot(self, user_id: int, position_id: str, position_info: Dict, 
                                   close_percent: float, api_client = None) -> Dict[str, Any]:
        """تنفيذ إغلاق جزئي لصفقة Spot"""
        try:
            logger.info(f"🔄 تنفيذ إغلاق جزئي Spot: {position_id} - {close_percent}%")
            
            # حساب الكمية
            calc_result = self.calculate_partial_close_quantity(position_info, close_percent)
            if not calc_result:
                return {'success': False, 'message': 'فشل في حساب الكمية'}
            
            symbol = position_info['symbol']
            side = position_info['side']
            close_quantity = calc_result['close_quantity']
            
            account_type = position_info.get('account_type', 'demo')
            
            if account_type == 'real' and api_client:
                # إغلاق حقيقي عبر API
                try:
                    # تنفيذ أمر معاكس
                    close_side = 'SELL' if side.upper() == 'BUY' else 'BUY'
                    
                    order_result = api_client.place_order(
                        symbol=symbol,
                        side=close_side,
                        order_type='MARKET',
                        qty=close_quantity,
                        category='spot'
                    )
                    
                    if not order_result or order_result.get('retCode') != 0:
                        return {
                            'success': False,
                            'message': f"فشل تنفيذ الأمر: {order_result.get('retMsg', 'خطأ غير معروف')}"
                        }
                    
                    # الحصول على سعر الإغلاق
                    close_price = float(order_result.get('result', {}).get('avgPrice', 0))
                    if not close_price:
                        close_price = api_client.get_ticker_price(symbol, 'spot')
                    
                    logger.info(f"✅ تم الإغلاق الجزئي الحقيقي: {close_quantity} @ {close_price}")
                    
                except Exception as e:
                    logger.error(f"خطأ في الإغلاق الجزئي الحقيقي: {e}")
                    return {'success': False, 'message': f'خطأ في تنفيذ الأمر: {e}'}
            
            else:
                # إغلاق تجريبي
                close_price = position_info.get('current_price', position_info.get('entry_price', 0))
                logger.info(f"✅ تم الإغلاق الجزئي التجريبي: {close_quantity} @ {close_price}")
            
            # حساب PnL للجزء المغلق
            entry_price = position_info['entry_price']
            
            if side.upper() == 'BUY':
                partial_pnl = (close_price - entry_price) * close_quantity
            else:
                partial_pnl = (entry_price - close_price) * close_quantity
            
            # إنشاء سجل الإغلاق الجزئي
            partial_close_record = {
                'timestamp': datetime.now().isoformat(),
                'close_percent': close_percent,
                'close_quantity': close_quantity,
                'close_price': close_price,
                'partial_pnl': partial_pnl,
                'remaining_quantity': calc_result['remaining_quantity']
            }
            
            # تحديث قاعدة البيانات
            order = self.db_manager.get_order(position_id)
            if order:
                # إضافة السجل إلى التاريخ
                partial_closes_history = order.get('partial_closes_history', [])
                if isinstance(partial_closes_history, str):
                    partial_closes_history = json.loads(partial_closes_history)
                
                partial_closes_history.append(partial_close_record)
                
                # تحديث الكمية المتبقية
                updates = {
                    'quantity': calc_result['remaining_quantity'],
                    'partial_closes_history': partial_closes_history
                }
                
                # إذا تم إغلاق 100%، غلق الصفقة
                if calc_result['remaining_quantity'] <= 0.0001:
                    updates['status'] = 'CLOSED'
                    updates['close_time'] = datetime.now().isoformat()
                    updates['close_price'] = close_price
                
                self.db_manager.update_order(position_id, updates)
                logger.info(f"✅ تم تحديث قاعدة البيانات للصفقة {position_id}")
            
            return {
                'success': True,
                'message': f'تم إغلاق {close_percent}% من الصفقة بنجاح',
                'partial_pnl': partial_pnl,
                'close_price': close_price,
                'close_quantity': close_quantity,
                'remaining_quantity': calc_result['remaining_quantity']
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي Spot: {e}")
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    def execute_partial_close_futures(self, user_id: int, position_id: str, position_info: Dict,
                                      close_percent: float, api_client = None) -> Dict[str, Any]:
        """تنفيذ إغلاق جزئي لصفقة Futures"""
        try:
            logger.info(f"🔄 تنفيذ إغلاق جزئي Futures: {position_id} - {close_percent}%")
            
            # حساب الكمية
            calc_result = self.calculate_partial_close_quantity(position_info, close_percent)
            if not calc_result:
                return {'success': False, 'message': 'فشل في حساب الكمية'}
            
            symbol = position_info['symbol']
            side = position_info['side']
            close_quantity = calc_result['close_quantity']
            
            account_type = position_info.get('account_type', 'demo')
            
            if account_type == 'real' and api_client:
                # إغلاق حقيقي عبر API
                try:
                    # تنفيذ أمر معاكس مع reduce_only=True
                    close_side = 'Sell' if side.upper() in ['BUY', 'LONG'] else 'Buy'
                    
                    order_result = api_client.place_order(
                        symbol=symbol,
                        side=close_side,
                        order_type='Market',
                        qty=close_quantity,
                        category='linear',
                        reduce_only=True
                    )
                    
                    if not order_result or order_result.get('retCode') != 0:
                        return {
                            'success': False,
                            'message': f"فشل تنفيذ الأمر: {order_result.get('retMsg', 'خطأ غير معروف')}"
                        }
                    
                    # الحصول على سعر الإغلاق
                    close_price = float(order_result.get('result', {}).get('avgPrice', 0))
                    if not close_price:
                        close_price = api_client.get_ticker_price(symbol, 'linear')
                    
                    logger.info(f"✅ تم الإغلاق الجزئي الحقيقي Futures: {close_quantity} @ {close_price}")
                    
                except Exception as e:
                    logger.error(f"خطأ في الإغلاق الجزئي الحقيقي Futures: {e}")
                    return {'success': False, 'message': f'خطأ في تنفيذ الأمر: {e}'}
            
            else:
                # إغلاق تجريبي
                close_price = position_info.get('current_price', position_info.get('entry_price', 0))
                logger.info(f"✅ تم الإغلاق الجزئي التجريبي Futures: {close_quantity} @ {close_price}")
            
            # حساب PnL للجزء المغلق
            entry_price = position_info['entry_price']
            leverage = position_info.get('leverage', 1)
            
            if side.upper() in ['BUY', 'LONG']:
                partial_pnl = (close_price - entry_price) * close_quantity
            else:
                partial_pnl = (entry_price - close_price) * close_quantity
            
            # إنشاء سجل الإغلاق الجزئي
            partial_close_record = {
                'timestamp': datetime.now().isoformat(),
                'close_percent': close_percent,
                'close_quantity': close_quantity,
                'close_price': close_price,
                'partial_pnl': partial_pnl,
                'remaining_quantity': calc_result['remaining_quantity'],
                'remaining_margin': calc_result.get('remaining_margin', 0)
            }
            
            # تحديث قاعدة البيانات
            order = self.db_manager.get_order(position_id)
            if order:
                # إضافة السجل إلى التاريخ
                partial_closes_history = order.get('partial_closes_history', [])
                if isinstance(partial_closes_history, str):
                    partial_closes_history = json.loads(partial_closes_history)
                
                partial_closes_history.append(partial_close_record)
                
                # تحديث الكمية والهامش المتبقيين
                updates = {
                    'quantity': calc_result['remaining_quantity'],
                    'margin_amount': calc_result.get('remaining_margin', 0),
                    'partial_closes_history': partial_closes_history
                }
                
                # إذا تم إغلاق 100%، غلق الصفقة
                if calc_result['remaining_quantity'] <= 0.0001:
                    updates['status'] = 'CLOSED'
                    updates['close_time'] = datetime.now().isoformat()
                    updates['close_price'] = close_price
                
                self.db_manager.update_order(position_id, updates)
                logger.info(f"✅ تم تحديث قاعدة البيانات للصفقة Futures {position_id}")
            
            return {
                'success': True,
                'message': f'تم إغلاق {close_percent}% من الصفقة بنجاح',
                'partial_pnl': partial_pnl,
                'close_price': close_price,
                'close_quantity': close_quantity,
                'remaining_quantity': calc_result['remaining_quantity'],
                'remaining_margin': calc_result.get('remaining_margin', 0)
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي Futures: {e}")
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    def execute_partial_close(self, user_id: int, position_id: str, close_percent: float,
                             api_client = None) -> Dict[str, Any]:
        """تنفيذ إغلاق جزئي (Spot أو Futures حسب نوع الصفقة)"""
        try:
            # جلب معلومات الصفقة من قاعدة البيانات
            order = self.db_manager.get_order(position_id)
            
            if not order:
                # محاولة الجلب من signal_positions
                # سنحتاج لتحديد user_id و symbol
                logger.error(f"الصفقة {position_id} غير موجودة")
                return {'success': False, 'message': 'الصفقة غير موجودة'}
            
            # التحقق من أن الصفقة مفتوحة
            if order.get('status') != 'OPEN':
                return {'success': False, 'message': 'الصفقة مغلقة بالفعل'}
            
            # تحديد نوع السوق
            market_type = order.get('market_type', 'spot')
            
            if market_type == 'spot':
                return self.execute_partial_close_spot(user_id, position_id, order, close_percent, api_client)
            elif market_type == 'futures':
                return self.execute_partial_close_futures(user_id, position_id, order, close_percent, api_client)
            else:
                return {'success': False, 'message': f'نوع سوق غير مدعوم: {market_type}'}
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإغلاق الجزئي: {e}")
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    def get_partial_close_history(self, position_id: str) -> list:
        """الحصول على تاريخ الإغلاقات الجزئية لصفقة"""
        try:
            order = self.db_manager.get_order(position_id)
            
            if not order:
                return []
            
            partial_closes_history = order.get('partial_closes_history', [])
            
            if isinstance(partial_closes_history, str):
                partial_closes_history = json.loads(partial_closes_history)
            
            return partial_closes_history
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ الإغلاقات الجزئية: {e}")
            return []


# دالة مساعدة
def create_partial_close_handler(db_manager):
    """إنشاء مثيل من معالج الإغلاق الجزئي"""
    return PartialCloseHandler(db_manager)

