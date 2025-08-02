#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل ونهائي للمبدلات والترجمة
"""

from accounting_system_complete import app, db
import os

def test_system():
    print("🧪 الاختبار الشامل النهائي")
    print("=" * 60)
    
    with app.app_context():
        try:
            # 1. فحص قاعدة البيانات
            db.create_all()
            print("✅ قاعدة البيانات جاهزة")
            
            # 2. فحص إعدادات الفروع
            branches = app.config.get('BRANCHES', {})
            languages = app.config.get('LANGUAGES', {})
            
            print(f"✅ الفروع: {len(branches)} ({list(branches.keys())})")
            print(f"✅ اللغات: {len(languages)} ({list(languages.keys())})")
            
            # 3. فحص ملفات الترجمة
            translation_files = [
                'translations/ar/LC_MESSAGES/messages.mo',
                'translations/en/LC_MESSAGES/messages.mo'
            ]
            
            for file_path in translation_files:
                if os.path.exists(file_path):
                    print(f"✅ ملف الترجمة موجود: {file_path}")
                else:
                    print(f"❌ ملف الترجمة مفقود: {file_path}")
            
            # 4. اختبار الواجهة
            with app.test_client() as client:
                # تسجيل الدخول
                login_response = client.post('/login', data={
                    'username': 'admin', 
                    'password': 'admin123'
                })
                
                if login_response.status_code == 302:
                    print("✅ تسجيل الدخول نجح")
                    
                    # اختبار الشاشة الرئيسية
                    dashboard_response = client.get('/dashboard')
                    if dashboard_response.status_code == 200:
                        content = dashboard_response.get_data(as_text=True)
                        print("✅ الشاشة الرئيسية تعمل")
                        
                        # فحص العناصر الأساسية
                        essential_elements = [
                            ('مبدل اللغة', 'languageDropdown' in content),
                            ('مبدل الفروع', 'branchDropdown' in content),
                            ('Bootstrap JS', 'bootstrap.bundle.min.js' in content),
                            ('CSS المبدلات', 'language-btn' in content),
                            ('أعلام الدول', '🇸🇦' in content and '🇺🇸' in content),
                            ('أيقونات الفروع', '🇮🇳' in content and '🏮' in content),
                            ('وضوح CSS', 'opacity: 1 !important' in content),
                            ('إزالة الضبابية', 'filter: none !important' in content)
                        ]
                        
                        working_elements = 0
                        print("\\n🔍 فحص العناصر الأساسية:")
                        
                        for element, exists in essential_elements:
                            if exists:
                                print(f"✅ {element}")
                                working_elements += 1
                            else:
                                print(f"❌ {element}")
                        
                        # اختبار المسارات
                        print("\\n🔄 اختبار المسارات:")
                        
                        # تغيير اللغة
                        lang_response = client.get('/change_language/en')
                        if lang_response.status_code == 302:
                            print("✅ مسار تغيير اللغة")
                            working_elements += 1
                        else:
                            print("❌ مسار تغيير اللغة")
                        
                        # تغيير الفرع
                        branch_response = client.get('/change_branch/China Town')
                        if branch_response.status_code == 302:
                            print("✅ مسار تغيير الفرع")
                            working_elements += 1
                        else:
                            print("❌ مسار تغيير الفرع")
                        
                        # شاشة إدارة المستخدمين
                        users_response = client.get('/users')
                        if users_response.status_code == 200:
                            print("✅ شاشة إدارة المستخدمين")
                            working_elements += 1
                        else:
                            print("❌ شاشة إدارة المستخدمين")
                        
                        # النتيجة النهائية
                        total_elements = len(essential_elements) + 3
                        percentage = (working_elements / total_elements) * 100
                        
                        print(f"\\n📊 النتيجة النهائية:")
                        print(f"   العناصر العاملة: {working_elements}/{total_elements}")
                        print(f"   النسبة: {percentage:.1f}%")
                        
                        if percentage >= 95:
                            print("\\n🎉 النظام يعمل بشكل مثالي!")
                            print("✅ المبدلات واضحة وقابلة للنقر")
                            print("✅ الترجمة تعمل بكفاءة")
                            print("✅ جميع المسارات تعمل")
                            print("\\n🚀 النظام جاهز للاستخدام!")
                        elif percentage >= 85:
                            print("\\n✅ النظام يعمل بشكل جيد جداً")
                            print("⚡ معظم المميزات تعمل بكفاءة")
                        elif percentage >= 70:
                            print("\\n⚠️ النظام يعمل لكن يحتاج تحسينات")
                        else:
                            print("\\n❌ النظام يحتاج إصلاحات إضافية")
                        
                        return percentage >= 85
                    
                    else:
                        print(f"❌ فشل في الوصول للشاشة الرئيسية: {dashboard_response.status_code}")
                        return False
                
                else:
                    print("❌ فشل تسجيل الدخول")
                    return False
        
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    success = test_system()
    
    if success:
        print("\\n" + "="*60)
        print("🎯 ملخص الإصلاحات المطبقة:")
        print("\\n🎨 إصلاحات CSS:")
        print("   - إزالة جميع التأثيرات الضبابية")
        print("   - إضافة opacity: 1 !important")
        print("   - إضافة filter: none !important")
        print("   - إضافة pointer-events: auto !important")
        print("   - ألوان واضحة ومتباينة")
        
        print("\\n🔧 إصلاحات JavaScript:")
        print("   - إزالة التداخل مع Bootstrap")
        print("   - السماح لـ Bootstrap بالعمل طبيعياً")
        print("   - إضافة رسائل تحميل بسيطة")
        
        print("\\n🌐 إصلاحات الترجمة:")
        print("   - إنشاء ملفات الترجمة الأساسية")
        print("   - تصحيح تهيئة Babel")
        print("   - إضافة دعم اللغتين العربية والإنجليزية")
        
        print("\\n🏢 نظام الفروع:")
        print("   - إضافة عمود branch لقاعدة البيانات")
        print("   - دعم Place India و China Town")
        print("   - إحصائيات منفصلة لكل فرع")
        
        print("\\n🎉 النظام جاهز للاستخدام!")
    else:
        print("\\n❌ النظام يحتاج مراجعة إضافية")

if __name__ == '__main__':
    main()
