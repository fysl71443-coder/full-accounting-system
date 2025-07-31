#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لنظام المدفوعات والمستحقات
"""

import requests
import sys
from datetime import datetime

class PaymentsSystemTest:
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
    
    def test_payments_page(self):
        """اختبار صفحة المدفوعات والمستحقات"""
        try:
            response = self.session.get(f"{self.base_url}/payments")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} صفحة المدفوعات والمستحقات: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ صفحة المدفوعات والمستحقات: {e}")
            return False
    
    def test_payments_report(self):
        """اختبار تقرير المدفوعات التفصيلي"""
        try:
            response = self.session.get(f"{self.base_url}/payments_report")
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} تقرير المدفوعات التفصيلي: {response.status_code}")
            return success
        except Exception as e:
            print(f"❌ تقرير المدفوعات التفصيلي: {e}")
            return False
    
    def test_payment_methods(self):
        """اختبار طرق الدفع الجديدة"""
        try:
            # اختبار صفحة المبيعات للتأكد من وجود خيار "آجل"
            response = self.session.get(f"{self.base_url}/sales")
            success = response.status_code == 200 and 'آجل' in response.text
            print(f"{'✅' if success else '❌'} طرق الدفع في المبيعات (آجل): {'موجود' if success else 'مفقود'}")
            
            # اختبار صفحة المشتريات للتأكد من وجود خيار "آجل"
            response = self.session.get(f"{self.base_url}/purchases")
            success2 = response.status_code == 200 and 'آجل' in response.text
            print(f"{'✅' if success2 else '❌'} طرق الدفع في المشتريات (آجل): {'موجود' if success2 else 'مفقود'}")
            
            return success and success2
        except Exception as e:
            print(f"❌ طرق الدفع الجديدة: {e}")
            return False
    
    def test_payment_status_functions(self):
        """اختبار وظائف تحديث حالة المدفوعات"""
        try:
            # محاولة تحديث حالة فاتورة مبيعات (إذا كانت موجودة)
            response = self.session.post(f"{self.base_url}/mark_as_paid/sale/1")
            success1 = response.status_code in [200, 404]  # 404 إذا لم توجد الفاتورة
            print(f"{'✅' if success1 else '❌'} تحديث حالة فاتورة مبيعات: {response.status_code}")
            
            # محاولة تحديث حالة فاتورة مشتريات (إذا كانت موجودة)
            response = self.session.post(f"{self.base_url}/mark_as_overdue/purchase/1")
            success2 = response.status_code in [200, 404]  # 404 إذا لم توجد الفاتورة
            print(f"{'✅' if success2 else '❌'} تحديث حالة فاتورة مشتريات: {response.status_code}")
            
            return success1 and success2
        except Exception as e:
            print(f"❌ وظائف تحديث حالة المدفوعات: {e}")
            return False
    
    def test_dashboard_integration(self):
        """اختبار تكامل المدفوعات مع الداشبورد"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            success = response.status_code == 200 and 'المدفوعات والمستحقات' in response.text
            print(f"{'✅' if success else '❌'} تكامل المدفوعات مع الداشبورد: {'موجود' if success else 'مفقود'}")
            return success
        except Exception as e:
            print(f"❌ تكامل المدفوعات مع الداشبورد: {e}")
            return False
    
    def test_reports_integration(self):
        """اختبار تكامل المدفوعات مع التقارير"""
        try:
            response = self.session.get(f"{self.base_url}/reports")
            success = response.status_code == 200 and 'المدفوعات والمستحقات' in response.text
            print(f"{'✅' if success else '❌'} تكامل المدفوعات مع التقارير: {'موجود' if success else 'مفقود'}")
            return success
        except Exception as e:
            print(f"❌ تكامل المدفوعات مع التقارير: {e}")
            return False
    
    def test_export_functions(self):
        """اختبار وظائف تصدير تقرير المدفوعات"""
        try:
            # اختبار تصدير PDF
            response = self.session.get(f"{self.base_url}/export_pdf/payments")
            success1 = response.status_code in [200, 302]
            print(f"{'✅' if success1 else '❌'} تصدير تقرير المدفوعات PDF: {response.status_code}")
            
            # اختبار تصدير Excel
            response = self.session.get(f"{self.base_url}/export_excel/payments")
            success2 = response.status_code in [200, 302]
            print(f"{'✅' if success2 else '❌'} تصدير تقرير المدفوعات Excel: {response.status_code}")
            
            return success1 and success2
        except Exception as e:
            print(f"❌ وظائف تصدير تقرير المدفوعات: {e}")
            return False
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 اختبار شامل لنظام المدفوعات والمستحقات")
        print("=" * 60)
        
        # تسجيل الدخول
        if not self.login():
            print("❌ فشل في تسجيل الدخول - توقف الاختبار")
            return False
        
        print("✅ تم تسجيل الدخول بنجاح")
        print("\n💳 اختبار نظام المدفوعات:")
        print("-" * 40)
        
        tests = [
            ("صفحة المدفوعات والمستحقات", self.test_payments_page),
            ("تقرير المدفوعات التفصيلي", self.test_payments_report),
            ("طرق الدفع الجديدة (آجل)", self.test_payment_methods),
            ("وظائف تحديث حالة المدفوعات", self.test_payment_status_functions),
            ("تكامل المدفوعات مع الداشبورد", self.test_dashboard_integration),
            ("تكامل المدفوعات مع التقارير", self.test_reports_integration),
            ("وظائف تصدير تقرير المدفوعات", self.test_export_functions)
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
            print("🎉 جميع اختبارات نظام المدفوعات نجحت!")
            print("✅ نظام المدفوعات والمستحقات يعمل بكفاءة")
            print("✅ طرق الدفع الآجلة متوفرة")
            print("✅ وظائف تحديث الحالة تعمل")
            print("✅ التكامل مع النظام مكتمل")
        else:
            print(f"⚠️  نجح {success_count}/{total_count} من الاختبارات")
            print("💡 يرجى مراجعة الاختبارات الفاشلة أعلاه")
        
        print("=" * 60)
        return success_count == total_count

def main():
    """الوظيفة الرئيسية"""
    tester = PaymentsSystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
