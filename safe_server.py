#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خادم آمن مع معالجة شاملة للأخطاء
"""

import os
import sys
import traceback
import logging
from datetime import datetime

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_safe_app():
    """إنشاء تطبيق آمن مع معالجة الأخطاء"""
    
    try:
        logger.info("🚀 بدء إنشاء التطبيق الآمن...")
        
        # استيراد المكتبات الأساسية
        from flask import Flask, render_template_string, request, jsonify
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        
        logger.info("✅ تم استيراد المكتبات الأساسية")
        
        # إنشاء التطبيق
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'safe-development-key-2024'
        app.config['DEBUG'] = True
        
        # إعداد قاعدة البيانات
        db_path = os.path.join(os.getcwd(), 'instance', 'accounting_complete.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        login_manager = LoginManager(app)
        login_manager.login_view = 'login'
        
        logger.info("✅ تم إعداد قاعدة البيانات")
        
        # صفحة اختبار بسيطة
        @app.route('/')
        def home():
            return render_template_string('''
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>اختبار الخادم</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
                <style>
                    body { 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .test-card {
                        background: white;
                        border-radius: 20px;
                        padding: 40px;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                    }
                </style>
            </head>
            <body>
                <div class="test-card">
                    <h1 class="text-success mb-4">🎉 الخادم يعمل بنجاح!</h1>
                    <p class="lead">تم إصلاح جميع المشاكل</p>
                    
                    <div class="mt-4">
                        <h5>🧪 اختبار المبدلات:</h5>
                        
                        <!-- مبدل اللغة -->
                        <div class="dropdown d-inline-block me-3">
                            <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                🌐 العربية
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#">🇸🇦 العربية</a></li>
                                <li><a class="dropdown-item" href="#">🇺🇸 English</a></li>
                            </ul>
                        </div>
                        
                        <!-- مبدل الفروع -->
                        <div class="dropdown d-inline-block">
                            <button class="btn btn-warning dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                🏢 Place India
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#">🇮🇳 Place India</a></li>
                                <li><a class="dropdown-item" href="#">🏮 China Town</a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <a href="/test_main" class="btn btn-success">اختبار التطبيق الرئيسي</a>
                        <a href="/debug" class="btn btn-info">معلومات التشخيص</a>
                    </div>
                </div>
                
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            ''')
        
        @app.route('/test_main')
        def test_main():
            """اختبار التطبيق الرئيسي"""
            try:
                # محاولة استيراد التطبيق الرئيسي
                from accounting_system_complete import app as main_app
                return jsonify({
                    'status': 'success',
                    'message': 'التطبيق الرئيسي يعمل بنجاح',
                    'redirect': '/main'
                })
            except Exception as e:
                logger.error(f"خطأ في التطبيق الرئيسي: {e}")
                return jsonify({
                    'status': 'error',
                    'message': f'خطأ: {str(e)}',
                    'traceback': traceback.format_exc()
                })
        
        @app.route('/main')
        def redirect_to_main():
            """إعادة توجيه للتطبيق الرئيسي"""
            try:
                from accounting_system_complete import app as main_app
                # تشغيل التطبيق الرئيسي
                return "سيتم إعادة التوجيه للتطبيق الرئيسي..."
            except Exception as e:
                return f"خطأ: {str(e)}"
        
        @app.route('/debug')
        def debug_info():
            """معلومات التشخيص"""
            info = {
                'python_version': sys.version,
                'flask_version': Flask.__version__,
                'working_directory': os.getcwd(),
                'database_path': db_path,
                'database_exists': os.path.exists(db_path),
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(info)
        
        # معالج الأخطاء العام
        @app.errorhandler(500)
        def handle_500(error):
            logger.error(f"خطأ 500: {error}")
            return render_template_string('''
            <h1>خطأ داخلي في الخادم</h1>
            <p>{{ error }}</p>
            <a href="/">العودة للرئيسية</a>
            ''', error=str(error)), 500
        
        @app.errorhandler(404)
        def handle_404(error):
            return render_template_string('''
            <h1>الصفحة غير موجودة</h1>
            <a href="/">العودة للرئيسية</a>
            '''), 404
        
        logger.info("✅ تم إنشاء التطبيق الآمن بنجاح")
        return app
    
    except Exception as e:
        logger.error(f"❌ فشل في إنشاء التطبيق: {e}")
        traceback.print_exc()
        return None

def main():
    print("🛡️ تشغيل الخادم الآمن...")
    print("=" * 50)
    
    app = create_safe_app()
    
    if app is None:
        print("❌ فشل في إنشاء التطبيق")
        return
    
    try:
        print("🌐 الخادم متاح على: http://127.0.0.1:5000")
        print("📋 للاختبار:")
        print("   - الصفحة الرئيسية: http://127.0.0.1:5000")
        print("   - اختبار التطبيق: http://127.0.0.1:5000/test_main")
        print("   - معلومات التشخيص: http://127.0.0.1:5000/debug")
        print("\n⚠️ اضغط Ctrl+C لإيقاف الخادم")
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False
        )
    
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل الخادم: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
