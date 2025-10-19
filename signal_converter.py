#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محول الإشارات - تحويل الإشارات البسيطة إلى التنسيق الداخلي
يدعم تنسيق الإشارات الجديد المبسط:
{
    "signal": "buy|sell|long|close_long|short|close_short",
    "symbol": "BTCUSDT",
    "id": "TV_001"
}
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalConverter:
    """محول الإشارات من التنسيق البسيط إلى التنسيق الداخلي"""
    
    # تعريف أنواع الإشارات المدعومة
    ALL_SIGNALS = ['buy', 'sell', 'close', 'partial_close', 'long', 'short', 'close_long', 'close_short']
    
    @staticmethod
    def convert_signal(signal_data: Dict, user_settings: Optional[Dict] = None) -> Optional[Dict]:
        """
        تحويل الإشارة البسيطة إلى التنسيق الداخلي
        
        Args:
            signal_data: بيانات الإشارة البسيطة
                - signal: نوع الإشارة (buy, sell, long, close_long, short, close_short)
                - symbol: رمز العملة (BTCUSDT, ETHUSDT, ...)
                - id: معرف الإشارة (TV_001, TV_002, ...)
            user_settings: إعدادات المستخدم (اختياري)
                - market_type: نوع السوق (spot/futures)
                - trade_amount: مبلغ التداول
                - leverage: الرافعة المالية
                - exchange: المنصة (bybit/mexc)
                - account_type: نوع الحساب (demo/real)
                
        Returns:
            بيانات الإشارة بالتنسيق الداخلي أو None في حالة الخطأ
        """
        try:
            # التحقق من صحة البيانات الأساسية
            if not signal_data:
                logger.error("❌ بيانات الإشارة فارغة")
                return None
            
            signal_type = signal_data.get('signal', '').lower().strip()
            symbol = signal_data.get('symbol', '').strip()
            signal_id = signal_data.get('id', '').strip()
            
            # التحقق من وجود الحقول الأساسية
            if not signal_type:
                logger.error("❌ نوع الإشارة (signal) مفقود")
                return None
                
            if not symbol:
                logger.error("❌ رمز العملة (symbol) مفقود")
                return None
            
            # التحقق من صحة نوع الإشارة
            if signal_type not in SignalConverter.ALL_SIGNALS:
                logger.error(f"❌ نوع إشارة غير مدعوم: {signal_type}")
                logger.info(f"📋 الأنواع المدعومة: {', '.join(SignalConverter.ALL_SIGNALS)}")
                return None
            
            logger.info(f"🔄 تحويل الإشارة: {signal_type.upper()} {symbol}")
            
            # تحديد نوع السوق والإجراء بناءً على نوع الإشارة
            converted_signal = SignalConverter._determine_signal_type(signal_type, symbol, signal_id, signal_data)
            
            if not converted_signal:
                logger.error(f"❌ فشل تحديد نوع الإشارة: {signal_type}")
                return None
            
            # إضافة إعدادات المستخدم إذا كانت موجودة
            if user_settings:
                converted_signal = SignalConverter._apply_user_settings(converted_signal, user_settings)
            
            # إضافة معلومات إضافية
            converted_signal['signal_id'] = signal_id
            converted_signal['timestamp'] = datetime.now().isoformat()
            converted_signal['original_signal'] = signal_data.copy()
            
            # إضافة معلومات إضافية للـ ID
            if signal_id:
                converted_signal['has_signal_id'] = True
                logger.info(f"🆔 الإشارة مرتبطة بالـ ID: {signal_id}")
            else:
                converted_signal['has_signal_id'] = False
                logger.warning(f"⚠️ الإشارة بدون ID - سيتم التعامل معها بالطريقة التقليدية")
            
            logger.info(f"✅ تم تحويل الإشارة بنجاح: {converted_signal}")
            
            return converted_signal
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحويل الإشارة: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _determine_signal_type(signal_type: str, symbol: str, signal_id: str, signal_data: Dict = None) -> Optional[Dict]:
        """
        تحديد نوع السوق والإجراء بناءً على نوع الإشارة
        
        Args:
            signal_type: نوع الإشارة
            symbol: رمز العملة
            signal_id: معرف الإشارة
            signal_data: البيانات الأصلية للإشارة (للاستفادة من النسبة المئوية)
            
        Returns:
            بيانات الإشارة الأساسية
        """
        try:
            converted = {
                'symbol': symbol,
                'signal_type': signal_type
            }
            
            # إشارة شراء (BUY)
            if signal_type in ['buy', 'long']:
                converted['action'] = 'buy'
                logger.info(f"🟢 إشارة شراء: {symbol}")
            
            # إشارة بيع (SELL)
            elif signal_type in ['sell', 'short']:
                converted['action'] = 'sell'
                logger.info(f"🔴 إشارة بيع: {symbol}")
            
            # إشارة إغلاق كامل (CLOSE)
            elif signal_type in ['close', 'close_long', 'close_short']:
                converted['action'] = 'close'
                logger.info(f"⚪ إشارة إغلاق كامل: {symbol}")
            
            # إشارة إغلاق جزئي (PARTIAL_CLOSE)
            elif signal_type == 'partial_close':
                converted['action'] = 'partial_close'
                # النسبة المئوية من البيانات الأصلية
                if signal_data and 'percentage' in signal_data:
                    percentage = float(signal_data['percentage'])
                    converted['percentage'] = percentage
                    logger.info(f"🟡 إشارة إغلاق جزئي: {symbol} ({percentage}%)")
                else:
                    converted['percentage'] = 50  # افتراضي 50%
                    logger.info(f"🟡 إشارة إغلاق جزئي: {symbol} (50% افتراضي)")
            
            else:
                logger.error(f"❌ نوع إشارة غير معروف: {signal_type}")
                return None
            
            return converted
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديد نوع الإشارة: {e}")
            return None
    
    @staticmethod
    def _apply_user_settings(signal: Dict, user_settings: Dict) -> Dict:
        """
        تطبيق إعدادات المستخدم على الإشارة
        
        Args:
            signal: بيانات الإشارة
            user_settings: إعدادات المستخدم
            
        Returns:
            بيانات الإشارة مع الإعدادات المطبقة
        """
        try:
            # إضافة مبلغ التداول
            if 'trade_amount' in user_settings:
                signal['amount'] = user_settings['trade_amount']
                logger.info(f"💰 مبلغ التداول: {signal['amount']}")
            else:
                signal['amount'] = 100.0  # القيمة الافتراضية
                logger.warning(f"⚠️ استخدام مبلغ التداول الافتراضي: {signal['amount']}")
            
            # إضافة الرافعة المالية (للفيوتشر فقط)
            if signal.get('market_type') == 'futures':
                if 'leverage' in user_settings:
                    signal['leverage'] = user_settings['leverage']
                    logger.info(f"⚡ الرافعة المالية: {signal['leverage']}x")
                else:
                    signal['leverage'] = 10  # القيمة الافتراضية
                    logger.warning(f"⚠️ استخدام الرافعة الافتراضية: {signal['leverage']}x")
            else:
                signal['leverage'] = 1  # بدون رافعة للـ Spot
            
            # إضافة المنصة
            if 'exchange' in user_settings:
                signal['exchange'] = user_settings['exchange']
            else:
                signal['exchange'] = 'bybit'  # الافتراضي
            
            # إضافة نوع الحساب
            if 'account_type' in user_settings:
                signal['account_type'] = user_settings['account_type']
            else:
                signal['account_type'] = 'demo'  # الافتراضي
            
            # تحديث نوع السوق إذا كان المستخدم لديه تفضيل خاص
            # ملاحظة: الإشارة تحدد النوع، لكن قد يريد المستخدم تجاوز ذلك
            if 'market_type' in user_settings:
                user_market = user_settings['market_type']
                signal_market = signal.get('market_type')
                
                # تحذير إذا كان هناك عدم توافق
                if user_market != signal_market:
                    logger.warning(
                        f"⚠️ عدم توافق نوع السوق: "
                        f"الإشارة={signal_market}, المستخدم={user_market}"
                    )
                    # الأولوية للإشارة
                    logger.info(f"✅ استخدام نوع السوق من الإشارة: {signal_market}")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ خطأ في تطبيق إعدادات المستخدم: {e}")
            return signal
    
    @staticmethod
    def validate_signal(signal_data: Dict) -> tuple[bool, str]:
        """
        التحقق من صحة الإشارة
        
        Args:
            signal_data: بيانات الإشارة
            
        Returns:
            (صحيح/خطأ, رسالة الخطأ إن وجدت)
        """
        try:
            # التحقق من وجود الحقول الأساسية
            required_fields = ['signal', 'symbol']
            for field in required_fields:
                if field not in signal_data or not signal_data[field]:
                    return False, f"الحقل '{field}' مطلوب ومفقود"
            
            # التحقق من نوع الإشارة
            signal_type = signal_data.get('signal', '').lower().strip()
            if signal_type not in SignalConverter.ALL_SIGNALS:
                return False, f"نوع إشارة غير مدعوم: {signal_type}. المدعوم: {', '.join(SignalConverter.ALL_SIGNALS)}"
            
            # التحقق من رمز العملة
            symbol = signal_data.get('symbol', '').strip()
            if len(symbol) < 6:  # مثل BTCUSDT
                return False, f"رمز العملة غير صحيح: {symbol}"
            
            return True, "الإشارة صحيحة"
            
        except Exception as e:
            return False, f"خطأ في التحقق من الإشارة: {e}"
    
    @staticmethod
    def get_signal_description(signal_type: str) -> str:
        """
        الحصول على وصف نوع الإشارة
        
        Args:
            signal_type: نوع الإشارة
            
        Returns:
            وصف الإشارة بالعربية
        """
        descriptions = {
            'buy': '🟢 شراء',
            'sell': '🔴 بيع',
            'close': '⚪ إغلاق كامل',
            'partial_close': '🟡 إغلاق جزئي'
        }
        
        return descriptions.get(signal_type.lower(), '❓ غير معروف')


# مثيل عام للمحول
signal_converter = SignalConverter()


# دالة مساعدة للاستخدام السريع
def convert_simple_signal(signal_data: Dict, user_settings: Optional[Dict] = None) -> Optional[Dict]:
    """
    دالة مساعدة لتحويل الإشارة البسيطة
    
    Args:
        signal_data: بيانات الإشارة البسيطة
        user_settings: إعدادات المستخدم (اختياري)
        
    Returns:
        بيانات الإشارة المحولة أو None
    """
    return signal_converter.convert_signal(signal_data, user_settings)


# دالة مساعدة للتحقق من صحة الإشارة
def validate_simple_signal(signal_data: Dict) -> tuple[bool, str]:
    """
    دالة مساعدة للتحقق من صحة الإشارة
    
    Args:
        signal_data: بيانات الإشارة
        
    Returns:
        (صحيح/خطأ, رسالة)
    """
    return signal_converter.validate_signal(signal_data)


if __name__ == "__main__":
    # أمثلة للاختبار
    print("=" * 80)
    print("اختبار محول الإشارات")
    print("=" * 80)
    
    # إعدادات مستخدم تجريبية
    test_user_settings = {
        'trade_amount': 100.0,
        'leverage': 10,
        'exchange': 'bybit',
        'account_type': 'demo',
        'market_type': 'spot'
    }
    
    # أمثلة الإشارات
    test_signals = [
        {'signal': 'buy', 'symbol': 'BTCUSDT', 'id': 'TV_B01'},
        {'signal': 'sell', 'symbol': 'BTCUSDT', 'id': 'TV_S01'},
        {'signal': 'close', 'symbol': 'BTCUSDT', 'id': 'TV_C01'},
        {'signal': 'partial_close', 'symbol': 'BTCUSDT', 'id': 'TV_PC01', 'percentage': 50},
        {'signal': 'partial_close', 'symbol': 'ETHUSDT', 'id': 'TV_PC02', 'percentage': 25}
    ]
    
    for test_signal in test_signals:
        print("\n" + "-" * 80)
        print(f"📥 الإشارة الأصلية: {test_signal}")
        
        # التحقق من صحة الإشارة
        is_valid, message = validate_simple_signal(test_signal)
        print(f"✅ صحة الإشارة: {is_valid} - {message}")
        
        if is_valid:
            # تحويل الإشارة
            converted = convert_simple_signal(test_signal, test_user_settings)
            if converted:
                print(f"📤 الإشارة المحولة:")
                for key, value in converted.items():
                    if key != 'original_signal':
                        print(f"   {key}: {value}")
        
        print("-" * 80)

