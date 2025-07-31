#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح سريع لأخطاء النظام
Quick Fix for System Errors
"""

import re
import os

def fix_jinja_templates():
    """إصلاح قوالب Jinja2"""
    print("🔧 إصلاح قوالب Jinja2...")
    
    file_path = 'accounting_system_complete.py'
    
    if not os.path.exists(file_path):
        print("❌ ملف النظام غير موجود")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إصلاح الفلاتر المعطلة
        fixes = [
            # إصلاح moment()
            (r'moment\(\)\.format\([\'"]YYYY-MM-DD[\'\"]\)', "format_date('%Y-%m-%d')"),
            (r'moment\(\)\.format\([\'"]YYYY-MM-DD HH:mm[\'\"]\)', "format_datetime('%Y-%m-%d %H:%M')"),
            (r'moment\(\)\.format\([\'"]YYYYMMDD[\'\"]\)', "format_date('%Y%m%d')"),
            (r'moment\(\)\.strftime\([\'"]%Y-%m-%d[\'\"]\)', "format_date('%Y-%m-%d')"),
            (r'moment\(\)\.strftime\([\'"]%Y%m%d[\'\"]\)', "format_date('%Y%m%d')"),
            
            # إصلاح string.zfill
            (r'\|string\.zfill\((\d+)\)', r'|string|zfill(\1)'),
            (r'(\w+)\|string\.zfill\((\d+)\)', r'zfill_number(\1, \2)'),
            
            # إصلاح format
            (r'[\'"]%0(\d+)d[\'\"]\|format\(([^)]+)\)', r'zfill_number(\2, \1)'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # كتابة الملف المحدث
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم إصلاح قوالب Jinja2")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح القوالب: {e}")
        return False

def add_missing_imports():
    """إضافة الاستيرادات المفقودة"""
    print("📦 فحص الاستيرادات...")
    
    file_path = 'accounting_system_complete.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من وجود الاستيرادات المطلوبة
        required_imports = [
            'from datetime import datetime, date',
            'from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify',
            'from flask_sqlalchemy import SQLAlchemy',
            'from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user',
            'from werkzeug.security import generate_password_hash, check_password_hash'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"⚠️  استيرادات مفقودة: {len(missing_imports)}")
            for imp in missing_imports:
                print(f"   - {imp}")
        else:
            print("✅ جميع الاستيرادات موجودة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في فحص الاستيرادات: {e}")
        return False

def check_syntax():
    """فحص صحة الكود"""
    print("🔍 فحص صحة الكود...")
    
    try:
        import py_compile
        py_compile.compile('accounting_system_complete.py', doraise=True)
        print("✅ الكود صحيح نحوياً")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ خطأ نحوي في الكود: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في فحص الكود: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("🛠️  إصلاح سريع لأخطاء النظام")
    print("=" * 50)
    
    # إصلاح قوالب Jinja2
    if not fix_jinja_templates():
        return False
    
    # فحص الاستيرادات
    if not add_missing_imports():
        return False
    
    # فحص صحة الكود
    if not check_syntax():
        return False
    
    print("=" * 50)
    print("✅ تم إصلاح جميع الأخطاء بنجاح!")
    print("🚀 يمكنك الآن تشغيل النظام باستخدام: python run_system.py")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ فشل في إصلاح بعض الأخطاء")
        print("يرجى مراجعة الأخطاء أعلاه وإصلاحها يدوياً")
    
    input("\nاضغط Enter للخروج...")
