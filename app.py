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
    # استيراد النظام الكامل
    from accounting_system_complete import app, init_db

    # تهيئة قاعدة البيانات عند الاستيراد
    with app.app_context():
        init_db()

    print("✅ تم تحميل النظام الكامل بنجاح")

except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    # إنشاء تطبيق بسيط في حالة فشل الاستيراد
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return '''
        <h1 style="text-align: center; color: red;">خطأ في تحميل النظام</h1>
        <p style="text-align: center;">يرجى التحقق من السجلات لمعرفة السبب</p>
        <p style="text-align: center;">Error loading system. Please check logs.</p>
        '''

# للنشر على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
