#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام ترتيب الأوامر الاحترافي لـ MEXC
يتبع ملف السياق لتنظيم تنفيذ الأوامر بشكل ترتيبي
"""

import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """حالات الأوامر"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

class OrderType(Enum):
    """أنواع الأوامر"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"

@dataclass
class OrderRequest:
    """طلب أمر منظم"""
    symbol: str
    side: str  # BUY/SELL
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    client_order_id: Optional[str] = None
    timestamp: Optional[int] = None
    priority: int = 1  # الأولوية (1 = أعلى أولوية)
    
    def __post_init__(self):
        if not self.client_order_id:
            self.client_order_id = f"bot-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        if not self.timestamp:
            self.timestamp = int(time.time() * 1000)

@dataclass
class OrderResult:
    """نتيجة تنفيذ الأمر"""
    client_order_id: str
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: Optional[float] = None
    error_message: Optional[str] = None
    execution_time: Optional[int] = None

class MEXCOrderManager:
    """مدير الأوامر الاحترافي لـ MEXC"""
    
    def __init__(self, mexc_bot):
        """
        تهيئة مدير الأوامر
        
        Args:
            mexc_bot: مثيل MEXC Trading Bot
        """
        self.mexc_bot = mexc_bot
        self.order_queue: List[OrderRequest] = []
        self.executed_orders: Dict[str, OrderResult] = {}
        self.max_concurrent_orders = 5
        self.order_timeout = 30  # ثانية
        
        logger.info("🔧 تهيئة MEXC Order Manager")
        logger.info(f"📊 الحد الأقصى للأوامر المتزامنة: {self.max_concurrent_orders}")
        logger.info(f"⏰ مهلة الأمر: {self.order_timeout} ثانية")
    
    def add_order(self, order_request: OrderRequest) -> str:
        """
        إضافة أمر إلى قائمة الانتظار
        
        Args:
            order_request: طلب الأمر
            
        Returns:
            client_order_id
        """
        # ترتيب الأوامر حسب الأولوية والوقت
        self.order_queue.append(order_request)
        self.order_queue.sort(key=lambda x: (x.priority, x.timestamp))
        
        logger.info(f"📝 إضافة أمر إلى قائمة الانتظار:")
        logger.info(f"   - ClientOrderId: {order_request.client_order_id}")
        logger.info(f"   - Symbol: {order_request.symbol}")
        logger.info(f"   - Side: {order_request.side}")
        logger.info(f"   - Type: {order_request.order_type.value}")
        logger.info(f"   - Quantity: {order_request.quantity}")
        logger.info(f"   - Priority: {order_request.priority}")
        
        return order_request.client_order_id
    
    def execute_orders(self) -> List[OrderResult]:
        """
        تنفيذ الأوامر في قائمة الانتظار
        
        Returns:
            قائمة نتائج الأوامر
        """
        results = []
        
        # تنفيذ الأوامر حسب الأولوية
        while self.order_queue and len(self.executed_orders) < self.max_concurrent_orders:
            order_request = self.order_queue.pop(0)
            
            logger.info(f"🚀 تنفيذ أمر: {order_request.client_order_id}")
            
            try:
                # تنفيذ الأمر
                result = self._execute_single_order(order_request)
                results.append(result)
                
                # حفظ النتيجة
                self.executed_orders[order_request.client_order_id] = result
                
            except Exception as e:
                logger.error(f"❌ خطأ في تنفيذ الأمر {order_request.client_order_id}: {e}")
                
                error_result = OrderResult(
                    client_order_id=order_request.client_order_id,
                    status=OrderStatus.FAILED,
                    error_message=str(e)
                )
                results.append(error_result)
                self.executed_orders[order_request.client_order_id] = error_result
        
        return results
    
    def _execute_single_order(self, order_request: OrderRequest) -> OrderResult:
        """
        تنفيذ أمر واحد
        
        Args:
            order_request: طلب الأمر
            
        Returns:
            نتيجة الأمر
        """
        start_time = time.time()
        
        try:
            # بناء معاملات الأمر
            params = {
                'symbol': order_request.symbol,
                'side': order_request.side,
                'type': order_request.order_type.value,
                'quantity': str(order_request.quantity),
                'newClientOrderId': order_request.client_order_id
            }
            
            # إضافة السعر للأوامر المحددة
            if order_request.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                if order_request.price:
                    params['price'] = str(order_request.price)
                else:
                    raise ValueError(f"السعر مطلوب لأوامر {order_request.order_type.value}")
            
            # إضافة سعر التوقف للأوامر الشرطية
            if order_request.order_type in [OrderType.STOP_MARKET, OrderType.STOP_LIMIT]:
                if order_request.stop_price:
                    params['stopPrice'] = str(order_request.stop_price)
                else:
                    raise ValueError(f"سعر التوقف مطلوب لأوامر {order_request.order_type.value}")
            
            logger.info(f"📋 معاملات الأمر: {params}")
            
            # إرسال الأمر إلى MEXC
            result = self.mexc_bot._make_request('POST', '/api/v3/order', params, signed=True)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            if result:
                logger.info(f"✅ تم تنفيذ الأمر بنجاح: {result}")
                
                return OrderResult(
                    client_order_id=order_request.client_order_id,
                    order_id=result.get('orderId'),
                    status=OrderStatus.FILLED if result.get('status') == 'FILLED' else OrderStatus.SUBMITTED,
                    filled_quantity=float(result.get('executedQty', 0)),
                    average_price=float(result.get('avgPrice', 0)) if result.get('avgPrice') else None,
                    execution_time=execution_time
                )
            else:
                logger.error(f"❌ فشل تنفيذ الأمر")
                
                return OrderResult(
                    client_order_id=order_request.client_order_id,
                    status=OrderStatus.FAILED,
                    error_message="فشل في إرسال الأمر إلى MEXC",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"❌ خطأ في تنفيذ الأمر: {e}")
            
            return OrderResult(
                client_order_id=order_request.client_order_id,
                status=OrderStatus.FAILED,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def get_order_status(self, client_order_id: str) -> Optional[OrderResult]:
        """
        الحصول على حالة أمر
        
        Args:
            client_order_id: معرف الأمر
            
        Returns:
            نتيجة الأمر أو None
        """
        return self.executed_orders.get(client_order_id)
    
    def cancel_order(self, client_order_id: str) -> bool:
        """
        إلغاء أمر
        
        Args:
            client_order_id: معرف الأمر
            
        Returns:
            True إذا تم الإلغاء بنجاح
        """
        try:
            # البحث عن الأمر في القائمة المنفذة
            if client_order_id in self.executed_orders:
                order_result = self.executed_orders[client_order_id]
                
                if order_result.order_id:
                    # إلغاء الأمر على MEXC
                    cancel_result = self.mexc_bot.cancel_order(
                        order_result.symbol if hasattr(order_result, 'symbol') else 'BTCUSDT',
                        order_result.order_id
                    )
                    
                    if cancel_result:
                        order_result.status = OrderStatus.CANCELLED
                        logger.info(f"✅ تم إلغاء الأمر: {client_order_id}")
                        return True
                    else:
                        logger.error(f"❌ فشل إلغاء الأمر: {client_order_id}")
                        return False
                else:
                    logger.warning(f"⚠️ لا يمكن إلغاء الأمر: {client_order_id} - لا يوجد order_id")
                    return False
            else:
                logger.warning(f"⚠️ الأمر غير موجود: {client_order_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في إلغاء الأمر: {e}")
            return False
    
    def get_execution_report(self) -> Dict[str, Any]:
        """
        الحصول على تقرير التنفيذ
        
        Returns:
            تقرير التنفيذ
        """
        total_orders = len(self.executed_orders)
        successful_orders = len([r for r in self.executed_orders.values() if r.status == OrderStatus.FILLED])
        failed_orders = len([r for r in self.executed_orders.values() if r.status == OrderStatus.FAILED])
        
        total_execution_time = sum([r.execution_time or 0 for r in self.executed_orders.values()])
        avg_execution_time = total_execution_time / total_orders if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'successful_orders': successful_orders,
            'failed_orders': failed_orders,
            'success_rate': (successful_orders / total_orders * 100) if total_orders > 0 else 0,
            'average_execution_time_ms': avg_execution_time,
            'pending_orders': len(self.order_queue),
            'active_orders': len([r for r in self.executed_orders.values() if r.status == OrderStatus.SUBMITTED])
        }

# دالة مساعدة لإنشاء مدير الأوامر
def create_mexc_order_manager(mexc_bot) -> MEXCOrderManager:
    """
    إنشاء مدير أوامر MEXC
    
    Args:
        mexc_bot: مثيل MEXC Trading Bot
        
    Returns:
        مدير الأوامر
    """
    return MEXCOrderManager(mexc_bot)
