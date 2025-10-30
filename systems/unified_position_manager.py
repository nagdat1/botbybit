#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير موحد للصفقات - ربط Signal ID مع Position ID وحفظ الصفقات
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class UnifiedPositionManager:
    """مدير موحد للصفقات يربط بين Signal ID و Position ID وقاعدة البيانات"""
    
    def __init__(self, db_manager, signal_id_manager):
        self.db_manager = db_manager
        self.signal_id_manager = signal_id_manager
    
    def save_position_on_open(self, user_id: int, signal_data: Dict, order_result: Dict, 
                             account_type: str = 'demo') -> bool:
        """حفظ الصفقة عند الفتح"""
        try:
            logger.info(f"💾 حفظ صفقة جديدة للمستخدم {user_id}")
            
            # استخراج البيانات الأساسية
            symbol = signal_data.get('symbol')
            side = signal_data.get('side')
            entry_price = signal_data.get('entry_price', order_result.get('entry_price', 0))
            quantity = signal_data.get('quantity', order_result.get('quantity', 0))
            market_type = signal_data.get('market_type', 'spot')
            exchange = signal_data.get('exchange', 'bybit')
            
            # Signal ID
            signal_id = signal_data.get('id', signal_data.get('signal_id', ''))
            
            # Position ID (من المنصة للحسابات الحقيقية)
            position_id_exchange = ""
            order_id = ""
            
            if account_type == 'real':
                # للحسابات الحقيقية، نستخدم رقم الأمر من المنصة
                position_id_exchange = order_result.get('orderId', order_result.get('orderLinkId', ''))
                order_id = position_id_exchange
                
                # ربط Signal ID مع Position ID في SignalIDManager
                if signal_id and position_id_exchange:
                    self.signal_id_manager.link_signal_to_position(signal_id, position_id_exchange)
                    logger.info(f"🔗 تم ربط {signal_id} → {position_id_exchange}")
            
            else:
                # للحسابات التجريبية، نولد order_id داخلي
                order_id = f"DEMO_{signal_id}_{uuid.uuid4().hex[:8]}" if signal_id else f"DEMO_{uuid.uuid4().hex[:12]}"
            
            # بيانات الصفقة الأساسية
            position_data = {
                'order_id': order_id,
                'user_id': user_id,
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'quantity': quantity,
                'status': 'OPEN',
                'market_type': market_type,
                'account_type': account_type,
                'exchange': exchange,
                'signal_id': signal_id,
                'position_id_exchange': position_id_exchange
            }
            
            # بيانات إضافية للفيوتشر
            if market_type == 'futures':
                position_data.update({
                    'leverage': signal_data.get('leverage', 1),
                    'margin_amount': signal_data.get('margin_amount', 0),
                    'liquidation_price': signal_data.get('liquidation_price', 0)
                })
            
            # TP & SL
            position_data['tps'] = signal_data.get('take_profits', signal_data.get('tps', []))
            position_data['sl'] = signal_data.get('stop_loss', signal_data.get('sl', 0))
            
            # حفظ في قاعدة البيانات
            success = self.db_manager.create_order(position_data)
            
            if success:
                logger.info(f"✅ تم حفظ الصفقة {order_id} بنجاح")
                
                # حفظ أيضاً في signal_positions إذا كان هناك signal_id
                if signal_id:
                    signal_position_data = {
                        'signal_id': signal_id,
                        'user_id': user_id,
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'quantity': quantity,
                        'exchange': exchange,
                        'market_type': market_type,
                        'order_id': order_id,
                        'status': 'OPEN'
                    }
                    self.db_manager.create_signal_position(signal_position_data)
                    logger.info(f"✅ تم حفظ في signal_positions أيضاً")
                
                return True
            else:
                logger.error(f"❌ فشل حفظ الصفقة في قاعدة البيانات")
                return False
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الصفقة عند الفتح: {e}")
            return False
    
    def save_position_on_close(self, user_id: int, position_id: str, close_data: Dict) -> bool:
        """حفظ بيانات الصفقة عند الإغلاق"""
        try:
            logger.info(f"💾 حفظ بيانات الإغلاق للصفقة {position_id}")
            
            # استخراج بيانات الإغلاق
            close_price = close_data.get('close_price', close_data.get('closing_price', 0))
            pnl_value = close_data.get('pnl_value', close_data.get('pnl', 0))
            pnl_percent = close_data.get('pnl_percent', 0)
            
            # تحديث الصفقة في قاعدة البيانات
            updates = {
                'status': 'CLOSED',
                'close_price': close_price,
                'pnl_value': pnl_value,
                'pnl_percent': pnl_percent,
                'close_time': datetime.now().isoformat()
            }
            
            # إضافة رسوم إذا كانت موجودة
            if 'fees' in close_data:
                updates['notes'] = f"Fees: {close_data['fees']}"
            
            success = self.db_manager.update_order(position_id, updates)
            
            if success:
                logger.info(f"✅ تم حفظ بيانات الإغلاق للصفقة {position_id}")
                
                # تحديث signal_positions إذا كان هناك signal_id
                order = self.db_manager.get_order(position_id)
                if order and order.get('signal_id'):
                    signal_id = order['signal_id']
                    symbol = order['symbol']
                    
                    self.db_manager.update_signal_position(
                        signal_id=signal_id,
                        user_id=user_id,
                        symbol=symbol,
                        updates={'status': 'CLOSED'}
                    )
                    logger.info(f"✅ تم تحديث signal_positions أيضاً")
                
                return True
            else:
                logger.error(f"❌ فشل تحديث بيانات الإغلاق")
                return False
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات الإغلاق: {e}")
            return False
    
    def get_position_by_signal_id(self, signal_id: str, user_id: int) -> Optional[Dict]:
        """الحصول على الصفقة باستخدام Signal ID"""
        try:
            # البحث في signal_positions أولاً
            positions = self.db_manager.get_signal_positions(signal_id, user_id)
            
            if positions:
                # الحصول على أول صفقة مفتوحة
                for pos in positions:
                    if pos.get('status') == 'OPEN':
                        # جلب البيانات الكاملة من orders
                        order_id = pos.get('order_id')
                        if order_id:
                            order = self.db_manager.get_order(order_id)
                            if order:
                                return order
                        return pos
            
            # البحث في orders مباشرة
            filters = {
                'status': 'OPEN'
            }
            orders = self.db_manager.get_user_trade_history(user_id, filters)
            
            for order in orders:
                if order.get('signal_id') == signal_id:
                    return order
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصفقة بواسطة Signal ID: {e}")
            return None
    
    def get_position_by_exchange_id(self, position_id_exchange: str, user_id: int) -> Optional[Dict]:
        """الحصول على الصفقة باستخدام Position ID من المنصة"""
        try:
            # البحث في orders
            filters = {
                'status': 'OPEN'
            }
            orders = self.db_manager.get_user_trade_history(user_id, filters)
            
            for order in orders:
                if order.get('position_id_exchange') == position_id_exchange:
                    return order
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصفقة بواسطة Exchange ID: {e}")
            return None
    
    def link_signal_to_exchange_position(self, signal_id: str, position_id_exchange: str, 
                                        user_id: int) -> bool:
        """ربط Signal ID مع Position ID من المنصة"""
        try:
            # ربط في SignalIDManager
            self.signal_id_manager.link_signal_to_position(signal_id, position_id_exchange)
            
            # تحديث في قاعدة البيانات
            filters = {
                'status': 'OPEN'
            }
            orders = self.db_manager.get_user_trade_history(user_id, filters)
            
            for order in orders:
                if order.get('signal_id') == signal_id:
                    updates = {
                        'position_id_exchange': position_id_exchange
                    }
                    self.db_manager.update_order(order['order_id'], updates)
                    logger.info(f"✅ تم ربط {signal_id} → {position_id_exchange} في قاعدة البيانات")
                    return True
            
            logger.warning(f"لم يتم العثور على صفقة بـ Signal ID: {signal_id}")
            return False
            
        except Exception as e:
            logger.error(f"خطأ في ربط Signal ID مع Exchange Position: {e}")
            return False
    
    def get_signal_id_for_position(self, position_id_exchange: str) -> Optional[str]:
        """الحصول على Signal ID من Position ID"""
        try:
            # محاولة من SignalIDManager أولاً
            signal_id = self.signal_id_manager.get_signal_id_from_position(position_id_exchange)
            
            if signal_id:
                return signal_id
            
            # البحث في قاعدة البيانات
            filters = {
                'status': 'OPEN',
                'limit': 100
            }
            orders = self.db_manager.get_user_trade_history(0, filters)  # سنحسن هذا لاحقاً
            
            for order in orders:
                if order.get('position_id_exchange') == position_id_exchange:
                    return order.get('signal_id', '')
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على Signal ID: {e}")
            return None
    
    def update_position_prices(self, position_id: str, current_price: float, 
                              pnl_value: float, pnl_percent: float) -> bool:
        """تحديث أسعار الصفقة (للعرض المباشر فقط - لا يُحفظ في قاعدة البيانات)"""
        try:
            # هذه الدالة تُستخدم فقط للعرض المباشر
            # لا نحفظ الأسعار اللحظية في قاعدة البيانات
            # فقط نُعيد البيانات المحدثة
            
            logger.debug(f"📊 تحديث أسعار الصفقة {position_id}: {current_price} | PnL: {pnl_value}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الصفقة: {e}")
            return False
    
    def close_position_by_signal_id(self, signal_id: str, user_id: int, close_data: Dict, 
                                   api_client = None) -> Dict[str, Any]:
        """إغلاق صفقة باستخدام Signal ID"""
        try:
            logger.info(f"🔒 إغلاق صفقة بـ Signal ID: {signal_id}")
            
            # الحصول على الصفقة
            position = self.get_position_by_signal_id(signal_id, user_id)
            
            if not position:
                return {
                    'success': False,
                    'message': f'لم يتم العثور على صفقة مفتوحة بـ Signal ID: {signal_id}'
                }
            
            position_id = position['order_id']
            account_type = position.get('account_type', 'demo')
            market_type = position.get('market_type', 'spot')
            
            # إغلاق الصفقة
            if account_type == 'real' and api_client:
                # إغلاق حقيقي عبر API
                try:
                    symbol = position['symbol']
                    side = position['side']
                    quantity = position['quantity']
                    
                    # أمر معاكس
                    close_side = 'SELL' if side.upper() == 'BUY' else 'BUY'
                    category = 'linear' if market_type == 'futures' else 'spot'
                    
                    order_result = api_client.place_order(
                        symbol=symbol,
                        side=close_side,
                        order_type='MARKET',
                        qty=quantity,
                        category=category,
                        reduce_only=(market_type == 'futures')
                    )
                    
                    if order_result and order_result.get('retCode') == 0:
                        close_price = float(order_result.get('result', {}).get('avgPrice', 0))
                        if not close_price:
                            close_price = api_client.get_ticker_price(symbol, category)
                        
                        close_data['close_price'] = close_price
                        logger.info(f"✅ تم إغلاق الصفقة الحقيقية @ {close_price}")
                    else:
                        return {
                            'success': False,
                            'message': f"فشل إغلاق الصفقة: {order_result.get('retMsg', 'خطأ')}"
                        }
                
                except Exception as e:
                    logger.error(f"خطأ في إغلاق الصفقة الحقيقية: {e}")
                    return {
                        'success': False,
                        'message': f'خطأ في تنفيذ الإغلاق: {str(e)}'
                    }
            
            # حفظ بيانات الإغلاق
            self.save_position_on_close(user_id, position_id, close_data)
            
            return {
                'success': True,
                'message': 'تم إغلاق الصفقة بنجاح',
                'position_id': position_id
            }
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة بـ Signal ID: {e}")
            return {
                'success': False,
                'message': f'خطأ: {str(e)}'
            }


# دالة مساعدة
def create_unified_position_manager(db_manager, signal_id_manager):
    """إنشاء مثيل من المدير الموحد"""
    return UnifiedPositionManager(db_manager, signal_id_manager)

