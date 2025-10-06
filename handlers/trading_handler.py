"""
📈 Trading Handler - معالج التداول
معالجة جميع عمليات التداول والصفقات
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from utils.keyboards import *
from utils.formatters import *
from utils.validators import *
from bybit_api import public_api, BybitAPI
from config import TRADING_CONFIG

logger = logging.getLogger(__name__)


class TradingHandler:
    """معالج عمليات التداول"""
    
    # ==================== القائمة الرئيسية ====================
    
    @staticmethod
    async def menu_trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة التداول"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            f"{EMOJIS['chart_up']} ━━━ التداول ━━━\n\n"
            f"اختر نوع الصفقة:",
            reply_markup=trading_menu_keyboard()
        )
    
    @staticmethod
    async def back_to_trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """العودة لقائمة التداول"""
        await TradingHandler.menu_trading(update, context)
    
    # ==================== بدء صفقة ====================
    
    @staticmethod
    async def trade_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء صفقة شراء"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        context.user_data['trade_action'] = 'buy'
        context.user_data['trade_data'] = {'side': 'buy'}
        
        await query.edit_message_text(
            f"{COLORS['green']} ━━━ صفقة شراء (BUY) ━━━\n\n"
            f"الخطوة 1/4: اختر نوع الصفقة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Spot", callback_data="set_type_spot"),
                    InlineKeyboardButton("🚀 Futures", callback_data="set_type_futures")
                ],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trading")]
            ])
        )
    
    @staticmethod
    async def trade_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء صفقة بيع"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        context.user_data['trade_action'] = 'sell'
        context.user_data['trade_data'] = {'side': 'sell'}
        
        await query.edit_message_text(
            f"{COLORS['red']} ━━━ صفقة بيع (SELL) ━━━\n\n"
            f"الخطوة 1/4: اختر نوع الصفقة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Spot", callback_data="set_type_spot"),
                    InlineKeyboardButton("🚀 Futures", callback_data="set_type_futures")
                ],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_trading")]
            ])
        )
    
    @staticmethod
    async def set_type_spot(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعيين نوع Spot"""
        query = update.callback_query
        await query.answer()
        
        trade_data = context.user_data.get('trade_data', {})
        trade_data['type'] = 'spot'
        trade_data['leverage'] = 1
        context.user_data['trade_data'] = trade_data
        
        await query.edit_message_text(
            f"📊 Spot Trading\n\n"
            f"الخطوة 2/4: اختر الزوج:",
            reply_markup=popular_symbols_keyboard()
        )
    
    @staticmethod
    async def set_type_futures(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعيين نوع Futures"""
        query = update.callback_query
        await query.answer()
        
        trade_data = context.user_data.get('trade_data', {})
        trade_data['type'] = 'futures'
        context.user_data['trade_data'] = trade_data
        
        await query.edit_message_text(
            f"🚀 Futures Trading\n\n"
            f"الخطوة 2/4: اختر الرافعة المالية:",
            reply_markup=leverage_keyboard()
        )
    
    @staticmethod
    async def set_leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تعيين الرافعة المالية"""
        query = update.callback_query
        await query.answer()
        
        # استخراج الرافعة من callback_data
        leverage = int(query.data.split('_')[1])
        
        trade_data = context.user_data.get('trade_data', {})
        trade_data['leverage'] = leverage
        context.user_data['trade_data'] = trade_data
        
        await query.edit_message_text(
            f"✅ الرافعة: {leverage}x\n\n"
            f"الخطوة 3/4: اختر الزوج:",
            reply_markup=popular_symbols_keyboard()
        )
    
    @staticmethod
    async def select_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار الزوج"""
        query = update.callback_query
        await query.answer()
        
        # استخراج الرمز من callback_data
        symbol = query.data.replace('select_symbol_', '')
        
        trade_data = context.user_data.get('trade_data', {})
        trade_data['symbol'] = symbol
        context.user_data['trade_data'] = trade_data
        
        # الحصول على السعر الحالي
        ticker = await public_api.get_ticker(symbol)
        
        msg = f"✅ الزوج: {symbol}\n"
        if ticker:
            msg += f"💹 السعر: {format_price(ticker['price'], 4)}\n"
            context.user_data['current_price'] = ticker['price']
        
        msg += f"\nالخطوة 4/4: أرسل المبلغ بالدولار\n"
        msg += f"الحد الأدنى: {TRADING_CONFIG['min_order_size']}$"
        
        await query.edit_message_text(
            msg,
            reply_markup=back_button("back_to_trading")
        )
    
    @staticmethod
    async def show_all_symbols(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض جميع الأزواج"""
        query = update.callback_query
        await query.answer("جاري التحميل...")
        
        # جلب الأزواج
        symbols = await public_api.get_all_symbols('spot')
        
        await query.edit_message_text(
            f"📋 الأزواج المتاحة ({len(symbols)})\n\n"
            f"اختر زوج:",
            reply_markup=symbol_search_keyboard(symbols, 0)
        )
    
    @staticmethod
    async def process_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة مبلغ الصفقة"""
        if context.user_data.get('trade_action') not in ['buy', 'sell']:
            return
        
        text = update.message.text
        trade_data = context.user_data.get('trade_data', {})
        
        if 'symbol' not in trade_data:
            return
        
        # التحقق من المبلغ
        is_valid, amount, msg = validate_amount(
            text,
            TRADING_CONFIG['min_order_size'],
            TRADING_CONFIG['max_order_size']
        )
        
        if not is_valid:
            await update.message.reply_text(format_error_message(msg))
            return
        
        trade_data['amount'] = amount
        context.user_data['trade_data'] = trade_data
        
        # تأكيد الصفقة
        await TradingHandler.confirm_trade(update, context)
    
    @staticmethod
    async def confirm_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد الصفقة"""
        trade_data = context.user_data.get('trade_data', {})
        current_price = context.user_data.get('current_price', 0)
        
        symbol = trade_data['symbol']
        side = trade_data['side']
        trade_type = trade_data['type']
        amount = trade_data['amount']
        leverage = trade_data.get('leverage', 1)
        
        # حساب الكمية
        quantity = amount / current_price if current_price > 0 else 0
        
        # تنسيق الرسالة
        side_emoji = COLORS['green'] if side == 'buy' else COLORS['red']
        type_emoji = "📊" if trade_type == 'spot' else "🚀"
        
        msg = f"""
{EMOJIS['target']} ━━━ تأكيد الصفقة ━━━

{side_emoji} الاتجاه: {side.upper()}
{type_emoji} النوع: {trade_type.upper()}
💱 الزوج: {symbol}
💰 المبلغ: {format_price(amount)}
"""
        
        if leverage > 1:
            msg += f"📊 الرافعة: {leverage}x\n"
        
        msg += f"""
💹 السعر: {format_price(current_price, 4)}
📦 الكمية: {quantity:.6f}

{EMOJIS['warning']} هل تريد تنفيذ الصفقة؟
"""
        
        await update.message.reply_text(
            msg,
            reply_markup=confirmation_keyboard('execute_trade')
        )
    
    @staticmethod
    async def execute_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنفيذ الصفقة"""
        query = update.callback_query
        await query.answer("جاري التنفيذ...")
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        trade_data = context.user_data.get('trade_data', {})
        current_price = context.user_data.get('current_price', 0)
        
        symbol = trade_data['symbol']
        side = trade_data['side']
        trade_type = trade_data['type']
        amount = trade_data['amount']
        leverage = trade_data.get('leverage', 1)
        
        # حساب الكمية
        quantity = amount / current_price
        
        # التحقق من الرصيد (للحساب التجريبي)
        if user_data['mode'] == 'demo':
            balance = user_data['demo_balance']
            required = amount / leverage if trade_type == 'futures' else amount
            
            if balance < required:
                await query.edit_message_text(
                    format_error_message(f"رصيدك غير كافٍ!\nالمطلوب: {format_price(required)}\nالرصيد: {format_price(balance)}"),
                    reply_markup=back_button("back_to_trading")
                )
                return
            
            # خصم من الرصيد
            new_balance = balance - required
            db.update_demo_balance(user_id, new_balance)
            
            # إنشاء الصفقة
            trade_id = db.create_trade(
                user_id=user_id,
                symbol=symbol,
                trade_type=trade_type,
                side=side,
                entry_price=current_price,
                quantity=quantity,
                leverage=leverage,
                mode='demo'
            )
            
            result_msg = f"""
{EMOJIS['success']} تم فتح الصفقة بنجاح!

{COLORS['green'] if side == 'buy' else COLORS['red']} {symbol} - {side.upper()}
💰 المبلغ: {format_price(amount)}
💹 السعر: {format_price(current_price, 4)}
📦 الكمية: {quantity:.6f}

💳 الرصيد المتبقي: {format_price(new_balance)}

يمكنك متابعة الصفقة من "صفقاتي"
"""
        
        else:  # حساب حقيقي
            # التحقق من API
            if not user_data.get('api_key'):
                await query.edit_message_text(
                    format_error_message("يجب إضافة بيانات API أولاً!"),
                    reply_markup=back_button("back_to_trading")
                )
                return
            
            try:
                # إنشاء API instance
                api = BybitAPI(
                    api_key=user_data['api_key'],
                    api_secret=user_data['api_secret']
                )
                
                # تنفيذ الصفقة
                if trade_type == 'spot':
                    order = await api.create_spot_order(symbol, side, quantity)
                else:  # futures
                    order = await api.create_futures_order(
                        symbol, side, quantity, leverage
                    )
                
                if not order:
                    raise Exception("فشل تنفيذ الأمر")
                
                # حفظ الصفقة
                trade_id = db.create_trade(
                    user_id=user_id,
                    symbol=symbol,
                    trade_type=trade_type,
                    side=side,
                    entry_price=current_price,
                    quantity=quantity,
                    leverage=leverage,
                    mode='real',
                    bybit_order_id=order.get('id')
                )
                
                result_msg = f"""
{EMOJIS['success']} تم فتح الصفقة على Bybit!

{COLORS['green'] if side == 'buy' else COLORS['red']} {symbol} - {side.upper()}
💰 المبلغ: {format_price(amount)}
💹 السعر: {format_price(current_price, 4)}
📦 الكمية: {quantity:.6f}

🆔 Order ID: {order.get('id')}

يمكنك متابعة الصفقة من "صفقاتي"
"""
            
            except Exception as e:
                logger.error(f"Trade execution error: {e}")
                await query.edit_message_text(
                    format_error_message(f"فشل تنفيذ الصفقة: {str(e)}"),
                    reply_markup=back_button("back_to_trading")
                )
                return
        
        await query.edit_message_text(
            result_msg,
            reply_markup=back_button()
        )
        
        # تنظيف الحالة
        context.user_data.pop('trade_action', None)
        context.user_data.pop('trade_data', None)
        context.user_data.pop('current_price', None)
    
    # ==================== إدارة الصفقات ====================
    
    @staticmethod
    async def menu_my_trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض صفقاتي - محسّن بتحديث متوازي"""
        query = update.callback_query
        await query.answer("جاري التحميل...")
        
        try:
            user_id = query.from_user.id
            trades = db.get_open_trades(user_id)
            
            # تحديث الأسعار بشكل متوازي (أسرع)
            if trades:
                # جلب جميع الأسعار دفعة واحدة
                symbols = list(set(trade['symbol'] for trade in trades))
                tickers_dict = await public_api.get_multiple_tickers(symbols)
                
                for trade in trades:
                    ticker = tickers_dict.get(trade['symbol'])
                    if ticker:
                        # حساب الربح/الخسارة
                        from bybit_api import BybitAPI
                        pnl, pnl_percent = BybitAPI().calculate_profit_loss(
                            trade['entry_price'],
                            ticker['price'],
                            trade['quantity'],
                            trade['side'],
                            trade.get('leverage', 1)
                        )
                        
                        # تحديث في قاعدة البيانات
                        db.update_trade_price(
                            trade['trade_id'],
                            ticker['price'],
                            pnl,
                            pnl_percent
                        )
                        
                        # تحديث في القائمة
                        trade['current_price'] = ticker['price']
                        trade['profit_loss'] = pnl
                        trade['profit_loss_percent'] = pnl_percent
            
            trades_msg = format_trades_list(trades)
            
            await query.edit_message_text(
                trades_msg,
                reply_markup=open_trades_keyboard(trades) if trades else back_button()
            )
        except Exception as e:
            logger.error(f"Error in menu_my_trades: {e}")
            await query.edit_message_text(
                format_error_message("حدث خطأ في تحميل الصفقات"),
                reply_markup=back_button()
            )
    
    @staticmethod
    async def view_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض تفاصيل صفقة"""
        query = update.callback_query
        await query.answer()
        
        # استخراج trade_id
        trade_id = query.data.replace('view_trade_', '')
        
        trade = db.get_trade(trade_id)
        if not trade:
            await query.answer("❌ الصفقة غير موجودة", show_alert=True)
            return
        
        # الحصول على السعر الحالي
        ticker = await public_api.get_ticker(trade['symbol'])
        current_price = ticker['price'] if ticker else trade.get('current_price')
        
        # تنسيق الرسالة
        trade_msg = format_trade_info(trade, current_price)
        
        await query.edit_message_text(
            trade_msg,
            reply_markup=trade_actions_keyboard(trade_id)
        )
    
    @staticmethod
    async def close_trade_partial(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إغلاق جزئي للصفقة"""
        query = update.callback_query
        await query.answer()
        
        # استخراج trade_id والنسبة
        parts = query.data.split('_')
        percent = int(parts[1])
        trade_id = parts[2]
        
        await TradingHandler._close_trade(query, context, trade_id, percent)
    
    @staticmethod
    async def close_trade_full(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إغلاق كامل للصفقة"""
        query = update.callback_query
        await query.answer()
        
        trade_id = query.data.replace('close_full_', '')
        
        await TradingHandler._close_trade(query, context, trade_id, 100)
    
    @staticmethod
    async def _close_trade(query, context, trade_id: str, percent: int):
        """منطق إغلاق الصفقة"""
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        trade = db.get_trade(trade_id)
        
        if not trade:
            await query.edit_message_text(
                format_error_message("الصفقة غير موجودة"),
                reply_markup=back_button("menu_my_trades")
            )
            return
        
        # الحصول على السعر الحالي
        ticker = await public_api.get_ticker(trade['symbol'])
        close_price = ticker['price'] if ticker else trade['current_price']
        
        # حساب الربح/الخسارة
        from bybit_api import BybitAPI
        pnl, pnl_percent = BybitAPI().calculate_profit_loss(
            trade['entry_price'],
            close_price,
            trade['quantity'] * (percent / 100),
            trade['side'],
            trade.get('leverage', 1)
        )
        
        # الإغلاق حسب نوع الحساب
        if user_data['mode'] == 'demo':
            # إعادة المبلغ للرصيد
            entry_value = trade['entry_price'] * trade['quantity'] * (percent / 100)
            leverage = trade.get('leverage', 1)
            margin_used = entry_value / leverage if leverage > 1 else entry_value
            
            new_balance = user_data['demo_balance'] + margin_used + pnl
            db.update_demo_balance(user_id, new_balance)
            
            # إغلاق الصفقة
            db.close_trade(trade_id, close_price, pnl, pnl_percent, percent)
            
            # تحديث الإحصائيات
            db.update_statistics(user_id, pnl)
            
            result_msg = f"""
{EMOJIS['success']} تم إغلاق {'الصفقة' if percent == 100 else f'{percent}% من الصفقة'}!

{COLORS['green'] if trade['side'] == 'buy' else COLORS['red']} {trade['symbol']} - {trade['side'].upper()}
💹 سعر الدخول: {format_price(trade['entry_price'], 4)}
💹 سعر الإغلاق: {format_price(close_price, 4)}

{format_profit_loss(pnl, pnl_percent)}

💳 الرصيد الجديد: {format_price(new_balance)}
"""
        
        else:  # حساب حقيقي
            try:
                api = BybitAPI(
                    api_key=user_data['api_key'],
                    api_secret=user_data['api_secret']
                )
                
                close_quantity = trade['quantity'] * (percent / 100)
                
                if trade['trade_type'] == 'spot':
                    order = await api.close_spot_position(
                        trade['symbol'],
                        trade['side'],
                        close_quantity
                    )
                else:  # futures
                    order = await api.close_futures_position(
                        trade['symbol'],
                        trade['side'],
                        close_quantity
                    )
                
                if not order:
                    raise Exception("فشل إغلاق الصفقة")
                
                # تحديث في قاعدة البيانات
                db.close_trade(trade_id, close_price, pnl, pnl_percent, percent)
                db.update_statistics(user_id, pnl)
                
                result_msg = f"""
{EMOJIS['success']} تم إغلاق {'الصفقة' if percent == 100 else f'{percent}% من الصفقة'} على Bybit!

{COLORS['green'] if trade['side'] == 'buy' else COLORS['red']} {trade['symbol']} - {trade['side'].upper()}
💹 سعر الدخول: {format_price(trade['entry_price'], 4)}
💹 سعر الإغلاق: {format_price(close_price, 4)}

{format_profit_loss(pnl, pnl_percent)}

🆔 Order ID: {order.get('id')}
"""
            
            except Exception as e:
                logger.error(f"Close trade error: {e}")
                await query.edit_message_text(
                    format_error_message(f"فشل إغلاق الصفقة: {str(e)}"),
                    reply_markup=back_button("menu_my_trades")
                )
                return
        
        await query.edit_message_text(
            result_msg,
            reply_markup=back_button("menu_my_trades")
        )
    
    @staticmethod
    async def refresh_trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحديث الصفقات"""
        await TradingHandler.menu_my_trades(update, context)
    
    @staticmethod
    async def manage_trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة الصفقات"""
        query = update.callback_query
        await query.answer()
        
        # عرض الصفقات المفتوحة مباشرة
        await TradingHandler.menu_my_trades(update, context)
    
    # ==================== إشارات Nagdat ====================
    
    @staticmethod
    async def menu_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة إشارات Nagdat"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = db.get_user(user_id)
        
        is_subscribed = user_data.get('activated_nagdat', 0) == 1
        
        await query.edit_message_text(
            f"{EMOJIS['signal']} ━━━ إشارات Nagdat ━━━\n\n"
            f"احصل على إشارات احترافية من المطور\n\n"
            f"الحالة: {'مُفعّل ✅' if is_subscribed else 'غير مُفعّل ❌'}",
            reply_markup=nagdat_signals_keyboard(is_subscribed)
        )
    
    @staticmethod
    async def subscribe_nagdat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الاشتراك في إشارات Nagdat"""
        query = update.callback_query
        await query.answer("تم التفعيل! ✅")
        
        user_id = query.from_user.id
        db.subscribe_to_nagdat(user_id)
        
        await query.edit_message_text(
            f"{EMOJIS['success']} تم تفعيل إشارات Nagdat!\n\n"
            f"{EMOJIS['bell']} ستصلك الإشارات فوراً عند إرسالها\n\n"
            f"يمكنك إلغاء الاشتراك في أي وقت",
            reply_markup=back_button("menu_signals")
        )
    
    @staticmethod
    async def unsubscribe_nagdat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء الاشتراك من إشارات Nagdat"""
        query = update.callback_query
        await query.answer("تم الإلغاء")
        
        user_id = query.from_user.id
        db.unsubscribe_from_nagdat(user_id)
        
        await query.edit_message_text(
            f"{EMOJIS['info']} تم إلغاء اشتراكك من إشارات Nagdat\n\n"
            f"يمكنك إعادة التفعيل في أي وقت",
            reply_markup=back_button("menu_signals")
        )

