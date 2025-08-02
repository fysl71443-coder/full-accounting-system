#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشخيص وإصلاح أخطاء الخادم
"""

import traceback
import sys

def test_imports():
    """اختبار استيراد المكتبات"""
    print("🔍 اختبار استيراد المكتبات...")
    
    try:
        from flask import Flask
        print("✅ Flask")
    except Exception as e:
        print(f"❌ Flask: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✅ Flask-SQLAlchemy")
    except Exception as e:
        print(f"❌ Flask-SQLAlchemy: {e}")
        return False
    
    try:
        from flask_login import LoginManager
        print("✅ Flask-Login")
    except Exception as e:
        print(f"❌ Flask-Login: {e}")
        return False
    
    try:
        from flask_babel import Babel
        print("✅ Flask-Babel")
    except Exception as e:
        print(f"❌ Flask-Babel: {e}")
        return False
    
    return True

def test_basic_app():
    """اختبار تطبيق Flask أساسي"""
    print("\n🧪 اختبار تطبيق Flask أساسي...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        
        @app.route('/')
        def test():
            return "Test OK"
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ تطبيق Flask الأساسي يعمل")
                return True
            else:
                print(f"❌ تطبيق Flask: status {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ تطبيق Flask: {e}")
        traceback.print_exc()
        return False

def test_main_app():
    """اختبار التطبيق الرئيسي"""
    print("\n🔍 اختبار التطبيق الرئيسي...")
    
    try:
        # محاولة استيراد التطبيق الرئيسي
        sys.path.insert(0, '.')
        from accounting_system_complete import app
        print("✅ تم استيراد التطبيق الرئيسي")
        
        # اختبار الصفحة الرئيسية
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ الصفحة الرئيسية: status {response.status_code}")
            
            # اختبار صفحة تسجيل الدخول
            response = client.get('/login')
            print(f"✅ صفحة تسجيل الدخول: status {response.status_code}")
            
            return True
    
    except Exception as e:
        print(f"❌ التطبيق الرئيسي: {e}")
        traceback.print_exc()
        return False

def test_database():
    """اختبار قاعدة البيانات"""
    print("\n💾 اختبار قاعدة البيانات...")
    
    try:
        from accounting_system_complete import app, db
        
        with app.app_context():
            # محاولة إنشاء الجداول
            db.create_all()
            print("✅ تم إنشاء الجداول")
            
            # فحص الجداول
            tables = db.engine.table_names()
            print(f"✅ عدد الجداول: {len(tables)}")
            
            return True
    
    except Exception as e:
        print(f"❌ قاعدة البيانات: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚨 تشخيص أخطاء الخادم")
    print("=" * 50)
    
    # اختبار المكتبات
    if not test_imports():
        print("\n❌ فشل في استيراد المكتبات")
        return
    
    # اختبار Flask الأساسي
    if not test_basic_app():
        print("\n❌ فشل في تطبيق Flask الأساسي")
        return
    
    # اختبار التطبيق الرئيسي
    if not test_main_app():
        print("\n❌ فشل في التطبيق الرئيسي")
        return
    
    # اختبار قاعدة البيانات
    if not test_database():
        print("\n❌ فشل في قاعدة البيانات")
        return
    
    print("\n🎉 جميع الاختبارات نجحت!")
    print("💡 المشكلة قد تكون في:")
    print("   1. إعدادات الخادم")
    print("   2. متغيرات البيئة")
    print("   3. صلاحيات الملفات")
    print("   4. منافذ الشبكة")

if __name__ == '__main__':
    main()
