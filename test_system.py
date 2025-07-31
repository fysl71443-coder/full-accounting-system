#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام المحاسبة الاحترافي
Comprehensive Test for Professional Accounting System
"""

import requests
import json
import time
from datetime import datetime

class SystemTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """تسجيل نتيجة الاختبار"""
        status = "✅ نجح" if success else "❌ فشل"
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}: {message}")
        
    def test_homepage(self):
        """اختبار الصفحة الرئيسية"""
        try:
            response = self.session.get(self.base_url)
            success = response.status_code == 200
            self.log_test("الصفحة الرئيسية", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("الصفحة الرئيسية", False, str(e))
            return False
    
    def test_login_page(self):
        """اختبار صفحة تسجيل الدخول"""
        try:
            response = self.session.get(f"{self.base_url}/login")
            success = response.status_code == 200 and "تسجيل الدخول" in response.text
            self.log_test("صفحة تسجيل الدخول", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة تسجيل الدخول", False, str(e))
            return False
    
    def test_login_functionality(self):
        """اختبار وظيفة تسجيل الدخول"""
        try:
            # الحصول على CSRF token
            login_page = self.session.get(f"{self.base_url}/login")
            
            # محاولة تسجيل الدخول
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            success = response.status_code in [200, 302]  # 302 للتوجيه بعد النجاح
            self.log_test("تسجيل الدخول", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("تسجيل الدخول", False, str(e))
            return False
    
    def test_dashboard(self):
        """اختبار لوحة التحكم"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            success = response.status_code == 200 and "لوحة التحكم" in response.text
            self.log_test("لوحة التحكم", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("لوحة التحكم", False, str(e))
            return False
    
    def test_customers_page(self):
        """اختبار صفحة العملاء"""
        try:
            response = self.session.get(f"{self.base_url}/customers")
            success = response.status_code == 200 and "العملاء" in response.text
            self.log_test("صفحة العملاء", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة العملاء", False, str(e))
            return False
    
    def test_suppliers_page(self):
        """اختبار صفحة الموردين"""
        try:
            response = self.session.get(f"{self.base_url}/suppliers")
            success = response.status_code == 200 and "الموردين" in response.text
            self.log_test("صفحة الموردين", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة الموردين", False, str(e))
            return False
    
    def test_products_page(self):
        """اختبار صفحة المنتجات"""
        try:
            response = self.session.get(f"{self.base_url}/products")
            success = response.status_code == 200 and "المنتجات" in response.text
            self.log_test("صفحة المنتجات", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة المنتجات", False, str(e))
            return False
    
    def test_sales_page(self):
        """اختبار صفحة المبيعات"""
        try:
            response = self.session.get(f"{self.base_url}/sales")
            success = response.status_code == 200 and "المبيعات" in response.text
            self.log_test("صفحة المبيعات", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة المبيعات", False, str(e))
            return False
    
    def test_reports_page(self):
        """اختبار صفحة التقارير"""
        try:
            response = self.session.get(f"{self.base_url}/reports")
            success = response.status_code == 200 and "التقارير" in response.text
            self.log_test("صفحة التقارير", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة التقارير", False, str(e))
            return False

    def test_expenses_page(self):
        """اختبار صفحة المصروفات"""
        try:
            response = self.session.get(f"{self.base_url}/expenses")
            success = response.status_code == 200 and "المصروفات" in response.text
            self.log_test("صفحة المصروفات", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة المصروفات", False, str(e))
            return False

    def test_purchases_page(self):
        """اختبار صفحة المشتريات"""
        try:
            response = self.session.get(f"{self.base_url}/purchases")
            success = response.status_code == 200 and "المشتريات" in response.text
            self.log_test("صفحة المشتريات", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة المشتريات", False, str(e))
            return False

    def test_settings_page(self):
        """اختبار صفحة الإعدادات"""
        try:
            response = self.session.get(f"{self.base_url}/settings")
            success = response.status_code == 200 and "إعدادات" in response.text
            self.log_test("صفحة الإعدادات", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة الإعدادات", False, str(e))
            return False

    def test_employees_page(self):
        """اختبار صفحة الموظفين"""
        try:
            response = self.session.get(f"{self.base_url}/employees")
            success = response.status_code == 200 and "الموظفين" in response.text
            self.log_test("صفحة الموظفين", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("صفحة الموظفين", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """اختبار نقاط النهاية API"""
        endpoints = [
            '/api/status',
            '/api/customers',
            '/api/suppliers',
            '/api/products',
            '/api/sales',
            '/api/statistics'
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                success = response.status_code == 200
                self.log_test(f"API {endpoint}", success, f"كود الاستجابة: {response.status_code}")
            except Exception as e:
                self.log_test(f"API {endpoint}", False, str(e))
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء الاختبار الشامل لنظام المحاسبة")
        print("=" * 60)
        
        # اختبار الاتصال الأساسي
        if not self.test_homepage():
            print("❌ فشل في الاتصال بالنظام. تأكد من تشغيل النظام أولاً.")
            return False
        
        # اختبار الصفحات الأساسية
        self.test_login_page()
        
        # تسجيل الدخول
        if self.test_login_functionality():
            # اختبار الصفحات المحمية
            self.test_dashboard()
            self.test_customers_page()
            self.test_suppliers_page()
            self.test_products_page()
            self.test_sales_page()
            self.test_purchases_page()
            self.test_expenses_page()
            self.test_employees_page()
            self.test_reports_page()
            self.test_settings_page()

            # اختبار API
            self.test_api_endpoints()
        
        # عرض النتائج
        self.show_results()
        
        return True
    
    def show_results(self):
        """عرض نتائج الاختبارات"""
        print("\n" + "=" * 60)
        print("📊 نتائج الاختبارات")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ نجح: {passed}")
        print(f"❌ فشل: {total - passed}")
        print(f"📈 معدل النجاح: {(passed/total)*100:.1f}%")
        
        # عرض الاختبارات الفاشلة
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n❌ الاختبارات الفاشلة:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        print("=" * 60)

def main():
    """الوظيفة الرئيسية"""
    print("🔧 اختبار نظام المحاسبة الاحترافي")
    print("تأكد من تشغيل النظام على http://localhost:5000")
    
    input("اضغط Enter للمتابعة...")
    
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == '__main__':
    main()
