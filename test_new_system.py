#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار النظام الجديد للسبوت والفيوتشر
"""

def test_spot_portfolio_logic():
    """اختبار منطق محفظة السبوت"""
    print("=" * 60)
    print("اختبار منطق محفظة السبوت")
    print("=" * 60)
    
    try:
        from enhanced_portfolio_manager import portfolio_factory
        
        # إنشاء مدير محفظة للمستخدم
        user_id = 12345
        portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
        
        print(f"تم إنشاء مدير محفظة للمستخدم {user_id}")
        
        # اختبار إضافة صفقة سبوت
        spot_position = {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'quantity': 0.1,
            'entry_price': 50000,
            'market_type': 'spot',
            'signal_id': 'SPOT_TEST_001',
            'exchange': 'bybit'
        }
        
        result = portfolio_manager.add_position(spot_position)
        print(f"إضافة صفقة سبوت: {'نجح' if result else 'فشل'}")
        
        # اختبار إضافة كمية أخرى لنفس الرمز (تعزيز)
        spot_position_2 = {
            'symbol': 'BTCUSDT',
            'side': 'buy',
            'quantity': 0.05,
            'entry_price': 51000,
            'market_type': 'spot',
            'signal_id': 'SPOT_TEST_001',
            'exchange': 'bybit'
        }
        
        result2 = portfolio_manager.add_position(spot_position_2)
        print(f"تعزيز صفقة سبوت: {'نجح' if result2 else 'فشل'}")
        
        # عرض المحفظة
        portfolio = portfolio_manager.get_user_portfolio()
        print(f"عدد الصفقات المفتوحة: {len(portfolio.get('open_positions', []))}")
        
    except Exception as e:
        print(f"خطأ في اختبار السبوت: {e}")

def test_futures_aggregation_logic():
    """اختبار منطق تجميع الفيوتشر"""
    print("\n" + "=" * 60)
    print("اختبار منطق تجميع الفيوتشر")
    print("=" * 60)
    
    try:
        from enhanced_portfolio_manager import portfolio_factory
        
        # إنشاء مدير محفظة للمستخدم
        user_id = 12345
        portfolio_manager = portfolio_factory.get_portfolio_manager(user_id)
        
        # اختبار إضافة صفقة فيوتشر
        futures_position = {
            'symbol': 'ETHUSDT',
            'side': 'buy',
            'quantity': 1.0,
            'entry_price': 3000,
            'market_type': 'futures',
            'signal_id': 'FUTURES_TEST_001',
            'exchange': 'bybit'
        }
        
        result = portfolio_manager.add_position(futures_position)
        print(f"إضافة صفقة فيوتشر: {'نجح' if result else 'فشل'}")
        
        # اختبار تعزيز نفس الـ ID
        futures_position_2 = {
            'symbol': 'ETHUSDT',
            'side': 'buy',
            'quantity': 0.5,
            'entry_price': 3100,
            'market_type': 'futures',
            'signal_id': 'FUTURES_TEST_001',
            'exchange': 'bybit'
        }
        
        result2 = portfolio_manager.add_position(futures_position_2)
        print(f"تعزيز صفقة فيوتشر: {'نجح' if result2 else 'فشل'}")
        
        # اختبار صفقة جديدة بدون ID (يجب إنشاء ID عشوائي)
        futures_position_3 = {
            'symbol': 'ETHUSDT',
            'side': 'sell',
            'quantity': 0.8,
            'entry_price': 3200,
            'market_type': 'futures',
            'exchange': 'bybit'
            # بدون signal_id - يجب إنشاء ID عشوائي
        }
        
        result3 = portfolio_manager.add_position(futures_position_3)
        print(f"صفقة جديدة بدون ID: {'نجح' if result3 else 'فشل'}")
        
        # عرض المحفظة
        portfolio = portfolio_manager.get_user_portfolio()
        print(f"عدد الصفقات المفتوحة: {len(portfolio.get('open_positions', []))}")
        
    except Exception as e:
        print(f"خطأ في اختبار الفيوتشر: {e}")

def test_id_generation():
    """اختبار إنشاء الـ ID العشوائي"""
    print("\n" + "=" * 60)
    print("اختبار إنشاء الـ ID العشوائي")
    print("=" * 60)
    
    try:
        from enhanced_portfolio_manager import EnhancedPortfolioManager
        
        # إنشاء مثيل للاختبار
        manager = EnhancedPortfolioManager(12345)
        
        # اختبار إنشاء ID
        id1 = manager._generate_random_id('BTCUSDT')
        id2 = manager._generate_random_id('ETHUSDT')
        
        print(f"ID 1: {id1}")
        print(f"ID 2: {id2}")
        print(f"الـ IDs مختلفة: {'نعم' if id1 != id2 else 'لا'}")
        
        # التحقق من صيغة الـ ID
        import re
        pattern = r'^[A-Z]+-\d{8}-\d{6}-[A-Z0-9]{4}$'
        
        valid1 = bool(re.match(pattern, id1))
        valid2 = bool(re.match(pattern, id2))
        
        print(f"صيغة ID 1 صحيحة: {'نعم' if valid1 else 'لا'}")
        print(f"صيغة ID 2 صحيحة: {'نعم' if valid2 else 'لا'}")
        
    except Exception as e:
        print(f"خطأ في اختبار الـ ID: {e}")

def test_system():
    """اختبار النظام الكامل"""
    print("بدء اختبار النظام الجديد")
    print("=" * 80)
    
    # اختبار منطق السبوت
    test_spot_portfolio_logic()
    
    # اختبار منطق الفيوتشر
    test_futures_aggregation_logic()
    
    # اختبار إنشاء الـ ID
    test_id_generation()
    
    print("\n" + "=" * 80)
    print("انتهى اختبار النظام الجديد")
    print("=" * 80)

if __name__ == "__main__":
    test_system()
