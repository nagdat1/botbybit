#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الإشارات المتقدم - نظام إدارة الإشارات مع ID والربط الاختياري
يدعم الحسابات التجريبية والحقيقية مع Spot/Futures
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class AccountType(Enum):
    """أنواع الحسابات"""
    DEMO = "demo"
    REAL = "real"

class MarketType(Enum):
    """أنواع الأسواق"""
    SPOT = "spot"
    FUTURES = "futures"

class SignalType(Enum):
    """أنواع الإشارات"""
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    PARTIAL_CLOSE = "partial_close"

@dataclass
class SignalData:
    """هيكل بيانات الإشارة"""
    signal: str
    symbol: str
    id: str
    percentage: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[int] = None

@dataclass
class Position:
    """هيكل بيانات الصفقة"""
    position_id: str
    signal_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    entry_price: float
    market_type: str  # 'spot' or 'futures'
    account_type: str  # 'demo' or 'real'
    exchange: str
    status: str  # 'open', 'closed', 'partial'
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class AdvancedSignalManager:
    """مدير الإشارات المتقدم مع نظام ID والربط الاختياري"""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}  # position_id -> Position
        self.signal_positions: Dict[str, List[str]] = {}  # signal_id -> [position_ids]
        self.user_settings: Dict[int, Dict] = {}  # user_id -> settings
        self.signal_history: List[Dict] = []
        self.lock = threading.Lock()
        
        # إعدادات افتراضية
        self.default_settings = {
            'account_type': AccountType.DEMO.value,
            'market_type': MarketType.SPOT.value,
            'exchange': 'bybit',
            'trade_amount': 100.0,
            'leverage': 10,
            'link_by_id': True,  # ربط الإشارات بنفس ID
            'language': 'ar'
        }
        
        logger.info("🚀 تم تهيئة مدير الإشارات المتقدم")
    
    def set_user_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """
        تعيين إعدادات المستخدم
        
        Args:
            user_id: معرف المستخدم
            settings: إعدادات المستخدم
            
        Returns:
            نجح التعيين أم لا
        """
        try:
            with self.lock:
                # دمج الإعدادات مع الافتراضية
                user_settings = self.default_settings.copy()
                user_settings.update(settings)
                
                # التحقق من صحة الإعدادات
                if not self._validate_settings(user_settings):
                    return False
                
                self.user_settings[user_id] = user_settings
                logger.info(f"✅ تم تعيين إعدادات المستخدم {user_id}: {user_settings}")
                return True
                
        except Exception as e:
            logger.error(f"❌ خطأ في تعيين إعدادات المستخدم {user_id}: {e}")
            return False
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المستخدم"""
        return self.user_settings.get(user_id, self.default_settings.copy())
    
    def process_signal(self, signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        معالجة الإشارة الواردة
        
        Args:
            signal_data: بيانات الإشارة
            user_id: معرف المستخدم
            
        Returns:
            نتيجة معالجة الإشارة
        """
        try:
            with self.lock:
                # التحقق من صحة الإشارة
                if not self._validate_signal(signal_data):
                    return {
                        'success': False,
                        'message': 'إشارة غير صحيحة',
                        'error': 'INVALID_SIGNAL'
                    }
                
                # الحصول على إعدادات المستخدم
                user_settings = self.get_user_settings(user_id)
                
                # إنشاء كائن الإشارة
                signal = SignalData(
                    signal=signal_data['signal'],
                    symbol=signal_data['symbol'],
                    id=signal_data['id'],
                    percentage=signal_data.get('percentage'),
                    user_id=user_id
                )
                
                # تسجيل الإشارة في التاريخ
                self._log_signal(signal, user_settings)
                
                # معالجة الإشارة حسب النوع
                result = self._process_signal_by_type(signal, user_settings)
                
                return result
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': 'PROCESSING_ERROR'
            }
    
    def _validate_signal(self, signal_data: Dict[str, Any]) -> bool:
        """التحقق من صحة الإشارة"""
        try:
            # التحقق من الحقول المطلوبة
            required_fields = ['signal', 'symbol', 'id']
            for field in required_fields:
                if field not in signal_data or not signal_data[field]:
                    logger.error(f"❌ الحقل المطلوب '{field}' مفقود")
                    return False
            
            # التحقق من نوع الإشارة
            signal_type = signal_data['signal'].lower()
            valid_signals = [s.value for s in SignalType]
            if signal_type not in valid_signals:
                logger.error(f"❌ نوع إشارة غير مدعوم: {signal_type}")
                return False
            
            # التحقق من رمز العملة
            symbol = signal_data['symbol'].strip()
            if len(symbol) < 6:
                logger.error(f"❌ رمز عملة غير صحيح: {symbol}")
                return False
            
            # التحقق من النسبة المئوية للإغلاق الجزئي
            if signal_type == 'partial_close':
                percentage = signal_data.get('percentage')
                if percentage is None or not (0 < percentage <= 100):
                    logger.error(f"❌ نسبة الإغلاق الجزئي غير صحيحة: {percentage}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من صحة الإشارة: {e}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """التحقق من صحة الإعدادات"""
        try:
            # التحقق من نوع الحساب
            account_type = settings.get('account_type')
            if account_type not in [a.value for a in AccountType]:
                logger.error(f"❌ نوع حساب غير صحيح: {account_type}")
                return False
            
            # التحقق من نوع السوق
            market_type = settings.get('market_type')
            if market_type not in [m.value for m in MarketType]:
                logger.error(f"❌ نوع سوق غير صحيح: {market_type}")
                return False
            
            # التحقق من مبلغ التداول
            trade_amount = settings.get('trade_amount', 0)
            if not isinstance(trade_amount, (int, float)) or trade_amount <= 0:
                logger.error(f"❌ مبلغ التداول غير صحيح: {trade_amount}")
                return False
            
            # التحقق من الرافعة المالية
            leverage = settings.get('leverage', 1)
            if not isinstance(leverage, (int, float)) or leverage < 1:
                logger.error(f"❌ الرافعة المالية غير صحيحة: {leverage}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من صحة الإعدادات: {e}")
            return False
    
    def _process_signal_by_type(self, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة الإشارة حسب النوع"""
        try:
            signal_type = signal.signal.lower()
            
            if signal_type == SignalType.BUY.value:
                return self._process_buy_signal(signal, user_settings)
            elif signal_type == SignalType.SELL.value:
                return self._process_sell_signal(signal, user_settings)
            elif signal_type == SignalType.CLOSE.value:
                return self._process_close_signal(signal, user_settings)
            elif signal_type == SignalType.PARTIAL_CLOSE.value:
                return self._process_partial_close_signal(signal, user_settings)
            else:
                return {
                    'success': False,
                    'message': f'نوع إشارة غير مدعوم: {signal_type}',
                    'error': 'UNSUPPORTED_SIGNAL_TYPE'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإشارة حسب النوع: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {str(e)}',
                'error': 'TYPE_PROCESSING_ERROR'
            }
    
    def _process_buy_signal(self, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة إشارة الشراء"""
        try:
            account_type = user_settings['account_type']
            market_type = user_settings['market_type']
            link_by_id = user_settings.get('link_by_id', True)
            
            logger.info(f"🟢 معالجة إشارة شراء: {signal.symbol} - ID: {signal.id}")
            
            # التحقق من الربط بالـ ID
            if link_by_id:
                existing_positions = self._get_positions_by_signal_id(signal.id, signal.user_id)
                
                # إذا كانت هناك صفقة موجودة بنفس ID
                if existing_positions:
                    # التحقق من الاتجاه
                    existing_side = existing_positions[0].side
                    
                    if existing_side == 'sell':
                        # إغلاق الصفقة البيعية وفتح شرائية
                        logger.info(f"🔄 إغلاق صفقة بيعية وفتح شرائية للـ ID: {signal.id}")
                        self._close_positions_by_signal_id(signal.id, signal.user_id)
                        return self._create_new_position(signal, user_settings, 'buy')
                    elif existing_side == 'buy':
                        # تعزيز الصفقة الشرائية
                        logger.info(f"📈 تعزيز صفقة شرائية للـ ID: {signal.id}")
                        return self._enhance_position(existing_positions[0], signal, user_settings)
            
            # إنشاء صفقة جديدة
            return self._create_new_position(signal, user_settings, 'buy')
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة إشارة الشراء: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة الشراء: {str(e)}',
                'error': 'BUY_SIGNAL_ERROR'
            }
    
    def _process_sell_signal(self, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة إشارة البيع"""
        try:
            account_type = user_settings['account_type']
            market_type = user_settings['market_type']
            link_by_id = user_settings.get('link_by_id', True)
            
            logger.info(f"🔴 معالجة إشارة بيع: {signal.symbol} - ID: {signal.id}")
            
            # التحقق من الربط بالـ ID
            if link_by_id:
                existing_positions = self._get_positions_by_signal_id(signal.id, signal.user_id)
                
                # إذا كانت هناك صفقة موجودة بنفس ID
                if existing_positions:
                    # التحقق من الاتجاه
                    existing_side = existing_positions[0].side
                    
                    if existing_side == 'buy':
                        # إغلاق الصفقة الشرائية وفتح بيعية
                        logger.info(f"🔄 إغلاق صفقة شرائية وفتح بيعية للـ ID: {signal.id}")
                        self._close_positions_by_signal_id(signal.id, signal.user_id)
                        return self._create_new_position(signal, user_settings, 'sell')
                    elif existing_side == 'sell':
                        # تعزيز الصفقة البيعية
                        logger.info(f"📉 تعزيز صفقة بيعية للـ ID: {signal.id}")
                        return self._enhance_position(existing_positions[0], signal, user_settings)
            
            # إنشاء صفقة جديدة
            return self._create_new_position(signal, user_settings, 'sell')
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة إشارة البيع: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة البيع: {str(e)}',
                'error': 'SELL_SIGNAL_ERROR'
            }
    
    def _process_close_signal(self, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة إشارة الإغلاق الكامل"""
        try:
            link_by_id = user_settings.get('link_by_id', True)
            
            logger.info(f"⚪ معالجة إشارة إغلاق كامل: {signal.symbol} - ID: {signal.id}")
            
            if link_by_id:
                # إغلاق الصفقات المرتبطة بالـ ID
                positions = self._get_positions_by_signal_id(signal.id, signal.user_id)
                
                if not positions:
                    return {
                        'success': False,
                        'message': f'لا توجد صفقات مرتبطة بالـ ID: {signal.id}',
                        'error': 'NO_POSITIONS_FOUND'
                    }
                
                closed_count = 0
                for position in positions:
                    if self._close_position(position):
                        closed_count += 1
                
                return {
                    'success': True,
                    'message': f'تم إغلاق {closed_count} صفقة مرتبطة بالـ ID: {signal.id}',
                    'closed_count': closed_count,
                    'signal_id': signal.id
                }
            else:
                # إغلاق جميع الصفقات على الرمز
                positions = self._get_positions_by_symbol(signal.symbol, signal.user_id)
                
                if not positions:
                    return {
                        'success': False,
                        'message': f'لا توجد صفقات مفتوحة على {signal.symbol}',
                        'error': 'NO_POSITIONS_FOUND'
                    }
                
                closed_count = 0
                for position in positions:
                    if self._close_position(position):
                        closed_count += 1
                
                return {
                    'success': True,
                    'message': f'تم إغلاق {closed_count} صفقة على {signal.symbol}',
                    'closed_count': closed_count,
                    'symbol': signal.symbol
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة إشارة الإغلاق: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة الإغلاق: {str(e)}',
                'error': 'CLOSE_SIGNAL_ERROR'
            }
    
    def _process_partial_close_signal(self, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة إشارة الإغلاق الجزئي"""
        try:
            link_by_id = user_settings.get('link_by_id', True)
            percentage = signal.percentage or 50
            
            logger.info(f"🟡 معالجة إشارة إغلاق جزئي {percentage}%: {signal.symbol} - ID: {signal.id}")
            
            if link_by_id:
                # إغلاق جزئي للصفقات المرتبطة بالـ ID
                positions = self._get_positions_by_signal_id(signal.id, signal.user_id)
                
                if not positions:
                    return {
                        'success': False,
                        'message': f'لا توجد صفقات مرتبطة بالـ ID: {signal.id}',
                        'error': 'NO_POSITIONS_FOUND'
                    }
                
                closed_count = 0
                for position in positions:
                    if self._partial_close_position(position, percentage):
                        closed_count += 1
                
                return {
                    'success': True,
                    'message': f'تم إغلاق جزئي {percentage}% من {closed_count} صفقة مرتبطة بالـ ID: {signal.id}',
                    'closed_count': closed_count,
                    'percentage': percentage,
                    'signal_id': signal.id
                }
            else:
                # إغلاق جزئي لجميع الصفقات على الرمز
                positions = self._get_positions_by_symbol(signal.symbol, signal.user_id)
                
                if not positions:
                    return {
                        'success': False,
                        'message': f'لا توجد صفقات مفتوحة على {signal.symbol}',
                        'error': 'NO_POSITIONS_FOUND'
                    }
                
                closed_count = 0
                for position in positions:
                    if self._partial_close_position(position, percentage):
                        closed_count += 1
                
                return {
                    'success': True,
                    'message': f'تم إغلاق جزئي {percentage}% من {closed_count} صفقة على {signal.symbol}',
                    'closed_count': closed_count,
                    'percentage': percentage,
                    'symbol': signal.symbol
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة إشارة الإغلاق الجزئي: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة إشارة الإغلاق الجزئي: {str(e)}',
                'error': 'PARTIAL_CLOSE_SIGNAL_ERROR'
            }
    
    def _create_new_position(self, signal: SignalData, user_settings: Dict[str, Any], side: str) -> Dict[str, Any]:
        """إنشاء صفقة جديدة"""
        try:
            position_id = f"POS_{signal.id}_{int(time.time())}"
            
            position = Position(
                position_id=position_id,
                signal_id=signal.id,
                symbol=signal.symbol,
                side=side,
                quantity=user_settings['trade_amount'],
                entry_price=0.0,  # سيتم تحديثه لاحقاً
                market_type=user_settings['market_type'],
                account_type=user_settings['account_type'],
                exchange=user_settings['exchange'],
                status='open'
            )
            
            # حفظ الصفقة
            self.positions[position_id] = position
            
            # ربط الصفقة بالـ ID
            if signal.id not in self.signal_positions:
                self.signal_positions[signal.id] = []
            self.signal_positions[signal.id].append(position_id)
            
            # تنفيذ الصفقة حسب نوع الحساب
            if user_settings['account_type'] == AccountType.REAL.value:
                # تنفيذ حقيقي عبر API
                execution_result = self._execute_real_position(position, user_settings)
            else:
                # تنفيذ تجريبي
                execution_result = self._execute_demo_position(position, user_settings)
            
            if execution_result['success']:
                logger.info(f"✅ تم إنشاء صفقة جديدة: {position_id}")
                return {
                    'success': True,
                    'message': f'تم إنشاء صفقة {side} جديدة: {signal.symbol}',
                    'position_id': position_id,
                    'signal_id': signal.id,
                    'account_type': user_settings['account_type'],
                    'execution_details': execution_result
                }
            else:
                # إزالة الصفقة في حالة فشل التنفيذ
                del self.positions[position_id]
                if signal.id in self.signal_positions:
                    self.signal_positions[signal.id].remove(position_id)
                
                return {
                    'success': False,
                    'message': f'فشل في تنفيذ الصفقة: {execution_result["message"]}',
                    'error': 'EXECUTION_FAILED',
                    'execution_details': execution_result
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء صفقة جديدة: {e}")
            return {
                'success': False,
                'message': f'خطأ في إنشاء صفقة جديدة: {str(e)}',
                'error': 'POSITION_CREATION_ERROR'
            }
    
    def _enhance_position(self, existing_position: Position, signal: SignalData, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تعزيز صفقة موجودة"""
        try:
            logger.info(f"📈 تعزيز صفقة موجودة: {existing_position.position_id}")
            
            # تحديث الكمية
            new_quantity = existing_position.quantity + user_settings['trade_amount']
            existing_position.quantity = new_quantity
            existing_position.updated_at = datetime.now()
            
            # تنفيذ التعزيز حسب نوع الحساب
            if user_settings['account_type'] == AccountType.REAL.value:
                execution_result = self._execute_real_enhancement(existing_position, user_settings)
            else:
                execution_result = self._execute_demo_enhancement(existing_position, user_settings)
            
            if execution_result['success']:
                logger.info(f"✅ تم تعزيز الصفقة: {existing_position.position_id}")
                return {
                    'success': True,
                    'message': f'تم تعزيز صفقة {existing_position.side}: {signal.symbol}',
                    'position_id': existing_position.position_id,
                    'signal_id': signal.id,
                    'new_quantity': new_quantity,
                    'enhancement_details': execution_result
                }
            else:
                # إعادة الكمية الأصلية في حالة فشل التعزيز
                existing_position.quantity -= user_settings['trade_amount']
                return {
                    'success': False,
                    'message': f'فشل في تعزيز الصفقة: {execution_result["message"]}',
                    'error': 'ENHANCEMENT_FAILED',
                    'enhancement_details': execution_result
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تعزيز الصفقة عمليات: {e}")
            return {
                'success': False,
                'message': f'خطأ في تعزيز الصفقة: {str(e)}',
                'error': 'ENHANCEMENT_ERROR'
            }
    
    def _close_position(self, position: Position) -> bool:
        """إغلاق صفقة"""
        try:
            position.status = 'closed'
            position.updated_at = datetime.now()
            
            logger.info(f"✅ تم إغلاق الصفقة: {position.position_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقة: {e}")
            return False
    
    def _partial_close_position(self, position: Position, percentage: float) -> bool:
        """إغلاق جزئي للصفقة"""
        try:
            # حساب الكمية الجديدة
            close_quantity = position.quantity * (percentage / 100)
            remaining_quantity = position.quantity - close_quantity
            
            if remaining_quantity <= 0:
                # إغلاق كامل إذا كانت النسبة 100% أو أكثر
                position.status = 'closed'
            else:
                # تحديث الكمية
                position.quantity = remaining_quantity
                position.status = 'partial'
            
            position.updated_at = datetime.now()
            
            logger.info(f"✅ تم إغلاق جزئي {percentage}% من الصفقة: {position.position_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في الإغلاق الجزئي: {e}")
            return False
    
    def _execute_real_position(self, position: Position, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ صفقة حقيقية عبر API"""
        try:
            # هنا سيتم استدعاء API المنصة الحقيقية
            # هذا مثال مبسط
            logger.info(f"🌐 تنفيذ صفقة حقيقية: {position.symbol} {position.side}")
            
            # محاكاة التنفيذ
            time.sleep(0.1)  # محاكاة تأخير الشبكة
            
            return {
                'success': True,
                'message': 'تم تنفيذ الصفقة الحقيقية بنجاح',
                'order_id': f"ORDER_{int(time.time())}",
                'executed_price': 50000.0,  # سيتم جلبه من API
                'executed_quantity': position.quantity
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة الحقيقية: {str(e)}',
                'error': 'REAL_EXECUTION_ERROR'
            }
    
    def _execute_demo_position(self, position: Position, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ صفقة تجريبية"""
        try:
            logger.info(f"🎮 تنفيذ صفقة تجريبية: {position.symbol} {position.side}")
            
            # محاكاة التنفيذ التجريبي
            time.sleep(0.05)  # محاكاة تأخير أقل
            
            return {
                'success': True,
                'message': 'تم تنفيذ الصفقة التجريبية بنجاح',
                'order_id': f"DEMO_ORDER_{int(time.time())}",
                'executed_price': 50000.0,  # سعر محاكي
                'executed_quantity': position.quantity
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تنفيذ الصفقة التجريبية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الصفقة التجريبية: {str(e)}',
                'error': 'DEMO_EXECUTION_ERROR'
            }
    
    def _execute_real_enhancement(self, position: Position, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ تعزيز صفقة حقيقية"""
        try:
            logger.info(f"🌐 تعزيز صفقة حقيقية: {position.position_id}")
            
            # محاكاة التعزيز
            time.sleep(0.1)
            
            return {
                'success': True,
                'message': 'تم تعزيز الصفقة الحقيقية بنجاح',
                'enhancement_amount': user_settings['trade_amount']
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تعزيز الصفقة الحقيقية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تعزيز الصفقة الحقيقية: {str(e)}',
                'error': 'REAL_ENHANCEMENT_ERROR'
            }
    
    def _execute_demo_enhancement(self, position: Position, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ تعزيز صفقة تجريبية"""
        try:
            logger.info(f"🎮 تعزيز صفقة تجريبية: {position.position_id}")
            
            # محاكاة التعزيز التجريبي
            time.sleep(0.05)
            
            return {
                'success': True,
                'message': 'تم تعزيز الصفقة التجريبية بنجاح',
                'enhancement_amount': user_settings['trade_amount']
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تعزيز الصفقة التجريبية: {e}")
            return {
                'success': False,
                'message': f'خطأ في تعزيز الصفقة التجريبية: {str(e)}',
                'error': 'DEMO_ENHANCEMENT_ERROR'
            }
    
    def _get_positions_by_signal_id(self, signal_id: str, user_id: int) -> List[Position]:
        """الحصول على الصفقات المرتبطة بـ ID الإشارة"""
        try:
            positions = []
            for position_id in self.signal_positions.get(signal_id, []):
                position = self.positions.get(position_id)
                if position and position.user_id == user_id and position.status == 'open':
                    positions.append(position)
            return positions
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الصفقات بالـ ID: {e}")
            return []
    
    def _get_positions_by_symbol(self, symbol: str, user_id: int) -> List[Position]:
        """الحصول على الصفقات المفتوحة على رمز معين"""
        try:
            positions = []
            for position in self.positions.values():
                if (position.symbol == symbol and 
                    position.user_id == user_id and 
                    position.status == 'open'):
                    positions.append(position)
            return positions
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الصفقات بالرمز: {e}")
            return []
    
    def _close_positions_by_signal_id(self, signal_id: str, user_id: int) -> int:
        """إغلاق جميع الصفقات المرتبطة بـ ID الإشارة"""
        try:
            positions = self._get_positions_by_signal_id(signal_id, user_id)
            closed_count = 0
            
            for position in positions:
                if self._close_position(position):
                    closed_count += 1
            
            return closed_count
            
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقات بالـ ID: {e}")
            return 0
    
    def _log_signal(self, signal: SignalData, user_settings: Dict[str, Any]) -> None:
        """تسجيل الإشارة في التاريخ"""
        try:
            log_entry = {
                'timestamp': signal.timestamp.isoformat(),
                'signal': signal.signal,
                'symbol': signal.symbol,
                'id': signal.id,
                'percentage': signal.percentage,
                'user_id': signal.user_id,
                'user_settings': user_settings.copy()
            }
            
            self.signal_history.append(log_entry)
            
            # الاحتفاظ بآخر 1000 إشارة فقط
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-1000:]
                
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل الإشارة: {e}")
    
    def get_user_positions(self, user_id: int) -> List[Dict[str, Any]]:
        """الحصول على صفقات المستخدم"""
        try:
            positions = []
            for position in self.positions.values():
                if position.user_id == user_id:
                    positions.append({
                        'position_id': position.position_id,
                        'signal_id': position.signal_id,
                        'symbol': position.symbol,
                        'side': position.side,
                        'quantity': position.quantity,
                        'entry_price': position.entry_price,
                        'market_type': position.market_type,
                        'account_type': position.account_type,
                        'exchange': position.exchange,
                        'status': position.status,
                        'created_at': position.created_at.isoformat(),
                        'updated_at': position.updated_at.isoformat()
                    })
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على صفقات المستخدم: {e}")
            return []
    
    def get_signal_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """الحصول على تاريخ الإشارات للمستخدم"""
        try:
            user_signals = [
                signal for signal in self.signal_history 
                if signal['user_id'] == user_id
            ]
            
            return user_signals[-limit:] if limit > 0 else user_signals
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على تاريخ الإشارات: {e}")
            return []
    
    def get_statistics(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إحصائيات المستخدم"""
        try:
            positions = self.get_user_positions(user_id)
            signals = self.get_signal_history(user_id)
            
            open_positions = [p for p in positions if p['status'] == 'open']
            closed_positions = [p for p in positions if p['status'] == 'closed']
            
            return {
                'total_positions': len(positions),
                'open_positions': len(open_positions),
                'closed_positions': len(closed_positions),
                'total_signals': len(signals),
                'account_type': self.get_user_settings(user_id).get('account_type', 'demo'),
                'market_type': self.get_user_settings(user_id).get('market_type', 'spot'),
                'link_by_id': self.get_user_settings(user_id).get('link_by_id', True)
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            return {}


# مثيل عام لمدير الإشارات المتقدم
advanced_signal_manager = AdvancedSignalManager()


# دوال مساعدة للاستخدام السريع
def process_signal(signal_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    """معالجة إشارة"""
    return advanced_signal_manager.process_signal(signal_data, user_id)


def set_user_settings(user_id: int, settings: Dict[str, Any]) -> bool:
    """تعيين إعدادات المستخدم"""
    return advanced_signal_manager.set_user_settings(user_id, settings)


def get_user_positions(user_id: int) -> List[Dict[str, Any]]:
    """الحصول على صفقات المستخدم"""
    return advanced_signal_manager.get_user_positions(user_id)


def get_user_statistics(user_id: int) -> Dict[str, Any]:
    """الحصول على إحصائيات المستخدم"""
    return advanced_signal_manager.get_statistics(user_id)


if __name__ == "__main__":
    # اختبار النظام
    print("=" * 80)
    print("اختبار مدير الإشارات المتقدم")
    print("=" * 80)
    
    # إعدادات المستخدم
    user_id = 12345
    settings = {
        'account_type': 'demo',
        'market_type': 'spot',
        'exchange': 'bybit',
        'trade_amount': 100.0,
        'leverage': 10,
        'link_by_id': True
    }
    
    # تعيين الإعدادات
    set_user_settings(user_id, settings)
    
    # أمثلة الإشارات
    test_signals = [
        {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'},
        {'signal': 'sell', 'symbol': 'BTCUSDT', 'id': 'TV_S01'},
        {'signal': 'close', 'symbol': 'BTCUSDT', 'id': 'TV_C01'},
        {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_PC01', 'percentage': 50}
    ]
    
    for signal in test_signals:
        print(f"\n📥 معالجة الإشارة: {signal}")
        result = process_signal(signal, user_id)
        print(f"📤 النتيجة: {result}")
    
    # إحصائيات المستخدم
    stats = get_user_statistics(user_id)
    print(f"\n📊 إحصائيات المستخدم: {stats}")
