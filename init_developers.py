#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لتهيئة المطورين في قاعدة البيانات
يتم تشغيله مرة واحدة عند بدء تشغيل البوت لأول مرة
"""

import logging
from database import db_manager
from developer_config import get_all_developers

logger = logging.getLogger(__name__)

def init_developers():
    """تهيئة المطورين في قاعدة البيانات"""
    try:
        developers = get_all_developers()
        
        logger.info(f"بدء تهيئة {len(developers)} مطور...")
        
        for dev in developers:
            # التحقق من وجود المطور
            existing_dev = db_manager.get_developer(dev['developer_id'])
            
            if existing_dev:
                # تحديث المعلومات إذا كان المطور موجوداً
                logger.info(f"المطور {dev['developer_name']} موجود بالفعل، تحديث المعلومات...")
                db_manager.update_developer(dev['developer_id'], {
                    'developer_name': dev['developer_name'],
                    'developer_key': dev['developer_key'],
                    'webhook_url': dev['webhook_url'],
                    'is_active': dev['is_active'],
                    'can_broadcast': dev['can_broadcast']
                })
            else:
                # إنشاء المطور
                logger.info(f"إنشاء مطور جديد: {dev['developer_name']}")
                success = db_manager.create_developer(
                    developer_id=dev['developer_id'],
                    developer_name=dev['developer_name'],
                    developer_key=dev['developer_key'],
                    webhook_url=dev['webhook_url']
                )
                
                if success:
                    # تحديث الصلاحيات
                    db_manager.update_developer(dev['developer_id'], {
                        'is_active': dev['is_active'],
                        'can_broadcast': dev['can_broadcast']
                    })
                    logger.info(f" تم إنشاء المطور {dev['developer_name']} بنجاح")
                else:
                    logger.error(f" فشل في إنشاء المطور {dev['developer_name']}")
        
        logger.info(" تم الانتهاء من تهيئة المطورين")
        return True
        
    except Exception as e:
        logger.error(f" خطأ في تهيئة المطورين: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # إعداد التسجيل
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(" بدء تهيئة المطورين...")
    success = init_developers()
    
    if success:
        print(" تم تهيئة المطورين بنجاح")
    else:
        print(" فشل في تهيئة المطورين")

