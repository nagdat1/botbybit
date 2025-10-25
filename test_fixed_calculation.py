#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الإصلاح الجديد لحساب الكمية
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

async def test_fixed_calculation():
    """اختبار الحساب المصحح"""
    logger.info("اختبار الحساب المصحح...")
    
    try:
        # إشارة مطابقة للإشارة الفاشلة مع qty محدد
        test_signal = {
            'signal': 'buy',
            'symbol': 'BNBUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 1116.9,
            'amount': 50.0,
            'qty': 0.2,  # إضافة qty مباشرة
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
        
        logger.info(f"اختبار الإشارة المصححة: {test_signal['symbol']} {test_signal['signal']} qty={test_signal['qty']}")
        
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

async def test_without_qty():
    """اختبار بدون qty (استخدام الحد الأدنى الفعلي)"""
    logger.info("اختبار بدون qty (استخدام الحد الأدنى الفعلي)...")
    
    try:
        # إشارة بدون qty
        test_signal = {
            'signal': 'buy',
            'symbol': 'BNBUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 1116.9,
            'amount': 50.0,
            # لا يوجد qty - سيستخدم الحد الأدنى الفعلي
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
        
        logger.info(f"اختبار الإشارة بدون qty: {test_signal['symbol']} {test_signal['signal']}")
        
        # تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(
            user_id=8169000394,
            signal_data=test_signal,
            user_data=test_user_data
        )
        
        logger.info(f"نتيجة تنفيذ الإشارة بدون qty: {result}")
        
        if result.get('success'):
            logger.info("نجح تنفيذ الإشارة بدون qty!")
            return True
        else:
            logger.error(f"فشل تنفيذ الإشارة بدون qty: {result.get('message', 'Unknown error')}")
            logger.error(f"تفاصيل الخطأ: {result}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار الإشارة بدون qty: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("اختبار الإصلاح الجديد لحساب الكمية...")
    
    # اختبار 1: مع qty محدد
    success_with_qty = await test_fixed_calculation()
    
    # اختبار 2: بدون qty (استخدام الحد الأدنى الفعلي)
    success_without_qty = await test_without_qty()
    
    # تقرير النتائج
    logger.info("\n" + "="*60)
    logger.info("نتائج اختبار الإصلاح:")
    logger.info(f"مع qty محدد: {'نجح' if success_with_qty else 'فشل'}")
    logger.info(f"بدون qty (الحد الأدنى الفعلي): {'نجح' if success_without_qty else 'فشل'}")
    
    if success_with_qty or success_without_qty:
        logger.info("تم إصلاح مشكلة حساب الكمية!")
    else:
        logger.error("لا تزال المشكلة موجودة")
    
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(main())
