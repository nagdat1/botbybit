#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المستخدمين المتعددين مع العزل الكامل
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import db_manager

logger = logging.getLogger(__name__)

# استيراد النظام المحسن
try:
    from simple_enhanced_system import SimpleEnhancedSystem
    ENHANCED_SYSTEM_AVAILABLE = True
    print("✅ النظام المحسن متاح في user_manager.py")
except ImportError as e:
    ENHANCED_SYSTEM_AVAILABLE = False
    print(f"⚠️ النظام المحسن غير متاح في user_manager.py: {e}")

class UserManager:
    """مدير المستخدمين المتعددين مع العزل الكامل"""
    
    def __init__(self, trading_account_class=None, bybit_api_class=None):
        self.users: Dict[int, Dict] = {}  # تخزين مؤقت لبيانات المستخدمين
        self.user_accounts: Dict[int, Dict] = {}  # حسابات تجريبية لكل مستخدم
        self.user_apis: Dict[int, Any] = {}  # APIs لكل مستخدم
        self.user_positions: Dict[int, Dict[str, Dict]] = {}  # صفقات كل مستخدم
        
        # تخزين الفئات للاستخدام عند الحاجة
        self.TradingAccount = trading_account_class
        self.BybitAPI = bybit_api_class
        
        # تهيئة النظام المحسن
        if ENHANCED_SYSTEM_AVAILABLE:
            try:
                self.enhanced_system = SimpleEnhancedSystem()
                print("✅ تم تهيئة النظام المحسن في UserManager")
            except Exception as e:
                print(f"⚠️ فشل في تهيئة النظام المحسن في UserManager: {e}")
                self.enhanced_system = None
        else:
            self.enhanced_system = None
        
        # تحميل المستخدمين من قاعدة البيانات
        # سيتم استدعاء load_all_users يدوياً بعد تهيئة الفئات
        # self.load_all_users()
    
    def load_all_users(self):
        """تحميل جميع المستخدمين من قاعدة البيانات"""
        try:
            users_data = db_manager.get_all_active_users()
            
            for user_data in users_data:
                user_id = user_data['user_id']
                self.users[user_id] = user_data
                
                # إنشاء حسابات تجريبية للمستخدم
                self._create_user_accounts(user_id, user_data)
                
                # إنشاء API للمستخدم إذا كان لديه مفاتيح
                if user_data.get('api_key') and user_data.get('api_secret'):
                    self._create_user_api(user_id, user_data['api_key'], user_data['api_secret'])
            
            logger.info(f"تم تحميل {len(self.users)} مستخدم")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل المستخدمين: {e}")
    
    def _create_user_accounts(self, user_id: int, user_data: Dict):
        """إنشاء حسابات تجريبية للمستخدم"""
        try:
            if not self.TradingAccount:
                logger.warning(f"TradingAccount class not set, skipping account creation for user {user_id}")
                return
                
            # حساب سبوت
            spot_account = self.TradingAccount(
                initial_balance=user_data.get('balance', 10000.0),
                account_type='spot'
            )
            
            # حساب فيوتشر
            futures_account = self.TradingAccount(
                initial_balance=user_data.get('balance', 10000.0),
                account_type='futures'
            )
            
            self.user_accounts[user_id] = {
                'spot': spot_account,
                'futures': futures_account
            }
            
            # تهيئة قائمة الصفقات للمستخدم
            self.user_positions[user_id] = {}
            
            logger.info(f"تم إنشاء حسابات للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء حسابات المستخدم {user_id}: {e}")
    
    def _create_user_api(self, user_id: int, api_key: str, api_secret: str):
        """إنشاء API للمستخدم"""
        try:
            if not self.BybitAPI:
                logger.warning(f"BybitAPI class not set, skipping API creation for user {user_id}")
                return
                
            self.user_apis[user_id] = self.BybitAPI(api_key, api_secret)
            logger.info(f"تم إنشاء API للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء API للمستخدم {user_id}: {e}")
    
    def create_user(self, user_id: int, api_key: str = None, api_secret: str = None) -> bool:
        """إنشاء مستخدم جديد"""
        try:
            # إنشاء في قاعدة البيانات
            success = db_manager.create_user(user_id, api_key, api_secret)
            
            if success:
                # تحميل بيانات المستخدم الجديد
                user_data = db_manager.get_user(user_id)
                
                if user_data:
                    self.users[user_id] = user_data
                    self._create_user_accounts(user_id, user_data)
                    
                    # إنشاء API إذا تم توفير المفاتيح
                    if api_key and api_secret:
                        self._create_user_api(user_id, api_key, api_secret)
                    
                    logger.info(f"تم إنشاء مستخدم جديد: {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        return self.users.get(user_id)
    
    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        """الحصول على إعدادات المستخدم في صيغة settings dict"""
        user_data = self.get_user(user_id)
        if not user_data:
            return None
        
        return {
            'market_type': user_data.get('market_type', 'spot'),
            'account_type': user_data.get('account_type', 'demo'),
            'trade_amount': user_data.get('trade_amount', 100.0),
            'leverage': user_data.get('leverage', 10)
        }
    
    def get_user_account(self, user_id: int, market_type: str = 'spot') -> Optional[Any]:
        """الحصول على حساب المستخدم"""
        user_accounts = self.user_accounts.get(user_id)
        if user_accounts:
            return user_accounts.get(market_type)
        return None
    
    def get_user_api(self, user_id: int) -> Optional[Any]:
        """الحصول على API المستخدم"""
        return self.user_apis.get(user_id)
    
    def get_user_positions(self, user_id: int) -> Dict[str, Dict]:
        """الحصول على صفقات المستخدم"""
        return self.user_positions.get(user_id, {})
    
    def update_user_api(self, user_id: int, api_key: str, api_secret: str) -> bool:
        """تحديث API keys للمستخدم"""
        try:
            # تحديث في قاعدة البيانات
            success = db_manager.update_user_api(user_id, api_key, api_secret)
            
            if success:
                # تحديث في الذاكرة
                if user_id in self.users:
                    self.users[user_id]['api_key'] = api_key
                    self.users[user_id]['api_secret'] = api_secret
                
                # إنشاء API جديد
                self._create_user_api(user_id, api_key, api_secret)
                
                logger.info(f"تم تحديث API للمستخدم {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث API للمستخدم {user_id}: {e}")
            return False
    
    def toggle_user_active(self, user_id: int) -> bool:
        """تبديل حالة تشغيل/إيقاف المستخدم"""
        try:
            success = db_manager.toggle_user_active(user_id)
            
            if success:
                # تحديث في الذاكرة
                if user_id in self.users:
                    current_status = self.users[user_id]['is_active']
                    self.users[user_id]['is_active'] = not current_status
                    
                    logger.info(f"تم تبديل حالة المستخدم {user_id} إلى: {not current_status}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تبديل حالة المستخدم {user_id}: {e}")
            return False
    
    def update_user_balance(self, user_id: int, balance: float) -> bool:
        """تحديث رصيد المستخدم"""
        try:
            success = db_manager.update_user_balance(user_id, balance)
            
            if success:
                # تحديث في الذاكرة
                if user_id in self.users:
                    self.users[user_id]['balance'] = balance
                
                # تحديث حسابات المستخدم
                user_accounts = self.user_accounts.get(user_id)
                if user_accounts:
                    user_accounts['spot'].update_balance(balance)
                    user_accounts['futures'].update_balance(balance)
                
                logger.info(f"تم تحديث رصيد المستخدم {user_id} إلى: {balance}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث رصيد المستخدم {user_id}: {e}")
            return False
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم"""
        try:
            success = db_manager.update_user_settings(user_id, settings)
            
            if success:
                # تحديث في الذاكرة
                if user_id in self.users:
                    for key, value in settings.items():
                        if key in ['partial_percents', 'tps_percents', 'notifications']:
                            self.users[user_id][key] = value
                
                logger.info(f"تم تحديث إعدادات المستخدم {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم {user_id}: {e}")
            return False
    
    def update_user(self, user_id: int, data: Dict) -> bool:
        """تحديث بيانات المستخدم العامة"""
        try:
            # تحديث في قاعدة البيانات
            success = db_manager.update_user_data(user_id, data)
            if success:
                # تحديث في الذاكرة المؤقتة
                if user_id in self.users:
                    self.users[user_id].update(data)
                logger.info(f"تم تحديث بيانات المستخدم {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"خطأ في تحديث بيانات المستخدم {user_id}: {e}")
            return False
    
    def is_user_active(self, user_id: int) -> bool:
        """التحقق من حالة المستخدم النشط"""
        user_data = self.get_user(user_id)
        return user_data and user_data.get('is_active', False)
    
    def has_api_keys(self, user_id: int) -> bool:
        """التحقق من وجود API keys للمستخدم"""
        user_data = self.get_user(user_id)
        return (user_data and 
                user_data.get('api_key') and 
                user_data.get('api_secret'))
    
    def execute_user_trade(self, user_id: int, symbol: str, action: str, price: float, 
                          amount: float, market_type: str = 'spot') -> tuple[bool, str]:
        """تنفيذ صفقة للمستخدم"""
        try:
            # التحقق من حالة المستخدم
            if not self.is_user_active(user_id):
                return False, "المستخدم غير نشط"
            
            # الحصول على حساب المستخدم
            account = self.get_user_account(user_id, market_type)
            if not account:
                return False, "حساب المستخدم غير موجود"
            
            # تنفيذ الصفقة حسب نوع السوق
            if market_type == 'futures':
                leverage = self.users[user_id].get('leverage', 10)
                success, result = account.open_futures_position(
                    symbol=symbol,
                    side=action,
                    margin_amount=amount,
                    price=price,
                    leverage=leverage
                )
            else:
                success, result = account.open_spot_position(
                    symbol=symbol,
                    side=action,
                    amount=amount,
                    price=price
                )
            
            if success:
                position_id = result
                
                # حفظ الصفقة في قاعدة البيانات
                order_data = {
                    'order_id': position_id,
                    'user_id': user_id,
                    'symbol': symbol,
                    'side': action,
                    'entry_price': price,
                    'quantity': amount,
                    'status': 'OPEN'
                }
                
                db_manager.create_order(order_data)
                
                # حفظ في الذاكرة
                self.user_positions[user_id][position_id] = {
                    'symbol': symbol,
                    'entry_price': price,
                    'side': action,
                    'account_type': market_type,
                    'quantity': amount,
                    'current_price': price,
                    'pnl_percent': 0.0
                }
                
                logger.info(f"تم تنفيذ صفقة للمستخدم {user_id}: {symbol} {action}")
                return True, position_id
            
            return False, result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ صفقة المستخدم {user_id}: {e}")
            return False, str(e)
    
    def close_user_position(self, user_id: int, position_id: str, close_price: float) -> tuple[bool, Dict]:
        """إغلاق صفقة المستخدم"""
        try:
            # الحصول على بيانات الصفقة
            position_data = self.user_positions[user_id].get(position_id)
            if not position_data:
                return False, {"error": "الصفقة غير موجودة"}
            
            # الحصول على حساب المستخدم
            account = self.get_user_account(user_id, position_data['account_type'])
            if not account:
                return False, {"error": "حساب المستخدم غير موجود"}
            
            # إغلاق الصفقة في الحساب
            if position_data['account_type'] == 'futures':
                success, result = account.close_futures_position(position_id, close_price)
            else:
                success, result = account.close_spot_position(position_id, close_price)
            
            if success:
                # تحديث في قاعدة البيانات
                db_manager.close_order(position_id, close_price, result.get('pnl', 0))
                
                # حذف من الذاكرة
                del self.user_positions[user_id][position_id]
                
                # تحديث الرصيد في قاعدة البيانات
                new_balance = account.balance
                self.update_user_balance(user_id, new_balance)
                
                logger.info(f"تم إغلاق صفقة المستخدم {user_id}: {position_id}")
                return True, result
            
            return False, result
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق صفقة المستخدم {user_id}: {e}")
            return False, {"error": str(e)}
    
    def update_user_positions_prices(self, user_id: int, prices: Dict[str, float]):
        """تحديث أسعار صفقات المستخدم"""
        try:
            user_positions = self.user_positions.get(user_id, {})
            if not user_positions:
                return
            
            # تحديث الأسعار
            for position_id, position_data in user_positions.items():
                symbol = position_data['symbol']
                if symbol in prices:
                    current_price = prices[symbol]
                    position_data['current_price'] = current_price
                    
                    # حساب الربح/الخسارة
                    entry_price = position_data['entry_price']
                    side = position_data['side']
                    
                    if side.lower() == "buy":
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                    else:
                        pnl_percent = ((entry_price - current_price) / entry_price) * 100
                    
                    position_data['pnl_percent'] = pnl_percent
            
            # تحديث في الحسابات التجريبية
            account = self.get_user_account(user_id, 'spot')
            if account:
                account.update_positions_pnl(prices)
            
            account = self.get_user_account(user_id, 'futures')
            if account:
                account.update_positions_pnl(prices)
                
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار صفقات المستخدم {user_id}: {e}")
    
    def get_user_account_info(self, user_id: int, market_type: str = 'spot') -> Dict:
        """الحصول على معلومات حساب المستخدم"""
        try:
            account = self.get_user_account(user_id, market_type)
            if account:
                return account.get_account_info()
            return {}
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات حساب المستخدم {user_id}: {e}")
            return {}
    
    def get_all_active_users(self) -> List[int]:
        """الحصول على جميع المستخدمين النشطين"""
        return [user_id for user_id, user_data in self.users.items() 
                if user_data.get('is_active', False)]
    
    def reload_user_data(self, user_id: int):
        """إعادة تحميل بيانات المستخدم من قاعدة البيانات"""
        try:
            user_data = db_manager.get_user(user_id)
            if user_data:
                self.users[user_id] = user_data
                logger.info(f"تم إعادة تحميل بيانات المستخدم {user_id}")
                
        except Exception as e:
            logger.error(f"خطأ في إعادة تحميل بيانات المستخدم {user_id}: {e}")

# سيتم إنشاء مثيل UserManager بعد تهيئة الفئات في bybit_trading_bot.py
user_manager = None
