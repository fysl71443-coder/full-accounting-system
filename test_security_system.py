#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 اختبار نظام الحماية المتقدم
Security System Testing Suite
"""

import requests
import time
import threading
from datetime import datetime

class SecurityTester:
    """فئة اختبار نظام الحماية"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, details=""):
        """تسجيل نتيجة الاختبار"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} - {test_name}: {details}")
    
    def test_sql_injection_protection(self):
        """اختبار الحماية من SQL Injection"""
        print("\n🔍 اختبار الحماية من SQL Injection...")
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1 #",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_payloads:
            try:
                response = self.session.post(f"{self.base_url}/login", 
                                           data={'username': payload, 'password': 'test'})
                
                if response.status_code == 403:
                    self.log_test("SQL Injection Protection", True, f"حُظر payload: {payload[:20]}...")
                elif response.status_code == 200 and "error" in response.text.lower():
                    self.log_test("SQL Injection Protection", True, f"تم رفض payload: {payload[:20]}...")
                else:
                    self.log_test("SQL Injection Protection", False, f"لم يُحظر payload: {payload[:20]}...")
                    
            except requests.exceptions.RequestException as e:
                self.log_test("SQL Injection Protection", False, f"خطأ في الطلب: {e}")
    
    def test_xss_protection(self):
        """اختبار الحماية من XSS"""
        print("\n🔍 اختبار الحماية من XSS...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            try:
                response = self.session.post(f"{self.base_url}/add_customer", 
                                           data={'name': payload, 'phone': '123456789'})
                
                if response.status_code == 403:
                    self.log_test("XSS Protection", True, f"حُظر payload: {payload[:30]}...")
                else:
                    self.log_test("XSS Protection", False, f"لم يُحظر payload: {payload[:30]}...")
                    
            except requests.exceptions.RequestException as e:
                self.log_test("XSS Protection", False, f"خطأ في الطلب: {e}")
    
    def test_brute_force_protection(self):
        """اختبار الحماية من Brute Force"""
        print("\n🔍 اختبار الحماية من Brute Force...")
        
        # محاولة تسجيل دخول متكررة بكلمات مرور خاطئة
        for i in range(10):
            try:
                response = self.session.post(f"{self.base_url}/login", 
                                           data={'username': 'admin', 'password': f'wrong_password_{i}'})
                
                if response.status_code == 403:
                    self.log_test("Brute Force Protection", True, f"تم حظر المحاولة رقم {i+1}")
                    break
                elif i == 9:
                    self.log_test("Brute Force Protection", False, "لم يتم حظر المحاولات المتكررة")
                    
            except requests.exceptions.RequestException as e:
                self.log_test("Brute Force Protection", False, f"خطأ في الطلب: {e}")
                break
    
    def test_rate_limiting(self):
        """اختبار حد المعدل"""
        print("\n🔍 اختبار حد المعدل...")
        
        def make_request():
            try:
                response = self.session.get(f"{self.base_url}/dashboard")
                return response.status_code
            except:
                return 0
        
        # إرسال طلبات متعددة بسرعة
        threads = []
        results = []
        
        for i in range(50):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        blocked_requests = sum(1 for status in results if status == 429)
        
        if blocked_requests > 0:
            self.log_test("Rate Limiting", True, f"تم حظر {blocked_requests} طلب من أصل 50")
        else:
            self.log_test("Rate Limiting", False, "لم يتم تطبيق حد المعدل")
    
    def test_honeypot_system(self):
        """اختبار نظام الفخاخ"""
        print("\n🔍 اختبار نظام الفخاخ...")
        
        honeypot_urls = [
            "/admin.php",
            "/wp-admin/",
            "/phpmyadmin/",
            "/.env",
            "/config.php"
        ]
        
        for url in honeypot_urls:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                
                if response.status_code == 403:
                    self.log_test("Honeypot System", True, f"تم اكتشاف الفخ: {url}")
                else:
                    self.log_test("Honeypot System", False, f"لم يتم اكتشاف الفخ: {url}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test("Honeypot System", False, f"خطأ في الطلب: {e}")
    
    def test_security_headers(self):
        """اختبار هيدرز الأمان"""
        print("\n🔍 اختبار هيدرز الأمان...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Content-Security-Policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                self.log_test("Security Headers", True, "جميع هيدرز الأمان موجودة")
            else:
                self.log_test("Security Headers", False, f"هيدرز مفقودة: {', '.join(missing_headers)}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Security Headers", False, f"خطأ في الطلب: {e}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🧪 بدء اختبار نظام الحماية المتقدم")
        print("=" * 60)
        
        start_time = time.time()
        
        # تشغيل الاختبارات
        self.test_security_headers()
        self.test_sql_injection_protection()
        self.test_xss_protection()
        self.test_brute_force_protection()
        self.test_rate_limiting()
        self.test_honeypot_system()
        
        end_time = time.time()
        
        # تلخيص النتائج
        print("\n" + "=" * 60)
        print("📊 ملخص نتائج الاختبار:")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ نجح: {passed_tests}")
        print(f"❌ فشل: {failed_tests}")
        print(f"📊 معدل النجاح: {success_rate:.1f}%")
        print(f"⏱️ وقت التنفيذ: {end_time - start_time:.2f} ثانية")
        
        if success_rate >= 80:
            print("\n🎉 ممتاز! نظام الحماية يعمل بكفاءة عالية")
        elif success_rate >= 60:
            print("\n✅ جيد! نظام الحماية يعمل بشكل مقبول")
        else:
            print("\n⚠️ تحذير! نظام الحماية يحتاج تحسينات")
        
        print("\n🔍 تفاصيل الاختبارات الفاشلة:")
        for result in self.test_results:
            if not result['success']:
                print(f"   ❌ {result['test']}: {result['details']}")
        
        return success_rate >= 80

def main():
    """الوظيفة الرئيسية"""
    print("🛡️ اختبار نظام الحماية المتقدم ضد الهاكرز")
    print("Advanced Security System Testing")
    print("=" * 60)
    
    # إنشاء مختبر الأمان
    tester = SecurityTester()
    
    # تشغيل الاختبارات
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 نظام الحماية جاهز ويوفر حماية قوية ضد الهاكرز!")
    else:
        print("⚠️ يرجى مراجعة نظام الحماية وإصلاح المشاكل المكتشفة")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
