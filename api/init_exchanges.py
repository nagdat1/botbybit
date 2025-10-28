#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exchange Initialization - تهيئة وتسجيل جميع المنصات
ملف مركزي لإدارة جميع المنصات المدعومة
"""

import logging
from api.exchange_base import exchange_registry

logger = logging.getLogger(__name__)


def initialize_all_exchanges():
    """
    تهيئة وتسجيل جميع المنصات المدعومة
    
    هذه الدالة تقوم بـ:
    1. استيراد جميع فئات المنصات
    2. تسجيلها في exchange_registry
    3. التأكد من جاهزيتها للاستخدام
    """
    
    logger.info("🔄 بدء تهيئة المنصات...")
    
    registered_count = 0
    
    # ✅ 1. تسجيل Bybit (مفعّل وجاهز)
    try:
        from api.exchanges.bybit_exchange import BybitExchange
        exchange_registry.register('bybit', BybitExchange)
        registered_count += 1
        logger.info("✅ تم تسجيل Bybit بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل تسجيل Bybit: {e}")
    
    # ✅ 2. تسجيل Bitget (مفعّل وجاهز)
    try:
        from api.exchanges.bitget_exchange import BitgetExchange
        exchange_registry.register('bitget', BitgetExchange)
        registered_count += 1
        logger.info("✅ تم تسجيل Bitget بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل تسجيل Bitget: {e}")
    
    # 🔶 4. تسجيل Binance (قالب جاهز - يحتاج استكمال)
    try:
        from api.exchanges.binance_exchange import BinanceExchange
        exchange_registry.register('binance', BinanceExchange)
        registered_count += 1
        logger.info("🔶 تم تسجيل Binance (قالب - يحتاج استكمال)")
    except Exception as e:
        logger.warning(f"⚠️ Binance غير متاح: {e}")
    
    # 🔶 5. تسجيل OKX (قالب جاهز - يحتاج استكمال)
    try:
        from api.exchanges.okx_exchange import OKXExchange
        exchange_registry.register('okx', OKXExchange)
        registered_count += 1
        logger.info("🔶 تم تسجيل OKX (قالب - يحتاج استكمال)")
    except Exception as e:
        logger.warning(f"⚠️ OKX غير متاح: {e}")
    
    # TODO: أضف منصات أخرى هنا
    # مثال:
    # try:
    #     from api.exchanges.kraken_exchange import KrakenExchange
    #     exchange_registry.register('kraken', KrakenExchange)
    #     registered_count += 1
    #     logger.info("✅ تم تسجيل Kraken بنجاح")
    # except Exception as e:
    #     logger.warning(f"⚠️ Kraken غير متاح: {e}")
    
    logger.info(f"✅ تم تسجيل {registered_count} منصة بنجاح")
    
    # عرض قائمة المنصات المسجلة
    all_exchanges = exchange_registry.get_all_exchanges()
    logger.info(f"📋 المنصات المتاحة: {', '.join(all_exchanges)}")
    
    return registered_count


def get_exchange_info_all():
    """
    الحصول على معلومات جميع المنصات المسجلة
    
    Returns:
        dict: قاموس يحتوي على معلومات كل منصة
    """
    all_exchanges = exchange_registry.get_all_exchanges()
    info = {}
    
    for exchange_name in all_exchanges:
        exchange_info = exchange_registry.get_exchange_info(exchange_name)
        if exchange_info:
            info[exchange_name] = exchange_info
    
    return info


def is_exchange_supported(exchange_name: str) -> bool:
    """
    التحقق من دعم المنصة
    
    Args:
        exchange_name: اسم المنصة
        
    Returns:
        bool: True إذا كانت المنصة مدعومة
    """
    return exchange_name.lower() in exchange_registry.get_all_exchanges()


def create_exchange_instance(user_id: int, exchange_name: str, 
                            api_key: str, api_secret: str):
    """
    إنشاء نسخة من المنصة للمستخدم
    
    Args:
        user_id: معرف المستخدم
        exchange_name: اسم المنصة
        api_key: مفتاح API
        api_secret: سر API
        
    Returns:
        نسخة من المنصة أو None
    """
    if not is_exchange_supported(exchange_name):
        logger.error(f"❌ المنصة {exchange_name} غير مدعومة")
        return None
    
    return exchange_registry.create_instance(user_id, exchange_name, api_key, api_secret)


def get_user_exchange(user_id: int, exchange_name: str):
    """
    الحصول على نسخة المنصة للمستخدم
    
    Args:
        user_id: معرف المستخدم
        exchange_name: اسم المنصة
        
    Returns:
        نسخة المنصة أو None
    """
    return exchange_registry.get_instance(user_id, exchange_name)


def remove_user_exchange(user_id: int, exchange_name: str = None):
    """
    حذف نسخة المنصة للمستخدم
    
    Args:
        user_id: معرف المستخدم
        exchange_name: اسم المنصة (اختياري)
    """
    exchange_registry.remove_instance(user_id, exchange_name)


# تهيئة تلقائية عند الاستيراد
try:
    initialize_all_exchanges()
except Exception as e:
    logger.error(f"❌ خطأ في التهيئة التلقائية: {e}")


"""
📚 دليل إضافة منصة جديدة:

1. إنشاء ملف جديد في api/exchanges/:
   - مثال: api/exchanges/kraken_exchange.py

2. إنشاء فئة ترث من ExchangeBase:
   ```python
   from api.exchange_base import ExchangeBase
   
   class KrakenExchange(ExchangeBase):
       def __init__(self, name='kraken', api_key=None, api_secret=None):
           super().__init__(name, api_key, api_secret)
       
       # تطبيق جميع الدوال المطلوبة
       def test_connection(self): ...
       def get_wallet_balance(self, market_type='spot'): ...
       # ... إلخ
   ```

3. تسجيل المنصة في هذا الملف (init_exchanges.py):
   ```python
   try:
       from api.exchanges.kraken_exchange import KrakenExchange
       exchange_registry.register('kraken', KrakenExchange)
       logger.info("✅ تم تسجيل Kraken بنجاح")
   except Exception as e:
       logger.warning(f"⚠️ Kraken غير متاح: {e}")
   ```

4. إضافة الأزرار في exchange_commands.py:
   - أضف زر للمنصة في cmd_select_exchange
   - أنشئ دالة show_[exchange]_options
   - أنشئ دالة start_[exchange]_setup

5. اختبار التكامل:
   - اختبر الربط والتفعيل
   - تأكد من عمل جميع الدوال
   - اختبر على Testnet أولاً

6. استمتع! 🎉
"""

