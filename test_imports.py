#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار جميع الاستيرادات المطلوبة للنظام
"""

def test_all_imports():
    """اختبار جميع الاستيرادات"""
    print("🔍 اختبار جميع الاستيرادات المطلوبة...")
    print("=" * 50)
    
    imports_to_test = [
        # Python standard library
        ('os', 'مكتبة النظام'),
        ('datetime', 'مكتبة التاريخ والوقت'),
        ('decimal', 'مكتبة الأرقام العشرية'),
        
        # Flask core
        ('flask', 'إطار عمل Flask'),
        ('flask_sqlalchemy', 'قاعدة البيانات'),
        ('flask_login', 'نظام تسجيل الدخول'),
        ('werkzeug.security', 'الأمان والتشفير'),
        
        # Additional
        ('itsdangerous', 'الأمان الإضافي'),
        ('jinja2', 'محرك القوالب'),
        ('markupsafe', 'أمان HTML'),
        ('click', 'واجهة سطر الأوامر'),
        ('gunicorn', 'خادم الإنتاج')
    ]
    
    success_count = 0
    total_count = len(imports_to_test)
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<20} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name:<20} - {description} - خطأ: {e}")
        except Exception as e:
            print(f"⚠️  {module_name:<20} - {description} - تحذير: {e}")
    
    print("=" * 50)
    print(f"📊 النتيجة: {success_count}/{total_count} مكتبة متوفرة")
    
    if success_count == total_count:
        print("🎉 جميع المكتبات متوفرة!")
        return True
    else:
        print("⚠️  بعض المكتبات مفقودة")
        return False

def test_system_import():
    """اختبار استيراد النظام الكامل"""
    print("\n🔍 اختبار استيراد النظام الكامل...")
    print("-" * 30)
    
    try:
        # محاولة استيراد النظام
        from accounting_system_complete import app, init_db
        print("✅ تم استيراد النظام بنجاح!")
        
        # اختبار التطبيق
        if app:
            print("✅ تطبيق Flask جاهز!")
            
            # عدد المسارات
            routes_count = len(app.url_map._rules)
            print(f"✅ عدد المسارات: {routes_count}")
            
            return True
        else:
            print("❌ تطبيق Flask غير متوفر!")
            return False
            
    except ImportError as e:
        print(f"❌ خطأ في استيراد النظام: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("🚀 اختبار شامل للاستيرادات - نظام المحاسبة")
    print("=" * 60)
    
    # اختبار المكتبات
    imports_ok = test_all_imports()
    
    # اختبار النظام
    system_ok = test_system_import()
    
    print("\n" + "=" * 60)
    if imports_ok and system_ok:
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ النظام جاهز للتشغيل والنشر")
        print("💡 يمكنك الآن تشغيل: python app.py")
    else:
        print("❌ بعض الاختبارات فشلت!")
        if not imports_ok:
            print("💡 قم بتثبيت المكتبات المفقودة: pip install -r requirements.txt")
        if not system_ok:
            print("💡 تحقق من ملف accounting_system_complete.py")
    
    print("=" * 60)
    return imports_ok and system_ok

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
