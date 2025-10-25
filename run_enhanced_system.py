#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل النهائي البسيط
تشغيل النظام المحسن مع الحفاظ على النظام الحالي
"""

import logging
import asyncio
import sys
import os

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def run_enhanced_system():
    """تشغيل النظام المحسن"""
    try:
        logger.info("🚀 بدء تشغيل النظام المحسن...")
        
        # استيراد النظام المحسن
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
        asyncio.run(run_enhanced_system())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        sys.exit(1)