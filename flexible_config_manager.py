#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الإعدادات المرن - يحافظ على آلية التوقيع وحساب السعر الحالية
يدعم تعديل المتغيرات (API، الرافعة، المبلغ) دون كسر النظام
"""

import logging
import json
from typing import Dict, Optional, Any, Tuple
from datetime import datetime
from database import db_manager
from real_account_manager import real_account_manager, BybitRealAccount

logger = logging.getLogger(__name__)

class FlexibleConfigManager:
    """مدير الإعدادات المرن - يحافظ على آلية التوقيع وحساب السعر"""
    
    def __init__(self):
        self.config_cache = {}  # تخزين مؤقت للإعدادات
        self.api_validators = {}  # مدققات API للمستخدمين
        
    def get_user_config(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم مع القيم الافتراضية"""
        try:
            # جلب البيانات من قاعدة البيانات
            user_data = db_manager.get_user(user_id)
            if not user_data:
                return self._get_default_config()
            
            # دمج إعدادات المستخدم مع القيم الافتراضية
            config = self._get_default_config()
            config.update({
                'user_id': user_id,
                'api_key': user_data.get('api_key', ''),
                'api_secret': user_data.get('api_secret', ''),
                'bybit_api_key': user_data.get('bybit_api_key', ''),
                'bybit_api_secret': user_data.get('bybit_api_secret', ''),
                'mexc_api_key': user_data.get('mexc_api_secret', ''),
                'mexc_api_secret': user_data.get('mexc_api_secret', ''),
                'exchange': user_data.get('exchange', 'bybit'),
                'account_type': user_data.get('account_type', 'demo'),
                'market_type': user_data.get('market_type', 'futures'),
                'trade_amount': user_data.get('trade_amount', 50.0),
                'leverage': user_data.get('leverage', 2),
                'is_active': user_data.get('is_active', True),
                'api_connected': user_data.get('api_connected', False),
                'last_updated': datetime.now().isoformat()
            })
            
            # تخزين في الذاكرة المؤقتة
            self.config_cache[user_id] = config
            
            return config
            
        except Exception as e:
            logger.error(f"خطأ في جلب إعدادات المستخدم {user_id}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """الحصول على الإعدادات الافتراضية"""
        return {
            'user_id': 0,
            'api_key': '',
            'api_secret': '',
            'bybit_api_key': '',
            'bybit_api_secret': '',
            'mexc_api_key': '',
            'mexc_api_secret': '',
            'exchange': 'bybit',
            'account_type': 'real',
            'market_type': 'futures',
            'trade_amount': 50.0,
            'leverage': 2,
            'is_active': True,
            'api_connected': False,
            'last_updated': datetime.now().isoformat()
        }
    
    def update_user_config(self, user_id: int, config_updates: Dict[str, Any]) -> Tuple[bool, str]:
        """تحديث إعدادات المستخدم مع التحقق من صحة البيانات"""
        try:
            # التحقق من صحة البيانات
            validation_result = self._validate_config_updates(config_updates)
            if not validation_result[0]:
                return False, validation_result[1]
            
            # تحديث في قاعدة البيانات
            success = db_manager.update_user_settings(user_id, config_updates)
            if not success:
                return False, "فشل في حفظ الإعدادات في قاعدة البيانات"
            
            # تحديث في الذاكرة المؤقتة
            if user_id in self.config_cache:
                self.config_cache[user_id].update(config_updates)
                self.config_cache[user_id]['last_updated'] = datetime.now().isoformat()
            
            # إذا تم تحديث API keys، اختبار الاتصال
            if 'api_key' in config_updates or 'api_secret' in config_updates:
                api_test_result = self._test_api_connection(user_id, config_updates)
                if api_test_result[0]:
                    logger.info(f"تم اختبار API بنجاح للمستخدم {user_id}")
                else:
                    logger.warning(f"فشل اختبار API للمستخدم {user_id}: {api_test_result[1]}")
            
            return True, "تم تحديث الإعدادات بنجاح"
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم {user_id}: {e}")
            return False, f"خطأ في تحديث الإعدادات: {e}"
    
    def _validate_config_updates(self, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من صحة البيانات المحدثة"""
        try:
            # التحقق من مبلغ التداول
            if 'trade_amount' in updates:
                amount = updates['trade_amount']
                if not isinstance(amount, (int, float)) or amount <= 0:
                    return False, "مبلغ التداول يجب أن يكون رقماً موجباً"
                if amount > 10000:
                    return False, "مبلغ التداول لا يمكن أن يتجاوز 10,000 USDT"
            
            # التحقق من الرافعة المالية
            if 'leverage' in updates:
                leverage = updates['leverage']
                if not isinstance(leverage, int) or leverage < 1 or leverage > 100:
                    return False, "الرافعة المالية يجب أن تكون بين 1 و 100"
            
            # التحقق من نوع السوق
            if 'market_type' in updates:
                market_type = updates['market_type']
                if market_type not in ['spot', 'futures']:
                    return False, "نوع السوق يجب أن يكون spot أو futures"
            
            # التحقق من نوع الحساب
            if 'account_type' in updates:
                account_type = updates['account_type']
                if account_type not in ['demo', 'real']:
                    return False, "نوع الحساب يجب أن يكون demo أو real"
            
            # التحقق من المنصة
            if 'exchange' in updates:
                exchange = updates['exchange']
                if exchange not in ['bybit', 'mexc']:
                    return False, "المنصة يجب أن تكون bybit أو mexc"
            
            return True, "البيانات صحيحة"
            
        except Exception as e:
            return False, f"خطأ في التحقق من البيانات: {e}"
    
    def _test_api_connection(self, user_id: int, config_updates: Dict[str, Any]) -> Tuple[bool, str]:
        """اختبار اتصال API مع الحفاظ على آلية التوقيع الحالية"""
        try:
            # الحصول على API keys
            api_key = config_updates.get('api_key', '')
            api_secret = config_updates.get('api_secret', '')
            
            if not api_key or not api_secret:
                return False, "مفاتيح API غير مكتملة"
            
            # إنشاء API مؤقت للاختبار باستخدام نفس آلية التوقيع
            temp_api = BybitRealAccount(api_key, api_secret)
            
            # اختبار الاتصال بجلب رصيد المحفظة
            balance = temp_api.get_wallet_balance('unified')
            
            if balance is not None:
                # تهيئة الحساب الحقيقي للمستخدم
                exchange = config_updates.get('exchange', 'bybit')
                if exchange == 'bybit':
                    real_account_manager.initialize_account(user_id, 'bybit', api_key, api_secret)
                
                # تحديث حالة الاتصال في قاعدة البيانات
                db_manager.update_user_data(user_id, {'api_connected': True})
                
                return True, "تم اختبار API بنجاح"
            else:
                return False, "فشل في جلب بيانات المحفظة"
                
        except Exception as e:
            logger.error(f"خطأ في اختبار API للمستخدم {user_id}: {e}")
            return False, f"خطأ في اختبار API: {e}"
    
    def calculate_trade_parameters(self, user_id: int, symbol: str, side: str, 
                                 current_price: float) -> Dict[str, Any]:
        """حساب معاملات التداول مع الحفاظ على آلية الحساب الحالية"""
        try:
            config = self.get_user_config(user_id)
            
            # الحصول على المعاملات الأساسية
            trade_amount = config['trade_amount']
            leverage = config['leverage']
            market_type = config['market_type']
            
            # حساب الكمية بناءً على نوع السوق
            if market_type == 'spot':
                # للسبوت: الكمية = المبلغ / السعر
                quantity = trade_amount / current_price
            else:
                # للفيوتشر: الكمية = (المبلغ * الرافعة) / السعر
                quantity = (trade_amount * leverage) / current_price
            
            # حساب الهامش المطلوب
            margin_required = trade_amount if market_type == 'spot' else trade_amount
            
            # حساب سعر التصفية للفيوتشر
            liquidation_price = None
            if market_type == 'futures':
                liquidation_price = self._calculate_liquidation_price(
                    current_price, side, leverage
                )
            
            return {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': current_price,
                'trade_amount': trade_amount,
                'leverage': leverage,
                'margin_required': margin_required,
                'liquidation_price': liquidation_price,
                'market_type': market_type,
                'account_type': config['account_type'],
                'exchange': config['exchange']
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب معاملات التداول للمستخدم {user_id}: {e}")
            return {}
    
    def _calculate_liquidation_price(self, entry_price: float, side: str, leverage: int) -> float:
        """حساب سعر التصفية باستخدام نفس الصيغة الحالية"""
        try:
            maintenance_margin_rate = 0.005  # 0.5%
            
            if side.lower() == "buy":
                # Long: Liquidation Price = Entry Price * (1 - (1/leverage) + maintenance_margin_rate)
                liquidation_price = entry_price * (1 - (1/leverage) + maintenance_margin_rate)
            else:
                # Short: Liquidation Price = Entry Price * (1 + (1/leverage) - maintenance_margin_rate)
                liquidation_price = entry_price * (1 + (1/leverage) - maintenance_margin_rate)
            
            return liquidation_price
            
        except Exception as e:
            logger.error(f"خطأ في حساب سعر التصفية: {e}")
            return 0.0
    
    def get_trading_summary(self, user_id: int) -> str:
        """الحصول على ملخص إعدادات التداول"""
        try:
            config = self.get_user_config(user_id)
            
            summary = f"""
**إعدادات التداول الحالية:**

🏦 **المنصة:** {config['exchange'].upper()}
🏪 **نوع السوق:** {config['market_type'].upper()}
👤 **نوع الحساب:** {config['account_type'].upper()}
💰 **مبلغ التداول:** {config['trade_amount']} USDT
⚡ **الرافعة المالية:** {config['leverage']}x
🔗 **حالة API:** {'🟢 متصل' if config['api_connected'] else '🔴 غير متصل'}
🟢 **حالة البوت:** {'نشط' if config['is_active'] else 'معطل'}

📅 **آخر تحديث:** {config['last_updated']}
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"خطأ في جلب ملخص التداول للمستخدم {user_id}: {e}")
            return "خطأ في جلب ملخص التداول"
    
    def clear_config_cache(self, user_id: int = None):
        """مسح الذاكرة المؤقتة للإعدادات"""
        try:
            if user_id:
                if user_id in self.config_cache:
                    del self.config_cache[user_id]
            else:
                self.config_cache.clear()
            
            logger.info(f"تم مسح الذاكرة المؤقتة للإعدادات")
            
        except Exception as e:
            logger.error(f"خطأ في مسح الذاكرة المؤقتة: {e}")
    
    def validate_trade_execution(self, user_id: int, trade_params: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من إمكانية تنفيذ الصفقة"""
        try:
            config = self.get_user_config(user_id)
            
            # التحقق من حالة البوت
            if not config['is_active']:
                return False, "البوت معطل"
            
            # التحقق من اتصال API للحسابات الحقيقية
            if config['account_type'] == 'real' and not config['api_connected']:
                return False, "API غير متصل"
            
            # التحقق من مبلغ التداول
            if trade_params.get('trade_amount', 0) <= 0:
                return False, "مبلغ التداول غير صحيح"
            
            # التحقق من الرافعة المالية للفيوتشر
            if config['market_type'] == 'futures':
                leverage = trade_params.get('leverage', 1)
                if leverage < 1 or leverage > 100:
                    return False, "الرافعة المالية غير صحيحة"
            
            return True, "يمكن تنفيذ الصفقة"
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من تنفيذ الصفقة: {e}")
            return False, f"خطأ في التحقق: {e}"

# إنشاء مثيل عام للمدير
flexible_config_manager = FlexibleConfigManager()
