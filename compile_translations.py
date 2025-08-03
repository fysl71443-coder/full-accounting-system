#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تجميع ملفات الترجمة
Compile Translation Files Script
"""

import os
import subprocess
import sys

def run_command(command, description):
    """تشغيل أمر في الطرفية مع معالجة الأخطاء"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - تم بنجاح")
        if result.stdout:
            print(f"📄 الإخراج: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في {description}")
        print(f"📄 رسالة الخطأ: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع في {description}: {e}")
        return False

def main():
    """الوظيفة الرئيسية لتجميع الترجمات"""
    print("🌐 سكريبت تجميع ملفات الترجمة")
    print("=" * 50)
    
    # التحقق من وجود babel
    if not run_command("pybabel --version", "فحص تثبيت Babel"):
        print("❌ يرجى تثبيت Flask-Babel أولاً:")
        print("pip install Flask-Babel")
        return False
    
    # استخراج النصوص القابلة للترجمة
    extract_cmd = "pybabel extract -F meal_babel.cfg -k _l -o messages.pot ."
    if not run_command(extract_cmd, "استخراج النصوص القابلة للترجمة"):
        return False
    
    # تحديث ملفات الترجمة الموجودة
    languages = ['ar', 'en']
    
    for lang in languages:
        po_file = f"translations/{lang}/LC_MESSAGES/messages.po"
        
        if os.path.exists(po_file):
            # تحديث الملف الموجود
            update_cmd = f"pybabel update -i messages.pot -d translations -l {lang}"
            if not run_command(update_cmd, f"تحديث ترجمة {lang}"):
                continue
        else:
            # إنشاء ملف ترجمة جديد
            init_cmd = f"pybabel init -i messages.pot -d translations -l {lang}"
            if not run_command(init_cmd, f"إنشاء ترجمة {lang}"):
                continue
        
        # تجميع الترجمة
        compile_cmd = f"pybabel compile -d translations -l {lang}"
        if run_command(compile_cmd, f"تجميع ترجمة {lang}"):
            print(f"✅ تم تجميع ترجمة {lang} بنجاح")
        else:
            print(f"❌ فشل في تجميع ترجمة {lang}")
    
    # تنظيف الملفات المؤقتة
    if os.path.exists("messages.pot"):
        os.remove("messages.pot")
        print("🧹 تم حذف الملفات المؤقتة")
    
    print("\n🎉 تم الانتهاء من تجميع الترجمات!")
    print("📁 ملفات .mo تم إنشاؤها في مجلدات translations/*/LC_MESSAGES/")
    print("🚀 يمكنك الآن تشغيل التطبيق مع دعم الترجمة")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
