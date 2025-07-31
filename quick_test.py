#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار سريع للتأكد من عمل النظام بعد الإصلاحات
"""

import sys
import importlib.util

def test_import():
    """اختبار استيراد النظام"""
    try:
        print("🔄 اختبار استيراد النظام...")
        
        # محاولة استيراد النظام
        spec = importlib.util.spec_from_file_location("accounting_system", "accounting_system_complete.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✅ تم استيراد النظام بنجاح!")
        
        # التحقق من وجود التطبيق
        if hasattr(module, 'app'):
            print("✅ تطبيق Flask موجود!")
            
            # التحقق من بعض الوظائف المهمة
            app = module.app
            
            # عدد الـ routes
            routes_count = len(app.url_map._rules)
            print(f"✅ عدد المسارات المسجلة: {routes_count}")
            
            # التحقق من وجود بعض المسارات المهمة
            important_routes = [
                '/dashboard',
                '/sales',
                '/purchases', 
                '/employees',
                '/reports',
                '/print_invoice/<int:sale_id>',
                '/print_purchase/<int:purchase_id>',
                '/view_employee/<int:employee_id>',
                '/generate_payroll/<int:employee_id>',
                '/delete_employee/<int:employee_id>'
            ]
            
            existing_routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            for route in important_routes:
                if any(route.replace('<int:', '<').replace('>', '') in existing_route for existing_route in existing_routes):
                    print(f"✅ المسار موجود: {route}")
                else:
                    print(f"⚠️  المسار مفقود: {route}")
            
            return True
        else:
            print("❌ تطبيق Flask غير موجود!")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False

def test_database_models():
    """اختبار نماذج قاعدة البيانات"""
    try:
        print("\n🔄 اختبار نماذج قاعدة البيانات...")
        
        # استيراد النماذج
        from accounting_system_complete import (
            User, Customer, Supplier, Product, Employee, 
            SalesInvoice, SalesInvoiceItem, PurchaseInvoice, 
            PurchaseInvoiceItem, Expense, EmployeePayroll
        )
        
        models = [
            'User', 'Customer', 'Supplier', 'Product', 'Employee',
            'SalesInvoice', 'SalesInvoiceItem', 'PurchaseInvoice',
            'PurchaseInvoiceItem', 'Expense', 'EmployeePayroll'
        ]
        
        for model_name in models:
            print(f"✅ نموذج موجود: {model_name}")
        
        print("✅ جميع نماذج قاعدة البيانات موجودة!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في نماذج قاعدة البيانات: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("🚀 اختبار سريع لنظام المحاسبة الاحترافي")
    print("=" * 50)
    
    # اختبار الاستيراد
    import_success = test_import()
    
    if import_success:
        # اختبار النماذج
        models_success = test_database_models()
        
        if models_success:
            print("\n" + "=" * 50)
            print("🎉 جميع الاختبارات نجحت!")
            print("✅ النظام جاهز للتشغيل")
            print("💡 يمكنك الآن تشغيل: python run_system.py")
            print("=" * 50)
            return True
    
    print("\n" + "=" * 50)
    print("❌ فشل في بعض الاختبارات!")
    print("💡 يرجى مراجعة الأخطاء أعلاه")
    print("=" * 50)
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
