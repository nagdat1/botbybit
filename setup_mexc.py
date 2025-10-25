#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت سريع لإعداد MEXC API
يساعدك في إضافة مفاتيح MEXC بسهولة
"""

import os
from pathlib import Path

def setup_mexc_api():
    """إعداد مفاتيح MEXC API"""
    print("=" * 70)
    print(" إعداد MEXC API")
    print("=" * 70)
    
    print("\n ستحتاج إلى:")
    print("   1. API Key من حسابك على MEXC")
    print("   2. API Secret من حسابك على MEXC")
    print("\n للحصول على المفاتيح:")
    print("   • اذهب إلى https://www.mexc.com/")
    print("   • Account → API Management")
    print("   • Create New API Key")
    print("   • فعّل صلاحية Spot Trading فقط")
    
    print("\n" + "=" * 70)
    
    # طلب المفاتيح
    print("\n🔑 أدخل مفاتيح MEXC API:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print(" لم تدخل API Key")
        return False
    
    api_secret = input("API Secret: ").strip()
    
    if not api_secret:
        print(" لم تدخل API Secret")
        return False
    
    # التحقق من وجود ملف .env
    env_file = Path('.env')
    
    print("\n التحقق من ملف .env...")
    
    if env_file.exists():
        print(" تم العثور على ملف .env")
        
        # قراءة المحتوى الحالي
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من وجود إعدادات MEXC
        if 'MEXC_API_KEY' in content:
            print(" يوجد إعدادات MEXC سابقة")
            overwrite = input("هل تريد استبدالها؟ (y/n): ").strip().lower()
            
            if overwrite != 'y':
                print(" تم الإلغاء")
                return False
            
            # إزالة الإعدادات القديمة
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            
            for line in lines:
                if 'MEXC_API_KEY' in line or 'MEXC_API_SECRET' in line:
                    continue
                if '# إعدادات MEXC API' in line:
                    skip_next = True
                    continue
                if skip_next and line.strip().startswith('#'):
                    continue
                skip_next = False
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # إضافة الإعدادات الجديدة
        if not content.endswith('\n'):
            content += '\n'
        
        content += f"""
# إعدادات MEXC API
# ملاحظة: MEXC تدعم التداول الفوري (Spot) فقط - لا يوجد دعم للفيوتشر
MEXC_API_KEY={api_key}
MEXC_API_SECRET={api_secret}
"""
        
        # حفظ الملف
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(" تم تحديث ملف .env")
    
    else:
        print(" لم يتم العثور على ملف .env، سيتم إنشاؤه...")
        
        # إنشاء ملف .env جديد
        content = f"""# إعدادات تلغرام
TELEGRAM_TOKEN=your_telegram_bot_token_here
ADMIN_USER_ID=your_telegram_user_id_here

# إعدادات Bybit API
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here

# إعدادات MEXC API
# ملاحظة: MEXC تدعم التداول الفوري (Spot) فقط - لا يوجد دعم للفيوتشر
MEXC_API_KEY={api_key}
MEXC_API_SECRET={api_secret}

# إعدادات Webhook
WEBHOOK_PORT=5000
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(" تم إنشاء ملف .env")
    
    # اختبار الاتصال
    print("\n🔌 اختبار الاتصال بـ MEXC...")
    
    try:
        from mexc_trading_bot import create_mexc_bot
        
        bot = create_mexc_bot(api_key, api_secret)
        
        if bot.test_connection():
            print(" الاتصال بـ MEXC ناجح!")
            
            # عرض بعض المعلومات
            balance = bot.get_account_balance()
            if balance:
                print("\n معلومات الحساب:")
                print(f"   • يمكن التداول: {'نعم' if balance['can_trade'] else 'لا'}")
                
                # عرض الرصيد
                has_balance = False
                for asset, info in balance['balances'].items():
                    if info['total'] > 0:
                        if not has_balance:
                            print("\n💵 الأرصدة:")
                            has_balance = True
                        print(f"   • {asset}: {info['total']:.8f}")
                
                if not has_balance:
                    print("    لا يوجد رصيد في الحساب")
            
            print("\n" + "=" * 70)
            print(" تم إعداد MEXC بنجاح!")
            print("=" * 70)
            print("\n الخطوات التالية:")
            print("   1. شغّل البوت: python app.py")
            print("   2. اختبر الإشارات: python test_send_signal.py")
            print("   3. اختر المنصة: 2 (MEXC)")
            print("\n📚 للمزيد من المعلومات:")
            print("   • README_MEXC.md - دليل شامل")
            print("   • INTEGRATION_GUIDE_MEXC.md - دليل التكامل")
            
            return True
        else:
            print(" فشل الاتصال بـ MEXC")
            print("\n تحقق من:")
            print("   • صحة API Key و Secret")
            print("   • تفعيل API Key في حسابك على MEXC")
            print("   • صلاحيات API Key (يجب تفعيل Spot Trading)")
            return False
    
    except ImportError:
        print(" لم يتم تثبيت المكتبات المطلوبة")
        print(" قم بتشغيل: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f" خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n مرحباً بك في إعداد MEXC API")
    print("=" * 70)
    print("\n ملاحظة هامة:")
    print("   MEXC تدعم التداول الفوري (Spot) فقط")
    print("   لا يوجد دعم لتداول الفيوتشر عبر API")
    print("\n" + "=" * 70)
    
    try:
        success = setup_mexc_api()
        
        if success:
            print("\n تم الإعداد بنجاح!")
        else:
            print("\n فشل الإعداد")
    
    except KeyboardInterrupt:
        print("\n\n تم إلغاء الإعداد")
    except Exception as e:
        print(f"\n\n خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()

