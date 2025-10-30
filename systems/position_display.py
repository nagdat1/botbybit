#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة عرض الصفقات المفتوحة - تصميم شبيه بـ Binance
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class PositionDisplayFormatter:
    """تنسيق عرض الصفقات بشكل احترافي"""
    
    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """تنسيق الأرقام بفواصل"""
        try:
            return f"{number:,.{decimals}f}"
        except:
            return str(number)
    
    @staticmethod
    def format_price(price: float, symbol: str = "") -> str:
        """تنسيق السعر حسب الرمز"""
        try:
            # تحديد عدد المنازل حسب السعر
            if price >= 1000:
                return f"{price:,.2f}"
            elif price >= 1:
                return f"{price:,.4f}"
            else:
                return f"{price:,.6f}"
        except:
            return str(price)
    
    @staticmethod
    def get_pnl_indicator(pnl_value: float) -> str:
        """الحصول على مؤشر الربح/الخسارة"""
        if pnl_value > 0:
            return "🟢"
        elif pnl_value < 0:
            return "🔴"
        else:
            return "⚪"
    
    @staticmethod
    def get_direction_arrow(pnl_percent: float) -> str:
        """الحصول على سهم الاتجاه"""
        if pnl_percent > 0:
            return "⬆️"
        elif pnl_percent < 0:
            return "⬇️"
        else:
            return "➡️"
    
    @staticmethod
    def format_spot_position(position_id: str, position_info: Dict) -> str:
        """تنسيق عرض صفقة Spot"""
        try:
            symbol = position_info.get('symbol', 'UNKNOWN')
            side = position_info.get('side', 'BUY').upper()
            signal_id = position_info.get('signal_id', '')
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', 0)
            quantity = position_info.get('quantity', 0)
            amount = quantity * entry_price
            pnl_value = position_info.get('pnl_value', 0)
            pnl_percent = position_info.get('pnl_percent', 0)
            
            # المؤشرات
            pnl_indicator = PositionDisplayFormatter.get_pnl_indicator(pnl_value)
            direction_arrow = PositionDisplayFormatter.get_direction_arrow(pnl_percent)
            
            # العنوان
            header = f"{pnl_indicator} {symbol} • {side}"
            if signal_id:
                header += f" • 📊 {signal_id}"
            
            # السعر
            price_change_percent = 0
            if entry_price > 0:
                price_change_percent = ((current_price - entry_price) / entry_price) * 100
            
            price_line = f"Entry: {PositionDisplayFormatter.format_price(entry_price)} → Mark: {PositionDisplayFormatter.format_price(current_price)} ({direction_arrow} {price_change_percent:+.2f}%)"
            
            # الحجم
            size_line = f"Size: {PositionDisplayFormatter.format_number(quantity, 4)} • Amount: {PositionDisplayFormatter.format_number(amount, 2)} USDT"
            
            # PnL
            pnl_line = f"P&L: {pnl_value:+,.2f} USDT ({pnl_percent:+.2f}%) {pnl_indicator}"
            
            # التجميع
            formatted = f"{header}\n{price_line}\n{size_line}\n{pnl_line}"
            
            return formatted
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق صفقة Spot: {e}")
            return f"خطأ في عرض الصفقة {position_id}"
    
    @staticmethod
    def format_futures_position(position_id: str, position_info: Dict) -> str:
        """تنسيق عرض صفقة Futures"""
        try:
            symbol = position_info.get('symbol', 'UNKNOWN')
            side = position_info.get('side', 'Buy').upper()
            if side == 'BUY':
                side = 'LONG'
            elif side == 'SELL':
                side = 'SHORT'
            
            signal_id = position_info.get('signal_id', '')
            entry_price = position_info.get('entry_price', 0)
            current_price = position_info.get('current_price', 0)
            quantity = position_info.get('quantity', 0)
            leverage = position_info.get('leverage', 1)
            margin_amount = position_info.get('margin_amount', 0)
            liquidation_price = position_info.get('liquidation_price', 0)
            pnl_value = position_info.get('pnl_value', 0)
            pnl_percent = position_info.get('pnl_percent', 0)
            
            # المؤشرات
            pnl_indicator = PositionDisplayFormatter.get_pnl_indicator(pnl_value)
            direction_arrow = PositionDisplayFormatter.get_direction_arrow(pnl_percent)
            
            # العنوان
            header = f"{pnl_indicator} {symbol} • {side}"
            if signal_id:
                header += f" • 📊 {signal_id}"
            
            # السعر
            price_change_percent = 0
            if entry_price > 0:
                price_change_percent = ((current_price - entry_price) / entry_price) * 100
            
            price_line = f"Entry: {PositionDisplayFormatter.format_price(entry_price)} → Mark: {PositionDisplayFormatter.format_price(current_price)} ({direction_arrow} {price_change_percent:+.2f}%)"
            
            # الحجم والرافعة
            size_line = f"Size: {PositionDisplayFormatter.format_number(quantity, 4)} • Margin: {PositionDisplayFormatter.format_number(margin_amount, 2)} • {leverage}x"
            
            # التصفية
            liq_distance = 0
            if current_price > 0 and liquidation_price > 0:
                if side == 'LONG':
                    liq_distance = ((current_price - liquidation_price) / current_price) * 100
                else:
                    liq_distance = ((liquidation_price - current_price) / current_price) * 100
            
            liq_warning = ""
            if liq_distance <= 1.5 and liq_distance > 0:
                liq_warning = " ⚠️ قريب من التصفية!"
            elif liq_distance < 0:
                liq_warning = " 🚨 خطر تصفية!"
            
            liq_line = f"Liq: {PositionDisplayFormatter.format_price(liquidation_price)} ({liq_distance:.2f}% away){liq_warning}"
            
            # PnL
            pnl_line = f"P&L: {pnl_value:+,.2f} USDT ({pnl_percent:+.2f}%) {pnl_indicator}"
            
            # التجميع
            formatted = f"{header}\n{price_line}\n{size_line}\n{liq_line}\n{pnl_line}"
            
            return formatted
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق صفقة Futures: {e}")
            return f"خطأ في عرض الصفقة {position_id}"
    
    @staticmethod
    def create_position_keyboard(position_id: str, position_info: Dict, compact: bool = False) -> List[List[InlineKeyboardButton]]:
        """إنشاء لوحة المفاتيح لإدارة الصفقة"""
        try:
            market_type = position_info.get('market_type', 'spot')
            pnl_value = position_info.get('pnl_value', 0)
            
            keyboard = []
            
            # الصف الأول: إدارة وإغلاق
            pnl_display = f"({pnl_value:+.2f})" if pnl_value != 0 else ""
            
            row1 = [
                InlineKeyboardButton(f"⚙️ إدارة", callback_data=f"manage_{position_id}"),
                InlineKeyboardButton(f"❌ إغلاق {pnl_display}", callback_data=f"close_{position_id}")
            ]
            keyboard.append(row1)
            
            # الصف الثاني: إغلاق جزئي للفيوتشر
            if market_type == 'futures' and not compact:
                row2 = [
                    InlineKeyboardButton("📊 25%", callback_data=f"partial_25_{position_id}"),
                    InlineKeyboardButton("📊 50%", callback_data=f"partial_50_{position_id}"),
                    InlineKeyboardButton("📊 75%", callback_data=f"partial_75_{position_id}")
                ]
                keyboard.append(row2)
            
            return keyboard
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء لوحة المفاتيح: {e}")
            return []


class PositionDisplayManager:
    """مدير عرض الصفقات المفتوحة"""
    
    def __init__(self):
        self.formatter = PositionDisplayFormatter()
    
    def format_spot_positions_message(self, spot_positions: Dict, account_type: str = "demo") -> tuple:
        """تنسيق رسالة صفقات Spot"""
        try:
            if not spot_positions:
                message = "📊 SPOT POSITIONS (0)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔄 لا توجد صفقات سبوت مفتوحة حالياً"
                return message, None
            
            # حساب إجمالي PnL
            total_pnl = sum(pos.get('pnl_value', 0) for pos in spot_positions.values())
            total_pnl_indicator = self.formatter.get_pnl_indicator(total_pnl)
            
            # العنوان
            account_indicator = "💼 حساب حقيقي" if account_type == "real" else "🎮 حساب تجريبي"
            header = f"{account_indicator}\n📊 SPOT POSITIONS ({len(spot_positions)})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            message = header
            keyboard = []
            
            # عرض كل صفقة
            for position_id, position_info in spot_positions.items():
                # تنسيق الصفقة
                position_text = self.formatter.format_spot_position(position_id, position_info)
                message += f"┌─────────────────────────────────┐\n{position_text}\n└─────────────────────────────────┘\n\n"
                
                # إضافة أزرار الصفقة
                position_keyboard = self.formatter.create_position_keyboard(position_id, position_info, compact=True)
                keyboard.extend(position_keyboard)
            
            # إجمالي PnL
            message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTotal P&L: {total_pnl:+,.2f} USDT {total_pnl_indicator}"
            
            # أزرار التحكم
            control_row = [
                InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions"),
                InlineKeyboardButton("📊 ملخص", callback_data="positions_summary")
            ]
            keyboard.append(control_row)
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            return message, reply_markup
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة صفقات Spot: {e}")
            return "خطأ في عرض الصفقات", None
    
    def format_futures_positions_message(self, futures_positions: Dict, account_type: str = "demo") -> tuple:
        """تنسيق رسالة صفقات Futures"""
        try:
            if not futures_positions:
                message = "📊 FUTURES POSITIONS (0)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔄 لا توجد صفقات فيوتشر مفتوحة حالياً"
                return message, None
            
            # حساب إجمالي PnL
            total_pnl = sum(pos.get('pnl_value', 0) for pos in futures_positions.values())
            total_pnl_indicator = self.formatter.get_pnl_indicator(total_pnl)
            
            # العنوان
            account_indicator = "💼 حساب حقيقي" if account_type == "real" else "🎮 حساب تجريبي"
            header = f"{account_indicator}\n📊 FUTURES POSITIONS ({len(futures_positions)})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            message = header
            keyboard = []
            
            # عرض كل صفقة
            for position_id, position_info in futures_positions.items():
                # تنسيق الصفقة
                position_text = self.formatter.format_futures_position(position_id, position_info)
                message += f"┌───────────────────────────────────┐\n{position_text}\n└───────────────────────────────────┘\n\n"
                
                # إضافة أزرار الصفقة
                position_keyboard = self.formatter.create_position_keyboard(position_id, position_info, compact=False)
                keyboard.extend(position_keyboard)
            
            # إجمالي PnL
            message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTotal P&L: {total_pnl:+,.2f} USDT {total_pnl_indicator}"
            
            # أزرار التحكم
            control_row = [
                InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions"),
                InlineKeyboardButton("📊 ملخص", callback_data="positions_summary")
            ]
            keyboard.append(control_row)
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            return message, reply_markup
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة صفقات Futures: {e}")
            return "خطأ في عرض الصفقات", None
    
    def format_all_positions_message(self, spot_positions: Dict, futures_positions: Dict, account_type: str = "demo") -> tuple:
        """تنسيق رسالة جميع الصفقات (Spot + Futures)"""
        try:
            # إذا لم تكن هناك صفقات
            if not spot_positions and not futures_positions:
                message = "📊 OPEN POSITIONS (0)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔄 لا توجد صفقات مفتوحة حالياً"
                return message, None
            
            # العنوان
            account_indicator = "💼 حساب حقيقي" if account_type == "real" else "🎮 حساب تجريبي"
            total_count = len(spot_positions) + len(futures_positions)
            header = f"{account_indicator}\n📊 OPEN POSITIONS ({total_count})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            message = header
            keyboard = []
            
            # صفقات Spot
            if spot_positions:
                message += f"💱 SPOT ({len(spot_positions)})\n"
                for position_id, position_info in spot_positions.items():
                    position_text = self.formatter.format_spot_position(position_id, position_info)
                    message += f"┌─────────────────────────────────┐\n{position_text}\n└─────────────────────────────────┘\n\n"
                    
                    position_keyboard = self.formatter.create_position_keyboard(position_id, position_info, compact=True)
                    keyboard.extend(position_keyboard)
            
            # صفقات Futures
            if futures_positions:
                message += f"\n⚡ FUTURES ({len(futures_positions)})\n"
                for position_id, position_info in futures_positions.items():
                    position_text = self.formatter.format_futures_position(position_id, position_info)
                    message += f"┌───────────────────────────────────┐\n{position_text}\n└───────────────────────────────────┘\n\n"
                    
                    position_keyboard = self.formatter.create_position_keyboard(position_id, position_info, compact=False)
                    keyboard.extend(position_keyboard)
            
            # إجمالي PnL
            total_pnl = sum(pos.get('pnl_value', 0) for pos in spot_positions.values())
            total_pnl += sum(pos.get('pnl_value', 0) for pos in futures_positions.values())
            total_pnl_indicator = self.formatter.get_pnl_indicator(total_pnl)
            
            message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTotal P&L: {total_pnl:+,.2f} USDT {total_pnl_indicator}"
            
            # أزرار التحكم
            control_row = [
                InlineKeyboardButton("🔄 تحديث", callback_data="refresh_positions"),
                InlineKeyboardButton("📊 ملخص", callback_data="positions_summary")
            ]
            keyboard.append(control_row)
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            return message, reply_markup
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة جميع الصفقات: {e}")
            return "خطأ في عرض الصفقات", None


# دالة مساعدة
def create_position_display_manager():
    """إنشاء مثيل من مدير العرض"""
    return PositionDisplayManager()

