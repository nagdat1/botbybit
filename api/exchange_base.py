#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Exchange Interface - الواجهة الأساسية للمنصات
نظام قابل للتوسع لإضافة منصات جديدة بسهولة
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class ExchangeBase(ABC):
    """
    الفئة الأساسية لجميع المنصات
    يجب أن ترث كل منصة جديدة من هذه الفئة وتنفذ جميع الدوال المطلوبة
    """
    
    def __init__(self, name: str, api_key: str = None, api_secret: str = None):
        """
        تهيئة المنصة
        
        Args:
            name: اسم المنصة (مثل: 'bybit', 'binance', 'okx')
            api_key: مفتاح API
            api_secret: سر API
        """
        self.name = name
        self.exchange_name = name  # إضافة للتوافق مع الكود الحالي
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_initialized = False
        
    @abstractmethod
    def test_connection(self) -> bool:
        """
        اختبار الاتصال بالمنصة
        
        Returns:
            bool: True إذا نجح الاتصال، False إذا فشل
        """
        pass
    
    @abstractmethod
    def get_wallet_balance(self, market_type: str = 'spot') -> Optional[Dict]:
        """
        جلب رصيد المحفظة
        
        Args:
            market_type: نوع السوق ('spot', 'futures', 'unified')
            
        Returns:
            dict: معلومات الرصيد أو None
        """
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: float = None, **kwargs) -> Optional[Dict]:
        """
        وضع أمر تداول
        
        Args:
            symbol: رمز العملة (مثل: 'BTCUSDT')
            side: الجانب ('buy', 'sell')
            order_type: نوع الأمر ('market', 'limit')
            quantity: الكمية
            price: السعر (للأوامر المحددة)
            **kwargs: معاملات إضافية
            
        Returns:
            dict: معلومات الأمر أو None
        """
        pass
    
    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        إلغاء أمر
        
        Args:
            symbol: رمز العملة
            order_id: رقم الأمر
            
        Returns:
            bool: True إذا نجح الإلغاء
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """
        جلب الأوامر المفتوحة
        
        Args:
            symbol: رمز العملة (اختياري، إذا لم يحدد يجلب جميع الأوامر)
            
        Returns:
            list: قائمة الأوامر المفتوحة
        """
        pass
    
    @abstractmethod
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """
        جلب الصفقات المفتوحة
        
        Args:
            symbol: رمز العملة (اختياري)
            
        Returns:
            list: قائمة الصفقات المفتوحة
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> bool:
        """
        إغلاق صفقة
        
        Args:
            symbol: رمز العملة
            
        Returns:
            bool: True إذا نجح الإغلاق
        """
        pass
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        تعيين الرافعة المالية
        
        Args:
            symbol: رمز العملة
            leverage: قيمة الرافعة المالية
            
        Returns:
            bool: True إذا نجح التعيين
        """
        pass
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        معلومات عامة عن المنصة
        
        Returns:
            dict: معلومات المنصة
        """
        return {
            'name': self.name,
            'supports_spot': self.supports_spot(),
            'supports_futures': self.supports_futures(),
            'supports_leverage': self.supports_leverage(),
            'max_leverage': self.get_max_leverage(),
            'supported_markets': self.get_supported_markets(),
            'referral_link': self.get_referral_link()
        }
    
    @abstractmethod
    def supports_spot(self) -> bool:
        """هل تدعم المنصة التداول الفوري"""
        pass
    
    @abstractmethod
    def supports_futures(self) -> bool:
        """هل تدعم المنصة تداول الفيوتشر"""
        pass
    
    @abstractmethod
    def supports_leverage(self) -> bool:
        """هل تدعم المنصة الرافعة المالية"""
        pass
    
    @abstractmethod
    def get_max_leverage(self) -> int:
        """أقصى رافعة مالية مدعومة"""
        pass
    
    @abstractmethod
    def get_supported_markets(self) -> List[str]:
        """قائمة الأسواق المدعومة"""
        pass
    
    @abstractmethod
    def get_referral_link(self) -> str:
        """رابط الإحالة للمنصة"""
        pass
    
    @abstractmethod
    def get_symbol_info(self, market_type: str, symbol: str) -> Optional[Dict]:
        """
        الحصول على معلومات الرمز (precision, min/max qty, etc.)
        
        Args:
            market_type: نوع السوق ('spot', 'futures', etc.)
            symbol: رمز العملة
            
        Returns:
            dict: معلومات الرمز أو None
        """
        pass
    
    def round_quantity(self, qty: float, market_type: str, symbol: str) -> float:
        """
        🔧 دالة أساسية مشتركة: تقريب الكمية بناءً على قواعد الرمز
        
        Args:
            qty: الكمية الأصلية
            market_type: نوع السوق
            symbol: رمز العملة
            
        Returns:
            الكمية المقربة حسب قواعد المنصة
        """
        try:
            # جلب معلومات الرمز
            symbol_info = self.get_symbol_info(market_type, symbol)
            
            if not symbol_info:
                logger.warning(f"⚠️ فشل جلب معلومات الرمز {symbol}، استخدام التقريب الافتراضي")
                return round(qty, 6)
            
            qty_step = float(symbol_info.get('qty_step', '0.001'))
            min_qty = symbol_info.get('min_qty', 0.0)
            max_qty = symbol_info.get('max_qty', float('inf'))
            qty_precision = symbol_info.get('qty_precision', 6)
            
            logger.info(f"📏 معلومات الرمز {symbol}:")
            logger.info(f"   qty_step: {qty_step}")
            logger.info(f"   min_qty: {min_qty}")
            logger.info(f"   max_qty: {max_qty}")
            logger.info(f"   precision: {qty_precision}")
            
            # تقريب حسب qty_step
            rounded_qty = round(qty / qty_step) * qty_step
            
            # التأكد من الحد الأدنى
            if rounded_qty < min_qty:
                logger.warning(f"⚠️ الكمية {rounded_qty} أقل من الحد الأدنى {min_qty}، تم تعديلها")
                rounded_qty = min_qty
            
            # التأكد من الحد الأقصى
            if rounded_qty > max_qty:
                logger.warning(f"⚠️ الكمية {rounded_qty} أكبر من الحد الأقصى {max_qty}، تم تعديلها")
                rounded_qty = max_qty
            
            # تقريب نهائي بناءً على precision
            rounded_qty = round(rounded_qty, qty_precision)
            
            logger.info(f"✅ تم تقريب الكمية: {qty} → {rounded_qty}")
            
            return rounded_qty
            
        except Exception as e:
            logger.error(f"❌ خطأ في تقريب الكمية: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # في حالة الخطأ، استخدم تقريب افتراضي
            return round(qty, 6)


class ExchangeRegistry:
    """
    سجل المنصات - لإدارة جميع المنصات المدعومة
    """
    
    def __init__(self):
        self._exchanges: Dict[str, type] = {}
        self._instances: Dict[int, Dict[str, ExchangeBase]] = {}  # user_id -> {exchange_name: instance}
        
    def register(self, name: str, exchange_class: type):
        """
        تسجيل منصة جديدة
        
        Args:
            name: اسم المنصة (مثل: 'bybit', 'binance')
            exchange_class: فئة المنصة التي ترث من ExchangeBase
        """
        if not issubclass(exchange_class, ExchangeBase):
            raise ValueError(f"{exchange_class} must inherit from ExchangeBase")
        
        self._exchanges[name.lower()] = exchange_class
        logger.info(f"✅ تم تسجيل منصة: {name}")
    
    def get_exchange_class(self, name: str) -> Optional[type]:
        """
        الحصول على فئة المنصة
        
        Args:
            name: اسم المنصة
            
        Returns:
            فئة المنصة أو None
        """
        return self._exchanges.get(name.lower())
    
    def create_instance(self, user_id: int, exchange_name: str, 
                       api_key: str, api_secret: str) -> Optional[ExchangeBase]:
        """
        إنشاء نسخة من المنصة لمستخدم معين
        
        Args:
            user_id: معرف المستخدم
            exchange_name: اسم المنصة
            api_key: مفتاح API
            api_secret: سر API
            
        Returns:
            نسخة من المنصة أو None
        """
        exchange_class = self.get_exchange_class(exchange_name)
        if not exchange_class:
            logger.error(f"❌ المنصة {exchange_name} غير مسجلة")
            return None
        
        try:
            instance = exchange_class(exchange_name, api_key, api_secret)
            
            # حفظ النسخة
            if user_id not in self._instances:
                self._instances[user_id] = {}
            self._instances[user_id][exchange_name.lower()] = instance
            
            logger.info(f"✅ تم إنشاء نسخة من {exchange_name} للمستخدم {user_id}")
            return instance
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء نسخة من {exchange_name}: {e}")
            return None
    
    def get_instance(self, user_id: int, exchange_name: str) -> Optional[ExchangeBase]:
        """
        الحصول على نسخة المنصة للمستخدم
        
        Args:
            user_id: معرف المستخدم
            exchange_name: اسم المنصة
            
        Returns:
            نسخة المنصة أو None
        """
        if user_id in self._instances:
            return self._instances[user_id].get(exchange_name.lower())
        return None
    
    def remove_instance(self, user_id: int, exchange_name: str = None):
        """
        حذف نسخة المنصة للمستخدم
        
        Args:
            user_id: معرف المستخدم
            exchange_name: اسم المنصة (إذا لم يحدد يحذف جميع المنصات)
        """
        if user_id in self._instances:
            if exchange_name:
                if exchange_name.lower() in self._instances[user_id]:
                    del self._instances[user_id][exchange_name.lower()]
                    logger.info(f"✅ تم حذف نسخة {exchange_name} للمستخدم {user_id}")
            else:
                del self._instances[user_id]
                logger.info(f"✅ تم حذف جميع المنصات للمستخدم {user_id}")
    
    def get_all_exchanges(self) -> List[str]:
        """الحصول على قائمة جميع المنصات المسجلة"""
        return list(self._exchanges.keys())
    
    def get_exchange_info(self, exchange_name: str) -> Optional[Dict]:
        """
        الحصول على معلومات المنصة
        
        Args:
            exchange_name: اسم المنصة
            
        Returns:
            dict: معلومات المنصة أو None
        """
        exchange_class = self.get_exchange_class(exchange_name)
        if exchange_class:
            # إنشاء نسخة مؤقتة للحصول على المعلومات
            temp_instance = exchange_class(exchange_name)
            return temp_instance.get_exchange_info()
        return None


# إنشاء نسخة عامة من السجل
exchange_registry = ExchangeRegistry()

