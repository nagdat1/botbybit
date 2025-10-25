#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص مشكلة فشل تنفيذ الإشارة مع BNBUSDT
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_account_manager import BybitRealAccount
from signal_executor import SignalExecutor
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

async def test_bnbusdt_order():
    """اختبار طلب BNBUSDT"""
    logger.info("اختبار طلب BNBUSDT...")
    
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
        
        # حساب الكمية بناءً على المبلغ المطلوب (50 دولار)
        amount_usd = 50.0
        qty = amount_usd / current_price
        logger.info(f"المبلغ المطلوب: ${amount_usd}")
        logger.info(f"الكمية المحسوبة: {qty:.6f} BNB")
        
        # اختبار وضع الأمر
        test_order = account.place_order(
            category='spot',
            symbol='BNBUSDT',
            side='Buy',
            order_type='Market',
            qty=round(qty, 6)
        )
        
        logger.info(f"نتيجة الطلب: {test_order}")
        
        if test_order and test_order.get('success'):
            logger.info("نجح طلب BNBUSDT!")
            return True
        else:
            error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
            error_code = test_order.get('error_code') if test_order else 'Unknown'
            logger.error(f"فشل طلب BNBUSDT: {error_code} - {error_msg}")
            return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار BNBUSDT: {e}")
        return False

async def test_bnbusdt_signal():
    """اختبار إشارة BNBUSDT"""
    logger.info("اختبار إشارة BNBUSDT...")
    
    try:
        # إشارة مطابقة للإشارة الفاشلة
        test_signal = {
            'signal': 'buy',
            'symbol': 'BNBUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 1116.9,
            'amount': 50.0,
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': '4',
            'timestamp': datetime.now().isoformat(),
            'has_signal_id': True,
            'enhanced_analysis': {
                'signal_quality': 'high',
                'confidence_level': 0.85,
                'market_conditions': 'favorable',
                'recommendation': 'execute',
                'risk_level': 'medium',
                'asset_type': 'stablecoin_pair',
                'volatility': 'medium'
            },
            'enhanced_risk_assessment': {
                'risk_level': 'low',
                'max_position_size': 0.2,
                'stop_loss': 0.02,
                'take_profit': 0.04,
                'recommendation': 'proceed_with_caution'
            },
            'enhanced_execution_plan': {
                'strategy': 'immediate',
                'timing': 'optimal',
                'price_optimization': True,
                'slippage_protection': True,
                'execution_priority': 'high',
                'execution_time': '1_minute'
            }
        }
        
        # بيانات المستخدم
        test_user_data = {
            'trade_amount': 50.0,
            'leverage': 1,
            'market_type': 'spot',
            'account_type': 'real',
            'bybit_api_key': BYBIT_API_KEY,
            'bybit_api_secret': BYBIT_API_SECRET
        }
        
        logger.info(f"اختبار الإشارة: {test_signal['symbol']} {test_signal['signal']} ${test_signal['amount']}")
        
        # تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(
            user_id=8169000394,
            signal_data=test_signal,
            user_data=test_user_data
        )
        
        logger.info(f"نتيجة تنفيذ الإشارة: {result}")
        
        if result.get('success'):
            logger.info("نجح تنفيذ إشارة BNBUSDT!")
            return True
        else:
            logger.error(f"فشل تنفيذ إشارة BNBUSDT: {result.get('message', 'Unknown error')}")
            logger.error(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار إشارة BNBUSDT: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_different_amounts_bnb():
    """اختبار مبالغ مختلفة لـ BNBUSDT"""
    logger.info("اختبار مبالغ مختلفة لـ BNBUSDT...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # جلب السعر الحالي
        ticker = account.get_ticker('spot', 'BNBUSDT')
        if not ticker:
            logger.error("فشل في جلب السعر")
            return False
        
        current_price = float(ticker['lastPrice'])
        logger.info(f"السعر الحالي: ${current_price}")
        
        # اختبار مبالغ مختلفة
        test_amounts = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        for amount_usd in test_amounts:
            qty = amount_usd / current_price
            logger.info(f"اختبار ${amount_usd} = {qty:.6f} BNB")
            
            test_order = account.place_order(
                category='spot',
                symbol='BNBUSDT',
                side='Buy',
                order_type='Market',
                qty=round(qty, 6)
            )
            
            if test_order and test_order.get('success'):
                logger.info(f"نجح مع المبلغ: ${amount_usd}")
                return amount_usd
            else:
                error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
                logger.warning(f"فشل مع المبلغ ${amount_usd}: {error_msg}")
        
        logger.error("لم تنجح أي مبلغ")
        return None
        
    except Exception as e:
        logger.error(f"خطأ في اختبار المبالغ: {e}")
        return None

async def main():
    """الدالة الرئيسية"""
    logger.info("فحص مشكلة فشل تنفيذ الإشارة مع BNBUSDT...")
    
    # اختبار 1: طلب مباشر
    direct_success = await test_bnbusdt_order()
    
    # اختبار 2: إشارة كاملة
    signal_success = await test_bnbusdt_signal()
    
    # اختبار 3: مبالغ مختلفة
    min_amount = await test_different_amounts_bnb()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج فحص BNBUSDT:")
    logger.info(f"الطلب المباشر: {'نجح' if direct_success else 'فشل'}")
    logger.info(f"تنفيذ الإشارة: {'نجح' if signal_success else 'فشل'}")
    logger.info(f"الحد الأدنى للمبلغ: ${min_amount if min_amount else 'غير محدد'}")
    
    if not direct_success and not signal_success:
        logger.error("المشكلة لا تزال موجودة مع BNBUSDT")
        logger.info("الأسباب المحتملة:")
        logger.info("1. BNBUSDT قد لا يكون متاح للتداول الفوري")
        logger.info("2. الحد الأدنى للطلب أعلى من المتوقع")
        logger.info("3. مشكلة في إعدادات الحساب")
        logger.info("4. العملة قد تكون مقيدة")
    else:
        logger.info("تم حل المشكلة مع BNBUSDT!")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
