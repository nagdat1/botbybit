#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال على استخدام نظام المطورين
يوضح كيفية التكامل مع البوت الموجود
"""

import asyncio
import logging
from developer_manager import developer_manager
from user_manager import user_manager
from developer_config import DEVELOPER_PERMISSIONS, DEVELOPER_MESSAGES

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeveloperBotIntegration:
    """مثال على التكامل بين نظام المطورين والبوت"""
    
    def __init__(self):
        self.dev_manager = developer_manager
        self.usr_manager = user_manager
    
    async def handle_start_command(self, user_id: int):
        """معالجة أمر /start"""
        # التحقق من نوع المستخدم
        if self.dev_manager.is_developer(user_id):
            return await self.show_developer_panel(user_id)
        else:
            return await self.show_user_menu(user_id)
    
    async def show_developer_panel(self, developer_id: int):
        """عرض لوحة تحكم المطور"""
        try:
            # الحصول على إحصائيات المطور
            stats = self.dev_manager.get_developer_statistics(developer_id)
            dev_info = self.dev_manager.get_developer(developer_id)
            
            if not dev_info:
                return " خطأ: لم يتم العثور على معلومات المطور"
            
            # بناء رسالة الإحصائيات
            message = DEVELOPER_MESSAGES['stats_header'].format(
                developer_name=dev_info['developer_name'],
                follower_count=stats['follower_count'],
                total_signals=stats['total_signals'],
                is_active=stats['is_active'],
                can_broadcast=stats['can_broadcast']
            )
            
            # إضافة الأزرار
            buttons = [
                [" إرسال إشارة", "👥 المتابعين"],
                [" الإحصائيات", " الإعدادات"],
                ["📱 إشعار جماعي", " تصدير البيانات"]
            ]
            
            return {
                'message': message,
                'buttons': buttons
            }
            
        except Exception as e:
            logger.error(f"خطأ في عرض لوحة المطور: {e}")
            return " حدث خطأ في عرض لوحة التحكم"
    
    async def show_user_menu(self, user_id: int):
        """عرض قائمة المستخدم العادي"""
        # التحقق من وجود المستخدم
        user = self.usr_manager.get_user(user_id)
        
        if not user:
            # مستخدم جديد - إنشاء حساب
            self.usr_manager.create_user(user_id)
        
        message = """
🤖 مرحباً بك في بوت التداول

اختر من القائمة أدناه:
        """
        
        buttons = [
            [" حسابي", "💼 الصفقات"],
            [" الإعدادات", "📜 السجل"],
            ["⚡ متابعة إشارات المطور"]
        ]
        
        return {
            'message': message,
            'buttons': buttons
        }
    
    async def handle_follow_developer(self, user_id: int, developer_id: int):
        """معالجة متابعة المطور"""
        try:
            # التحقق من أن المطور نشط
            if not self.dev_manager.is_developer_active(developer_id):
                return " المطور غير نشط حالياً"
            
            # التحقق من أن المستخدم ليس متابعاً بالفعل
            if self.dev_manager.is_following(developer_id, user_id):
                return " أنت تتابع هذا المطور بالفعل"
            
            # إضافة المتابع
            success = self.dev_manager.add_follower(developer_id, user_id)
            
            if success:
                dev_info = self.dev_manager.get_developer(developer_id)
                return f" تم متابعة المطور {dev_info['developer_name']} بنجاح\n\nستتلقى جميع الإشارات تلقائياً"
            else:
                return " فشل في متابعة المطور"
                
        except Exception as e:
            logger.error(f"خطأ في متابعة المطور: {e}")
            return " حدث خطأ أثناء المتابعة"
    
    async def handle_unfollow_developer(self, user_id: int, developer_id: int):
        """معالجة إلغاء متابعة المطور"""
        try:
            # التحقق من أن المستخدم يتابع المطور
            if not self.dev_manager.is_following(developer_id, user_id):
                return " أنت لا تتابع هذا المطور"
            
            # إزالة المتابع
            success = self.dev_manager.remove_follower(developer_id, user_id)
            
            if success:
                dev_info = self.dev_manager.get_developer(developer_id)
                return f" تم إلغاء متابعة المطور {dev_info['developer_name']}"
            else:
                return " فشل في إلغاء المتابعة"
                
        except Exception as e:
            logger.error(f"خطأ في إلغاء متابعة المطور: {e}")
            return " حدث خطأ أثناء إلغاء المتابعة"
    
    async def broadcast_signal(self, developer_id: int, signal_data: dict):
        """إرسال إشارة من المطور لجميع المتابعين"""
        try:
            # التحقق من الصلاحيات
            if not self.dev_manager.can_broadcast_signals(developer_id):
                return {
                    'success': False,
                    'message': DEVELOPER_MESSAGES['permission_denied']
                }
            
            # إرسال الإشارة
            result = self.dev_manager.broadcast_signal_to_followers(
                developer_id=developer_id,
                signal_data=signal_data
            )
            
            if result['success']:
                # بناء رسالة النجاح
                message = DEVELOPER_MESSAGES['signal_broadcast_success'].format(
                    follower_count=result['follower_count'],
                    sent_count=len(result['sent_to']),
                    symbol=signal_data.get('symbol', 'N/A'),
                    action=signal_data.get('action', 'N/A')
                )
                
                return {
                    'success': True,
                    'message': message,
                    'signal_id': result['signal_id']
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشارة: {e}")
            return {
                'success': False,
                'message': f" حدث خطأ: {str(e)}"
            }
    
    async def show_followers_list(self, developer_id: int):
        """عرض قائمة متابعي المطور"""
        try:
            followers = self.dev_manager.get_followers(developer_id)
            
            if not followers:
                return "📭 لا يوجد متابعين حالياً"
            
            message = f"👥 قائمة المتابعين ({len(followers)} متابع)\n\n"
            
            for i, user_id in enumerate(followers[:50], 1):  # عرض أول 50 متابع
                user = self.usr_manager.get_user(user_id)
                if user:
                    username = user.get('username', 'N/A')
                    message += f"{i}. {username} (ID: {user_id})\n"
                else:
                    message += f"{i}. User ID: {user_id}\n"
            
            if len(followers) > 50:
                message += f"\n... و {len(followers) - 50} متابع آخرين"
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة المتابعين: {e}")
            return " حدث خطأ في عرض القائمة"
    
    async def process_developer_signal_for_users(self, signal_data: dict, target_users: list):
        """معالجة إشارة المطور لجميع المستخدمين المستهدفين"""
        try:
            results = {
                'successful': [],
                'failed': []
            }
            
            for user_id in target_users:
                try:
                    # التحقق من أن المستخدم نشط
                    if not self.usr_manager.is_user_active(user_id):
                        results['failed'].append({
                            'user_id': user_id,
                            'reason': 'المستخدم غير نشط'
                        })
                        continue
                    
                    # تنفيذ الإشارة للمستخدم
                    success, message = await self.execute_signal_for_user(
                        user_id=user_id,
                        signal_data=signal_data
                    )
                    
                    if success:
                        results['successful'].append(user_id)
                    else:
                        results['failed'].append({
                            'user_id': user_id,
                            'reason': message
                        })
                        
                except Exception as e:
                    logger.error(f"خطأ في معالجة الإشارة للمستخدم {user_id}: {e}")
                    results['failed'].append({
                        'user_id': user_id,
                        'reason': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في معالجة إشارة المطور: {e}")
            return {'successful': [], 'failed': []}
    
    async def execute_signal_for_user(self, user_id: int, signal_data: dict):
        """تنفيذ إشارة لمستخدم محدد"""
        try:
            # استخراج بيانات الإشارة
            symbol = signal_data.get('symbol')
            action = signal_data.get('action')
            price = signal_data.get('price')
            amount = signal_data.get('amount', 100.0)
            market_type = signal_data.get('market_type', 'spot')
            
            # تنفيذ الصفقة
            success, result = self.usr_manager.execute_user_trade(
                user_id=user_id,
                symbol=symbol,
                action=action,
                price=price,
                amount=amount,
                market_type=market_type
            )
            
            return success, result
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإشارة للمستخدم {user_id}: {e}")
            return False, str(e)


# مثال على الاستخدام
async def main():
    """مثال على الاستخدام"""
    integration = DeveloperBotIntegration()
    
    # مثال 1: عرض لوحة المطور
    developer_id = 8169000394
    panel = await integration.show_developer_panel(developer_id)
    print("لوحة المطور:", panel)
    
    # مثال 2: متابعة المطور
    user_id = 123456789
    follow_result = await integration.handle_follow_developer(user_id, developer_id)
    print("نتيجة المتابعة:", follow_result)
    
    # مثال 3: إرسال إشارة
    signal_data = {
        'symbol': 'BTCUSDT',
        'action': 'BUY',
        'price': 50000,
        'amount': 100,
        'market_type': 'spot'
    }
    broadcast_result = await integration.broadcast_signal(developer_id, signal_data)
    print("نتيجة الإرسال:", broadcast_result)
    
    # مثال 4: عرض المتابعين
    followers_list = await integration.show_followers_list(developer_id)
    print("قائمة المتابعين:", followers_list)


if __name__ == "__main__":
    print(" مثال على نظام المطورين\n")
    asyncio.run(main())

