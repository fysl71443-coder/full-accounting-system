#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح مشاكل النشر والتشغيل
"""

import os
import sys
import re

def check_duplicate_routes():
    """البحث عن routes مكررة"""
    print("🔍 البحث عن routes مكررة...")
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع الـ routes
    route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"]'
    routes = re.findall(route_pattern, content)
    
    # البحث عن المكررات
    route_counts = {}
    for route in routes:
        route_counts[route] = route_counts.get(route, 0) + 1
    
    duplicates = {route: count for route, count in route_counts.items() if count > 1}
    
    if duplicates:
        print("❌ تم العثور على routes مكررة:")
        for route, count in duplicates.items():
            print(f"   - {route}: {count} مرات")
        return False
    else:
        print("✅ لا توجد routes مكررة")
        return True

def check_duplicate_functions():
    """البحث عن وظائف مكررة"""
    print("🔍 البحث عن وظائف مكررة...")
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع الوظائف
    function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    functions = re.findall(function_pattern, content)
    
    # البحث عن المكررات
    function_counts = {}
    for func in functions:
        function_counts[func] = function_counts.get(func, 0) + 1
    
    duplicates = {func: count for func, count in function_counts.items() if count > 1}
    
    if duplicates:
        print("❌ تم العثور على وظائف مكررة:")
        for func, count in duplicates.items():
            print(f"   - {func}: {count} مرات")
        return False
    else:
        print("✅ لا توجد وظائف مكررة")
        return True

def check_syntax():
    """فحص صحة الكود"""
    print("🔍 فحص صحة الكود...")
    
    try:
        with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # محاولة تجميع الكود
        compile(code, 'accounting_system_complete.py', 'exec')
        print("✅ الكود صحيح نحوياً")
        return True
        
    except SyntaxError as e:
        print(f"❌ خطأ نحوي في السطر {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ خطأ في الكود: {e}")
        return False

def check_imports():
    """فحص الاستيرادات"""
    print("🔍 فحص الاستيرادات...")
    
    try:
        # محاولة استيراد المكتبات المطلوبة
        required_modules = [
            'flask', 'flask_sqlalchemy', 'werkzeug', 
            'datetime', 'os', 'sqlite3'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module} غير موجود")
                return False
        
        print("✅ جميع الاستيرادات متوفرة")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في فحص الاستيرادات: {e}")
        return False

def create_wsgi_file():
    """إنشاء ملف WSGI للنشر"""
    print("📝 إنشاء ملف WSGI...")
    
    wsgi_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WSGI entry point for the accounting system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from accounting_system_complete import app, init_db
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # WSGI application
    application = app
    
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        
except Exception as e:
    print(f"Error starting application: {e}")
    raise
'''
    
    with open('wsgi.py', 'w', encoding='utf-8') as f:
        f.write(wsgi_content)
    
    print("✅ تم إنشاء ملف wsgi.py")

def create_requirements():
    """إنشاء ملف requirements.txt"""
    print("📝 تحديث ملف requirements.txt...")
    
    requirements = '''Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
gunicorn==21.2.0
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("✅ تم تحديث ملف requirements.txt")

def main():
    """الوظيفة الرئيسية"""
    print("🔧 إصلاح مشاكل النشر والتشغيل")
    print("=" * 50)
    
    all_good = True
    
    # فحص الكود
    if not check_syntax():
        all_good = False
    
    # فحص الـ routes المكررة
    if not check_duplicate_routes():
        all_good = False
    
    # فحص الوظائف المكررة
    if not check_duplicate_functions():
        all_good = False
    
    # فحص الاستيرادات
    if not check_imports():
        all_good = False
    
    # إنشاء ملفات النشر
    create_wsgi_file()
    create_requirements()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 جميع الفحوصات نجحت!")
        print("✅ النظام جاهز للنشر")
        print("💡 يمكنك الآن رفع التحديثات:")
        print("   git add .")
        print("   git commit -m 'Fix deployment issues'")
        print("   git push origin main")
    else:
        print("❌ توجد مشاكل تحتاج إصلاح!")
        print("💡 يرجى مراجعة الأخطاء أعلاه")
    
    print("=" * 50)
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
