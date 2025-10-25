#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص العملات المتاحة في Bybit وإيجاد بديل مناسب
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_account_manager import BybitRealAccount
from config import BYBIT_API_KEY, BYBIT_API_SECRET

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def get_available_symbols():
    """جلب العملات المتاحة في Bybit"""
    logger.info("جلب العملات المتاحة في Bybit...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب جميع العملات المتاحة للسبوت
        symbols = account._make_request('GET', '/v5/market/instruments-info', {'category': 'spot'})
        
        if symbols and 'list' in symbols:
            logger.info(f"عدد العملات المتاحة: {len(symbols['list'])}")
            
            # عرض بعض العملات المتاحة
            available_symbols = []
            for symbol_info in symbols['list'][:20]:  # أول 20 عملة
                symbol = symbol_info.get('symbol', '')
                if symbol and 'USDT' in symbol:
                    available_symbols.append(symbol)
                    logger.info(f"متاح: {symbol}")
            
            return available_symbols
        else:
            logger.error("فشل في جلب العملات المتاحة")
            return []
        
    except Exception as e:
        logger.error(f"خطأ في جلب العملات المتاحة: {e}")
        return []

async def test_popular_symbols():
    """اختبار العملات الشائعة"""
    logger.info("اختبار العملات الشائعة...")
    
    # عملات شائعة للاختبار
    popular_symbols = [
        'ETHUSDT',    # إيثريوم
        'ADAUSDT',    # كاردانو
        'SOLUSDT',    # سولانا
        'DOGEUSDT',   # دوجكوين
        'MATICUSDT',  # بوليجون
        'AVAXUSDT',   # أفالانش
        'DOTUSDT',    # بولكادوت
        'LINKUSDT',   # تشين لينك
        'UNIUSDT',    # يوني سواب
        'ATOMUSDT'    # كوزموس
    ]
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        working_symbols = []
        
        for symbol in popular_symbols:
            logger.info(f"اختبار {symbol}...")
            
            # جلب السعر
            ticker = account.get_ticker('spot', symbol)
            if ticker:
                current_price = float(ticker['lastPrice'])
                logger.info(f"✅ {symbol} متاح - السعر: ${current_price}")
                working_symbols.append(symbol)
            else:
                logger.warning(f"❌ {symbol} غير متاح")
        
        return working_symbols
        
    except Exception as e:
        logger.error(f"خطأ في اختبار العملات: {e}")
        return []

async def test_small_order_with_working_symbol():
    """اختبار طلب صغير مع عملة تعمل"""
    logger.info("اختبار طلب صغير مع عملة تعمل...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار مع ETHUSDT (عادة ما يكون متاح)
        symbol = 'ETHUSDT'
        
        # جلب السعر
        ticker = account.get_ticker('spot', symbol)
        if not ticker:
            logger.error(f"فشل في جلب السعر لـ {symbol}")
            return False
        
        current_price = float(ticker['lastPrice'])
        logger.info(f"السعر الحالي لـ {symbol}: ${current_price}")
        
        # حساب الكمية بناءً على المبلغ المطلوب (50 دولار)
        amount_usd = 50.0
        qty = amount_usd / current_price
        logger.info(f"المبلغ المطلوب: ${amount_usd}")
        logger.info(f"الكمية المحسوبة: {qty:.6f} ETH")
        
        # اختبار وضع الأمر
        test_order = account.place_order(
            category='spot',
            symbol=symbol,
            side='Buy',
            order_type='Market',
            qty=round(qty, 6)
        )
        
        logger.info(f"نتيجة الطلب: {test_order}")
        
        if test_order and test_order.get('success'):
            logger.info(f"نجح طلب {symbol}!")
            return True
        else:
            error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
            error_code = test_order.get('error_code') if test_order else 'Unknown'
            logger.error(f"فشل طلب {symbol}: {error_code} - {error_msg}")
            return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الطلب: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("فحص العملات المتاحة وإيجاد بديل مناسب...")
    
    # اختبار 1: جلب العملات المتاحة
    available_symbols = await get_available_symbols()
    
    # اختبار 2: اختبار العملات الشائعة
    working_symbols = await test_popular_symbols()
    
    # اختبار 3: اختبار طلب صغير مع عملة تعمل
    order_success = await test_small_order_with_working_symbol()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج فحص العملات:")
    logger.info(f"العملات المتاحة: {len(available_symbols) if available_symbols else 0}")
    logger.info(f"العملات الشائعة التي تعمل: {len(working_symbols)}")
    logger.info(f"اختبار الطلب: {'نجح' if order_success else 'فشل'}")
    
    if working_symbols:
        logger.info(f"العملات التي تعمل: {', '.join(working_symbols[:5])}")
    
    logger.info("\nالتوصيات:")
    logger.info("1. استخدم عملة متاحة مثل ETHUSDT أو ADAUSDT")
    logger.info("2. تجنب العملات غير المدعومة مثل NFPUSDT")
    logger.info("3. تحقق من توفر العملة قبل إرسال الإشارة")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
