#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام متكامل لربط إدارة المخاطر بالمحفظة
يتضمن فحص مستمر للصفقات المفتوحة وإغلاقها تلقائياً عند الوصول للحد
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from users.database import db_manager

logger = logging.getLogger(__name__)

class RiskPortfolioIntegration:
    """نظام متكامل لربط إدارة المخاطر بالمحفظة"""
    
    def __init__(self):
        self.monitoring_active = {}  # {user_id: bool}
        self.last_check = {}  # {user_id: datetime}
    
    async def check_and_close_if_limit_reached(self, user_id: int, account_type: str = 'demo', 
                                                 bot_application = None) -> dict:
        """فحص حدود المخاطر وإغلاق الصفقات إذا لزم الأمر
        
        Args:
            user_id: معرف المستخدم
            account_type: نوع الحساب
            bot_application: تطبيق البوت لإرسال الإشعارات
            
        Returns:
            dict: {
                'action_taken': str - الإجراء المتخذ,
                'closed_positions': int - عدد الصفقات المغلقة,
                'risk_status': str - حالة المخاطر,
                'message': str - رسالة توضيحية
            }
        """
        try:
            # فحص حدود المخاطر
            risk_check = db_manager.check_risk_limits_before_trade(user_id, account_type)
            
            if not risk_check['can_trade'] and risk_check['risk_status'] == 'danger':
                # الوصول للحد الأقصى - إغلاق جميع الصفقات
                logger.warning(f"🚨 المستخدم {user_id} وصل للحد الأقصى للخسارة!")
                
                # الحصول على الصفقات المفتوحة
                open_positions = db_manager.get_user_orders(user_id, status='OPEN')
                
                if not open_positions:
                    return {
                        'action_taken': 'no_action',
                        'closed_positions': 0,
                        'risk_status': 'danger',
                        'message': 'لا توجد صفقات مفتوحة للإغلاق'
                    }
                
                # إغلاق جميع الصفقات
                closed_count = 0
                total_pnl = 0.0
                
                for position in open_positions:
                    try:
                        # إغلاق الصفقة
                        success = await self.close_position_emergency(
                            user_id, 
                            position, 
                            account_type
                        )
                        
                        if success:
                            closed_count += 1
                            total_pnl += position.get('unrealized_pnl', 0.0)
                            logger.info(f"✅ تم إغلاق الصفقة {position['order_id']} للمستخدم {user_id}")
                    
                    except Exception as e:
                        logger.error(f"❌ خطأ في إغلاق الصفقة {position.get('order_id')}: {e}")
                
                # إيقاف البوت للمستخدم
                db_manager.toggle_user_active(user_id)
                
                # إرسال إشعار للمستخدم
                if bot_application:
                    await self.send_risk_alert(
                        bot_application,
                        user_id,
                        risk_check,
                        closed_count,
                        total_pnl
                    )
                
                return {
                    'action_taken': 'closed_all_and_stopped',
                    'closed_positions': closed_count,
                    'risk_status': 'danger',
                    'message': f'تم إغلاق {closed_count} صفقة وإيقاف البوت',
                    'total_pnl': total_pnl,
                    'risk_info': risk_check
                }
            
            elif risk_check['risk_status'] == 'warning':
                # تحذير - إرسال إشعار فقط
                if bot_application:
                    await self.send_warning_alert(bot_application, user_id, risk_check)
                
                return {
                    'action_taken': 'warning_sent',
                    'closed_positions': 0,
                    'risk_status': 'warning',
                    'message': 'تم إرسال تحذير للمستخدم',
                    'risk_info': risk_check
                }
            
            else:
                # آمن - لا حاجة لأي إجراء
                return {
                    'action_taken': 'no_action',
                    'closed_positions': 0,
                    'risk_status': 'safe',
                    'message': 'الوضع آمن',
                    'risk_info': risk_check
                }
        
        except Exception as e:
            logger.error(f"❌ خطأ في فحص وإغلاق صفقات المستخدم {user_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'action_taken': 'error',
                'closed_positions': 0,
                'risk_status': 'unknown',
                'message': f'خطأ: {str(e)}'
            }
    
    async def close_position_emergency(self, user_id: int, position: dict, 
                                        account_type: str = 'demo') -> bool:
        """إغلاق صفقة في حالة الطوارئ
        
        Args:
            user_id: معرف المستخدم
            position: بيانات الصفقة
            account_type: نوع الحساب
            
        Returns:
            bool: نجاح الإغلاق
        """
        try:
            order_id = position['order_id']
            symbol = position['symbol']
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            
            # حساب السعر الحالي (افتراضياً نفس سعر الدخول - يجب تحديثه من السوق)
            current_price = position.get('current_price', entry_price)
            
            # حساب PnL
            if side.lower() == 'buy':
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity
            
            # تحديث حالة الصفقة في قاعدة البيانات
            db_manager.close_order(order_id, pnl)
            
            # تحديث الرصيد
            user_data = db_manager.get_user(user_id)
            if user_data:
                new_balance = user_data['balance'] + pnl
                db_manager.update_user_balance(user_id, new_balance)
            
            # تحديث إحصائيات المخاطر
            db_manager.update_loss_after_trade_close(user_id, pnl)
            
            logger.info(f"✅ تم إغلاق الصفقة {order_id} في حالة الطوارئ: PnL={pnl:.2f}")
            return True
        
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقة في حالة الطوارئ: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def send_risk_alert(self, bot_application, user_id: int, risk_check: dict,
                               closed_count: int, total_pnl: float):
        """إرسال إشعار خطر للمستخدم
        
        Args:
            bot_application: تطبيق البوت
            user_id: معرف المستخدم
            risk_check: نتائج فحص المخاطر
            closed_count: عدد الصفقات المغلقة
            total_pnl: إجمالي الربح/الخسارة
        """
        try:
            message = f"""
🚨 **تنبيه خطر - تم إيقاف التداول!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **السبب:**
{risk_check['reason']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **الإحصائيات:**
💰 الرصيد الفعلي: {risk_check['real_balance']:.2f} USDT
📉 الخسارة الحالية: {risk_check['current_loss']:.2f} USDT
🎯 الحد الأقصى: {risk_check['max_loss_allowed']:.2f} USDT
📅 خسارة يومية: {risk_check.get('daily_loss', 0):.2f} USDT
📆 خسارة أسبوعية: {risk_check.get('weekly_loss', 0):.2f} USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 **الإجراءات المتخذة:**
✅ تم إغلاق {closed_count} صفقة مفتوحة
💵 إجمالي PnL من الإغلاق: {total_pnl:+.2f} USDT
⏸️ تم إيقاف البوت تلقائياً

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **ماذا تفعل الآن؟**
1. راجع استراتيجيتك
2. قيّم إدارة المخاطر
3. عدّل الحدود إذا لزم الأمر
4. أعد تفعيل البوت عندما تكون مستعداً

⚙️ لإعادة تفعيل البوت: /start ثم "📊 حالة الحساب"
            """
            
            await bot_application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ تم إرسال إشعار الخطر للمستخدم {user_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال إشعار الخطر: {e}")
    
    async def send_warning_alert(self, bot_application, user_id: int, risk_check: dict):
        """إرسال تحذير للمستخدم
        
        Args:
            bot_application: تطبيق البوت
            user_id: معرف المستخدم
            risk_check: نتائج فحص المخاطر
        """
        try:
            message = f"""
⚠️ **تحذير - اقتراب من حد المخاطر!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **الوضع الحالي:**
💰 الرصيد الفعلي: {risk_check['real_balance']:.2f} USDT
📉 الخسارة الحالية: {risk_check['current_loss']:.2f} USDT
🎯 الحد الأقصى: {risk_check['max_loss_allowed']:.2f} USDT
📏 الهامش المتبقي: {risk_check['remaining_margin']:.2f} USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **توصيات:**
• قلل من حجم التداول
• راجع الصفقات المفتوحة
• فكر في إغلاق بعض الصفقات الخاسرة
• كن حذراً في الصفقات القادمة

⚙️ لمراجعة إعدادات المخاطر: /start ثم "⚙️ الإعدادات" ثم "🛡️ إدارة المخاطر"
            """
            
            await bot_application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ تم إرسال تحذير للمستخدم {user_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التحذير: {e}")
    
    async def monitor_user_continuously(self, user_id: int, account_type: str = 'demo',
                                         bot_application = None, interval: int = 60):
        """مراقبة مستمرة لمخاطر المستخدم
        
        Args:
            user_id: معرف المستخدم
            account_type: نوع الحساب
            bot_application: تطبيق البوت
            interval: الفترة بين الفحوصات (بالثواني)
        """
        self.monitoring_active[user_id] = True
        logger.info(f"🔍 بدء المراقبة المستمرة للمستخدم {user_id}")
        
        while self.monitoring_active.get(user_id, False):
            try:
                # فحص المخاطر
                result = await self.check_and_close_if_limit_reached(
                    user_id,
                    account_type,
                    bot_application
                )
                
                self.last_check[user_id] = datetime.now()
                
                # إذا تم إيقاف البوت، إيقاف المراقبة
                if result['action_taken'] == 'closed_all_and_stopped':
                    self.monitoring_active[user_id] = False
                    logger.info(f"⏸️ تم إيقاف المراقبة للمستخدم {user_id} بسبب الوصول للحد")
                    break
                
                # الانتظار قبل الفحص التالي
                await asyncio.sleep(interval)
            
            except Exception as e:
                logger.error(f"❌ خطأ في المراقبة المستمرة للمستخدم {user_id}: {e}")
                await asyncio.sleep(interval)
        
        logger.info(f"🛑 تم إيقاف المراقبة المستمرة للمستخدم {user_id}")
    
    def stop_monitoring(self, user_id: int):
        """إيقاف المراقبة المستمرة لمستخدم
        
        Args:
            user_id: معرف المستخدم
        """
        self.monitoring_active[user_id] = False
        logger.info(f"🛑 تم طلب إيقاف المراقبة للمستخدم {user_id}")
    
    def get_monitoring_status(self, user_id: int) -> dict:
        """الحصول على حالة المراقبة لمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            dict: حالة المراقبة
        """
        return {
            'is_active': self.monitoring_active.get(user_id, False),
            'last_check': self.last_check.get(user_id)
        }

# إنشاء مثيل عام
risk_portfolio_integration = RiskPortfolioIntegration()

