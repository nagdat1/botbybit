#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exchanges Module - مجلد المنصات
يحتوي على جميع تطبيقات المنصات المدعومة
"""

from .bybit_exchange import BybitExchange
from .bitget_exchange import BitgetExchange

# TODO: استيراد المنصات الأخرى عند إضافتها
# from .binance_exchange import BinanceExchange
# from .okx_exchange import OKXExchange
# from .coinbase_exchange import CoinbaseExchange

__all__ = [
    'BybitExchange',
    'BitgetExchange',
    # 'BinanceExchange',
    # 'OKXExchange',
    # 'CoinbaseExchange',
]

