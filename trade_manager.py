# -*- coding: utf-8 -*-
"""
نظام إدارة الصفقات المتقدم مع الأزرار الديناميكية
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TradeManager:
    """مدير الصفقات المتقدم"""
    
    def __init__(self):
        self.active_trades: Dict[str, Dict] = {}
        self.trade_settings: Dict[str, Dict] = {
            'tp_percentages': [1.0, 2.0, 5.0],
            'sl_percentages': [1.0, 2.0, 3.0],
            'partial_close_percentages': [25.0, 50.0, 75.0]
        }
    
    def create_trade(self, trade_data: Dict) -> str:
        """إنشاء صفقة جديدة"""
        try:
            trade_id = f"trade_{int(datetime.now().timestamp() * 1000)}"
            
            trade_info = {
                'trade_id': trade_id,
                'symbol': trade_data['symbol'],
                'side': trade_data['side'],
                'entry_price': trade_data['entry_price'],
                'quantity': trade_data['quantity'],
                'current_price': trade_data['entry_price'],
                'pnl': 0.0,
                'pnl_percentage': 0.0,
                'status': 'OPEN',
                'created_at': datetime.now().isoformat(),
                'tp_targets': [],
                'sl_target': None,
                'partial_closes': [],
                'remaining_quantity': trade_data['quantity']
            }
            
            self.active_trades[trade_id] = trade_info
            logger.info(f"تم إنشاء صفقة جديدة: {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الصفقة: {e}")
            return None
    
    def update_trade_price(self, trade_id: str, current_price: float) -> bool:
        """تحديث سعر الصفقة"""
        try:
            if trade_id not in self.active_trades:
                return False
            
            trade = self.active_trades[trade_id]
            trade['current_price'] = current_price
            
            # حساب الربح/الخسارة
            entry_price = trade['entry_price']
            side = trade['side']
            
            if side.upper() == 'BUY':
                pnl_percentage = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percentage = ((entry_price - current_price) / entry_price) * 100
            
            pnl_amount = (pnl_percentage / 100) * trade['quantity'] * entry_price
            
            trade['pnl'] = pnl_amount
            trade['pnl_percentage'] = pnl_percentage
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث سعر الصفقة: {e}")
            return False
    
    def execute_tp(self, trade_id: str, percentage: float) -> tuple[bool, str]:
        """تنفيذ هدف الربح"""
        try:
            if trade_id not in self.active_trades:
                return False, "الصفقة غير موجودة"
            
            trade = self.active_trades[trade_id]
            
            if trade['status'] != 'OPEN':
                return False, "الصفقة غير مفتوحة"
            
            # حساب الكمية للإغلاق
            close_quantity = (percentage / 100) * trade['remaining_quantity']
            
            if close_quantity <= 0:
                return False, "الكمية غير صالحة"
            
            # تحديث الكمية المتبقية
            trade['remaining_quantity'] -= close_quantity
            trade['partial_closes'].append({
                'type': 'TP',
                'percentage': percentage,
                'quantity': close_quantity,
                'price': trade['current_price'],
                'timestamp': datetime.now().isoformat()
            })
            
            # إغلاق الصفقة إذا تم إغلاقها بالكامل
            if trade['remaining_quantity'] <= 0.001:  # تحمل خطأ صغير
                trade['status'] = 'CLOSED'
                trade['remaining_quantity'] = 0
            
            logger.info(f"تم تنفيذ TP {percentage}% للصفقة {trade_id}")
            return True, f"تم تنفيذ هدف الربح {percentage}% بنجاح"
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ TP: {e}")
            return False, f"خطأ في تنفيذ TP: {str(e)}"
    
    def execute_sl(self, trade_id: str, percentage: float) -> tuple[bool, str]:
        """تنفيذ وقف الخسارة"""
        try:
            if trade_id not in self.active_trades:
                return False, "الصفقة غير موجودة"
            
            trade = self.active_trades[trade_id]
            
            if trade['status'] != 'OPEN':
                return False, "الصفقة غير مفتوحة"
            
            # حساب سعر وقف الخسارة
            entry_price = trade['entry_price']
            side = trade['side']
            
            if side.upper() == 'BUY':
                sl_price = entry_price * (1 - percentage / 100)
            else:
                sl_price = entry_price * (1 + percentage / 100)
            
            # التحقق من أن السعر الحالي قد وصل لوقف الخسارة
            current_price = trade['current_price']
            
            if side.upper() == 'BUY' and current_price <= sl_price:
                # إغلاق الصفقة بالكامل
                trade['status'] = 'CLOSED'
                trade['remaining_quantity'] = 0
                trade['partial_closes'].append({
                    'type': 'SL',
                    'percentage': percentage,
                    'quantity': trade['remaining_quantity'],
                    'price': current_price,
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"تم تنفيذ SL {percentage}% للصفقة {trade_id}")
                return True, f"تم تنفيذ وقف الخسارة {percentage}% بنجاح"
            else:
                # تعيين وقف الخسارة للمراقبة
                trade['sl_target'] = {
                    'percentage': percentage,
                    'price': sl_price,
                    'set_at': datetime.now().isoformat()
                }
                return True, f"تم تعيين وقف الخسارة {percentage}% للمراقبة"
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ SL: {e}")
            return False, f"خطأ في تنفيذ SL: {str(e)}"
    
    def execute_partial_close(self, trade_id: str, percentage: float) -> tuple[bool, str]:
        """تنفيذ الإغلاق الجزئي"""
        try:
            if trade_id not in self.active_trades:
                return False, "الصفقة غير موجودة"
            
            trade = self.active_trades[trade_id]
            
            if trade['status'] != 'OPEN':
                return False, "الصفقة غير مفتوحة"
            
            # حساب الكمية للإغلاق
            close_quantity = (percentage / 100) * trade['remaining_quantity']
            
            if close_quantity <= 0:
                return False, "الكمية غير صالحة"
            
            # تحديث الكمية المتبقية
            trade['remaining_quantity'] -= close_quantity
            trade['partial_closes'].append({
                'type': 'PARTIAL',
                'percentage': percentage,
                'quantity': close_quantity,
                'price': trade['current_price'],
                'timestamp': datetime.now().isoformat()
            })
            
            # إغلاق الصفقة إذا تم إغلاقها بالكامل
            if trade['remaining_quantity'] <= 0.001:  # تحمل خطأ صغير
                trade['status'] = 'CLOSED'
                trade['remaining_quantity'] = 0
            
            logger.info(f"تم تنفيذ إغلاق جزئي {percentage}% للصفقة {trade_id}")
            return True, f"تم تنفيذ الإغلاق الجزئي {percentage}% بنجاح"
            
        except Exception as e:
            logger.error(f"خطأ في الإغلاق الجزئي: {e}")
            return False, f"خطأ في الإغلاق الجزئي: {str(e)}"
    
    def close_trade_completely(self, trade_id: str) -> tuple[bool, str]:
        """إغلاق الصفقة بالكامل"""
        try:
            if trade_id not in self.active_trades:
                return False, "الصفقة غير موجودة"
            
            trade = self.active_trades[trade_id]
            
            if trade['status'] != 'OPEN':
                return False, "الصفقة غير مفتوحة"
            
            # إغلاق الصفقة بالكامل
            remaining_qty = trade['remaining_quantity']
            trade['status'] = 'CLOSED'
            trade['remaining_quantity'] = 0
            trade['partial_closes'].append({
                'type': 'FULL_CLOSE',
                'percentage': 100.0,
                'quantity': remaining_qty,
                'price': trade['current_price'],
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"تم إغلاق الصفقة بالكامل: {trade_id}")
            return True, "تم إغلاق الصفقة بالكامل بنجاح"
            
        except Exception as e:
            logger.error(f"خطأ في الإغلاق الكامل: {e}")
            return False, f"خطأ في الإغلاق الكامل: {str(e)}"
    
    def get_trade_info(self, trade_id: str) -> Optional[Dict]:
        """الحصول على معلومات الصفقة"""
        return self.active_trades.get(trade_id)
    
    def get_user_trades(self, user_id: int) -> List[Dict]:
        """الحصول على صفقات المستخدم"""
        user_trades = []
        for trade_id, trade_info in self.active_trades.items():
            if trade_info.get('user_id') == user_id:
                user_trades.append(trade_info)
        return user_trades
    
    def update_trade_settings(self, tp_percentages: List[float], 
                            sl_percentages: List[float], 
                            partial_close_percentages: List[float]) -> bool:
        """تحديث إعدادات الصفقات"""
        try:
            self.trade_settings['tp_percentages'] = tp_percentages
            self.trade_settings['sl_percentages'] = sl_percentages
            self.trade_settings['partial_close_percentages'] = partial_close_percentages
            
            logger.info("تم تحديث إعدادات الصفقات")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات الصفقات: {e}")
            return False
    
    def get_trade_settings(self) -> Dict:
        """الحصول على إعدادات الصفقات"""
        return self.trade_settings.copy()