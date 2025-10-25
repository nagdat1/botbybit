#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل الرئيسي للنظام المحسن
يحافظ على آلية التوقيع وحساب السعر مع دعم تعديل المتغيرات
"""

import logging
import asyncio
import sys
import os

# إضافة المسار الحالي إلى Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """الدالة الرئيسية لتشغيل النظام المحسن"""
    try:
        logger.info("🚀 بدء تشغيل النظام المحسن...")
        
        # استيراد المكونات المحسنة
        from flexible_config_manager import flexible_config_manager
        from enhanced_bot_interface import enhanced_bot_interface
        from enhanced_trade_executor import enhanced_trade_executor
        from integrated_trading_system import integrated_trading_system
        
        # تهيئة النظام المحسن
        await flexible_config_manager.initialize_system()
        await enhanced_bot_interface.initialize_interface()
        await enhanced_trade_executor.initialize_executor()
        await integrated_trading_system.initialize_system()
        
        # تشغيل النظام المحسن
        await integrated_trading_system.run_enhanced_system()
        
        logger.info("✅ تم تشغيل النظام المحسن بنجاح!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل النظام المحسن: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎯 بدء تشغيل النظام المحسن...")
    print("🛡️ آلية التوقيع وحساب السعر محفوظة")
    print("🎯 جميع المتغيرات قابلة للتعديل")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        sys.exit(1)
