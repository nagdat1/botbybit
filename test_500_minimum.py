#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الحد الأدنى الجديد ($500)
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

async def test_500_minimum():
    """اختبار الحد الأدنى الجديد ($500)"""
    logger.info("اختبار الحد الأدنى الجديد ($500)...")
    
    try:
        # إشارة بدون qty (ستستخدم الحد الأدنى الجديد)
        test_signal = {
            'signal': 'buy',
            'symbol': 'BNBUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 1116.9,
            'amount': 50.0,
            # لا يوجد qty - سيستخدم الحد الأدنى الجديد ($500)
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': '4',
            'timestamp': datetime.now().isoformat(),
            'has_signal_id': True
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
        
        logger.info(f"اختبار الإشارة مع الحد الأدنى الجديد: {test_signal['symbol']} {test_signal['signal']}")
        
        # تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(
            user_id=8169000394,
            signal_data=test_signal,
            user_data=test_user_data
        )
        
        logger.info(f"نتيجة تنفيذ الإشارة مع الحد الأدنى الجديد: {result}")
        
        if result.get('success'):
            logger.info("نجح تنفيذ الإشارة مع الحد الأدنى الجديد!")
            return True
        else:
            logger.error(f"فشل تنفيذ الإشارة مع الحد الأدنى الجديد: {result.get('message', 'Unknown error')}")
            logger.error(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار الحد الأدنى الجديد: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_different_minimums():
    """اختبار حدود أدنى مختلفة"""
    logger.info("اختبار حدود أدنى مختلفة...")
    
    minimums_to_test = [300, 400, 500, 600, 700, 800, 900, 1000]
    
    for min_value in minimums_to_test:
        logger.info(f"اختبار الحد الأدنى: ${min_value}")
        
        try:
            # إشارة مع qty محدد بناءً على الحد الأدنى
            test_signal = {
                'signal': 'buy',
                'symbol': 'BNBUSDT',
                'id': '4',
                'generated_id': False,
                'position_id': 'POS-4',
                'price': 1116.9,
                'amount': 50.0,
                'qty': min_value / 1116.9,  # حساب qty بناءً على الحد الأدنى
                'leverage': 1,
                'exchange': 'bybit',
                'account_type': 'real',
                'signal_id': '4',
                'timestamp': datetime.now().isoformat(),
                'has_signal_id': True
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
            
            # تنفيذ الإشارة
            result = await SignalExecutor.execute_signal(
                user_id=8169000394,
                signal_data=test_signal,
                user_data=test_user_data
            )
            
            if result.get('success'):
                logger.info(f"نجح مع الحد الأدنى: ${min_value}")
                return min_value
            else:
                logger.warning(f"فشل مع الحد الأدنى: ${min_value} - {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"خطأ في اختبار الحد الأدنى ${min_value}: {e}")
    
    return None

async def main():
    """الدالة الرئيسية"""
    logger.info("اختبار الحد الأدنى الجديد ($500)...")
    
    # اختبار 1: الحد الأدنى الجديد ($500)
    success_500 = await test_500_minimum()
    
    # اختبار 2: حدود أدنى مختلفة
    working_minimum = await test_different_minimums()
    
    # تقرير النتائج
    logger.info("\n" + "="*60)
    logger.info("نتائج اختبار الحد الأدنى الجديد:")
    logger.info(f"الحد الأدنى $500: {'نجح' if success_500 else 'فشل'}")
    logger.info(f"الحد الأدنى العامل: ${working_minimum if working_minimum else 'غير محدد'}")
    
    if success_500:
        logger.info("تم إصلاح المشكلة مع الحد الأدنى $500!")
    elif working_minimum:
        logger.info(f"تم إصلاح المشكلة مع الحد الأدنى ${working_minimum}!")
    else:
        logger.error("لا تزال المشكلة موجودة حتى مع الحد الأدنى $1000")
    
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(main())
