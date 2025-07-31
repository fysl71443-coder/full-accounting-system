#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لجميع التقارير والأزرار
"""

import requests
import sys
from datetime import datetime

class ReportsTest:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def login(self):
        """تسجيل الدخول"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            return response.status_code in [200, 302]
        except Exception as e:
            print(f"خطأ في تسجيل الدخول: {e}")
            return False
    
    def test_reports_page(self):
        """اختبار صفحة التقارير الرئيسية"""
        try:
            response = self.session.get(f"{self.base_url}/reports")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} صفحة التقارير الرئيسية: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ صفحة التقارير الرئيسية: {e}")
            return False
    
    def test_employees_report(self):
        """اختبار تقرير الموظفين التفصيلي"""
        try:
            response = self.session.get(f"{self.base_url}/employees_report")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} تقرير الموظفين التفصيلي: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ تقرير الموظفين التفصيلي: {e}")
            return False
    
    def test_expenses_report(self):
        """اختبار تقرير المصروفات"""
        try:
            response = self.session.get(f"{self.base_url}/expenses_report")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} تقرير المصروفات: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ تقرير المصروفات: {e}")
            return False
    
    def test_inventory_report(self):
        """اختبار تقرير المخزون"""
        try:
            response = self.session.get(f"{self.base_url}/inventory_report")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} تقرير المخزون: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ تقرير المخزون: {e}")
            return False
    
    def test_payroll_report(self):
        """اختبار تقرير كشوف الرواتب"""
        try:
            response = self.session.get(f"{self.base_url}/payroll_report")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} تقرير كشوف الرواتب: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ تقرير كشوف الرواتب: {e}")
            return False
    
    def test_quick_reports(self):
        """اختبار التقارير السريعة"""
        periods = ['daily', 'weekly', 'monthly', 'yearly']
        results = []
        
        for period in periods:
            try:
                response = self.session.get(f"{self.base_url}/quick_report/{period}")
                success = response.status_code == 200
                print(f"{'✅' if success else '❌'} التقرير السريع ({period}): {response.status_code}")
                results.append(success)
            except Exception as e:
                print(f"❌ التقرير السريع ({period}): {e}")
                results.append(False)
        
        return all(results)
    
    def test_export_functions(self):
        """اختبار وظائف التصدير"""
        report_types = ['employees', 'expenses', 'inventory', 'payroll']
        export_types = ['pdf', 'excel']
        results = []
        
        for report_type in report_types:
            for export_type in export_types:
                try:
                    response = self.session.get(f"{self.base_url}/export_{export_type}/{report_type}")
                    success = response.status_code in [200, 302]  # 302 للإعادة التوجيه
                    print(f"{'✅' if success else '❌'} تصدير {report_type} كـ {export_type}: {response.status_code}")
                    results.append(success)
                except Exception as e:
                    print(f"❌ تصدير {report_type} كـ {export_type}: {e}")
                    results.append(False)
        
        return all(results)
    
    def test_print_functions(self):
        """اختبار وظائف الطباعة"""
        try:
            # اختبار طباعة فاتورة مبيعات
            response = self.session.get(f"{self.base_url}/print_invoice/1")
            invoice_print = response.status_code == 200
            print(f"{'✅' if invoice_print else '❌'} طباعة فاتورة المبيعات: {response.status_code}")
            
            # اختبار طباعة فاتورة مشتريات
            response = self.session.get(f"{self.base_url}/print_purchase/1")
            purchase_print = response.status_code == 200
            print(f"{'✅' if purchase_print else '❌'} طباعة فاتورة المشتريات: {response.status_code}")
            
            return invoice_print and purchase_print
        except Exception as e:
            print(f"❌ وظائف الطباعة: {e}")
            return False
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 اختبار شامل لجميع التقارير والأزرار")
        print("=" * 60)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        print("✅ تم تسجيل الدخول بنجاح")
        print("\n📊 اختبار التقارير:")
        print("-" * 30)
        
        tests = [
            ("صفحة التقارير الرئيسية", self.test_reports_page),
            ("تقرير الموظفين التفصيلي", self.test_employees_report),
            ("تقرير المصروفات", self.test_expenses_report),
            ("تقرير المخزون", self.test_inventory_report),
            ("تقرير كشوف الرواتب", self.test_payroll_report),
            ("التقارير السريعة", self.test_quick_reports),
            ("وظائف التصدير", self.test_export_functions),
            ("وظائف الطباعة", self.test_print_functions)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 اختبار {test_name}:")
            result = test_func()
            results.append(result)
        
        print("\n" + "=" * 60)
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            print("🎉 جميع الاختبارات نجحت!")
            print("✅ جميع التقارير والأزرار تعمل بكفاءة")
        else:
            print(f"⚠️  نجح {success_count}/{total_count} من الاختبارات")
            print("💡 يرجى مراجعة الاختبارات الفاشلة أعلاه")
        
        print("=" * 60)
        return success_count == total_count

def main():
    """الوظيفة الرئيسية"""
    tester = ReportsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
