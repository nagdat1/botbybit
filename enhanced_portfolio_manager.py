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
        
    def sync_positions_with_memory(self) -> bool:
        """مزامنة الصفقات بين الذاكرة وقاعدة البيانات"""
        try:
            logger.info(f"مزامنة الصفقات للمستخدم {self.user_id}...")
            
            # جلب الصفقات من الذاكرة
            memory_positions = user_manager.user_positions.get(self.user_id, {})
            
            # جلب الصفقات من قاعدة البيانات
            db_positions = db_manager.get_user_orders(self.user_id, status='OPEN')
            db_position_ids = {pos.get('order_id') for pos in db_positions if pos.get('order_id')}
            
            # حفظ الصفقات المفقودة في قاعدة البيانات
            synced_count = 0
            for position_id, position_info in memory_positions.items():
                if position_id not in db_position_ids:
                    # صفقة موجودة في الذاكرة ولكن ليست في قاعدة البيانات
                    position_data = {
                        'order_id': position_id,
                        'user_id': self.user_id,
                        'symbol': position_info.get('symbol'),
                        'side': position_info.get('side'),
                        'entry_price': position_info.get('entry_price'),
                        'quantity': position_info.get('position_size', position_info.get('amount', 0)),
                        'market_type': position_info.get('account_type', 'spot'),
                        'exchange': position_info.get('exchange', 'bybit'),
                        'leverage': position_info.get('leverage', 1),
                        'status': 'OPEN',
                        'notes': 'مزامنة تلقائية من الذاكرة'
                    }
                    
                    if 'signal_id' in position_info:
                        position_data['signal_id'] = position_info['signal_id']
                    
                    success = self.add_position(position_data)
                    if success:
                        synced_count += 1
                        logger.info(f"تمت مزامنة الصفقة: {position_id}")
            
            if synced_count > 0:
                logger.info(f"تمت مزامنة {synced_count} صفقة مع قاعدة البيانات")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في مزامنة الصفقات: {e}")
            return False
    
    def get_user_portfolio(self, force_refresh: bool = False) -> Dict[str, Any]:
        """الحصول على محفظة المستخدم الشاملة"""
        try:
            # مزامنة الصفقات أولاً
            self.sync_positions_with_memory()
            
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
        """إضافة صفقة جديدة للمحفظة مع منطق السبوت والفيوتشر"""
        try:
            # إضافة البيانات المطلوبة
            position_data['user_id'] = self.user_id
            position_data['status'] = 'OPEN'
            position_data['open_time'] = datetime.now().isoformat()
            
            # تحديد نوع السوق
            market_type = position_data.get('market_type', 'spot')
            symbol = position_data.get('symbol', '')
            signal_id = position_data.get('signal_id', '')
            side = position_data.get('side', 'buy')
            
            # منطق مختلف حسب نوع السوق
            if market_type == 'spot':
                # في السبوت: معاملة كمحفظة حقيقية
                success = self._handle_spot_position(position_data)
            else:
                # في الفيوتشر: تجميع حسب ID
                success = self._handle_futures_position(position_data)
            
            if success:
                # إعادة تحميل المحفظة
                self.get_user_portfolio(force_refresh=True)
                logger.info(f"تم إضافة صفقة جديدة للمستخدم {self.user_id}: {symbol} ({market_type})")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إضافة صفقة للمستخدم {self.user_id}: {e}")
            return False
    
    def _handle_spot_position(self, position_data: Dict[str, Any]) -> bool:
        """معالجة صفقة السبوت كمحفظة حقيقية موحدة"""
        try:
            symbol = position_data.get('symbol', '')
            side = position_data.get('side', 'buy')
            quantity = position_data.get('quantity', 0)
            entry_price = position_data.get('entry_price', 0)
            
            # إنشاء معرف موحد للعملة (بدون /USDT)
            base_currency = symbol.replace('USDT', '').replace('BTC', '').replace('ETH', '')
            if symbol.endswith('USDT'):
                base_currency = symbol.replace('USDT', '')
            elif symbol.endswith('BTC'):
                base_currency = symbol.replace('BTC', '')
            elif symbol.endswith('ETH'):
                base_currency = symbol.replace('ETH', '')
            else:
                base_currency = symbol.split('/')[0] if '/' in symbol else symbol
            
            # معرف موحد للمركز (مركز واحد لكل عملة)
            unified_position_id = f"SPOT_{base_currency}_spot"
            
            # البحث عن المركز الموحد في قاعدة البيانات
            existing_position = db_manager.get_order(unified_position_id)
            
            if existing_position:
                # تحديث المركز الموجود
                if side.lower() == 'buy':
                    # شراء: إضافة كمية وحساب متوسط السعر المرجح
                    old_quantity = existing_position.get('quantity', 0)
                    old_price = existing_position.get('entry_price', 0)
                    new_quantity = old_quantity + quantity
                    
                    # حساب متوسط السعر المرجح
                    total_value = (old_quantity * old_price) + (quantity * entry_price)
                    new_average_price = total_value / new_quantity
                    
                    # تحديث المركز الموحد
                    updates = {
                        'quantity': new_quantity,
                        'entry_price': new_average_price,
                        'last_update': datetime.now().isoformat()
                    }
                    success = db_manager.update_order(unified_position_id, updates)
                    
                    logger.info(f" تم تحديث المركز الموحد {unified_position_id}: كمية جديدة={new_quantity}, متوسط السعر={new_average_price:.6f}")
                    
                else:  # sell
                    # بيع: تقليل كمية وحساب الربح
                    old_quantity = existing_position.get('quantity', 0)
                    if old_quantity >= quantity:
                        new_quantity = old_quantity - quantity
                        
                        # حساب الربح من البيع
                        profit_usdt = (entry_price - existing_position.get('entry_price', 0)) * quantity
                        
                        if new_quantity > 0:
                            # تحديث الكمية المتبقية
                            updates = {
                                'quantity': new_quantity,
                                'last_update': datetime.now().isoformat()
                            }
                            success = db_manager.update_order(unified_position_id, updates)
                            logger.info(f" تم تقليل كمية المركز الموحد {unified_position_id}: كمية جديدة={new_quantity}, ربح البيع={profit_usdt:.2f} USDT")
                        else:
                            # إغلاق المركز بالكامل
                            success = db_manager.close_order(unified_position_id, entry_price, profit_usdt)
                            logger.info(f" تم إغلاق المركز الموحد {unified_position_id} بالكامل، ربح إجمالي={profit_usdt:.2f} USDT")
                    else:
                        logger.warning(f" كمية البيع {quantity} أكبر من الكمية المتاحة {old_quantity}")
                        return False
            else:
                # إنشاء مركز جديد للعملة
                if side.lower() == 'buy':
                    # تحديث معرف المركز الموحد
                    position_data['order_id'] = unified_position_id
                    position_data['base_currency'] = base_currency
                    position_data['market_type'] = 'spot'
                    
                    success = db_manager.create_comprehensive_position(position_data)
                    logger.info(f" تم إنشاء مركز موحد جديد {unified_position_id}: كمية={quantity}, سعر={entry_price:.6f}")
                else:
                    logger.warning(f" محاولة بيع {symbol} بدون رصيد متاح")
                    return False
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في معالجة صفقة السبوت الموحدة: {e}")
            return False
    
    def _handle_futures_position(self, position_data: Dict[str, Any]) -> bool:
        """معالجة صفقة الفيوتشر مع تجميع حسب ID"""
        try:
            symbol = position_data.get('symbol', '')
            side = position_data.get('side', 'buy')
            quantity = position_data.get('quantity', 0)
            entry_price = position_data.get('entry_price', 0)
            signal_id = position_data.get('signal_id', '')
            
            # إنشاء ID عشوائي إذا لم يكن موجوداً
            if not signal_id:
                signal_id = self._generate_random_id(symbol)
                position_data['signal_id'] = signal_id
                logger.info(f"تم إنشاء ID عشوائي: {signal_id}")
            
            # البحث عن صفقة موجودة بنفس ID
            existing_position = db_manager.get_position_by_signal_id(signal_id, self.user_id, symbol)
            
            if existing_position:
                # تجميع الصفقات بنفس ID
                if side.lower() == 'buy' and existing_position['side'].lower() == 'buy':
                    # تعزيز Long
                    new_quantity = existing_position['quantity'] + quantity
                    # حساب متوسط السعر المرجح
                    total_value = (existing_position['quantity'] * existing_position['entry_price']) + (quantity * entry_price)
                    new_average_price = total_value / new_quantity
                    
                    # تحديث الصفقة الموجودة
                    updates = {
                        'quantity': new_quantity,
                        'entry_price': new_average_price,
                        'last_update': datetime.now().isoformat()
                    }
                    success = db_manager.update_signal_position(signal_id, self.user_id, symbol, updates)
                    
                elif side.lower() == 'sell' and existing_position['side'].lower() == 'sell':
                    # تعزيز Short
                    new_quantity = existing_position['quantity'] + quantity
                    # حساب متوسط السعر المرجح
                    total_value = (existing_position['quantity'] * existing_position['entry_price']) + (quantity * entry_price)
                    new_average_price = total_value / new_quantity
                    
                    # تحديث الصفقة الموجودة
                    updates = {
                        'quantity': new_quantity,
                        'entry_price': new_average_price,
                        'last_update': datetime.now().isoformat()
                    }
                    success = db_manager.update_signal_position(signal_id, self.user_id, symbol, updates)
                    
                else:
                    # اتجاه معاكس - إنشاء صفقة منفصلة
                    position_data['order_id'] = f"FUTURES_{symbol}_{signal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    success = db_manager.create_comprehensive_position(position_data)
                    
            else:
                # صفقة جديدة
                position_data['order_id'] = f"FUTURES_{symbol}_{signal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                success = db_manager.create_comprehensive_position(position_data)
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في معالجة صفقة الفيوتشر: {e}")
            return False
    
    def _generate_random_id(self, symbol: str) -> str:
        """إنشاء ID عشوائي للصفقة"""
        import random
        import string
        
        # صيغة: SYMBOL-YYYYMMDD-HHMMSS-RAND4
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{symbol}-{timestamp}-{random_part}"
    
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
    
    def get_all_user_positions_unified(self, account_type: str = 'demo') -> List[Dict]:
        """جمع جميع الصفقات من جميع المصادر بشكل موحد"""
        try:
            logger.info(f"جمع جميع الصفقات للمستخدم {self.user_id} - نوع الحساب: {account_type}")
            
            all_positions = []
            position_ids_seen = set()
            
            if account_type == 'demo':
                # 1. من الذاكرة (user_manager.user_positions)
                logger.info(f" DEBUG: user_manager.user_positions = {user_manager.user_positions}")
                logger.info(f" DEBUG: self.user_id = {self.user_id}")
                logger.info(f" DEBUG: type(self.user_id) = {type(self.user_id)}")
                
                memory_positions = user_manager.user_positions.get(self.user_id, {})
                logger.info(f" DEBUG: memory_positions للمستخدم {self.user_id} = {memory_positions}")
                logger.info(f" DEBUG: type(memory_positions) = {type(memory_positions)}")
                logger.info(f"صفقات من الذاكرة: {len(memory_positions)}")
                
                # فحص مفصل لكل صفقة
                for pos_id, pos_info in memory_positions.items():
                    logger.info(f" DEBUG: صفقة {pos_id} = {pos_info}")
                    logger.info(f" DEBUG: account_type في الصفقة = {pos_info.get('account_type')}")
                    logger.info(f" DEBUG: market_type في الصفقة = {pos_info.get('market_type')}")
                
                for position_id, position_info in memory_positions.items():
                    if position_id not in position_ids_seen:
                        all_positions.append({
                            'order_id': position_id,
                            'symbol': position_info.get('symbol'),
                            'side': position_info.get('side'),
                            'entry_price': position_info.get('entry_price'),
                            'quantity': position_info.get('position_size', position_info.get('amount', 0)),
                            'market_type': position_info.get('account_type', 'spot'),
                            'exchange': position_info.get('exchange', 'bybit'),
                            'leverage': position_info.get('leverage', 1),
                            'current_price': position_info.get('current_price', position_info.get('entry_price')),
                            'pnl_percent': position_info.get('pnl_percent', 0),
                            'status': 'OPEN',
                            'source': 'memory'
                        })
                        position_ids_seen.add(position_id)
                
                # 2. من قاعدة البيانات (للتأكد)
                db_positions = db_manager.get_user_orders(self.user_id, status='OPEN')
                logger.info(f"صفقات من قاعدة البيانات: {len(db_positions)}")
                
                for pos in db_positions:
                    position_id = pos.get('order_id')
                    if position_id and position_id not in position_ids_seen:
                        all_positions.append({
                            **pos,
                            'source': 'database'
                        })
                        position_ids_seen.add(position_id)
                
            else:  # real account
                # 1. من المنصة (مصدر الحقيقة)
                try:
                    from real_account_manager import real_account_manager
                    real_account = real_account_manager.get_account(self.user_id)
                    
                    if real_account:
                        user_data = user_manager.get_user(self.user_id)
                        market_type = user_data.get('market_type', 'spot') if user_data else 'spot'
                        
                        if hasattr(real_account, 'get_open_positions'):
                            category = "linear" if market_type == 'futures' else "spot"
                            platform_positions = real_account.get_open_positions(category)
                            logger.info(f"صفقات من المنصة: {len(platform_positions)}")
                            
                            for idx, pos in enumerate(platform_positions):
                                position_id = f"real_{pos.get('symbol')}_{idx}"
                                if position_id not in position_ids_seen:
                                    all_positions.append({
                                        'order_id': position_id,
                                        'symbol': pos.get('symbol'),
                                        'side': pos.get('side', 'Buy').lower(),
                                        'entry_price': float(pos.get('entry_price', pos.get('avgPrice', 0))),
                                        'quantity': float(pos.get('size', 0)),
                                        'market_type': market_type,
                                        'exchange': user_data.get('exchange', 'bybit') if user_data else 'bybit',
                                        'leverage': int(pos.get('leverage', 1)),
                                        'current_price': float(pos.get('mark_price', pos.get('markPrice', 0))),
                                        'pnl_percent': float(pos.get('unrealized_pnl', 0)),
                                        'status': 'OPEN',
                                        'source': 'platform',
                                        'is_real': True
                                    })
                                    position_ids_seen.add(position_id)
                except Exception as e:
                    logger.error(f"خطأ في جلب الصفقات من المنصة: {e}")
                
                # 2. من قاعدة البيانات المحلية (للمتابعة)
                db_positions = db_manager.get_user_orders(self.user_id, status='OPEN')
                logger.info(f"صفقات من قاعدة البيانات المحلية: {len(db_positions)}")
                
                for pos in db_positions:
                    position_id = pos.get('order_id')
                    if position_id and position_id not in position_ids_seen:
                        all_positions.append({
                            **pos,
                            'source': 'database_local'
                        })
                        position_ids_seen.add(position_id)
            
            logger.info(f"إجمالي الصفقات الفريدة: {len(all_positions)}")
            return all_positions
            
        except Exception as e:
            logger.error(f"خطأ في جمع الصفقات: {e}")
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
 **ملخص المحفظة**

 **القيمة الإجمالية:** ${summary.get('portfolio_value', 0):,.2f}
 **الربح/الخسارة:** ${stats.get('total_pnl', 0):,.2f}
 **معدل الفوز:** {summary.get('win_rate', 0):.1f}%

 **الصفقات:**
• الصفقات المفتوحة: {summary.get('total_open_positions', 0)}
• الصفقات المغلقة: {summary.get('total_closed_positions', 0)}
• الرموز المتداولة: {summary.get('total_symbols', 0)}

⏰ **آخر تحديث:** {portfolio.get('last_updated', 'غير متاح')}
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملخص المحفظة: {e}")
            return f" خطأ في تحميل المحفظة: {e}"

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

