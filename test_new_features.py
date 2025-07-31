#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار الميزات الجديدة في نظام المحاسبة
"""

import requests
import json
from datetime import datetime

class NewFeaturesTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, details=""):
        """تسجيل نتيجة الاختبار"""
        status = "✅ نجح" if success else "❌ فشل"
        result = f"{status} - {test_name}"
        if details:
            result += f" ({details})"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def login(self):
        """تسجيل الدخول"""
        try:
            response = self.session.post(f"{self.base_url}/login", data={
                'username': 'admin',
                'password': 'admin123'
            })
            success = response.status_code == 302 or "dashboard" in response.text
            self.log_test("تسجيل الدخول", success)
            return success
        except Exception as e:
            self.log_test("تسجيل الدخول", False, str(e))
            return False
    
    def test_sales_invoice_with_items(self):
        """اختبار فاتورة مبيعات مع أصناف"""
        try:
            # بيانات الفاتورة مع الأصناف
            invoice_data = {
                'invoice_number': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'customer_id': '',  # عميل نقدي
                'payment_method': 'mada',
                'has_tax': 'on',
                'tax_rate': '15',
                'subtotal': '1000.00',
                'tax_amount': '150.00',
                'total': '1150.00',
                'notes': 'فاتورة اختبار للأصناف الجديدة',
                # الأصناف
                'items[0][name]': 'منتج اختبار 1',
                'items[0][description]': 'وصف المنتج الأول',
                'items[0][quantity]': '2',
                'items[0][price]': '300.00',
                'items[0][total]': '600.00',
                'items[1][name]': 'منتج اختبار 2',
                'items[1][description]': 'وصف المنتج الثاني',
                'items[1][quantity]': '1',
                'items[1][price]': '400.00',
                'items[1][total]': '400.00'
            }
            
            response = self.session.post(f"{self.base_url}/add_sale", data=invoice_data)
            success = response.status_code in [200, 302]
            self.log_test("إنشاء فاتورة مبيعات مع أصناف", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("إنشاء فاتورة مبيعات مع أصناف", False, str(e))
            return False
    
    def test_payment_methods(self):
        """اختبار طرق الدفع الجديدة"""
        payment_methods = ['mada', 'visa', 'mastercard', 'stc', 'gcc', 'aks', 'bank', 'cash']
        
        for method in payment_methods:
            try:
                invoice_data = {
                    'invoice_number': f'PAY-{method}-{datetime.now().strftime("%H%M%S")}',
                    'payment_method': method,
                    'has_tax': '',  # بدون ضريبة
                    'tax_rate': '0',
                    'subtotal': '100.00',
                    'tax_amount': '0.00',
                    'total': '100.00',
                    'items[0][name]': f'اختبار طريقة دفع {method}',
                    'items[0][quantity]': '1',
                    'items[0][price]': '100.00',
                    'items[0][total]': '100.00'
                }
                
                response = self.session.post(f"{self.base_url}/add_sale", data=invoice_data)
                success = response.status_code in [200, 302]
                self.log_test(f"طريقة الدفع: {method}", success)
            except Exception as e:
                self.log_test(f"طريقة الدفع: {method}", False, str(e))
    
    def test_tax_control(self):
        """اختبار التحكم في الضريبة"""
        try:
            # فاتورة بدون ضريبة
            no_tax_data = {
                'invoice_number': f'NOTAX-{datetime.now().strftime("%H%M%S")}',
                'payment_method': 'cash',
                'has_tax': '',  # بدون ضريبة
                'tax_rate': '0',
                'subtotal': '500.00',
                'tax_amount': '0.00',
                'total': '500.00',
                'items[0][name]': 'منتج بدون ضريبة',
                'items[0][quantity]': '1',
                'items[0][price]': '500.00',
                'items[0][total]': '500.00'
            }
            
            response = self.session.post(f"{self.base_url}/add_sale", data=no_tax_data)
            success = response.status_code in [200, 302]
            self.log_test("فاتورة بدون ضريبة", success)
            
            # فاتورة بضريبة مخصصة
            custom_tax_data = {
                'invoice_number': f'CTAX-{datetime.now().strftime("%H%M%S")}',
                'payment_method': 'visa',
                'has_tax': 'on',
                'tax_rate': '10',  # ضريبة 10%
                'subtotal': '1000.00',
                'tax_amount': '100.00',
                'total': '1100.00',
                'items[0][name]': 'منتج بضريبة مخصصة',
                'items[0][quantity]': '1',
                'items[0][price]': '1000.00',
                'items[0][total]': '1000.00'
            }
            
            response = self.session.post(f"{self.base_url}/add_sale", data=custom_tax_data)
            success = response.status_code in [200, 302]
            self.log_test("فاتورة بضريبة مخصصة (10%)", success)
            
        except Exception as e:
            self.log_test("اختبار التحكم في الضريبة", False, str(e))
    
    def test_employee_with_payroll_settings(self):
        """اختبار إضافة موظف مع إعدادات الراتب"""
        try:
            employee_data = {
                'name': 'موظف اختبار الراتب',
                'position': 'محاسب',
                'salary': '5000.00',
                'hire_date': '2024-01-01',
                'phone': '0501234567',
                'email': 'test.employee@company.com',
                'working_days': '26',
                'overtime_rate': '50.00',
                'allowances': '500.00',
                'deductions': '200.00'
            }
            
            response = self.session.post(f"{self.base_url}/add_employee", data=employee_data)
            success = response.status_code in [200, 302]
            self.log_test("إضافة موظف مع إعدادات الراتب", success, f"كود الاستجابة: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("إضافة موظف مع إعدادات الراتب", False, str(e))
            return False
    
    def test_reports_access(self):
        """اختبار الوصول للتقارير المطورة"""
        reports = [
            ('expenses_report', 'تقرير المصروفات التفصيلي'),
            ('inventory_report', 'تقرير المخزون التفصيلي'),
            ('reports', 'صفحة التقارير الرئيسية')
        ]
        
        for endpoint, name in reports:
            try:
                response = self.session.get(f"{self.base_url}/{endpoint}")
                success = response.status_code == 200
                self.log_test(f"الوصول لـ {name}", success, f"كود الاستجابة: {response.status_code}")
            except Exception as e:
                self.log_test(f"الوصول لـ {name}", False, str(e))
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 بدء اختبار الميزات الجديدة")
        print("=" * 60)
        
        # تسجيل الدخول أولاً
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return
        
        print("\n📋 اختبار فواتير المبيعات الجديدة:")
        print("-" * 40)
        self.test_sales_invoice_with_items()
        self.test_payment_methods()
        self.test_tax_control()
        
        print("\n👥 اختبار نظام الموظفين المحسن:")
        print("-" * 40)
        self.test_employee_with_payroll_settings()
        
        print("\n📊 اختبار التقارير المطورة:")
        print("-" * 40)
        self.test_reports_access()
        
        # عرض النتائج النهائية
        print("\n" + "=" * 60)
        print("📈 ملخص نتائج الاختبار:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"   📊 إجمالي الاختبارات: {total_tests}")
        print(f"   ✅ نجح: {passed_tests}")
        print(f"   ❌ فشل: {failed_tests}")
        print(f"   📈 معدل النجاح: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ الاختبارات الفاشلة:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = NewFeaturesTest()
    tester.run_all_tests()
