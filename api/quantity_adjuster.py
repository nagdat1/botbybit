"""
أداة الشراء التقريبي الذكية
تعمل مع جميع المنصات لتجنب أخطاء الكمية
"""

import logging
from typing import Dict, Optional, Tuple, List
from decimal import Decimal, ROUND_DOWN, ROUND_UP

logger = logging.getLogger(__name__)

class QuantityAdjuster:
    """فئة لتعديل الكمية بذكاء لتجنب أخطاء المنصات"""
    
    # قواعد التقريب لكل منصة
    EXCHANGE_RULES = {
        'bybit': {
            'min_qty': 0.001,
            'max_precision': 6,
            'step_size': 0.001,
            'min_notional': 10.0  # USDT
        },
        'binance': {
            'min_qty': 0.001,
            'max_precision': 8,
            'step_size': 0.001,
            'min_notional': 10.0  # USDT
        },
        'bitget': {
            'min_qty': 0.001,
            'max_precision': 6,
            'step_size': 0.001,
            'min_notional': 5.0  # USDT
        },
        'okx': {
            'min_qty': 0.001,
            'max_precision': 8,
            'step_size': 0.001,
            'min_notional': 10.0  # USDT
        }
    }
    
    @staticmethod
    def adjust_quantity_for_exchange(qty: float, price: float, exchange: str, 
                                   symbol: str = None, market_type: str = 'futures') -> Tuple[float, Dict]:
        """
        تعديل الكمية حسب قواعد المنصة
        
        Args:
            qty: الكمية الأصلية
            price: السعر الحالي
            exchange: اسم المنصة
            symbol: رمز العملة (اختياري)
            market_type: نوع السوق (futures/spot)
            
        Returns:
            tuple: (الكمية المعدلة, معلومات التعديل)
        """
        try:
            exchange = exchange.lower()
            rules = QuantityAdjuster.EXCHANGE_RULES.get(exchange, QuantityAdjuster.EXCHANGE_RULES['bybit'])
            
            logger.info(f"🔧 تعديل الكمية للمنصة {exchange}")
            logger.info(f"   الكمية الأصلية: {qty}")
            logger.info(f"   السعر: {price}")
            logger.info(f"   قواعد المنصة: {rules}")
            
            # التحقق من الحد الأدنى للكمية
            if qty < rules['min_qty']:
                logger.warning(f"⚠️ الكمية أقل من الحد الأدنى: {qty} < {rules['min_qty']}")
                qty = rules['min_qty']
            
            # تطبيق step_size
            step_size = rules['step_size']
            if step_size > 0:
                qty = round(qty / step_size) * step_size
            
            # تقريب حسب دقة المنصة
            precision = rules['max_precision']
            qty = round(qty, precision)
            
            # التحقق من القيمة الإجمالية (notional value)
            notional_value = qty * price
            min_notional = rules['min_notional']
            
            if notional_value < min_notional:
                logger.warning(f"⚠️ القيمة الإجمالية أقل من المطلوب: {notional_value} < {min_notional}")
                # زيادة الكمية لتحقيق الحد الأدنى
                required_qty = min_notional / price
                qty = max(qty, required_qty)
                
                # إعادة تطبيق القواعد
                if step_size > 0:
                    qty = round(qty / step_size) * step_size
                qty = round(qty, precision)
            
            adjustment_info = {
                'adjusted': True,
                'original_qty': qty,
                'final_qty': qty,
                'notional_value': qty * price,
                'exchange': exchange,
                'rules_applied': rules
            }
            
            logger.info(f"✅ الكمية المعدلة: {qty}")
            logger.info(f"   القيمة الإجمالية: {qty * price:.2f} USDT")
            
            return qty, adjustment_info
            
        except Exception as e:
            logger.error(f"❌ خطأ في تعديل الكمية: {e}")
            return qty, {'adjusted': False, 'error': str(e)}
    
    @staticmethod
    def smart_quantity_adjustment(qty: float, price: float, trade_amount: float, 
                                leverage: int = 1, exchange: str = 'bybit') -> float:
        """
        تعديل ذكي للكمية بناءً على المبلغ والرافعة
        
        Args:
            qty: الكمية الأصلية
            price: السعر الحالي
            trade_amount: المبلغ المطلوب
            leverage: الرافعة المالية
            exchange: المنصة
            
        Returns:
            الكمية المعدلة
        """
        try:
            logger.info(f"🧠 التعديل الذكي للكمية:")
            logger.info(f"   المدخلات: qty={qty}, price={price}, amount={trade_amount}, leverage={leverage}")
            
            # إعادة حساب الكمية من المبلغ والرافعة
            if trade_amount > 0 and price > 0:
                calculated_qty = (trade_amount * leverage) / price
                logger.info(f"   الكمية المحسوبة من المبلغ: {calculated_qty}")
                
                # استخدام الكمية المحسوبة إذا كانت مختلفة كثيراً عن الأصلية
                if abs(calculated_qty - qty) / qty > 0.1:  # فرق أكثر من 10%
                    logger.info(f"   استخدام الكمية المحسوبة بدلاً من الأصلية")
                    qty = calculated_qty
            
            # تطبيق قواعد المنصة
            adjusted_qty, _ = QuantityAdjuster.adjust_quantity_for_exchange(
                qty, price, exchange
            )
            
            # التحقق من المنطقية
            if adjusted_qty <= 0:
                logger.error(f"❌ الكمية المعدلة غير صالحة: {adjusted_qty}")
                return qty
            
            # التحقق من أن التعديل ليس مفرطاً
            change_ratio = abs(adjusted_qty - qty) / qty if qty > 0 else 0
            if change_ratio > 0.5:  # تغيير أكثر من 50%
                logger.warning(f"⚠️ تعديل كبير في الكمية: {qty} → {adjusted_qty} ({change_ratio:.1%})")
            
            logger.info(f"✅ النتيجة النهائية: {qty} → {adjusted_qty}")
            return adjusted_qty
            
        except Exception as e:
            logger.error(f"❌ خطأ في التعديل الذكي: {e}")
            return qty
    
    @staticmethod
    def get_multiple_quantity_options(qty: float, price: float, exchange: str = 'bybit') -> List[float]:
        """
        الحصول على خيارات متعددة للكمية للمحاولة
        
        Args:
            qty: الكمية الأصلية
            price: السعر
            exchange: المنصة
            
        Returns:
            قائمة بالكميات المقترحة
        """
        try:
            options = []
            rules = QuantityAdjuster.EXCHANGE_RULES.get(exchange.lower(), 
                                                      QuantityAdjuster.EXCHANGE_RULES['bybit'])
            
            # الكمية الأصلية معدلة
            base_qty, _ = QuantityAdjuster.adjust_quantity_for_exchange(qty, price, exchange)
            options.append(base_qty)
            
            # خيارات إضافية
            step = rules['step_size']
            precision = rules['max_precision']
            
            # كمية أكبر قليلاً
            if step > 0:
                higher_qty = round((base_qty + step), precision)
                if higher_qty != base_qty:
                    options.append(higher_qty)
            
            # كمية أصغر قليلاً (إذا كانت أكبر من الحد الأدنى)
            if step > 0:
                lower_qty = round((base_qty - step), precision)
                if lower_qty >= rules['min_qty'] and lower_qty != base_qty:
                    options.append(lower_qty)
            
            # ترتيب حسب الأولوية
            options = sorted(set(options), reverse=True)  # الأكبر أولاً
            
            logger.info(f"🎯 خيارات الكمية المقترحة: {options}")
            return options
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء خيارات الكمية: {e}")
            return [qty]
    
    @staticmethod
    def validate_quantity(qty: float, price: float, exchange: str, 
                         market_type: str = 'futures') -> Dict:
        """
        التحقق من صحة الكمية قبل إرسال الطلب
        
        Args:
            qty: الكمية
            price: السعر
            exchange: المنصة
            market_type: نوع السوق
            
        Returns:
            نتيجة التحقق
        """
        try:
            rules = QuantityAdjuster.EXCHANGE_RULES.get(exchange.lower(), 
                                                      QuantityAdjuster.EXCHANGE_RULES['bybit'])
            
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
            
            # التحقق من الحد الأدنى للكمية
            if qty < rules['min_qty']:
                validation_result['valid'] = False
                validation_result['errors'].append(f"الكمية أقل من الحد الأدنى: {qty} < {rules['min_qty']}")
                validation_result['suggestions'].append(f"استخدم كمية أكبر من {rules['min_qty']}")
            
            # التحقق من القيمة الإجمالية
            notional_value = qty * price
            if notional_value < rules['min_notional']:
                validation_result['valid'] = False
                validation_result['errors'].append(f"القيمة الإجمالية أقل من المطلوب: {notional_value:.2f} < {rules['min_notional']}")
                required_qty = rules['min_notional'] / price
                validation_result['suggestions'].append(f"استخدم كمية أكبر من {required_qty:.6f}")
            
            # التحقق من step_size
            step_size = rules['step_size']
            if step_size > 0:
                remainder = qty % step_size
                if remainder > 0.000001:  # تجنب أخطاء الفاصلة العائمة
                    validation_result['warnings'].append(f"الكمية لا تتوافق مع step_size: {step_size}")
                    suggested_qty = round(qty / step_size) * step_size
                    validation_result['suggestions'].append(f"استخدم {suggested_qty:.6f} بدلاً من {qty}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من الكمية: {e}")
            return {
                'valid': False,
                'errors': [f"خطأ في التحقق: {str(e)}"],
                'warnings': [],
                'suggestions': []
            }
