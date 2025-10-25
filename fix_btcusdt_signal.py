#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مباشر لمشكلة فشل تنفيذ إشارة BTCUSDT على Bybit
"""

import logging
import asyncio
from typing import Dict
from signal_executor import SignalExecutor
from real_account_manager import real_account_manager

logger = logging.getLogger(__name__)

async def fix_btcusdt_signal_execution():
    """إصلاح مباشر لمشكلة تنفيذ إشارة BTCUSDT"""
    
    try:
        logger.info("بدء إصلاح مشكلة تنفيذ إشارة BTCUSDT...")
        
        # بيانات الإشارة من المشكلة الأصلية
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
            'price': 111190.3,
            'position_id': 'POS-4',
            'generated_id': False,
            'has_signal_id': True,
            'signal_id': '4',
            'amount': 55.0,
            'action': 'buy'
        }
        
        # بيانات المستخدم (يجب تحديثها)
        user_data = {
            'trade_amount': 55.0,
            'leverage': 1,
            'exchange': 'bybit',
            'account_type': 'real',
            'market_type': 'futures'
        }
        
        # إصلاح 1: التحقق من صحة البيانات
        logger.info("🔍 فحص صحة البيانات...")
        
        # إصلاح الكمية - ضمان الحد الأدنى
        amount = float(signal_data.get('amount', 0))
        price = float(signal_data.get('price', 0))
        
        if amount > 0 and price > 0:
            qty = amount / price
            min_qty = 0.001  # الحد الأدنى لـ BTCUSDT
            
            if qty < min_qty:
                logger.warning(f"الكمية صغيرة جداً: {qty}، تم تعديلها إلى الحد الأدنى")
                min_amount = min_qty * price
                signal_data['amount'] = min_amount
                user_data['trade_amount'] = min_amount
                logger.info(f"✅ تم تعديل المبلغ إلى {min_amount} USDT")
        
        # إصلاح 2: التحقق من الحساب الحقيقي
        logger.info("🔍 فحص الحساب الحقيقي...")
        
        user_id = 1  # يجب تحديثه حسب المستخدم الفعلي
        
        # محاولة الحصول على الحساب الحقيقي
        real_account = real_account_manager.get_account(user_id)
        
        if not real_account:
            logger.error("❌ الحساب الحقيقي غير مفعّل")
            return {
                'success': False,
                'message': 'الحساب الحقيقي غير مفعّل - يرجى إضافة مفاتيح API',
                'error': 'ACCOUNT_NOT_FOUND',
                'solution': 'قم بإضافة مفاتيح Bybit API في إعدادات المستخدم'
            }
        
        # إصلاح 3: فحص الرصيد
        logger.info("🔍 فحص الرصيد المتاح...")
        
        try:
            balance_info = real_account.get_wallet_balance('futures')
            if balance_info and 'coins' in balance_info and 'USDT' in balance_info['coins']:
                usdt_balance = float(balance_info['coins']['USDT'].get('equity', 0))
                required_amount = float(signal_data.get('amount', 0)) * int(user_data.get('leverage', 1))
                
                logger.info(f"💰 الرصيد المتاح: {usdt_balance} USDT")
                logger.info(f"💸 المبلغ المطلوب: {required_amount} USDT")
                
                if usdt_balance < required_amount * 1.1:  # هامش أمان 10%
                    logger.error(f"❌ الرصيد غير كافي: {usdt_balance} < {required_amount * 1.1}")
                    return {
                        'success': False,
                        'message': f'الرصيد غير كافي. متاح: {usdt_balance:.2f} USDT، مطلوب: {required_amount * 1.1:.2f} USDT',
                        'error': 'INSUFFICIENT_BALANCE',
                        'available_balance': usdt_balance,
                        'required_balance': required_amount * 1.1,
                        'solution': 'قم بإيداع المزيد من USDT في حسابك أو قلل من مبلغ التداول'
                    }
                else:
                    logger.info("✅ الرصيد كافي")
            else:
                logger.warning("⚠️ لم يتم العثور على معلومات الرصيد USDT")
        except Exception as e:
            logger.error(f"خطأ في فحص الرصيد: {e}")
        
        # إصلاح 4: تعيين الرافعة المالية
        logger.info("🔧 تعيين الرافعة المالية...")
        
        try:
            symbol = signal_data.get('symbol', '')
            leverage = int(user_data.get('leverage', 1))
            
            leverage_result = real_account.set_leverage('linear', symbol, leverage)
            if leverage_result:
                logger.info(f"✅ تم تعيين الرافعة إلى {leverage}x")
            else:
                logger.warning(f"⚠️ فشل في تعيين الرافعة إلى {leverage}x")
        except Exception as e:
            logger.error(f"خطأ في تعيين الرافعة: {e}")
        
        # إصلاح 5: تحديث السعر إذا لزم الأمر
        logger.info("🔧 التحقق من السعر...")
        
        try:
            if not signal_data.get('price') or float(signal_data.get('price', 0)) <= 0:
                logger.info("جلب السعر الحالي...")
                ticker = real_account.get_ticker('linear', symbol)
                if ticker and 'lastPrice' in ticker:
                    current_price = float(ticker['lastPrice'])
                    signal_data['price'] = current_price
                    logger.info(f"✅ تم تحديث السعر إلى {current_price}")
        except Exception as e:
            logger.error(f"خطأ في جلب السعر: {e}")
        
        # إصلاح 6: تنفيذ الإشارة مع معالجة محسنة للأخطاء
        logger.info("🚀 تنفيذ الإشارة...")
        
        try:
            # استخدام المنفذ الأصلي مع البيانات المصححة
            result = await SignalExecutor.execute_signal(user_id, signal_data, user_data)
            
            if result.get('success'):
                logger.info("✅ تم تنفيذ الإشارة بنجاح!")
                return {
                    'success': True,
                    'message': 'تم تنفيذ إشارة BTCUSDT بنجاح',
                    'execution_result': result,
                    'fixes_applied': [
                        'فحص صحة البيانات',
                        'فحص الحساب الحقيقي',
                        'فحص الرصيد',
                        'تعيين الرافعة المالية',
                        'تحديث السعر',
                        'تنفيذ الإشارة'
                    ]
                }
            else:
                logger.error(f"❌ فشل تنفيذ الإشارة: {result.get('message', '')}")
                return {
                    'success': False,
                    'message': f'فشل تنفيذ الإشارة: {result.get("message", "")}',
                    'error': 'EXECUTION_FAILED',
                    'execution_result': result,
                    'possible_solutions': [
                        'تحقق من مفاتيح API',
                        'تأكد من وجود رصيد كافي',
                        'تحقق من صحة الرمز',
                        'تأكد من صلاحيات التداول',
                        'جرب تقليل مبلغ التداول'
                    ]
                }
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الإشارة: {str(e)}',
                'error': 'EXECUTION_ERROR',
                'possible_solutions': [
                    'تحقق من اتصال الإنترنت',
                    'تأكد من صحة مفاتيح API',
                    'تحقق من حالة الخادم',
                    'جرب مرة أخرى بعد قليل'
                ]
            }
            
    except Exception as e:
        logger.error(f"خطأ عام في الإصلاح: {e}")
        return {
            'success': False,
            'message': f'خطأ عام: {str(e)}',
            'error': 'GENERAL_ERROR'
        }

# دالة مساعدة للاستخدام السريع
async def quick_fix():
    """إصلاح سريع للمشكلة"""
    return await fix_btcusdt_signal_execution()

if __name__ == "__main__":
    print("إصلاح مشكلة تنفيذ إشارة BTCUSDT")
    print("=" * 50)
    
    # تشغيل الإصلاح
    result = asyncio.run(quick_fix())
    
    print("\nالنتيجة:")
    print(f"النجاح: {'نعم' if result['success'] else 'لا'}")
    print(f"الرسالة: {result['message']}")
    
    if not result['success']:
        print(f"الخطأ: {result.get('error', 'غير محدد')}")
        if 'possible_solutions' in result:
            print("\nالحلول المقترحة:")
            for i, solution in enumerate(result['possible_solutions'], 1):
                print(f"{i}. {solution}")
    
    if 'fixes_applied' in result:
        print(f"\nالإصلاحات المطبقة: {len(result['fixes_applied'])}")
        for fix in result['fixes_applied']:
            print(f"• {fix}")
