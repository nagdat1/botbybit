#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المحفظة المحسن - إدارة شاملة للصفقات والمحفظة
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from database import db_manager
from user_manager import user_manager

logger = logging.getLogger(__name__)

class EnhancedPortfolioManager:
    """مدير المحفظة المحسن"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.portfolio_cache = {}
        self.last_update = None
        
    def get_user_portfolio(self, force_refresh: bool = False) -> Dict[str, Any]:
        """الحصول على محفظة المستخدم الشاملة"""
        try:
            # التحقق من التخزين المؤقت
            if not force_refresh and self.portfolio_cache and self.last_update:
                time_diff = datetime.now() - self.last_update
                if time_diff.total_seconds() < 30:  # 30 ثانية
                    return self.portfolio_cache
            
            # جلب البيانات من قاعدة البيانات
            portfolio_summary = db_manager.get_user_portfolio_summary(self.user_id)
            all_positions = db_manager.get_all_user_positions(self.user_id)
            
            # تحليل الصفقات المفتوحة
            open_positions = []
            closed_positions = []
            portfolio_stats = {
                'total_value': 0.0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'successful_trades': 0
            }
            
            for position in all_positions:
                if position.get('status') == 'OPEN':
                    open_positions.append(position)
                    # حساب القيمة الإجمالية
                    if 'entry_price' in position and 'quantity' in position:
                        portfolio_stats['total_value'] += position['entry_price'] * position['quantity']
                else:
                    closed_positions.append(position)
                    portfolio_stats['total_trades'] += 1
                    # حساب معدل الفوز (مبسط)
                    if position.get('pnl', 0) > 0:
                        portfolio_stats['successful_trades'] += 1
            
            # حساب معدل الفوز
            if portfolio_stats['total_trades'] > 0:
                portfolio_stats['win_rate'] = (portfolio_stats['successful_trades'] / portfolio_stats['total_trades']) * 100
            
            # تجميع الصفقات حسب الرمز
            positions_by_symbol = {}
            for position in open_positions:
                symbol = position.get('symbol', 'UNKNOWN')
                if symbol not in positions_by_symbol:
                    positions_by_symbol[symbol] = {
                        'symbol': symbol,
                        'total_quantity': 0,
                        'average_price': 0,
                        'total_value': 0,
                        'positions': []
                    }
                
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                
                positions_by_symbol[symbol]['total_quantity'] += quantity
                positions_by_symbol[symbol]['total_value'] += quantity * entry_price
                positions_by_symbol[symbol]['positions'].append(position)
            
            # حساب متوسط السعر لكل رمز
            for symbol_data in positions_by_symbol.values():
                if symbol_data['total_quantity'] > 0:
                    symbol_data['average_price'] = symbol_data['total_value'] / symbol_data['total_quantity']
            
            # إعداد البيانات النهائية
            portfolio_data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'portfolio_stats': portfolio_stats,
                'open_positions': open_positions,
                'closed_positions': closed_positions[:10],  # آخر 10 صفقات مغلقة
                'positions_by_symbol': list(positions_by_symbol.values()),
                'summary': {
                    'total_open_positions': len(open_positions),
                    'total_closed_positions': len(closed_positions),
                    'total_symbols': len(positions_by_symbol),
                    'portfolio_value': portfolio_stats['total_value'],
                    'win_rate': portfolio_stats['win_rate']
                }
            }
            
            # تحديث التخزين المؤقت
            self.portfolio_cache = portfolio_data
            self.last_update = datetime.now()
            
            logger.info(f"تم تحديث محفظة المستخدم {self.user_id}: {len(open_positions)} صفقات مفتوحة")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على محفظة المستخدم {self.user_id}: {e}")
            return {
                'user_id': self.user_id,
                'error': str(e),
                'portfolio_stats': {'total_value': 0, 'total_pnl': 0, 'win_rate': 0},
                'open_positions': [],
                'closed_positions': [],
                'positions_by_symbol': [],
                'summary': {'total_open_positions': 0, 'total_closed_positions': 0}
            }
    
    def add_position(self, position_data: Dict[str, Any]) -> bool:
        """إضافة صفقة جديدة للمحفظة"""
        try:
            # إضافة البيانات المطلوبة
            position_data['user_id'] = self.user_id
            position_data['status'] = 'OPEN'
            position_data['open_time'] = datetime.now().isoformat()
            
            # حفظ الصفقة
            success = db_manager.create_comprehensive_position(position_data)
            
            if success:
                # إعادة تحميل المحفظة
                self.get_user_portfolio(force_refresh=True)
                logger.info(f"تم إضافة صفقة جديدة للمستخدم {self.user_id}: {position_data.get('symbol')}")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إضافة صفقة للمستخدم {self.user_id}: {e}")
            return False
    
    def close_position(self, order_id: str, close_price: float = None) -> bool:
        """إغلاق صفقة"""
        try:
            success = db_manager.update_position_status(order_id, 'CLOSED', close_price)
            
            if success:
                # إعادة تحميل المحفظة
                self.get_user_portfolio(force_refresh=True)
                logger.info(f"تم إغلاق صفقة {order_id} للمستخدم {self.user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق صفقة {order_id}: {e}")
            return False
    
    def update_position(self, order_id: str, updates: Dict[str, Any]) -> bool:
        """تحديث صفقة موجودة"""
        try:
            success = db_manager.update_order(order_id, updates)
            
            if success:
                # إعادة تحميل المحفظة
                self.get_user_portfolio(force_refresh=True)
                logger.info(f"تم تحديث صفقة {order_id} للمستخدم {self.user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث صفقة {order_id}: {e}")
            return False
    
    def get_position_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على صفقة محددة"""
        try:
            position = db_manager.get_order(order_id)
            return position
        except Exception as e:
            logger.error(f"خطأ في الحصول على صفقة {order_id}: {e}")
            return None
    
    def get_positions_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """الحصول على جميع صفقات رمز معين"""
        try:
            portfolio = self.get_user_portfolio()
            symbol_positions = []
            
            for position in portfolio.get('open_positions', []):
                if position.get('symbol') == symbol:
                    symbol_positions.append(position)
            
            return symbol_positions
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على صفقات الرمز {symbol}: {e}")
            return []
    
    def calculate_portfolio_pnl(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """حساب الربح/الخسارة للمحفظة"""
        try:
            portfolio = self.get_user_portfolio()
            total_pnl = 0.0
            positions_pnl = []
            
            for position in portfolio.get('open_positions', []):
                symbol = position.get('symbol')
                entry_price = position.get('entry_price', 0)
                quantity = position.get('quantity', 0)
                side = position.get('side', 'buy')
                
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    
                    if side.lower() == 'buy':
                        pnl = (current_price - entry_price) * quantity
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                    else:
                        pnl = (entry_price - current_price) * quantity
                        pnl_percent = ((entry_price - current_price) / entry_price) * 100
                    
                    position_pnl = {
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'quantity': quantity,
                        'pnl': pnl,
                        'pnl_percent': pnl_percent
                    }
                    
                    positions_pnl.append(position_pnl)
                    total_pnl += pnl
            
            return {
                'total_pnl': total_pnl,
                'positions_pnl': positions_pnl,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب الربح/الخسارة: {e}")
            return {'total_pnl': 0, 'positions_pnl': [], 'error': str(e)}
    
    def get_portfolio_summary_for_display(self) -> str:
        """الحصول على ملخص المحفظة للعرض"""
        try:
            portfolio = self.get_user_portfolio()
            summary = portfolio.get('summary', {})
            stats = portfolio.get('portfolio_stats', {})
            
            message = f"""
📊 **ملخص المحفظة**

💰 **القيمة الإجمالية:** ${summary.get('portfolio_value', 0):,.2f}
📈 **الربح/الخسارة:** ${stats.get('total_pnl', 0):,.2f}
🎯 **معدل الفوز:** {summary.get('win_rate', 0):.1f}%

📋 **الصفقات:**
• الصفقات المفتوحة: {summary.get('total_open_positions', 0)}
• الصفقات المغلقة: {summary.get('total_closed_positions', 0)}
• الرموز المتداولة: {summary.get('total_symbols', 0)}

⏰ **آخر تحديث:** {portfolio.get('last_updated', 'غير متاح')}
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملخص المحفظة: {e}")
            return f"❌ خطأ في تحميل المحفظة: {e}"

# مدير عام للمحافظ
class PortfolioManagerFactory:
    """مصنع مديري المحافظ"""
    
    def __init__(self):
        self.portfolio_managers: Dict[int, EnhancedPortfolioManager] = {}
    
    def get_portfolio_manager(self, user_id: int) -> EnhancedPortfolioManager:
        """الحصول على مدير المحفظة للمستخدم"""
        if user_id not in self.portfolio_managers:
            self.portfolio_managers[user_id] = EnhancedPortfolioManager(user_id)
        return self.portfolio_managers[user_id]
    
    def clear_cache(self, user_id: int = None):
        """مسح التخزين المؤقت"""
        if user_id:
            if user_id in self.portfolio_managers:
                self.portfolio_managers[user_id].portfolio_cache = {}
                self.portfolio_managers[user_id].last_update = None
        else:
            for manager in self.portfolio_managers.values():
                manager.portfolio_cache = {}
                manager.last_update = None

# مثيل عام
portfolio_factory = PortfolioManagerFactory()
