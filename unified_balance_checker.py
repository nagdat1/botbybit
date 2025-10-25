#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فحص الرصيد الموحد والبسيط
"""

import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class UnifiedBalanceChecker:
    """نظام فحص الرصيد الموحد والبسيط"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_balance_simple(self, account, trade_amount: float, price: float, 
                           leverage: int, market_type: str, exchange: str, symbol: str) -> Dict:
        """
        فحص الرصيد بطريقة بسيطة وموحدة
        
        Args:
            account: حساب التداول
            trade_amount: مبلغ التداول بالـ USDT
            price: السعر الحالي
            leverage: الرافعة المالية
            market_type: نوع السوق (spot/futures)
            exchange: المنصة (bybit/mexc)
            symbol: رمز التداول
            
        Returns:
            نتيجة فحص الرصيد
        """
        try:
            # حساب الكمية المطلوبة
            qty = trade_amount / price
            
            # حساب الهامش المطلوب
            if market_type == 'spot':
                required_margin = qty * price
            else:  # futures
                required_margin = (qty * price) / leverage
            
            # جلب الرصيد المتاح
            available_balance = self._get_available_balance(account, exchange, market_type)
            
            if available_balance is None:
                return {
                    'success': False,
                    'message': 'Failed to get balance information',
                    'error': 'BALANCE_FETCH_FAILED'
                }
            
            # فحص الرصيد
            if available_balance >= required_margin:
                return {
                    'success': True,
                    'message': 'Balance sufficient for order',
                    'available_balance': available_balance,
                    'required_balance': required_margin,
                    'quantity': qty
                }
            else:
                shortage = required_margin - available_balance
                return {
                    'success': False,
                    'message': f'Insufficient balance. Available: {available_balance:.2f} USDT, Required: {required_margin:.2f} USDT',
                    'error': 'INSUFFICIENT_BALANCE',
                    'available_balance': available_balance,
                    'required_balance': required_margin,
                    'shortage': shortage,
                    'suggestions': self._generate_suggestions(available_balance, required_margin, trade_amount, price, leverage, market_type)
                }
                
        except Exception as e:
            self.logger.error(f"Error in balance check: {e}")
            return {
                'success': False,
                'message': f'Balance check error: {str(e)}',
                'error': 'BALANCE_CHECK_ERROR'
            }
    
    def _get_available_balance(self, account, exchange: str, market_type: str) -> Optional[float]:
        """جلب الرصيد المتاح"""
        try:
            if exchange == 'bybit':
                balance_info = account.get_wallet_balance('futures' if market_type == 'futures' else 'spot')
                if balance_info and 'coins' in balance_info and 'USDT' in balance_info['coins']:
                    return float(balance_info['coins']['USDT']['equity'])
                else:
                    self.logger.error("No USDT balance found in Bybit response")
                    return None
            elif exchange == 'mexc':
                balance_info = account.get_account_balance()
                if balance_info and 'USDT' in balance_info:
                    return float(balance_info['USDT']['free'])
                else:
                    self.logger.error("No USDT balance found in MEXC response")
                    return None
            else:
                self.logger.error(f"Unsupported exchange: {exchange}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return None
    
    def _generate_suggestions(self, available_balance: float, required_balance: float, 
                            trade_amount: float, price: float, leverage: int, market_type: str) -> list:
        """إنشاء اقتراحات لحل مشكلة الرصيد"""
        suggestions = []
        shortage = required_balance - available_balance
        
        # اقتراح 1: تقليل مبلغ التداول
        if market_type == 'spot':
            max_affordable_amount = available_balance
        else:
            max_affordable_amount = available_balance * leverage
        
        suggestions.append(f"تقليل المبلغ إلى {max_affordable_amount:.2f} USDT")
        
        # اقتراح 2: زيادة الرافعة (للفيوتشر فقط)
        if market_type == 'futures' and leverage < 10:
            min_leverage_needed = int(required_balance / available_balance) + 1
            if min_leverage_needed <= 10:
                suggestions.append(f"زيادة الرافعة إلى {min_leverage_needed}x")
        
        # اقتراح 3: إضافة رصيد
        suggestions.append(f"إضافة {shortage:.2f} USDT للحساب")
        
        # اقتراح 4: انتظار انخفاض السعر
        if market_type == 'spot':
            affordable_price = available_balance / (trade_amount / price)
            suggestions.append(f"انتظار انخفاض السعر إلى {affordable_price:.2f} أو أقل")
        
        return suggestions

# مثيل عام للنظام الموحد
unified_balance_checker = UnifiedBalanceChecker()
