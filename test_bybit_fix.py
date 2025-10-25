#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لحل مشكلة فشل تنفيذ الإشارة على Bybit
"""

import asyncio
import logging
from typing import Dict
from fix_btcusdt_signal import fix_btcusdt_signal_execution
from comprehensive_bybit_fix import quick_fix_bybit_signal

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bybit_fix_test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

async def test_bybit_signal_fix():
    """اختبار شامل لحل مشكلة Bybit"""
    
    print("🧪 اختبار شامل لحل مشكلة فشل تنفيذ الإشارة على Bybit")
    print("=" * 70)
    
    # بيانات الإشارة من المشكلة الأصلية
    test_signal = {
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
        'price': 111190.3,
        'position_id': 'POS-4',
        'generated_id': False,
        'has_signal_id': True,
        'signal_id': '4',
        'amount': 55.0,
        'action': 'buy'
    }
    
    # بيانات المستخدم للاختبار
    test_user_data = {
        'trade_amount': 55.0,
        'leverage': 1,
        'exchange': 'bybit',
        'account_type': 'real',
        'market_type': 'futures',
        'bybit_api_key': 'YOUR_API_KEY_HERE',  # يجب استبدالها
        'bybit_api_secret': 'YOUR_API_SECRET_HERE'  # يجب استبدالها
    }
    
    print("📊 بيانات الاختبار:")
    print(f"الرمز: {test_signal['symbol']}")
    print(f"الإجراء: {test_signal['action']}")
    print(f"المبلغ: {test_signal['amount']} USDT")
    print(f"السعر: {test_signal['price']}")
    print(f"الرافعة: {test_user_data['leverage']}x")
    print()
    
    # اختبار 1: الإصلاح المباشر
    print("🔧 اختبار 1: الإصلاح المباشر لإشارة BTCUSDT")
    print("-" * 50)
    
    try:
        result1 = await fix_btcusdt_signal_execution()
        
        print(f"النتيجة: {'✅ نجح' if result1['success'] else '❌ فشل'}")
        print(f"الرسالة: {result1['message']}")
        
        if not result1['success']:
            print(f"الخطأ: {result1.get('error', 'غير محدد')}")
            if 'possible_solutions' in result1:
                print("💡 الحلول المقترحة:")
                for i, solution in enumerate(result1['possible_solutions'], 1):
                    print(f"   {i}. {solution}")
        
        if 'fixes_applied' in result1:
            print(f"🔧 الإصلاحات المطبقة: {len(result1['fixes_applied'])}")
            for fix in result1['fixes_applied']:
                print(f"   • {fix}")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار 1: {e}")
    
    print("\n" + "="*70 + "\n")
    
    # اختبار 2: الإصلاح الشامل
    print("🔧 اختبار 2: الإصلاح الشامل")
    print("-" * 50)
    
    try:
        result2 = await quick_fix_bybit_signal(1, test_signal, test_user_data)
        
        print(f"النتيجة: {'✅ نجح' if result2['success'] else '❌ فشل'}")
        print(f"الرسالة: {result2['message']}")
        
        if 'diagnosis' in result2:
            print("\n🔍 نتائج التشخيص:")
            diagnosis = result2['diagnosis']
            for key, value in diagnosis.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
        
        if 'fixes_applied' in result2:
            print(f"\n🔧 الإصلاحات المطبقة: {len(result2['fixes_applied'])}")
            for fix in result2['fixes_applied']:
                print(f"   • {fix}")
        
        if 'errors_found' in result2:
            print(f"\n🚨 الأخطاء المكتشفة: {len(result2['errors_found'])}")
            for error in result2['errors_found']:
                print(f"   • {error}")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار 2: {e}")
    
    print("\n" + "="*70 + "\n")
    
    # ملخص النتائج
    print("📋 ملخص النتائج:")
    print("-" * 30)
    
    if 'result1' in locals() and result1['success']:
        print("✅ الإصلاح المباشر: نجح")
    else:
        print("❌ الإصلاح المباشر: فشل")
    
    if 'result2' in locals() and result2['success']:
        print("✅ الإصلاح الشامل: نجح")
    else:
        print("❌ الإصلاح الشامل: فشل")
    
    print("\n💡 توصيات:")
    print("1. تأكد من تحديث مفاتيح API في test_user_data")
    print("2. تحقق من وجود رصيد كافي في الحساب")
    print("3. تأكد من صحة إعدادات الحساب")
    print("4. جرب الإصلاحات المقترحة حسب نوع الخطأ")
    
    return {
        'test1_result': result1 if 'result1' in locals() else None,
        'test2_result': result2 if 'result2' in locals() else None
    }

async def test_specific_scenarios():
    """اختبار سيناريوهات محددة"""
    
    print("\n🎯 اختبار سيناريوهات محددة:")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'كمية صغيرة جداً',
            'signal': {'symbol': 'BTCUSDT', 'amount': 0.1, 'price': 111190.3, 'action': 'buy'},
            'expected': 'يجب تصحيح الكمية إلى الحد الأدنى'
        },
        {
            'name': 'رمز غير صحيح',
            'signal': {'symbol': 'INVALID', 'amount': 55.0, 'price': 100, 'action': 'buy'},
            'expected': 'يجب رفض الرمز غير الصحيح'
        },
        {
            'name': 'سعر صفر',
            'signal': {'symbol': 'BTCUSDT', 'amount': 55.0, 'price': 0, 'action': 'buy'},
            'expected': 'يجب جلب السعر الحالي'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 السيناريو {i}: {scenario['name']}")
        print(f"المتوقع: {scenario['expected']}")
        
        # هنا يمكن إضافة اختبارات محددة لكل سيناريو
        print("   (يتطلب مفاتيح API صحيحة للاختبار الفعلي)")

def print_usage_instructions():
    """طباعة تعليمات الاستخدام"""
    
    print("\n📖 تعليمات الاستخدام:")
    print("=" * 50)
    
    print("1. إصلاح سريع لمشكلة محددة:")
    print("   python fix_btcusdt_signal.py")
    
    print("\n2. إصلاح شامل:")
    print("   python comprehensive_bybit_fix.py")
    
    print("\n3. إصلاح مخصص:")
    print("   from fix_btcusdt_signal import fix_btcusdt_signal_execution")
    print("   result = await fix_btcusdt_signal_execution()")
    
    print("\n4. متطلبات:")
    print("   • مفاتيح Bybit API صحيحة")
    print("   • رصيد كافي في الحساب")
    print("   • اتصال بالإنترنت")
    print("   • صلاحيات التداول مفعلة")
    
    print("\n5. نصائح:")
    print("   • تأكد من صحة البيانات قبل التنفيذ")
    print("   • راقب السجلات للتفاصيل")
    print("   • جرب الحلول المقترحة حسب نوع الخطأ")

if __name__ == "__main__":
    print("🚀 بدء اختبار حل مشكلة Bybit...")
    
    # تشغيل الاختبارات
    try:
        result = asyncio.run(test_bybit_signal_fix())
        asyncio.run(test_specific_scenarios())
        print_usage_instructions()
        
        print("\n✅ انتهى الاختبار بنجاح!")
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\n💥 خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
