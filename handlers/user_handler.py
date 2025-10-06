"""
👤 User Handler - معالج المستخدمين
معالجة جميع تفاعلات المستخدمين العاديين
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from utils.keyboards import *
from utils.formatters import *
from utils.validators import *
from bybit_api import public_api
from config import DEMO_INITIAL_BALANCE

logger = logging.getLogger(__name__)


class UserHandler:
    """معالج تفاعلات المستخدمين"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /start"""
        user = update.effective_user
        
        # التحقق من المستخدم أو إنشاؤه
        user_data = db.get_user(user.id)
        is_new = False
        
        if not user_data:
            user_data = db.create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            is_new = True
            logger.info(f"✅ New user created: {user.id} - {user.username}")
        
        # رسالة الترحيب
        welcome_msg = format_welcome_message(user.first_name, is_new)
        
        # التحقق إذا كان أدمن
        from config import ADMIN_USER_ID
        is_admin = (user.id == ADMIN_USER_ID)
        
        await update.message.reply_text(
            welcome_msg,
            reply_markup=main_menu_keyboard(is_admin)
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /help"""
        help_text = MESSAGES['help'].format(**EMOJIS)
        help_text = help_text.replace("{warning}", EMOJIS['warning'])
        help_text = help_text.replace("{fire}", EMOJIS['fire'])
        
        await update.message.reply_text(
            help_text,
            reply_markup=back_button()
        )
    
    @staticmethod
    async def menu_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المحفظة"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await query.edit_message_text("❌ خطأ: المستخدم غير موجود")
            return
        
        # الحصول على الصفقات المفتوحة
        trades = db.get_open_trades(user_id)
        
        # تنسيق رسالة المحفظة
        wallet_msg = format_wallet_info(user_data, trades)
        
        await query.edit_message_text(
            wallet_msg,
            reply_markup=back_button(),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def menu_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة الإعدادات"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        
        await query.edit_message_text(
            f"{EMOJIS['settings']} ━━━ الإعدادات ━━━",
            reply_markup=settings_keyboard(user_data)
        )
    
    @staticmethod
    async def settings_switch_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تبديل نوع الحساب"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            f"{EMOJIS['info']} اختر نوع الحساب:",
            reply_markup=account_type_keyboard()
        )
    
    @staticmethod
    async def account_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تفعيل الحساب التجريبي"""
        query = update.callback_query
        await query.answer("تم التبديل إلى الحساب التجريبي")
        
        user_id = query.from_user.id
        db.update_user_mode(user_id, 'demo')
        
        # إعادة تعيين الرصيد إذا لزم الأمر
        user_data = db.get_user(user_id)
        if user_data['demo_balance'] <= 0:
            db.update_demo_balance(user_id, DEMO_INITIAL_BALANCE)
        
        await query.edit_message_text(
            f"{EMOJIS['success']} تم التبديل إلى الحساب التجريبي!\n\n"
            f"رصيدك الحالي: {format_price(user_data['demo_balance'])}\n\n"
            f"يمكنك الآن البدء بالتداول بأمان 🎮",
            reply_markup=back_button()
        )
    
    @staticmethod
    async def account_real(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تفعيل الحساب الحقيقي"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        
        if not user_data.get('api_key'):
            await query.edit_message_text(
                f"{EMOJIS['warning']} للتبديل إلى الحساب الحقيقي، يجب إضافة بيانات API أولاً.\n\n"
                f"أرسل بيانات API بالصيغة التالية:\n\n"
                f"`/setapi YOUR_API_KEY YOUR_API_SECRET`\n\n"
                f"{EMOJIS['shield']} احصل على API من Bybit:\n"
                f"Settings → API → Create New Key",
                parse_mode='Markdown',
                reply_markup=back_button()
            )
            return
        
        db.update_user_mode(user_id, 'real')
        
        await query.edit_message_text(
            f"{EMOJIS['success']} تم التبديل إلى الحساب الحقيقي!\n\n"
            f"{EMOJIS['fire']} أنت الآن تتداول بأموال حقيقية\n"
            f"{EMOJIS['warning']} كن حذراً وتداول بمسؤولية",
            reply_markup=back_button()
        )
    
    @staticmethod
    async def setapi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر تعيين API"""
        user_id = update.effective_user.id
        
        # التحقق من الصيغة
        if len(context.args) < 2:
            await update.message.reply_text(
                f"{EMOJIS['error']} صيغة خاطئة!\n\n"
                f"الصيغة الصحيحة:\n"
                f"`/setapi YOUR_API_KEY YOUR_API_SECRET`",
                parse_mode='Markdown'
            )
            return
        
        api_key = context.args[0]
        api_secret = context.args[1]
        
        # التحقق من صحة البيانات
        is_valid_key, msg_key = validate_api_key(api_key)
        is_valid_secret, msg_secret = validate_api_secret(api_secret)
        
        if not is_valid_key or not is_valid_secret:
            await update.message.reply_text(
                f"{EMOJIS['error']} {msg_key if not is_valid_key else msg_secret}"
            )
            return
        
        # حفظ البيانات
        db.update_user_api(user_id, api_key, api_secret)
        
        # حذف رسالة المستخدم للأمان
        try:
            await update.message.delete()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{EMOJIS['success']} تم حفظ بيانات API بنجاح!\n\n"
                 f"{EMOJIS['shield']} تم حذف رسالتك للأمان\n\n"
                 f"يمكنك الآن التبديل إلى الحساب الحقيقي من الإعدادات"
        )
    
    @staticmethod
    async def settings_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلومات Webhook"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        
        webhook_url = user_data['webhook_url']
        webhook_token = user_data['webhook_token']
        
        # تنسيق الرسالة
        from config import BASE_WEBHOOK_URL
        full_url = f"{BASE_WEBHOOK_URL}{webhook_url}"
        
        msg = format_webhook_info(full_url, webhook_token)
        
        await query.edit_message_text(
            msg,
            parse_mode='Markdown',
            reply_markup=back_button("menu_settings")
        )
    
    @staticmethod
    async def menu_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة المساعدة"""
        query = update.callback_query
        await query.answer()
        
        help_text = MESSAGES['help'].format(**EMOJIS)
        help_text = help_text.replace("{warning}", EMOJIS['warning'])
        help_text = help_text.replace("{fire}", EMOJIS['fire'])
        
        await query.edit_message_text(
            help_text,
            reply_markup=back_button()
        )
    
    @staticmethod
    async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """العودة للقائمة الرئيسية"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        from config import ADMIN_USER_ID
        is_admin = (user_id == ADMIN_USER_ID)
        
        welcome_msg = format_welcome_message(query.from_user.first_name, False)
        
        await query.edit_message_text(
            welcome_msg,
            reply_markup=main_menu_keyboard(is_admin)
        )

