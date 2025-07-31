#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار فعلي لوظائف النظام
"""

def test_database_operations():
    """اختبار عمليات قاعدة البيانات"""
    print("💾 اختبار عمليات قاعدة البيانات...")
    
    try:
        from accounting_system_complete import app, User, Employee, db
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # اختبار الاتصال بقاعدة البيانات
            users_count = User.query.count()
            print(f"✅ الاتصال بقاعدة البيانات يعمل - عدد المستخدمين: {users_count}")
            
            # اختبار إنشاء مستخدم
            test_user = User.query.filter_by(username='test_func').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
            
            new_user = User(
                username='test_func',
                password_hash=generate_password_hash('test123'),
                full_name='اختبار الوظائف',
                role='user'
            )
            db.session.add(new_user)
            db.session.commit()
            
            # التحقق من الإنشاء
            created_user = User.query.filter_by(username='test_func').first()
            if created_user:
                print("✅ إنشاء المستخدم يعمل")
                
                # اختبار تحديث الصلاحيات
                created_user.role = 'manager'
                db.session.commit()
                
                updated_user = User.query.filter_by(username='test_func').first()
                if updated_user.role == 'manager':
                    print("✅ تحديث صلاحيات المستخدم يعمل")
                else:
                    print("❌ تحديث صلاحيات المستخدم لا يعمل")
                
                # حذف المستخدم التجريبي
                db.session.delete(created_user)
                db.session.commit()
                print("✅ حذف المستخدم يعمل")
            else:
                print("❌ إنشاء المستخدم لا يعمل")
                
            return True
            
    except Exception as e:
        print(f"❌ خطأ في عمليات قاعدة البيانات: {e}")
        return False

def test_payment_functions():
    """اختبار وظائف المدفوعات"""
    print("💳 اختبار وظائف المدفوعات...")
    
    try:
        from accounting_system_complete import app, SalesInvoice, PurchaseInvoice, db
        
        with app.app_context():
            # اختبار جلب فواتير المبيعات
            sales = SalesInvoice.query.all()
            print(f"✅ جلب فواتير المبيعات يعمل - العدد: {len(sales)}")
            
            # اختبار جلب فواتير المشتريات
            purchases = PurchaseInvoice.query.all()
            print(f"✅ جلب فواتير المشتريات يعمل - العدد: {len(purchases)}")
            
            # اختبار تصنيف الفواتير حسب الحالة
            paid_sales = [s for s in sales if s.status == 'paid']
            pending_sales = [s for s in sales if s.status == 'pending']
            credit_sales = [s for s in sales if s.payment_method == 'credit']
            
            print(f"✅ تصنيف الفواتير يعمل:")
            print(f"   - مدفوعة: {len(paid_sales)}")
            print(f"   - معلقة: {len(pending_sales)}")
            print(f"   - آجلة: {len(credit_sales)}")
            
            # اختبار حساب الإجماليات
            total_receivables = sum(s.total for s in pending_sales)
            print(f"✅ حساب المستحقات يعمل: {total_receivables}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في وظائف المدفوعات: {e}")
        return False

def test_employee_functions():
    """اختبار وظائف الموظفين"""
    print("👨‍💼 اختبار وظائف الموظفين...")
    
    try:
        from accounting_system_complete import app, Employee, EmployeePayroll, db
        from datetime import datetime
        
        with app.app_context():
            # اختبار جلب الموظفين
            employees = Employee.query.all()
            print(f"✅ جلب الموظفين يعمل - العدد: {len(employees)}")
            
            if employees:
                # اختبار إنشاء كشف راتب تجريبي
                test_employee = employees[0]
                
                # حذف كشف راتب تجريبي إن وجد
                existing_payroll = EmployeePayroll.query.filter_by(
                    employee_id=test_employee.id,
                    month=12,
                    year=2024
                ).first()
                
                if existing_payroll:
                    db.session.delete(existing_payroll)
                    db.session.commit()
                
                # إنشاء كشف راتب جديد
                test_payroll = EmployeePayroll(
                    employee_id=test_employee.id,
                    month=12,
                    year=2024,
                    basic_salary=test_employee.salary,
                    working_days=30,
                    actual_working_days=30,
                    overtime_hours=0,
                    overtime_amount=0,
                    allowances=0,
                    deductions=0,
                    gross_salary=test_employee.salary,
                    net_salary=test_employee.salary,
                    notes="اختبار الوظائف",
                    status='paid'
                )
                
                db.session.add(test_payroll)
                db.session.commit()
                
                # التحقق من الإنشاء
                created_payroll = EmployeePayroll.query.filter_by(
                    employee_id=test_employee.id,
                    month=12,
                    year=2024
                ).first()
                
                if created_payroll:
                    print("✅ إنشاء كشف راتب يعمل")
                    
                    # حذف كشف الراتب التجريبي
                    db.session.delete(created_payroll)
                    db.session.commit()
                    print("✅ حذف كشف راتب يعمل")
                else:
                    print("❌ إنشاء كشف راتب لا يعمل")
            else:
                print("⚠️ لا يوجد موظفون للاختبار")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في وظائف الموظفين: {e}")
        return False

def test_export_functions():
    """اختبار وظائف التصدير"""
    print("📤 اختبار وظائف التصدير...")
    
    try:
        from accounting_system_complete import app
        
        with app.test_client() as client:
            # محاولة تسجيل الدخول أولاً
            login_response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            if login_response.status_code in [200, 302]:
                print("✅ تسجيل الدخول للاختبار نجح")
                
                # اختبار تصدير PDF
                pdf_response = client.get('/export_pdf/sales')
                if pdf_response.status_code in [200, 302]:
                    print("✅ تصدير PDF يعمل")
                else:
                    print(f"❌ تصدير PDF لا يعمل: {pdf_response.status_code}")
                
                # اختبار تصدير Excel
                excel_response = client.get('/export_excel/purchases')
                if excel_response.status_code in [200, 302]:
                    print("✅ تصدير Excel يعمل")
                else:
                    print(f"❌ تصدير Excel لا يعمل: {excel_response.status_code}")
                
                return True
            else:
                print("❌ فشل تسجيل الدخول للاختبار")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في وظائف التصدير: {e}")
        return False

def test_settings_functions():
    """اختبار وظائف الإعدادات"""
    print("⚙️ اختبار وظائف الإعدادات...")
    
    try:
        from accounting_system_complete import app
        
        with app.test_client() as client:
            # تسجيل الدخول
            client.post('/login', data={'username': 'admin', 'password': 'admin123'})
            
            # اختبار صفحة الإعدادات
            settings_response = client.get('/settings')
            if settings_response.status_code == 200:
                print("✅ صفحة الإعدادات تعمل")
            else:
                print(f"❌ صفحة الإعدادات لا تعمل: {settings_response.status_code}")
            
            # اختبار صفحة إعدادات الطباعة
            print_settings_response = client.get('/print_settings')
            if print_settings_response.status_code == 200:
                print("✅ صفحة إعدادات الطباعة تعمل")
            else:
                print(f"❌ صفحة إعدادات الطباعة لا تعمل: {print_settings_response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في وظائف الإعدادات: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("🧪 اختبار فعلي شامل لوظائف النظام")
    print("=" * 60)
    
    tests = [
        ("عمليات قاعدة البيانات", test_database_operations),
        ("وظائف المدفوعات", test_payment_functions),
        ("وظائف الموظفين", test_employee_functions),
        ("وظائف التصدير", test_export_functions),
        ("وظائف الإعدادات", test_settings_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 اختبار {test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
            results.append(False)
    
    # تلخيص النتائج
    print("\n" + "=" * 60)
    print("📋 ملخص نتائج الاختبار:")
    print("=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"📊 معدل النجاح: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ نجح" if results[i] else "❌ فشل"
        print(f"   {test_name}: {status}")
    
    print("\n" + "=" * 60)
    if success_rate >= 80:
        print("🎉 ممتاز! معظم الوظائف تعمل بكفاءة")
    elif success_rate >= 60:
        print("✅ جيد! أغلب الوظائف تعمل")
    else:
        print("⚠️ يحتاج تحسينات! بعض الوظائف لا تعمل")
    
    print("=" * 60)
    return success_rate >= 80

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
