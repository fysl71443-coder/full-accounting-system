#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي الكامل
Professional Complete Accounting System
"""

import os
import sys
from accounting_system_complete import app, db

def create_database():
    """إنشاء قاعدة البيانات والجداول"""
    try:
        with app.app_context():
            db.create_all()

            # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
            from accounting_system_complete import User
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    full_name='مدير النظام',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ تم إنشاء المستخدم الافتراضي: admin / admin123")

            print("✅ تم إنشاء قاعدة البيانات بنجاح")
            return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

def check_requirements():
    """فحص المتطلبات المطلوبة"""
    required_packages = [
        'flask',
        'flask-sqlalchemy', 
        'flask-login',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ المكتبات التالية مفقودة:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 لتثبيت المكتبات المطلوبة، قم بتنفيذ:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ جميع المكتبات المطلوبة متوفرة")
    return True

def run_system():
    """تشغيل النظام"""
    print("🚀 بدء تشغيل نظام المحاسبة الاحترافي...")
    print("=" * 50)
    
    # فحص المتطلبات
    if not check_requirements():
        return False
    
    # إنشاء قاعدة البيانات
    if not create_database():
        return False
    
    # تشغيل النظام
    try:
        print("🌐 النظام يعمل على: http://localhost:5000")
        print("👤 المستخدم الافتراضي: admin")
        print("🔑 كلمة المرور الافتراضية: admin123")
        print("=" * 50)
        print("📱 اضغط Ctrl+C لإيقاف النظام")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف النظام بواسطة المستخدم")
        return True
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        return False

if __name__ == '__main__':
    success = run_system()
    sys.exit(0 if success else 1)
