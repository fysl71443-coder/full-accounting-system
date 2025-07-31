#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة دخول نظام المحاسبة الاحترافي - محسن لـ Render
Entry point for Professional Accounting System - Render Optimized
"""

import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔄 جاري تحميل النظام...")

    # استيراد النظام الكامل
    from accounting_system_complete import app, init_db

    print("✅ تم استيراد النظام بنجاح")

    # تهيئة قاعدة البيانات عند الاستيراد
    try:
        with app.app_context():
            init_db()
        print("✅ تم تهيئة قاعدة البيانات بنجاح")
    except Exception as db_error:
        print(f"⚠️ تحذير في قاعدة البيانات: {db_error}")
        # المتابعة حتى لو كان هناك خطأ في قاعدة البيانات

    print("🎉 تم تحميل النظام الكامل بنجاح")

except Exception as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    print(f"❌ نوع الخطأ: {type(e).__name__}")
    print("🔄 جاري تحميل النسخة المبسطة...")

    try:
        # تحميل النسخة المبسطة كبديل
        from accounting_system_simple import app, init_db

        # تهيئة قاعدة البيانات للنسخة المبسطة
        with app.app_context():
            init_db()

        print("✅ تم تحميل النسخة المبسطة بنجاح")

    except Exception as simple_error:
        print(f"❌ فشل في تحميل النسخة المبسطة: {simple_error}")

        # إنشاء تطبيق أساسي جداً
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def hello():
            return f'''
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>خطأ في النظام</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: red; }}
                    .details {{ background: #f5f5f5; padding: 20px; margin: 20px; border-radius: 10px; }}
                </style>
            </head>
            <body>
                <h1 class="error">خطأ في تحميل النظام</h1>
                <div class="details">
                    <h3>تفاصيل الخطأ الرئيسي:</h3>
                    <p><strong>الخطأ:</strong> {e}</p>
                    <p><strong>النوع:</strong> {type(e).__name__}</p>
                    <hr>
                    <h3>تفاصيل خطأ النسخة المبسطة:</h3>
                    <p><strong>الخطأ:</strong> {simple_error}</p>
                    <p><strong>النوع:</strong> {type(simple_error).__name__}</p>
                </div>
                <p>يرجى التحقق من السجلات لمعرفة السبب</p>
                <hr>
                <p><strong>Error loading system. Please check logs.</strong></p>
            </body>
            </html>
            '''

# للنشر على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
