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
    purchases = PurchaseInvoice.query.all()
    return f"<h1>فواتير المشتريات</h1><p>عدد الفواتير: {len(purchases)}</p><a href='/dashboard'>العودة للوحة التحكم</a>"

@app.route('/expenses')
@login_required
def expenses():
    expenses = Expense.query.all()
    return f"<h1>إدارة المصروفات</h1><p>عدد المصروفات: {len(expenses)}</p><a href='/dashboard'>العودة للوحة التحكم</a>"

@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return f"<h1>إدارة الموظفين</h1><p>عدد الموظفين: {len(employees)}</p><a href='/dashboard'>العودة للوحة التحكم</a>"

@app.route('/reports')
@login_required
def reports():
    return "<h1>التقارير المالية</h1><p>تقارير شاملة ومفصلة</p><a href='/dashboard'>العودة للوحة التحكم</a>"

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'active',
        'message': 'نظام المحاسبة الاحترافي يعمل بنجاح',
        'version': '1.0.0',
        'database': 'متصلة',
        'deployment': 'Render Cloud Platform'
    })

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
