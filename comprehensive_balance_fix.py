#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الإصلاح الشامل لمشكلة عدم كفاية الرصيد
يدمج النظام المحسن مع النظام الحالي
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from signal_executor import signal_executor
from balance_fix_system import enhanced_signal_executor, balance_validator

logger = logging.getLogger(__name__)

class ComprehensiveBalanceFix:
    """نظام الإصلاح الشامل لمشكلة عدم كفاية الرصيد"""
    
    @staticmethod
    async def execute_signal_with_comprehensive_fix(
        user_id: int, 
        signal_data: Dict, 
        user_data: Dict
    ) -> Dict:
        """
        تنفيذ الإشارة مع الإصلاح الشامل لمشكلة عدم كفاية الرصيد
        
        هذا النظام يجمع بين:
        1. النظام المحسن للتحقق من الرصيد
        2. النظام العادي كـ fallback
        3. معالجة محسنة للأخطاء
        4. اقتراحات ذكية للمستخدم
        """
        try:
            logger.info(f"🔧 بدء الإصلاح الشامل للإشارة للمستخدم {user_id}")
            
            # الخطوة 1: محاولة استخدام النظام المحسن أولاً
            try:
                logger.info("🔄 المحاولة الأولى: النظام المحسن")
                
                enhanced_result = await enhanced_signal_executor.execute_signal_with_balance_check(
                    user_id, signal_data, user_data
                )
                
                if enhanced_result.get('success'):
                    logger.info("✅ نجح النظام المحسن")
                    return enhanced_result
                
                # إذا فشل بسبب عدم كفاية الرصيد، نعيد النتيجة مع الاقتراحات
                if enhanced_result.get('error') == 'INSUFFICIENT_BALANCE':
                    logger.warning("⚠️ فشل بسبب عدم كفاية الرصيد - إرجاع النتيجة المحسنة")
                    return enhanced_result
                
                # للأخطاء الأخرى، نتابع للنظام العادي
                logger.warning(f"⚠️ فشل النظام المحسن لأسباب أخرى: {enhanced_result.get('message')}")
                
            except Exception as e:
                logger.error(f"❌ خطأ في النظام المحسن: {e}")
            
            # الخطوة 2: استخدام النظام العادي كـ fallback
            logger.info("🔄 المحاولة الثانية: النظام العادي")
            
            try:
                fallback_result = await signal_executor.execute_signal(user_id, signal_data, user_data)
                
                if fallback_result.get('success'):
                    logger.info("✅ نجح النظام العادي")
                    return fallback_result
                
                # تحليل خطأ النظام العادي
                error_message = fallback_result.get('message', '')
                
                if 'الرصيد غير كافي' in error_message or 'insufficient balance' in error_message.lower():
                    logger.warning("⚠️ النظام العادي أيضاً فشل بسبب عدم كفاية الرصيد")
                    
                    # محاولة اقتراح حلول
                    suggestion = await ComprehensiveBalanceFix._generate_balance_suggestions(
                        user_id, signal_data, user_data
                    )
                    
                    return {
                        'success': False,
                        'message': f'الرصيد غير كافي. {suggestion}',
                        'error': 'INSUFFICIENT_BALANCE',
                        'suggestion': suggestion,
                        'fallback_result': fallback_result
                    }
                
                logger.error(f"❌ فشل النظام العادي: {error_message}")
                return fallback_result
                
            except Exception as e:
                logger.error(f"❌ خطأ في النظام العادي: {e}")
            
            # الخطوة 3: إذا فشل كل شيء، إرجاع رسالة خطأ شاملة
            logger.error("❌ فشل جميع المحاولات")
            
            return {
                'success': False,
                'message': 'فشل تنفيذ الإشارة - تحقق من الرصيد والإعدادات',
                'error': 'COMPREHENSIVE_FAILURE',
                'suggestions': [
                    'تحقق من وجود رصيد كافي في الحساب',
                    'تأكد من صحة مفاتيح API',
                    'تحقق من إعدادات الرافعة المالية',
                    'جرب مبلغ تداول أقل'
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الإصلاح الشامل: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'message': f'خطأ في الإصلاح الشامل: {str(e)}',
                'error': 'COMPREHENSIVE_ERROR'
            }
    
    @staticmethod
    async def _generate_balance_suggestions(
        user_id: int, 
        signal_data: Dict, 
        user_data: Dict
    ) -> str:
        """توليد اقتراحات ذكية لحل مشكلة عدم كفاية الرصيد"""
        try:
            from real_account_manager import real_account_manager
            
            real_account = real_account_manager.get_account(user_id)
            if not real_account:
                return "تحقق من إعدادات الحساب الحقيقي"
            
            # جلب معلومات الرصيد
            market_type = user_data.get('market_type', 'futures')
            account_type = 'futures' if market_type == 'futures' else 'spot'
            
            balance_info = real_account.get_wallet_balance(account_type)
            
            if not balance_info or 'coins' not in balance_info or 'USDT' not in balance_info['coins']:
                return "تحقق من وجود رصيد USDT في الحساب"
            
            available_balance = balance_info['coins']['USDT']['equity']
            
            # حساب المبلغ المطلوب
            price = float(signal_data.get('price', 0))
            trade_amount = user_data.get('trade_amount', 100.0)
            leverage = user_data.get('leverage', 10)
            
            if market_type == 'futures':
                required_amount = (trade_amount * leverage) / price
            else:
                required_amount = trade_amount / price
            
            # حساب الكمية المثلى
            if market_type == 'futures':
                optimal_qty = (available_balance * 0.9 * leverage) / price
            else:
                optimal_qty = (available_balance * 0.9) / price
            
            suggestions = []
            
            if optimal_qty > 0.001:  # إذا كانت الكمية المثلى أكبر من الحد الأدنى
                suggestions.append(f"جرب كمية أقل: {optimal_qty:.6f} {signal_data.get('symbol', '').split('USDT')[0]}")
            
            suggestions.append(f"أودع المزيد من USDT (متاح حالياً: {available_balance:.2f} USDT)")
            
            if leverage > 1:
                suggestions.append(f"قلل الرافعة المالية من {leverage}x إلى 1x")
            
            suggestions.append(f"قلل مبلغ التداول من {trade_amount} إلى {available_balance * 0.5:.0f}")
            
            return " | ".join(suggestions)
            
        except Exception as e:
            logger.error(f"خطأ في توليد الاقتراحات: {e}")
            return "تحقق من الرصيد والإعدادات"

    @staticmethod
    async def diagnose_balance_issue(user_id: int) -> Dict:
        """تشخيص مشكلة الرصيد للمستخدم"""
        try:
            from real_account_manager import real_account_manager
            
            real_account = real_account_manager.get_account(user_id)
            if not real_account:
                return {
                    'success': False,
                    'message': 'لا يوجد حساب حقيقي مفعل',
                    'solutions': [
                        'أضف مفاتيح API صحيحة',
                        'تأكد من تفعيل الحساب الحقيقي'
                    ]
                }
            
            # فحص الرصيد في جميع أنواع الحسابات
            diagnostics = {
                'spot_balance': None,
                'futures_balance': None,
                'unified_balance': None
            }
            
            for account_type in ['spot', 'futures', 'unified']:
                try:
                    balance_info = real_account.get_wallet_balance(account_type)
                    if balance_info:
                        diagnostics[f'{account_type}_balance'] = balance_info
                except Exception as e:
                    logger.warning(f"فشل جلب رصيد {account_type}: {e}")
            
            # تحليل النتائج
            analysis = {
                'has_usdt': False,
                'total_usdt': 0.0,
                'available_usdt': 0.0,
                'recommendations': []
            }
            
            for account_type, balance_info in diagnostics.items():
                if balance_info and 'coins' in balance_info and 'USDT' in balance_info['coins']:
                    usdt_info = balance_info['coins']['USDT']
                    analysis['has_usdt'] = True
                    analysis['total_usdt'] += usdt_info.get('equity', 0)
                    analysis['available_usdt'] += usdt_info.get('available', 0)
            
            if not analysis['has_usdt']:
                analysis['recommendations'].append('أودع USDT في الحساب')
            elif analysis['total_usdt'] < 10:
                analysis['recommendations'].append(f'الرصيد منخفض ({analysis["total_usdt"]:.2f} USDT) - أودع المزيد')
            elif analysis['available_usdt'] < 5:
                analysis['recommendations'].append(f'الرصيد المتاح منخفض ({analysis["available_usdt"]:.2f} USDT)')
            
            return {
                'success': True,
                'analysis': analysis,
                'diagnostics': diagnostics,
                'recommendations': analysis['recommendations']
            }
            
        except Exception as e:
            logger.error(f"خطأ في تشخيص مشكلة الرصيد: {e}")
            return {
                'success': False,
                'message': f'خطأ في التشخيص: {str(e)}',
                'solutions': ['تحقق من إعدادات الحساب', 'تأكد من صحة مفاتيح API']
            }


# مثيل عام للنظام الشامل
comprehensive_balance_fix = ComprehensiveBalanceFix()


async def test_comprehensive_fix():
    """اختبار النظام الشامل"""
    print("🧪 اختبار النظام الشامل لإصلاح مشكلة عدم كفاية الرصيد")
    
    test_user_id = 12345
    test_signal_data = {
        'action': 'buy',
        'symbol': 'BTCUSDT',
        'price': 111084.4,
        'signal_id': '4',
        'has_signal_id': True
    }
    
    test_user_data = {
        'account_type': 'real',
        'exchange': 'bybit',
        'market_type': 'futures',
        'trade_amount': 55.0,
        'leverage': 1
    }
    
    try:
        # اختبار التنفيذ الشامل
        result = await comprehensive_balance_fix.execute_signal_with_comprehensive_fix(
            test_user_id, test_signal_data, test_user_data
        )
        
        print(f"📊 نتيجة الاختبار الشامل: {result}")
        
        if result.get('success'):
            print("✅ الاختبار نجح!")
        else:
            print(f"❌ الاختبار فشل: {result.get('message')}")
            
            if result.get('suggestion'):
                print(f"💡 الاقتراح: {result.get('suggestion')}")
            
            if result.get('suggestions'):
                print("🔧 الحلول المقترحة:")
                for suggestion in result.get('suggestions', []):
                    print(f"  • {suggestion}")
        
        # اختبار التشخيص
        print("\n🔍 اختبار التشخيص...")
        diagnosis = await comprehensive_balance_fix.diagnose_balance_issue(test_user_id)
        print(f"📋 نتيجة التشخيص: {diagnosis}")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_comprehensive_fix())
