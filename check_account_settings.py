#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص إعدادات الحساب ونوع الحساب في Bybit
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

async def check_account_settings():
    """فحص إعدادات الحساب"""
    logger.info("فحص إعدادات الحساب...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # فحص معلومات الحساب
        account_info = account.get_account_info()
        if account_info:
            logger.info(f"معلومات الحساب: {account_info}")
        
        # فحص الرصيد
        balance = account.get_wallet_balance('spot')
        if balance:
            logger.info(f"الرصيد: {balance}")
        
        # فحص إعدادات التداول
        trading_settings = account.get_trading_settings()
        if trading_settings:
            logger.info(f"إعدادات التداول: {trading_settings}")
        
        return True
        
    except Exception as e:
        logger.error(f"خطأ في فحص إعدادات الحساب: {e}")
        return False

async def test_different_order_types():
    """اختبار أنواع أوامر مختلفة"""
    logger.info("اختبار أنواع أوامر مختلفة...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب السعر الحالي
        ticker = account.get_ticker('spot', 'BTCUSDT')
        if not ticker:
            logger.error("فشل في جلب السعر")
            return False
        
        current_price = float(ticker['lastPrice'])
        logger.info(f"السعر الحالي: ${current_price:,.2f}")
        
        # اختبار أمر Limit بدلاً من Market
        limit_price = current_price * 0.99  # سعر أقل بـ 1%
        qty = 0.001  # كمية صغيرة
        
        logger.info(f"اختبار أمر Limit بسعر ${limit_price:,.2f} وكمية {qty}")
        
        limit_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Limit',
            qty=qty,
            price=limit_price
        )
        
        logger.info(f"نتيجة أمر Limit: {limit_order}")
        
        if limit_order and limit_order.get('success'):
            logger.info("نجح أمر Limit!")
            return True
        else:
            error_msg = limit_order.get('error', 'Unknown error') if limit_order else 'No response'
            logger.warning(f"فشل أمر Limit: {error_msg}")
        
        # اختبار أمر Market مع كمية أكبر
        large_qty = 0.01  # كمية أكبر
        
        logger.info(f"اختبار أمر Market بكمية أكبر: {large_qty}")
        
        market_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=large_qty
        )
        
        logger.info(f"نتيجة أمر Market الكبير: {market_order}")
        
        if market_order and market_order.get('success'):
            logger.info("نجح أمر Market الكبير!")
            return True
        else:
            error_msg = market_order.get('error', 'Unknown error') if market_order else 'No response'
            logger.warning(f"فشل أمر Market الكبير: {error_msg}")
        
        return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار أنواع الأوامر: {e}")
        return False

async def test_api_permissions():
    """فحص صلاحيات API"""
    logger.info("فحص صلاحيات API...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار قراءة البيانات
        logger.info("اختبار قراءة البيانات...")
        ticker = account.get_ticker('spot', 'BTCUSDT')
        if ticker:
            logger.info("✅ يمكن قراءة البيانات")
        else:
            logger.error("❌ لا يمكن قراءة البيانات")
            return False
        
        # اختبار قراءة الرصيد
        logger.info("اختبار قراءة الرصيد...")
        balance = account.get_wallet_balance('spot')
        if balance:
            logger.info("✅ يمكن قراءة الرصيد")
        else:
            logger.error("❌ لا يمكن قراءة الرصيد")
            return False
        
        # اختبار وضع أمر (سيفشل لكن نفحص الرسالة)
        logger.info("اختبار وضع أمر...")
        test_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001
        )
        
        if test_order:
            if test_order.get('success'):
                logger.info("✅ يمكن وضع الأوامر")
            else:
                error_code = test_order.get('error_code')
                error_msg = test_order.get('error')
                
                if error_code == 170140:
                    logger.warning("⚠️ يمكن وضع الأوامر لكن الحد الأدنى غير مناسب")
                elif error_code == 10004:
                    logger.error("❌ مشكلة في التوقيع")
                elif error_code == 10001:
                    logger.error("❌ مشكلة في الصلاحيات")
                else:
                    logger.warning(f"⚠️ خطأ آخر: {error_code} - {error_msg}")
        else:
            logger.error("❌ لا يمكن وضع الأوامر")
        
        return True
        
    except Exception as e:
        logger.error(f"خطأ في فحص صلاحيات API: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("فحص شامل لإعدادات الحساب وAPI...")
    
    # اختبار 1: فحص إعدادات الحساب
    account_ok = await check_account_settings()
    
    # اختبار 2: فحص صلاحيات API
    api_ok = await test_api_permissions()
    
    # اختبار 3: اختبار أنواع أوامر مختلفة
    orders_ok = await test_different_order_types()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج الفحص الشامل:")
    logger.info(f"إعدادات الحساب: {'✅' if account_ok else '❌'}")
    logger.info(f"صلاحيات API: {'✅' if api_ok else '❌'}")
    logger.info(f"أنواع الأوامر: {'✅' if orders_ok else '❌'}")
    
    if not orders_ok:
        logger.info("\nالتوصيات:")
        logger.info("1. تحقق من إعدادات API في حساب Bybit")
        logger.info("2. تأكد من تفعيل صلاحية 'Spot Trading'")
        logger.info("3. تحقق من الحد الأدنى للطلب في إعدادات الحساب")
        logger.info("4. جرب استخدام أمر Limit بدلاً من Market")
        logger.info("5. تأكد من أن الحساب مفعل للتداول الفوري")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
