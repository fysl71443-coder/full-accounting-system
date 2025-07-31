#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نهائي سريع لنظام المحاسبة
"""

def test_system_simple():
    """اختبار بسيط للنظام"""
    print("🔍 اختبار سريع لنظام المحاسبة الاحترافي")
    print("=" * 50)

    try:
        # اختبار استيراد النظام
        print("📦 اختبار استيراد النظام...")
        from accounting_system_complete import app, init_db
        print("✅ تم استيراد النظام بنجاح")

        # اختبار التطبيق
        print("🚀 اختبار التطبيق...")
        if app:
            routes_count = len(app.url_map._rules)
            print(f"✅ التطبيق جاهز مع {routes_count} مسار")
        else:
            print("❌ التطبيق غير متوفر")
            return False

        # اختبار قاعدة البيانات
        print("💾 اختبار قاعدة البيانات...")
        with app.app_context():
            init_db()
            print("✅ قاعدة البيانات جاهزة")

        # اختبار المسارات المهمة
        print("🔗 اختبار المسارات المهمة...")
        important_routes = [
            '/dashboard', '/sales', '/purchases', '/employees',
            '/reports', '/payments', '/payments_report', '/users',
            '/print_settings', '/settings'
        ]

        existing_routes = [str(rule) for rule in app.url_map.iter_rules()]
        missing_routes = []

        for route in important_routes:
            found = any(route in existing_route for existing_route in existing_routes)
            if found:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} مفقود")
                missing_routes.append(route)

        if missing_routes:
            print(f"   ⚠️  {len(missing_routes)} مسار مفقود")
            return False

        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ النظام جاهز للعمل")
        return True

    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

if __name__ == "__main__":
    print("🚀 اختبار نظام المحاسبة الاحترافي")
    print("=" * 50)

    success = test_system_simple()

    print("\n" + "=" * 50)
    if success:
        print("🎯 النظام جاهز للاستخدام!")
        print("💡 لتشغيل النظام:")
        print("   python app.py")
        print("   ثم افتح المتصفح على: http://localhost:5000")
        print("   تسجيل الدخول: admin / admin123")
    else:
        print("❌ يوجد مشاكل في النظام!")
        print("💡 يرجى مراجعة الأخطاء أعلاه")

    print("=" * 50)
