#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point for Render Deployment
نقطة دخول WSGI للنشر على Render
"""

import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # استيراد النظام الكامل
    from accounting_system_complete import app, init_db
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        init_db()
    
    print("✅ تم تحميل النظام الكامل بنجاح")
    
except Exception as e:
    print(f"❌ خطأ في تحميل النظام: {e}")
    
    # إنشاء تطبيق بسيط في حالة الخطأ
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return f'''
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>خطأ في النظام</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: red; }}
                .info {{ color: blue; }}
            </style>
        </head>
        <body>
            <h1 class="error">خطأ في تحميل النظام</h1>
            <p class="info">Error: {e}</p>
            <p>يرجى التحقق من السجلات لمعرفة السبب</p>
            <p>Please check logs for more details</p>
        </body>
        </html>
        '''

# للنشر على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
