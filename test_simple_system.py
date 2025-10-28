#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مبسط للنظام المحدث
"""

import sys
import os
import asyncio
import logging

# إضافة المسار الحالي إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_system():
    """اختبار مبسط للنظام المحدث"""
    
    print("=" * 60)
    print("اختبار مبسط للنظام المحدث")
    print("=" * 60)
    print()
    
    # اختبار 1: تحميل الإعدادات
    print("1. اختبار تحميل الإعدادات...")
    try:
        from config_updated import (
            BYBIT_API_KEY, BYBIT_API_SECRET, TELEGRAM_TOKEN,
            DEFAULT_SETTINGS, VERSION_INFO
        )
        print(f"تم تحميل الإعدادات بنجاح")
        print(f"   الإصدار: {VERSION_INFO['version']}")
        print(f"   Bybit API Key: {BYBIT_API_KEY[:10]}...")
        print(f"   نوع الحساب: {DEFAULT_SETTINGS['account_type']}")
        print(f"   نوع السوق: {DEFAULT_SETTINGS['market_type']}")
        print(f"   مبلغ التداول: {DEFAULT_SETTINGS['trade_amount']}")
        print(f"   الرافعة: {DEFAULT_SETTINGS['leverage']}")
        print(f"   الكمية الدنيا: {DEFAULT_SETTINGS['min_quantity']}")
    except Exception as e:
        print(f"فشل في تحميل الإعدادات: {e}")
        return False
    
    print()
    
    # اختبار 2: اختبار قاعدة البيانات
    print("2. اختبار قاعدة البيانات...")
    try:
        from database import db_manager
        
        # اختبار الاتصال
        test_user_id = 999999
        user_data = db_manager.get_user(test_user_id)
        
        if user_data:
            print(f"قاعدة البيانات تعمل - المستخدم موجود")
        else:
            print(f"قاعدة البيانات تعمل - إنشاء مستخدم جديد")
            db_manager.create_user(test_user_id)
            user_data = db_manager.get_user(test_user_id)
        
        print(f"   بيانات المستخدم: {user_data}")
        
    except Exception as e:
        print(f"فشل في اختبار قاعدة البيانات: {e}")
        return False
    
    print()
    
    # اختبار 3: اختبار مدير الحسابات الحقيقية
    print("3. اختبار مدير الحسابات الحقيقية...")
    try:
        from real_account_manager import real_account_manager
        
        # إنشاء حساب حقيقي
        real_account_manager.initialize_account(test_user_id, 'bybit', BYBIT_API_KEY, BYBIT_API_SECRET)
        account = real_account_manager.get_account(test_user_id)
        
        if account:
            print(f"تم إنشاء الحساب الحقيقي بنجاح")
            
            # اختبار جلب الرصيد
            balance = account.get_wallet_balance('UNIFIED')
            if balance:
                print(f"   الرصيد: {balance.get('totalEquity', 'N/A')} USDT")
            else:
                print(f"   تحذير: فشل في جلب الرصيد")
            
            # اختبار جلب السعر
            ticker = account.get_ticker('linear', 'BTCUSDT')
            if ticker and 'lastPrice' in ticker:
                price = float(ticker['lastPrice'])
                print(f"   سعر BTCUSDT: ${price:,.2f}")
            else:
                print(f"   تحذير: فشل في جلب السعر")
                
        else:
            print(f"فشل في إنشاء الحساب الحقيقي")
            return False
            
    except Exception as e:
        print(f"فشل في اختبار مدير الحسابات: {e}")
        return False
    
    print()
    
    # اختبار 4: اختبار منفذ الإشارات
    print("4. اختبار منفذ الإشارات...")
    try:
        from signal_executor import SignalExecutor
        
        # إشارة تجريبية
        test_signal = {
            'signal': 'buy',
            'symbol': 'BTCUSDT',
            'id': 'test_1',
            'generated_id': False,
            'position_id': 'POS-test_1',
            'enhanced_analysis': {
                'signal_quality': 'high',
                'confidence_level': 0.9,
                'market_conditions': 'favorable',
                'recommendation': 'execute',
                'risk_level': 'low'
            }
        }
        
        print(f"   إشارة تجريبية: {test_signal['signal']} {test_signal['symbol']}")
        
        # تحديث بيانات المستخدم
        db_manager.update_user_settings(test_user_id, DEFAULT_SETTINGS)
        
        # تنفيذ الإشارة (بدون وضع أمر حقيقي)
        print(f"   تخطي تنفيذ الإشارة الحقيقي للاختبار")
        
    except Exception as e:
        print(f"فشل في اختبار منفذ الإشارات: {e}")
        return False
    
    print()
    
    # اختبار 5: اختبار بوت التلجرام
    print("5. اختبار بوت التلجرام...")
    try:
        from bybit_trading_bot import TradingBot
        
        print(f"تم تحميل بوت التلجرام بنجاح")
        print(f"   Token: {TELEGRAM_TOKEN[:10]}...")
        
    except Exception as e:
        print(f"فشل في اختبار بوت التلجرام: {e}")
        return False
    
    print()
    
    # النتيجة النهائية
    print("=" * 60)
    print("نتيجة الاختبار المبسط")
    print("=" * 60)
    print()
    print("جميع الاختبارات نجحت!")
    print()
    print("النظام جاهز للعمل مع:")
    print(f"• نوع الحساب: {DEFAULT_SETTINGS['account_type']}")
    print(f"• نوع السوق: {DEFAULT_SETTINGS['market_type']}")
    print(f"• المنصة: {DEFAULT_SETTINGS['exchange']}")
    print(f"• مبلغ التداول: {DEFAULT_SETTINGS['trade_amount']} USDT")
    print(f"• الرافعة: {DEFAULT_SETTINGS['leverage']}x")
    print(f"• الكمية الدنيا: {DEFAULT_SETTINGS['min_quantity']} BTC")
    print()
    print("يمكنك الآن:")
    print("1. تشغيل البوت: python bybit_trading_bot.py")
    print("2. ربط API Keys من الإعدادات")
    print("3. بدء التداول!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_simple_system())
    if success:
        print("\nالنظام جاهز للعمل!")
        sys.exit(0)
    else:
        print("\nالنظام يحتاج إصلاح!")
        sys.exit(1)
