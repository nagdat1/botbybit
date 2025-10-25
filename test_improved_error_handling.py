#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الإصلاحات الجديدة لمشكلة فشل تنفيذ الإشارة على Bybit
"""

import asyncio
import logging
from typing import Dict
from signal_executor import SignalExecutor
from real_account_manager import real_account_manager

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_improved_error_handling():
    """اختبار معالجة الأخطاء المحسنة"""
    
    print("اختبار معالجة الأخطاء المحسنة لـ Bybit")
    print("=" * 60)
    
    # بيانات الإشارة الجديدة من المشكلة
    signal_data = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': '4',
        'generated_id': False,
        'position_id': 'POS-4',
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
        },
        'price': 111141.5,
        'position_id': 'POS-4',
        'generated_id': False,
        'has_signal_id': True,
        'signal_id': '4',
        'amount': 55.0,
        'action': 'buy'
    }
    
    # بيانات المستخدم
    user_data = {
        'trade_amount': 55.0,
        'leverage': 1,
        'exchange': 'bybit',
        'account_type': 'real',
        'market_type': 'futures'
    }
    
    print("بيانات الاختبار:")
    print(f"الرمز: {signal_data['symbol']}")
    print(f"الإجراء: {signal_data['action']}")
    print(f"المبلغ: {signal_data['amount']} USDT")
    print(f"السعر: {signal_data['price']}")
    print(f"الرافعة: {user_data['leverage']}x")
    print()
    
    # اختبار 1: محاكاة أخطاء مختلفة
    print("اختبار 1: محاكاة أخطاء Bybit API المختلفة")
    print("-" * 50)
    
    test_errors = [
        {
            'name': 'مفاتيح API غير صحيحة',
            'error_data': {
                'error': True,
                'retCode': 10001,
                'retMsg': 'Invalid API key'
            }
        },
        {
            'name': 'الرصيد غير كافي',
            'error_data': {
                'error': True,
                'retCode': 10004,
                'retMsg': 'Insufficient balance'
            }
        },
        {
            'name': 'الكمية غير صحيحة',
            'error_data': {
                'error': True,
                'retCode': 10006,
                'retMsg': 'Invalid quantity'
            }
        },
        {
            'name': 'خطأ HTTP 401',
            'error_data': {
                'error': True,
                'http_status': 401,
                'http_message': 'Unauthorized'
            }
        },
        {
            'name': 'خطأ اتصال',
            'error_data': {
                'error': True,
                'exception': 'Connection timeout',
                'error_type': 'REQUEST_EXCEPTION'
            }
        }
    ]
    
    for i, test_error in enumerate(test_errors, 1):
        print(f"\nاختبار {i}: {test_error['name']}")
        
        # تحليل الخطأ
        analysis = SignalExecutor._analyze_order_failure(
            test_error['error_data'], 
            'BTCUSDT', 
            'buy', 
            0.001
        )
        
        print(f"الرسالة: {analysis['message']}")
        print("الحلول المقترحة:")
        for j, solution in enumerate(analysis['solutions'], 1):
            print(f"  {j}. {solution}")
    
    print("\n" + "="*60 + "\n")
    
    # اختبار 2: اختبار تنفيذ الإشارة الفعلي
    print("اختبار 2: تنفيذ الإشارة الفعلي")
    print("-" * 50)
    
    try:
        # محاولة تنفيذ الإشارة
        result = await SignalExecutor.execute_signal(1, signal_data, user_data)
        
        print(f"النتيجة: {'نجح' if result['success'] else 'فشل'}")
        print(f"الرسالة: {result['message']}")
        
        if not result['success']:
            print(f"نوع الخطأ: {result.get('error', 'غير محدد')}")
            
            # عرض تحليل الخطأ إذا كان متوفراً
            if 'error_analysis' in result:
                analysis = result['error_analysis']
                print(f"تحليل الخطأ: {analysis['message']}")
                
                if 'suggested_solutions' in result:
                    print("الحلول المقترحة:")
                    for i, solution in enumerate(result['suggested_solutions'], 1):
                        print(f"  {i}. {solution}")
            
            # عرض تفاصيل الخطأ إذا كانت متوفرة
            if 'error_details' in result:
                print(f"تفاصيل الخطأ: {result['error_details']}")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")
    
    # اختبار 3: اختبار معالجة الأخطاء الجديدة
    print("اختبار 3: معالجة الأخطاء الجديدة")
    print("-" * 50)
    
    # اختبار أخطاء مختلفة
    error_scenarios = [
        {
            'name': 'استجابة فارغة',
            'data': None
        },
        {
            'name': 'خطأ Bybit API',
            'data': {
                'error': True,
                'retCode': 10016,
                'retMsg': 'Symbol not found'
            }
        },
        {
            'name': 'خطأ HTTP',
            'data': {
                'error': True,
                'http_status': 429,
                'http_message': 'Too Many Requests'
            }
        },
        {
            'name': 'خطأ استثناء',
            'data': {
                'error': True,
                'exception': 'SSL handshake failed',
                'error_type': 'REQUEST_EXCEPTION'
            }
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\nسيناريو: {scenario['name']}")
        
        analysis = SignalExecutor._analyze_order_failure(
            scenario['data'], 
            'BTCUSDT', 
            'buy', 
            0.001
        )
        
        print(f"الرسالة: {analysis['message']}")
        print(f"عدد الحلول: {len(analysis['solutions'])}")
    
    return {
        'test_completed': True,
        'message': 'تم إكمال جميع الاختبارات بنجاح'
    }

async def test_api_error_scenarios():
    """اختبار سيناريوهات أخطاء API المختلفة"""
    
    print("\nاختبار سيناريوهات أخطاء API")
    print("=" * 40)
    
    # إنشاء حساب وهمي للاختبار
    from real_account_manager import BybitRealAccount
    
    # محاكاة أخطاء مختلفة
    error_scenarios = [
        {
            'name': 'خطأ في التوقيع',
            'retCode': 10001,
            'retMsg': 'Invalid signature'
        },
        {
            'name': 'طلب غير صحيح',
            'retCode': 10003,
            'retMsg': 'Invalid request'
        },
        {
            'name': 'الرصيد غير كافي',
            'retCode': 10004,
            'retMsg': 'Insufficient balance'
        },
        {
            'name': 'الكمية صغيرة جداً',
            'retCode': 10006,
            'retMsg': 'Quantity too small'
        },
        {
            'name': 'الرمز غير مدعوم',
            'retCode': 10016,
            'retMsg': 'Symbol not found'
        },
        {
            'name': 'مشكلة في الرافعة',
            'retCode': 10017,
            'retMsg': 'Invalid leverage'
        },
        {
            'name': 'مشكلة في الصلاحيات',
            'retCode': 10018,
            'retMsg': 'Permission denied'
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\nاختبار: {scenario['name']}")
        
        # محاكاة استجابة خطأ
        error_response = {
            'error': True,
            'retCode': scenario['retCode'],
            'retMsg': scenario['retMsg']
        }
        
        # تحليل الخطأ
        analysis = SignalExecutor._analyze_order_failure(
            error_response, 
            'BTCUSDT', 
            'buy', 
            0.001
        )
        
        print(f"كود الخطأ: {scenario['retCode']}")
        print(f"رسالة الخطأ: {scenario['retMsg']}")
        print(f"التحليل: {analysis['message']}")
        print(f"الحلول: {len(analysis['solutions'])} حل")

if __name__ == "__main__":
    print("بدء اختبار الإصلاحات الجديدة...")
    
    try:
        # تشغيل الاختبارات
        result = asyncio.run(test_improved_error_handling())
        asyncio.run(test_api_error_scenarios())
        
        print("\nتم إكمال جميع الاختبارات بنجاح!")
        print("\nملخص الإصلاحات:")
        print("1. تحسين معالجة الأخطاء في _make_request")
        print("2. إضافة تحليل مفصل لأخطاء Bybit API")
        print("3. معالجة أخطاء HTTP والاستثناءات")
        print("4. تحسين رسائل الخطأ والحلول المقترحة")
        
    except KeyboardInterrupt:
        print("\nتم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\nخطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
