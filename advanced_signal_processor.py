#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الإشارات المتقدم - Advanced Signal Processor
يدعم تحليل الإشارات المتقدم وتقييم جودتها وتطبيق فلاتر ذكية
"""

import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import statistics

logger = logging.getLogger(__name__)

class SignalQuality(Enum):
    """جودة الإشارة"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

class SignalSource(Enum):
    """مصدر الإشارة"""
    TRADINGVIEW = "tradingview"
    TELEGRAM = "telegram"
    API = "api"
    MANUAL = "manual"
    ALGORITHM = "algorithm"

class SignalStatus(Enum):
    """حالة الإشارة"""
    PENDING = "pending"
    PROCESSING = "processing"
    EXECUTED = "executed"
    FAILED = "failed"
    GANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class SignalMetadata:
    """بيانات وصفية للإشارة"""
    source: SignalSource
    timestamp: datetime
    signal_id: str
    user_id: int
    confidence: float
    quality_score: float
    validation_status: str
    processing_time: float = 0.0
    execution_time: float = 0.0
    result: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SignalFilters:
    """فلاتر الإشارات"""
    min_confidence: float = 0.7
    max_age_seconds: int = 300  # 5 دقائق
    min_quality_score: float = 0.6
    allowed_sources: List[SignalSource] = field(default_factory=lambda: [SignalSource.TRADINGVIEW, SignalSource.API])
    max_signals_per_minute: int = 10
    duplicate_check_window: int = 60  # ثانية واحدة

@dataclass
class SignalAnalysis:
    """تحليل الإشارة"""
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    volume_score: float
    volatility_score: float
    overall_score: float
    recommendations: List[str]
    risk_factors: List[str]

class AdvancedSignalProcessor:
    """معالج الإشارات المتقدم"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.signal_history: List[SignalMetadata] = []
        self.active_signals: Dict[str, SignalMetadata] = {}
        self.filters = SignalFilters()
        self.performance_metrics = {
            'total_signals': 0,
            'successful_signals': 0,
            'failed_signals': 0,
            'average_confidence': 0.0,
            'average_quality': 0.0,
            'success_rate': 0.0
        }
        
        # إعدادات التحليل
        self.technical_indicators_enabled = True
        self.fundamental_analysis_enabled = True
        self.sentiment_analysis_enabled = True
        self.volume_analysis_enabled = True
        self.volatility_analysis_enabled = True
        
        # ذاكرة التخزين المؤقت
        self.signal_cache: Dict[str, Dict] = {}
        self.duplicate_signals: Dict[str, datetime] = {}
        
        logger.info(f"تم تهيئة معالج الإشارات المتقدم للمستخدم {user_id}")
    
    def process_signal(self, raw_signal: Dict[str, Any], 
                      market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """معالجة الإشارة المتقدمة"""
        try:
            start_time = time.time()
            
            # إنشاء معرف فريد للإشارة
            signal_id = self._generate_signal_id(raw_signal)
            
            logger.info(f"معالجة الإشارة {signal_id} للمستخدم {self.user_id}")
            
            # التحقق من التكرار
            if self._is_duplicate_signal(signal_id, raw_signal):
                return {
                    'success': False,
                    'signal_id': signal_id,
                    'message': 'إشارة مكررة - تم تجاهلها',
                    'status': SignalStatus.GANCELLED.value
                }
            
            # تحليل جودة الإشارة
            quality_analysis = self._analyze_signal_quality(raw_signal)
            
            # تطبيق الفلاتر
            filter_result = self._apply_signal_filters(raw_signal, quality_analysis)
            if not filter_result['passed']:
                return {
                    'success': False,
                    'signal_id': signal_id,
                    'message': filter_result['reason'],
                    'status': SignalStatus.GANCELLED.value,
                    'quality_analysis': quality_analysis
                }
            
            # تحليل الإشارة المتقدم
            signal_analysis = self._perform_advanced_analysis(raw_signal, market_data)
            
            # إنشاء بيانات الإشارة المحسنة
            enhanced_signal = self._create_enhanced_signal(raw_signal, signal_analysis, quality_analysis)
            
            # حفظ الإشارة
            signal_metadata = SignalMetadata(
                source=self._detect_signal_source(raw_signal),
                timestamp=datetime.now(),
                signal_id=signal_id,
                user_id=self.user_id,
                confidence=quality_analysis.get('confidence', 0.0),
                quality_score=quality_analysis.get('quality_score', 0.0),
                validation_status='validated'
            )
            
            self.signal_history.append(signal_metadata)
            self.active_signals[signal_id] = signal_metadata
            
            # تحديث المقاييس
            self._update_performance_metrics(signal_metadata)
            
            processing_time = time.time() - start_time
            signal_metadata.processing_time = processing_time
            
            logger.info(f"تم معالجة الإشارة {signal_id} بنجاح في {processing_time:.2f} ثانية")
            
            return {
                'success': True,
                'signal_id': signal_id,
                'enhanced_signal': enhanced_signal,
                'quality_analysis': quality_analysis,
                'signal_analysis': signal_analysis,
                'processing_time': processing_time,
                'status': SignalStatus.PROCESSING.value,
                'metadata': {
                    'source': signal_metadata.source.value,
                    'timestamp': signal_metadata.timestamp.isoformat(),
                    'confidence': signal_metadata.confidence,
                    'quality_score': signal_metadata.quality_score
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'signal_id': signal_id if 'signal_id' in locals() else None,
                'message': f'خطأ في معالجة الإشارة: {e}',
                'status': SignalStatus.FAILED.value
            }
    
    def _generate_signal_id(self, signal_data: Dict[str, Any]) -> str:
        """توليد معرف فريد للإشارة"""
        try:
            # إنشاء سلسلة من البيانات الأساسية
            base_string = f"{signal_data.get('symbol', '')}_{signal_data.get('action', '')}_{self.user_id}_{int(time.time())}"
            
            # إضافة بيانات إضافية للتفرد
            if 'id' in signal_data:
                base_string += f"_{signal_data['id']}"
            
            # توليد hash
            signal_hash = hashlib.md5(base_string.encode()).hexdigest()[:12]
            
            return f"SIG_{self.user_id}_{signal_hash}"
            
        except Exception as e:
            logger.error(f"خطأ في توليد معرف الإشارة: {e}")
            return f"SIG_{self.user_id}_{int(time.time())}"
    
    def _is_duplicate_signal(self, signal_id: str, signal_data: Dict[str, Any]) -> bool:
        """التحقق من تكرار الإشارة"""
        try:
            # إنشاء مفتاح للتحقق من التكرار
            duplicate_key = f"{signal_data.get('symbol', '')}_{signal_data.get('action', '')}_{self.user_id}"
            
            current_time = datetime.now()
            
            # فحص النافذة الزمنية
            if duplicate_key in self.duplicate_signals:
                last_time = self.duplicate_signals[duplicate_key]
                if (current_time - last_time).total_seconds() < self.filters.duplicate_check_window:
                    logger.warning(f"إشارة مكررة مكتشفة: {duplicate_key}")
                    return True
            
            # تحديث الوقت
            self.duplicate_signals[duplicate_key] = current_time
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من تكرار الإشارة: {e}")
            return False
    
    def _analyze_signal_quality(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل جودة الإشارة"""
        try:
            quality_scores = {}
            
            # تحليل البيانات الأساسية
            basic_score = self._analyze_basic_data(signal_data)
            quality_scores['basic_data'] = basic_score
            
            # تحليل التوقيت
            timing_score = self._analyze_timing(signal_data)
            quality_scores['timing'] = timing_score
            
            # تحليل السياق
            context_score = self._analyze_context(signal_data)
            quality_scores['context'] = context_score
            
            # تحليل الاتساق
            consistency_score = self._analyze_consistency(signal_data)
            quality_scores['consistency'] = consistency_score
            
            # حساب النتيجة الإجمالية
            overall_score = statistics.mean([basic_score, timing_score, context_score, consistency_score])
            
            # تحديد مستوى الجودة
            if overall_score >= 0.9:
                quality_level = SignalQuality.EXCELLENT
            elif overall_score >= 0.7:
                quality_level = SignalQuality.GOOD
            elif overall_score >= 0.5:
                quality_level = SignalQuality.FAIR
            elif overall_score >= 0.3:
                quality_level = SignalQuality.POOR
            else:
                quality_level = SignalQuality.INVALID
            
            return {
                'overall_score': overall_score,
                'quality_level': quality_level.value,
                'detailed_scores': quality_scores,
                'confidence': overall_score,
                'quality_score': overall_score
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل جودة الإشارة: {e}")
            return {
                'overall_score': 0.0,
                'quality_level': SignalQuality.INVALID.value,
                'confidence': 0.0,
                'quality_score': 0.0,
                'error': str(e)
            }
    
    def _analyze_basic_data(self, signal_data: Dict[str, Any]) -> float:
        """تحليل البيانات الأساسية"""
        try:
            score = 0.0
            total_checks = 0
            
            # فحص الحقول المطلوبة
            required_fields = ['symbol', 'action']
            for field in required_fields:
                total_checks += 1
                if field in signal_data and signal_data[field]:
                    score += 1.0
            
            # فحص صحة الرمز
            total_checks += 1
            symbol = signal_data.get('symbol', '')
            if len(symbol) >= 6 and symbol.isupper():
                score += 1.0
            
            # فحص صحة الإجراء
            total_checks += 1
            action = signal_data.get('action', '').lower()
            valid_actions = ['buy', 'sell', 'close', 'long', 'short', 'close_long', 'close_short']
            if action in valid_actions:
                score += 1.0
            
            return score / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"خطأ في تحليل البيانات الأساسية: {e}")
            return 0.0
    
    def _analyze_timing(self, signal_data: Dict[str, Any]) -> float:
        """تحليل التوقيت"""
        try:
            # فحص وجود timestamp
            if 'timestamp' in signal_data:
                signal_time = datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.now()
                age_seconds = (current_time - signal_time).total_seconds()
                
                # تقليل النتيجة مع زيادة العمر
                if age_seconds < 60:  # أقل من دقيقة
                    return 1.0
                elif age_seconds < 300:  # أقل من 5 دقائق
                    return 0.8
                elif age_seconds < 900:  # أقل من 15 دقيقة
                    return 0.6
                else:
                    return 0.3
            
            return 0.5  # قيمة افتراضية إذا لم يكن هناك timestamp
            
        except Exception as e:
            logger.error(f"خطأ في تحليل التوقيت: {e}")
            return 0.5
    
    def _analyze_context(self, signal_data: Dict[str, Any]) -> float:
        """تحليل السياق"""
        try:
            score = 0.0
            total_checks = 0
            
            # فحص وجود معلومات إضافية
            context_fields = ['price', 'amount', 'leverage', 'market_type']
            for field in context_fields:
                total_checks += 1
                if field in signal_data and signal_data[field]:
                    score += 0.5
            
            # فحص وجود معرف الإشارة
            if 'id' in signal_data and signal_data['id']:
                score += 0.5
                total_checks += 1
            
            # فحص وجود معلومات إضافية
            if 'notes' in signal_data or 'description' in signal_data:
                score += 0.3
                total_checks += 1
            
            return score / total_checks if total_checks > 0 else 0.5
            
        except Exception as e:
            logger.error(f"خطأ في تحليل السياق: {e}")
            return 0.5
    
    def _analyze_consistency(self, signal_data: Dict[str, Any]) -> float:
        """تحليل الاتساق"""
        try:
            # فحص الاتساق مع الإشارات السابقة
            symbol = signal_data.get('symbol', '')
            action = signal_data.get('action', '').lower()
            
            # البحث عن إشارات مشابهة حديثة
            recent_signals = [
                sig for sig in self.signal_history[-10:]  # آخر 10 إشارات
                if sig.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            similar_signals = [
                sig for sig in recent_signals
                if self._signals_similar(signal_data, sig)
            ]
            
            # تقليل النتيجة إذا كان هناك تكرار مفرط
            if len(similar_signals) > 3:
                return 0.3
            elif len(similar_signals) > 1:
                return 0.6
            else:
                return 1.0
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الاتساق: {e}")
            return 0.7
    
    def _signals_similar(self, signal1: Dict[str, Any], signal2: SignalMetadata) -> bool:
        """فحص تشابه الإشارات"""
        try:
            # مقارنة الرمز والإجراء
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return True  # مؤقتاً
            
        except Exception as e:
            logger.error(f"خطأ في فحص تشابه الإشارات: {e}")
            return False
    
    def _apply_signal_filters(self, signal_data: Dict[str, Any], 
                            quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """تطبيق فلاتر الإشارات"""
        try:
            # فحص الثقة
            confidence = quality_analysis.get('confidence', 0.0)
            if confidence < self.filters.min_confidence:
                return {
                    'passed': False,
                    'reason': f'ثقة الإشارة {confidence:.2f} أقل من الحد الأدنى {self.filters.min_confidence}'
                }
            
            # فحص جودة الإشارة
            quality_score = quality_analysis.get('quality_score', 0.0)
            if quality_score < self.filters.min_quality_score:
                return {
                    'passed': False,
                    'reason': f'جودة الإشارة {quality_score:.2f} أقل من الحد الأدنى {self.filters.min_quality_score}'
                }
            
            # فحص العمر
            if 'timestamp' in signal_data:
                signal_time = datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00'))
                age_seconds = (datetime.now() - signal_time).total_seconds()
                if age_seconds > self.filters.max_age_seconds:
                    return {
                        'passed': False,
                        'reason': f'عمر الإشارة {age_seconds:.0f} ثانية أكبر من الحد الأقصى {self.filters.max_age_seconds}'
                    }
            
            # فحص المصدر
            source = self._detect_signal_source(signal_data)
            if source not in self.filters.allowed_sources:
                return {
                    'passed': False,
                    'reason': f'مصدر الإشارة {source.value} غير مسموح'
                }
            
            # فحص معدل الإشارات
            recent_signals = [
                sig for sig in self.signal_history
                if sig.timestamp > datetime.now() - timedelta(minutes=1)
            ]
            if len(recent_signals) >= self.filters.max_signals_per_minute:
                return {
                    'passed': False,
                    'reason': f'معدل الإشارات {len(recent_signals)} في الدقيقة يتجاوز الحد الأقصى {self.filters.max_signals_per_minute}'
                }
            
            return {
                'passed': True,
                'reason': 'جميع الفلاتر تم اجتيازها بنجاح'
            }
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق فلاتر الإشارات: {e}")
            return {
                'passed': False,
                'reason': f'خطأ في تطبيق الفلاتر: {e}'
            }
    
    def _detect_signal_source(self, signal_data: Dict[str, Any]) -> SignalSource:
        """تحديد مصدر الإشارة"""
        try:
            # فحص وجود معرف TradingView
            if 'id' in signal_data and signal_data['id'].startswith('TV_'):
                return SignalSource.TRADINGVIEW
            
            # فحص وجود معرف Telegram
            if 'telegram_id' in signal_data or 'chat_id' in signal_data:
                return SignalSource.TELEGRAM
            
            # فحص وجود API headers
            if 'api_key' in signal_data or 'source' in signal_data:
                return SignalSource.API
            
            # افتراض أنه يدوي
            return SignalSource.MANUAL
            
        except Exception as e:
            logger.error(f"خطأ في تحديد مصدر الإشارة: {e}")
            return SignalSource.MANUAL
    
    def _perform_advanced_analysis(self, signal_data: Dict[str, Any], 
                                 market_data: Dict[str, Any] = None) -> SignalAnalysis:
        """إجراء تحليل متقدم للإشارة"""
        try:
            # تحليل تقني
            technical_score = self._perform_technical_analysis(signal_data, market_data)
            
            # تحليل أساسي
            fundamental_score = self._perform_fundamental_analysis(signal_data, market_data)
            
            # تحليل المشاعر
            sentiment_score = self._perform_sentiment_analysis(signal_data, market_data)
            
            # تحليل الحجم
            volume_score = self._perform_volume_analysis(signal_data, market_data)
            
            # تحليل التقلبات
            volatility_score = self._perform_volatility_analysis(signal_data, market_data)
            
            # حساب النتيجة الإجمالية
            scores = [technical_score, fundamental_score, sentiment_score, volume_score, volatility_score]
            overall_score = statistics.mean([s for s in scores if s is not None])
            
            # إنشاء التوصيات
            recommendations = self._generate_recommendations(signal_data, scores)
            
            # تحديد عوامل المخاطرة
            risk_factors = self._identify_risk_factors(signal_data, scores)
            
            return SignalAnalysis(
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                sentiment_score=sentiment_score,
                volume_score=volume_score,
                volatility_score=volatility_score,
                overall_score=overall_score,
                recommendations=recommendations,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"خطأ في التحليل المتقدم: {e}")
            return SignalAnalysis(
                technical_score=0.5,
                fundamental_score=0.5,
                sentiment_score=0.5,
                volume_score=0.5,
                volatility_score=0.5,
                overall_score=0.5,
                recommendations=['تحليل غير متاح'],
                risk_factors=['خطأ في التحليل']
            )
    
    def _perform_technical_analysis(self, signal_data: Dict[str, Any], 
                                  market_data: Dict[str, Any] = None) -> float:
        """التحليل التقني"""
        try:
            if not self.technical_indicators_enabled or not market_data:
                return 0.5
            
            # تحليل المؤشرات التقنية
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return 0.7
            
        except Exception as e:
            logger.error(f"خطأ في التحليل التقني: {e}")
            return 0.5
    
    def _perform_fundamental_analysis(self, signal_data: Dict[str, Any], 
                                    market_data: Dict[str, Any] = None) -> float:
        """التحليل الأساسي"""
        try:
            if not self.fundamental_analysis_enabled:
                return 0.5
            
            # تحليل البيانات الأساسية
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return 0.6
            
        except Exception as e:
            logger.error(f"خطأ في التحليل الأساسي: {e}")
            return 0.5
    
    def _perform_sentiment_analysis(self, signal_data: Dict[str, Any], 
                                  market_data: Dict[str, Any] = None) -> float:
        """تحليل المشاعر"""
        try:
            if not self.sentiment_analysis_enabled:
                return 0.5
            
            # تحليل المشاعر
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return 0.65
            
        except Exception as e:
            logger.error(f"خطأ في تحليل المشاعر: {e}")
            return 0.5
    
    def _perform_volume_analysis(self, signal_data: Dict[str, Any], 
                               market_data: Dict[str, Any] = None) -> float:
        """تحليل الحجم"""
        try:
            if not self.volume_analysis_enabled or not market_data:
                return 0.5
            
            # تحليل الحجم
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return 0.7
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الحجم: {e}")
            return 0.5
    
    def _perform_volatility_analysis(self, signal_data: Dict[str, Any], 
                                   market_data: Dict[str, Any] = None) -> float:
        """تحليل التقلبات"""
        try:
            if not self.volatility_analysis_enabled or not market_data:
                return 0.5
            
            # تحليل التقلبات
            # هذا تبسيط - يمكن تحسينه لاحقاً
            return 0.6
            
        except Exception as e:
            logger.error(f"خطأ في تحليل التقلبات: {e}")
            return 0.5
    
    def _generate_recommendations(self, signal_data: Dict[str, Any], scores: List[float]) -> List[str]:
        """توليد التوصيات"""
        try:
            recommendations = []
            
            # توصيات بناءً على النتائج
            if scores[0] > 0.8:  # تحليل تقني جيد
                recommendations.append("الإشارة مدعومة بقوة بالتحليل التقني")
            
            if scores[1] > 0.8:  # تحليل أساسي جيد
                recommendations.append("الإشارة مدعومة بالتحليل الأساسي")
            
            if scores[2] > 0.8:  # مشاعر إيجابية
                recommendations.append("المشاعر السوقية إيجابية")
            
            if scores[3] > 0.8:  # حجم جيد
                recommendations.append("الحجم يدعم الإشارة")
            
            if scores[4] < 0.3:  # تقلبات منخفضة
                recommendations.append("التقلبات منخفضة - مخاطرة أقل")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"خطأ في توليد التوصيات: {e}")
            return []
    
    def _identify_risk_factors(self, signal_data: Dict[str, Any], scores: List[float]) -> List[str]:
        """تحديد عوامل المخاطرة"""
        try:
            risk_factors = []
            
            # عوامل المخاطرة بناءً على النتائج
            if scores[0] < 0.4:  # تحليل تقني ضعيف
                risk_factors.append("التحليل التقني ضعيف")
            
            if scores[1] < 0.4:  # تحليل أساسي ضعيف
                risk_factors.append("التحليل الأساسي ضعيف")
            
            if scores[2] < 0.4:  # مشاعر سلبية
                risk_factors.append("المشاعر السوقية سلبية")
            
            if scores[3] < 0.4:  # حجم ضعيف
                risk_factors.append("الحجم ضعيف")
            
            if scores[4] > 0.8:  # تقلبات عالية
                risk_factors.append("التقلبات عالية - مخاطرة أكبر")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"خطأ في تحديد عوامل المخاطرة: {e}")
            return []
    
    def _create_enhanced_signal(self, raw_signal: Dict[str, Any], 
                              signal_analysis: SignalAnalysis, 
                              quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء إشارة محسنة"""
        try:
            enhanced_signal = raw_signal.copy()
            
            # إضافة التحليل
            enhanced_signal['analysis'] = {
                'technical_score': signal_analysis.technical_score,
                'fundamental_score': signal_analysis.fundamental_score,
                'sentiment_score': signal_analysis.sentiment_score,
                'volume_score': signal_analysis.volume_score,
                'volatility_score': signal_analysis.volatility_score,
                'overall_score': signal_analysis.overall_score,
                'recommendations': signal_analysis.recommendations,
                'risk_factors': signal_analysis.risk_factors
            }
            
            # إضافة معلومات الجودة
            enhanced_signal['quality'] = quality_analysis
            
            # إضافة معلومات إضافية
            enhanced_signal['enhanced_metadata'] = {
                'processed_at': datetime.now().isoformat(),
                'processor_version': '2.0',
                'user_id': self.user_id,
                'confidence_level': quality_analysis.get('confidence', 0.0),
                'quality_level': quality_analysis.get('quality_level', 'unknown')
            }
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الإشارة المحسنة: {e}")
            return raw_signal
    
    def _update_performance_metrics(self, signal_metadata: SignalMetadata):
        """تحديث مقاييس الأداء"""
        try:
            self.performance_metrics['total_signals'] += 1
            
            # تحديث متوسط الثقة
            total_confidence = sum(sig.confidence for sig in self.signal_history)
            self.performance_metrics['average_confidence'] = total_confidence / len(self.signal_history)
            
            # تحديث متوسط الجودة
            total_quality = sum(sig.quality_score for sig in self.signal_history)
            self.performance_metrics['average_quality'] = total_quality / len(self.signal_history)
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مقاييس الأداء: {e}")
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الإشارات"""
        try:
            total_signals = len(self.signal_history)
            if total_signals == 0:
                return {'total_signals': 0, 'message': 'لا توجد إشارات معالجة'}
            
            # إحصائيات الجودة
            quality_distribution = {}
            for quality in SignalQuality:
                count = sum(1 for sig in self.signal_history 
                           if sig.quality_score >= self._get_quality_threshold(quality))
                quality_distribution[quality.value] = count
            
            # إحصائيات المصادر
            source_distribution = {}
            for source in SignalSource:
                count = sum(1 for sig in self.signal_history if sig.source == source)
                source_distribution[source.value] = count
            
            return {
                'total_signals': total_signals,
                'average_confidence': self.performance_metrics['average_confidence'],
                'average_quality': self.performance_metrics['average_quality'],
                'quality_distribution': quality_distribution,
                'source_distribution': source_distribution,
                'performance_metrics': self.performance_metrics,
                'filters': {
                    'min_confidence': self.filters.min_confidence,
                    'min_quality_score': self.filters.min_quality_score,
                    'max_age_seconds': self.filters.max_age_seconds,
                    'allowed_sources': [s.value for s in self.filters.allowed_sources]
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الإشارات: {e}")
            return {'error': str(e)}
    
    def _get_quality_threshold(self, quality: SignalQuality) -> float:
        """الحصول على عتبة الجودة"""
        thresholds = {
            SignalQuality.EXCELLENT: 0.9,
            SignalQuality.GOOD: 0.7,
            SignalQuality.FAIR: 0.5,
            SignalQuality.POOR: 0.3,
            SignalQuality.INVALID: 0.0
        }
        return thresholds.get(quality, 0.0)
    
    def update_filters(self, new_filters: Dict[str, Any]) -> bool:
        """تحديث فلاتر الإشارات"""
        try:
            for key, value in new_filters.items():
                if hasattr(self.filters, key):
                    setattr(self.filters, key, value)
            
            logger.info(f"تم تحديث فلاتر الإشارات للمستخدم {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث فلاتر الإشارات: {e}")
            return False


# مدير الإشارات العام
class GlobalSignalManager:
    """مدير الإشارات العام لجميع المستخدمين"""
    
    def __init__(self):
        self.user_processors: Dict[int, AdvancedSignalProcessor] = {}
        self.global_statistics = {
            'total_signals_processed': 0,
            'average_processing_time': 0.0,
            'success_rate': 0.0
        }
    
    def get_signal_processor(self, user_id: int) -> AdvancedSignalProcessor:
        """الحصول على معالج الإشارات للمستخدم"""
        if user_id not in self.user_processors:
            self.user_processors[user_id] = AdvancedSignalProcessor(user_id)
        return self.user_processors[user_id]
    
    def process_signal_for_user(self, user_id: int, signal_data: Dict[str, Any], 
                              market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """معالجة الإشارة للمستخدم"""
        try:
            processor = self.get_signal_processor(user_id)
            result = processor.process_signal(signal_data, market_data)
            
            # تحديث الإحصائيات العامة
            if result.get('success', False):
                self.global_statistics['total_signals_processed'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة للمستخدم {user_id}: {e}")
            return {
                'success': False,
                'message': f'خطأ في معالجة الإشارة: {e}',
                'status': SignalStatus.FAILED.value
            }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        try:
            user_stats = {}
            for user_id, processor in self.user_processors.items():
                user_stats[user_id] = processor.get_signal_statistics()
            
            return {
                'global_statistics': self.global_statistics,
                'user_statistics': user_stats,
                'total_users': len(self.user_processors)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات العامة: {e}")
            return {'error': str(e)}


# مثيل عام لمدير الإشارات
global_signal_manager = GlobalSignalManager()
