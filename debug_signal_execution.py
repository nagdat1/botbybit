#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص تفصيلي لمشكلة تنفيذ الإشارة
"""

import sys
import os
import asyncio
import logging

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_executor import SignalExecutor
from database import db_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_signal_execution():
    """فحص تفصيلي لمشكلة تنفيذ الإشارة"""
    
    print("=== فحص تفصيلي لمشكلة تنفيذ الإشارة ===")
    print()
    
    try:
        # بيانات المستخدم
        user_id = 999999
        
        print(f"1. جلب بيانات المستخدم {user_id}...")
        user_data = db_manager.get_user(user_id)
        if not user_data:
            print("فشل في جلب بيانات المستخدم")
            return False
        
        print(f"نوع الحساب: {user_data.get('account_type', 'N/A')}")
        print(f"المنصة: {user_data.get('exchange', 'N/A')}")
        print(f"نوع السوق: {user_data.get('market_type', 'N/A')}")
        print(f"API Key موجود: {'نعم' if user_data.get('bybit_api_key') else 'لا'}")
        print(f"API Secret موجود: {'نعم' if user_data.get('bybit_api_secret') else 'لا'}")
        print()
        
        # بيانات الإشارة
        signal_data = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'action': 'buy',
            'amount': 50.0,
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'signal_id': '4',
            'has_signal_id': True,
            'enhanced_analysis': {
                'signal_quality': 'high',
                'confidence_level': 0.9,
                'market_conditions': 'favorable',
                'recommendation': 'execute',
                'risk_level': 'medium',
                'signal_type': 'bullish',
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
        
        print("2. تنفيذ الإشارة...")
        print(f"الرمز: {signal_data['symbol']}")
        print(f"النوع: {signal_data['action']}")
        print(f"المبلغ: {signal_data['amount']}")
        print(f"الرافعة: {signal_data['leverage']}")
        print()
        
        result = await SignalExecutor.execute_signal(user_id, signal_data, user_data)
        
        print("3. نتيجة تنفيذ الإشارة:")
        print(f"النجاح: {result.get('success', False)}")
        print(f"الرسالة: {result.get('message', 'N/A')}")
        print(f"الخطأ: {result.get('error', 'N/A')}")
        print(f"تفاصيل الخطأ: {result.get('error_details', 'N/A')}")
        print()
        
        if result.get('success'):
            print("تم تنفيذ الإشارة بنجاح!")
            return True
        else:
            print("فشل في تنفيذ الإشارة")
            return False
            
    except Exception as e:
        print(f"خطأ في فحص تنفيذ الإشارة: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_signal_execution())
    if success:
        print("الفحص نجح!")
    else:
        print("الفحص فشل")
        sys.exit(1)
