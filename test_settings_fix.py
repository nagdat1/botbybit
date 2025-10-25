#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح تحديث إعدادات المستخدم
"""

import logging
import sys
import os
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from user_manager import UserManager

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_user_settings_update():
    """اختبار تحديث إعدادات المستخدم"""
    logger.info("اختبار تحديث إعدادات المستخدم...")
    
    try:
        # إنشاء مدير قاعدة البيانات
        db_manager = DatabaseManager()
        
        # إنشاء مدير المستخدمين
        user_manager = UserManager()
        
        # معرف المستخدم للاختبار
        test_user_id = 8169000394
        
        # جلب البيانات الحالية
        logger.info(f"جلب البيانات الحالية للمستخدم {test_user_id}...")
        user_data_before = db_manager.get_user(test_user_id)
        
        if user_data_before:
            logger.info(f"البيانات قبل التحديث:")
            logger.info(f"  trade_amount: {user_data_before.get('trade_amount', 'غير محدد')}")
            logger.info(f"  leverage: {user_data_before.get('leverage', 'غير محدد')}")
            logger.info(f"  market_type: {user_data_before.get('market_type', 'غير محدد')}")
            logger.info(f"  account_type: {user_data_before.get('account_type', 'غير محدد')}")
        else:
            logger.error(f"المستخدم {test_user_id} غير موجود")
            return False
        
        # تحديث المبلغ
        new_amount = 55.0
        logger.info(f"تحديث المبلغ إلى {new_amount}...")
        success = db_manager.update_user_settings(test_user_id, {'trade_amount': new_amount})
        
        if success:
            logger.info("تم تحديث المبلغ بنجاح")
        else:
            logger.error("فشل في تحديث المبلغ")
            return False
        
        # تحديث الرافعة
        new_leverage = 1
        logger.info(f"تحديث الرافعة إلى {new_leverage}...")
        success = db_manager.update_user_settings(test_user_id, {'leverage': new_leverage})
        
        if success:
            logger.info("تم تحديث الرافعة بنجاح")
        else:
            logger.error("فشل في تحديث الرافعة")
            return False
        
        # تحديث نوع السوق
        new_market_type = 'spot'
        logger.info(f"تحديث نوع السوق إلى {new_market_type}...")
        success = db_manager.update_user_settings(test_user_id, {'market_type': new_market_type})
        
        if success:
            logger.info("تم تحديث نوع السوق بنجاح")
        else:
            logger.error("فشل في تحديث نوع السوق")
            return False
        
        # تحديث نوع الحساب
        new_account_type = 'real'
        logger.info(f"تحديث نوع الحساب إلى {new_account_type}...")
        success = db_manager.update_user_settings(test_user_id, {'account_type': new_account_type})
        
        if success:
            logger.info("تم تحديث نوع الحساب بنجاح")
        else:
            logger.error("فشل في تحديث نوع الحساب")
            return False
        
        # جلب البيانات بعد التحديث
        logger.info(f"جلب البيانات بعد التحديث...")
        user_data_after = db_manager.get_user(test_user_id)
        
        if user_data_after:
            logger.info(f"البيانات بعد التحديث:")
            logger.info(f"  trade_amount: {user_data_after.get('trade_amount', 'غير محدد')}")
            logger.info(f"  leverage: {user_data_after.get('leverage', 'غير محدد')}")
            logger.info(f"  market_type: {user_data_after.get('market_type', 'غير محدد')}")
            logger.info(f"  account_type: {user_data_after.get('account_type', 'غير محدد')}")
            
            # التحقق من التحديث
            if (user_data_after.get('trade_amount') == new_amount and
                user_data_after.get('leverage') == new_leverage and
                user_data_after.get('market_type') == new_market_type and
                user_data_after.get('account_type') == new_account_type):
                logger.info("تم تحديث جميع الإعدادات بنجاح!")
                return True
            else:
                logger.error("لم يتم تحديث جميع الإعدادات بشكل صحيح")
                return False
        else:
            logger.error("فشل في جلب البيانات بعد التحديث")
            return False
        
    except Exception as e:
        logger.error(f"خطأ في اختبار تحديث الإعدادات: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """الدالة الرئيسية"""
    logger.info("اختبار إصلاح تحديث إعدادات المستخدم...")
    
    success = test_user_settings_update()
    
    logger.info("\n" + "="*60)
    logger.info("نتائج اختبار تحديث الإعدادات:")
    logger.info(f"التحديث: {'نجح' if success else 'فشل'}")
    
    if success:
        logger.info("تم إصلاح مشكلة تحديث الإعدادات!")
        logger.info("الآن يجب أن تعمل الإشارات مع الإعدادات الجديدة")
    else:
        logger.error("لا تزال المشكلة موجودة")
    
    logger.info("="*60)

if __name__ == "__main__":
    main()
