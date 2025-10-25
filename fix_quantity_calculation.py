#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشكلة حساب الكمية في السبوت
المشكلة: استخدام amount/price بدلاً من qty مباشرة
"""

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

def test_correct_quantity_calculation():
    """اختبار الحساب الصحيح للكمية"""
    logger.info("اختبار الحساب الصحيح للكمية...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب السعر الحالي لـ BNBUSDT
        ticker = account.get_ticker('spot', 'BNBUSDT')
        if not ticker:
            logger.error("فشل في جلب السعر لـ BNBUSDT")
            return False
        
        current_price = float(ticker['lastPrice'])
        logger.info(f"السعر الحالي لـ BNBUSDT: ${current_price}")
        
        # الطريقة الخاطئة (الحالية)
        amount_usd = 50.0
        wrong_qty = amount_usd / current_price
        logger.info(f"الطريقة الخاطئة: ${amount_usd} / ${current_price} = {wrong_qty:.6f} BNB")
        
        # الطريقة الصحيحة (يجب استخدامها)
        # في السبوت، يجب أن نستخدم qty مباشرة وليس amount
        # أو نحسب qty بناءً على الحد الأدنى المطلوب
        
        # اختبار الحد الأدنى المطلوب
        min_order_value = 100.0  # الحد الأدنى المقدر
        correct_qty = min_order_value / current_price
        logger.info(f"الطريقة الصحيحة: ${min_order_value} / ${current_price} = {correct_qty:.6f} BNB")
        
        # اختبار وضع الأمر بالكمية الصحيحة
        logger.info(f"اختبار وضع أمر بكمية صحيحة: {correct_qty:.6f} BNB")
        test_order = account.place_order(
            category='spot',
            symbol='BNBUSDT',
            side='Buy',
            order_type='Market',
            qty=round(correct_qty, 6)
        )
        
        logger.info(f"نتيجة الطلب: {test_order}")
        
        if test_order and test_order.get('success'):
            logger.info("نجح الطلب بالكمية الصحيحة!")
            return True
        else:
            error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
            error_code = test_order.get('error_code') if test_order else 'Unknown'
            logger.error(f"فشل الطلب بالكمية الصحيحة: {error_code} - {error_msg}")
            
            # إذا فشل، جرب كمية أكبر
            larger_qty = (min_order_value * 2) / current_price
            logger.info(f"جرب كمية أكبر: {larger_qty:.6f} BNB")
            
            test_order2 = account.place_order(
                category='spot',
                symbol='BNBUSDT',
                side='Buy',
                order_type='Market',
                qty=round(larger_qty, 6)
            )
            
            if test_order2 and test_order2.get('success'):
                logger.info("نجح الطلب بالكمية الأكبر!")
                return True
            else:
                logger.error(f"فشل الطلب بالكمية الأكبر: {test_order2}")
                return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الحساب: {e}")
        return False

def analyze_bybit_spot_requirements():
    """تحليل متطلبات Bybit للسبوت"""
    logger.info("تحليل متطلبات Bybit للسبوت...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب معلومات الرمز
        symbol_info = account._make_request('GET', '/v5/market/instruments-info', {'category': 'spot', 'symbol': 'BNBUSDT'})
        
        if symbol_info and 'list' in symbol_info and symbol_info['list']:
            info = symbol_info['list'][0]
            logger.info(f"معلومات BNBUSDT:")
            logger.info(f"  الحد الأدنى للطلب: {info.get('lotSizeFilter', {}).get('minOrderAmt', 'غير محدد')} USDT")
            logger.info(f"  الحد الأقصى للطلب: {info.get('lotSizeFilter', {}).get('maxOrderAmt', 'غير محدد')} USDT")
            logger.info(f"  الحد الأدنى للكمية: {info.get('lotSizeFilter', {}).get('minOrderQty', 'غير محدد')} BNB")
            logger.info(f"  دقة الكمية: {info.get('lotSizeFilter', {}).get('basePrecision', 'غير محدد')}")
            
            min_order_amt = float(info.get('lotSizeFilter', {}).get('minOrderAmt', 0))
            min_order_qty = float(info.get('lotSizeFilter', {}).get('minOrderQty', 0))
            
            logger.info(f"\nالحد الأدنى المطلوب:")
            logger.info(f"  قيمة الطلب: ${min_order_amt}")
            logger.info(f"  كمية الطلب: {min_order_qty} BNB")
            
            return min_order_amt, min_order_qty
        else:
            logger.error("فشل في جلب معلومات الرمز")
            return None, None
        
    except Exception as e:
        logger.error(f"خطأ في تحليل المتطلبات: {e}")
        return None, None

def main():
    """الدالة الرئيسية"""
    logger.info("إصلاح مشكلة حساب الكمية في السبوت...")
    
    # تحليل متطلبات Bybit
    min_amt, min_qty = analyze_bybit_spot_requirements()
    
    # اختبار الحساب الصحيح
    success = test_correct_quantity_calculation()
    
    # تقرير النتائج
    logger.info("\n" + "="*60)
    logger.info("نتائج تحليل مشكلة حساب الكمية:")
    logger.info(f"الحد الأدنى لقيمة الطلب: ${min_amt if min_amt else 'غير محدد'}")
    logger.info(f"الحد الأدنى لكمية الطلب: {min_qty if min_qty else 'غير محدد'} BNB")
    logger.info(f"اختبار الحساب الصحيح: {'نجح' if success else 'فشل'}")
    
    logger.info("\nالمشكلة المكتشفة:")
    logger.info("1. الكود الحالي يستخدم: qty = amount / price")
    logger.info("2. هذا يعطي كمية صغيرة جداً")
    logger.info("3. Bybit يرفض الطلبات الصغيرة")
    
    logger.info("\nالحل المطلوب:")
    logger.info("1. استخدام qty مباشرة من الإشارة")
    logger.info("2. أو حساب qty بناءً على الحد الأدنى المطلوب")
    logger.info("3. أو استخدام amount كقيمة طلب وليس كمية")
    
    logger.info("="*60)

if __name__ == "__main__":
    main()
