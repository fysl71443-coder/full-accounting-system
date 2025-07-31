#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشغيل نظام المحاسبة الاحترافي مع الإصلاحات
"""

import os
import sys
import subprocess
import time

def check_system():
    """فحص النظام قبل التشغيل"""
    print("🔍 فحص النظام قبل التشغيل...")
    
    # فحص وجود الملفات المطلوبة
    required_files = [
        'accounting_system_complete.py',
        'app.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} مفقود")
            return False
    
    # تشغيل فحص الإصلاحات
    print("\n🔧 تشغيل فحص الإصلاحات...")
    try:
        result = subprocess.run([sys.executable, 'fix_deployment.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ فحص الإصلاحات نجح")
        else:
            print("❌ فحص الإصلاحات فشل")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ خطأ في فحص الإصلاحات: {e}")
        return False
    
    # تشغيل الاختبار السريع
    print("\n⚡ تشغيل الاختبار السريع...")
    try:
        result = subprocess.run([sys.executable, 'quick_test.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ الاختبار السريع نجح")
        else:
            print("❌ الاختبار السريع فشل")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ خطأ في الاختبار السريع: {e}")
        return False
    
    return True

def install_requirements():
    """تثبيت المتطلبات"""
    print("📦 تثبيت المتطلبات...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ تم تثبيت المتطلبات بنجاح")
            return True
        else:
            print("❌ فشل في تثبيت المتطلبات")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False

def run_system():
    """تشغيل النظام"""
    print("🚀 تشغيل نظام المحاسبة الاحترافي...")
    print("=" * 50)
    
    try:
        # استيراد النظام
        from accounting_system_complete import app, init_db
        
        # تهيئة قاعدة البيانات
        print("🔄 تهيئة قاعدة البيانات...")
        with app.app_context():
            init_db()
        print("✅ تم تهيئة قاعدة البيانات")
        
        # تشغيل الخادم
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 تشغيل الخادم على المنفذ {port}")
        print(f"🔗 رابط النظام: http://localhost:{port}")
        print("👤 تسجيل الدخول: admin / admin123")
        print("=" * 50)
        print("💡 اضغط Ctrl+C لإيقاف الخادم")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """الوظيفة الرئيسية"""
    print("🎯 تشغيل نظام المحاسبة الاحترافي - الإصدار المُصلح")
    print("=" * 60)
    
    # فحص النظام
    if not check_system():
        print("❌ فشل في فحص النظام!")
        return False
    
    # تثبيت المتطلبات
    if not install_requirements():
        print("❌ فشل في تثبيت المتطلبات!")
        return False
    
    print("\n✅ جميع الفحوصات نجحت!")
    print("🚀 بدء تشغيل النظام...")
    time.sleep(2)
    
    # تشغيل النظام
    return run_system()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ فشل في تشغيل النظام!")
        sys.exit(1)
    else:
        print("\n✅ تم إغلاق النظام بنجاح")
        sys.exit(0)
