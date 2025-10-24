"""
Simple test for button handlers
"""

print("="*60)
print("Testing button handlers")
print("="*60)

try:
    # Test import
    import bybit_trading_bot
    print("SUCCESS: bybit_trading_bot imported")
    
    # Check main functions
    functions = [
        'handle_callback',
        'handle_text_input',
        'start',
        'settings_menu',
        'portfolio_handler',
        'open_positions'
    ]
    
    print("\nChecking functions:")
    for func in functions:
        exists = hasattr(bybit_trading_bot, func)
        status = "OK" if exists else "MISSING"
        print(f"  {func}: {status}")
    
    # Check main function
    has_main = hasattr(bybit_trading_bot, 'main')
    print(f"\nmain function: {'OK' if has_main else 'MISSING'}")
    
    print("\n" + "="*60)
    print("Test completed successfully")
    print("="*60)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

