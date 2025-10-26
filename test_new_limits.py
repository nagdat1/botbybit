#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الحدود الأدنى الجديدة
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

async def test_new_limits():
    """اختبار الحدود الأدنى الجديدة"""
    logger.info("اختبار الحدود الأدنى الجديدة...")
    
    try:
        # إشارة BTCUSDT مع الحد الأدنى الجديد ($5000)
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 111279.4,
            'amount': 52.0,
            # لا يوجد qty - سيستخدم الحد الأدنى الجديد ($5000)
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': '4',
            'timestamp': datetime.now().isoformat(),
            'has_signal_id': True
        }
        
        # بيانات المستخدم
        test_user_data = {
            'trade_amount': 52.0,
            'leverage': 1,
            'market_type': 'spot',
            'account_type': 'real',
            'bybit_api_key': BYBIT_API_KEY,
            'bybit_api_secret': BYBIT_API_SECRET
        }
        
        logger.info(f"اختبار الإشارة المصححة: {test_signal['symbol']} {test_signal['signal']}")
        logger.info(f"الحد الأدنى الجديد: $5000 لـ BTCUSDT")
        
        # تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(
            user_id=8169000394,
            signal_data=test_signal,
            user_data=test_user_data
        )
        
        logger.info(f"نتيجة تنفيذ الإشارة المصححة: {result}")
        
        if result.get('success'):
            logger.info("نجح تنفيذ الإشارة المصححة!")
            return True
        else:
            logger.error(f"فشل تنفيذ الإشارة المصححة: {result.get('message', 'Unknown error')}")
            logger.error(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار الإشارة المصححة: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("اختبار الحدود الأدنى الجديدة...")
    
    # اختبار BTCUSDT مع الحد الأدنى الجديد
    success = await test_new_limits()
    
    # تقرير النتائج
    logger.info("\n" + "="*60)
    logger.info("نتائج اختبار الحدود الأدنى الجديدة:")
    logger.info(f"BTCUSDT مع الحد الأدنى $5000: {'نجح' if success else 'فشل'}")
    
    if success:
        logger.info("تم إصلاح مشكلة الحد الأدنى!")
    else:
        logger.error("لا تزال المشكلة موجودة")
        logger.error("قد يحتاج الحد الأدنى إلى زيادة أكثر")
    
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(main())

