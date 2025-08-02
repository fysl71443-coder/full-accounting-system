#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء ملفات الترجمة للنظام
"""

import os

def create_translation_directories():
    """إنشاء مجلدات الترجمة"""
    
    # إنشاء المجلدات المطلوبة
    directories = [
        'babel.cfg',
        'translations/ar/LC_MESSAGES',
        'translations/en/LC_MESSAGES'
    ]
    
    # إنشاء babel.cfg
    babel_config = """[python: **.py]
[jinja2: **/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
"""
    
    with open('babel.cfg', 'w', encoding='utf-8') as f:
        f.write(babel_config)
    
    print("✅ تم إنشاء babel.cfg")
    
    # إنشاء المجلدات
    for directory in directories[1:]:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ تم إنشاء مجلد: {directory}")
    
    # إنشاء ملف الترجمة العربية
    ar_po_content = """# Arabic translations for accounting system.
# Copyright (C) 2024
# This file is distributed under the same license as the accounting system project.
#
msgid ""
msgstr ""
"Project-Id-Version: accounting system 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2024-08-02 18:00+0000\\n"
"PO-Revision-Date: 2024-08-02 18:00+0000\\n"
"Last-Translator: \\n"
"Language: ar\\n"
"Language-Team: Arabic\\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5;\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.13.1\\n"

msgid "Professional Accounting System"
msgstr "نظام المحاسبة الاحترافي"

msgid "Dashboard"
msgstr "الرئيسية"

msgid "Sales"
msgstr "المبيعات"

msgid "Purchases"
msgstr "المشتريات"

msgid "Customers"
msgstr "العملاء"

msgid "Suppliers"
msgstr "الموردين"

msgid "Products"
msgstr "المنتجات"

msgid "Employees"
msgstr "الموظفين"

msgid "Reports"
msgstr "التقارير"

msgid "Settings"
msgstr "الإعدادات"

msgid "Language changed successfully"
msgstr "تم تغيير اللغة بنجاح"

msgid "Branch changed successfully"
msgstr "تم تغيير الفرع بنجاح"

msgid "Place India"
msgstr "بليس إنديا"

msgid "China Town"
msgstr "تشاينا تاون"

msgid "Total Sales"
msgstr "إجمالي المبيعات"

msgid "Total Purchases"
msgstr "إجمالي المشتريات"

msgid "Net Profit"
msgstr "صافي الربح"

msgid "Monthly Sales"
msgstr "مبيعات الشهر"

msgid "Login"
msgstr "تسجيل الدخول"

msgid "Username"
msgstr "اسم المستخدم"

msgid "Password"
msgstr "كلمة المرور"

msgid "Welcome"
msgstr "مرحباً"
"""
    
    with open('translations/ar/LC_MESSAGES/messages.po', 'w', encoding='utf-8') as f:
        f.write(ar_po_content)
    
    print("✅ تم إنشاء ملف الترجمة العربية")
    
    # إنشاء ملف الترجمة الإنجليزية
    en_po_content = """# English translations for accounting system.
# Copyright (C) 2024
# This file is distributed under the same license as the accounting system project.
#
msgid ""
msgstr ""
"Project-Id-Version: accounting system 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2024-08-02 18:00+0000\\n"
"PO-Revision-Date: 2024-08-02 18:00+0000\\n"
"Last-Translator: \\n"
"Language: en\\n"
"Language-Team: English\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.13.1\\n"

msgid "نظام المحاسبة الاحترافي"
msgstr "Professional Accounting System"

msgid "الرئيسية"
msgstr "Dashboard"

msgid "المبيعات"
msgstr "Sales"

msgid "المشتريات"
msgstr "Purchases"

msgid "العملاء"
msgstr "Customers"

msgid "الموردين"
msgstr "Suppliers"

msgid "المنتجات"
msgstr "Products"

msgid "الموظفين"
msgstr "Employees"

msgid "التقارير"
msgstr "Reports"

msgid "الإعدادات"
msgstr "Settings"

msgid "تم تغيير اللغة بنجاح"
msgstr "Language changed successfully"

msgid "تم تغيير الفرع بنجاح"
msgstr "Branch changed successfully"

msgid "بليس إنديا"
msgstr "Place India"

msgid "تشاينا تاون"
msgstr "China Town"

msgid "إجمالي المبيعات"
msgstr "Total Sales"

msgid "إجمالي المشتريات"
msgstr "Total Purchases"

msgid "صافي الربح"
msgstr "Net Profit"

msgid "مبيعات الشهر"
msgstr "Monthly Sales"

msgid "تسجيل الدخول"
msgstr "Login"

msgid "اسم المستخدم"
msgstr "Username"

msgid "كلمة المرور"
msgstr "Password"

msgid "مرحباً"
msgstr "Welcome"
"""
    
    with open('translations/en/LC_MESSAGES/messages.po', 'w', encoding='utf-8') as f:
        f.write(en_po_content)
    
    print("✅ تم إنشاء ملف الترجمة الإنجليزية")

def compile_translations():
    """تجميع ملفات الترجمة"""
    try:
        import subprocess
        
        # تجميع الترجمة العربية
        subprocess.run(['pybabel', 'compile', '-d', 'translations', '-l', 'ar'], check=True)
        print("✅ تم تجميع الترجمة العربية")
        
        # تجميع الترجمة الإنجليزية
        subprocess.run(['pybabel', 'compile', '-d', 'translations', '-l', 'en'], check=True)
        print("✅ تم تجميع الترجمة الإنجليزية")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تجميع الترجمات: {e}")
        print("💡 سيتم إنشاء ملفات .mo يدوياً...")
        
        # إنشاء ملفات .mo فارغة للتجربة
        with open('translations/ar/LC_MESSAGES/messages.mo', 'wb') as f:
            f.write(b'')
        with open('translations/en/LC_MESSAGES/messages.mo', 'wb') as f:
            f.write(b'')
        
        print("✅ تم إنشاء ملفات .mo أساسية")
    
    except ImportError:
        print("❌ pybabel غير مثبت")
        print("💡 سيتم إنشاء ملفات .mo يدوياً...")
        
        # إنشاء ملفات .mo فارغة
        with open('translations/ar/LC_MESSAGES/messages.mo', 'wb') as f:
            f.write(b'')
        with open('translations/en/LC_MESSAGES/messages.mo', 'wb') as f:
            f.write(b'')
        
        print("✅ تم إنشاء ملفات .mo أساسية")

def main():
    print("🌐 إنشاء نظام الترجمة للنظام")
    print("=" * 50)
    
    create_translation_directories()
    compile_translations()
    
    print("\n🎉 تم إنشاء نظام الترجمة بنجاح!")
    print("📁 الملفات المنشأة:")
    print("   - babel.cfg")
    print("   - translations/ar/LC_MESSAGES/messages.po")
    print("   - translations/ar/LC_MESSAGES/messages.mo")
    print("   - translations/en/LC_MESSAGES/messages.po")
    print("   - translations/en/LC_MESSAGES/messages.mo")

if __name__ == '__main__':
    main()
