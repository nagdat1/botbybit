#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الإشارات - إدارة استقبال ومعالجة إشارات التداول
"""

import logging
import uuid
from typing import Dict, Optional, Tuple
from datetime import datetime
from database import db_manager

logger = logging.getLogger(__name__)

class SignalManager:
    """مدير الإشارات - معالجة إشارات التداول بشكل متقدم"""
    
    # أنواع الإشارات المدعومة
    SIGNAL_TYPES = {
        'buy': {'market': 'spot', 'action': 'open', 'side': 'Buy'},
        'sell': {'market': 'spot', 'action': 'close', 'side': 'Sell'},
        'long': {'market': 'futures', 'action': 'open', 'side': 'Buy'},
        'close_long': {'market': 'futures', 'action': 'close', 'side': 'Buy'},
        'short': {'market': 'futures', 'action': 'open', 'side': 'Sell'},
        'close_short': {'market': 'futures', 'action': 'close', 'side': 'Sell'},
    }
    
    @staticmethod
    def validate_signal(signal_data: Dict) -> Tuple[bool, str]:
        """
        التحقق من صحة الإشارة
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # التحقق من وجود الحقول الإلزامية
            required_fields = ['signal', 'symbol']
            for field in required_fields:
                if field not in signal_data:
                    return False, f"Missing required field: {field}"
            
            # التحقق من نوع الإشارة
            signal_type = signal_data.get('signal', '').lower()
            if signal_type not in SignalManager.SIGNAL_TYPES:
                return False, f"Unknown signal type: {signal_type}. Supported: {', '.join(SignalManager.SIGNAL_TYPES.keys())}"
            
            # التحقق من الرمز
            symbol = signal_data.get('symbol', '')
            if not symbol or len(symbol) < 2:
                return False, "Invalid symbol"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الإشارة: {e}")
            return False, str(e)
    
    @staticmethod
    def generate_signal_id(signal_data: Dict) -> str:
        """
        توليد معرف فريد للإشارة
        إذا كان موجود في البيانات يتم استخدامه، وإلا يتم توليده
        """
        # التحقق من وجود ID في البيانات
        if 'id' in signal_data and signal_data['id']:
            return str(signal_data['id'])
        
        # توليد ID بناءً على الوقت والبيانات
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        signal_type = signal_data.get('signal', '')
        symbol = signal_data.get('symbol', '')
        
        # استخدام UUID مع البيانات الأساسية
        unique_str = f"{timestamp}_{signal_type}_{symbol}"
        signal_id = f"{unique_str}_{str(uuid.uuid4())[:8]}"
        
        return signal_id
    
    @staticmethod
    def process_signal(user_id: int, signal_data: Dict) -> Dict:
        """
        معالجة الإشارة الواردة
        
        Returns:
            {
                'success': bool,
                'message': str,
                'signal_id': str,
                'action': str,  # 'open', 'close', 'ignore'
                'should_execute': bool
            }
        """
        try:
            # التحقق من صحة الإشارة
            is_valid, error_msg = SignalManager.validate_signal(signal_data)
            if not is_valid:
                logger.error(f"❌ إشارة غير صالحة: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'should_execute': False
                }
            
            signal_type = signal_data.get('signal', '').lower()
            symbol = signal_data.get('symbol', '')
            
            # توليد معرف الإشارة
            signal_id = SignalManager.generate_signal_id(signal_data)
            signal_data['signal_id'] = signal_id
            
            logger.info(f"📨 معالجة إشارة: {signal_type} {symbol} [ID: {signal_id}]")
            
            # التحقق من الإشارة المكررة
            if db_manager.check_signal_exists(signal_id, user_id):
                logger.warning(f"⚠️ إشارة مكررة تم تجاهلها: {signal_id}")
                return {
                    'success': False,
                    'message': f'Duplicate signal ignored: {signal_id}',
                    'signal_id': signal_id,
                    'action': 'ignore',
                    'should_execute': False
                }
            
            # حفظ الإشارة في قاعدة البيانات
            signal_record = {
                'signal_id': signal_id,
                'user_id': user_id,
                'signal_type': signal_type,
                'symbol': symbol,
                'price': signal_data.get('price'),
                'market_type': SignalManager.SIGNAL_TYPES[signal_type]['market'],
                'raw_data': signal_data
            }
            
            saved_id = db_manager.create_signal(signal_record)
            if not saved_id:
                logger.error(f"❌ فشل في حفظ الإشارة: {signal_id}")
                return {
                    'success': False,
                    'message': 'Failed to save signal',
                    'signal_id': signal_id,
                    'should_execute': False
                }
            
            # معالجة حسب نوع الإشارة
            signal_info = SignalManager.SIGNAL_TYPES[signal_type]
            action = signal_info['action']
            
            if action == 'open':
                # إشارة فتح صفقة جديدة
                logger.info(f"✅ إشارة فتح صفقة: {signal_type} {symbol}")
                return {
                    'success': True,
                    'message': f'Open {signal_type} signal for {symbol}',
                    'signal_id': signal_id,
                    'action': 'open',
                    'market_type': signal_info['market'],
                    'side': signal_info['side'],
                    'should_execute': True
                }
            
            elif action == 'close':
                # إشارة إغلاق صفقة
                # التحقق من وجود صفقة مفتوحة مرتبطة بهذا الـ ID
                if signal_type in ['close_long', 'close_short']:
                    # للإغلاق المرتبط بـ ID محدد
                    original_signal_id = signal_data.get('original_id') or signal_data.get('id')
                    if not original_signal_id:
                        logger.warning(f"⚠️ إشارة إغلاق بدون original_id: {signal_id}")
                        db_manager.update_signal_status(
                            signal_id, user_id, 'ignored', 
                            notes='No original_id provided'
                        )
                        return {
                            'success': False,
                            'message': 'Close signal requires original_id',
                            'signal_id': signal_id,
                            'action': 'ignore',
                            'should_execute': False
                        }
                    
                    # البحث عن الصفقة المفتوحة
                    open_order = db_manager.get_open_order_by_signal(str(original_signal_id), user_id)
                    if not open_order:
                        logger.warning(f"⚠️ لا توجد صفقة مفتوحة للإشارة: {original_signal_id}")
                        db_manager.update_signal_status(
                            signal_id, user_id, 'ignored', 
                            notes=f'No open position for signal: {original_signal_id}'
                        )
                        return {
                            'success': False,
                            'message': f'No open position found for signal: {original_signal_id}',
                            'signal_id': signal_id,
                            'action': 'ignore',
                            'should_execute': False
                        }
                    
                    logger.info(f"✅ إشارة إغلاق صفقة: {signal_type} {symbol} [Original: {original_signal_id}]")
                    return {
                        'success': True,
                        'message': f'Close {signal_type} signal for {symbol}',
                        'signal_id': signal_id,
                        'original_signal_id': original_signal_id,
                        'action': 'close',
                        'market_type': signal_info['market'],
                        'side': signal_info['side'],
                        'order_to_close': open_order,
                        'should_execute': True
                    }
                
                else:
                    # إغلاق عادي (sell في spot)
                    logger.info(f"✅ إشارة إغلاق: {signal_type} {symbol}")
                    return {
                        'success': True,
                        'message': f'Close signal for {symbol}',
                        'signal_id': signal_id,
                        'action': 'close',
                        'market_type': signal_info['market'],
                        'side': signal_info['side'],
                        'should_execute': True
                    }
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الإشارة: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': str(e),
                'should_execute': False
            }
    
    @staticmethod
    def update_signal_with_order(signal_id: str, user_id: int, 
                                 order_id: str, status: str = 'executed') -> bool:
        """تحديث الإشارة بعد تنفيذ الأمر"""
        return db_manager.update_signal_status(
            signal_id, user_id, status, 
            order_id=order_id,
            notes=f'Order {order_id} created'
        )
    
    @staticmethod
    def mark_signal_failed(signal_id: str, user_id: int, error_message: str) -> bool:
        """تعليم الإشارة كفاشلة"""
        return db_manager.update_signal_status(
            signal_id, user_id, 'failed',
            notes=error_message
        )

# مثيل عام
signal_manager = SignalManager()

