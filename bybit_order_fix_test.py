#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح مشكلة تنفيذ الأوامر على Bybit
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
        logging.FileHandler('bybit_fix_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_bybit_api_connection():
    """اختبار الاتصال بـ Bybit API"""
    logger.info("🔍 اختبار الاتصال بـ Bybit API...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار جلب الرصيد
        balance = account.get_wallet_balance('spot')
        if balance:
            logger.info(f"✅ نجح الاتصال! الرصيد المتاح: {balance.get('available_balance', 0)} USDT")
            return True, account
        else:
            logger.error("❌ فشل في جلب الرصيد")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال: {e}")
        return False, None

async def test_order_placement(account):
    """اختبار وضع أمر تجريبي"""
    logger.info("🔍 اختبار وضع أمر تجريبي...")
    
    try:
        # اختبار أمر سبوت صغير جداً
        test_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001  # مبلغ صغير جداً للاختبار
        )
        
        if test_order and test_order.get('success'):
            logger.info(f"✅ نجح وضع الأمر! Order ID: {test_order.get('order_id')}")
            return True, test_order
        else:
            logger.error(f"❌ فشل وضع الأمر: {test_order}")
            return False, test_order
            
    except Exception as e:
        logger.error(f"❌ خطأ في وضع الأمر: {e}")
        return False, None

async def test_signal_execution():
    """اختبار تنفيذ الإشارة"""
    logger.info("🔍 اختبار تنفيذ الإشارة...")
    
    try:
        # إشارة تجريبية
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'TEST_001',
            'generated_id': False,
            'position_id': 'POS-TEST-001',
            'price': 111100.1,
            'amount': 40.0,
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': 'TEST_001',
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
            'market_type': 'spot',
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
            logger.info(f"✅ نجح تنفيذ الإشارة! النتيجة: {result}")
            return True, result
        else:
            logger.error(f"❌ فشل تنفيذ الإشارة: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"❌ خطأ في تنفيذ الإشارة: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """الدالة الرئيسية للاختبار"""
    logger.info("🚀 بدء اختبار إصلاح مشكلة Bybit...")
    
    # اختبار 1: الاتصال بـ API
    connection_success, account = await test_bybit_api_connection()
    if not connection_success:
        logger.error("❌ فشل اختبار الاتصال، إيقاف الاختبارات")
        return
    
    # اختبار 2: وضع أمر تجريبي
    order_success, order_result = await test_order_placement(account)
    if not order_success:
        logger.warning("⚠️ فشل اختبار وضع الأمر، لكن نتابع اختبار الإشارة")
    
    # اختبار 3: تنفيذ الإشارة
    signal_success, signal_result = await test_signal_execution()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("📊 تقرير نتائج الاختبار:")
    logger.info(f"🔗 الاتصال بـ API: {'✅ نجح' if connection_success else '❌ فشل'}")
    logger.info(f"📝 وضع الأمر: {'✅ نجح' if order_success else '❌ فشل'}")
    logger.info(f"📡 تنفيذ الإشارة: {'✅ نجح' if signal_success else '❌ فشل'}")
    
    if signal_success:
        logger.info("🎉 تم إصلاح المشكلة بنجاح!")
    else:
        logger.error("❌ لا تزال هناك مشاكل تحتاج إلى إصلاح")
        if signal_result:
            logger.error(f"تفاصيل الخطأ: {signal_result}")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
