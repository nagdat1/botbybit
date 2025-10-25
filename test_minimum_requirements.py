#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص مشكلة الحد الأدنى للطلب في Bybit
المستخدم يقول أنه يمكنه عمل صفقة بنفس الرصيد على المنصة
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

async def test_minimum_order_value():
    """اختبار الحد الأدنى لقيمة الطلب بدلاً من الكمية"""
    logger.info("اختبار الحد الأدنى لقيمة الطلب...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب السعر الحالي
        ticker = account.get_ticker('spot', 'BTCUSDT')
        if not ticker:
            logger.error("فشل في جلب السعر")
            return False
        
        current_price = float(ticker['lastPrice'])
        logger.info(f"السعر الحالي لـ BTCUSDT: ${current_price:,.2f}")
        
        # اختبار قيم مختلفة للطلب (بالدولار)
        test_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # بالدولار
        
        for value_usd in test_values:
            # حساب الكمية بناءً على القيمة بالدولار
            qty = value_usd / current_price
            logger.info(f"اختبار قيمة ${value_usd} = {qty:.6f} BTC")
            
            test_order = account.place_order(
                category='spot',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Market',
                qty=round(qty, 6)  # تقريب إلى 6 خانات عشرية
            )
            
            if test_order and test_order.get('success'):
                logger.info(f"نجح مع القيمة: ${value_usd}")
                return value_usd
            else:
                error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
                logger.warning(f"فشل مع القيمة ${value_usd}: {error_msg}")
        
        logger.error("لم تنجح أي قيمة - تحقق من الإعدادات")
        return None
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الحد الأدنى: {e}")
        return None

async def test_bybit_minimum_requirements():
    """فحص متطلبات Bybit للحد الأدنى"""
    logger.info("فحص متطلبات Bybit للحد الأدنى...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب معلومات الرمز
        instruments = account.get_instruments_info('spot', 'BTCUSDT')
        if instruments:
            logger.info(f"معلومات الرمز: {instruments}")
            
            # البحث عن الحد الأدنى للطلب
            for instrument in instruments:
                if instrument.get('symbol') == 'BTCUSDT':
                    min_order_qty = instrument.get('lotSizeFilter', {}).get('minOrderQty')
                    min_order_amt = instrument.get('lotSizeFilter', {}).get('minOrderAmt')
                    
                    logger.info(f"الحد الأدنى للكمية: {min_order_qty}")
                    logger.info(f"الحد الأدنى للمبلغ: {min_order_amt}")
                    
                    return {
                        'min_qty': min_order_qty,
                        'min_amt': min_order_amt
                    }
        
        return None
        
    except Exception as e:
        logger.error(f"خطأ في فحص المتطلبات: {e}")
        return None

async def test_small_order():
    """اختبار طلب صغير جداً"""
    logger.info("اختبار طلب صغير جداً...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب السعر الحالي
        ticker = account.get_ticker('spot', 'BTCUSDT')
        if not ticker:
            logger.error("فشل في جلب السعر")
            return False
        
        current_price = float(ticker['lastPrice'])
        
        # اختبار طلب بقيمة 10 دولار فقط
        value_usd = 10
        qty = value_usd / current_price
        
        logger.info(f"اختبار طلب بقيمة ${value_usd} = {qty:.8f} BTC")
        
        test_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=round(qty, 8)  # تقريب إلى 8 خانات عشرية
        )
        
        logger.info(f"نتيجة الطلب: {test_order}")
        
        if test_order and test_order.get('success'):
            logger.info("نجح الطلب الصغير!")
            return True
        else:
            error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
            logger.error(f"فشل الطلب الصغير: {error_msg}")
            return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الطلب الصغير: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("فحص مشكلة الحد الأدنى للطلب في Bybit...")
    
    # اختبار 1: فحص متطلبات Bybit
    requirements = await test_bybit_minimum_requirements()
    if requirements:
        logger.info(f"متطلبات Bybit: {requirements}")
    
    # اختبار 2: اختبار الحد الأدنى لقيمة الطلب
    min_value = await test_minimum_order_value()
    if min_value:
        logger.info(f"الحد الأدنى لقيمة الطلب: ${min_value}")
    
    # اختبار 3: اختبار طلب صغير جداً
    small_order_success = await test_small_order()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج فحص الحد الأدنى:")
    logger.info(f"متطلبات Bybit: {requirements if requirements else 'غير متاحة'}")
    logger.info(f"الحد الأدنى لقيمة الطلب: ${min_value if min_value else 'غير محدد'}")
    logger.info(f"الطلب الصغير: {'نجح' if small_order_success else 'فشل'}")
    
    if small_order_success:
        logger.info("يمكن تنفيذ طلبات صغيرة!")
        logger.info("المشكلة قد تكون في طريقة حساب الكمية في الكود")
    else:
        logger.info("لا يمكن تنفيذ طلبات صغيرة")
        logger.info("المشكلة في متطلبات Bybit للحد الأدنى")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
