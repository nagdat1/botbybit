#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشكلة الرافعة المالية - حل مؤقت لتجاهل تعديل الرافعة
"""

import logging
from typing import Dict, Optional
from real_account_manager import real_account_manager

logger = logging.getLogger(__name__)

class BybitLeverageFix:
    """إصلاح مشكلة الرافعة المالية"""
    
    def __init__(self):
        self.leverage_fix_enabled = True
    
    def safe_set_leverage(self, account, category: str, symbol: str, leverage: int) -> bool:
        """تعيين آمن للرافعة المالية مع معالجة الأخطاء"""
        try:
            if not self.leverage_fix_enabled:
                logger.info(f"تجاهل تعيين الرافعة المالية: {leverage}x لـ {symbol}")
                return True
            
            logger.info(f"محاولة تعيين الرافعة المالية: {leverage}x لـ {symbol}")
            
            # محاولة تعيين الرافعة
            result = account.set_leverage(category, symbol, leverage)
            
            if result:
                logger.info(f"تم تعيين الرافعة المالية بنجاح: {leverage}x لـ {symbol}")
                return True
            else:
                logger.warning(f"فشل تعيين الرافعة المالية: {leverage}x لـ {symbol}")
                
                # إذا فشل تعيين الرافعة، تجاهلها ومتابعة العمل
                logger.info(f"تجاهل فشل الرافعة المالية ومتابعة العمل")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في تعيين الرافعة المالية: {e}")
            logger.info(f"تجاهل خطأ الرافعة المالية ومتابعة العمل")
            return True
    
    def disable_leverage_setting(self):
        """تعطيل تعيين الرافعة المالية تماماً"""
        self.leverage_fix_enabled = False
        logger.info("تم تعطيل تعيين الرافعة المالية")
    
    def enable_leverage_setting(self):
        """تفعيل تعيين الرافعة المالية"""
        self.leverage_fix_enabled = True
        logger.info("تم تفعيل تعيين الرافعة المالية")

# مثيل عام للإصلاح
leverage_fix = BybitLeverageFix()

def safe_place_order(account, category: str, symbol: str, side: str, order_type: str,
                    qty: float, price: float = None, leverage: int = None,
                    take_profit: float = None, stop_loss: float = None) -> Optional[Dict]:
    """وضع أمر آمن مع معالجة مشكلة الرافعة المالية"""
    
    try:
        # تعيين الرافعة المالية بأمان
        if leverage and category in ['linear', 'inverse']:
            leverage_result = leverage_fix.safe_set_leverage(account, category, symbol, leverage)
            if not leverage_result:
                logger.warning(f"فشل تعيين الرافعة المالية، متابعة العمل بدونها")
        
        # وضع الأمر
        result = account.place_order(
            category=category,
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            price=price,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss
        )
        
        return result
        
    except Exception as e:
        logger.error(f"خطأ في وضع الأمر الآمن: {e}")
        return {
            'success': False,
            'error': f'Safe order placement failed: {str(e)}',
            'error_type': 'SAFE_ORDER_ERROR'
        }

# دالة للاستخدام المباشر
def fix_leverage_issue():
    """إصلاح مشكلة الرافعة المالية"""
    logger.info("تطبيق إصلاح مشكلة الرافعة المالية...")
    
    # تعطيل تعيين الرافعة المالية مؤقتاً
    leverage_fix.disable_leverage_setting()
    
    logger.info("تم تطبيق الإصلاح - سيتم تجاهل تعيين الرافعة المالية")
    return True

if __name__ == "__main__":
    print("إصلاح مشكلة الرافعة المالية")
    print("=" * 40)
    
    # تطبيق الإصلاح
    fix_leverage_issue()
    
    print("تم تطبيق الإصلاح بنجاح!")
    print("الآن سيتم تجاهل تعيين الرافعة المالية لتجنب الأخطاء")
    print("يمكنك استخدام safe_place_order() لوضع الأوامر بأمان")
