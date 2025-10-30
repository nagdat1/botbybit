#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام جلب الصفقات المفتوحة - دعم الحسابات الحقيقية والتجريبية
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class PositionFetcher:
    """جلب الصفقات المفتوحة من مصادر مختلفة"""
    
    def __init__(self, db_manager, signal_id_manager):
        self.db_manager = db_manager
        self.signal_id_manager = signal_id_manager
        self.last_fetch_time = {}
        self.debounce_seconds = 2  # تأخير بين التحديثات
        
    def _should_fetch(self, user_id: int) -> bool:
        """التحقق من إمكانية الجلب (debounce)"""
        current_time = time.time()
        last_time = self.last_fetch_time.get(user_id, 0)
        
        if current_time - last_time >= self.debounce_seconds:
            self.last_fetch_time[user_id] = current_time
            return True
        
        logger.debug(f"Debounce: تم منع طلب التحديث للمستخدم {user_id}")
        return False
    
    def get_demo_positions(self, user_id: int, market_type: str = None) -> Dict[str, Any]:
        """جلب الصفقات التجريبية من قاعدة البيانات"""
        try:
            logger.info(f"📊 جلب الصفقات التجريبية للمستخدم {user_id}")
            
            # جلب الصفقات المفتوحة من قاعدة البيانات
            filters = {
                'status': 'OPEN',
                'account_type': 'demo'
            }
            
            if market_type:
                filters['market_type'] = market_type
            
            orders = self.db_manager.get_user_trade_history(user_id, filters)
            
            positions = {}
            for order in orders:
                position_id = order['order_id']
                
                # إنشاء معلومات الصفقة
                position_info = {
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'entry_price': order['entry_price'],
                    'quantity': order['quantity'],
                    'market_type': order.get('market_type', 'spot'),
                    'leverage': order.get('leverage', 1),
                    'margin_amount': order.get('margin_amount', 0.0),
                    'liquidation_price': order.get('liquidation_price', 0.0),
                    'open_time': order.get('open_time'),
                    'signal_id': order.get('signal_id', ''),
                    'account_type': 'demo',
                    'status': 'OPEN'
                }
                
                positions[position_id] = position_info
            
            logger.info(f"✅ تم جلب {len(positions)} صفقة تجريبية مفتوحة")
            return positions
            
        except Exception as e:
            logger.error(f"خطأ في جلب الصفقات التجريبية: {e}")
            return {}
    
    def update_demo_positions_prices(self, positions: Dict, api_client) -> Dict:
        """تحديث أسعار الصفقات التجريبية من API"""
        try:
            if not api_client:
                logger.warning("لا يوجد API client لتحديث الأسعار")
                return positions
            
            logger.info(f"🔄 تحديث أسعار {len(positions)} صفقة تجريبية")
            
            for position_id, position_info in positions.items():
                try:
                    symbol = position_info['symbol']
                    market_type = position_info.get('market_type', 'spot')
                    
                    # تحديد category حسب market_type
                    category = "linear" if market_type == "futures" else "spot"
                    
                    # جلب السعر الحالي من API
                    current_price = api_client.get_ticker_price(symbol, category)
                    
                    if current_price:
                        position_info['current_price'] = current_price
                        
                        # حساب PnL
                        entry_price = position_info['entry_price']
                        quantity = position_info['quantity']
                        side = position_info['side'].lower()
                        
                        if market_type == 'spot':
                            # حساب PnL للسبوت
                            amount = quantity * entry_price
                            contracts = quantity
                            
                            if side == 'buy':
                                pnl_value = (current_price - entry_price) * contracts
                            else:
                                pnl_value = (entry_price - current_price) * contracts
                            
                            pnl_percent = (pnl_value / amount) * 100 if amount > 0 else 0
                            
                        else:  # futures
                            # حساب PnL للفيوتشر
                            leverage = position_info.get('leverage', 1)
                            margin_amount = position_info.get('margin_amount', 0.0)
                            
                            contracts = (margin_amount * leverage) / entry_price
                            
                            if side == 'buy' or side == 'long':
                                pnl_value = (current_price - entry_price) * contracts
                            else:
                                pnl_value = (entry_price - current_price) * contracts
                            
                            pnl_percent = (pnl_value / margin_amount) * 100 if margin_amount > 0 else 0
                        
                        position_info['pnl_value'] = pnl_value
                        position_info['pnl_percent'] = pnl_percent
                        
                except Exception as e:
                    logger.error(f"خطأ في تحديث سعر الصفقة {position_id}: {e}")
                    continue
            
            logger.info("✅ تم تحديث الأسعار بنجاح")
            return positions
            
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار الصفقات التجريبية: {e}")
            return positions
    
    def get_real_positions(self, user_id: int, api_client, market_type: str = None) -> Dict[str, Any]:
        """جلب الصفقات الحقيقية من API"""
        try:
            if not api_client:
                logger.warning("لا يوجد API client للحساب الحقيقي")
                return {}
            
            # التحقق من debounce
            if not self._should_fetch(user_id):
                logger.info("تم تخطي الجلب بسبب debounce")
                return {}
            
            logger.info(f"📊 جلب الصفقات الحقيقية للمستخدم {user_id}")
            
            positions = {}
            
            # جلب صفقات Spot إذا كان market_type = spot أو None
            if not market_type or market_type == 'spot':
                try:
                    spot_positions = api_client.get_open_positions(category='spot')
                    if spot_positions:
                        for pos in spot_positions:
                            position_id = pos.get('orderId', pos.get('symbol'))
                            
                            position_info = {
                                'symbol': pos['symbol'],
                                'side': pos.get('side', 'BUY'),
                                'entry_price': float(pos.get('avgPrice', 0)),
                                'quantity': float(pos.get('qty', 0)),
                                'current_price': float(pos.get('markPrice', pos.get('lastPrice', 0))),
                                'market_type': 'spot',
                                'account_type': 'real',
                                'position_id_exchange': position_id,
                                'status': 'OPEN'
                            }
                            
                            # حساب PnL
                            amount = position_info['quantity'] * position_info['entry_price']
                            if position_info['current_price']:
                                if position_info['side'].lower() == 'buy':
                                    pnl_value = (position_info['current_price'] - position_info['entry_price']) * position_info['quantity']
                                else:
                                    pnl_value = (position_info['entry_price'] - position_info['current_price']) * position_info['quantity']
                                
                                position_info['pnl_value'] = pnl_value
                                position_info['pnl_percent'] = (pnl_value / amount) * 100 if amount > 0 else 0
                            
                            positions[position_id] = position_info
                            
                except Exception as e:
                    logger.error(f"خطأ في جلب صفقات Spot الحقيقية: {e}")
            
            # جلب صفقات Futures إذا كان market_type = futures أو None
            if not market_type or market_type == 'futures':
                try:
                    futures_positions = api_client.get_open_positions(category='linear')
                    if futures_positions:
                        for pos in futures_positions:
                            position_id = pos.get('positionIdx', pos.get('symbol'))
                            
                            position_info = {
                                'symbol': pos['symbol'],
                                'side': pos.get('side', 'Buy'),
                                'entry_price': float(pos.get('avgPrice', 0)),
                                'quantity': float(pos.get('size', 0)),
                                'current_price': float(pos.get('markPrice', 0)),
                                'leverage': int(pos.get('leverage', 1)),
                                'margin_amount': float(pos.get('positionIM', 0)),
                                'liquidation_price': float(pos.get('liqPrice', 0)),
                                'unrealized_pnl': float(pos.get('unrealisedPnl', 0)),
                                'market_type': 'futures',
                                'account_type': 'real',
                                'position_id_exchange': position_id,
                                'status': 'OPEN'
                            }
                            
                            # PnL
                            position_info['pnl_value'] = position_info['unrealized_pnl']
                            if position_info['margin_amount'] > 0:
                                position_info['pnl_percent'] = (position_info['pnl_value'] / position_info['margin_amount']) * 100
                            else:
                                position_info['pnl_percent'] = 0
                            
                            positions[position_id] = position_info
                            
                except Exception as e:
                    logger.error(f"خطأ في جلب صفقات Futures الحقيقية: {e}")
            
            logger.info(f"✅ تم جلب {len(positions)} صفقة حقيقية مفتوحة")
            return positions
            
        except Exception as e:
            logger.error(f"خطأ في جلب الصفقات الحقيقية: {e}")
            return {}
    
    def link_signal_ids_to_positions(self, positions: Dict) -> Dict:
        """ربط Signal IDs بالصفقات من قاعدة البيانات"""
        try:
            logger.info(f"🔗 ربط Signal IDs مع {len(positions)} صفقة")
            
            for position_id, position_info in positions.items():
                try:
                    # محاولة الحصول على signal_id من SignalIDManager
                    signal_id = self.signal_id_manager.get_signal_id_from_position(position_id)
                    
                    if signal_id:
                        position_info['signal_id'] = signal_id
                        logger.debug(f"تم ربط الصفقة {position_id} بـ Signal ID: {signal_id}")
                    else:
                        # محاولة الحصول من position_id_exchange في قاعدة البيانات
                        position_id_exchange = position_info.get('position_id_exchange', position_id)
                        
                        # البحث في قاعدة البيانات
                        filters = {
                            'status': 'OPEN',
                            'limit': 100
                        }
                        
                        orders = self.db_manager.get_user_trade_history(0, filters)  # سيتم تحسين هذا لاحقاً
                        
                        for order in orders:
                            if order.get('position_id_exchange') == position_id_exchange:
                                position_info['signal_id'] = order.get('signal_id', '')
                                break
                        
                except Exception as e:
                    logger.error(f"خطأ في ربط Signal ID للصفقة {position_id}: {e}")
                    continue
            
            logger.info("✅ تم الربط بنجاح")
            return positions
            
        except Exception as e:
            logger.error(f"خطأ في ربط Signal IDs: {e}")
            return positions
    
    def get_all_open_positions(self, user_id: int, account_type: str, api_client = None, market_type: str = None) -> Dict[str, Any]:
        """جلب جميع الصفقات المفتوحة حسب نوع الحساب"""
        try:
            logger.info(f"📊 جلب جميع الصفقات المفتوحة للمستخدم {user_id} - نوع الحساب: {account_type}")
            
            if account_type == 'demo':
                # جلب الصفقات التجريبية من قاعدة البيانات
                positions = self.get_demo_positions(user_id, market_type)
                
                # تحديث الأسعار من API
                if api_client:
                    positions = self.update_demo_positions_prices(positions, api_client)
                
            elif account_type == 'real':
                # جلب الصفقات الحقيقية من API
                positions = self.get_real_positions(user_id, api_client, market_type)
                
                # ربط Signal IDs
                positions = self.link_signal_ids_to_positions(positions)
            
            else:
                logger.error(f"نوع حساب غير صحيح: {account_type}")
                return {}
            
            logger.info(f"✅ تم جلب {len(positions)} صفقة مفتوحة بنجاح")
            return positions
            
        except Exception as e:
            logger.error(f"خطأ في جلب جميع الصفقات المفتوحة: {e}")
            return {}
    
    def separate_positions_by_market(self, positions: Dict) -> tuple:
        """فصل الصفقات حسب نوع السوق (Spot/Futures)"""
        try:
            spot_positions = {}
            futures_positions = {}
            
            for position_id, position_info in positions.items():
                market_type = position_info.get('market_type', 'spot')
                
                if market_type == 'spot':
                    spot_positions[position_id] = position_info
                elif market_type == 'futures':
                    futures_positions[position_id] = position_info
            
            logger.info(f"✅ تم فصل الصفقات: {len(spot_positions)} Spot، {len(futures_positions)} Futures")
            return spot_positions, futures_positions
            
        except Exception as e:
            logger.error(f"خطأ في فصل الصفقات: {e}")
            return {}, {}


# دالة مساعدة لإنشاء مثيل
def create_position_fetcher(db_manager, signal_id_manager):
    """إنشاء مثيل من PositionFetcher"""
    return PositionFetcher(db_manager, signal_id_manager)

