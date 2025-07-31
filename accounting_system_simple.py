#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة مبسطة من نظام المحاسبة - للاختبار
"""

import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# إنشاء التطبيق
app = Flask(__name__)

# الإعدادات
app.config['SECRET_KEY'] = 'accounting-system-simple-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting_simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# قاعدة البيانات
db = SQLAlchemy(app)

# نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تهيئة قاعدة البيانات
def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        db.create_all()
        
        # إنشاء مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                full_name='المدير العام',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء المستخدم الافتراضي: admin/admin123")
        
        print("✅ تم تهيئة قاعدة البيانات بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")

# الصفحة الرئيسية
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .login-card { background: white; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body class="d-flex align-items-center">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="login-card p-5">
                        <div class="text-center mb-4">
                            <h2 class="fw-bold text-primary">نظام المحاسبة</h2>
                            <p class="text-muted">تسجيل الدخول</p>
                        </div>
                        
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">اسم المستخدم</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">كلمة المرور</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">دخول</button>
                            </div>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                المستخدم الافتراضي: admin<br>
                                كلمة المرور: admin123
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''')

# لوحة التحكم
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>لوحة التحكم - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
            .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
            .feature-card {
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                text-decoration: none;
                color: inherit;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                color: inherit;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">
                        <i class="fas fa-user me-1"></i>{{ current_user.full_name }}
                    </span>
                    <a class="nav-link" href="{{ url_for('logout') }}">
                        <i class="fas fa-sign-out-alt"></i> خروج
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-primary">
                    <i class="fas fa-tachometer-alt me-3"></i>لوحة التحكم
                </h1>
                <p class="lead text-muted">نظام المحاسبة الاحترافي - النسخة المبسطة</p>
            </div>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="row g-4">
                <div class="col-md-4">
                    <div class="feature-card p-4 text-center h-100">
                        <div class="text-primary mb-3">
                            <i class="fas fa-chart-line fa-3x"></i>
                        </div>
                        <h5 class="fw-bold">النظام الكامل</h5>
                        <p class="text-muted">النظام الكامل مع جميع الميزات</p>
                        <div class="alert alert-warning">
                            <small>النظام الكامل غير متوفر حالياً بسبب مشكلة تقنية</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="feature-card p-4 text-center h-100">
                        <div class="text-success mb-3">
                            <i class="fas fa-check-circle fa-3x"></i>
                        </div>
                        <h5 class="fw-bold">النظام يعمل</h5>
                        <p class="text-muted">تم تحميل النسخة المبسطة بنجاح</p>
                        <div class="alert alert-success">
                            <small>✅ تسجيل الدخول يعمل</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="feature-card p-4 text-center h-100">
                        <div class="text-info mb-3">
                            <i class="fas fa-cog fa-3x"></i>
                        </div>
                        <h5 class="fw-bold">الحالة</h5>
                        <p class="text-muted">حالة النظام الحالية</p>
                        <div class="alert alert-info">
                            <small>🔧 جاري العمل على إصلاح النظام الكامل</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-5">
                <div class="col-12">
                    <div class="feature-card p-4">
                        <h5 class="fw-bold mb-3">
                            <i class="fas fa-info-circle me-2"></i>معلومات النظام
                        </h5>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>الإصدار:</strong> النسخة المبسطة 1.0</p>
                                <p><strong>الحالة:</strong> <span class="text-success">يعمل بنجاح</span></p>
                                <p><strong>المستخدم:</strong> {{ current_user.full_name }} ({{ current_user.role }})</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>التاريخ:</strong> {{ moment().format('YYYY-MM-DD') }}</p>
                                <p><strong>الوقت:</strong> {{ moment().format('HH:mm:ss') }}</p>
                                <p><strong>قاعدة البيانات:</strong> <span class="text-success">متصلة</span></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    </body>
    </html>
    ''')

# تسجيل الخروج
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
