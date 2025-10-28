#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مثال توضيحي للتحويل الذكي
"""

def demonstrate_conversion():
    """توضيح كيف يعمل التحويل الذكي"""
    
    print("=" * 80)
    print("مثال توضيحي للتحويل الذكي")
    print("=" * 80)
    
    print("\nمثال 1: Bitcoin (BTCUSDT)")
    print("-" * 40)
    
    amount_usd = 60.0  # المدخلات (طريقتك)
    btc_price = 110000  # السعر الحالي
    
    # التحويل الذكي
    btc_quantity = amount_usd / btc_price
    
    print(f"المدخلات (طريقتك):")
    print(f"   amount: {amount_usd} USD")
    print(f"   symbol: BTCUSDT")
    print(f"   action: buy")
    
    print(f"\nالمخرجات (طريقة المنصة):")
    print(f"   quantity: {btc_quantity:.6f} BTC")
    print(f"   side: BUY")
    print(f"   type: MARKET")
    
    print(f"\nالعملية الخفية:")
    print(f"   ${amount_usd} ÷ ${btc_price} = {btc_quantity:.6f} BTC")
    
    # مثال 2: ETH
    print("\nمثال 2: Ethereum (ETHUSDT)")
    print("-" * 40)
    
    amount_usd = 100.0  # المدخلات (طريقتك)
    eth_price = 4000    # السعر الحالي
    
    # التحويل الذكي
    eth_quantity = amount_usd / eth_price
    
    print(f"المدخلات (طريقتك):")
    print(f"   amount: {amount_usd} USD")
    print(f"   symbol: ETHUSDT")
    print(f"   action: buy")
    
    print(f"\nالمخرجات (طريقة المنصة):")
    print(f"   quantity: {eth_quantity:.6f} ETH")
    print(f"   side: BUY")
    print(f"   type: MARKET")
    
    print(f"\nالعملية الخفية:")
    print(f"   ${amount_usd} ÷ ${eth_price} = {eth_quantity:.6f} ETH")
    
    # مثال 3: Bybit مع الرافعة
    print("\nمثال 3: Bybit Futures مع الرافعة")
    print("-" * 40)
    
    amount_usd = 50.0   # المدخلات (طريقتك)
    btc_price = 110000  # السعر الحالي
    leverage = 10       # الرافعة
    
    # التحويل الذكي مع الرافعة
    btc_quantity_with_leverage = (amount_usd * leverage) / btc_price
    
    print(f"المدخلات (طريقتك):")
    print(f"   amount: {amount_usd} USD")
    print(f"   symbol: BTCUSDT")
    print(f"   action: buy")
    print(f"   leverage: {leverage}x")
    
    print(f"\nالمخرجات (طريقة المنصة):")
    print(f"   qty: {btc_quantity_with_leverage:.6f} BTC")
    print(f"   side: Buy")
    print(f"   category: linear")
    print(f"   leverage: {leverage}")
    
    print(f"\nالعملية الخفية:")
    print(f"   (${amount_usd} × {leverage}) ÷ ${btc_price} = {btc_quantity_with_leverage:.6f} BTC")
    
    print("\n" + "=" * 80)
    print("الخلاصة:")
    print("   - أنت تدخل المبلغ بالدولار (طريقتك)")
    print("   - النظام يحول تلقائياً إلى كمية العملة (طريقة المنصة)")
    print("   - كل شيء يحدث في الخلفية دون تدخل منك")
    print("=" * 80)

if __name__ == "__main__":
    demonstrate_conversion()
