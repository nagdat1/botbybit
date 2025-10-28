#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الصفقات المرتبطة بالـ ID - إدارة الصفقات المرتبطة بمعرفات الإشارات
يدعم ربط الصفقات بالإشارات عبر الـ ID لضمان التنفيذ الصحيح لـ TP/SL
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from database import db_manager

logger = logging.getLogger(__name__)

class SignalPositionManager:
    """مدير الصفقات المرتبطة بالـ ID"""
    
    def __init__(self):
        self.db = db_manager
    
    def create_position(self, signal_id: str, user_id: int, symbol: str, 
                       side: str, entry_price: float, quantity: float,
                       exchange: str, market_type: str, order_id: str = None) -> bool:
        """
        إنشاء صفقة جديدة مرتبطة بالـ ID
        
        Args:
            signal_id: معرف الإشارة (مثل TV_B01)
            user_id: معرف المستخدم
            symbol: رمز العملة (BTCUSDT)
            side: جهة الصفقة (Buy/Sell)
            entry_price: سعر الدخول
            quantity: الكمية
            exchange: المنصة (bybit/mexc)
            market_type: نوع السوق (spot/futures)
            order_id: معرف الأمر من المنصة
            
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            position_data = {
                'signal_id': signal_id,
                'user_id': user_id,
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'quantity': quantity,
                'exchange': exchange,
                'market_type': market_type,
                'order_id': order_id or '',
                'status': 'OPEN',
                'notes': f'Created from signal {signal_id}'
            }
            
            success = self.db.create_signal_position(position_data)
            
            if success:
                logger.info(f" تم إنشاء صفقة مرتبطة بالـ ID: {signal_id} - {symbol} - {side}")
            else:
                logger.error(f" فشل إنشاء صفقة مرتبطة بالـ ID: {signal_id}")
            
            return success
            
        except Exception as e:
            logger.error(f" خطأ في إنشاء صفقة مرتبطة بالـ ID: {e}")
            return False
    
    def get_position(self, signal_id: str, user_id: int, symbol: str) -> Optional[Dict]:
        """
        الحصول على صفقة محددة بالـ ID
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم
            symbol: رمز العملة
            
        Returns:
            بيانات الصفقة أو None
        """
        try:
            position = self.db.get_position_by_signal_id(signal_id, user_id, symbol)
            
            if position:
                logger.debug(f" تم العثور على صفقة: {signal_id} - {symbol}")
            else:
                logger.debug(f" لم يتم العثور على صفقة: {signal_id} - {symbol}")
            
            return position
            
        except Exception as e:
            logger.error(f" خطأ في الحصول على الصفقة: {e}")
            return None
    
    def get_user_positions(self, user_id: int, status: str = None) -> List[Dict]:
        """
        الحصول على جميع الصفقات المرتبطة بالـ ID للمستخدم
        
        Args:
            user_id: معرف المستخدم
            status: حالة الصفقات (OPEN/CLOSED) أو None لجميع الحالات
            
        Returns:
            قائمة الصفقات
        """
        try:
            positions = self.db.get_user_signal_positions(user_id, status)
            logger.info(f" تم العثور على {len(positions)} صفقة للمستخدم {user_id}")
            return positions
            
        except Exception as e:
            logger.error(f" خطأ في الحصول على صفقات المستخدم: {e}")
            return []
    
    def get_signal_positions(self, signal_id: str, user_id: int = None) -> List[Dict]:
        """
        الحصول على جميع الصفقات المرتبطة بمعرف إشارة معين
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم (اختياري)
            
        Returns:
            قائمة الصفقات
        """
        try:
            positions = self.db.get_signal_positions(signal_id, user_id)
            logger.info(f" تم العثور على {len(positions)} صفقة للإشارة {signal_id}")
            return positions
            
        except Exception as e:
            logger.error(f" خطأ في الحصول على صفقات الإشارة: {e}")
            return []
    
    def close_position(self, signal_id: str, user_id: int, symbol: str) -> bool:
        """
        إغلاق صفقة مرتبطة بالـ ID
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم
            symbol: رمز العملة
            
        Returns:
            True إذا تم الإغلاق بنجاح
        """
        try:
            success = self.db.close_signal_position(signal_id, user_id, symbol)
            
            if success:
                logger.info(f" تم إغلاق صفقة مرتبطة بالـ ID: {signal_id} - {symbol}")
            else:
                logger.error(f" فشل إغلاق صفقة مرتبطة بالـ ID: {signal_id} - {symbol}")
            
            return success
            
        except Exception as e:
            logger.error(f" خطأ في إغلاق الصفقة: {e}")
            return False
    
    def partial_close_position(self, signal_id: str, user_id: int, symbol: str, 
                              percentage: float) -> Tuple[bool, str]:
        """
        إغلاق جزئي لصفقة مرتبطة بالـ ID
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم
            symbol: رمز العملة
            percentage: النسبة المئوية للإغلاق (1-100)
            
        Returns:
            (نجح/فشل, رسالة)
        """
        try:
            # التحقق من صحة النسبة
            if percentage <= 0 or percentage > 100:
                return False, f"نسبة غير صحيحة: {percentage}%. يجب أن تكون بين 1 و 100"
            
            # الحصول على الصفقة
            position = self.get_position(signal_id, user_id, symbol)
            
            if not position:
                return False, f"لم يتم العثور على صفقة مرتبطة بالـ ID: {signal_id}"
            
            if position['status'] != 'OPEN':
                return False, f"الصفقة غير مفتوحة: {position['status']}"
            
            # حساب الكمية المراد إغلاقها
            current_qty = float(position['quantity'])
            close_qty = current_qty * (percentage / 100)
            remaining_qty = current_qty - close_qty
            
            # تحديث الكمية المتبقية
            updates = {
                'quantity': remaining_qty,
                'notes': f'Partial close {percentage}% - Remaining: {remaining_qty}'
            }
            
            success = self.db.update_signal_position(signal_id, user_id, symbol, updates)
            
            if success:
                logger.info(f" تم إغلاق جزئي {percentage}% من صفقة {signal_id} - {symbol}")
                return True, f"تم إغلاق {percentage}% من الصفقة. المتبقي: {remaining_qty}"
            else:
                logger.error(f" فشل الإغلاق الجزئي لصفقة {signal_id}")
                return False, "فشل في تحديث الصفقة"
            
        except Exception as e:
            logger.error(f" خطأ في الإغلاق الجزئي: {e}")
            return False, f"خطأ في الإغلاق الجزئي: {e}"
    
    def update_position(self, signal_id: str, user_id: int, symbol: str, 
                       updates: Dict) -> bool:
        """
        تحديث صفقة مرتبطة بالـ ID
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم
            symbol: رمز العملة
            updates: التحديثات المراد تطبيقها
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        try:
            success = self.db.update_signal_position(signal_id, user_id, symbol, updates)
            
            if success:
                logger.info(f" تم تحديث صفقة مرتبطة بالـ ID: {signal_id} - {symbol}")
            else:
                logger.error(f" فشل تحديث صفقة مرتبطة بالـ ID: {signal_id} - {symbol}")
            
            return success
            
        except Exception as e:
            logger.error(f" خطأ في تحديث الصفقة: {e}")
            return False
    
    def find_positions_for_close(self, signal_id: str, user_id: int, symbol: str) -> List[Dict]:
        """
        البحث عن الصفقات المرتبطة بالـ ID للإغلاق
        
        Args:
            signal_id: معرف الإشارة
            user_id: معرف المستخدم
            symbol: رمز العملة
            
        Returns:
            قائمة الصفقات المفتوحة المرتبطة بالـ ID
        """
        try:
            # البحث عن الصفقات المفتوحة المرتبطة بالـ ID
            positions = self.get_signal_positions(signal_id, user_id)
            
            # تصفية الصفقات المفتوحة على نفس الرمز
            open_positions = [
                pos for pos in positions 
                if pos['symbol'] == symbol and pos['status'] == 'OPEN'
            ]
            
            logger.info(f" تم العثور على {len(open_positions)} صفقة مفتوحة للإشارة {signal_id} - {symbol}")
            
            return open_positions
            
        except Exception as e:
            logger.error(f" خطأ في البحث عن الصفقات للإغلاق: {e}")
            return []
    
    def get_position_summary(self, user_id: int) -> Dict:
        """
        الحصول على ملخص الصفقات المرتبطة بالـ ID للمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            ملخص الصفقات
        """
        try:
            all_positions = self.get_user_positions(user_id)
            open_positions = [p for p in all_positions if p['status'] == 'OPEN']
            closed_positions = [p for p in all_positions if p['status'] == 'CLOSED']
            
            # تجميع حسب الرمز
            symbols = {}
            for pos in open_positions:
                symbol = pos['symbol']
                if symbol not in symbols:
                    symbols[symbol] = {
                        'total_qty': 0,
                        'avg_price': 0,
                        'positions': []
                    }
                
                symbols[symbol]['total_qty'] += float(pos['quantity'])
                symbols[symbol]['positions'].append(pos)
            
            # حساب متوسط السعر
            for symbol, data in symbols.items():
                total_value = sum(float(p['quantity']) * float(p['entry_price']) for p in data['positions'])
                data['avg_price'] = total_value / data['total_qty'] if data['total_qty'] > 0 else 0
            
            summary = {
                'total_positions': len(all_positions),
                'open_positions': len(open_positions),
                'closed_positions': len(closed_positions),
                'symbols': symbols,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info(f" ملخص الصفقات للمستخدم {user_id}: {len(open_positions)} مفتوحة، {len(closed_positions)} مغلقة")
            
            return summary
            
        except Exception as e:
            logger.error(f" خطأ في الحصول على ملخص الصفقات: {e}")
            return {
                'total_positions': 0,
                'open_positions': 0,
                'closed_positions': 0,
                'symbols': {},
                'last_updated': datetime.now().isoformat()
            }
    
    def cleanup_old_positions(self, days: int = 30) -> int:
        """
        تنظيف الصفقات القديمة المغلقة
        
        Args:
            days: عدد الأيام للاحتفاظ بالصفقات المغلقة
            
        Returns:
            عدد الصفقات المحذوفة
        """
        try:
            # هذه الدالة يمكن تطويرها لاحقاً لحذف الصفقات القديمة
            logger.info(f"🧹 تنظيف الصفقات القديمة (أكثر من {days} يوم)")
            # TODO: تطبيق منطق الحذف
            return 0
            
        except Exception as e:
            logger.error(f" خطأ في تنظيف الصفقات القديمة: {e}")
            return 0


# مثيل عام لمدير الصفقات المرتبطة بالـ ID
signal_position_manager = SignalPositionManager()


# دوال مساعدة للاستخدام السريع
def create_signal_position(signal_id: str, user_id: int, symbol: str, 
                          side: str, entry_price: float, quantity: float,
                          exchange: str, market_type: str, order_id: str = None) -> bool:
    """دالة مساعدة لإنشاء صفقة مرتبطة بالـ ID"""
    return signal_position_manager.create_position(
        signal_id, user_id, symbol, side, entry_price, quantity, exchange, market_type, order_id
    )


def get_signal_position(signal_id: str, user_id: int, symbol: str) -> Optional[Dict]:
    """دالة مساعدة للحصول على صفقة مرتبطة بالـ ID"""
    return signal_position_manager.get_position(signal_id, user_id, symbol)


def close_signal_position(signal_id: str, user_id: int, symbol: str) -> bool:
    """دالة مساعدة لإغلاق صفقة مرتبطة بالـ ID"""
    return signal_position_manager.close_position(signal_id, user_id, symbol)


def partial_close_signal_position(signal_id: str, user_id: int, symbol: str, 
                                 percentage: float) -> Tuple[bool, str]:
    """دالة مساعدة للإغلاق الجزئي لصفقة مرتبطة بالـ ID"""
    return signal_position_manager.partial_close_position(signal_id, user_id, symbol, percentage)


if __name__ == "__main__":
    # اختبار النظام
    print("=" * 80)
    print("اختبار مدير الصفقات المرتبطة بالـ ID")
    print("=" * 80)
    
    # بيانات اختبار
    test_signal_id = "TEST_001"
    test_user_id = 123456789
    test_symbol = "BTCUSDT"
    
    print(f"\n اختبار إنشاء صفقة:")
    print(f"Signal ID: {test_signal_id}")
    print(f"User ID: {test_user_id}")
    print(f"Symbol: {test_symbol}")
    
    # إنشاء صفقة اختبار
    success = create_signal_position(
        signal_id=test_signal_id,
        user_id=test_user_id,
        symbol=test_symbol,
        side="Buy",
        entry_price=50000.0,
        quantity=0.001,
        exchange="bybit",
        market_type="spot",
        order_id="TEST_ORDER_001"
    )
    
    print(f" نتيجة الإنشاء: {success}")
    
    if success:
        # الحصول على الصفقة
        position = get_signal_position(test_signal_id, test_user_id, test_symbol)
        print(f" الصفقة المنشأة: {position}")
        
        # اختبار الإغلاق الجزئي
        print(f"\n🟡 اختبار الإغلاق الجزئي 50%:")
        success, message = partial_close_signal_position(test_signal_id, test_user_id, test_symbol, 50)
        print(f" النتيجة: {success} - {message}")
        
        # اختبار الإغلاق الكامل
        print(f"\n⚪ اختبار الإغلاق الكامل:")
        success = close_signal_position(test_signal_id, test_user_id, test_symbol)
        print(f" النتيجة: {success}")
    
    print("\n" + "=" * 80)
