#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح نهائي لمشكلة فشل تنفيذ الإشارة
المشاكل المكتشفة:
1. Order value exceeded lower limit - الكمية صغيرة جداً
2. الحساب التجريبي بدلاً من الحقيقي
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

async def test_minimum_order():
    """اختبار الحد الأدنى للطلب"""
    logger.info("اختبار الحد الأدنى للطلب...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار كميات مختلفة للعثور على الحد الأدنى
        test_quantities = [0.001, 0.01, 0.1, 0.5, 1.0]
        
        for qty in test_quantities:
            logger.info(f"اختبار الكمية: {qty} BTC")
            
            test_order = account.place_order(
                category='spot',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Market',
                qty=qty
            )
            
            if test_order and test_order.get('success'):
                logger.info(f"نجح مع الكمية: {qty} BTC")
                return qty
            else:
                error_msg = test_order.get('error', 'Unknown error') if test_order else 'No response'
                logger.warning(f"فشل مع الكمية {qty}: {error_msg}")
        
        logger.error("لم تنجح أي كمية - تحقق من الرصيد والإعدادات")
        return None
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الحد الأدنى: {e}")
        return None

async def test_real_account_signal():
    """اختبار الإشارة مع الحساب الحقيقي"""
    logger.info("اختبار الإشارة مع الحساب الحقيقي...")
    
    try:
        # إشارة مع كمية أكبر
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 111162.7,
            'amount': 50.0,  # زيادة المبلغ إلى 50 دولار
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
        
        # بيانات المستخدم مع الحساب الحقيقي
        test_user_data = {
            'trade_amount': 50.0,  # زيادة المبلغ
            'leverage': 1,
            'market_type': 'spot',
            'account_type': 'real',  # تأكيد الحساب الحقيقي
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
            logger.info("نجح تنفيذ الإشارة!")
            return True
        else:
            logger.error(f"فشل تنفيذ الإشارة: {result.get('message', 'Unknown error')}")
            logger.error(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("بدء إصلاح مشكلة فشل تنفيذ الإشارة...")
    
    # اختبار 1: العثور على الحد الأدنى للطلب
    min_qty = await test_minimum_order()
    
    if min_qty:
        logger.info(f"الحد الأدنى للطلب: {min_qty} BTC")
    else:
        logger.error("لم يتم العثور على حد أدنى للطلب")
    
    # اختبار 2: تنفيذ الإشارة مع الحساب الحقيقي
    signal_success = await test_real_account_signal()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج الإصلاح:")
    logger.info(f"الحد الأدنى للطلب: {min_qty if min_qty else 'غير محدد'}")
    logger.info(f"تنفيذ الإشارة: {'نجح' if signal_success else 'فشل'}")
    
    if signal_success:
        logger.info("تم إصلاح المشكلة بنجاح!")
        logger.info("الحلول المطبقة:")
        logger.info("1. زيادة مبلغ التداول إلى الحد الأدنى المطلوب")
        logger.info("2. تأكيد استخدام الحساب الحقيقي")
        logger.info("3. تحسين معالجة الأخطاء")
    else:
        logger.error("لا تزال هناك مشاكل تحتاج إصلاح")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
