#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الأدوات الموحد - Unified Tools Manager
يربط جميع الأدوات والمكونات في نظام واحد متكامل
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedToolsManager:
    """مدير الأدوات الموحد"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تحميل جميع الأدوات المتاحة
        self.available_tools = {}
        self._load_all_tools()
        
        self.logger.info("🚀 تم تهيئة مدير الأدوات الموحد")
    
    def _load_all_tools(self):
        """تحميل جميع الأدوات المتاحة"""
        try:
            # 1. نظام إدارة الإشارات الجديد
            try:
                from signal_system_integration import signal_system_integration
                self.available_tools['signal_system'] = {
                    'name': 'نظام إدارة الإشارات',
                    'module': signal_system_integration,
                    'status': 'active',
                    'features': [
                        'إدارة إشارات متقدمة مع ID',
                        'ربط الإشارات بنفس ID',
                        'دعم الحسابات التجريبية والحقيقية',
                        'دعم أسواق Spot و Futures'
                    ]
                }
                self.logger.info("✅ تم تحميل نظام إدارة الإشارات")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل نظام إدارة الإشارات: {e}")
            
            # 2. محسن البوت المتقدم
            try:
                from trading_bot_optimizer import TradingBotOptimizer
                self.available_tools['bot_optimizer'] = {
                    'name': 'محسن البوت المتقدم',
                    'module': TradingBotOptimizer,
                    'status': 'active',
                    'features': [
                        'تحسين الأداء الشامل',
                        'تحسين نسبة المخاطر إلى العوائد',
                        'تحسين معدل الفوز',
                        'تحسين عامل الربح'
                    ]
                }
                self.logger.info("✅ تم تحميل محسن البوت المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل محسن البوت: {e}")
            
            # 3. مدير المحفظة المتقدم
            try:
                from advanced_portfolio_manager import global_portfolio_manager
                self.available_tools['portfolio_manager'] = {
                    'name': 'مدير المحفظة المتقدم',
                    'module': global_portfolio_manager,
                    'status': 'active',
                    'features': [
                        'إدارة المحفظة الذكية',
                        'توزيع الأصول',
                        'إعادة التوازن التلقائي',
                        'تحليل الأداء'
                    ]
                }
                self.logger.info("✅ تم تحميل مدير المحفظة المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير المحفظة: {e}")
            
            # 4. مدير المخاطر المتقدم
            try:
                from advanced_risk_manager import global_risk_manager
                self.available_tools['risk_manager'] = {
                    'name': 'مدير المخاطر المتقدم',
                    'module': global_risk_manager,
                    'status': 'active',
                    'features': [
                        'إدارة المخاطر الذكية',
                        'حساب حجم الصفقة الأمثل',
                        'تقييم المخاطر',
                        'حماية رأس المال'
                    ]
                }
                self.logger.info("✅ تم تحميل مدير المخاطر المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير المخاطر: {e}")
            
            # 5. معالج الإشارات المتقدم
            try:
                from advanced_signal_processor import global_signal_manager
                self.available_tools['signal_processor'] = {
                    'name': 'معالج الإشارات المتقدم',
                    'module': global_signal_manager,
                    'status': 'active',
                    'features': [
                        'معالجة إشارات ذكية',
                        'تحليل الإشارات',
                        'تصفية الإشارات',
                        'تحسين دقة الإشارات'
                    ]
                }
                self.logger.info("✅ تم تحميل معالج الإشارات المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل معالج الإشارات: {e}")
            
            # 6. منفذ الصفقات المتقدم
            try:
                from advanced_trade_executor import global_trade_executor
                self.available_tools['trade_executor'] = {
                    'name': 'منفذ الصفقات المتقدم',
                    'module': global_trade_executor,
                    'status': 'active',
                    'features': [
                        'تنفيذ صفقات ذكي',
                        'تحسين نقاط الدخول',
                        'إدارة الأوامر',
                        'تنفيذ متقدم'
                    ]
                }
                self.logger.info("✅ تم تحميل منفذ الصفقات المتقدم")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل منفذ الصفقات: {e}")
            
            # 7. مدير الصفقات
            try:
                from position_manager import PositionManager
                self.available_tools['position_manager'] = {
                    'name': 'مدير الصفقات',
                    'module': PositionManager,
                    'status': 'active',
                    'features': [
                        'إدارة الصفقات المفتوحة',
                        'تعيين TP/SL',
                        'تعديل الصفقات',
                        'إغلاق الصفقات'
                    ]
                }
                self.logger.info("✅ تم تحميل مدير الصفقات")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الصفقات: {e}")
            
            # 8. مدير الحسابات الحقيقية
            try:
                from real_account_manager import real_account_manager
                self.available_tools['real_account_manager'] = {
                    'name': 'مدير الحسابات الحقيقية',
                    'module': real_account_manager,
                    'status': 'active',
                    'features': [
                        'إدارة الحسابات الحقيقية',
                        'تنفيذ الصفقات الحقيقية',
                        'متابعة الأرصدة',
                        'إدارة API'
                    ]
                }
                self.logger.info("✅ تم تحميل مدير الحسابات الحقيقية")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل مدير الحسابات الحقيقية: {e}")
            
            # 9. نظام المطورين
            try:
                from developer_manager import developer_manager
                self.available_tools['developer_system'] = {
                    'name': 'نظام المطورين',
                    'module': developer_manager,
                    'status': 'active',
                    'features': [
                        'إدارة المطورين',
                        'توزيع الإشارات',
                        'إدارة المتابعين',
                        'نظام الاشتراكات'
                    ]
                }
                self.logger.info("✅ تم تحميل نظام المطورين")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل نظام المطورين: {e}")
            
            # 10. النظام المحسن المتكامل
            try:
                from integrated_trading_system import IntegratedTradingSystem
                self.available_tools['integrated_system'] = {
                    'name': 'النظام المحسن المتكامل',
                    'module': IntegratedTradingSystem,
                    'status': 'active',
                    'features': [
                        'نظام تداول متكامل',
                        'تحليل شامل',
                        'إدارة متقدمة',
                        'تحسين تلقائي'
                    ]
                }
                self.logger.info("✅ تم تحميل النظام المحسن المتكامل")
            except ImportError as e:
                self.logger.warning(f"⚠️ فشل تحميل النظام المحسن المتكامل: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل الأدوات: {e}")
    
    def get_available_tools(self) -> Dict[str, Any]:
        """الحصول على قائمة الأدوات المتاحة"""
        return self.available_tools
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """الحصول على أداة محددة"""
        tool = self.available_tools.get(tool_name)
        if tool:
            return tool['module']
        return None
    
    def get_tools_status(self) -> Dict[str, Any]:
        """الحصول على حالة جميع الأدوات"""
        status = {
            'total_tools': len(self.available_tools),
            'active_tools': sum(1 for tool in self.available_tools.values() if tool['status'] == 'active'),
            'tools': {}
        }
        
        for tool_name, tool_info in self.available_tools.items():
            status['tools'][tool_name] = {
                'name': tool_info['name'],
                'status': tool_info['status'],
                'features_count': len(tool_info['features'])
            }
        
        return status
    
    def get_tools_menu_buttons(self) -> List[List[Dict[str, str]]]:
        """الحصول على أزرار قائمة الأدوات للبوت"""
        buttons = []
        
        # ترتيب الأدوات حسب الأهمية
        priority_tools = [
            ('signal_system', '🎯 نظام الإشارات'),
            ('portfolio_manager', '💼 إدارة المحفظة'),
            ('risk_manager', '🛡️ إدارة المخاطر'),
            ('position_manager', '📊 إدارة الصفقات'),
            ('bot_optimizer', '⚡ تحسين البوت'),
            ('signal_processor', '🔍 معالج الإشارات'),
            ('trade_executor', '🚀 منفذ الصفقات'),
            ('real_account_manager', '💰 الحسابات الحقيقية'),
            ('developer_system', '👨‍💻 نظام المطورين'),
            ('integrated_system', '🎛️ النظام المتكامل')
        ]
        
        # إنشاء صفين من الأزرار
        row = []
        for tool_key, tool_label in priority_tools:
            if tool_key in self.available_tools:
                row.append({
                    'text': tool_label,
                    'callback_data': f'tool_{tool_key}'
                })
                
                # إضافة صف جديد بعد كل زرين
                if len(row) == 2:
                    buttons.append(row)
                    row = []
        
        # إضافة أي أزرار متبقية
        if row:
            buttons.append(row)
        
        # زر العودة
        buttons.append([{'text': '🔙 رجوع', 'callback_data': 'main_menu'}])
        
        return buttons
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """الحصول على معلومات أداة محددة"""
        return self.available_tools.get(tool_name)
    
    def is_tool_available(self, tool_name: str) -> bool:
        """التحقق من توفر أداة"""
        return tool_name in self.available_tools
    
    def get_system_summary(self) -> str:
        """الحصول على ملخص النظام"""
        total = len(self.available_tools)
        active = sum(1 for tool in self.available_tools.values() if tool['status'] == 'active')
        
        summary = f"📊 **ملخص النظام**\n\n"
        summary += f"🔧 إجمالي الأدوات: {total}\n"
        summary += f"✅ الأدوات النشطة: {active}\n"
        summary += f"⚙️ معدل التوفر: {(active/total*100):.1f}%\n\n"
        
        summary += "**الأدوات المتاحة:**\n"
        for tool_name, tool_info in self.available_tools.items():
            status_icon = "✅" if tool_info['status'] == 'active' else "❌"
            summary += f"{status_icon} {tool_info['name']}\n"
        
        return summary


# مثيل عام لمدير الأدوات الموحد
unified_tools_manager = UnifiedToolsManager()


# دوال مساعدة للاستخدام السريع
def get_available_tools() -> Dict[str, Any]:
    """الحصول على قائمة الأدوات المتاحة"""
    return unified_tools_manager.get_available_tools()


def get_tool(tool_name: str) -> Optional[Any]:
    """الحصول على أداة محددة"""
    return unified_tools_manager.get_tool(tool_name)


def get_tools_status() -> Dict[str, Any]:
    """الحصول على حالة جميع الأدوات"""
    return unified_tools_manager.get_tools_status()


def get_tools_menu_buttons() -> List[List[Dict[str, str]]]:
    """الحصول على أزرار قائمة الأدوات"""
    return unified_tools_manager.get_tools_menu_buttons()


def is_tool_available(tool_name: str) -> bool:
    """التحقق من توفر أداة"""
    return unified_tools_manager.is_tool_available(tool_name)


def get_system_summary() -> str:
    """الحصول على ملخص النظام"""
    return unified_tools_manager.get_system_summary()


if __name__ == "__main__":
    # اختبار مدير الأدوات الموحد
    print("=" * 80)
    print("اختبار مدير الأدوات الموحد")
    print("=" * 80)
    
    # حالة الأدوات
    status = get_tools_status()
    print(f"\n📊 حالة الأدوات:")
    print(f"   إجمالي الأدوات: {status['total_tools']}")
    print(f"   الأدوات النشطة: {status['active_tools']}")
    
    # قائمة الأدوات
    print(f"\n🔧 الأدوات المتاحة:")
    for tool_name, tool_status in status['tools'].items():
        print(f"   • {tool_status['name']}: {tool_status['status']}")
    
    # ملخص النظام
    print(f"\n{get_system_summary()}")
