#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف اختبار لتشغيل الخادم واختبار المبدلات
"""

from accounting_system_complete import app, db
import webbrowser
import threading
import time

def open_browser():
    """فتح المتصفح بعد تأخير قصير"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000/dashboard')

def main():
    print("🚀 تشغيل خادم الاختبار...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # إنشاء الجداول
            db.create_all()
            print("✅ قاعدة البيانات جاهزة")
            
            # فحص إعدادات الفروع
            branches = app.config.get('BRANCHES', {})
            print(f"✅ الفروع المتاحة: {len(branches)}")
            for branch_name in branches.keys():
                print(f"   🏢 {branch_name}")
            
            # فحص إعدادات اللغات
            languages = app.config.get('LANGUAGES', {})
            print(f"✅ اللغات المتاحة: {len(languages)}")
            for lang_code, lang_name in languages.items():
                print(f"   🌐 {lang_code}: {lang_name}")
            
        except Exception as e:
            print(f"❌ خطأ في التهيئة: {e}")
            return
    
    print("\n🌐 الخادم سيعمل على: http://127.0.0.1:5000")
    print("📋 للاختبار:")
    print("   1. انتقل إلى http://127.0.0.1:5000/dashboard")
    print("   2. سجل الدخول: admin / admin123")
    print("   3. اختبر مبدل اللغة (🌐)")
    print("   4. اختبر مبدل الفروع (🏢)")
    print("   5. اختبر شاشة إدارة المستخدمين")
    print("\n⚠️ اضغط Ctrl+C لإيقاف الخادم")
    print("=" * 50)
    
    # فتح المتصفح تلقائياً
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # تشغيل الخادم
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # تجنب إعادة التحميل المزدوج
        )
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف الخادم")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل الخادم: {e}")

if __name__ == '__main__':
    main()
