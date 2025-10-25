#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة الرافعة المالية في Bybit
المشكلة: فشل تنفيذ الصفقات بعد تغيير الرافعة المالية
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
        logging.FileHandler('leverage_fix_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_leverage_setting():
    """اختبار تعيين الرافعة المالية"""
    logger.info("اختبار تعيين الرافعة المالية...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار تعيين الرافعة المالية لـ BTCUSDT
        leverage_result = account.set_leverage('linear', 'BTCUSDT', 1)
        
        if leverage_result:
            logger.info("نجح تعيين الرافعة المالية!")
            return True, account
        else:
            logger.error("فشل تعيين الرافعة المالية")
            return False, account
            
    except Exception as e:
        logger.error(f"خطأ في تعيين الرافعة المالية: {e}")
        return False, None

async def test_order_with_leverage(account):
    """اختبار وضع أمر مع الرافعة المالية"""
    logger.info("اختبار وضع أمر مع الرافعة المالية...")
    
    try:
        # اختبار أمر فيوتشر صغير جداً
        test_order = account.place_order(
            category='linear',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001,  # مبلغ صغير جداً للاختبار
            leverage=1
        )
        
        if test_order and test_order.get('success'):
            logger.info(f"نجح وضع الأمر! Order ID: {test_order.get('order_id')}")
            return True, test_order
        else:
            logger.error(f"فشل وضع الأمر: {test_order}")
            return False, test_order
            
    except Exception as e:
        logger.error(f"خطأ في وضع الأمر: {e}")
        return False, None

async def test_signal_execution_with_leverage():
    """اختبار تنفيذ الإشارة مع الرافعة المالية"""
    logger.info("اختبار تنفيذ الإشارة مع الرافعة المالية...")
    
    try:
        # إشارة تجريبية للفيوتشر
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'LEVERAGE_TEST_001',
            'generated_id': False,
            'position_id': 'POS-LEVERAGE-TEST-001',
            'price': 111100.1,
            'amount': 40.0,
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': 'LEVERAGE_TEST_001',
            'timestamp': datetime.now().isoformat(),
            'has_signal_id': True,
            'enhanced_analysis': {
                'signal_quality': 'high',
                'confidence_level': 0.85,
                'market_conditions': 'favorable',
                'recommendation': 'execute',
                'risk_level': 'medium',
                'asset_type': 'cryptocurrency',
                'volatility': 'high'
            },
            'enhanced_risk_assessment': {
                'risk_level': 'low',
                'max_position_size': 0.2,
                'stop_loss': 0.02,
                'take_profit': 0.04,
                'recommendation': 'proceed_with_caution'
            },
            'enhanced_execution_plan': {
                'strategy': 'TWAP',
                'timing': 'optimal',
                'price_optimization': True,
                'slippage_protection': True,
                'execution_priority': 'high',
                'execution_time': '5_minutes'
            }
        }
        
        # بيانات المستخدم التجريبية
        test_user_data = {
            'trade_amount': 40.0,
            'leverage': 1,
            'market_type': 'futures',  # فيوتشر لاختبار الرافعة المالية
            'bybit_api_key': BYBIT_API_KEY,
            'bybit_api_secret': BYBIT_API_SECRET
        }
        
        # تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(
            user_id=8169000394,  # ID المستخدم التجريبي
            signal_data=test_signal,
            user_data=test_user_data
        )
        
        if result.get('success'):
            logger.info(f"نجح تنفيذ الإشارة! النتيجة: {result}")
            return True, result
        else:
            logger.error(f"فشل تنفيذ الإشارة: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"خطأ في تنفيذ الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """الدالة الرئيسية للاختبار"""
    logger.info("بدء اختبار إصلاح مشكلة الرافعة المالية...")
    
    # اختبار 1: تعيين الرافعة المالية
    leverage_success, account = await test_leverage_setting()
    if not leverage_success:
        logger.error("فشل اختبار تعيين الرافعة المالية")
        return
    
    # اختبار 2: وضع أمر مع الرافعة المالية
    order_success, order_result = await test_order_with_leverage(account)
    if not order_success:
        logger.warning("فشل اختبار وضع الأمر، لكن نتابع اختبار الإشارة")
    
    # اختبار 3: تنفيذ الإشارة مع الرافعة المالية
    signal_success, signal_result = await test_signal_execution_with_leverage()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("تقرير نتائج اختبار الرافعة المالية:")
    logger.info(f"تعيين الرافعة المالية: {'نجح' if leverage_success else 'فشل'}")
    logger.info(f"وضع الأمر: {'نجح' if order_success else 'فشل'}")
    logger.info(f"تنفيذ الإشارة: {'نجح' if signal_success else 'فشل'}")
    
    if signal_success:
        logger.info("تم إصلاح مشكلة الرافعة المالية بنجاح!")
    else:
        logger.error("لا تزال هناك مشاكل في الرافعة المالية")
        if signal_result:
            logger.error(f"تفاصيل الخطأ: {signal_result}")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
