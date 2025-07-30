#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي الكامل - متوافق مع Python 3.11
Complete Professional Accounting System - Python 3.11 Compatible
"""

import os
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# إنشاء التطبيق
app = Flask(__name__)

# الإعدادات
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'accounting-system-complete-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///accounting_complete.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# قاعدة البيانات
db = SQLAlchemy(app)

# نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== نماذج قاعدة البيانات =====

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    tax_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=10)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='sales_invoices')

class PurchaseInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='purchase_invoices')

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(20), default='cash')
    receipt_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # 'received' or 'paid'
    payment_method = db.Column(db.String(20), default='cash')
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='payments')
    supplier = db.relationship('Supplier', backref='payments')

# ===== الصفحات الأساسية =====

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام المحاسبة الاحترافي الكامل</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .hero-section {
                padding: 100px 0;
                color: white;
                text-align: center;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .btn-custom {
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                color: white;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="hero-section">
            <div class="container">
                <h1 class="display-3 mb-4">
                    <i class="fas fa-calculator me-3"></i>
                    نظام المحاسبة الاحترافي الكامل
                </h1>
                <p class="lead mb-5">حل شامل ومتكامل لإدارة جميع العمليات المحاسبية والمالية</p>
                <a href="{{ url_for('login') }}" class="btn btn-custom btn-lg">
                    <i class="fas fa-sign-in-alt me-2"></i>دخول النظام
                </a>
            </div>
        </div>

        <div class="container mb-5">
            <div class="row">
                <div class="col-md-4">
                    <div class="feature-card text-center">
                        <i class="fas fa-users fa-3x text-primary mb-3"></i>
                        <h4>إدارة العملاء والموردين</h4>
                        <p>نظام شامل لإدارة بيانات العملاء والموردين مع إمكانية التتبع والتقارير</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card text-center">
                        <i class="fas fa-file-invoice fa-3x text-success mb-3"></i>
                        <h4>الفواتير والمبيعات</h4>
                        <p>إنشاء وإدارة فواتير المبيعات والمشتريات مع حساب الضرائب تلقائياً</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card text-center">
                        <i class="fas fa-chart-line fa-3x text-warning mb-3"></i>
                        <h4>التقارير المالية</h4>
                        <p>تقارير مالية شاملة ومفصلة مع رسوم بيانية تفاعلية</p>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تسجيل الدخول - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
            }
            .login-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="login-card">
                        <div class="text-center mb-4">
                            <i class="fas fa-calculator fa-3x text-primary mb-3"></i>
                            <h3>تسجيل الدخول</h3>
                            <p class="text-muted">نظام المحاسبة الاحترافي</p>
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
                                <label for="username" class="form-label">اسم المستخدم</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-user"></i></span>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                            </div>
                            <div class="mb-4">
                                <label for="password" class="form-label">كلمة المرور</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 py-2">
                                <i class="fas fa-sign-in-alt me-2"></i>دخول
                            </button>
                        </form>

                        <div class="text-center mt-4">
                            <small class="text-muted">
                                المستخدم الافتراضي: <strong>admin</strong><br>
                                كلمة المرور: <strong>admin123</strong>
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # إحصائيات النظام
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    total_products = Product.query.count()
    total_employees = Employee.query.count()

    # إحصائيات مالية
    total_sales = db.session.query(db.func.sum(SalesInvoice.total)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses

    # المنتجات منخفضة المخزون
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_quantity).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .stat-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                transition: transform 0.3s ease;
            }
            .stat-card:hover { transform: translateY(-5px); }
            .stat-icon {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
            }
            .function-card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                text-decoration: none;
                color: inherit;
            }
            .function-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
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
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-tachometer-alt me-2"></i>لوحة التحكم</h2>
                    <p class="text-muted">نظرة عامة على النظام والإحصائيات</p>
                </div>
            </div>

            <!-- إحصائيات سريعة -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-primary mx-auto mb-3">
                            <i class="fas fa-users"></i>
                        </div>
                        <h3 class="mb-1">{{ total_customers }}</h3>
                        <p class="text-muted mb-0">العملاء</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-success mx-auto mb-3">
                            <i class="fas fa-truck"></i>
                        </div>
                        <h3 class="mb-1">{{ total_suppliers }}</h3>
                        <p class="text-muted mb-0">الموردين</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-warning mx-auto mb-3">
                            <i class="fas fa-box"></i>
                        </div>
                        <h3 class="mb-1">{{ total_products }}</h3>
                        <p class="text-muted mb-0">المنتجات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-info mx-auto mb-3">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <h3 class="mb-1">{{ total_employees }}</h3>
                        <p class="text-muted mb-0">الموظفين</p>
                    </div>
                </div>
            </div>

            <!-- إحصائيات مالية -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-success mx-auto mb-3">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <h4 class="mb-1">{{ "%.2f"|format(total_sales) }} ر.س</h4>
                        <p class="text-muted mb-0">إجمالي المبيعات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-danger mx-auto mb-3">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <h4 class="mb-1">{{ "%.2f"|format(total_purchases) }} ر.س</h4>
                        <p class="text-muted mb-0">إجمالي المشتريات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon bg-warning mx-auto mb-3">
                            <i class="fas fa-receipt"></i>
                        </div>
                        <h4 class="mb-1">{{ "%.2f"|format(total_expenses) }} ر.س</h4>
                        <p class="text-muted mb-0">إجمالي المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <div class="stat-icon {{ 'bg-success' if net_profit >= 0 else 'bg-danger' }} mx-auto mb-3">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <h4 class="mb-1">{{ "%.2f"|format(net_profit) }} ر.س</h4>
                        <p class="text-muted mb-0">صافي الربح</p>
                    </div>
                </div>
            </div>

            <!-- الوظائف الرئيسية -->
            <div class="row">
                <div class="col-12 mb-3">
                    <h4><i class="fas fa-cogs me-2"></i>الوظائف الرئيسية</h4>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('customers') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-users fa-2x text-primary mb-3"></i>
                            <h5>إدارة العملاء</h5>
                            <p class="text-muted">إضافة وإدارة بيانات العملاء</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('suppliers') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-truck fa-2x text-success mb-3"></i>
                            <h5>إدارة الموردين</h5>
                            <p class="text-muted">إضافة وإدارة بيانات الموردين</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('products') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-box fa-2x text-warning mb-3"></i>
                            <h5>إدارة المنتجات</h5>
                            <p class="text-muted">إدارة المخزون والمنتجات</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('sales') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-file-invoice fa-2x text-info mb-3"></i>
                            <h5>فواتير المبيعات</h5>
                            <p class="text-muted">إنشاء وإدارة فواتير المبيعات</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('purchases') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-shopping-cart fa-2x text-secondary mb-3"></i>
                            <h5>فواتير المشتريات</h5>
                            <p class="text-muted">إنشاء وإدارة فواتير المشتريات</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('expenses') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-receipt fa-2x text-danger mb-3"></i>
                            <h5>إدارة المصروفات</h5>
                            <p class="text-muted">تسجيل وإدارة المصروفات</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('employees') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-user-tie fa-2x text-primary mb-3"></i>
                            <h5>إدارة الموظفين</h5>
                            <p class="text-muted">إدارة بيانات الموظفين والرواتب</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('reports') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-chart-bar fa-2x text-success mb-3"></i>
                            <h5>التقارير المالية</h5>
                            <p class="text-muted">تقارير شاملة ومفصلة</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('api_status') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-code fa-2x text-info mb-3"></i>
                            <h5>واجهة API</h5>
                            <p class="text-muted">واجهة برمجية للتكامل</p>
                        </div>
                    </a>
                </div>

                <div class="col-md-4">
                    <a href="{{ url_for('settings') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-cogs fa-2x text-secondary mb-3"></i>
                            <h5>إعدادات النظام</h5>
                            <p class="text-muted">إدارة وتخصيص النظام</p>
                        </div>
                    </a>
                </div>

                {% if current_user.role == 'admin' %}
                <div class="col-md-4">
                    <a href="{{ url_for('users') }}" class="function-card d-block">
                        <div class="text-center">
                            <i class="fas fa-users-cog fa-2x text-danger mb-3"></i>
                            <h5>إدارة المستخدمين</h5>
                            <p class="text-muted">إدارة المستخدمين والصلاحيات</p>
                        </div>
                    </a>
                </div>
                {% endif %}
            </div>

            <!-- تنبيهات المخزون -->
            {% if low_stock_products %}
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert alert-warning">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>تنبيه: منتجات منخفضة المخزون</h5>
                        <ul class="mb-0">
                            {% for product in low_stock_products %}
                            <li>{{ product.name }} - الكمية المتاحة: {{ product.quantity }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''',
    total_customers=total_customers, total_suppliers=total_suppliers,
    total_products=total_products, total_employees=total_employees,
    total_sales=total_sales, total_purchases=total_purchases,
    total_expenses=total_expenses, net_profit=net_profit,
    low_stock_products=low_stock_products)

# ===== إدارة العملاء =====

@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة العملاء - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-users me-2"></i>إدارة العملاء</h5>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCustomerModal">
                        <i class="fas fa-plus me-2"></i>إضافة عميل جديد
                    </button>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>الاسم</th>
                                    <th>الهاتف</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>العنوان</th>
                                    <th>تاريخ الإضافة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for customer in customers %}
                                <tr>
                                    <td>{{ customer.name }}</td>
                                    <td>{{ customer.phone or '-' }}</td>
                                    <td>{{ customer.email or '-' }}</td>
                                    <td>{{ customer.address or '-' }}</td>
                                    <td>{{ customer.created_at.strftime('%Y-%m-%d') if customer.created_at else '-' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal إضافة عميل -->
        <div class="modal fade" id="addCustomerModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة عميل جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_customer') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="name" class="form-label">اسم العميل *</label>
                                <input type="text" class="form-control" id="name" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="phone" class="form-label">رقم الهاتف</label>
                                <input type="text" class="form-control" id="phone" name="phone">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" id="email" name="email">
                            </div>
                            <div class="mb-3">
                                <label for="address" class="form-label">العنوان</label>
                                <textarea class="form-control" id="address" name="address" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="submit" class="btn btn-primary">حفظ</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', customers=customers)

@app.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    customer = Customer(
        name=request.form['name'],
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        address=request.form.get('address')
    )
    db.session.add(customer)
    db.session.commit()
    flash('تم إضافة العميل بنجاح', 'success')
    return redirect(url_for('customers'))

# ===== باقي الوظائف (مبسطة) =====

@app.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الموردين - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .table-hover tbody tr:hover { background-color: #f8f9fa; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="card shadow">
                <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-truck me-2"></i>إدارة الموردين</h5>
                    <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addSupplierModal">
                        <i class="fas fa-plus me-2"></i>إضافة مورد جديد
                    </button>
                </div>
                <div class="card-body">
                    {% if suppliers %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>#</th>
                                    <th>اسم المورد</th>
                                    <th>الهاتف</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>العنوان</th>
                                    <th>الرقم الضريبي</th>
                                    <th>تاريخ الإضافة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for supplier in suppliers %}
                                <tr>
                                    <td>{{ loop.index }}</td>
                                    <td><strong>{{ supplier.name }}</strong></td>
                                    <td>{{ supplier.phone or '-' }}</td>
                                    <td>{{ supplier.email or '-' }}</td>
                                    <td>{{ supplier.address or '-' }}</td>
                                    <td>{{ supplier.tax_number or '-' }}</td>
                                    <td>{{ supplier.created_at.strftime('%Y-%m-%d') if supplier.created_at else '-' }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-truck fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا توجد موردين مسجلين</h5>
                        <p class="text-muted">ابدأ بإضافة مورد جديد</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة مورد -->
        <div class="modal fade" id="addSupplierModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>إضافة مورد جديد</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_supplier') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="name" class="form-label">اسم المورد *</label>
                                        <input type="text" class="form-control" id="name" name="name" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="phone" class="form-label">رقم الهاتف</label>
                                        <input type="text" class="form-control" id="phone" name="phone">
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="email" class="form-label">البريد الإلكتروني</label>
                                        <input type="email" class="form-control" id="email" name="email">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="tax_number" class="form-label">الرقم الضريبي</label>
                                        <input type="text" class="form-control" id="tax_number" name="tax_number">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="address" class="form-label">العنوان</label>
                                <textarea class="form-control" id="address" name="address" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save me-2"></i>حفظ المورد
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', suppliers=suppliers)

@app.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    supplier = Supplier(
        name=request.form['name'],
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        address=request.form.get('address'),
        tax_number=request.form.get('tax_number')
    )
    db.session.add(supplier)
    db.session.commit()
    flash('تم إضافة المورد بنجاح', 'success')
    return redirect(url_for('suppliers'))

@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    low_stock_count = Product.query.filter(Product.quantity <= Product.min_quantity).count()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المنتجات والمخزون - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .low-stock { background-color: #fff3cd !important; }
            .out-of-stock { background-color: #f8d7da !important; }
            .stock-badge {
                font-size: 0.8em;
                padding: 0.25em 0.5em;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- إحصائيات سريعة -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-box fa-2x mb-2"></i>
                            <h4>{{ products|length }}</h4>
                            <p class="mb-0">إجمالي المنتجات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                            <h4>{{ low_stock_count }}</h4>
                            <p class="mb-0">منتجات منخفضة المخزون</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-dollar-sign fa-2x mb-2"></i>
                            <h4>{{ "%.0f"|format(products|sum(attribute='price')|default(0)) }}</h4>
                            <p class="mb-0">إجمالي قيمة الأسعار</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-warehouse fa-2x mb-2"></i>
                            <h4>{{ products|sum(attribute='quantity')|default(0) }}</h4>
                            <p class="mb-0">إجمالي الكمية</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow">
                <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-box me-2"></i>إدارة المنتجات والمخزون</h5>
                    <button type="button" class="btn btn-dark" data-bs-toggle="modal" data-bs-target="#addProductModal">
                        <i class="fas fa-plus me-2"></i>إضافة منتج جديد
                    </button>
                </div>
                <div class="card-body">
                    {% if products %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>#</th>
                                    <th>اسم المنتج</th>
                                    <th>الفئة</th>
                                    <th>سعر البيع</th>
                                    <th>سعر التكلفة</th>
                                    <th>الكمية المتاحة</th>
                                    <th>الحد الأدنى</th>
                                    <th>حالة المخزون</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for product in products %}
                                <tr class="{% if product.quantity == 0 %}out-of-stock{% elif product.quantity <= product.min_quantity %}low-stock{% endif %}">
                                    <td>{{ loop.index }}</td>
                                    <td>
                                        <strong>{{ product.name }}</strong>
                                        {% if product.description %}
                                        <br><small class="text-muted">{{ product.description[:50] }}...</small>
                                        {% endif %}
                                    </td>
                                    <td>{{ product.category or '-' }}</td>
                                    <td><strong>{{ "%.2f"|format(product.price) }} ر.س</strong></td>
                                    <td>{{ "%.2f"|format(product.cost or 0) }} ر.س</td>
                                    <td><span class="badge bg-primary">{{ product.quantity }}</span></td>
                                    <td>{{ product.min_quantity }}</td>
                                    <td>
                                        {% if product.quantity == 0 %}
                                        <span class="badge bg-danger stock-badge">نفد المخزون</span>
                                        {% elif product.quantity <= product.min_quantity %}
                                        <span class="badge bg-warning stock-badge">مخزون منخفض</span>
                                        {% else %}
                                        <span class="badge bg-success stock-badge">متوفر</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" title="تعديل">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-success" title="إضافة كمية">
                                            <i class="fas fa-plus"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" title="حذف">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-box fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا توجد منتجات مسجلة</h5>
                        <p class="text-muted">ابدأ بإضافة منتج جديد لإدارة المخزون</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة منتج -->
        <div class="modal fade" id="addProductModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>إضافة منتج جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_product') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="name" class="form-label">اسم المنتج *</label>
                                        <input type="text" class="form-control" id="name" name="name" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="category" class="form-label">الفئة</label>
                                        <input type="text" class="form-control" id="category" name="category">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="description" class="form-label">وصف المنتج</label>
                                <textarea class="form-control" id="description" name="description" rows="2"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="price" class="form-label">سعر البيع *</label>
                                        <input type="number" step="0.01" class="form-control" id="price" name="price" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="cost" class="form-label">سعر التكلفة</label>
                                        <input type="number" step="0.01" class="form-control" id="cost" name="cost">
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="quantity" class="form-label">الكمية الأولية</label>
                                        <input type="number" class="form-control" id="quantity" name="quantity" value="0">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="min_quantity" class="form-label">الحد الأدنى للمخزون</label>
                                        <input type="number" class="form-control" id="min_quantity" name="min_quantity" value="10">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-save me-2"></i>حفظ المنتج
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', products=products, low_stock_count=low_stock_count)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    product = Product(
        name=request.form['name'],
        description=request.form.get('description'),
        category=request.form.get('category'),
        price=float(request.form['price']),
        cost=float(request.form.get('cost', 0)),
        quantity=int(request.form.get('quantity', 0)),
        min_quantity=int(request.form.get('min_quantity', 10))
    )
    db.session.add(product)
    db.session.commit()
    flash('تم إضافة المنتج بنجاح', 'success')
    return redirect(url_for('products'))

@app.route('/sales')
@login_required
def sales():
    sales = SalesInvoice.query.order_by(SalesInvoice.created_at.desc()).all()
    customers = Customer.query.all()
    total_sales = sum(sale.total for sale in sales)

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>فواتير المبيعات - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .status-pending { color: #ffc107; }
            .status-paid { color: #198754; }
            .status-cancelled { color: #dc3545; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- إحصائيات المبيعات -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-file-invoice fa-2x mb-2"></i>
                            <h4>{{ sales|length }}</h4>
                            <p class="mb-0">إجمالي الفواتير</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-dollar-sign fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_sales) }} ر.س</h4>
                            <p class="mb-0">إجمالي المبيعات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-2x mb-2"></i>
                            <h4>{{ customers|length }}</h4>
                            <p class="mb-0">العملاء المسجلين</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-file-invoice me-2"></i>فواتير المبيعات</h5>
                    <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addSaleModal">
                        <i class="fas fa-plus me-2"></i>فاتورة جديدة
                    </button>
                </div>
                <div class="card-body">
                    {% if sales %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>رقم الفاتورة</th>
                                    <th>العميل</th>
                                    <th>التاريخ</th>
                                    <th>المبلغ الفرعي</th>
                                    <th>الضريبة</th>
                                    <th>الإجمالي</th>
                                    <th>الحالة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for sale in sales %}
                                <tr>
                                    <td><strong>{{ sale.invoice_number }}</strong></td>
                                    <td>{{ sale.customer.name if sale.customer else 'عميل نقدي' }}</td>
                                    <td>{{ sale.date.strftime('%Y-%m-%d') }}</td>
                                    <td>{{ "%.2f"|format(sale.subtotal) }} ر.س</td>
                                    <td>{{ "%.2f"|format(sale.tax_amount) }} ر.س</td>
                                    <td><strong>{{ "%.2f"|format(sale.total) }} ر.س</strong></td>
                                    <td>
                                        <span class="badge
                                        {% if sale.status == 'paid' %}bg-success
                                        {% elif sale.status == 'pending' %}bg-warning
                                        {% else %}bg-danger{% endif %}">
                                        {% if sale.status == 'paid' %}مدفوعة
                                        {% elif sale.status == 'pending' %}معلقة
                                        {% else %}ملغية{% endif %}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" title="عرض">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-success" title="طباعة">
                                            <i class="fas fa-print"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-file-invoice fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا توجد فواتير مبيعات</h5>
                        <p class="text-muted">ابدأ بإنشاء فاتورة جديدة</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة فاتورة -->
        <div class="modal fade" id="addSaleModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-info text-white">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>فاتورة مبيعات جديدة</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_sale') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="invoice_number" class="form-label">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" id="invoice_number" name="invoice_number"
                                               value="INV-{{ moment().format('YYYYMMDD') }}-{{ (sales|length + 1)|string.zfill(3) }}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="customer_id" class="form-label">العميل</label>
                                        <select class="form-select" id="customer_id" name="customer_id">
                                            <option value="">عميل نقدي</option>
                                            {% for customer in customers %}
                                            <option value="{{ customer.id }}">{{ customer.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="subtotal" class="form-label">المبلغ الفرعي *</label>
                                        <input type="number" step="0.01" class="form-control" id="subtotal" name="subtotal" required>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="tax_amount" class="form-label">الضريبة (15%)</label>
                                        <input type="number" step="0.01" class="form-control" id="tax_amount" name="tax_amount" readonly>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="total" class="form-label">الإجمالي</label>
                                        <input type="number" step="0.01" class="form-control" id="total" name="total" readonly>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="notes" class="form-label">ملاحظات</label>
                                <textarea class="form-control" id="notes" name="notes" rows="2"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-info">
                                <i class="fas fa-save me-2"></i>حفظ الفاتورة
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // حساب الضريبة والإجمالي تلقائياً
            document.getElementById('subtotal').addEventListener('input', function() {
                const subtotal = parseFloat(this.value) || 0;
                const taxAmount = subtotal * 0.15;
                const total = subtotal + taxAmount;

                document.getElementById('tax_amount').value = taxAmount.toFixed(2);
                document.getElementById('total').value = total.toFixed(2);
            });
        </script>
    </body>
    </html>
    ''', sales=sales, customers=customers, total_sales=total_sales)

@app.route('/add_sale', methods=['POST'])
@login_required
def add_sale():
    sale = SalesInvoice(
        invoice_number=request.form['invoice_number'],
        customer_id=request.form.get('customer_id') if request.form.get('customer_id') else None,
        subtotal=float(request.form['subtotal']),
        tax_amount=float(request.form.get('tax_amount', 0)),
        total=float(request.form.get('total', 0)),
        notes=request.form.get('notes'),
        status='pending'
    )
    db.session.add(sale)
    db.session.commit()
    flash('تم إنشاء فاتورة المبيعات بنجاح', 'success')
    return redirect(url_for('sales'))

@app.route('/purchases')
@login_required
def purchases():
    purchases = PurchaseInvoice.query.order_by(PurchaseInvoice.created_at.desc()).all()
    suppliers = Supplier.query.all()
    total_purchases = sum(purchase.total for purchase in purchases)

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>فواتير المشتريات - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .purchase-card { border-left: 4px solid #6f42c1; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- إحصائيات المشتريات -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-secondary text-white purchase-card">
                        <div class="card-body text-center">
                            <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                            <h4>{{ purchases|length }}</h4>
                            <p class="mb-0">إجمالي فواتير المشتريات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-danger text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-money-bill-wave fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_purchases) }} ر.س</h4>
                            <p class="mb-0">إجمالي قيمة المشتريات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-dark text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-truck fa-2x mb-2"></i>
                            <h4>{{ suppliers|length }}</h4>
                            <p class="mb-0">الموردين المسجلين</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow">
                <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-shopping-cart me-2"></i>فواتير المشتريات</h5>
                    <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addPurchaseModal">
                        <i class="fas fa-plus me-2"></i>فاتورة مشتريات جديدة
                    </button>
                </div>
                <div class="card-body">
                    {% if purchases %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>رقم الفاتورة</th>
                                    <th>المورد</th>
                                    <th>التاريخ</th>
                                    <th>المبلغ الفرعي</th>
                                    <th>الضريبة</th>
                                    <th>الإجمالي</th>
                                    <th>الحالة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for purchase in purchases %}
                                <tr>
                                    <td><strong>{{ purchase.invoice_number }}</strong></td>
                                    <td>{{ purchase.supplier.name if purchase.supplier else 'مورد غير محدد' }}</td>
                                    <td>{{ purchase.date.strftime('%Y-%m-%d') }}</td>
                                    <td>{{ "%.2f"|format(purchase.subtotal) }} ر.س</td>
                                    <td>{{ "%.2f"|format(purchase.tax_amount) }} ر.س</td>
                                    <td><strong>{{ "%.2f"|format(purchase.total) }} ر.س</strong></td>
                                    <td>
                                        <span class="badge
                                        {% if purchase.status == 'paid' %}bg-success
                                        {% elif purchase.status == 'pending' %}bg-warning
                                        {% else %}bg-danger{% endif %}">
                                        {% if purchase.status == 'paid' %}مدفوعة
                                        {% elif purchase.status == 'pending' %}معلقة
                                        {% else %}ملغية{% endif %}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" title="عرض">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-success" title="طباعة">
                                            <i class="fas fa-print"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-warning" title="تعديل">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا توجد فواتير مشتريات</h5>
                        <p class="text-muted">ابدأ بإنشاء فاتورة مشتريات جديدة</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة فاتورة مشتريات -->
        <div class="modal fade" id="addPurchaseModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-secondary text-white">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>فاتورة مشتريات جديدة</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_purchase') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="invoice_number" class="form-label">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" id="invoice_number" name="invoice_number"
                                               value="PUR-{{ moment().format('YYYYMMDD') }}-{{ (purchases|length + 1)|string.zfill(3) }}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="supplier_id" class="form-label">المورد *</label>
                                        <select class="form-select" id="supplier_id" name="supplier_id" required>
                                            <option value="">اختر المورد</option>
                                            {% for supplier in suppliers %}
                                            <option value="{{ supplier.id }}">{{ supplier.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="subtotal" class="form-label">المبلغ الفرعي *</label>
                                        <input type="number" step="0.01" class="form-control" id="subtotal" name="subtotal" required>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="tax_amount" class="form-label">الضريبة (15%)</label>
                                        <input type="number" step="0.01" class="form-control" id="tax_amount" name="tax_amount" readonly>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="total" class="form-label">الإجمالي</label>
                                        <input type="number" step="0.01" class="form-control" id="total" name="total" readonly>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="notes" class="form-label">ملاحظات</label>
                                <textarea class="form-control" id="notes" name="notes" rows="2" placeholder="أي ملاحظات إضافية..."></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-light" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-secondary">
                                <i class="fas fa-save me-2"></i>حفظ فاتورة المشتريات
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // حساب الضريبة والإجمالي تلقائياً
            document.getElementById('subtotal').addEventListener('input', function() {
                const subtotal = parseFloat(this.value) || 0;
                const taxAmount = subtotal * 0.15;
                const total = subtotal + taxAmount;

                document.getElementById('tax_amount').value = taxAmount.toFixed(2);
                document.getElementById('total').value = total.toFixed(2);
            });
        </script>
    </body>
    </html>
    ''', purchases=purchases, suppliers=suppliers, total_purchases=total_purchases)

@app.route('/add_purchase', methods=['POST'])
@login_required
def add_purchase():
    purchase = PurchaseInvoice(
        invoice_number=request.form['invoice_number'],
        supplier_id=int(request.form['supplier_id']),
        subtotal=float(request.form['subtotal']),
        tax_amount=float(request.form.get('tax_amount', 0)),
        total=float(request.form.get('total', 0)),
        notes=request.form.get('notes'),
        status='pending'
    )
    db.session.add(purchase)
    db.session.commit()
    flash('تم إنشاء فاتورة المشتريات بنجاح', 'success')
    return redirect(url_for('purchases'))

@app.route('/expenses')
@login_required
def expenses():
    expenses = Expense.query.order_by(Expense.created_at.desc()).all()
    total_expenses = sum(expense.amount for expense in expenses)

    # تجميع المصروفات حسب الفئة
    from sqlalchemy import func
    expense_categories = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).group_by(Expense.category).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المصروفات - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .expense-card { border-left: 4px solid #dc3545; }
            .category-badge {
                font-size: 0.8em;
                padding: 0.25em 0.5em;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- إحصائيات المصروفات -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-danger text-white expense-card">
                        <div class="card-body text-center">
                            <i class="fas fa-receipt fa-2x mb-2"></i>
                            <h4>{{ expenses|length }}</h4>
                            <p class="mb-0">إجمالي المصروفات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-dark">
                        <div class="card-body text-center">
                            <i class="fas fa-money-bill-wave fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_expenses) }} ر.س</h4>
                            <p class="mb-0">إجمالي القيمة</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-tags fa-2x mb-2"></i>
                            <h4>{{ expense_categories|length }}</h4>
                            <p class="mb-0">فئات المصروفات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-calendar-day fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_expenses / (expenses|length) if expenses|length > 0 else 0) }}</h4>
                            <p class="mb-0">متوسط المصروف</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تحليل الفئات -->
            {% if expense_categories %}
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h6 class="mb-0"><i class="fas fa-chart-pie me-2"></i>تحليل المصروفات حسب الفئة</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        {% for category in expense_categories %}
                        <div class="col-md-4 mb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="badge bg-secondary category-badge">{{ category.category }}</span>
                                <span><strong>{{ "%.2f"|format(category.total) }} ر.س</strong> ({{ category.count }} مصروف)</span>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endif %}

            <div class="card shadow">
                <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-receipt me-2"></i>إدارة المصروفات</h5>
                    <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addExpenseModal">
                        <i class="fas fa-plus me-2"></i>إضافة مصروف جديد
                    </button>
                </div>
                <div class="card-body">
                    {% if expenses %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>التاريخ</th>
                                    <th>الوصف</th>
                                    <th>الفئة</th>
                                    <th>المبلغ</th>
                                    <th>طريقة الدفع</th>
                                    <th>رقم الإيصال</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for expense in expenses %}
                                <tr>
                                    <td>{{ expense.date.strftime('%Y-%m-%d') }}</td>
                                    <td>
                                        <strong>{{ expense.description }}</strong>
                                        {% if expense.notes %}
                                        <br><small class="text-muted">{{ expense.notes[:50] }}...</small>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <span class="badge bg-secondary category-badge">{{ expense.category }}</span>
                                    </td>
                                    <td><strong class="text-danger">{{ "%.2f"|format(expense.amount) }} ر.س</strong></td>
                                    <td>
                                        {% if expense.payment_method == 'cash' %}
                                        <i class="fas fa-money-bill text-success"></i> نقدي
                                        {% elif expense.payment_method == 'card' %}
                                        <i class="fas fa-credit-card text-primary"></i> بطاقة
                                        {% elif expense.payment_method == 'bank' %}
                                        <i class="fas fa-university text-info"></i> بنكي
                                        {% else %}
                                        <i class="fas fa-question text-muted"></i> أخرى
                                        {% endif %}
                                    </td>
                                    <td>{{ expense.receipt_number or '-' }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" title="عرض">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-warning" title="تعديل">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" title="حذف">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-receipt fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا توجد مصروفات مسجلة</h5>
                        <p class="text-muted">ابدأ بإضافة مصروف جديد</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة مصروف -->
        <div class="modal fade" id="addExpenseModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>إضافة مصروف جديد</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_expense') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="mb-3">
                                        <label for="description" class="form-label">وصف المصروف *</label>
                                        <input type="text" class="form-control" id="description" name="description" required>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="amount" class="form-label">المبلغ *</label>
                                        <input type="number" step="0.01" class="form-control" id="amount" name="amount" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="category" class="form-label">الفئة *</label>
                                        <select class="form-select" id="category" name="category" required>
                                            <option value="">اختر الفئة</option>
                                            <option value="مكتب">مصروفات مكتبية</option>
                                            <option value="سفر">سفر وانتقالات</option>
                                            <option value="اتصالات">اتصالات وإنترنت</option>
                                            <option value="كهرباء">كهرباء ومياه</option>
                                            <option value="إيجار">إيجار</option>
                                            <option value="صيانة">صيانة وإصلاح</option>
                                            <option value="تسويق">تسويق وإعلان</option>
                                            <option value="أخرى">أخرى</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="payment_method" class="form-label">طريقة الدفع</label>
                                        <select class="form-select" id="payment_method" name="payment_method">
                                            <option value="cash">نقدي</option>
                                            <option value="card">بطاقة ائتمان</option>
                                            <option value="bank">تحويل بنكي</option>
                                            <option value="check">شيك</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="receipt_number" class="form-label">رقم الإيصال</label>
                                        <input type="text" class="form-control" id="receipt_number" name="receipt_number">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="date" class="form-label">التاريخ</label>
                                        <input type="date" class="form-control" id="date" name="date" value="{{ moment().format('YYYY-MM-DD') }}">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="notes" class="form-label">ملاحظات</label>
                                <textarea class="form-control" id="notes" name="notes" rows="2"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-danger">
                                <i class="fas fa-save me-2"></i>حفظ المصروف
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', expenses=expenses, total_expenses=total_expenses, expense_categories=expense_categories)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    from datetime import datetime
    expense_date = datetime.strptime(request.form.get('date', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

    expense = Expense(
        description=request.form['description'],
        amount=float(request.form['amount']),
        category=request.form['category'],
        payment_method=request.form.get('payment_method', 'cash'),
        receipt_number=request.form.get('receipt_number'),
        date=expense_date,
        notes=request.form.get('notes')
    )
    db.session.add(expense)
    db.session.commit()
    flash('تم إضافة المصروف بنجاح', 'success')
    return redirect(url_for('expenses'))

@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    active_employees = Employee.query.filter_by(status='active').count()
    total_salaries = sum(emp.salary for emp in employees if emp.status == 'active')

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الموظفين والرواتب - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .employee-card { border-left: 4px solid #198754; }
            .status-active { color: #198754; }
            .status-inactive { color: #dc3545; }
            .salary-highlight { background-color: #e8f5e8; font-weight: bold; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- إحصائيات الموظفين -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white employee-card">
                        <div class="card-body text-center">
                            <i class="fas fa-user-tie fa-2x mb-2"></i>
                            <h4>{{ employees|length }}</h4>
                            <p class="mb-0">إجمالي الموظفين</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-user-check fa-2x mb-2"></i>
                            <h4>{{ active_employees }}</h4>
                            <p class="mb-0">الموظفين النشطين</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-dark">
                        <div class="card-body text-center">
                            <i class="fas fa-money-check-alt fa-2x mb-2"></i>
                            <h4>{{ "%.0f"|format(total_salaries) }} ر.س</h4>
                            <p class="mb-0">إجمالي الرواتب الشهرية</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-calculator fa-2x mb-2"></i>
                            <h4>{{ "%.0f"|format(total_salaries / active_employees if active_employees > 0 else 0) }}</h4>
                            <p class="mb-0">متوسط الراتب</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card shadow">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-user-tie me-2"></i>إدارة الموظفين والرواتب</h5>
                    <div>
                        <button type="button" class="btn btn-light me-2" data-bs-toggle="modal" data-bs-target="#payrollModal">
                            <i class="fas fa-money-check-alt me-2"></i>كشف الرواتب
                        </button>
                        <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addEmployeeModal">
                            <i class="fas fa-plus me-2"></i>إضافة موظف جديد
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    {% if employees %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>الاسم</th>
                                    <th>المنصب</th>
                                    <th>الراتب الشهري</th>
                                    <th>الهاتف</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>تاريخ التوظيف</th>
                                    <th>الحالة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for employee in employees %}
                                <tr>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="avatar-circle bg-primary text-white me-2" style="width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                                {{ employee.name[0].upper() }}
                                            </div>
                                            <strong>{{ employee.name }}</strong>
                                        </div>
                                    </td>
                                    <td>{{ employee.position }}</td>
                                    <td class="salary-highlight">{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                    <td>{{ employee.phone or '-' }}</td>
                                    <td>{{ employee.email or '-' }}</td>
                                    <td>{{ employee.hire_date.strftime('%Y-%m-%d') }}</td>
                                    <td>
                                        {% if employee.status == 'active' %}
                                        <span class="badge bg-success">نشط</span>
                                        {% else %}
                                        <span class="badge bg-danger">غير نشط</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-info" title="عرض الملف">
                                            <i class="fas fa-user"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-success" title="كشف راتب">
                                            <i class="fas fa-money-check"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-warning" title="تعديل">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" title="حذف">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="fas fa-user-tie fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">لا يوجد موظفين مسجلين</h5>
                        <p class="text-muted">ابدأ بإضافة موظف جديد</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة موظف -->
        <div class="modal fade" id="addEmployeeModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title"><i class="fas fa-plus me-2"></i>إضافة موظف جديد</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_employee') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="name" class="form-label">اسم الموظف *</label>
                                        <input type="text" class="form-control" id="name" name="name" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="position" class="form-label">المنصب *</label>
                                        <input type="text" class="form-control" id="position" name="position" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="salary" class="form-label">الراتب الشهري *</label>
                                        <input type="number" step="0.01" class="form-control" id="salary" name="salary" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="hire_date" class="form-label">تاريخ التوظيف *</label>
                                        <input type="date" class="form-control" id="hire_date" name="hire_date" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="phone" class="form-label">رقم الهاتف</label>
                                        <input type="text" class="form-control" id="phone" name="phone">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="email" class="form-label">البريد الإلكتروني</label>
                                        <input type="email" class="form-control" id="email" name="email">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>حفظ الموظف
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Modal كشف الرواتب -->
        <div class="modal fade" id="payrollModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title"><i class="fas fa-money-check-alt me-2"></i>كشف الرواتب الشهري</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead class="table-success">
                                    <tr>
                                        <th>الموظف</th>
                                        <th>المنصب</th>
                                        <th>الراتب الأساسي</th>
                                        <th>البدلات</th>
                                        <th>الخصومات</th>
                                        <th>صافي الراتب</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for employee in employees %}
                                    {% if employee.status == 'active' %}
                                    <tr>
                                        <td><strong>{{ employee.name }}</strong></td>
                                        <td>{{ employee.position }}</td>
                                        <td>{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                        <td>0.00 ر.س</td>
                                        <td>0.00 ر.س</td>
                                        <td class="salary-highlight">{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                    </tr>
                                    {% endif %}
                                    {% endfor %}
                                </tbody>
                                <tfoot class="table-dark">
                                    <tr>
                                        <th colspan="5">الإجمالي</th>
                                        <th>{{ "%.2f"|format(total_salaries) }} ر.س</th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-success">
                            <i class="fas fa-print me-2"></i>طباعة كشف الرواتب
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', employees=employees, active_employees=active_employees, total_salaries=total_salaries)

@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    from datetime import datetime
    hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()

    employee = Employee(
        name=request.form['name'],
        position=request.form['position'],
        salary=float(request.form['salary']),
        hire_date=hire_date,
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        status='active'
    )
    db.session.add(employee)
    db.session.commit()
    flash('تم إضافة الموظف بنجاح', 'success')
    return redirect(url_for('employees'))

@app.route('/reports')
@login_required
def reports():
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta

    # إحصائيات عامة
    total_sales = db.session.query(func.sum(SalesInvoice.total)).scalar() or 0
    total_purchases = db.session.query(func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses

    # إحصائيات شهرية للمبيعات
    current_year = datetime.now().year
    monthly_sales = db.session.query(
        extract('month', SalesInvoice.date).label('month'),
        func.sum(SalesInvoice.total).label('total')
    ).filter(extract('year', SalesInvoice.date) == current_year).group_by(extract('month', SalesInvoice.date)).all()

    # إحصائيات شهرية للمشتريات
    monthly_purchases = db.session.query(
        extract('month', PurchaseInvoice.date).label('month'),
        func.sum(PurchaseInvoice.total).label('total')
    ).filter(extract('year', PurchaseInvoice.date) == current_year).group_by(extract('month', PurchaseInvoice.date)).all()

    # إحصائيات المصروفات حسب الفئة
    expense_by_category = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).group_by(Expense.category).all()

    # أفضل العملاء (حسب إجمالي المبيعات)
    top_customers = db.session.query(
        Customer.name,
        func.sum(SalesInvoice.total).label('total_sales')
    ).join(SalesInvoice).group_by(Customer.id, Customer.name).order_by(func.sum(SalesInvoice.total).desc()).limit(5).all()

    # أفضل الموردين (حسب إجمالي المشتريات)
    top_suppliers = db.session.query(
        Supplier.name,
        func.sum(PurchaseInvoice.total).label('total_purchases')
    ).join(PurchaseInvoice).group_by(Supplier.id, Supplier.name).order_by(func.sum(PurchaseInvoice.total).desc()).limit(5).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>التقارير المالية المتقدمة - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .report-card {
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .report-card:hover { transform: translateY(-5px); }
            .profit-positive { color: #198754; }
            .profit-negative { color: #dc3545; }
            .chart-container {
                position: relative;
                height: 400px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-chart-bar me-2"></i>التقارير المالية المتقدمة</h2>
                    <p class="text-muted">تحليل شامل للأداء المالي والإحصائيات</p>
                </div>
            </div>

            <!-- الملخص المالي -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card report-card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-arrow-up fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_sales) }} ر.س</h4>
                            <p class="mb-0">إجمالي المبيعات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card report-card bg-danger text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-arrow-down fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_purchases) }} ر.س</h4>
                            <p class="mb-0">إجمالي المشتريات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card report-card bg-warning text-dark">
                        <div class="card-body text-center">
                            <i class="fas fa-receipt fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_expenses) }} ر.س</h4>
                            <p class="mb-0">إجمالي المصروفات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card report-card {{ 'bg-success' if net_profit >= 0 else 'bg-danger' }} text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-line fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(net_profit) }} ر.س</h4>
                            <p class="mb-0">صافي الربح</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- الرسوم البيانية -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card report-card">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>المبيعات والمشتريات الشهرية</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="salesPurchasesChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card report-card">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0"><i class="fas fa-chart-pie me-2"></i>توزيع المصروفات حسب الفئة</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="expensesChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- أفضل العملاء والموردين -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card report-card">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-users me-2"></i>أفضل العملاء</h6>
                        </div>
                        <div class="card-body">
                            {% if top_customers %}
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>العميل</th>
                                            <th>إجمالي المبيعات</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for customer in top_customers %}
                                        <tr>
                                            <td>{{ customer.name }}</td>
                                            <td><strong>{{ "%.2f"|format(customer.total_sales) }} ر.س</strong></td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            {% else %}
                            <p class="text-muted text-center">لا توجد بيانات عملاء</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card report-card">
                        <div class="card-header bg-secondary text-white">
                            <h6 class="mb-0"><i class="fas fa-truck me-2"></i>أفضل الموردين</h6>
                        </div>
                        <div class="card-body">
                            {% if top_suppliers %}
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>المورد</th>
                                            <th>إجمالي المشتريات</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for supplier in top_suppliers %}
                                        <tr>
                                            <td>{{ supplier.name }}</td>
                                            <td><strong>{{ "%.2f"|format(supplier.total_purchases) }} ر.س</strong></td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            {% else %}
                            <p class="text-muted text-center">لا توجد بيانات موردين</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>

            <!-- أزرار التقارير -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card report-card">
                        <div class="card-header bg-dark text-white">
                            <h6 class="mb-0"><i class="fas fa-file-export me-2"></i>تصدير التقارير</h6>
                        </div>
                        <div class="card-body text-center">
                            <button class="btn btn-success me-2" onclick="window.print()">
                                <i class="fas fa-print me-2"></i>طباعة التقرير
                            </button>
                            <button class="btn btn-primary me-2" onclick="exportToPDF()">
                                <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                            </button>
                            <button class="btn btn-info" onclick="exportToExcel()">
                                <i class="fas fa-file-excel me-2"></i>تصدير Excel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
        <script src="/static/js/accounting-system.js"></script>
        <script>
            // رسم بياني للمبيعات والمشتريات
            const salesPurchasesCtx = document.getElementById('salesPurchasesChart').getContext('2d');
            new Chart(salesPurchasesCtx, {
                type: 'line',
                data: {
                    labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
                    datasets: [{
                        label: 'المبيعات',
                        data: [
                            {% for i in range(1, 13) %}
                            {{ monthly_sales|selectattr('month', 'equalto', i)|map(attribute='total')|first or 0 }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        borderColor: 'rgb(25, 135, 84)',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'المشتريات',
                        data: [
                            {% for i in range(1, 13) %}
                            {{ monthly_purchases|selectattr('month', 'equalto', i)|map(attribute='total')|first or 0 }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        borderColor: 'rgb(220, 53, 69)',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'المبيعات والمشتريات الشهرية ({{ current_year }})'
                        }
                    }
                }
            });

            // رسم بياني للمصروفات
            const expensesCtx = document.getElementById('expensesChart').getContext('2d');
            new Chart(expensesCtx, {
                type: 'doughnut',
                data: {
                    labels: [
                        {% for category in expense_by_category %}
                        '{{ category.category }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        data: [
                            {% for category in expense_by_category %}
                            {{ category.total }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'توزيع المصروفات حسب الفئة'
                        }
                    }
                }
            });

            // وظائف التصدير
            function printReport() {
                window.print();
            }

            function exportPDF() {
                alert('سيتم تطوير تصدير PDF قريباً');
            }

            function exportExcel() {
                alert('سيتم تطوير تصدير Excel قريباً');
            }
        </script>
    </body>
    </html>
    ''',
    total_sales=total_sales, total_purchases=total_purchases, total_expenses=total_expenses,
    net_profit=net_profit, monthly_sales=monthly_sales, monthly_purchases=monthly_purchases,
    expense_by_category=expense_by_category, top_customers=top_customers, top_suppliers=top_suppliers,
    current_year=current_year)

@app.route('/api/status')
def api_status():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>واجهة API - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .api-card {
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .endpoint-card {
                border-left: 4px solid #0d6efd;
                margin-bottom: 15px;
            }
            .method-get { border-left-color: #198754; }
            .method-post { border-left-color: #fd7e14; }
            .method-put { border-left-color: #0dcaf0; }
            .method-delete { border-left-color: #dc3545; }
            .code-block {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-code me-2"></i>واجهة API - نظام المحاسبة</h2>
                    <p class="text-muted">واجهة برمجية شاملة للتكامل مع النظام</p>
                </div>
            </div>

            <!-- حالة النظام -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card api-card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-check-circle fa-2x mb-2"></i>
                            <h5>نشط</h5>
                            <p class="mb-0">حالة النظام</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card api-card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-code-branch fa-2x mb-2"></i>
                            <h5>v2.0.0</h5>
                            <p class="mb-0">إصدار API</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card api-card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-database fa-2x mb-2"></i>
                            <h5>متصلة</h5>
                            <p class="mb-0">قاعدة البيانات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card api-card bg-warning text-dark">
                        <div class="card-body text-center">
                            <i class="fas fa-cloud fa-2x mb-2"></i>
                            <h5>Render</h5>
                            <p class="mb-0">منصة النشر</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- نقاط النهاية المتاحة -->
            <div class="card api-card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-list me-2"></i>نقاط النهاية المتاحة (API Endpoints)</h5>
                </div>
                <div class="card-body">

                    <!-- العملاء -->
                    <div class="card endpoint-card method-get">
                        <div class="card-body">
                            <h6><span class="badge bg-success">GET</span> /api/customers</h6>
                            <p class="text-muted">الحصول على قائمة جميع العملاء</p>
                            <div class="code-block">
                                <code>curl -X GET {{ request.url_root }}api/customers</code>
                            </div>
                        </div>
                    </div>

                    <div class="card endpoint-card method-post">
                        <div class="card-body">
                            <h6><span class="badge bg-warning">POST</span> /api/customers</h6>
                            <p class="text-muted">إضافة عميل جديد</p>
                            <div class="code-block">
                                <code>curl -X POST {{ request.url_root }}api/customers -H "Content-Type: application/json" -d '{"name": "عميل جديد", "phone": "0501234567"}'</code>
                            </div>
                        </div>
                    </div>

                    <!-- الموردين -->
                    <div class="card endpoint-card method-get">
                        <div class="card-body">
                            <h6><span class="badge bg-success">GET</span> /api/suppliers</h6>
                            <p class="text-muted">الحصول على قائمة جميع الموردين</p>
                            <div class="code-block">
                                <code>curl -X GET {{ request.url_root }}api/suppliers</code>
                            </div>
                        </div>
                    </div>

                    <!-- المنتجات -->
                    <div class="card endpoint-card method-get">
                        <div class="card-body">
                            <h6><span class="badge bg-success">GET</span> /api/products</h6>
                            <p class="text-muted">الحصول على قائمة جميع المنتجات</p>
                            <div class="code-block">
                                <code>curl -X GET {{ request.url_root }}api/products</code>
                            </div>
                        </div>
                    </div>

                    <!-- المبيعات -->
                    <div class="card endpoint-card method-get">
                        <div class="card-body">
                            <h6><span class="badge bg-success">GET</span> /api/sales</h6>
                            <p class="text-muted">الحصول على قائمة فواتير المبيعات</p>
                            <div class="code-block">
                                <code>curl -X GET {{ request.url_root }}api/sales</code>
                            </div>
                        </div>
                    </div>

                    <!-- الإحصائيات -->
                    <div class="card endpoint-card method-get">
                        <div class="card-body">
                            <h6><span class="badge bg-success">GET</span> /api/statistics</h6>
                            <p class="text-muted">الحصول على إحصائيات النظام</p>
                            <div class="code-block">
                                <code>curl -X GET {{ request.url_root }}api/statistics</code>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- أمثلة الاستجابة -->
            <div class="card api-card">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="fas fa-code me-2"></i>أمثلة الاستجابة</h5>
                </div>
                <div class="card-body">
                    <h6>مثال استجابة GET /api/statistics:</h6>
                    <div class="code-block">
                        <pre><code class="language-json">{
  "status": "success",
  "data": {
    "customers": 15,
    "suppliers": 8,
    "products": 25,
    "employees": 5,
    "total_sales": 45000.00,
    "total_purchases": 32000.00,
    "total_expenses": 8000.00,
    "net_profit": 5000.00
  },
  "timestamp": "2024-01-15T10:30:00Z"
}</code></pre>
                    </div>
                </div>
            </div>

            <!-- اختبار API -->
            <div class="card api-card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-play me-2"></i>اختبار API</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <button class="btn btn-success w-100 mb-2" onclick="testAPI('/api/statistics')">
                                <i class="fas fa-chart-bar me-2"></i>اختبار الإحصائيات
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-primary w-100 mb-2" onclick="testAPI('/api/customers')">
                                <i class="fas fa-users me-2"></i>اختبار العملاء
                            </button>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h6>نتيجة الاختبار:</h6>
                        <div id="apiResult" class="code-block" style="min-height: 100px;">
                            <em class="text-muted">اضغط على أحد الأزرار لاختبار API</em>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
        <script>
            async function testAPI(endpoint) {
                const resultDiv = document.getElementById('apiResult');
                resultDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الاختبار...';

                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    resultDiv.innerHTML = '<pre><code class="language-json">' + JSON.stringify(data, null, 2) + '</code></pre>';
                    Prism.highlightAll();
                } catch (error) {
                    resultDiv.innerHTML = '<div class="text-danger">خطأ: ' + error.message + '</div>';
                }
            }
        </script>
    </body>
    </html>
    ''')

# API Endpoints
@app.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'email': c.email,
            'address': c.address,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in customers],
        'count': len(customers)
    })

@app.route('/api/suppliers')
def api_suppliers():
    suppliers = Supplier.query.all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': s.id,
            'name': s.name,
            'phone': s.phone,
            'email': s.email,
            'address': s.address,
            'created_at': s.created_at.isoformat() if s.created_at else None
        } for s in suppliers],
        'count': len(suppliers)
    })

@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'cost': float(p.cost) if p.cost else None,
            'quantity': p.quantity,
            'min_quantity': p.min_quantity,
            'category': p.category,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in products],
        'count': len(products)
    })

@app.route('/api/sales')
def api_sales():
    sales = SalesInvoice.query.all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': s.id,
            'invoice_number': s.invoice_number,
            'customer_name': s.customer.name if s.customer else 'عميل نقدي',
            'date': s.date.isoformat(),
            'total': float(s.total),
            'status': s.status,
            'created_at': s.created_at.isoformat() if s.created_at else None
        } for s in sales],
        'count': len(sales)
    })

@app.route('/api/statistics')
def api_statistics():
    from sqlalchemy import func

    # إحصائيات أساسية
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    total_products = Product.query.count()
    total_employees = Employee.query.count()

    # إحصائيات مالية
    total_sales = db.session.query(func.sum(SalesInvoice.total)).scalar() or 0
    total_purchases = db.session.query(func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses

    return jsonify({
        'status': 'success',
        'data': {
            'counts': {
                'customers': total_customers,
                'suppliers': total_suppliers,
                'products': total_products,
                'employees': total_employees
            },
            'financial': {
                'total_sales': float(total_sales),
                'total_purchases': float(total_purchases),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit)
            }
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# ===== نظام إدارة المستخدمين =====

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المستخدمين - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="javascript:history.back()">
                        <i class="fas fa-arrow-right me-1"></i>رجوع
                    </a>
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="card shadow">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-users-cog me-2"></i>إدارة المستخدمين</h5>
                    <button type="button" class="btn btn-light" data-bs-toggle="modal" data-bs-target="#addUserModal">
                        <i class="fas fa-plus me-2"></i>إضافة مستخدم جديد
                    </button>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>اسم المستخدم</th>
                                    <th>الاسم الكامل</th>
                                    <th>الدور</th>
                                    <th>تاريخ الإنشاء</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for user in users %}
                                <tr>
                                    <td><strong>{{ user.username }}</strong></td>
                                    <td>{{ user.full_name }}</td>
                                    <td>
                                        <span class="badge {{ 'bg-danger' if user.role == 'admin' else 'bg-primary' }}">
                                            {{ 'مدير' if user.role == 'admin' else 'مستخدم' }}
                                        </span>
                                    </td>
                                    <td>{{ user.created_at.strftime('%Y-%m-%d') if user.created_at else '-' }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-warning" onclick="editUser({{ user.id }})">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        {% if user.id != current_user.id %}
                                        <button class="btn btn-sm btn-outline-danger" onclick="deleteUser({{ user.id }}, '{{ user.username }}')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                        {% endif %}
                                        <button class="btn btn-sm btn-outline-info" onclick="resetPassword({{ user.id }})">
                                            <i class="fas fa-key"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal إضافة مستخدم -->
        <div class="modal fade" id="addUserModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">إضافة مستخدم جديد</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_user') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="username" class="form-label">اسم المستخدم *</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="full_name" class="form-label">الاسم الكامل *</label>
                                <input type="text" class="form-control" id="full_name" name="full_name" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">كلمة المرور *</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <div class="mb-3">
                                <label for="role" class="form-label">الدور</label>
                                <select class="form-select" id="role" name="role">
                                    <option value="user">مستخدم</option>
                                    <option value="admin">مدير</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="submit" class="btn btn-primary">حفظ المستخدم</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function editUser(id) {
                // تحميل بيانات المستخدم وفتح نموذج التحرير
                alert('سيتم تطوير تحرير المستخدم قريباً');
            }

            function deleteUser(id, username) {
                if (confirm('هل أنت متأكد من حذف المستخدم: ' + username + '؟')) {
                    fetch('/delete_user/' + id, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم حذف المستخدم بنجاح');
                            location.reload();
                        } else {
                            alert('حدث خطأ أثناء الحذف');
                        }
                    });
                }
            }

            function resetPassword(id) {
                const newPassword = prompt('أدخل كلمة المرور الجديدة:');
                if (newPassword) {
                    fetch('/reset_password/' + id, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({password: newPassword})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم تغيير كلمة المرور بنجاح');
                        } else {
                            alert('حدث خطأ أثناء تغيير كلمة المرور');
                        }
                    });
                }
            }
        </script>
    </body>
    </html>
    ''', users=users)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية لإضافة مستخدمين', 'error')
        return redirect(url_for('dashboard'))

    # التحقق من عدم وجود اسم المستخدم
    existing_user = User.query.filter_by(username=request.form['username']).first()
    if existing_user:
        flash('اسم المستخدم موجود بالفعل', 'error')
        return redirect(url_for('users'))

    user = User(
        username=request.form['username'],
        full_name=request.form['full_name'],
        role=request.form.get('role', 'user')
    )
    user.set_password(request.form['password'])

    db.session.add(user)
    db.session.commit()
    flash('تم إضافة المستخدم بنجاح', 'success')
    return redirect(url_for('users'))

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})

    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'لا يمكن حذف نفسك'})

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})

    user = User.query.get_or_404(user_id)
    new_password = request.json.get('password')

    if new_password:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'كلمة المرور مطلوبة'})

# ===== وظائف الحذف والتحرير =====

@app.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_supplier/<int:supplier_id>', methods=['DELETE'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'success': True})

# ===== وظائف الطباعة والتصدير =====

@app.route('/print_invoice/<int:invoice_id>')
@login_required
def print_invoice(invoice_id):
    invoice = SalesInvoice.query.get_or_404(invoice_id)
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {{ invoice.invoice_number }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .invoice-details { margin: 20px 0; }
            .total { font-size: 18px; font-weight: bold; }
            @media print {
                .no-print { display: none; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>فاتورة مبيعات</h1>
            <h2>رقم الفاتورة: {{ invoice.invoice_number }}</h2>
        </div>

        <div class="invoice-details">
            <p><strong>العميل:</strong> {{ invoice.customer.name if invoice.customer else 'عميل نقدي' }}</p>
            <p><strong>التاريخ:</strong> {{ invoice.date.strftime('%Y-%m-%d') }}</p>
            <p><strong>المبلغ الفرعي:</strong> {{ "%.2f"|format(invoice.subtotal) }} ر.س</p>
            <p><strong>الضريبة:</strong> {{ "%.2f"|format(invoice.tax_amount) }} ر.س</p>
            <p class="total"><strong>الإجمالي:</strong> {{ "%.2f"|format(invoice.total) }} ر.س</p>
            {% if invoice.notes %}
            <p><strong>ملاحظات:</strong> {{ invoice.notes }}</p>
            {% endif %}
        </div>

        <div class="no-print">
            <button onclick="window.print()" class="btn btn-primary">طباعة</button>
            <button onclick="window.close()" class="btn btn-secondary">إغلاق</button>
        </div>

        <script>
            window.onload = function() {
                window.print();
            }
        </script>
    </body>
    </html>
    ''', invoice=invoice)

@app.route('/export_pdf/<report_type>')
@login_required
def export_pdf(report_type):
    # هذه وظيفة أساسية للتصدير - يمكن تطويرها لاحقاً
    flash('سيتم تطوير تصدير PDF قريباً', 'info')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/export_excel/<report_type>')
@login_required
def export_excel(report_type):
    # هذه وظيفة أساسية للتصدير - يمكن تطويرها لاحقاً
    flash('سيتم تطوير تصدير Excel قريباً', 'info')
    return redirect(request.referrer or url_for('dashboard'))

# ===== تحديث الملف الشخصي =====

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.full_name = request.form['full_name']

    # التحقق من عدم وجود اسم المستخدم الجديد
    new_username = request.form['username']
    if new_username != current_user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            flash('اسم المستخدم موجود بالفعل', 'error')
            return redirect(url_for('settings'))
        current_user.username = new_username

    db.session.commit()
    flash('تم تحديث الملف الشخصي بنجاح', 'success')
    return redirect(url_for('settings'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if not current_user.check_password(current_password):
        flash('كلمة المرور الحالية غير صحيحة', 'error')
        return redirect(url_for('settings'))

    if new_password != confirm_password:
        flash('كلمة المرور الجديدة غير متطابقة', 'error')
        return redirect(url_for('settings'))

    if len(new_password) < 6:
        flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
        return redirect(url_for('settings'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('تم تغيير كلمة المرور بنجاح', 'success')
    return redirect(url_for('settings'))

# ===== نظام الإعدادات المحسن =====

@app.route('/settings')
@login_required
def settings():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إعدادات النظام - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .settings-card {
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }
            .settings-card:hover { transform: translateY(-2px); }
            .feature-icon {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
                margin: 0 auto 15px;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-cogs me-2"></i>إعدادات النظام</h2>
                    <p class="text-muted">إدارة وتخصيص إعدادات نظام المحاسبة</p>
                </div>
            </div>

            <!-- معلومات النظام -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card settings-card bg-primary text-white">
                        <div class="card-body text-center">
                            <div class="feature-icon bg-light text-primary">
                                <i class="fas fa-info-circle"></i>
                            </div>
                            <h6>معلومات النظام</h6>
                            <p class="mb-0">الإصدار 2.0.0</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card settings-card bg-success text-white">
                        <div class="card-body text-center">
                            <div class="feature-icon bg-light text-success">
                                <i class="fas fa-database"></i>
                            </div>
                            <h6>قاعدة البيانات</h6>
                            <p class="mb-0">SQLite متصلة</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card settings-card bg-warning text-dark">
                        <div class="card-body text-center">
                            <div class="feature-icon bg-light text-warning">
                                <i class="fas fa-users"></i>
                            </div>
                            <h6>المستخدمين</h6>
                            <p class="mb-0">{{ current_user.full_name }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card settings-card bg-info text-white">
                        <div class="card-body text-center">
                            <div class="feature-icon bg-light text-info">
                                <i class="fas fa-cloud"></i>
                            </div>
                            <h6>النشر</h6>
                            <p class="mb-0">Render Cloud</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- إعدادات النظام -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card settings-card">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0"><i class="fas fa-user-cog me-2"></i>إعدادات المستخدم</h6>
                        </div>
                        <div class="card-body">
                            <form>
                                <div class="mb-3">
                                    <label class="form-label">الاسم الكامل</label>
                                    <input type="text" class="form-control" value="{{ current_user.full_name }}" readonly>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">اسم المستخدم</label>
                                    <input type="text" class="form-control" value="{{ current_user.username }}" readonly>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الدور</label>
                                    <input type="text" class="form-control" value="{{ current_user.role }}" readonly>
                                </div>
                                <button type="button" class="btn btn-primary" disabled>
                                    <i class="fas fa-save me-2"></i>حفظ التغييرات
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card settings-card">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-cogs me-2"></i>إعدادات النظام</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">اسم الشركة</label>
                                <input type="text" class="form-control" value="شركة المحاسبة الاحترافية">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">معدل الضريبة (%)</label>
                                <input type="number" class="form-control" value="15" step="0.01">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">العملة</label>
                                <select class="form-select">
                                    <option selected>ريال سعودي (ر.س)</option>
                                    <option>دولار أمريكي ($)</option>
                                    <option>يورو (€)</option>
                                </select>
                            </div>
                            <button type="button" class="btn btn-success">
                                <i class="fas fa-save me-2"></i>حفظ الإعدادات
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- أدوات النظام -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card settings-card">
                        <div class="card-header bg-dark text-white">
                            <h6 class="mb-0"><i class="fas fa-tools me-2"></i>أدوات النظام</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <div class="feature-icon bg-info">
                                            <i class="fas fa-download"></i>
                                        </div>
                                        <h6>نسخ احتياطي</h6>
                                        <button class="btn btn-info btn-sm">
                                            <i class="fas fa-download me-1"></i>إنشاء نسخة
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <div class="feature-icon bg-warning">
                                            <i class="fas fa-upload"></i>
                                        </div>
                                        <h6>استعادة</h6>
                                        <button class="btn btn-warning btn-sm">
                                            <i class="fas fa-upload me-1"></i>استعادة نسخة
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <div class="feature-icon bg-success">
                                            <i class="fas fa-sync"></i>
                                        </div>
                                        <h6>تحديث</h6>
                                        <button class="btn btn-success btn-sm">
                                            <i class="fas fa-sync me-1"></i>تحديث النظام
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <div class="feature-icon bg-danger">
                                            <i class="fas fa-trash"></i>
                                        </div>
                                        <h6>إعادة تعيين</h6>
                                        <button class="btn btn-danger btn-sm" onclick="confirmReset()">
                                            <i class="fas fa-trash me-1"></i>إعادة تعيين
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- معلومات تقنية -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card settings-card">
                        <div class="card-header bg-secondary text-white">
                            <h6 class="mb-0"><i class="fas fa-info me-2"></i>معلومات تقنية</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>إصدار النظام:</strong></td>
                                            <td>2.0.0 Professional</td>
                                        </tr>
                                        <tr>
                                            <td><strong>إصدار Python:</strong></td>
                                            <td>3.11.7</td>
                                        </tr>
                                        <tr>
                                            <td><strong>إصدار Flask:</strong></td>
                                            <td>3.0.0</td>
                                        </tr>
                                        <tr>
                                            <td><strong>قاعدة البيانات:</strong></td>
                                            <td>SQLite</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>منصة النشر:</strong></td>
                                            <td>Render Cloud Platform</td>
                                        </tr>
                                        <tr>
                                            <td><strong>تاريخ آخر تحديث:</strong></td>
                                            <td>{{ moment().format('YYYY-MM-DD HH:mm') }}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>حالة النظام:</strong></td>
                                            <td><span class="badge bg-success">نشط</span></td>
                                        </tr>
                                        <tr>
                                            <td><strong>وقت التشغيل:</strong></td>
                                            <td>متاح 24/7</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal تغيير كلمة المرور -->
        <div class="modal fade" id="changePasswordModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">تغيير كلمة المرور</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('change_password') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="current_password" class="form-label">كلمة المرور الحالية *</label>
                                <input type="password" class="form-control" id="current_password" name="current_password" required>
                            </div>
                            <div class="mb-3">
                                <label for="new_password" class="form-label">كلمة المرور الجديدة *</label>
                                <input type="password" class="form-control" id="new_password" name="new_password" required minlength="6">
                            </div>
                            <div class="mb-3">
                                <label for="confirm_password" class="form-label">تأكيد كلمة المرور *</label>
                                <input type="password" class="form-control" id="confirm_password" name="confirm_password" required minlength="6">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="submit" class="btn btn-warning">تغيير كلمة المرور</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="/static/js/accounting-system.js"></script>
        <script>
            function confirmReset() {
                if (confirm('هل أنت متأكد من إعادة تعيين النظام؟ سيتم حذف جميع البيانات!')) {
                    alert('تم إلغاء العملية للحماية');
                }
            }

            // التحقق من تطابق كلمة المرور
            document.getElementById('confirm_password').addEventListener('input', function() {
                const newPassword = document.getElementById('new_password').value;
                const confirmPassword = this.value;

                if (newPassword !== confirmPassword) {
                    this.setCustomValidity('كلمة المرور غير متطابقة');
                } else {
                    this.setCustomValidity('');
                }
            });
        </script>
    </body>
    </html>
    ''')

# ===== تهيئة قاعدة البيانات =====

def init_db():
    """تهيئة قاعدة البيانات وإنشاء البيانات الأساسية"""
    with app.app_context():
        db.create_all()

        # إنشاء مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='مدير النظام',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)

            # إضافة بيانات تجريبية
            sample_customer = Customer(
                name='عميل تجريبي',
                phone='0501234567',
                email='customer@example.com',
                address='الرياض، المملكة العربية السعودية'
            )

            sample_supplier = Supplier(
                name='مورد تجريبي',
                phone='0507654321',
                email='supplier@example.com',
                address='جدة، المملكة العربية السعودية'
            )

            sample_product = Product(
                name='منتج تجريبي',
                description='وصف المنتج التجريبي',
                price=100.00,
                cost=80.00,
                quantity=50,
                min_quantity=10,
                category='عام'
            )

            sample_employee = Employee(
                name='موظف تجريبي',
                position='محاسب',
                salary=5000.00,
                phone='0509876543',
                email='employee@example.com',
                hire_date=date.today()
            )

            db.session.add_all([sample_customer, sample_supplier, sample_product, sample_employee])
            db.session.commit()
            print('✅ تم إنشاء المستخدم الافتراضي والبيانات التجريبية')

# تشغيل النظام
if __name__ == '__main__':
    print('🚀 بدء تشغيل نظام المحاسبة الاحترافي')
    print('✅ تم تحميل النظام الكامل')

    # تهيئة قاعدة البيانات
    init_db()
    print('✅ تم تهيئة قاعدة البيانات')
    print('🌐 الرابط: http://localhost:5000')
    print('👤 المستخدم: admin | كلمة المرور: admin123')

    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# للنشر على Render
init_db()
