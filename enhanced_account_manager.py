#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الحسابات المحسن - Enhanced Account Manager
يدعم حسابات Demo/Real وأسواق Spot/Futures مع نظام ID
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class EnhancedAccountManager:
    """مدير الحسابات المحسن مع دعم نظام ID"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # قاعدة بيانات الحسابات
        self.accounts: Dict[str, Dict[str, Any]] = {}
        
        # قاعدة بيانات الصفقات
        self.positions: Dict[str, Dict[str, Any]] = {}
        
        # ربط الصفقات بالإشارات
        self.position_signal_map: Dict[str, str] = {}  # position_id -> signal_id
        
        self.logger.info("💼 تم تهيئة مدير الحسابات المحسن")
    
    def create_account(self, user_id: int, account_type: str, market_type: str, 
                      exchange: str = 'bybit') -> Dict[str, Any]:
        """إنشاء حساب جديد"""
        try:
            account_id = f"{user_id}_{account_type}_{market_type}_{exchange}"
            
            if account_id in self.accounts:
                return {
                    'success': True,
                    'message': 'الحساب موجود بالفعل',
                    'account_id': account_id
                }
            
            # إنشاء الحساب
            account = {
                'account_id': account_id,
                'user_id': user_id,
                'account_type': account_type,  # demo أو real
                'market_type': market_type,    # spot أو futures
                'exchange': exchange,          # bybit أو mexc
                'balance': 10000.0 if account_type == 'demo' else 0.0,
                'available_balance': 10000.0 if account_type == 'demo' else 0.0,
                'margin_locked': 0.0,
                'positions': {},
                'trade_history': [],
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            
            self.accounts[account_id] = account
            
            self.logger.info(f"✅ تم إنشاء حساب: {account_id}")
            
            return {
                'success': True,
                'message': 'تم إنشاء الحساب بنجاح',
                'account_id': account_id,
                'account': account
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إنشاء الحساب: {e}")
            return {
                'success': False,
                'message': f'خطأ في إنشاء الحساب: {str(e)}',
                'error': str(e)
            }
    
    def get_account(self, user_id: int, account_type: str, market_type: str, 
                   exchange: str = 'bybit') -> Optional[Dict[str, Any]]:
        """الحصول على حساب"""
        account_id = f"{user_id}_{account_type}_{market_type}_{exchange}"
        return self.accounts.get(account_id)
    
    def open_position(self, user_id: int, signal_data: Dict[str, Any], 
                     account_type: str, market_type: str, exchange: str = 'bybit') -> Dict[str, Any]:
        """فتح صفقة جديدة مع ربط بـ signal_id"""
        try:
            # الحصول على الحساب
            account = self.get_account(user_id, account_type, market_type, exchange)
            
            if not account:
                # إنشاء الحساب إذا لم يكن موجوداً
                create_result = self.create_account(user_id, account_type, market_type, exchange)
                if not create_result['success']:
                    return create_result
                account = create_result['account']
            
            # استخراج بيانات الإشارة
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '').upper()
            signal_id = signal_data.get('id')
            
            if not signal_type or not symbol:
                return {
                    'success': False,
                    'message': 'بيانات الإشارة غير مكتملة',
                    'error': 'incomplete_signal_data'
                }
            
            # إنشاء ID الصفقة
            if signal_id:
                position_id = signal_id  # استخدام ID الإشارة كمعرف للصفقة
                self.logger.info(f"🆔 استخدام ID الإشارة كمعرف للصفقة: {position_id}")
            else:
                position_id = f"{symbol}_{signal_type}_{int(time.time() * 1000000)}"
                self.logger.info(f"🎲 توليد ID عشوائي للصفقة: {position_id}")
            
            # إنشاء الصفقة
            position = {
                'position_id': position_id,
                'signal_id': signal_id,
                'user_id': user_id,
                'account_id': account['account_id'],
                'symbol': symbol,
                'signal_type': signal_type,
                'side': 'buy' if signal_type in ['buy', 'long'] else 'sell',
                'market_type': market_type,
                'exchange': exchange,
                'account_type': account_type,
                'entry_price': 0.0,  # سيتم تحديثه عند التنفيذ
                'quantity': 0.0,     # سيتم تحديثه عند التنفيذ
                'margin_amount': 0.0, # سيتم تحديثه عند التنفيذ
                'leverage': 1,       # سيتم تحديثه عند التنفيذ
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # حفظ الصفقة
            self.positions[position_id] = position
            
            # ربط الصفقة بالحساب
            account['positions'][position_id] = position
            
            # ربط الصفقة بالإشارة إذا كان هناك signal_id
            if signal_id:
                self.position_signal_map[position_id] = signal_id
            
            # تحديث نشاط الحساب
            account['last_activity'] = datetime.now().isoformat()
            
            self.logger.info(f"✅ تم فتح صفقة: {position_id} للمستخدم {user_id}")
            
            return {
                'success': True,
                'message': 'تم فتح الصفقة بنجاح',
                'position_id': position_id,
                'signal_id': signal_id,
                'position': position
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في فتح الصفقة: {e}")
            return {
                'success': False,
                'message': f'خطأ في فتح الصفقة: {str(e)}',
                'error': str(e)
            }
    
    def update_position(self, position_id: str, updates: Dict[str, Any]) -> bool:
        """تحديث بيانات الصفقة"""
        try:
            if position_id not in self.positions:
                self.logger.warning(f"⚠️ الصفقة غير موجودة: {position_id}")
                return False
            
            # تحديث البيانات
            self.positions[position_id].update(updates)
            self.positions[position_id]['updated_at'] = datetime.now().isoformat()
            
            # تحديث في الحساب أيضاً
            position = self.positions[position_id]
            account_id = position['account_id']
            
            if account_id in self.accounts:
                self.accounts[account_id]['positions'][position_id] = position
                self.accounts[account_id]['last_activity'] = datetime.now().isoformat()
            
            self.logger.info(f"✅ تم تحديث الصفقة: {position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث الصفقة: {e}")
            return False
    
    def close_position(self, position_id: str, closing_price: float) -> Dict[str, Any]:
        """إغلاق صفقة"""
        try:
            if position_id not in self.positions:
                return {
                    'success': False,
                    'message': 'الصفقة غير موجودة',
                    'error': 'position_not_found'
                }
            
            position = self.positions[position_id]
            
            # حساب PnL
            entry_price = position.get('entry_price', 0)
            quantity = position.get('quantity', 0)
            side = position.get('side', 'buy')
            
            if side == 'buy':
                pnl = (closing_price - entry_price) * quantity
            else:
                pnl = (entry_price - closing_price) * quantity
            
            # تحديث الصفقة
            self.update_position(position_id, {
                'status': 'closed',
                'closing_price': closing_price,
                'pnl': pnl,
                'closed_at': datetime.now().isoformat()
            })
            
            # تحديث الحساب
            account_id = position['account_id']
            if account_id in self.accounts:
                account = self.accounts[account_id]
                
                # تحديث الرصيد
                if position['account_type'] == 'demo':
                    account['balance'] += pnl
                    account['available_balance'] += pnl
                
                # إضافة للتاريخ
                trade_record = {
                    'position_id': position_id,
                    'signal_id': position.get('signal_id'),
                    'symbol': position['symbol'],
                    'side': position['side'],
                    'entry_price': entry_price,
                    'closing_price': closing_price,
                    'quantity': quantity,
                    'pnl': pnl,
                    'closed_at': datetime.now().isoformat()
                }
                
                account['trade_history'].append(trade_record)
            
            self.logger.info(f"✅ تم إغلاق الصفقة: {position_id} مع PnL: {pnl:.2f}")
            
            return {
                'success': True,
                'message': 'تم إغلاق الصفقة بنجاح',
                'position_id': position_id,
                'pnl': pnl,
                'closing_price': closing_price
            }
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إغلاق الصفقة: {e}")
            return {
                'success': False,
                'message': f'خطأ في إغلاق الصفقة: {str(e)}',
                'error': str(e)
            }
    
    def get_positions_by_signal_id(self, signal_id: str) -> List[Dict[str, Any]]:
        """الحصول على الصفقات المرتبطة بإشارة"""
        positions = []
        for position_id, position in self.positions.items():
            if position.get('signal_id') == signal_id:
                positions.append(position)
        return positions
    
    def get_position_by_id(self, position_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على صفقة بواسطة ID"""
        return self.positions.get(position_id)
    
    def get_user_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """الحصول على حسابات المستخدم"""
        accounts = []
        for account in self.accounts.values():
            if account['user_id'] == user_id:
                accounts.append(account)
        return accounts
    
    def get_account_statistics(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إحصائيات الحساب"""
        accounts = self.get_user_accounts(user_id)
        
        total_balance = sum(account['balance'] for account in accounts)
        total_positions = sum(len(account['positions']) for account in accounts)
        
        # إحصائيات الصفقات
        all_trades = []
        for account in accounts:
            all_trades.extend(account['trade_history'])
        
        total_pnl = sum(trade['pnl'] for trade in all_trades)
        winning_trades = len([trade for trade in all_trades if trade['pnl'] > 0])
        losing_trades = len([trade for trade in all_trades if trade['pnl'] < 0])
        
        return {
            'user_id': user_id,
            'total_accounts': len(accounts),
            'total_balance': total_balance,
            'total_positions': total_positions,
            'total_trades': len(all_trades),
            'total_pnl': total_pnl,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / len(all_trades) * 100) if all_trades else 0
        }


# مثيل عام لمدير الحسابات المحسن
enhanced_account_manager = EnhancedAccountManager()


# دوال مساعدة للاستخدام السريع
def create_account(user_id: int, account_type: str, market_type: str, exchange: str = 'bybit') -> Dict[str, Any]:
    """إنشاء حساب"""
    return enhanced_account_manager.create_account(user_id, account_type, market_type, exchange)


def open_position(user_id: int, signal_data: Dict[str, Any], account_type: str, 
                 market_type: str, exchange: str = 'bybit') -> Dict[str, Any]:
    """فتح صفقة"""
    return enhanced_account_manager.open_position(user_id, signal_data, account_type, market_type, exchange)


def get_positions_by_signal_id(signal_id: str) -> List[Dict[str, Any]]:
    """الحصول على الصفقات المرتبطة بإشارة"""
    return enhanced_account_manager.get_positions_by_signal_id(signal_id)


if __name__ == "__main__":
    # اختبار مدير الحسابات المحسن
    print("=" * 80)
    print("اختبار مدير الحسابات المحسن")
    print("=" * 80)
    
    # اختبار إنشاء حساب
    account_result = create_account(12345, 'demo', 'futures', 'bybit')
    print(f"\n🧪 اختبار إنشاء حساب: {account_result['success']}")
    if account_result['success']:
        print(f"   ID الحساب: {account_result['account_id']}")
    
    # اختبار فتح صفقة مع ID
    signal_data = {
        'signal': 'buy',
        'symbol': 'BTCUSDT',
        'id': 'TV_B01'
    }
    
    position_result = open_position(12345, signal_data, 'demo', 'futures', 'bybit')
    print(f"\n🧪 اختبار فتح صفقة مع ID: {position_result['success']}")
    if position_result['success']:
        print(f"   ID الصفقة: {position_result['position_id']}")
        print(f"   ID الإشارة: {position_result['signal_id']}")
    
    # اختبار فتح صفقة بدون ID
    signal_data_no_id = {
        'signal': 'sell',
        'symbol': 'ETHUSDT'
    }
    
    position_result2 = open_position(12345, signal_data_no_id, 'demo', 'spot', 'bybit')
    print(f"\n🧪 اختبار فتح صفقة بدون ID: {position_result2['success']}")
    if position_result2['success']:
        print(f"   ID الصفقة: {position_result2['position_id']}")
        print(f"   ID الإشارة: {position_result2['signal_id']}")
    
    # اختبار الحصول على الصفقات المرتبطة بإشارة
    if position_result['success']:
        positions = get_positions_by_signal_id('TV_B01')
        print(f"\n🔗 الصفقات المرتبطة بـ TV_B01: {len(positions)}")
    
    # اختبار الإحصائيات
    stats = enhanced_account_manager.get_account_statistics(12345)
    print(f"\n📊 الإحصائيات: {stats}")
