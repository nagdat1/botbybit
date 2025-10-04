#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أمثلة على استخدام نظام TP/SL المتقدم
"""

from order_manager import order_manager, PriceType

# ==============================
# مثال 1: صفقة بسيطة مع TP/SL واحد
# ==============================
def example_1_simple_tp_sl():
    """صفقة شراء BTC مع TP و SL بسيط"""
    
    # بيانات الصفقة
    order_id = "BTC_TRADE_001"
    user_id = 123456
    symbol = "BTCUSDT"
    side = "buy"
    entry_price = 50000.0
    quantity = 0.1
    
    # Take Profit: +5% من سعر الدخول، إغلاق 100%
    take_profits = [
        {
            'level': 1,
            'price_type': 'percentage',
            'value': 5.0,  # +5%
            'close_percentage': 100.0  # إغلاق كامل
        }
    ]
    
    # Stop Loss: -2% من سعر الدخول
    stop_loss = {
        'price_type': 'percentage',
        'value': 2.0,  # -2%
        'trailing': False
    }
    
    # إنشاء الصفقة المُدارة
    order = order_manager.create_managed_order(
        order_id=order_id,
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        quantity=quantity,
        take_profits=take_profits,
        stop_loss=stop_loss
    )
    
    if order:
        print(f"✅ تم إنشاء صفقة بسيطة:")
        print(f"   TP: {order.take_profit_levels[0].target_price:.2f} (+5%)")
        print(f"   SL: {order.stop_loss.target_price:.2f} (-2%)")
    
    return order


# ==============================
# مثال 2: صفقة مع Take Profit متعدد
# ==============================
def example_2_multiple_tp():
    """صفقة شراء BTC مع 3 مستويات TP"""
    
    order_id = "BTC_TRADE_002"
    user_id = 123456
    symbol = "BTCUSDT"
    side = "buy"
    entry_price = 50000.0
    quantity = 0.3
    
    # 3 مستويات Take Profit
    take_profits = [
        {
            'level': 1,
            'price_type': 'percentage',
            'value': 2.0,  # +2%
            'close_percentage': 33.33  # إغلاق 33%
        },
        {
            'level': 2,
            'price_type': 'percentage',
            'value': 5.0,  # +5%
            'close_percentage': 33.33  # إغلاق 33%
        },
        {
            'level': 3,
            'price_type': 'percentage',
            'value': 10.0,  # +10%
            'close_percentage': 33.34  # إغلاق الباقي
        }
    ]
    
    # Stop Loss
    stop_loss = {
        'price_type': 'percentage',
        'value': 2.0,
        'trailing': False
    }
    
    order = order_manager.create_managed_order(
        order_id=order_id,
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        quantity=quantity,
        take_profits=take_profits,
        stop_loss=stop_loss
    )
    
    if order:
        print(f"\n✅ تم إنشاء صفقة مع TP متعدد:")
        for tp in order.take_profit_levels:
            print(f"   TP{tp.level_number}: {tp.target_price:.2f} ({tp.close_percentage}%)")
        print(f"   SL: {order.stop_loss.target_price:.2f}")
    
    return order


# ==============================
# مثال 3: صفقة مع أسعار محددة
# ==============================
def example_3_fixed_prices():
    """صفقة شراء ETH مع أسعار محددة"""
    
    order_id = "ETH_TRADE_003"
    user_id = 123456
    symbol = "ETHUSDT"
    side = "buy"
    entry_price = 3000.0
    quantity = 1.0
    
    # Take Profits بأسعار محددة
    take_profits = [
        {
            'level': 1,
            'price_type': 'price',
            'value': 3150.0,  # سعر محدد
            'close_percentage': 50.0
        },
        {
            'level': 2,
            'price_type': 'price',
            'value': 3300.0,  # سعر محدد
            'close_percentage': 50.0
        }
    ]
    
    # Stop Loss بسعر محدد
    stop_loss = {
        'price_type': 'price',
        'value': 2910.0,  # سعر محدد
        'trailing': False
    }
    
    order = order_manager.create_managed_order(
        order_id=order_id,
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        quantity=quantity,
        take_profits=take_profits,
        stop_loss=stop_loss
    )
    
    if order:
        print(f"\n✅ تم إنشاء صفقة بأسعار محددة:")
        for tp in order.take_profit_levels:
            print(f"   TP{tp.level_number}: {tp.target_price:.2f}")
        print(f"   SL: {order.stop_loss.target_price:.2f}")
    
    return order


# ==============================
# مثال 4: محاكاة تحديثات الأسعار
# ==============================
def example_4_price_simulation():
    """محاكاة تحديثات الأسعار وتفعيل TP/SL"""
    
    # إنشاء صفقة
    order = example_1_simple_tp_sl()
    
    if not order:
        return
    
    print(f"\n📊 محاكاة تحديثات الأسعار:")
    print(f"   سعر الدخول: {order.entry_price:.2f}")
    
    # محاكاة أسعار مختلفة
    test_prices = [
        50500.0,  # +1%
        51000.0,  # +2%
        52000.0,  # +4%
        52500.0,  # +5% - سيتم تفعيل TP
        53000.0,  # +6%
    ]
    
    for price in test_prices:
        result = order.update_price(price)
        
        print(f"\n   السعر الحالي: {price:.2f}")
        print(f"   PnL: {order.unrealized_pnl:.2f}")
        
        if result.get('triggered'):
            event_type = result['type']
            data = result['data']
            
            if event_type == 'TAKE_PROFIT':
                tp = data['take_profit']
                print(f"   🎯 تم تفعيل TP{tp.level_number}!")
                print(f"      الكمية المُغلقة: {data['close_quantity']}")
                print(f"      الربح: {data['pnl']:.2f}")
            
            elif event_type == 'STOP_LOSS':
                print(f"   ⚠️ تم تفعيل Stop Loss!")
                print(f"      الخسارة: {data['pnl']:.2f}")


# ==============================
# مثال 5: صفقة بيع (Short)
# ==============================
def example_5_short_trade():
    """صفقة بيع BTC"""
    
    order_id = "BTC_SHORT_001"
    user_id = 123456
    symbol = "BTCUSDT"
    side = "sell"  # بيع
    entry_price = 50000.0
    quantity = 0.1
    
    # Take Profit للبيع: السعر ينخفض
    take_profits = [
        {
            'level': 1,
            'price_type': 'percentage',
            'value': 3.0,  # -3%
            'close_percentage': 50.0
        },
        {
            'level': 2,
            'price_type': 'percentage',
            'value': 6.0,  # -6%
            'close_percentage': 50.0
        }
    ]
    
    # Stop Loss للبيع: السعر يرتفع
    stop_loss = {
        'price_type': 'percentage',
        'value': 2.0,  # +2%
        'trailing': False
    }
    
    order = order_manager.create_managed_order(
        order_id=order_id,
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        quantity=quantity,
        take_profits=take_profits,
        stop_loss=stop_loss
    )
    
    if order:
        print(f"\n✅ تم إنشاء صفقة بيع:")
        for tp in order.take_profit_levels:
            print(f"   TP{tp.level_number}: {tp.target_price:.2f}")
        print(f"   SL: {order.stop_loss.target_price:.2f}")
    
    return order


# ==============================
# مثال 6: Futures مع رافعة مالية
# ==============================
def example_6_futures_leverage():
    """صفقة Futures مع رافعة مالية"""
    
    order_id = "BTC_FUTURES_001"
    user_id = 123456
    symbol = "BTCUSDT"
    side = "buy"
    entry_price = 50000.0
    margin_amount = 1000.0  # الهامش
    leverage = 10  # الرافعة 10x
    
    # حساب الكمية بناءً على الرافعة
    position_size = margin_amount * leverage
    quantity = position_size / entry_price
    
    # Take Profit متدرج
    take_profits = [
        {
            'level': 1,
            'price_type': 'percentage',
            'value': 2.0,  # +2%
            'close_percentage': 50.0
        },
        {
            'level': 2,
            'price_type': 'percentage',
            'value': 4.0,  # +4%
            'close_percentage': 50.0
        }
    ]
    
    # Stop Loss محكم في Futures
    stop_loss = {
        'price_type': 'percentage',
        'value': 5.0,  # -5%
        'trailing': False
    }
    
    order = order_manager.create_managed_order(
        order_id=order_id,
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        quantity=quantity,
        market_type='futures',
        leverage=leverage,
        take_profits=take_profits,
        stop_loss=stop_loss
    )
    
    if order:
        print(f"\n✅ تم إنشاء صفقة Futures:")
        print(f"   الهامش: {margin_amount:.2f}")
        print(f"   الرافعة: {leverage}x")
        print(f"   حجم الصفقة: {position_size:.2f}")
        print(f"   الكمية: {quantity:.6f}")
        for tp in order.take_profit_levels:
            print(f"   TP{tp.level_number}: {tp.target_price:.2f} ({tp.close_percentage}%)")
        print(f"   SL: {order.stop_loss.target_price:.2f}")
    
    return order


# ==============================
# التشغيل
# ==============================
if __name__ == "__main__":
    print("=" * 50)
    print("أمثلة على نظام TP/SL المتقدم")
    print("=" * 50)
    
    # تشغيل الأمثلة
    example_1_simple_tp_sl()
    example_2_multiple_tp()
    example_3_fixed_prices()
    example_4_price_simulation()
    example_5_short_trade()
    example_6_futures_leverage()
    
    print("\n" + "=" * 50)
    print("✅ انتهت الأمثلة")
    print("=" * 50)

