#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص سريع للنظام بعد النشر
"""

def check_system():
    """فحص سريع للنظام"""
    print("🔍 فحص سريع للنظام...")
    
    try:
        # اختبار الاستيراد
        print("1. اختبار الاستيراد...")
        from accounting_system_complete import app, init_db
        print("   ✅ تم استيراد النظام بنجاح")
        
        # اختبار التطبيق
        print("2. اختبار التطبيق...")
        if app:
            routes_count = len(app.url_map._rules)
            print(f"   ✅ التطبيق جاهز مع {routes_count} مسار")
        else:
            print("   ❌ التطبيق غير متوفر")
            return False
        
        # اختبار قاعدة البيانات
        print("3. اختبار قاعدة البيانات...")
        with app.app_context():
            init_db()
            print("   ✅ قاعدة البيانات جاهزة")
        
        # اختبار المسارات المهمة
        print("4. اختبار المسارات المهمة...")
        important_routes = [
            '/dashboard', '/sales', '/purchases', '/employees', 
            '/reports', '/payments', '/payments_report'
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
        
        print("\n🎉 جميع الفحوصات نجحت!")
        print("✅ النظام جاهز للعمل")
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("🚀 فحص سريع لنظام المحاسبة الاحترافي")
    print("=" * 50)
    
    success = check_system()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 النظام جاهز للاستخدام!")
        print("💡 يمكنك الآن:")
        print("   - تشغيل النظام: python app.py")
        print("   - اختبار المدفوعات: python test_payments_system.py")
        print("   - اختبار التقارير: python test_reports.py")
    else:
        print("❌ يوجد مشاكل في النظام!")
        print("💡 يرجى مراجعة الأخطاء أعلاه")
    
    print("=" * 50)
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
