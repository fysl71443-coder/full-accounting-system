#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WSGI entry point for the accounting system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from accounting_system_complete import app, init_db, SOCKETIO_AVAILABLE, socketio

    # Initialize database
    print("🚀 بدء تهيئة النظام للإنتاج...")
    with app.app_context():
        init_db()
    print("✅ تم تهيئة النظام بنجاح")

    # WSGI application with SocketIO support
    if SOCKETIO_AVAILABLE and socketio:
        print("🔄 استخدام SocketIO للتحديث الفوري")
        application = socketio
    else:
        print("📡 استخدام Flask العادي")
        application = app

    print("🌐 النظام جاهز للعمل في الإنتاج")

    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 5000))
        if SOCKETIO_AVAILABLE and socketio:
            socketio.run(app, host='0.0.0.0', port=port, debug=False)
        else:
            app.run(host='0.0.0.0', port=port, debug=False)

except Exception as e:
    print(f"❌ خطأ في تهيئة النظام: {e}")

    # إنشاء تطبيق بديل في حالة الخطأ
    from flask import Flask
    application = Flask(__name__)

    @application.route('/')
    def error_page():
        return f"""
        <h1>خطأ في النظام</h1>
        <p>حدث خطأ أثناء تهيئة النظام: {e}</p>
        <p>يرجى التحقق من إعدادات قاعدة البيانات</p>
        """
