#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة المخاطر المتقدم - Advanced Risk Management System
يدعم استراتيجيات متقدمة لإدارة المخاطر والتداول الآمن
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """مستويات المخاطر"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TradeType(Enum):
    """أنواع التداول"""
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"

@dataclass
class RiskMetrics:
    """مقاييس المخاطر"""
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    monthly_pnl: float = 0.0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    volatility: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class RiskLimits:
    """حدود المخاطر"""
    max_daily_loss: float = 500.0
    max_weekly_loss: float = 2000.0
    max_monthly_loss: float = 8000.0
    max_position_size: float = 1000.0
    max_leverage: float = 10.0
    max_correlation: float = 0.7
    max_drawdown: float = 15.0
    min_balance_ratio: float = 0.1

@dataclass
class PositionRisk:
    """مخاطر الصفقة"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    leverage: float
    margin_used: float
    pnl: float
    pnl_percent: float
    risk_score: float
    volatility: float
    correlation: Dict[str, float] = field(default_factory=dict)

class AdvancedRiskManager:
    """مدير المخاطر المتقدم"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.risk_limits = RiskLimits()
        self.risk_metrics = RiskMetrics()
        self.positions: Dict[str, PositionRisk] = {}
        self.trade_history: List[Dict] = []
        self.market_data: Dict[str, Dict] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        # إعدادات متقدمة
        self.auto_stop_loss = True
        self.trailing_stop = True
        self.portfolio_rebalancing = True
        self.dynamic_position_sizing = True
        self.volatility_adjustment = True
        
        # إحصائيات الأداء
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'current_streak': 0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0
        }
        
        logger.info(f"تم تهيئة مدير المخاطر المتقدم للمستخدم {user_id}")
    
    def update_risk_limits(self, limits: Dict[str, float]) -> bool:
        """تحديث حدود المخاطر"""
        try:
            for key, value in limits.items():
                if hasattr(self.risk_limits, key):
                    setattr(self.risk_limits, key, value)
            
            logger.info(f"تم تحديث حدود المخاطر للمستخدم {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث حدود المخاطر: {e}")
            return False
    
    def calculate_position_size(self, symbol: str, signal_strength: float, 
                              volatility: float, account_balance: float) -> float:
        """حساب حجم الصفقة الأمثل باستخدام Kelly Criterion"""
        try:
            # حساب النسبة المئوية للمخاطرة
            base_risk_percent = 0.02  # 2% من الرصيد كقاعدة
            
            # تعديل المخاطرة حسب قوة الإشارة
            signal_adjustment = min(signal_strength, 2.0)  # أقصى تعديل 2x
            
            # تعديل المخاطرة حسب التقلبات
            volatility_adjustment = max(0.5, 1.0 - (volatility - 0.02) * 10)  # تقليل المخاطرة مع زيادة التقلبات
            
            # حساب المخاطرة النهائية
            adjusted_risk_percent = base_risk_percent * signal_adjustment * volatility_adjustment
            
            # حساب حجم الصفقة
            position_size = account_balance * adjusted_risk_percent
            
            # تطبيق الحد الأقصى
            max_size = min(position_size, self.risk_limits.max_position_size)
            
            logger.info(f"حجم الصفقة المحسوب: {max_size:.2f} (المخاطرة: {adjusted_risk_percent:.2%})")
            return max_size
            
        except Exception as e:
            logger.error(f"خطأ في حساب حجم الصفقة: {e}")
            return 0.0
    
    def assess_position_risk(self, symbol: str, side: str, size: float, 
                           entry_price: float, leverage: float = 1.0) -> Dict[str, Any]:
        """تقييم مخاطر الصفقة"""
        try:
            # الحصول على بيانات السوق
            market_info = self.market_data.get(symbol, {})
            volatility = market_info.get('volatility', 0.02)
            current_price = market_info.get('price', entry_price)
            
            # حساب الهامش المستخدم
            margin_used = (size * entry_price) / leverage
            
            # حساب الربح/الخسارة المحتملة
            pnl = (current_price - entry_price) * size if side.lower() == 'buy' else (entry_price - current_price) * size
            pnl_percent = (pnl / (size * entry_price)) * 100
            
            # حساب درجة المخاطرة
            risk_score = self._calculate_risk_score(symbol, size, volatility, leverage, margin_used)
            
            # إنشاء كائن مخاطر الصفقة
            position_risk = PositionRisk(
                symbol=symbol,
                side=side,
                size=size,
                entry_price=entry_price,
                current_price=current_price,
                leverage=leverage,
                margin_used=margin_used,
                pnl=pnl,
                pnl_percent=pnl_percent,
                risk_score=risk_score,
                volatility=volatility
            )
            
            # حفظ الصفقة
            self.positions[symbol] = position_risk
            
            # تقييم المخاطر الإجمالية
            portfolio_risk = self._assess_portfolio_risk()
            
            return {
                'position_risk': position_risk,
                'portfolio_risk': portfolio_risk,
                'recommendation': self._get_risk_recommendation(risk_score, portfolio_risk),
                'stop_loss_price': self._calculate_stop_loss(entry_price, side, volatility),
                'take_profit_price': self._calculate_take_profit(entry_price, side, volatility)
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقييم مخاطر الصفقة: {e}")
            return {'error': str(e)}
    
    def _calculate_risk_score(self, symbol: str, size: float, volatility: float, 
                            leverage: float, margin_used: float) -> float:
        """حساب درجة المخاطرة"""
        try:
            # حساب المخاطرة الأساسية
            base_risk = volatility * leverage
            
            # تعديل المخاطرة حسب حجم الصفقة
            size_risk = min(size / 1000.0, 1.0)  # تطبيع حجم الصفقة
            
            # تعديل المخاطرة حسب الهامش المستخدم
            margin_risk = min(margin_used / 5000.0, 1.0)  # تطبيع الهامش
            
            # حساب درجة المخاطرة النهائية (0-100)
            risk_score = (base_risk * 50 + size_risk * 30 + margin_risk * 20) * 100
            
            return min(risk_score, 100.0)
            
        except Exception as e:
            logger.error(f"خطأ في حساب درجة المخاطرة: {e}")
            return 50.0  # درجة مخاطرة متوسطة في حالة الخطأ
    
    def _assess_portfolio_risk(self) -> Dict[str, Any]:
        """تقييم مخاطر المحفظة الإجمالية"""
        try:
            total_margin = sum(pos.margin_used for pos in self.positions.values())
            total_pnl = sum(pos.pnl for pos in self.positions.values())
            
            # حساب التوزيع
            symbol_distribution = {}
            for symbol, pos in self.positions.items():
                symbol_distribution[symbol] = pos.margin_used / total_margin if total_margin > 0 else 0
            
            # حساب التقلبات المحفظة
            portfolio_volatility = self._calculate_portfolio_volatility()
            
            # حساب الحد الأقصى للخسارة المحتملة
            max_loss = sum(pos.size * pos.entry_price * pos.volatility * pos.leverage 
                          for pos in self.positions.values())
            
            return {
                'total_positions': len(self.positions),
                'total_margin_used': total_margin,
                'total_pnl': total_pnl,
                'portfolio_volatility': portfolio_volatility,
                'max_potential_loss': max_loss,
                'symbol_distribution': symbol_distribution,
                'risk_level': self._determine_risk_level(portfolio_volatility, max_loss)
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقييم مخاطر المحفظة: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_volatility(self) -> float:
        """حساب تقلبات المحفظة"""
        try:
            if not self.positions:
                return 0.0
            
            # حساب متوسط التقلبات المرجح
            total_weight = 0
            weighted_volatility = 0
            
            for pos in self.positions.values():
                weight = pos.margin_used
                total_weight += weight
                weighted_volatility += pos.volatility * weight
            
            return weighted_volatility / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"خطأ في حساب تقلبات المحفظة: {e}")
            return 0.0
    
    def _determine_risk_level(self, volatility: float, max_loss: float) -> RiskLevel:
        """تحديد مستوى المخاطرة"""
        if volatility > 0.05 or max_loss > self.risk_limits.max_daily_loss:
            return RiskLevel.CRITICAL
        elif volatility > 0.03 or max_loss > self.risk_limits.max_daily_loss * 0.7:
            return RiskLevel.HIGH
        elif volatility > 0.02 or max_loss > self.risk_limits.max_daily_loss * 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_risk_recommendation(self, risk_score: float, portfolio_risk: Dict[str, Any]) -> str:
        """الحصول على توصية المخاطرة"""
        if risk_score > 80 or portfolio_risk.get('risk_level') == RiskLevel.CRITICAL:
            return "REDUCE_POSITION"
        elif risk_score > 60 or portfolio_risk.get('risk_level') == RiskLevel.HIGH:
            return "MONITOR_CLOSELY"
        elif risk_score > 40 or portfolio_risk.get('risk_level') == RiskLevel.MEDIUM:
            return "PROCEED_CAUTIOUSLY"
        else:
            return "SAFE_TO_PROCEED"
    
    def _calculate_stop_loss(self, entry_price: float, side: str, volatility: float) -> float:
        """حساب وقف الخسارة الأمثل"""
        # حساب المسافة بناءً على التقلبات
        atr_multiplier = 2.0  # مضاعف ATR
        stop_distance = entry_price * volatility * atr_multiplier
        
        if side.lower() == 'buy':
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
    
    def _calculate_take_profit(self, entry_price: float, side: str, volatility: float) -> float:
        """حساب هدف الربح الأمثل"""
        # حساب المسافة بناءً على التقلبات ونسبة المخاطرة/العائد
        risk_reward_ratio = 2.0  # نسبة المخاطرة/العائد
        stop_distance = entry_price * volatility * 2.0
        profit_distance = stop_distance * risk_reward_ratio
        
        if side.lower() == 'buy':
            return entry_price + profit_distance
        else:
            return entry_price - profit_distance
    
    def check_risk_limits(self, new_trade: Dict[str, Any]) -> Dict[str, Any]:
        """فحص حدود المخاطر قبل تنفيذ الصفقة"""
        try:
            symbol = new_trade.get('symbol')
            size = new_trade.get('size', 0)
            leverage = new_trade.get('leverage', 1)
            
            # فحص الحد الأقصى لحجم الصفقة
            if size > self.risk_limits.max_position_size:
                return {
                    'allowed': False,
                    'reason': f'حجم الصفقة {size} يتجاوز الحد الأقصى {self.risk_limits.max_position_size}',
                    'suggestion': f'تقليل الحجم إلى {self.risk_limits.max_position_size}'
                }
            
            # فحص الحد الأقصى للرافعة المالية
            if leverage > self.risk_limits.max_leverage:
                return {
                    'allowed': False,
                    'reason': f'الرافعة المالية {leverage}x تتجاوز الحد الأقصى {self.risk_limits.max_leverage}x',
                    'suggestion': f'تقليل الرافعة إلى {self.risk_limits.max_leverage}x'
                }
            
            # فحص الخسارة اليومية
            if self.risk_metrics.daily_pnl < -self.risk_limits.max_daily_loss:
                return {
                    'allowed': False,
                    'reason': f'الخسارة اليومية {abs(self.risk_metrics.daily_pnl)} تتجاوز الحد الأقصى {self.risk_limits.max_daily_loss}',
                    'suggestion': 'إيقاف التداول اليوم'
                }
            
            # فحص الخسارة الأسبوعية
            if self.risk_metrics.weekly_pnl < -self.risk_limits.max_weekly_loss:
                return {
                    'allowed': False,
                    'reason': f'الخسارة الأسبوعية {abs(self.risk_metrics.weekly_pnl)} تتجاوز الحد الأقصى {self.risk_limits.max_weekly_loss}',
                    'suggestion': 'إيقاف التداول الأسبوعي'
                }
            
            return {
                'allowed': True,
                'reason': 'جميع حدود المخاطر ضمن الحدود المسموحة',
                'warnings': self._get_risk_warnings(new_trade)
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص حدود المخاطر: {e}")
            return {
                'allowed': False,
                'reason': f'خطأ في فحص المخاطر: {e}',
                'suggestion': 'مراجعة إعدادات المخاطر'
            }
    
    def _get_risk_warnings(self, trade: Dict[str, Any]) -> List[str]:
        """الحصول على تحذيرات المخاطرة"""
        warnings = []
        
        symbol = trade.get('symbol')
        size = trade.get('size', 0)
        leverage = trade.get('leverage', 1)
        
        # تحذير من حجم الصفقة الكبير
        if size > self.risk_limits.max_position_size * 0.8:
            warnings.append(f"حجم الصفقة كبير ({size}) - تقليل المخاطرة")
        
        # تحذير من الرافعة المالية العالية
        if leverage > self.risk_limits.max_leverage * 0.8:
            warnings.append(f"رافعة مالية عالية ({leverage}x) - زيادة المخاطرة")
        
        # تحذير من الخسارة المتقاربة
        if self.risk_metrics.daily_pnl < -self.risk_limits.max_daily_loss * 0.8:
            warnings.append("الخسارة اليومية تقترب من الحد الأقصى")
        
        return warnings
    
    def update_market_data(self, symbol: str, price: float, volatility: float = None):
        """تحديث بيانات السوق"""
        try:
            self.market_data[symbol] = {
                'price': price,
                'volatility': volatility or self.market_data.get(symbol, {}).get('volatility', 0.02),
                'last_updated': datetime.now()
            }
            
            # تحديث أسعار الصفقات المفتوحة
            if symbol in self.positions:
                self.positions[symbol].current_price = price
                # إعادة حساب الربح/الخسارة
                pos = self.positions[symbol]
                if pos.side.lower() == 'buy':
                    pos.pnl = (price - pos.entry_price) * pos.size
                else:
                    pos.pnl = (pos.entry_price - price) * pos.size
                pos.pnl_percent = (pos.pnl / (pos.size * pos.entry_price)) * 100
                
        except Exception as e:
            logger.error(f"خطأ في تحديث بيانات السوق: {e}")
    
    def get_risk_report(self) -> Dict[str, Any]:
        """الحصول على تقرير المخاطر"""
        try:
            portfolio_risk = self._assess_portfolio_risk()
            
            return {
                'user_id': self.user_id,
                'timestamp': datetime.now().isoformat(),
                'risk_metrics': {
                    'daily_pnl': self.risk_metrics.daily_pnl,
                    'weekly_pnl': self.risk_metrics.weekly_pnl,
                    'total_pnl': self.risk_metrics.total_pnl,
                    'max_drawdown': self.risk_metrics.max_drawdown,
                    'win_rate': self.risk_metrics.win_rate,
                    'profit_factor': self.risk_metrics.profit_factor
                },
                'portfolio_risk': portfolio_risk,
                'risk_limits': {
                    'max_daily_loss': self.risk_limits.max_daily_loss,
                    'max_weekly_loss': self.risk_limits.max_weekly_loss,
                    'max_position_size': self.risk_limits.max_position_size,
                    'max_leverage': self.risk_limits.max_leverage
                },
                'performance_stats': self.performance_stats,
                'recommendations': self._get_risk_recommendations()
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير المخاطر: {e}")
            return {'error': str(e)}
    
    def _get_risk_recommendations(self) -> List[str]:
        """الحصول على توصيات المخاطر"""
        recommendations = []
        
        # توصية بناءً على الخسارة اليومية
        if self.risk_metrics.daily_pnl < -self.risk_limits.max_daily_loss * 0.7:
            recommendations.append("تجنب فتح صفقات جديدة اليوم - الخسارة تقترب من الحد الأقصى")
        
        # توصية بناءً على معدل الفوز
        if self.performance_stats['total_trades'] > 10 and self.performance_stats['win_rate'] < 0.4:
            recommendations.append("معدل الفوز منخفض - مراجعة استراتيجية التداول")
        
        # توصية بناءً على التقلبات
        portfolio_volatility = self._calculate_portfolio_volatility()
        if portfolio_volatility > 0.04:
            recommendations.append("التقلبات عالية - تقليل حجم الصفقات")
        
        return recommendations
    
    def reset_daily_metrics(self):
        """إعادة تعيين المقاييس اليومية"""
        try:
            self.risk_metrics.daily_pnl = 0.0
            self.performance_stats['current_streak'] = 0
            logger.info(f"تم إعادة تعيين المقاييس اليومية للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين المقاييس اليومية: {e}")
    
    def reset_weekly_metrics(self):
        """إعادة تعيين المقاييس الأسبوعية"""
        try:
            self.risk_metrics.weekly_pnl = 0.0
            logger.info(f"تم إعادة تعيين المقاييس الأسبوعية للمستخدم {self.user_id}")
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين المقاييس الأسبوعية: {e}")


# مدير المخاطر العام
class GlobalRiskManager:
    """مدير المخاطر العام لجميع المستخدمين"""
    
    def __init__(self):
        self.user_risk_managers: Dict[int, AdvancedRiskManager] = {}
        self.global_settings = {
            'market_volatility_threshold': 0.05,
            'correlation_threshold': 0.7,
            'global_position_limit': 10000.0,
            'emergency_stop_enabled': True
        }
        
    def get_risk_manager(self, user_id: int) -> AdvancedRiskManager:
        """الحصول على مدير المخاطر للمستخدم"""
        if user_id not in self.user_risk_managers:
            self.user_risk_managers[user_id] = AdvancedRiskManager(user_id)
        return self.user_risk_managers[user_id]
    
    def check_global_risk(self, user_id: int, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """فحص المخاطر العامة"""
        try:
            risk_manager = self.get_risk_manager(user_id)
            
            # فحص المخاطر المحلية
            local_check = risk_manager.check_risk_limits(trade_data)
            
            # فحص المخاطر العامة
            global_check = self._check_global_limits(user_id, trade_data)
            
            # دمج النتائج
            result = {
                'allowed': local_check.get('allowed', False) and global_check.get('allowed', False),
                'local_check': local_check,
                'global_check': global_check,
                'final_recommendation': self._get_final_recommendation(local_check, global_check)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في فحص المخاطر العامة: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'suggestion': 'مراجعة إعدادات المخاطر'
            }
    
    def _check_global_limits(self, user_id: int, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """فحص الحدود العامة"""
        try:
            # حساب إجمالي الصفقات المفتوحة
            total_positions = 0
            total_margin = 0
            
            for manager in self.user_risk_managers.values():
                total_positions += len(manager.positions)
                total_margin += sum(pos.margin_used for pos in manager.positions.values())
            
            # فحص الحد الأقصى للصفقات العامة
            if total_positions > 50:  # حد أقصى 50 صفقة مفتوحة
                return {
                    'allowed': False,
                    'reason': f'إجمالي الصفقات المفتوحة {total_positions} يتجاوز الحد الأقصى',
                    'suggestion': 'إغلاق بعض الصفقات قبل فتح صفقات جديدة'
                }
            
            # فحص الحد الأقصى للهامش العام
            if total_margin > self.global_settings['global_position_limit']:
                return {
                    'allowed': False,
                    'reason': f'إجمالي الهامش المستخدم {total_margin} يتجاوز الحد الأقصى',
                    'suggestion': 'تقليل حجم الصفقات أو إغلاق بعض الصفقات'
                }
            
            return {
                'allowed': True,
                'reason': 'جميع الحدود العامة ضمن الحدود المسموحة'
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص الحدود العامة: {e}")
            return {
                'allowed': False,
                'reason': f'خطأ في فحص الحدود العامة: {e}'
            }
    
    def _get_final_recommendation(self, local_check: Dict, global_check: Dict) -> str:
        """الحصول على التوصية النهائية"""
        if not local_check.get('allowed', False):
            return local_check.get('suggestion', 'مراجعة المخاطر المحلية')
        elif not global_check.get('allowed', False):
            return global_check.get('suggestion', 'مراجعة المخاطر العامة')
        else:
            return 'التداول آمن'
    
    def get_global_risk_report(self) -> Dict[str, Any]:
        """الحصول على تقرير المخاطر العام"""
        try:
            total_users = len(self.user_risk_managers)
            total_positions = sum(len(manager.positions) for manager in self.user_risk_managers.values())
            total_margin = sum(sum(pos.margin_used for pos in manager.positions.values()) 
                             for manager in self.user_risk_managers.values())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'global_metrics': {
                    'total_users': total_users,
                    'total_positions': total_positions,
                    'total_margin_used': total_margin,
                    'average_positions_per_user': total_positions / total_users if total_users > 0 else 0
                },
                'global_settings': self.global_settings,
                'user_reports': {
                    user_id: manager.get_risk_report() 
                    for user_id, manager in self.user_risk_managers.items()
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير المخاطر العام: {e}")
            return {'error': str(e)}


# مثيل عام لمدير المخاطر
global_risk_manager = GlobalRiskManager()
