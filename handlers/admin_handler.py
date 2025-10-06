"""
👨‍💻 Admin Handler - معالج المطور
معالجة تفاعلات المطور Nagdat
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from utils.keyboards import *
from utils.formatters import *
from utils.validators import *
from bybit_api import public_api
from config import ADMIN_USER_ID, DEVELOPER_INFO

logger = logging.getLogger(__name__)


class AdminHandler:
    """معالج تفاعلات المطور"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """التحقق من صلاحيات المطور"""
        return user_id == ADMIN_USER_ID
    
    @staticmethod
    async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لوحة المطور"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not AdminHandler.is_admin(user_id):
            await query.answer("⛔ ليس لديك صلاحية للوصول", show_alert=True)
            return
        
        # جمع الإحصائيات
        total_users = db.get_all_users_count()
        active_users = db.get_active_users_count()
        subscribers = len(db.get_nagdat_subscribers())
        signals_sent = db.get_total_signals_sent()
        
        # تنسيق الرسالة
        msg = MESSAGES['developer_panel'].format(
            subscribers=subscribers,
            signals_sent=signals_sent
        )
        msg = msg.replace("{star}", EMOJIS['star'])
        msg = msg.replace("{info}", EMOJIS['info'])
        msg = msg.replace("{chart_up}", EMOJIS['chart_up'])
        msg = msg.replace("{fire}", EMOJIS['fire'])
        
        await query.edit_message_text(
            msg,
            reply_markup=admin_panel_keyboard()
        )
    
    @staticmethod
    async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إحصائيات البوت"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not AdminHandler.is_admin(user_id):
            await query.answer("⛔ ليس لديك صلاحية", show_alert=True)
            return
        
        # جمع الإحصائيات
        stats = {
            'total_users': db.get_all_users_count(),
            'active_users': db.get_active_users_count(),
            'subscribers': len(db.get_nagdat_subscribers()),
            'signals_sent': db.get_total_signals_sent(),
            'active_trades': 0  # TODO: حساب الصفقات النشطة
        }
        
        stats_msg = format_admin_stats(stats)
        
        await query.edit_message_text(
            stats_msg,
            reply_markup=back_button("admin_panel")
        )
    
    @staticmethod
    async def admin_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المشتركين"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not AdminHandler.is_admin(user_id):
            await query.answer("⛔ ليس لديك صلاحية", show_alert=True)
            return
        
        subscribers = db.get_nagdat_subscribers()
        
        if not subscribers:
            msg = f"{EMOJIS['info']} لا يوجد مشتركين حالياً"
        else:
            msg = f"{EMOJIS['bell']} ━━━ المشتركين ({len(subscribers)}) ━━━\n\n"
            
            for i, sub_id in enumerate(subscribers[:20], 1):
                user_data = db.get_user(sub_id)
                if user_data:
                    username = user_data.get('username', 'Unknown')
                    msg += f"{i}. @{username} (ID: {sub_id})\n"
            
            if len(subscribers) > 20:
                msg += f"\n... و {len(subscribers) - 20} آخرين"
        
        await query.edit_message_text(
            msg,
            reply_markup=back_button("admin_panel")
        )
    
    @staticmethod
    async def admin_send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء إرسال إشارة"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not AdminHandler.is_admin(user_id):
            await query.answer("⛔ ليس لديك صلاحية", show_alert=True)
            return
        
        # حفظ الحالة
        context.user_data['admin_action'] = 'send_signal'
        context.user_data['signal_data'] = {}
        
        await query.edit_message_text(
            f"{EMOJIS['signal']} ━━━ إرسال إشارة جديدة ━━━\n\n"
            f"الخطوة 1/4: اختر نوع الإشارة:",
            reply_markup=signal_type_keyboard()
        )
    
    @staticmethod
    async def signal_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إشارة شراء"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['signal_data']['action'] = 'buy'
        
        await query.edit_message_text(
            f"{COLORS['green']} إشارة شراء (BUY)\n\n"
            f"الخطوة 2/4: أرسل رمز الزوج\n"
            f"مثال: BTC/USDT أو BTCUSDT",
            reply_markup=back_button("admin_panel")
        )
    
    @staticmethod
    async def signal_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إشارة بيع"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['signal_data']['action'] = 'sell'
        
        await query.edit_message_text(
            f"{COLORS['red']} إشارة بيع (SELL)\n\n"
            f"الخطوة 2/4: أرسل رمز الزوج\n"
            f"مثال: BTC/USDT أو BTCUSDT",
            reply_markup=back_button("admin_panel")
        )
    
    @staticmethod
    async def process_signal_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة مدخلات الإشارة"""
        user_id = update.effective_user.id
        
        if not AdminHandler.is_admin(user_id):
            return
        
        if context.user_data.get('admin_action') != 'send_signal':
            return
        
        signal_data = context.user_data.get('signal_data', {})
        text = update.message.text
        
        # الخطوة 2: رمز الزوج
        if 'action' in signal_data and 'symbol' not in signal_data:
            is_valid, symbol = validate_symbol(text)
            if not is_valid:
                await update.message.reply_text(format_error_message(symbol))
                return
            
            signal_data['symbol'] = symbol
            context.user_data['signal_data'] = signal_data
            
            await update.message.reply_text(
                f"✅ الزوج: {symbol}\n\n"
                f"الخطوة 3/4: أرسل الرافعة المالية (1-20)\n"
                f"أو أرسل 0 للتخطي"
            )
        
        # الخطوة 3: الرافعة
        elif 'symbol' in signal_data and 'leverage' not in signal_data:
            try:
                leverage = int(text)
                if leverage < 0 or leverage > 20:
                    raise ValueError()
                
                signal_data['leverage'] = leverage if leverage > 0 else 1
                context.user_data['signal_data'] = signal_data
                
                await update.message.reply_text(
                    f"✅ الرافعة: {signal_data['leverage']}x\n\n"
                    f"الخطوة 4/4: أرسل ملاحظة إضافية\n"
                    f"أو أرسل 'تخطي' للإرسال مباشرة"
                )
            except:
                await update.message.reply_text(
                    format_error_message("الرجاء إدخال رقم بين 0-20")
                )
        
        # الخطوة 4: الملاحظات
        elif 'leverage' in signal_data and 'message' not in signal_data:
            if text.lower() != 'تخطي':
                signal_data['message'] = sanitize_input(text)
            else:
                signal_data['message'] = None
            
            context.user_data['signal_data'] = signal_data
            
            # عرض ملخص الإشارة
            await AdminHandler.confirm_signal(update, context)
    
    @staticmethod
    async def confirm_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد إرسال الإشارة"""
        signal_data = context.user_data.get('signal_data', {})
        
        # الحصول على السعر الحالي
        ticker = await public_api.get_ticker(signal_data['symbol'])
        
        # تنسيق الرسالة
        action_emoji = COLORS['green'] if signal_data['action'] == 'buy' else COLORS['red']
        
        msg = f"""
{EMOJIS['signal']} ━━━ تأكيد الإشارة ━━━

{action_emoji} الإجراء: {signal_data['action'].upper()}
💱 الزوج: {signal_data['symbol']}
📊 الرافعة: {signal_data['leverage']}x
"""
        
        if ticker:
            msg += f"💹 السعر الحالي: {format_price(ticker['price'], 4)}\n"
        
        if signal_data.get('message'):
            msg += f"\n📝 ملاحظات: {signal_data['message']}\n"
        
        msg += f"\n{EMOJIS['bell']} سيتم إرسالها إلى {len(db.get_nagdat_subscribers())} مشترك"
        
        # حفظ ticker في الحالة
        context.user_data['signal_ticker'] = ticker
        
        await update.message.reply_text(
            msg,
            reply_markup=confirm_signal_keyboard(signal_data)
        )
    
    @staticmethod
    async def confirm_send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد وإرسال الإشارة"""
        query = update.callback_query
        await query.answer()
        
        signal_data = context.user_data.get('signal_data', {})
        ticker = context.user_data.get('signal_ticker')
        
        # حفظ الإشارة في قاعدة البيانات
        signal_id = db.create_signal(
            sender_id=query.from_user.id,
            symbol=signal_data['symbol'],
            action=signal_data['action'],
            leverage=signal_data['leverage'],
            message=signal_data.get('message')
        )
        
        # الحصول على المشتركين
        subscribers = db.get_nagdat_subscribers()
        
        if not subscribers:
            await query.edit_message_text(
                f"{EMOJIS['info']} لا يوجد مشتركين لإرسال الإشارة",
                reply_markup=back_button("admin_panel")
            )
            return
        
        # تنسيق رسالة الإشارة
        signal_msg = format_nagdat_signal(signal_data, ticker)
        
        # إرسال للمشتركين
        success_count = 0
        failed_count = 0
        
        for user_id in subscribers:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=signal_msg,
                    parse_mode='Markdown'
                )
                db.increment_subscriber_signals(user_id)
                db.increment_signal_execution(signal_id)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send signal to {user_id}: {e}")
                failed_count += 1
        
        # رسالة النتيجة
        result_msg = f"""
{EMOJIS['success']} تم إرسال الإشارة بنجاح!

{EMOJIS['bell']} أُرسلت إلى: {success_count} مشترك
"""
        
        if failed_count > 0:
            result_msg += f"{EMOJIS['warning']} فشل الإرسال لـ: {failed_count}\n"
        
        await query.edit_message_text(
            result_msg,
            reply_markup=back_button("admin_panel")
        )
        
        # تنظيف الحالة
        context.user_data.pop('admin_action', None)
        context.user_data.pop('signal_data', None)
        context.user_data.pop('signal_ticker', None)
    
    @staticmethod
    async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رسالة جماعية"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not AdminHandler.is_admin(user_id):
            await query.answer("⛔ ليس لديك صلاحية", show_alert=True)
            return
        
        context.user_data['admin_action'] = 'broadcast'
        
        await query.edit_message_text(
            f"📢 ━━━ رسالة جماعية ━━━\n\n"
            f"أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:",
            reply_markup=back_button("admin_panel")
        )
    
    @staticmethod
    async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسالة الجماعية"""
        user_id = update.effective_user.id
        
        if not AdminHandler.is_admin(user_id):
            return
        
        if context.user_data.get('admin_action') != 'broadcast':
            return
        
        message = update.message.text
        
        # الحصول على جميع المستخدمين
        # TODO: إضافة دالة في database.py للحصول على كل المستخدمين
        
        await update.message.reply_text(
            f"{EMOJIS['info']} جاري الإرسال...",
        )
        
        # هنا يتم الإرسال لكل المستخدمين
        # TODO: تنفيذ منطق الإرسال الجماعي
        
        context.user_data.pop('admin_action', None)

