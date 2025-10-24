"""
🚀 نظام المحفظة المتطور والذكي
Ultimate Portfolio Management System

نظام محفظة شامل ومتطور يدعم:
- إدارة شاملة للمحافظ التجريبية والحقيقية
- تحليلات متقدمة للأداء
- إدارة المخاطر الذكية
- تقارير مفصلة ومؤشرات أداء
- واجهة مستخدم متطورة
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio

logger = logging.getLogger(__name__)

class AccountType(Enum):
    DEMO = "demo"
    REAL = "real"

class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    BOTH = "both"

class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"

@dataclass
class Position:
    """صفقة في المحفظة"""
    id: str
    symbol: str
    side: str
    entry_price: float
    quantity: float
    current_price: float
    market_type: str
    account_type: str
    leverage: int
    status: PositionStatus
    created_at: datetime
    updated_at: datetime
    signal_id: Optional[str] = None
    notes: str = ""
    
    @property
    def market_value(self) -> float:
        """القيمة السوقية الحالية"""
        return self.quantity * self.current_price
    
    @property
    def entry_value(self) -> float:
        """قيمة الدخول"""
        return self.quantity * self.entry_price
    
    @property
    def pnl_absolute(self) -> float:
        """الربح/الخسارة المطلق"""
        return self.market_value - self.entry_value
    
    @property
    def pnl_percentage(self) -> float:
        """الربح/الخسارة بالنسبة المئوية"""
        if self.entry_value == 0:
            return 0
        return (self.pnl_absolute / self.entry_value) * 100
    
    @property
    def is_profitable(self) -> bool:
        """هل الصفقة رابحة؟"""
        return self.pnl_absolute > 0

@dataclass
class PortfolioSummary:
    """ملخص المحفظة"""
    total_value: float
    total_invested: float
    total_pnl: float
    pnl_percentage: float
    open_positions: int
    closed_positions: int
    win_rate: float
    best_trade: float
    worst_trade: float
    avg_trade: float
    sharpe_ratio: float
    max_drawdown: float
    last_updated: datetime

class UltimatePortfolioManager:
    """مدير المحفظة المتطور والذكي"""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.closed_positions: Dict[str, Position] = {}
        self.portfolio_history: List[Dict] = []
        self.risk_settings: Dict = {}
        self.performance_metrics: Dict = {}
        
    async def add_position(self, position_data: Dict[str, Any]) -> bool:
        """إضافة صفقة جديدة للمحفظة"""
        try:
            position_id = position_data.get('id', f"pos_{len(self.positions) + 1}")
            
            position = Position(
                id=position_id,
                symbol=position_data['symbol'],
                side=position_data['side'],
                entry_price=position_data['entry_price'],
                quantity=position_data['quantity'],
                current_price=position_data.get('current_price', position_data['entry_price']),
                market_type=position_data['market_type'],
                account_type=position_data['account_type'],
                leverage=position_data.get('leverage', 1),
                status=PositionStatus.OPEN,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                signal_id=position_data.get('signal_id'),
                notes=position_data.get('notes', '')
            )
            
            # إضافة للمحفظة
            self.positions[position_id] = position
            
            # تحديث إحصائيات الأداء
            await self._update_performance_metrics()
            
            logger.info(f"✅ تم إضافة صفقة جديدة: {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة الصفقة: {e}")
            return False
    
    async def update_position(self, position_id: str, updates: Dict[str, Any]) -> bool:
        """تحديث صفقة موجودة"""
        try:
            if position_id not in self.positions:
                logger.warning(f"⚠️ الصفقة غير موجودة: {position_id}")
                return False
            
            position = self.positions[position_id]
            
            # تحديث الحقول
            for field, value in updates.items():
                if hasattr(position, field):
                    setattr(position, field, value)
            
            position.updated_at = datetime.now()
            
            # تحديث إحصائيات الأداء
            await self._update_performance_metrics()
            
            logger.info(f"✅ تم تحديث الصفقة: {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث الصفقة: {e}")
            return False
    
    async def close_position(self, position_id: str, exit_price: float, reason: str = "") -> bool:
        """إغلاق صفقة"""
        try:
            if position_id not in self.positions:
                logger.warning(f"⚠️ الصفقة غير موجودة: {position_id}")
                return False
            
            position = self.positions[position_id]
            position.current_price = exit_price
            position.status = PositionStatus.CLOSED
            position.updated_at = datetime.now()
            
            if reason:
                position.notes += f" | إغلاق: {reason}"
            
            # نقل للصفقات المغلقة
            self.closed_positions[position_id] = position
            del self.positions[position_id]
            
            # تحديث إحصائيات الأداء
            await self._update_performance_metrics()
            
            logger.info(f"✅ تم إغلاق الصفقة: {position_id}, الربح/الخسارة: {position.pnl_absolute:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إغلاق الصفقة: {e}")
            return False
    
    async def get_portfolio_summary(self, account_type: str = "demo") -> PortfolioSummary:
        """الحصول على ملخص المحفظة"""
        try:
            # تصفية الصفقات حسب نوع الحساب
            account_positions = [p for p in self.positions.values() if p.account_type == account_type]
            account_closed = [p for p in self.closed_positions.values() if p.account_type == account_type]
            
            # حساب القيم الأساسية
            total_value = sum(p.market_value for p in account_positions)
            total_invested = sum(p.entry_value for p in account_positions)
            total_pnl = sum(p.pnl_absolute for p in account_positions + account_closed)
            
            # حساب النسب المئوية
            pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            # إحصائيات الصفقات
            open_positions = len(account_positions)
            closed_positions = len(account_closed)
            
            # معدل النجاح
            winning_trades = [p for p in account_closed if p.pnl_absolute > 0]
            win_rate = (len(winning_trades) / len(account_closed) * 100) if account_closed else 0
            
            # أفضل وأسوأ صفقة
            if account_closed:
                best_trade = max(p.pnl_absolute for p in account_closed)
                worst_trade = min(p.pnl_absolute for p in account_closed)
                avg_trade = sum(p.pnl_absolute for p in account_closed) / len(account_closed)
            else:
                best_trade = worst_trade = avg_trade = 0
            
            # مؤشرات الأداء المتقدمة
            sharpe_ratio = await self._calculate_sharpe_ratio(account_closed)
            max_drawdown = await self._calculate_max_drawdown(account_closed)
            
            return PortfolioSummary(
                total_value=total_value,
                total_invested=total_invested,
                total_pnl=total_pnl,
                pnl_percentage=pnl_percentage,
                open_positions=open_positions,
                closed_positions=closed_positions,
                win_rate=win_rate,
                best_trade=best_trade,
                worst_trade=worst_trade,
                avg_trade=avg_trade,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب ملخص المحفظة: {e}")
            return PortfolioSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, datetime.now())
    
    async def get_performance_analytics(self, account_type: str = "demo", period_days: int = 30) -> Dict:
        """تحليلات الأداء المتقدمة"""
        try:
            # تصفية الصفقات حسب الفترة
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            account_positions = [p for p in self.positions.values() if p.account_type == account_type]
            account_closed = [
                p for p in self.closed_positions.values() 
                if p.account_type == account_type and p.created_at >= start_date
            ]
            
            # تحليل الأداء اليومي
            daily_pnl = await self._calculate_daily_pnl(account_closed, period_days)
            
            # تحليل الأداء الشهري
            monthly_pnl = await self._calculate_monthly_pnl(account_closed)
            
            # تحليل الأداء حسب العملة
            currency_analysis = await self._analyze_by_currency(account_closed)
            
            # تحليل الأداء حسب نوع السوق
            market_analysis = await self._analyze_by_market_type(account_closed)
            
            # تحليل المخاطر
            risk_analysis = await self._analyze_risk_metrics(account_closed)
            
            return {
                'period': f"{period_days} days",
                'daily_pnl': daily_pnl,
                'monthly_pnl': monthly_pnl,
                'currency_analysis': currency_analysis,
                'market_analysis': market_analysis,
                'risk_analysis': risk_analysis,
                'total_trades': len(account_closed),
                'winning_trades': len([p for p in account_closed if p.pnl_absolute > 0]),
                'losing_trades': len([p for p in account_closed if p.pnl_absolute < 0]),
                'avg_win': sum(p.pnl_absolute for p in account_closed if p.pnl_absolute > 0) / max(len([p for p in account_closed if p.pnl_absolute > 0]), 1),
                'avg_loss': sum(p.pnl_absolute for p in account_closed if p.pnl_absolute < 0) / max(len([p for p in account_closed if p.pnl_absolute < 0]), 1),
                'profit_factor': abs(sum(p.pnl_absolute for p in account_closed if p.pnl_absolute > 0) / sum(p.pnl_absolute for p in account_closed if p.pnl_absolute < 0)) if any(p.pnl_absolute < 0 for p in account_closed) else float('inf')
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل الأداء: {e}")
            return {}
    
    async def get_portfolio_recommendations(self, account_type: str = "demo") -> List[Dict]:
        """توصيات ذكية للمحفظة"""
        try:
            recommendations = []
            
            # تحليل الصفقات المفتوحة
            open_positions = [p for p in self.positions.values() if p.account_type == account_type]
            
            # توصية لتأمين الأرباح
            profitable_positions = [p for p in open_positions if p.pnl_percentage > 10]
            if profitable_positions:
                recommendations.append({
                    'type': 'take_profit',
                    'priority': 'high',
                    'title': 'تأمين الأرباح',
                    'description': f'لديك {len(profitable_positions)} صفقة رابحة بأكثر من 10%',
                    'action': 'فكر في إغلاق جزئي لتأمين الأرباح'
                })
            
            # توصية لإدارة المخاطر
            losing_positions = [p for p in open_positions if p.pnl_percentage < -5]
            if losing_positions:
                recommendations.append({
                    'type': 'risk_management',
                    'priority': 'high',
                    'title': 'إدارة المخاطر',
                    'description': f'لديك {len(losing_positions)} صفقة خاسرة بأكثر من 5%',
                    'action': 'فكر في وضع Stop Loss أو إغلاق الصفقات الخاسرة'
                })
            
            # توصية للتنويع
            if len(open_positions) > 0:
                symbols = set(p.symbol for p in open_positions)
                if len(symbols) < 3:
                    recommendations.append({
                        'type': 'diversification',
                        'priority': 'medium',
                        'title': 'تنويع المحفظة',
                        'description': f'محفظتك تحتوي على {len(symbols)} عملة فقط',
                        'action': 'فكر في التنويع لتقليل المخاطر'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء التوصيات: {e}")
            return []
    
    async def _update_performance_metrics(self):
        """تحديث مؤشرات الأداء"""
        try:
            # حفظ تاريخ المحفظة
            portfolio_snapshot = {
                'timestamp': datetime.now().isoformat(),
                'total_positions': len(self.positions),
                'total_closed': len(self.closed_positions),
                'total_value': sum(p.market_value for p in self.positions.values()),
                'total_pnl': sum(p.pnl_absolute for p in self.positions.values())
            }
            
            self.portfolio_history.append(portfolio_snapshot)
            
            # الاحتفاظ بآخر 100 نقطة فقط
            if len(self.portfolio_history) > 100:
                self.portfolio_history = self.portfolio_history[-100:]
                
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث مؤشرات الأداء: {e}")
    
    async def _calculate_sharpe_ratio(self, positions: List[Position]) -> float:
        """حساب نسبة شارب"""
        try:
            if not positions:
                return 0
            
            returns = [p.pnl_percentage for p in positions]
            if not returns:
                return 0
            
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            
            if std_return == 0:
                return 0
            
            # افتراض معدل خالي من المخاطر = 0%
            risk_free_rate = 0
            return (avg_return - risk_free_rate) / std_return
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب نسبة شارب: {e}")
            return 0
    
    async def _calculate_max_drawdown(self, positions: List[Position]) -> float:
        """حساب أقصى انخفاض"""
        try:
            if not positions:
                return 0
            
            # ترتيب الصفقات حسب التاريخ
            sorted_positions = sorted(positions, key=lambda p: p.created_at)
            
            peak = 0
            max_drawdown = 0
            
            for position in sorted_positions:
                if position.pnl_absolute > peak:
                    peak = position.pnl_absolute
                
                drawdown = peak - position.pnl_absolute
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return max_drawdown
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب أقصى انخفاض: {e}")
            return 0
    
    async def _calculate_daily_pnl(self, positions: List[Position], days: int) -> List[Dict]:
        """حساب الربح/الخسارة اليومي"""
        try:
            daily_pnl = {}
            
            for position in positions:
                date = position.created_at.date()
                if date not in daily_pnl:
                    daily_pnl[date] = 0
                daily_pnl[date] += position.pnl_absolute
            
            # تحويل إلى قائمة مرتبة
            result = []
            for date, pnl in sorted(daily_pnl.items()):
                result.append({
                    'date': date.isoformat(),
                    'pnl': pnl
                })
            
            return result[-days:]  # آخر N أيام
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب الربح اليومي: {e}")
            return []
    
    async def _calculate_monthly_pnl(self, positions: List[Position]) -> List[Dict]:
        """حساب الربح/الخسارة الشهري"""
        try:
            monthly_pnl = {}
            
            for position in positions:
                month_key = position.created_at.strftime('%Y-%m')
                if month_key not in monthly_pnl:
                    monthly_pnl[month_key] = 0
                monthly_pnl[month_key] += position.pnl_absolute
            
            # تحويل إلى قائمة مرتبة
            result = []
            for month, pnl in sorted(monthly_pnl.items()):
                result.append({
                    'month': month,
                    'pnl': pnl
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في حساب الربح الشهري: {e}")
            return []
    
    async def _analyze_by_currency(self, positions: List[Position]) -> Dict:
        """تحليل الأداء حسب العملة"""
        try:
            currency_stats = {}
            
            for position in positions:
                symbol = position.symbol
                if symbol not in currency_stats:
                    currency_stats[symbol] = {
                        'total_trades': 0,
                        'winning_trades': 0,
                        'total_pnl': 0,
                        'avg_pnl': 0
                    }
                
                stats = currency_stats[symbol]
                stats['total_trades'] += 1
                stats['total_pnl'] += position.pnl_absolute
                
                if position.pnl_absolute > 0:
                    stats['winning_trades'] += 1
            
            # حساب المتوسطات
            for symbol, stats in currency_stats.items():
                if stats['total_trades'] > 0:
                    stats['avg_pnl'] = stats['total_pnl'] / stats['total_trades']
                    stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
            
            return currency_stats
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل العملات: {e}")
            return {}
    
    async def _analyze_by_market_type(self, positions: List[Position]) -> Dict:
        """تحليل الأداء حسب نوع السوق"""
        try:
            market_stats = {}
            
            for position in positions:
                market_type = position.market_type
                if market_type not in market_stats:
                    market_stats[market_type] = {
                        'total_trades': 0,
                        'winning_trades': 0,
                        'total_pnl': 0,
                        'avg_pnl': 0
                    }
                
                stats = market_stats[market_type]
                stats['total_trades'] += 1
                stats['total_pnl'] += position.pnl_absolute
                
                if position.pnl_absolute > 0:
                    stats['winning_trades'] += 1
            
            # حساب المتوسطات
            for market_type, stats in market_stats.items():
                if stats['total_trades'] > 0:
                    stats['avg_pnl'] = stats['total_pnl'] / stats['total_trades']
                    stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
            
            return market_stats
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل أنواع السوق: {e}")
            return {}
    
    async def _analyze_risk_metrics(self, positions: List[Position]) -> Dict:
        """تحليل مؤشرات المخاطر"""
        try:
            if not positions:
                return {}
            
            pnls = [p.pnl_absolute for p in positions]
            
            # حساب الانحراف المعياري
            mean_pnl = sum(pnls) / len(pnls)
            variance = sum((pnl - mean_pnl) ** 2 for pnl in pnls) / len(pnls)
            std_deviation = variance ** 0.5
            
            # حساب معامل الاختلاف
            cv = (std_deviation / abs(mean_pnl)) if mean_pnl != 0 else 0
            
            # حساب القيمة المعرضة للمخاطر (VaR)
            sorted_pnls = sorted(pnls)
            var_95 = sorted_pnls[int(len(sorted_pnls) * 0.05)] if len(sorted_pnls) > 20 else min(pnls)
            
            return {
                'standard_deviation': std_deviation,
                'coefficient_of_variation': cv,
                'var_95': var_95,
                'max_loss': min(pnls),
                'max_gain': max(pnls),
                'risk_score': min(cv * 100, 100)  # درجة مخاطر من 0-100
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل المخاطر: {e}")
            return {}

# إنشاء مثيل عام للمدير
ultimate_portfolio_manager = UltimatePortfolioManager()
