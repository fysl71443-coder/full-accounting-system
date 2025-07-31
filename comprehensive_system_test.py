#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لجميع وظائف نظام المحاسبة الاحترافي
"""

import requests
import sys
from datetime import datetime
import time

class ComprehensiveSystemTest:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """تسجيل نتيجة الاختبار"""
        status = "✅" if success else "❌"
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
        
    def login(self):
        """تسجيل الدخول"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            success = response.status_code in [200, 302]
            self.log_test("تسجيل الدخول", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("تسجيل الدخول", False, str(e))
            return False
    
    def test_main_pages(self):
        """اختبار الصفحات الرئيسية"""
        pages = [
            ('/dashboard', 'لوحة التحكم'),
            ('/customers', 'إدارة العملاء'),
            ('/suppliers', 'إدارة الموردين'),
            ('/products', 'إدارة المنتجات'),
            ('/employees', 'إدارة الموظفين'),
            ('/sales', 'فواتير المبيعات'),
            ('/purchases', 'فواتير المشتريات'),
            ('/expenses', 'إدارة المصروفات'),
            ('/reports', 'التقارير'),
            ('/payments', 'المدفوعات والمستحقات'),
            ('/settings', 'الإعدادات')
        ]
        
        for url, name in pages:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                success = response.status_code == 200
                self.log_test(f"صفحة {name}", success, f"كود: {response.status_code}")
            except Exception as e:
                self.log_test(f"صفحة {name}", False, str(e))
    
    def test_reports(self):
        """اختبار التقارير التفصيلية"""
        reports = [
            ('/expenses_report', 'تقرير المصروفات التفصيلي'),
            ('/inventory_report', 'تقرير المخزون التفصيلي'),
            ('/employees_report', 'تقرير الموظفين التفصيلي'),
            ('/payroll_report', 'تقرير كشوف الرواتب'),
            ('/payments_report', 'تقرير المدفوعات التفصيلي')
        ]
        
        for url, name in reports:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                success = response.status_code == 200
                self.log_test(f"{name}", success, f"كود: {response.status_code}")
            except Exception as e:
                self.log_test(f"{name}", False, str(e))
    
    def test_export_functions(self):
        """اختبار وظائف التصدير"""
        export_types = [
            ('sales', 'المبيعات'),
            ('purchases', 'المشتريات'),
            ('expenses', 'المصروفات'),
            ('inventory', 'المخزون'),
            ('employees', 'الموظفين'),
            ('payroll', 'كشوف الرواتب'),
            ('payments', 'المدفوعات')
        ]
        
        for export_type, name in export_types:
            # اختبار تصدير PDF
            try:
                response = self.session.get(f"{self.base_url}/export_pdf/{export_type}")
                success = response.status_code in [200, 302]
                self.log_test(f"تصدير PDF - {name}", success, f"كود: {response.status_code}")
            except Exception as e:
                self.log_test(f"تصدير PDF - {name}", False, str(e))
            
            # اختبار تصدير Excel
            try:
                response = self.session.get(f"{self.base_url}/export_excel/{export_type}")
                success = response.status_code in [200, 302]
                self.log_test(f"تصدير Excel - {name}", success, f"كود: {response.status_code}")
            except Exception as e:
                self.log_test(f"تصدير Excel - {name}", False, str(e))
    
    def test_user_management(self):
        """اختبار إدارة المستخدمين"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            success = response.status_code == 200
            self.log_test("صفحة إدارة المستخدمين", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("صفحة إدارة المستخدمين", False, str(e))
    
    def test_print_settings(self):
        """اختبار إعدادات الطباعة"""
        try:
            response = self.session.get(f"{self.base_url}/print_settings")
            success = response.status_code == 200
            self.log_test("إعدادات الطباعة", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("إعدادات الطباعة", False, str(e))
    
    def test_payment_functions(self):
        """اختبار وظائف المدفوعات"""
        # اختبار تحديث حالة المدفوعات (محاكاة)
        try:
            response = self.session.post(f"{self.base_url}/mark_as_paid/sale/1")
            success = response.status_code in [200, 404]  # 404 إذا لم توجد الفاتورة
            self.log_test("تحديث حالة فاتورة مبيعات", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("تحديث حالة فاتورة مبيعات", False, str(e))
        
        try:
            response = self.session.post(f"{self.base_url}/mark_as_overdue/purchase/1")
            success = response.status_code in [200, 404]
            self.log_test("تحديث حالة فاتورة مشتريات", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("تحديث حالة فاتورة مشتريات", False, str(e))
    
    def test_employee_payment(self):
        """اختبار تسجيل دفع الموظفين"""
        try:
            response = self.session.get(f"{self.base_url}/record_employee_payment/1")
            success = response.status_code in [200, 404]
            self.log_test("صفحة تسجيل دفع الموظف", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("صفحة تسجيل دفع الموظف", False, str(e))
    
    def test_api_endpoints(self):
        """اختبار نقاط API"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            success = response.status_code == 200
            self.log_test("API Status", success, f"كود: {response.status_code}")
        except Exception as e:
            self.log_test("API Status", False, str(e))
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل"""
        print("🚀 بدء الاختبار الشامل لنظام المحاسبة الاحترافي")
        print("=" * 70)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        print("\n📄 اختبار الصفحات الرئيسية:")
        print("-" * 50)
        self.test_main_pages()
        
        print("\n📊 اختبار التقارير التفصيلية:")
        print("-" * 50)
        self.test_reports()
        
        print("\n📤 اختبار وظائف التصدير:")
        print("-" * 50)
        self.test_export_functions()
        
        print("\n👥 اختبار إدارة المستخدمين:")
        print("-" * 50)
        self.test_user_management()
        
        print("\n🖨️ اختبار إعدادات الطباعة:")
        print("-" * 50)
        self.test_print_settings()
        
        print("\n💳 اختبار وظائف المدفوعات:")
        print("-" * 50)
        self.test_payment_functions()
        
        print("\n👨‍💼 اختبار دفع الموظفين:")
        print("-" * 50)
        self.test_employee_payment()
        
        print("\n🔌 اختبار API:")
        print("-" * 50)
        self.test_api_endpoints()
        
        # تلخيص النتائج
        self.print_summary()
        
        return self.get_success_rate() > 0.8  # 80% نجاح على الأقل
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n" + "=" * 70)
        print("📋 ملخص نتائج الاختبار الشامل")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 إجمالي الاختبارات: {total_tests}")
        print(f"✅ الاختبارات الناجحة: {successful_tests}")
        print(f"❌ الاختبارات الفاشلة: {failed_tests}")
        print(f"📈 معدل النجاح: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ الاختبارات الفاشلة:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['name']}: {result['message']}")
        
        print("\n" + "=" * 70)
        if success_rate >= 90:
            print("🎉 ممتاز! النظام يعمل بكفاءة عالية")
        elif success_rate >= 80:
            print("✅ جيد! النظام يعمل بشكل مقبول")
        elif success_rate >= 60:
            print("⚠️ متوسط! يحتاج بعض التحسينات")
        else:
            print("❌ ضعيف! يحتاج مراجعة شاملة")
        print("=" * 70)
    
    def get_success_rate(self):
        """حساب معدل النجاح"""
        if not self.test_results:
            return 0
        successful = sum(1 for result in self.test_results if result['success'])
        return successful / len(self.test_results)

def main():
    """الوظيفة الرئيسية"""
    tester = ComprehensiveSystemTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
