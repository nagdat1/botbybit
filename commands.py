#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الأوامر الأساسية للبوت
يدعم أوامر /balance, /buy, /sell مع حماية المستخدمين
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from user_manager import user_manager
from order_manager import order_manager
from api_manager import api_manager
from ui_manager import ui_manager
from database import db_manager

logger = logging.getLogger(__name__)

class CommandHandler:
    """معالج الأوامر الأساسية"""
    
    def __init__(self):
        self.command_history: Dict[int, List[Dict]] = {}
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /start"""
        try:
            user_id = update.effective_user.id
            username = update.effective_user.username
            first_name = update.effective_user.first_name
            last_name = update.effective_user.last_name
            
            # إضافة المستخدم إلى النظام
            user_manager.get_user_environment(user_id)
            
            # الحصول على لوحة المفاتيح الرئيسية
            keyboard = ui_manager.get_main_menu_keyboard(user_id)
            
            # رسالة الترحيب
            welcome_text = f"""
🤖 مرحباً بك في بوت التداول الذكي على Bybit

👤 مرحباً {first_name}!

🔧 الميزات المتاحة:
• 🔗 ربط مفاتيح API الخاصة بك
• ⚙️ إعدادات مخصصة لكل مستخدم
• 📊 إدارة الصفقات مع TP/SL
• 💰 تداول حقيقي وتجريبي
• 📈 مراقبة الأسعار في الوقت الفعلي

استخدم الأزرار أدناه للتنقل في البوت
            """
            
            await update.message.reply_text(welcome_text, reply_markup=keyboard)
            
            # تسجيل الأمر في التاريخ
            self._log_command(user_id, "/start", "success")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر /start: {e}")
            await update.message.reply_text("❌ حدث خطأ في بدء البوت")
    
    async def handle_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /balance"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من وجود المستخدم
            user_env = user_manager.get_user_environment(user_id)
            
            # الحصول على معلومات الرصيد
            balance_info = user_env.get_balance_info()
            trading_stats = user_env.get_trading_stats()
            settings = user_env.get_settings()
            
            # الحصول على رصيد API إذا كان مرتبطاً
            api_balance = None
            if user_env.has_api_keys():
                try:
                    api_response = api_manager.get_user_balance(user_id)
                    if api_response.get("retCode") == 0:
                        balance_list = api_response.get("result", {}).get("list", [])
                        if balance_list:
                            api_balance = balance_list[0]
                except Exception as e:
                    logger.error(f"خطأ في الحصول على رصيد API للمستخدم {user_id}: {e}")
            
            # تنسيق رسالة الرصيد
            balance_text = f"""
💰 معلومات الرصيد

📊 الحساب التجريبي:
• الرصيد الكلي: {balance_info['balance']:.2f} USDT
• الرصيد المتاح: {balance_info['available_balance']:.2f} USDT
• الهامش المحجوز: {balance_info['margin_locked']:.2f} USDT
• إجمالي PnL: {balance_info['total_pnl']:.2f} USDT

📈 إحصائيات التداول:
• إجمالي الصفقات: {trading_stats['total_trades']}
• الصفقات الرابحة: {trading_stats['winning_trades']}
• الصفقات الخاسرة: {trading_stats['losing_trades']}
• معدل النجاح: {trading_stats['win_rate']:.1f}%

⚙️ الإعدادات:
• نوع السوق: {settings.get('market_type', 'spot').upper()}
• الرافعة المالية: {settings.get('leverage', 1)}x
• مبلغ التداول: {settings.get('trade_amount', 100)} USDT
            """
            
            # إضافة رصيد API إذا كان متاحاً
            if api_balance:
                total_equity = api_balance.get("totalEquity", "0")
                available_balance = api_balance.get("availableBalance", "0")
                
                balance_text += f"""

🔗 الحساب الحقيقي (Bybit):
• إجمالي الأسهم: {total_equity} USDT
• الرصيد المتاح: {available_balance} USDT
                """
            
            await update.message.reply_text(balance_text)
            
            # تسجيل الأمر
            self._log_command(user_id, "/balance", "success")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر /balance: {e}")
            await update.message.reply_text("❌ خطأ في الحصول على معلومات الرصيد")
    
    async def handle_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /buy"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من نشاط المستخدم
            if not user_manager.is_user_active(user_id):
                await update.message.reply_text("❌ البوت متوقف لهذا المستخدم")
                return
            
            # التحقق من وجود مفاتيح API
            if not api_manager.has_user_api(user_id):
                await update.message.reply_text("❌ يجب ربط مفاتيح API أولاً")
                return
            
            # التحقق من المعاملات
            if not context.args or len(context.args) < 2:
                await update.message.reply_text(
                    "❌ استخدام خاطئ!\n"
                    "استخدم: /buy SYMBOL QUANTITY\n"
                    "مثال: /buy BTCUSDT 0.001"
                )
                return
            
            symbol = context.args[0].upper()
            quantity = float(context.args[1])
            
            if quantity <= 0:
                await update.message.reply_text("❌ الكمية يجب أن تكون أكبر من صفر")
                return
            
            # الحصول على السعر الحالي
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            market_type = settings.get('market_type', 'spot')
            category = "linear" if market_type == "futures" else "spot"
            
            current_price = api_manager.get_user_price(user_id, symbol, category)
            if not current_price:
                await update.message.reply_text(f"❌ لا يمكن الحصول على سعر {symbol}")
                return
            
            # التحقق من وجود الرمز
            if not api_manager.get_user_api(user_id).check_symbol_exists(symbol, category):
                await update.message.reply_text(f"❌ الرمز {symbol} غير موجود في {market_type.upper()}")
                return
            
            # تنفيذ الصفقة
            success, result = await self._execute_trade(
                user_id, symbol, "buy", quantity, current_price, category
            )
            
            if success:
                await update.message.reply_text(f"✅ تم تنفيذ أمر الشراء بنجاح\n{result}")
                self._log_command(user_id, f"/buy {symbol} {quantity}", "success")
            else:
                await update.message.reply_text(f"❌ فشل في تنفيذ أمر الشراء: {result}")
                self._log_command(user_id, f"/buy {symbol} {quantity}", "failed")
            
        except ValueError:
            await update.message.reply_text("❌ الكمية يجب أن تكون رقماً صحيحاً")
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر /buy: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر الشراء")
    
    async def handle_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /sell"""
        try:
            user_id = update.effective_user.id
            
            # التحقق من نشاط المستخدم
            if not user_manager.is_user_active(user_id):
                await update.message.reply_text("❌ البوت متوقف لهذا المستخدم")
                return
            
            # التحقق من وجود مفاتيح API
            if not api_manager.has_user_api(user_id):
                await update.message.reply_text("❌ يجب ربط مفاتيح API أولاً")
                return
            
            # التحقق من المعاملات
            if not context.args or len(context.args) < 2:
                await update.message.reply_text(
                    "❌ استخدام خاطئ!\n"
                    "استخدم: /sell SYMBOL QUANTITY\n"
                    "مثال: /sell BTCUSDT 0.001"
                )
                return
            
            symbol = context.args[0].upper()
            quantity = float(context.args[1])
            
            if quantity <= 0:
                await update.message.reply_text("❌ الكمية يجب أن تكون أكبر من صفر")
                return
            
            # الحصول على السعر الحالي
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            market_type = settings.get('market_type', 'spot')
            category = "linear" if market_type == "futures" else "spot"
            
            current_price = api_manager.get_user_price(user_id, symbol, category)
            if not current_price:
                await update.message.reply_text(f"❌ لا يمكن الحصول على سعر {symbol}")
                return
            
            # التحقق من وجود الرمز
            if not api_manager.get_user_api(user_id).check_symbol_exists(symbol, category):
                await update.message.reply_text(f"❌ الرمز {symbol} غير موجود في {market_type.upper()}")
                return
            
            # تنفيذ الصفقة
            success, result = await self._execute_trade(
                user_id, symbol, "sell", quantity, current_price, category
            )
            
            if success:
                await update.message.reply_text(f"✅ تم تنفيذ أمر البيع بنجاح\n{result}")
                self._log_command(user_id, f"/sell {symbol} {quantity}", "success")
            else:
                await update.message.reply_text(f"❌ فشل في تنفيذ أمر البيع: {result}")
                self._log_command(user_id, f"/sell {symbol} {quantity}", "failed")
            
        except ValueError:
            await update.message.reply_text("❌ الكمية يجب أن تكون رقماً صحيحاً")
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر /sell: {e}")
            await update.message.reply_text("❌ حدث خطأ في تنفيذ أمر البيع")
    
    async def _execute_trade(self, user_id: int, symbol: str, side: str, 
                           quantity: float, price: float, category: str) -> Tuple[bool, str]:
        """تنفيذ الصفقة"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            
            # تحديد نوع التداول
            account_type = settings.get('account_type', 'demo')
            
            if account_type == 'real':
                # تنفيذ صفقة حقيقية
                return await self._execute_real_trade(user_id, symbol, side, quantity, price, category)
            else:
                # تنفيذ صفقة تجريبية
                return await self._execute_demo_trade(user_id, symbol, side, quantity, price, category)
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة للمستخدم {user_id}: {e}")
            return False, str(e)
    
    async def _execute_real_trade(self, user_id: int, symbol: str, side: str, 
                                quantity: float, price: float, category: str) -> Tuple[bool, str]:
        """تنفيذ صفقة حقيقية"""
        try:
            # وضع أمر في Bybit
            response = api_manager.place_user_order(
                user_id, symbol, side, "Market", str(quantity), category=category
            )
            
            if response.get("retCode") == 0:
                order_id = response.get("result", {}).get("orderId", "")
                
                result_text = f"""
📊 الرمز: {symbol}
🔄 النوع: {side.upper()}
📊 الكمية: {quantity}
💲 السعر: {price:.6f}
🏪 السوق: {category.upper()}
🆔 رقم الأمر: {order_id}
                """
                
                return True, result_text
            else:
                error_msg = response.get("retMsg", "خطأ غير محدد")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة الحقيقية للمستخدم {user_id}: {e}")
            return False, str(e)
    
    async def _execute_demo_trade(self, user_id: int, symbol: str, side: str, 
                                 quantity: float, price: float, category: str) -> Tuple[bool, str]:
        """تنفيذ صفقة تجريبية"""
        try:
            user_env = user_manager.get_user_environment(user_id)
            settings = user_env.get_settings()
            
            # حساب الهامش للفيوتشر
            leverage = settings.get('leverage', 1)
            margin_amount = 0
            
            if category == "linear" and leverage > 1:
                margin_amount = (quantity * price) / leverage
            
            # إنشاء الصفقة في النظام التجريبي
            success, order_id = order_manager.create_order(
                user_id=user_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                leverage=leverage,
                margin_amount=margin_amount
            )
            
            if success:
                result_text = f"""
📊 الرمز: {symbol}
🔄 النوع: {side.upper()}
📊 الكمية: {quantity}
💲 السعر: {price:.6f}
🏪 السوق: {category.upper()}
⚡ الرافعة: {leverage}x
🆔 رقم الصفقة: {order_id}
                """
                
                if margin_amount > 0:
                    result_text += f"💰 الهامش: {margin_amount:.2f} USDT\n"
                
                return True, result_text
            else:
                return False, order_id
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة التجريبية للمستخدم {user_id}: {e}")
            return False, str(e)
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /help"""
        try:
            help_text = """
🤖 أوامر البوت المتاحة:

🔧 الأوامر الأساسية:
• /start - بدء البوت وعرض القائمة الرئيسية
• /balance - عرض معلومات الرصيد والإحصائيات
• /help - عرض هذه الرسالة

📊 أوامر التداول:
• /buy SYMBOL QUANTITY - شراء رمز معين
• /sell SYMBOL QUANTITY - بيع رمز معين

📝 أمثلة:
• /buy BTCUSDT 0.001
• /sell ETHUSDT 0.1

🔗 الربط:
• اضغط على زر "🔗 الربط" لربط مفاتيح API
• أدخل مفاتيحك بالصيغة: API_KEY API_SECRET

⚙️ الإعدادات:
• اضغط على "⚙️ الإعدادات" لتخصيص البوت
• يمكنك تغيير نوع السوق والرافعة المالية

📊 الصفقات:
• اضغط على "📊 الصفقات المفتوحة" لإدارة صفقاتك
• يمكنك إضافة TP/SL والإغلاق الجزئي

❓ للمساعدة: تواصل مع الدعم الفني
            """
            
            await update.message.reply_text(help_text)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر /help: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض المساعدة")
    
    def _log_command(self, user_id: int, command: str, status: str):
        """تسجيل الأمر في التاريخ"""
        try:
            if user_id not in self.command_history:
                self.command_history[user_id] = []
            
            self.command_history[user_id].append({
                'command': command,
                'status': status,
                'timestamp': datetime.now()
            })
            
            # الاحتفاظ بآخر 50 أمر فقط
            if len(self.command_history[user_id]) > 50:
                self.command_history[user_id] = self.command_history[user_id][-50:]
                
        except Exception as e:
            logger.error(f"خطأ في تسجيل الأمر: {e}")
    
    def get_command_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ الأوامر"""
        try:
            history = self.command_history.get(user_id, [])
            return history[-limit:] if history else []
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ الأوامر: {e}")
            return []

# إنشاء مثيل عام لمعالج الأوامر
command_handler = CommandHandler()
