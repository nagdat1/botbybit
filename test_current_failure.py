#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مباشر لمعرفة سبب فشل تنفيذ الإشارة
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

async def test_current_signal():
    """اختبار الإشارة الحالية"""
    logger.info("اختبار الإشارة الحالية...")
    
    try:
        # إشارة مطابقة للإشارة الفاشلة
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': '4',
            'generated_id': False,
            'position_id': 'POS-4',
            'price': 111162.7,
            'amount': 40.0,
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
        
        # بيانات المستخدم
        test_user_data = {
            'trade_amount': 40.0,
            'leverage': 1,
            'market_type': 'spot',  # تجربة السبوت أولاً
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

async def test_direct_order():
    """اختبار وضع أمر مباشر"""
    logger.info("اختبار وضع أمر مباشر...")
    
    try:
        # إنشاء حساب Bybit
        account = BybitRealAccount(BYBIT_API_KEY, BYBIT_API_SECRET)
        
        # اختبار جلب الرصيد أولاً
        balance = account.get_wallet_balance('spot')
        if balance:
            logger.info(f"الرصيد المتاح: {balance.get('available_balance', 0)} USDT")
            logger.info(f"الرصيد الإجمالي: {balance.get('total_equity', 0)} USDT")
            
            # فحص رصيد USDT
            if 'coins' in balance and 'USDT' in balance['coins']:
                usdt_balance = balance['coins']['USDT']['equity']
                logger.info(f"رصيد USDT: {usdt_balance}")
                
                if usdt_balance < 50:
                    logger.warning(f"الرصيد منخفض: {usdt_balance} USDT - قد يكون هذا سبب الفشل")
                else:
                    logger.info("الرصيد كافي للصفقة")
            else:
                logger.warning("لم يتم العثور على رصيد USDT")
        else:
            logger.error("فشل في جلب الرصيد")
            return False
        
        # اختبار وضع أمر صغير جداً
        test_order = account.place_order(
            category='spot',
            symbol='BTCUSDT',
            side='Buy',
            order_type='Market',
            qty=0.001  # مبلغ صغير جداً للاختبار
        )
        
        logger.info(f"نتيجة وضع الأمر: {test_order}")
        
        if test_order and test_order.get('success'):
            logger.info("نجح وضع الأمر!")
            return True
        else:
            logger.error(f"فشل وضع الأمر: {test_order}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار وضع الأمر: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("بدء اختبار مباشر لمعرفة سبب فشل الإشارة...")
    
    # اختبار 1: وضع أمر مباشر
    direct_success = await test_direct_order()
    
    # اختبار 2: تنفيذ الإشارة
    signal_success = await test_current_signal()
    
    # تقرير النتائج
    logger.info("\n" + "="*50)
    logger.info("نتائج الاختبار المباشر:")
    logger.info(f"وضع الأمر المباشر: {'نجح' if direct_success else 'فشل'}")
    logger.info(f"تنفيذ الإشارة: {'نجح' if signal_success else 'فشل'}")
    
    if not direct_success:
        logger.error("المشكلة في وضع الأمر المباشر - تحقق من:")
        logger.error("1. الرصيد المتاح")
        logger.error("2. مفاتيح API")
        logger.error("3. إعدادات الحساب")
    
    if not signal_success:
        logger.error("المشكلة في تنفيذ الإشارة - تحقق من:")
        logger.error("1. إعدادات نوع الحساب")
        logger.error("2. إعدادات نوع السوق")
        logger.error("3. معالجة الإشارة")
    
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main())
