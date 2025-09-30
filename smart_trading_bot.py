#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت ذكي للتداول - Smart Trading Bot
يوفر واجهة ذكية للتداول على منصة Bybit
"""

import logging
from typing import Dict, Any, Optional
from bybit_trading_bot import TradingAccount

logger = logging.getLogger(__name__)

class SmartTradingBot:
    """البوت الذكي للتداول مع دعم متعدد المستخدمين"""

    def __init__(self):
        self.accounts: Dict[int, TradingAccount] = {}
        self.user_settings: Dict[int, Dict[str, Any]] = {}

    def get_user_account(self, user_id: int) -> TradingAccount:
        """الحصول على حساب المستخدم أو إنشاء حساب جديد"""
        if user_id not in self.accounts:
            # إنشاء حساب تجريبي افتراضي
            self.accounts[user_id] = TradingAccount(initial_balance=10000.0)

            # إعدادات افتراضية للمستخدم
            self.user_settings[user_id] = {
                'trade_amount': 100.0,
                'market_type': 'spot',
                'leverage': 1,
                'is_active': True
            }

        return self.accounts[user_id]

    def get_current_account(self, user_id: int = None) -> TradingAccount:
        """الحصول على الحساب الحالي للمستخدم"""
        if user_id is None:
            # إرجاع الحساب الأول كافتراضي إذا لم يحدد المستخدم
            if self.accounts:
                return list(self.accounts.values())[0]
            else:
                # إنشاء حساب افتراضي
                return TradingAccount(initial_balance=10000.0)

        return self.get_user_account(user_id)

    def get_account_info(self, user_id: int = None) -> Dict[str, Any]:
        """الحصول على معلومات الحساب"""
        account = self.get_current_account(user_id)

        return {
            'balance': account.balance,
            'available_balance': account.get_available_balance(),
            'margin_locked': account.margin_locked,
            'total_trades': account.total_trades,
            'winning_trades': account.winning_trades,
            'losing_trades': account.losing_trades,
            'open_positions': len(account.positions),
            'account_type': account.account_type
        }

    def update_user_settings(self, user_id: int, settings: Dict[str, Any]):
        """تحديث إعدادات المستخدم"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}

        self.user_settings[user_id].update(settings)

    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم"""
        return self.user_settings.get(user_id, {
            'trade_amount': 100.0,
            'market_type': 'spot',
            'leverage': 1,
            'is_active': True
        })

    def process_signal(self, signal_data: Dict[str, Any], user_id: int = None) -> bool:
        """معالجة إشارة تداول"""
        try:
            account = self.get_current_account(user_id)
            symbol = signal_data.get('symbol')
            action = signal_data.get('action')

            if not symbol or not action:
                logger.error("بيانات الإشارة غير مكتملة")
                return False

            # استخدام الإعدادات الافتراضية للتداول
            settings = self.get_user_settings(user_id)
            trade_amount = settings.get('trade_amount', 100.0)

            if action.lower() == 'buy':
                # تنفيذ أمر شراء
                success, message = account.open_spot_position(
                    symbol=symbol,
                    side='buy',
                    amount=trade_amount,
                    price=0.0  # سيتم تحديث السعر لاحقاً
                )
                return success
            elif action.lower() == 'sell':
                # تنفيذ أمر بيع
                success, message = account.open_spot_position(
                    symbol=symbol,
                    side='sell',
                    amount=trade_amount,
                    price=0.0  # سيتم تحديث السعر لاحقاً
                )
                return success
            else:
                logger.error(f"نوع العملية غير مدعوم: {action}")
                return False

        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            return False

# إنشاء مثيل عام للبوت الذكي
smart_trading_bot = SmartTradingBot()
