#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الحسابات المحسن
يدعم الحسابات التجريبية والحقيقية مع Spot/Futures
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class AccountType(Enum):
    """أنواع الحسابات"""
    DEMO = "demo"
    REAL = "real"

class MarketType(Enum):
    """أنواع الأسواق"""
    SPOT = "spot"
    FUTURES = "futures"

class ExchangeType(Enum):
    """أنواع المنصات"""
    BYBIT = "bybit"
    MEXC = "mexc"

@dataclass
class AccountBalance:
    """هيكل بيانات رصيد الحساب"""
    account_type: str
    market_type: str
    exchange: str
    total_balance: float
    available_balance: float
    used_margin: float
    unrealized_pnl: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Trade:
    """هيكل بيانات الصفقة"""
    trade_id: str
    signal_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    amount: float
    account_type: str
    market_type: str
    exchange: str
    status: str  # 'pending', 'filled', 'cancelled', 'partial'
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class EnhancedAccountManager:
    """مدير الحسابات المحسن"""
    
    def __init__(self):
        self.accounts: Dict[str, AccountBalance] = {}  # account_key -> AccountBalance
        self.trades: Dict[str, Trade] = {}  # trade_id -> Trade
        self.user_accounts: Dict[int, Dict[str, str]] = {}  # user_id -> {account_type: account_key}
        self.lock = threading.Lock()
        
        # إعدادات الحسابات التجريبية
        self.demo_initial_balances = {
            'spot': {
                'bybit': 10000.0,
                'mexc': 10000.0
            },
            'futures': {
                'bybit': 10000.0,
                'mexc': 0.0  # MEXC لا يدعم الفيوتشر
            }
        }
        
        logger.info("🚀 تم تهيئة مدير الحسابات المحسن")
    
    def create_user_accounts(self, user_id: int) -> Dict[str, Any]:
        """
        إنشاء حسابات المستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            نتيجة إنشاء الحسابات
        """
        try:
            with self.lock:
                if user_id in self.user_accounts:
                    return {
                        'success': True,
                        'message': 'الحسابات موجودة بالفعل',
                        'accounts': self.user_accounts[user_id]
                    }
                
                # إنشاء حسابات تجريبية
                demo_accounts = {}
                for market_type in ['spot', 'futures']:
                    for exchange in ['bybit', 'mexc']:
                        if market_type == 'futures' and exchange == 'mexc':
                            continue  # MEXC لا يدعم الفيوتشر
                        
                        account_key = f"DEMO_{user_id}_{market_type}_{exchange}"
                        
                        # إنشاء رصيد الحساب التجريبي
                        initial_balance = self.demo_initial_balances[market_type][exchange]
                        account_balance = AccountBalance(
                            account_type='demo',
                            market_type=market_type,
                            exchange=exchange,
                            total_balance=initial_balance,
                            available_balance=initial_balance,
                            used_margin=0.0,
                            unrealized_pnl=0.0
                        )
                        
                        self.accounts[account_key] = account_balance
                        demo_accounts[f"demo_{market_type}_{exchange}"] = account_key
                
                # حفظ حسابات المستخدم
                self.user_accounts[user_id] = demo_accounts
                
                logger.info(f"✅ تم إنشاء حسابات المستخدم {user_id}: {demo_accounts}")
                
                return {
                    'success': True,
                    'message': 'تم إنشاء الحسابات بنجاح',
                    'accounts': demo_accounts
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء حسابات المستخدم: {e}")
            return {
                'success': False,
                'message': f'خطأ في إنشاء الحسابات: {str(e)}',
                'error': 'ACCOUNT_CREATION_ERROR'
            }
    
    def get_account_balance(self, user_id: int, account_type: str, market_type: str, exchange: str) -> Dict[str, Any]:
        """
        الحصول على رصيد الحساب
        
        Args:
            user_id: معرف المستخدم
            account_type: نوع الحساب (demo/real)
            market_type: نوع السوق (spot/futures)
            exchange: المنصة (bybit/mexc)
            
        Returns:
            رصيد الحساب
        """
        try:
            with self.lock:
                # البحث عن الحساب
                account_key = self._get_account_key(user_id, account_type, market_type, exchange)
                
                if not account_key or account_key not in self.accounts:
                    return {
                        'success': False,
                        'message': f'الحساب غير موجود: {account_type}_{market_type}_{exchange}',
                        'error': 'ACCOUNT_NOT_FOUND'
                    }
                
                account = self.accounts[account_key]
                
                return {
                    'success': True,
                    'balance': {
                        'total_balance': account.total_balance,
                        'available_balance': account.available_balance,
                        'used_margin': account.used_margin,
                        'unrealized_pnl': account.unrealized_pnl,
                        'account_type': account.account_type,
                        'market_type': account.market_type,
                        'exchange': account.exchange,
                        'last_updated': account.last_updated.isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على رصيد الحساب: {e}")
            return {
                'success': False,
                'message': f'خطأ في الحصول على رصيد الحساب: {str(e)}',
                'error': 'BALANCE_ERROR'
            }
    
    def execute_trade(self, user_id: int, signal_data: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ صفقة
        
        Args:
            user_id: معرف المستخدم
            signal_data: بيانات الإشارة
            user_settings: إعدادات المستخدم
            
        Returns:
            نتيجة تنفيذ الصفقة
        """
        try:
            with self.lock:
                account_type = user_settings.get('account_type', 'demo')
                market_type = user_settings.get('market_type', 'spot')
                exchange = user_settings.get('exchange', 'bybit')
                trade_amount = float(user_settings.get('trade_amount', 100.0))
                
                # البحث عن الحساب
                account_key = self._get_account_key(user_id, account_type, market_type, exchange)
                
                if not account_key or account_key not in self.accounts:
                    return {
                        'success': False,
                        'message': f'الحساب غير موجود: {account_type}_{market_type}_{exchange}',
                        'error': 'ACCOUNT_NOT_FOUND'
                    }
                
                account = self.accounts[account_key]
                
                # التحقق من الرصيد المتاح
                if account_type == 'demo':
                    # للحسابات التجريبية، نتحقق من الرصيد المتاح
                    if account.available_balance < trade_amount:
                        return {
                            'success': False,
                            'message': f'الرصيد غير كافي. المتاح: {account.available_balance}, المطلوب: {trade_amount}',
                            'error': 'INSUFFICIENT_BALANCE'
                        }
                else:
                    # للحسابات الحقيقية، نتحقق من API المنصة
                    # هنا سيتم استدعاء API المنصة الحقيقية
                    pass
                
                # إنشاء الصفقة
                trade_id = f"TRADE_{user_id}_{signal_data['id']}_{int(time.time())}"
                
                trade = Trade(
                    trade_id=trade_id,
                    signal_id=signal_data['id'],
                    symbol=signal_data['symbol'],
                    side=signal_data['signal'],
                    quantity=trade_amount,
                    price=0.0,  # سيتم تحديثه لاحقاً
                    amount=trade_amount,
                    account_type=account_type,
                    market_type=market_type,
                    exchange=exchange,
                    status='pending'
                )
                
                # حفظ الصفقة
                self.trades[trade_id] = trade
                
                # تحديث رصيد الحساب
                if account_type == 'demo':
                    account.available_balance -= trade_amount
                    account.used_margin += trade_amount
                    account.last_updated = datetime.now()
                
                # تنفيذ الصفقة حسب نوع الحساب
                if account_type == 'demo':
                    execution_result = self._execute_demo_trade(trade, account)
                else:
                    execution_result = self._execute_real_trade(trade, account)
                
                if execution_result['success']:
                    trade.status = 'filled'
                    trade.price = execution_result.get('price', 0.0)
                    trade.updated_at = datetime.now()
                    
                    logger.info(f"✅ تم تنفيذ الصفقة بنجاح: {trade_id}")
                    
                    return {
                        'success': True,
                        'message': 'تم تنفيذ الصفقة بنجاح',
                        'trade_id': trade_id,
                        'signal_id': signal_data['id'],
                        'execution_details': execution_result
                    }
                else:
                    trade.status = 'cancelled'
                    trade.updated_at = datetime.now()
                    
                    # إعادة الرصيد في حالة فشل التنفيذ
                    if account_type == 'demo':
                        account.available_balance += trade_amount
                        account.used_margin -= trade_amount
                    
                    return {
                        'success': False,
                        'message': f'فشل في تنفيذ الصفقة: {execution_result["message"]}',
                        'error': 'TRADE_EXECUTION_FAILED',
                        'trade_id': trade_id
                    }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة: {str(e)}',
                'error': 'TRADE_EXECUTION_ERROR'
            }
    
    def _execute_demo_trade(self, trade: Trade, account: AccountBalance) -> Dict[str, Any]:
        """تنفيذ صفقة تجريبية"""
        try:
            logger.info(f"🎮 تنفيذ صفقة تجريبية: {trade.trade_id}")
            
            # محاكاة التنفيذ التجريبي
            time.sleep(0.1)  # محاكاة تأخير
            
            # محاكاة السعر (سيتم جلبه من API حقيقي)
            mock_price = 50000.0 if trade.symbol == 'BTCUSDT' else 3000.0
            
            # محاكاة النتيجة
            return {
                'success': True,
                'message': 'تم تنفيذ الصفقة التجريبية بنجاح',
                'price': mock_price,
                'executed_at': datetime.now().isoformat(),
                'account_type': 'demo'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة التجريبية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة التجريبية: {str(e)}',
                'error': 'DEMO_EXECUTION_ERROR'
            }
    
    def _execute_real_trade(self, trade: Trade, account: AccountBalance) -> Dict[str, Any]:
        """تنفيذ صفقة حقيقية"""
        try:
            logger.info(f"🌐 تنفيذ صفقة حقيقية: {trade.trade_id}")
            
            # هنا سيتم استدعاء API المنصة الحقيقية
            # هذا مثال مبسط
            
            # محاكاة التنفيذ الحقيقي
            time.sleep(0.2)  # محاكاة تأخير أطول
            
            # محاكاة السعر (سيتم جلبه من API حقيقي)
            mock_price = 50000.0 if trade.symbol == 'BTCUSDT' else 3000.0
            
            # محاكاة النتيجة
            return {
                'success': True,
                'message': 'تم تنفيذ الصفقة الحقيقية بنجاح',
                'price': mock_price,
                'executed_at': datetime.now().isoformat(),
                'account_type': 'real'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة الحقيقية: {str(e)}',
                'error': 'REAL_EXECUTION_ERROR'
            }
    
    def _get_account_key(self, user_id: int, account_type: str, market_type: str, exchange: str) -> Optional[str]:
        """الحصول على مفتاح الحساب"""
        try:
            if user_id not in self.user_accounts:
                return None
            
            account_key_name = f"{account_type}_{market_type}_{exchange}"
            return self.user_accounts[user_id].get(account_key_name)
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على مفتاح الحساب: {e}")
            return None
    
    def get_user_trades(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """الحصول على صفقات المستخدم"""
        try:
            user_trades = []
            for trade in self.trades.values():
                if trade.signal_id.startswith(f"TV_{user_id}") or str(user_id) in trade.trade_id:
                    user_trades.append({
                        'trade_id': trade.trade_id,
                        'signal_id': trade.signal_id,
                        'symbol': trade.symbol,
                        'side': trade.side,
                        'quantity': trade.quantity,
                        'price': trade.price,
                        'amount': trade.amount,
                        'account_type': trade.account_type,
                        'market_type': trade.market_type,
                        'exchange': trade.exchange,
                        'status': trade.status,
                        'created_at': trade.created_at.isoformat(),
                        'updated_at': trade.updated_at.isoformat()
                    })
            
            # ترتيب حسب التاريخ (الأحدث أولاً)
            user_trades.sort(key=lambda x: x['created_at'], reverse=True)
            
            return user_trades[:limit] if limit > 0 else user_trades
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على صفقات المستخدم: {e}")
            return []
    
    def get_user_accounts_summary(self, user_id: int) -> Dict[str, Any]:
        """الحصول على ملخص حسابات المستخدم"""
        try:
            if user_id not in self.user_accounts:
                return {
                    'success': False,
                    'message': 'المستخدم ليس لديه حسابات',
                    'error': 'NO_ACCOUNTS'
                }
            
            accounts_summary = {}
            
            for account_name, account_key in self.user_accounts[user_id].items():
                if account_key in self.accounts:
                    account = self.accounts[account_key]
                    accounts_summary[account_name] = {
                        'total_balance': account.total_balance,
                        'available_balance': account.available_balance,
                        'used_margin': account.used_margin,
                        'unrealized_pnl': account.unrealized_pnl,
                        'account_type': account.account_type,
                        'market_type': account.market_type,
                        'exchange': account.exchange,
                        'last_updated': account.last_updated.isoformat()
                    }
            
            # إحصائيات الصفقات
            user_trades = self.get_user_trades(user_id)
            total_trades = len(user_trades)
            successful_trades = len([t for t in user_trades if t['status'] == 'filled'])
            
            return {
                'success': True,
                'user_id': user_id,
                'accounts': accounts_summary,
                'statistics': {
                    'total_trades': total_trades,
                    'successful_trades': successful_trades,
                    'success_rate': (successful_trades / total_trades * 100) if total_trades > 0 else 0
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على ملخص الحسابات: {e}")
            return {
                'success': False,
                'message': f'خطأ في الحصول على ملخص الحسابات: {str(e)}',
                'error': 'SUMMARY_ERROR'
            }
    
    def reset_demo_account(self, user_id: int, account_type: str, market_type: str, exchange: str) -> Dict[str, Any]:
        """إعادة تعيين الحساب التجريبي"""
        try:
            with self.lock:
                if account_type != 'demo':
                    return {
                        'success': False,
                        'message': 'يمكن إعادة تعيين الحسابات التجريبية فقط',
                        'error': 'INVALID_ACCOUNT_TYPE'
                    }
                
                account_key = self._get_account_key(user_id, account_type, market_type, exchange)
                
                if not account_key or account_key not in self.accounts:
                    return {
                        'success': False,
                        'message': 'الحساب غير موجود',
                        'error': 'ACCOUNT_NOT_FOUND'
                    }
                
                # إعادة تعيين الرصيد
                initial_balance = self.demo_initial_balances[market_type][exchange]
                account = self.accounts[account_key]
                account.total_balance = initial_balance
                account.available_balance = initial_balance
                account.used_margin = 0.0
                account.unrealized_pnl = 0.0
                account.last_updated = datetime.now()
                
                logger.info(f"✅ تم إعادة تعيين الحساب التجريبي: {account_key}")
                
                return {
                    'success': True,
                    'message': 'تم إعادة تعيين الحساب التجريبي بنجاح',
                    'new_balance': initial_balance
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في إعادة تعيين الحساب التجريبي: {e}")
            return {
                'success': False,
                'message': f'خطأ في إعادة تعيين الحساب التجريبي: {str(e)}',
                'error': 'RESET_ERROR'
            }


# مثيل عام لمدير الحسابات المحسن
enhanced_account_manager = EnhancedAccountManager()


# دوال مساعدة للاستخدام السريع
def create_user_accounts(user_id: int) -> Dict[str, Any]:
    """إنشاء حسابات المستخدم"""
    return enhanced_account_manager.create_user_accounts(user_id)


def get_account_balance(user_id: int, account_type: str, market_type: str, exchange: str) -> Dict[str, Any]:
    """الحصول على رصيد الحساب"""
    return enhanced_account_manager.get_account_balance(user_id, account_type, market_type, exchange)


def execute_trade(user_id: int, signal_data: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
    """تنفيذ صفقة"""
    return enhanced_account_manager.execute_trade(user_id, signal_data, user_settings)


def get_user_accounts_summary(user_id: int) -> Dict[str, Any]:
    """الحصول على ملخص حسابات المستخدم"""
    return enhanced_account_manager.get_user_accounts_summary(user_id)


def reset_demo_account(user_id: int, account_type: str, market_type: str, exchange: str) -> Dict[str, Any]:
    """إعادة تعيين الحساب التجريبي"""
    return enhanced_account_manager.reset_demo_account(user_id, account_type, market_type, exchange)


if __name__ == "__main__":
    # اختبار مدير الحسابات المحسن
    print("=" * 80)
    print("اختبار مدير الحسابات المحسن")
    print("=" * 80)
    
    # إنشاء حسابات مستخدم
    user_id = 12345
    create_result = create_user_accounts(user_id)
    print(f"✅ إنشاء الحسابات: {create_result}")
    
    # الحصول على رصيد الحساب
    balance_result = get_account_balance(user_id, 'demo', 'spot', 'bybit')
    print(f"💰 رصيد الحساب: {balance_result}")
    
    # تنفيذ صفقة
    signal_data = {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'}
    user_settings = {
        'account_type': 'demo',
        'market_type': 'spot',
        'exchange': 'bybit',
        'trade_amount': 100.0
    }
    
    trade_result = execute_trade(user_id, signal_data, user_settings)
    print(f"📈 نتيجة الصفقة: {trade_result}")
    
    # ملخص الحسابات
    summary = get_user_accounts_summary(user_id)
    print(f"📊 ملخص الحسابات: {summary}")
