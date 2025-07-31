#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي الكامل - متوافق مع Python 3.11
Complete Professional Accounting System - Python 3.11 Compatible
"""

import os
from datetime import datetime, date

# إضافة دوال مساعدة لـ Jinja2
def format_date(format_string='%Y-%m-%d'):
    """دالة لتنسيق التاريخ الحالي"""
    return datetime.now().strftime(format_string)

def format_datetime(format_string='%Y-%m-%d %H:%M'):
    """دالة لتنسيق التاريخ والوقت الحالي"""
    return datetime.now().strftime(format_string)

def zfill_number(number, width=3):
    """دالة لإضافة أصفار للرقم"""
    return str(number).zfill(width)
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

# تسجيل الدوال المساعدة مع Jinja2
app.jinja_env.globals.update(
    format_date=format_date,
    format_datetime=format_datetime,
    zfill_number=zfill_number,
    now=datetime.now
)

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
    tax_rate = db.Column(db.Numeric(5, 2), default=15.0)  # معدل الضريبة
    has_tax = db.Column(db.Boolean, default=True)  # هل تحتوي على ضريبة
    total = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), default='cash')  # mada,bank,visa,cash,mastercard,aks,gcc,stc
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('Customer', backref='sales_invoices')
    items = db.relationship('SalesInvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')

class SalesInvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('sales_invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)  # اسم المنتج (للمرونة)
    description = db.Column(db.Text)  # وصف الصنف
    quantity = db.Column(db.Numeric(10, 3), nullable=False, default=1.0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)

    product = db.relationship('Product', backref=db.backref('sales_items', lazy=True))

class PurchaseInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=15.0)  # معدل الضريبة
    has_tax = db.Column(db.Boolean, default=True)  # هل تحتوي على ضريبة
    total = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), default='cash')  # mada,bank,visa,cash,mastercard,aks,gcc,stc
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='purchase_invoices')
    items = db.relationship('PurchaseInvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')

class PurchaseInvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)  # اسم المنتج (للمرونة)
    description = db.Column(db.Text)  # وصف الصنف
    quantity = db.Column(db.Numeric(10, 3), nullable=False, default=1.0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)

    product = db.relationship('Product', backref=db.backref('purchase_items', lazy=True))

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

    # إعدادات الراتب والعمل
    working_days = db.Column(db.Integer, default=30)  # أيام العمل في الشهر
    overtime_rate = db.Column(db.Numeric(10, 2), default=0.0)  # معدل الساعة الإضافية
    allowances = db.Column(db.Numeric(10, 2), default=0.0)  # البدلات
    deductions = db.Column(db.Numeric(10, 2), default=0.0)  # الاستقطاعات

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة مع كشوف الرواتب
    payrolls = db.relationship('EmployeePayroll', backref='employee', lazy=True, cascade='all, delete-orphan')

class EmployeePayroll(db.Model):
    """كشف راتب الموظف الشهري"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # الشهر (1-12)
    year = db.Column(db.Integer, nullable=False)  # السنة

    # تفاصيل الراتب
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)  # الراتب الأساسي
    working_days = db.Column(db.Integer, default=30)  # أيام العمل المقررة
    actual_working_days = db.Column(db.Integer, default=30)  # أيام العمل الفعلية
    overtime_hours = db.Column(db.Numeric(8, 2), default=0.0)  # الساعات الإضافية
    overtime_amount = db.Column(db.Numeric(10, 2), default=0.0)  # مبلغ الساعات الإضافية
    allowances = db.Column(db.Numeric(10, 2), default=0.0)  # البدلات
    deductions = db.Column(db.Numeric(10, 2), default=0.0)  # الاستقطاعات

    # المبالغ المحسوبة
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False)  # إجمالي الراتب
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)  # صافي الراتب

    # معلومات إضافية
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, paid
    payment_date = db.Column(db.Date)
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
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    total_customers = len(customers)

    # إحصائيات العملاء
    customers_with_sales = db.session.query(Customer).join(SalesInvoice).distinct().count()

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
        <title>فواتير المبيعات - نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .table-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .btn-action {
                border-radius: 10px;
                padding: 0.5rem 1rem;
                margin: 0.2rem;
                transition: all 0.3s ease;
            }
            .btn-action:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .status-pending { color: #ffc107; }
            .status-paid { color: #198754; }
            .status-cancelled { color: #dc3545; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
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
            <!-- عنوان الصفحة -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-success">
                    <i class="fas fa-file-invoice me-3"></i>فواتير المبيعات
                </h1>
                <p class="lead text-muted">إدارة وتتبع جميع فواتير المبيعات</p>
            </div>

            <!-- إحصائيات المبيعات -->
            <div class="row g-4 mb-5">
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-file-invoice fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ sales|length }}</h3>
                        <p class="text-muted mb-0">إجمالي الفواتير</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-dollar-sign fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ "%.2f"|format(total_sales) }}</h3>
                        <p class="text-muted mb-0">إجمالي المبيعات (ر.س)</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-users fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-primary">{{ customers|length }}</h3>
                        <p class="text-muted mb-0">العملاء المسجلين</p>
                    </div>
                </div>
            </div>

            <div class="table-container">
                <div class="card-header bg-success text-white p-4 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0 fw-bold"><i class="fas fa-file-invoice me-2"></i>قائمة فواتير المبيعات</h5>
                    <button type="button" class="btn btn-light btn-lg" data-bs-toggle="modal" data-bs-target="#addSaleModal">
                        <i class="fas fa-plus me-2"></i>فاتورة جديدة
                    </button>
                </div>
                <div class="card-body p-0">
                    {% if sales %}
                    <div class="table-responsive">
                        <table class="table table-hover mb-0" id="salesTable">
                            <thead class="table-dark">
                                <tr>
                                    <th class="p-3">رقم الفاتورة</th>
                                    <th class="p-3">العميل</th>
                                    <th class="p-3">التاريخ</th>
                                    <th class="p-3">المبلغ الفرعي</th>
                                    <th class="p-3">الضريبة</th>
                                    <th class="p-3">الإجمالي</th>
                                    <th class="p-3">الحالة</th>
                                    <th class="p-3">الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for sale in sales %}
                                <tr>
                                    <td class="p-3">
                                        <strong class="text-primary">{{ sale.invoice_number }}</strong>
                                    </td>
                                    <td class="p-3">
                                        <div>
                                            <strong>{{ sale.customer.name if sale.customer else 'عميل نقدي' }}</strong>
                                            {% if sale.customer and sale.customer.phone %}
                                            <br><small class="text-muted">{{ sale.customer.phone }}</small>
                                            {% endif %}
                                        </div>
                                    </td>
                                    <td class="p-3">{{ sale.date.strftime('%Y-%m-%d') }}</td>
                                    <td class="p-3">{{ "%.2f"|format(sale.subtotal) }} ر.س</td>
                                    <td class="p-3">{{ "%.2f"|format(sale.tax_amount) }} ر.س</td>
                                    <td class="p-3">
                                        <strong class="text-success fs-6">{{ "%.2f"|format(sale.total) }} ر.س</strong>
                                    </td>
                                    <td class="p-3">
                                        <span class="badge
                                        {% if sale.status == 'paid' %}bg-success
                                        {% elif sale.status == 'pending' %}bg-warning
                                        {% else %}bg-danger{% endif %}">
                                        {% if sale.status == 'paid' %}مدفوعة
                                        {% elif sale.status == 'pending' %}معلقة
                                        {% else %}ملغية{% endif %}
                                        </span>
                                    </td>
                                    <td class="p-3">
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-sm btn-outline-primary btn-action" title="عرض التفاصيل" onclick="viewSale({{ sale.id }})">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-success btn-action" title="طباعة الفاتورة" onclick="printInvoice({{ sale.id }})">
                                                <i class="fas fa-print"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-warning btn-action" title="تعديل" onclick="editSale({{ sale.id }})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger btn-action" title="حذف" onclick="deleteSale({{ sale.id }}, '{{ sale.invoice_number }}')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="fas fa-file-invoice fa-4x text-muted mb-3"></i>
                            <h4 class="text-muted">لا توجد فواتير مبيعات</h4>
                            <p class="text-muted">ابدأ بإنشاء أول فاتورة مبيعات</p>
                        </div>
                        <button type="button" class="btn btn-success btn-lg" data-bs-toggle="modal" data-bs-target="#addSaleModal">
                            <i class="fas fa-plus me-2"></i>إنشاء فاتورة جديدة
                        </button>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة فاتورة -->
        <div class="modal fade" id="addSaleModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title fw-bold"><i class="fas fa-plus me-2"></i>فاتورة مبيعات جديدة</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_sale') }}" id="salesInvoiceForm">
                        <div class="modal-body">
                            <!-- معلومات الفاتورة الأساسية -->
                            <div class="row mb-4">
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="invoice_number" class="form-label fw-bold">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" id="invoice_number" name="invoice_number"
                                               value="INV-{{ format_date('%Y%m%d') }}-{{ zfill_number(sales|length + 1, 3) }}" required>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="customer_id" class="form-label fw-bold">العميل</label>
                                        <select class="form-select" id="customer_id" name="customer_id">
                                            <option value="">عميل نقدي</option>
                                            {% for customer in customers %}
                                            <option value="{{ customer.id }}">{{ customer.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="payment_method" class="form-label fw-bold">طريقة الدفع *</label>
                                        <select class="form-select" id="payment_method" name="payment_method" required>
                                            <option value="cash">نقدي</option>
                                            <option value="mada">مدى</option>
                                            <option value="visa">فيزا</option>
                                            <option value="mastercard">ماستركارد</option>
                                            <option value="bank">تحويل بنكي</option>
                                            <option value="stc">STC Pay</option>
                                            <option value="gcc">GCC Pay</option>
                                            <option value="aks">أكس</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- إعدادات الضريبة -->
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="has_tax" name="has_tax" checked>
                                        <label class="form-check-label fw-bold" for="has_tax">
                                            تطبيق الضريبة على الفاتورة
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="tax_rate" class="form-label fw-bold">معدل الضريبة (%)</label>
                                        <input type="number" step="0.01" class="form-control" id="tax_rate" name="tax_rate" value="15" min="0" max="100">
                                    </div>
                                </div>
                            </div>

                            <!-- أصناف الفاتورة -->
                            <div class="mb-4">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h6 class="fw-bold text-primary">
                                        <i class="fas fa-list me-2"></i>أصناف الفاتورة
                                    </h6>
                                    <button type="button" class="btn btn-sm btn-primary" onclick="addInvoiceItem()">
                                        <i class="fas fa-plus me-1"></i>إضافة صنف
                                    </button>
                                </div>

                                <div class="table-responsive">
                                    <table class="table table-bordered" id="invoiceItemsTable">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">اسم الصنف</th>
                                                <th width="20%">الوصف</th>
                                                <th width="15%">الكمية</th>
                                                <th width="15%">سعر الوحدة</th>
                                                <th width="15%">الإجمالي</th>
                                                <th width="10%">إجراءات</th>
                                            </tr>
                                        </thead>
                                        <tbody id="invoiceItemsBody">
                                            <tr class="invoice-item">
                                                <td>
                                                    <input type="text" class="form-control item-name" name="items[0][name]" placeholder="اسم الصنف" required>
                                                </td>
                                                <td>
                                                    <input type="text" class="form-control item-description" name="items[0][description]" placeholder="الوصف">
                                                </td>
                                                <td>
                                                    <input type="number" step="0.001" class="form-control item-quantity" name="items[0][quantity]" value="1" min="0.001" required>
                                                </td>
                                                <td>
                                                    <input type="number" step="0.01" class="form-control item-price" name="items[0][price]" value="0" min="0" required>
                                                </td>
                                                <td>
                                                    <input type="number" step="0.01" class="form-control item-total" name="items[0][total]" value="0" readonly>
                                                </td>
                                                <td>
                                                    <button type="button" class="btn btn-sm btn-danger" onclick="removeInvoiceItem(this)">
                                                        <i class="fas fa-trash"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- ملخص الفاتورة -->
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="mb-3">
                                        <label for="notes" class="form-label fw-bold">ملاحظات</label>
                                        <textarea class="form-control" id="notes" name="notes" rows="2"></textarea>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <h6 class="fw-bold text-primary mb-3">ملخص الفاتورة</h6>
                                            <div class="d-flex justify-content-between mb-2">
                                                <span>المبلغ الفرعي:</span>
                                                <span id="invoice_subtotal">0.00 ر.س</span>
                                            </div>
                                            <div class="d-flex justify-content-between mb-2" id="tax_row">
                                                <span>الضريبة (<span id="tax_rate_display">15</span>%):</span>
                                                <span id="invoice_tax">0.00 ر.س</span>
                                            </div>
                                            <hr>
                                            <div class="d-flex justify-content-between fw-bold text-success">
                                                <span>الإجمالي:</span>
                                                <span id="invoice_total">0.00 ر.س</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- الحقول المخفية للإرسال -->
                            <input type="hidden" id="subtotal" name="subtotal" value="0">
                            <input type="hidden" id="tax_amount" name="tax_amount" value="0">
                            <input type="hidden" id="total" name="total" value="0">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>إلغاء
                            </button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save me-2"></i>حفظ الفاتورة
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // وظائف إدارة فواتير المبيعات
            function viewSale(saleId) {
                alert('عرض تفاصيل الفاتورة رقم: ' + saleId);
                // يمكن إضافة modal لعرض التفاصيل
            }

            function editSale(saleId) {
                alert('تعديل الفاتورة رقم: ' + saleId);
                // يمكن إضافة modal للتعديل
            }

            function deleteSale(saleId, invoiceNumber) {
                if (confirm('هل أنت متأكد من حذف الفاتورة: ' + invoiceNumber + '؟')) {
                    fetch('/delete_sale/' + saleId, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم حذف الفاتورة بنجاح');
                            location.reload();
                        } else {
                            alert('حدث خطأ أثناء الحذف: ' + (data.message || 'خطأ غير معروف'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('حدث خطأ أثناء الحذف');
                    });
                }
            }

            function printInvoice(saleId) {
                window.open('/print_invoice/' + saleId, '_blank');
            }

            // إدارة أصناف الفاتورة
            let itemIndex = 1;

            function addInvoiceItem() {
                const tbody = document.getElementById('invoiceItemsBody');
                const newRow = document.createElement('tr');
                newRow.className = 'invoice-item';
                newRow.innerHTML = `
                    <td>
                        <input type="text" class="form-control item-name" name="items[${itemIndex}][name]" placeholder="اسم الصنف" required>
                    </td>
                    <td>
                        <input type="text" class="form-control item-description" name="items[${itemIndex}][description]" placeholder="الوصف">
                    </td>
                    <td>
                        <input type="number" step="0.001" class="form-control item-quantity" name="items[${itemIndex}][quantity]" value="1" min="0.001" required>
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control item-price" name="items[${itemIndex}][price]" value="0" min="0" required>
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control item-total" name="items[${itemIndex}][total]" value="0" readonly>
                    </td>
                    <td>
                        <button type="button" class="btn btn-sm btn-danger" onclick="removeInvoiceItem(this)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(newRow);
                itemIndex++;

                // إضافة event listeners للحقول الجديدة
                attachItemEventListeners(newRow);
            }

            function removeInvoiceItem(button) {
                const row = button.closest('tr');
                if (document.querySelectorAll('.invoice-item').length > 1) {
                    row.remove();
                    calculateInvoiceTotal();
                } else {
                    alert('يجب أن تحتوي الفاتورة على صنف واحد على الأقل');
                }
            }

            function attachItemEventListeners(row) {
                const quantityInput = row.querySelector('.item-quantity');
                const priceInput = row.querySelector('.item-price');
                const totalInput = row.querySelector('.item-total');

                function calculateItemTotal() {
                    const quantity = parseFloat(quantityInput.value) || 0;
                    const price = parseFloat(priceInput.value) || 0;
                    const total = quantity * price;
                    totalInput.value = total.toFixed(2);
                    calculateInvoiceTotal();
                }

                quantityInput.addEventListener('input', calculateItemTotal);
                priceInput.addEventListener('input', calculateItemTotal);
            }

            function calculateInvoiceTotal() {
                let subtotal = 0;
                document.querySelectorAll('.item-total').forEach(input => {
                    subtotal += parseFloat(input.value) || 0;
                });

                const hasTax = document.getElementById('has_tax').checked;
                const taxRate = parseFloat(document.getElementById('tax_rate').value) || 0;
                const taxAmount = hasTax ? (subtotal * taxRate / 100) : 0;
                const total = subtotal + taxAmount;

                // تحديث العرض
                document.getElementById('invoice_subtotal').textContent = subtotal.toFixed(2) + ' ر.س';
                document.getElementById('invoice_tax').textContent = taxAmount.toFixed(2) + ' ر.س';
                document.getElementById('invoice_total').textContent = total.toFixed(2) + ' ر.س';
                document.getElementById('tax_rate_display').textContent = taxRate;

                // تحديث الحقول المخفية
                document.getElementById('subtotal').value = subtotal.toFixed(2);
                document.getElementById('tax_amount').value = taxAmount.toFixed(2);
                document.getElementById('total').value = total.toFixed(2);

                // إظهار/إخفاء صف الضريبة
                document.getElementById('tax_row').style.display = hasTax ? 'flex' : 'none';
            }

            // تهيئة الصفحة
            document.addEventListener('DOMContentLoaded', function() {

                // إضافة event listeners للصف الأول
                const firstRow = document.querySelector('.invoice-item');
                if (firstRow) {
                    attachItemEventListeners(firstRow);
                }

                // event listeners لإعدادات الضريبة
                document.getElementById('has_tax').addEventListener('change', calculateInvoiceTotal);
                document.getElementById('tax_rate').addEventListener('input', calculateInvoiceTotal);

                // تحسين تجربة المستخدم
                const cards = document.querySelectorAll('.stat-card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-10px)';
                    });

                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });

                // تحسين النموذج
                const form = document.getElementById('salesInvoiceForm');
                if (form) {
                    form.addEventListener('submit', function(e) {
                        const items = document.querySelectorAll('.invoice-item');
                        let hasValidItems = false;

                        items.forEach(item => {
                            const name = item.querySelector('.item-name').value.trim();
                            const quantity = parseFloat(item.querySelector('.item-quantity').value);
                            const price = parseFloat(item.querySelector('.item-price').value);

                            if (name && quantity > 0 && price >= 0) {
                                hasValidItems = true;
                            }
                        });

                        if (!hasValidItems) {
                            e.preventDefault();
                            alert('يجب إضافة صنف واحد صحيح على الأقل');
                            return false;
                        }
                    });
                }
            });
        </script>
    </body>
    </html>
    ''', sales=sales, customers=customers, total_sales=total_sales)

@app.route('/add_sale', methods=['POST'])
@login_required
def add_sale():
    try:
        # إنشاء الفاتورة
        sale = SalesInvoice(
            invoice_number=request.form['invoice_number'],
            customer_id=request.form.get('customer_id') if request.form.get('customer_id') else None,
            subtotal=float(request.form['subtotal']),
            tax_amount=float(request.form.get('tax_amount', 0)),
            tax_rate=float(request.form.get('tax_rate', 15)),
            has_tax=bool(request.form.get('has_tax')),
            total=float(request.form.get('total', 0)),
            payment_method=request.form.get('payment_method', 'cash'),
            notes=request.form.get('notes'),
            status='pending'
        )
        db.session.add(sale)
        db.session.flush()  # للحصول على ID الفاتورة

        # إضافة أصناف الفاتورة
        items_data = {}
        for key, value in request.form.items():
            if key.startswith('items[') and '][' in key:
                # استخراج الفهرس والحقل من اسم الحقل
                parts = key.split('][')
                index = parts[0].split('[')[1]
                field = parts[1].rstrip(']')

                if index not in items_data:
                    items_data[index] = {}
                items_data[index][field] = value

        # إنشاء أصناف الفاتورة
        for index, item_data in items_data.items():
            if item_data.get('name') and item_data.get('quantity') and item_data.get('price'):
                quantity = float(item_data['quantity'])
                price = float(item_data['price'])
                total_price = quantity * price

                item = SalesInvoiceItem(
                    invoice_id=sale.id,
                    product_name=item_data['name'],
                    description=item_data.get('description', ''),
                    quantity=quantity,
                    unit_price=price,
                    total_price=total_price
                )
                db.session.add(item)

        db.session.commit()
        flash('تم إنشاء فاتورة المبيعات بنجاح', 'success')
        return redirect(url_for('sales'))

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إنشاء الفاتورة: {str(e)}', 'error')
        return redirect(url_for('sales'))

@app.route('/delete_sale/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    try:
        sale = SalesInvoice.query.get_or_404(sale_id)
        db.session.delete(sale)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الفاتورة بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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
        <title>فواتير المشتريات - نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .table-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .btn-action {
                border-radius: 10px;
                padding: 0.5rem 1rem;
                margin: 0.2rem;
                transition: all 0.3s ease;
            }
            .btn-action:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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
            <!-- عنوان الصفحة -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-secondary">
                    <i class="fas fa-shopping-cart me-3"></i>فواتير المشتريات
                </h1>
                <p class="lead text-muted">إدارة وتتبع جميع فواتير المشتريات والموردين</p>
            </div>

            <!-- إحصائيات المشتريات -->
            <div class="row g-4 mb-5">
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-secondary mb-3">
                            <i class="fas fa-shopping-cart fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-secondary">{{ purchases|length }}</h3>
                        <p class="text-muted mb-0">إجمالي فواتير المشتريات</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-danger mb-3">
                            <i class="fas fa-money-bill-wave fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-danger">{{ "%.2f"|format(total_purchases) }}</h3>
                        <p class="text-muted mb-0">إجمالي قيمة المشتريات (ر.س)</p>
                            <p class="mb-0">إجمالي قيمة المشتريات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-dark mb-3">
                            <i class="fas fa-truck fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-dark">{{ suppliers|length }}</h3>
                        <p class="text-muted mb-0">الموردين المسجلين</p>
                    </div>
                </div>
            </div>

            <div class="table-container">
                <div class="card-header bg-secondary text-white p-4 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0 fw-bold"><i class="fas fa-shopping-cart me-2"></i>قائمة فواتير المشتريات</h5>
                    <button type="button" class="btn btn-light btn-lg" data-bs-toggle="modal" data-bs-target="#addPurchaseModal">
                        <i class="fas fa-plus me-2"></i>فاتورة مشتريات جديدة
                    </button>
                </div>
                <div class="card-body p-0">
                    {% if purchases %}
                    <div class="table-responsive">
                        <table class="table table-hover mb-0" id="purchasesTable">
                            <thead class="table-dark">
                                <tr>
                                    <th class="p-3">رقم الفاتورة</th>
                                    <th class="p-3">المورد</th>
                                    <th class="p-3">التاريخ</th>
                                    <th class="p-3">المبلغ الفرعي</th>
                                    <th class="p-3">الضريبة</th>
                                    <th class="p-3">الإجمالي</th>
                                    <th class="p-3">الحالة</th>
                                    <th class="p-3">الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for purchase in purchases %}
                                <tr>
                                    <td class="p-3">
                                        <strong class="text-secondary">{{ purchase.invoice_number }}</strong>
                                    </td>
                                    <td class="p-3">
                                        <div>
                                            <strong>{{ purchase.supplier.name if purchase.supplier else 'مورد غير محدد' }}</strong>
                                            {% if purchase.supplier and purchase.supplier.phone %}
                                            <br><small class="text-muted">{{ purchase.supplier.phone }}</small>
                                            {% endif %}
                                        </div>
                                    </td>
                                    <td class="p-3">{{ purchase.date.strftime('%Y-%m-%d') }}</td>
                                    <td class="p-3">{{ "%.2f"|format(purchase.subtotal) }} ر.س</td>
                                    <td class="p-3">{{ "%.2f"|format(purchase.tax_amount) }} ر.س</td>
                                    <td class="p-3">
                                        <strong class="text-danger fs-6">{{ "%.2f"|format(purchase.total) }} ر.س</strong>
                                    </td>
                                    <td class="p-3">
                                        <span class="badge
                                        {% if purchase.status == 'paid' %}bg-success
                                        {% elif purchase.status == 'pending' %}bg-warning
                                        {% else %}bg-danger{% endif %}">
                                        {% if purchase.status == 'paid' %}مدفوعة
                                        {% elif purchase.status == 'pending' %}معلقة
                                        {% else %}ملغية{% endif %}
                                        </span>
                                    </td>
                                    <td class="p-3">
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-sm btn-outline-primary btn-action" title="عرض التفاصيل" onclick="viewPurchase({{ purchase.id }})">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-success btn-action" title="طباعة الفاتورة" onclick="printPurchase({{ purchase.id }})">
                                                <i class="fas fa-print"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-warning btn-action" title="تعديل" onclick="editPurchase({{ purchase.id }})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger btn-action" title="حذف" onclick="deletePurchase({{ purchase.id }}, '{{ purchase.invoice_number }}')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="fas fa-shopping-cart fa-4x text-muted mb-3"></i>
                            <h4 class="text-muted">لا توجد فواتير مشتريات</h4>
                            <p class="text-muted">ابدأ بإنشاء أول فاتورة مشتريات</p>
                        </div>
                        <button type="button" class="btn btn-secondary btn-lg" data-bs-toggle="modal" data-bs-target="#addPurchaseModal">
                            <i class="fas fa-plus me-2"></i>إنشاء فاتورة مشتريات جديدة
                        </button>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Modal إضافة فاتورة مشتريات -->
        <div class="modal fade" id="addPurchaseModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-secondary text-white">
                        <h5 class="modal-title fw-bold"><i class="fas fa-plus me-2"></i>فاتورة مشتريات جديدة</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_purchase') }}" id="purchaseInvoiceForm">
                        <div class="modal-body">
                            <!-- معلومات الفاتورة الأساسية -->
                            <div class="row mb-4">
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="purchase_invoice_number" class="form-label fw-bold">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" id="purchase_invoice_number" name="invoice_number"
                                               value="PUR-{{ format_date('%Y%m%d') }}-{{ zfill_number(purchases|length + 1, 3) }}" required>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="purchase_supplier_id" class="form-label fw-bold">المورد *</label>
                                        <select class="form-select" id="purchase_supplier_id" name="supplier_id" required>
                                            <option value="">اختر المورد</option>
                                            {% for supplier in suppliers %}
                                            <option value="{{ supplier.id }}">{{ supplier.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="purchase_payment_method" class="form-label fw-bold">طريقة الدفع *</label>
                                        <select class="form-select" id="purchase_payment_method" name="payment_method" required>
                                            <option value="cash">نقدي</option>
                                            <option value="mada">مدى</option>
                                            <option value="visa">فيزا</option>
                                            <option value="mastercard">ماستركارد</option>
                                            <option value="bank">تحويل بنكي</option>
                                            <option value="stc">STC Pay</option>
                                            <option value="gcc">GCC Pay</option>
                                            <option value="aks">أكس</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- إعدادات الضريبة -->
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="purchase_has_tax" name="has_tax" checked>
                                        <label class="form-check-label fw-bold" for="purchase_has_tax">
                                            تطبيق الضريبة على الفاتورة
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="purchase_tax_rate" class="form-label fw-bold">معدل الضريبة (%)</label>
                                        <input type="number" step="0.01" class="form-control" id="purchase_tax_rate" name="tax_rate" value="15" min="0" max="100">
                                    </div>
                                </div>
                            </div>

                            <!-- أصناف الفاتورة -->
                            <div class="mb-4">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h6 class="fw-bold text-secondary">
                                        <i class="fas fa-list me-2"></i>أصناف فاتورة المشتريات
                                    </h6>
                                    <button type="button" class="btn btn-sm btn-secondary" onclick="addPurchaseItem()">
                                        <i class="fas fa-plus me-1"></i>إضافة صنف
                                    </button>
                                </div>

                                <div class="table-responsive">
                                    <table class="table table-bordered" id="purchaseItemsTable">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="25%">اسم الصنف</th>
                                                <th width="20%">الوصف</th>
                                                <th width="15%">الكمية</th>
                                                <th width="15%">سعر الوحدة</th>
                                                <th width="15%">الإجمالي</th>
                                                <th width="10%">إجراءات</th>
                                            </tr>
                                        </thead>
                                        <tbody id="purchaseItemsBody">
                                            <tr class="purchase-item">
                                                <td>
                                                    <input type="text" class="form-control purchase-item-name" name="items[0][name]" placeholder="اسم الصنف" required>
                                                </td>
                                                <td>
                                                    <input type="text" class="form-control purchase-item-description" name="items[0][description]" placeholder="الوصف">
                                                </td>
                                                <td>
                                                    <input type="number" step="0.001" class="form-control purchase-item-quantity" name="items[0][quantity]" value="1" min="0.001" required>
                                                </td>
                                                <td>
                                                    <input type="number" step="0.01" class="form-control purchase-item-price" name="items[0][price]" value="0" min="0" required>
                                                </td>
                                                <td>
                                                    <input type="number" step="0.01" class="form-control purchase-item-total" name="items[0][total]" value="0" readonly>
                                                </td>
                                                <td>
                                                    <button type="button" class="btn btn-sm btn-danger" onclick="removePurchaseItem(this)">
                                                        <i class="fas fa-trash"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- ملخص الفاتورة -->
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="mb-3">
                                        <label for="purchase_notes" class="form-label fw-bold">ملاحظات</label>
                                        <textarea class="form-control" id="purchase_notes" name="notes" rows="2" placeholder="أي ملاحظات إضافية..."></textarea>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <h6 class="fw-bold text-secondary mb-3">ملخص فاتورة المشتريات</h6>
                                            <div class="d-flex justify-content-between mb-2">
                                                <span>المبلغ الفرعي:</span>
                                                <span id="purchase_invoice_subtotal">0.00 ر.س</span>
                                            </div>
                                            <div class="d-flex justify-content-between mb-2" id="purchase_tax_row">
                                                <span>الضريبة (<span id="purchase_tax_rate_display">15</span>%):</span>
                                                <span id="purchase_invoice_tax">0.00 ر.س</span>
                                            </div>
                                            <hr>
                                            <div class="d-flex justify-content-between fw-bold text-secondary">
                                                <span>الإجمالي:</span>
                                                <span id="purchase_invoice_total">0.00 ر.س</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- الحقول المخفية للإرسال -->
                            <input type="hidden" id="purchase_subtotal" name="subtotal" value="0">
                            <input type="hidden" id="purchase_tax_amount" name="tax_amount" value="0">
                            <input type="hidden" id="purchase_total" name="total" value="0">
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
            // وظائف إدارة فواتير المشتريات
            function viewPurchase(purchaseId) {
                alert('عرض تفاصيل فاتورة المشتريات رقم: ' + purchaseId);
                // يمكن إضافة modal لعرض التفاصيل
            }

            function editPurchase(purchaseId) {
                alert('تعديل فاتورة المشتريات رقم: ' + purchaseId);
                // يمكن إضافة modal للتعديل
            }

            function deletePurchase(purchaseId, invoiceNumber) {
                if (confirm('هل أنت متأكد من حذف فاتورة المشتريات: ' + invoiceNumber + '؟')) {
                    fetch('/delete_purchase/' + purchaseId, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم حذف فاتورة المشتريات بنجاح');
                            location.reload();
                        } else {
                            alert('حدث خطأ أثناء الحذف: ' + (data.message || 'خطأ غير معروف'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('حدث خطأ أثناء الحذف');
                    });
                }
            }

            function printPurchase(purchaseId) {
                window.open('/print_purchase/' + purchaseId, '_blank');
            }

            // إدارة أصناف فاتورة المشتريات
            let purchaseItemIndex = 1;

            function addPurchaseItem() {
                const tbody = document.getElementById('purchaseItemsBody');
                const newRow = document.createElement('tr');
                newRow.className = 'purchase-item';
                newRow.innerHTML = `
                    <td>
                        <input type="text" class="form-control purchase-item-name" name="items[${purchaseItemIndex}][name]" placeholder="اسم الصنف" required>
                    </td>
                    <td>
                        <input type="text" class="form-control purchase-item-description" name="items[${purchaseItemIndex}][description]" placeholder="الوصف">
                    </td>
                    <td>
                        <input type="number" step="0.001" class="form-control purchase-item-quantity" name="items[${purchaseItemIndex}][quantity]" value="1" min="0.001" required>
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control purchase-item-price" name="items[${purchaseItemIndex}][price]" value="0" min="0" required>
                    </td>
                    <td>
                        <input type="number" step="0.01" class="form-control purchase-item-total" name="items[${purchaseItemIndex}][total]" value="0" readonly>
                    </td>
                    <td>
                        <button type="button" class="btn btn-sm btn-danger" onclick="removePurchaseItem(this)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(newRow);
                purchaseItemIndex++;

                // إضافة event listeners للحقول الجديدة
                attachPurchaseItemEventListeners(newRow);
            }

            function removePurchaseItem(button) {
                const row = button.closest('tr');
                if (document.querySelectorAll('.purchase-item').length > 1) {
                    row.remove();
                    calculatePurchaseInvoiceTotal();
                } else {
                    alert('يجب أن تحتوي الفاتورة على صنف واحد على الأقل');
                }
            }

            function attachPurchaseItemEventListeners(row) {
                const quantityInput = row.querySelector('.purchase-item-quantity');
                const priceInput = row.querySelector('.purchase-item-price');
                const totalInput = row.querySelector('.purchase-item-total');

                function calculatePurchaseItemTotal() {
                    const quantity = parseFloat(quantityInput.value) || 0;
                    const price = parseFloat(priceInput.value) || 0;
                    const total = quantity * price;
                    totalInput.value = total.toFixed(2);
                    calculatePurchaseInvoiceTotal();
                }

                quantityInput.addEventListener('input', calculatePurchaseItemTotal);
                priceInput.addEventListener('input', calculatePurchaseItemTotal);
            }

            function calculatePurchaseInvoiceTotal() {
                let subtotal = 0;
                document.querySelectorAll('.purchase-item-total').forEach(input => {
                    subtotal += parseFloat(input.value) || 0;
                });

                const hasTax = document.getElementById('purchase_has_tax').checked;
                const taxRate = parseFloat(document.getElementById('purchase_tax_rate').value) || 0;
                const taxAmount = hasTax ? (subtotal * taxRate / 100) : 0;
                const total = subtotal + taxAmount;

                // تحديث العرض
                document.getElementById('purchase_invoice_subtotal').textContent = subtotal.toFixed(2) + ' ر.س';
                document.getElementById('purchase_invoice_tax').textContent = taxAmount.toFixed(2) + ' ر.س';
                document.getElementById('purchase_invoice_total').textContent = total.toFixed(2) + ' ر.س';
                document.getElementById('purchase_tax_rate_display').textContent = taxRate;

                // تحديث الحقول المخفية
                document.getElementById('purchase_subtotal').value = subtotal.toFixed(2);
                document.getElementById('purchase_tax_amount').value = taxAmount.toFixed(2);
                document.getElementById('purchase_total').value = total.toFixed(2);

                // إظهار/إخفاء صف الضريبة
                document.getElementById('purchase_tax_row').style.display = hasTax ? 'flex' : 'none';
            }

            // تهيئة الصفحة
            document.addEventListener('DOMContentLoaded', function() {

                // إضافة event listeners للصف الأول
                const firstPurchaseRow = document.querySelector('.purchase-item');
                if (firstPurchaseRow) {
                    attachPurchaseItemEventListeners(firstPurchaseRow);
                }

                // event listeners لإعدادات الضريبة
                document.getElementById('purchase_has_tax').addEventListener('change', calculatePurchaseInvoiceTotal);
                document.getElementById('purchase_tax_rate').addEventListener('input', calculatePurchaseInvoiceTotal);

                // تحسين تجربة المستخدم
                const cards = document.querySelectorAll('.stat-card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-10px)';
                    });

                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });

                // تحسين النموذج
                const purchaseForm = document.getElementById('purchaseInvoiceForm');
                if (purchaseForm) {
                    purchaseForm.addEventListener('submit', function(e) {
                        const items = document.querySelectorAll('.purchase-item');
                        let hasValidItems = false;

                        items.forEach(item => {
                            const name = item.querySelector('.purchase-item-name').value.trim();
                            const quantity = parseFloat(item.querySelector('.purchase-item-quantity').value);
                            const price = parseFloat(item.querySelector('.purchase-item-price').value);

                            if (name && quantity > 0 && price >= 0) {
                                hasValidItems = true;
                            }
                        });

                        if (!hasValidItems) {
                            e.preventDefault();
                            alert('يجب إضافة صنف واحد صحيح على الأقل');
                            return false;
                        }
                    });
                }
            });
        </script>
    </body>
    </html>
    ''', purchases=purchases, suppliers=suppliers, total_purchases=total_purchases)

@app.route('/add_purchase', methods=['POST'])
@login_required
def add_purchase():
    try:
        # إنشاء فاتورة المشتريات
        purchase = PurchaseInvoice(
            invoice_number=request.form['invoice_number'],
            supplier_id=int(request.form['supplier_id']),
            subtotal=float(request.form['subtotal']),
            tax_amount=float(request.form.get('tax_amount', 0)),
            tax_rate=float(request.form.get('tax_rate', 15)),
            has_tax=bool(request.form.get('has_tax')),
            total=float(request.form.get('total', 0)),
            payment_method=request.form.get('payment_method', 'cash'),
            notes=request.form.get('notes'),
            status='pending'
        )
        db.session.add(purchase)
        db.session.flush()  # للحصول على ID الفاتورة

        # إضافة أصناف فاتورة المشتريات
        items_data = {}
        for key, value in request.form.items():
            if key.startswith('items[') and '][' in key:
                # استخراج الفهرس والحقل من اسم الحقل
                parts = key.split('][')
                index = parts[0].split('[')[1]
                field = parts[1].rstrip(']')

                if index not in items_data:
                    items_data[index] = {}
                items_data[index][field] = value

        # إنشاء أصناف فاتورة المشتريات
        for index, item_data in items_data.items():
            if item_data.get('name') and item_data.get('quantity') and item_data.get('price'):
                quantity = float(item_data['quantity'])
                price = float(item_data['price'])
                total_price = quantity * price

                item = PurchaseInvoiceItem(
                    invoice_id=purchase.id,
                    product_name=item_data['name'],
                    description=item_data.get('description', ''),
                    quantity=quantity,
                    unit_price=price,
                    total_price=total_price
                )
                db.session.add(item)

        db.session.commit()
        flash('تم إنشاء فاتورة المشتريات بنجاح', 'success')
        return redirect(url_for('purchases'))

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إنشاء فاتورة المشتريات: {str(e)}', 'error')
        return redirect(url_for('purchases'))

@app.route('/delete_purchase/<int:purchase_id>', methods=['DELETE'])
@login_required
def delete_purchase(purchase_id):
    try:
        purchase = PurchaseInvoice.query.get_or_404(purchase_id)
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف فاتورة المشتريات بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# وظائف إدارة الموظفين المتقدمة
@app.route('/view_employee/<int:employee_id>')
@login_required
def view_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    payrolls = EmployeePayroll.query.filter_by(employee_id=employee_id).order_by(EmployeePayroll.year.desc(), EmployeePayroll.month.desc()).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>ملف الموظف - {{ employee.name }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .employee-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: none;
                overflow: hidden;
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
                    <a class="nav-link" href="{{ url_for('employees') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للموظفين
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-primary">
                    <i class="fas fa-user me-3"></i>ملف الموظف
                </h1>
            </div>

            <!-- معلومات الموظف -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="employee-card p-4">
                        <div class="row">
                            <div class="col-md-6">
                                <h5 class="fw-bold text-primary mb-3">المعلومات الشخصية</h5>
                                <p><strong>الاسم:</strong> {{ employee.name }}</p>
                                <p><strong>المنصب:</strong> {{ employee.position }}</p>
                                <p><strong>الهاتف:</strong> {{ employee.phone or '-' }}</p>
                                <p><strong>البريد الإلكتروني:</strong> {{ employee.email or '-' }}</p>
                                <p><strong>تاريخ التوظيف:</strong> {{ employee.hire_date.strftime('%Y-%m-%d') }}</p>
                                <p><strong>الحالة:</strong>
                                    <span class="badge {% if employee.status == 'active' %}bg-success{% else %}bg-danger{% endif %}">
                                        {{ 'نشط' if employee.status == 'active' else 'غير نشط' }}
                                    </span>
                                </p>
                            </div>
                            <div class="col-md-6">
                                <h5 class="fw-bold text-success mb-3">معلومات الراتب</h5>
                                <p><strong>الراتب الأساسي:</strong> {{ "%.2f"|format(employee.salary) }} ر.س</p>
                                <p><strong>أيام العمل:</strong> {{ employee.working_days or 30 }} يوم</p>
                                <p><strong>معدل الساعة الإضافية:</strong> {{ "%.2f"|format(employee.overtime_rate or 0) }} ر.س</p>
                                <p><strong>البدلات:</strong> {{ "%.2f"|format(employee.allowances or 0) }} ر.س</p>
                                <p><strong>الاستقطاعات:</strong> {{ "%.2f"|format(employee.deductions or 0) }} ر.س</p>
                                <p><strong>صافي الراتب:</strong>
                                    <span class="fw-bold text-success">
                                        {{ "%.2f"|format((employee.salary or 0) + (employee.allowances or 0) - (employee.deductions or 0)) }} ر.س
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="employee-card p-4 text-center">
                        <div class="avatar-circle bg-primary text-white mx-auto mb-3" style="width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
                            {{ employee.name[0].upper() }}
                        </div>
                        <h5 class="fw-bold">{{ employee.name }}</h5>
                        <p class="text-muted">{{ employee.position }}</p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-success" onclick="generatePayroll({{ employee.id }})">
                                <i class="fas fa-money-check me-2"></i>إنشاء كشف راتب
                            </button>
                            <button class="btn btn-warning" onclick="editEmployee({{ employee.id }})">
                                <i class="fas fa-edit me-2"></i>تعديل البيانات
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- كشوف الرواتب السابقة -->
            {% if payrolls %}
            <div class="employee-card">
                <div class="card-header bg-info text-white p-4">
                    <h5 class="mb-0 fw-bold">
                        <i class="fas fa-history me-2"></i>كشوف الرواتب السابقة
                    </h5>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="table-dark">
                                <tr>
                                    <th>الشهر/السنة</th>
                                    <th>الراتب الأساسي</th>
                                    <th>الساعات الإضافية</th>
                                    <th>البدلات</th>
                                    <th>الاستقطاعات</th>
                                    <th>صافي الراتب</th>
                                    <th>الحالة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for payroll in payrolls %}
                                <tr>
                                    <td>{{ payroll.month }}/{{ payroll.year }}</td>
                                    <td>{{ "%.2f"|format(payroll.basic_salary) }} ر.س</td>
                                    <td>{{ "%.2f"|format(payroll.overtime_amount) }} ر.س</td>
                                    <td>{{ "%.2f"|format(payroll.allowances) }} ر.س</td>
                                    <td>{{ "%.2f"|format(payroll.deductions) }} ر.س</td>
                                    <td class="fw-bold text-success">{{ "%.2f"|format(payroll.net_salary) }} ر.س</td>
                                    <td>
                                        <span class="badge {% if payroll.status == 'paid' %}bg-success{% else %}bg-warning{% endif %}">
                                            {{ 'مدفوع' if payroll.status == 'paid' else 'معلق' }}
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function generatePayroll(employeeId) {
                window.location.href = '/generate_payroll/' + employeeId;
            }

            function editEmployee(employeeId) {
                window.location.href = '/edit_employee/' + employeeId;
            }
        </script>
    </body>
    </html>
    ''', employee=employee, payrolls=payrolls)

@app.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الموظف بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/generate_payroll/<int:employee_id>')
@login_required
def generate_payroll(employee_id):
    from datetime import datetime
    employee = Employee.query.get_or_404(employee_id)
    current_month = datetime.now().month
    current_year = datetime.now().year

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إنشاء كشف راتب - {{ employee.name }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .payroll-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: none;
                overflow: hidden;
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
                    <a class="nav-link" href="{{ url_for('view_employee', employee_id=employee.id) }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع لملف الموظف
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-success">
                    <i class="fas fa-money-check me-3"></i>إنشاء كشف راتب
                </h1>
                <p class="lead text-muted">{{ employee.name }} - {{ employee.position }}</p>
            </div>

            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="payroll-card">
                        <div class="card-header bg-success text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-calendar me-2"></i>بيانات كشف الراتب
                            </h5>
                        </div>
                        <div class="card-body p-4">
                            <form method="POST" action="{{ url_for('save_payroll') }}">
                                <input type="hidden" name="employee_id" value="{{ employee.id }}">

                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">الشهر</label>
                                        <select class="form-select" name="month" required>
                                            {% for i in range(1, 13) %}
                                            <option value="{{ i }}" {% if i == current_month %}selected{% endif %}>
                                                {% if i == 1 %}يناير{% elif i == 2 %}فبراير{% elif i == 3 %}مارس{% elif i == 4 %}أبريل{% elif i == 5 %}مايو{% elif i == 6 %}يونيو{% elif i == 7 %}يوليو{% elif i == 8 %}أغسطس{% elif i == 9 %}سبتمبر{% elif i == 10 %}أكتوبر{% elif i == 11 %}نوفمبر{% else %}ديسمبر{% endif %}
                                            </option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">السنة</label>
                                        <input type="number" class="form-control" name="year" value="{{ current_year }}" min="2020" max="2030" required>
                                    </div>
                                </div>

                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">الراتب الأساسي</label>
                                        <input type="number" step="0.01" class="form-control" name="basic_salary" value="{{ employee.salary }}" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">أيام العمل الفعلية</label>
                                        <input type="number" class="form-control" name="actual_working_days" value="{{ employee.working_days or 30 }}" min="1" max="31" required>
                                    </div>
                                </div>

                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">الساعات الإضافية</label>
                                        <input type="number" step="0.01" class="form-control" name="overtime_hours" value="0" min="0" id="overtime_hours">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">مبلغ الساعات الإضافية</label>
                                        <input type="number" step="0.01" class="form-control" name="overtime_amount" value="0" readonly id="overtime_amount">
                                    </div>
                                </div>

                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">البدلات</label>
                                        <input type="number" step="0.01" class="form-control" name="allowances" value="{{ employee.allowances or 0 }}">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">الاستقطاعات</label>
                                        <input type="number" step="0.01" class="form-control" name="deductions" value="{{ employee.deductions or 0 }}">
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label class="form-label fw-bold">ملاحظات</label>
                                    <textarea class="form-control" name="notes" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                                </div>

                                <div class="card bg-light p-3 mb-4">
                                    <h6 class="fw-bold text-success mb-3">ملخص كشف الراتب</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <p>الراتب الأساسي: <span id="display_basic">{{ "%.2f"|format(employee.salary) }}</span> ر.س</p>
                                            <p>الساعات الإضافية: <span id="display_overtime">0.00</span> ر.س</p>
                                            <p>البدلات: <span id="display_allowances">{{ "%.2f"|format(employee.allowances or 0) }}</span> ر.س</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p>الاستقطاعات: <span id="display_deductions">{{ "%.2f"|format(employee.deductions or 0) }}</span> ر.س</p>
                                            <p class="fw-bold text-success">صافي الراتب: <span id="display_net">{{ "%.2f"|format(employee.salary + (employee.allowances or 0) - (employee.deductions or 0)) }}</span> ر.س</p>
                                        </div>
                                    </div>
                                </div>

                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <button type="button" class="btn btn-secondary" onclick="history.back()">
                                        <i class="fas fa-times me-2"></i>إلغاء
                                    </button>
                                    <button type="submit" class="btn btn-success">
                                        <i class="fas fa-save me-2"></i>حفظ كشف الراتب
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // حساب الساعات الإضافية تلقائياً
            document.getElementById('overtime_hours').addEventListener('input', function() {
                const hours = parseFloat(this.value) || 0;
                const rate = {{ employee.overtime_rate or 0 }};
                const amount = hours * rate;
                document.getElementById('overtime_amount').value = amount.toFixed(2);
                document.getElementById('display_overtime').textContent = amount.toFixed(2);
                calculateNetSalary();
            });

            // حساب صافي الراتب
            function calculateNetSalary() {
                const basic = parseFloat(document.querySelector('[name="basic_salary"]').value) || 0;
                const overtime = parseFloat(document.getElementById('overtime_amount').value) || 0;
                const allowances = parseFloat(document.querySelector('[name="allowances"]').value) || 0;
                const deductions = parseFloat(document.querySelector('[name="deductions"]').value) || 0;

                const net = basic + overtime + allowances - deductions;

                document.getElementById('display_basic').textContent = basic.toFixed(2);
                document.getElementById('display_allowances').textContent = allowances.toFixed(2);
                document.getElementById('display_deductions').textContent = deductions.toFixed(2);
                document.getElementById('display_net').textContent = net.toFixed(2);
            }

            // إضافة event listeners للحقول
            document.querySelector('[name="basic_salary"]').addEventListener('input', calculateNetSalary);
            document.querySelector('[name="allowances"]').addEventListener('input', calculateNetSalary);
            document.querySelector('[name="deductions"]').addEventListener('input', calculateNetSalary);
        </script>
    </body>
    </html>
    ''', employee=employee, current_month=current_month, current_year=current_year)

@app.route('/save_payroll', methods=['POST'])
@login_required
def save_payroll():
    try:
        employee_id = int(request.form['employee_id'])
        month = int(request.form['month'])
        year = int(request.form['year'])

        # التحقق من عدم وجود كشف راتب لنفس الشهر والسنة
        existing_payroll = EmployeePayroll.query.filter_by(
            employee_id=employee_id,
            month=month,
            year=year
        ).first()

        if existing_payroll:
            flash('يوجد كشف راتب لهذا الموظف في نفس الشهر والسنة', 'error')
            return redirect(url_for('generate_payroll', employee_id=employee_id))

        # حساب المبالغ
        basic_salary = float(request.form['basic_salary'])
        overtime_hours = float(request.form.get('overtime_hours', 0))
        overtime_amount = float(request.form.get('overtime_amount', 0))
        allowances = float(request.form.get('allowances', 0))
        deductions = float(request.form.get('deductions', 0))

        gross_salary = basic_salary + overtime_amount + allowances
        net_salary = gross_salary - deductions

        # إنشاء كشف الراتب
        payroll = EmployeePayroll(
            employee_id=employee_id,
            month=month,
            year=year,
            basic_salary=basic_salary,
            working_days=int(request.form.get('working_days', 30)),
            actual_working_days=int(request.form['actual_working_days']),
            overtime_hours=overtime_hours,
            overtime_amount=overtime_amount,
            allowances=allowances,
            deductions=deductions,
            gross_salary=gross_salary,
            net_salary=net_salary,
            notes=request.form.get('notes'),
            status='pending'
        )

        db.session.add(payroll)
        db.session.commit()

        flash('تم إنشاء كشف الراتب بنجاح', 'success')
        return redirect(url_for('view_employee', employee_id=employee_id))

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إنشاء كشف الراتب: {str(e)}', 'error')
        return redirect(url_for('generate_payroll', employee_id=request.form.get('employee_id', 1)))

# تقرير الموظفين التفصيلي
@app.route('/employees_report')
@login_required
def employees_report():
    from sqlalchemy import func

    employees = Employee.query.all()
    total_employees = len(employees)
    active_employees = len([e for e in employees if e.status == 'active'])
    total_salaries = sum(e.salary for e in employees if e.status == 'active')
    total_allowances = sum(e.allowances or 0 for e in employees if e.status == 'active')
    total_deductions = sum(e.deductions or 0 for e in employees if e.status == 'active')

    # الموظفين حسب المنصب
    positions = {}
    for employee in employees:
        if employee.position not in positions:
            positions[employee.position] = []
        positions[employee.position].append(employee)

    # كشوف الرواتب الحديثة
    recent_payrolls = EmployeePayroll.query.order_by(EmployeePayroll.created_at.desc()).limit(10).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير الموظفين التفصيلي - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            .chart-container {
                position: relative;
                height: 400px;
                margin: 20px 0;
            }
            @media print {
                .no-print { display: none !important; }
                body { background: white !important; }
                .stat-card { box-shadow: none !important; border: 1px solid #ddd !important; }
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark no-print">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                <div class="navbar-nav ms-auto">
                    <button class="btn btn-light me-2" onclick="window.print()">
                        <i class="fas fa-print me-1"></i>طباعة
                    </button>
                    <div class="dropdown me-2">
                        <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-filter me-1"></i>فلترة
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="?status=active">الموظفين النشطين</a></li>
                            <li><a class="dropdown-item" href="?status=inactive">الموظفين غير النشطين</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('employees_report') }}">جميع الموظفين</a></li>
                        </ul>
                    </div>
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-primary">
                    <i class="fas fa-users me-3"></i>تقرير الموظفين التفصيلي
                </h1>
                <p class="lead text-muted">تحليل شامل لجميع موظفي الشركة ورواتبهم</p>
            </div>

            <!-- الإحصائيات الرئيسية -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-users fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-primary">{{ total_employees }}</h3>
                        <p class="text-muted mb-0">إجمالي الموظفين</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-user-check fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ active_employees }}</h3>
                        <p class="text-muted mb-0">الموظفين النشطين</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-money-bill-wave fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-warning">{{ "%.2f"|format(total_salaries) }}</h3>
                        <p class="text-muted mb-0">إجمالي الرواتب (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-calculator fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ "%.2f"|format(total_salaries + total_allowances - total_deductions) }}</h3>
                        <p class="text-muted mb-0">صافي الرواتب (ر.س)</p>
                    </div>
                </div>
            </div>

            <!-- الرسوم البيانية -->
            <div class="row g-4 mb-5">
                <div class="col-md-6">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-pie me-2"></i>الموظفين حسب المنصب
                        </h5>
                        <div class="chart-container">
                            <canvas id="positionsChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-bar me-2"></i>توزيع الرواتب
                        </h5>
                        <div class="chart-container">
                            <canvas id="salariesChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تفاصيل الموظفين -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-primary text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-list me-2"></i>تفاصيل جميع الموظفين
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>الاسم</th>
                                            <th>المنصب</th>
                                            <th>تاريخ التوظيف</th>
                                            <th>الراتب الأساسي</th>
                                            <th>البدلات</th>
                                            <th>الاستقطاعات</th>
                                            <th>صافي الراتب</th>
                                            <th>الحالة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for employee in employees %}
                                        <tr>
                                            <td>
                                                <div class="d-flex align-items-center">
                                                    <div class="avatar-circle bg-primary text-white me-2" style="width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">
                                                        {{ employee.name[0].upper() }}
                                                    </div>
                                                    <strong>{{ employee.name }}</strong>
                                                </div>
                                            </td>
                                            <td>
                                                <span class="badge bg-info">{{ employee.position }}</span>
                                            </td>
                                            <td>{{ employee.hire_date.strftime('%Y-%m-%d') }}</td>
                                            <td class="fw-bold text-primary">{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                            <td class="text-success">
                                                {% if employee.allowances and employee.allowances > 0 %}
                                                {{ "%.2f"|format(employee.allowances) }} ر.س
                                                {% else %}
                                                -
                                                {% endif %}
                                            </td>
                                            <td class="text-danger">
                                                {% if employee.deductions and employee.deductions > 0 %}
                                                {{ "%.2f"|format(employee.deductions) }} ر.س
                                                {% else %}
                                                -
                                                {% endif %}
                                            </td>
                                            <td class="fw-bold text-success">
                                                {{ "%.2f"|format((employee.salary or 0) + (employee.allowances or 0) - (employee.deductions or 0)) }} ر.س
                                            </td>
                                            <td>
                                                {% if employee.status == 'active' %}
                                                <span class="badge bg-success">نشط</span>
                                                {% else %}
                                                <span class="badge bg-danger">غير نشط</span>
                                                {% endif %}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- كشوف الرواتب الحديثة -->
            {% if recent_payrolls %}
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-success text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-history me-2"></i>كشوف الرواتب الحديثة
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>الموظف</th>
                                            <th>الشهر/السنة</th>
                                            <th>الراتب الأساسي</th>
                                            <th>الساعات الإضافية</th>
                                            <th>صافي الراتب</th>
                                            <th>الحالة</th>
                                            <th>تاريخ الإنشاء</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for payroll in recent_payrolls %}
                                        <tr>
                                            <td><strong>{{ payroll.employee.name }}</strong></td>
                                            <td>{{ payroll.month }}/{{ payroll.year }}</td>
                                            <td>{{ "%.2f"|format(payroll.basic_salary) }} ر.س</td>
                                            <td>{{ "%.2f"|format(payroll.overtime_amount) }} ر.س</td>
                                            <td class="fw-bold text-success">{{ "%.2f"|format(payroll.net_salary) }} ر.س</td>
                                            <td>
                                                <span class="badge {% if payroll.status == 'paid' %}bg-success{% else %}bg-warning{% endif %}">
                                                    {{ 'مدفوع' if payroll.status == 'paid' else 'معلق' }}
                                                </span>
                                            </td>
                                            <td>{{ payroll.created_at.strftime('%Y-%m-%d') }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // رسم بياني للمناصب
            const positionsCtx = document.getElementById('positionsChart').getContext('2d');
            new Chart(positionsCtx, {
                type: 'doughnut',
                data: {
                    labels: [
                        {% for position, emps in positions.items() %}
                        '{{ position }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        data: [
                            {% for position, emps in positions.items() %}
                            {{ emps|length }}{{ ',' if not loop.last }}
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
                    maintainAspectRatio: false
                }
            });

            // رسم بياني للرواتب
            const salariesCtx = document.getElementById('salariesChart').getContext('2d');
            new Chart(salariesCtx, {
                type: 'bar',
                data: {
                    labels: [
                        {% for employee in employees[:10] %}
                        '{{ employee.name[:15] }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        label: 'صافي الراتب (ر.س)',
                        data: [
                            {% for employee in employees[:10] %}
                            {{ (employee.salary or 0) + (employee.allowances or 0) - (employee.deductions or 0) }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        backgroundColor: '#36A2EB'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        </script>
    </body>
    </html>
    ''', employees=employees, total_employees=total_employees, active_employees=active_employees,
         total_salaries=total_salaries, total_allowances=total_allowances, total_deductions=total_deductions,
         positions=positions, recent_payrolls=recent_payrolls)

# نظام طباعة الفواتير الاحترافي
@app.route('/print_invoice/<int:sale_id>')
@login_required
def print_invoice(sale_id):
    sale = SalesInvoice.query.get_or_404(sale_id)
    items = SalesInvoiceItem.query.filter_by(invoice_id=sale_id).all()

    # معلومات الشركة (يمكن تخصيصها)
    company_info = {
        'name': 'شركة المحاسبة الاحترافية',
        'tax_number': '123456789012345',
        'address': 'الرياض، المملكة العربية السعودية',
        'phone': '+966 11 123 4567',
        'email': 'info@company.com'
    }

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة مبيعات - {{ sale.invoice_number }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <style>
            @media print {
                .no-print { display: none !important; }
                body { margin: 0; padding: 20px; }
                .invoice-container { box-shadow: none !important; }
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }

            .invoice-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                padding: 30px;
                margin: 20px auto;
                max-width: 800px;
            }

            .company-header {
                border-bottom: 3px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }

            .invoice-title {
                background: linear-gradient(45deg, #007bff, #0056b3);
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }

            .info-section {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }

            .items-table {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                overflow: hidden;
            }

            .items-table th {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                text-align: center;
                padding: 12px;
            }

            .items-table td {
                padding: 10px;
                border-bottom: 1px solid #dee2e6;
            }

            .totals-section {
                background-color: #e3f2fd;
                padding: 20px;
                border-radius: 8px;
                border: 2px solid #2196f3;
            }

            .payment-method-badge {
                display: inline-block;
                padding: 8px 15px;
                border-radius: 20px;
                font-weight: bold;
                color: white;
            }

            .qr-code {
                width: 100px;
                height: 100px;
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <!-- رأس الشركة -->
            <div class="company-header">
                <div class="row">
                    <div class="col-md-8">
                        <h2 class="fw-bold text-primary mb-2">{{ company_info.name }}</h2>
                        <p class="mb-1"><i class="fas fa-map-marker-alt me-2"></i>{{ company_info.address }}</p>
                        <p class="mb-1"><i class="fas fa-phone me-2"></i>{{ company_info.phone }}</p>
                        <p class="mb-1"><i class="fas fa-envelope me-2"></i>{{ company_info.email }}</p>
                        <p class="mb-0"><strong>الرقم الضريبي:</strong> {{ company_info.tax_number }}</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="qr-code">
                            رمز QR
                        </div>
                    </div>
                </div>
            </div>

            <!-- عنوان الفاتورة -->
            <div class="invoice-title">
                <h3 class="mb-0">فاتورة مبيعات</h3>
                <h4 class="mb-0">{{ sale.invoice_number }}</h4>
            </div>

            <!-- معلومات الفاتورة والعميل -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="info-section">
                        <h6 class="fw-bold text-primary mb-3">معلومات الفاتورة</h6>
                        <p class="mb-2"><strong>رقم الفاتورة:</strong> {{ sale.invoice_number }}</p>
                        <p class="mb-2"><strong>التاريخ:</strong> {{ sale.date.strftime('%Y-%m-%d') }}</p>
                        <p class="mb-2"><strong>طريقة الدفع:</strong>
                            <span class="payment-method-badge" style="background-color:
                                {% if sale.payment_method == 'cash' %}#28a745
                                {% elif sale.payment_method == 'mada' %}#6f42c1
                                {% elif sale.payment_method == 'visa' %}#007bff
                                {% elif sale.payment_method == 'mastercard' %}#dc3545
                                {% elif sale.payment_method == 'stc' %}#20c997
                                {% elif sale.payment_method == 'gcc' %}#fd7e14
                                {% else %}#6c757d{% endif %};">
                                {% if sale.payment_method == 'cash' %}نقدي
                                {% elif sale.payment_method == 'mada' %}مدى
                                {% elif sale.payment_method == 'visa' %}فيزا
                                {% elif sale.payment_method == 'mastercard' %}ماستركارد
                                {% elif sale.payment_method == 'stc' %}STC Pay
                                {% elif sale.payment_method == 'gcc' %}GCC Pay
                                {% elif sale.payment_method == 'aks' %}أكس
                                {% elif sale.payment_method == 'bank' %}تحويل بنكي
                                {% else %}{{ sale.payment_method }}{% endif %}
                            </span>
                        </p>
                        <p class="mb-0"><strong>الحالة:</strong>
                            <span class="badge {% if sale.status == 'paid' %}bg-success{% elif sale.status == 'pending' %}bg-warning{% else %}bg-danger{% endif %}">
                                {% if sale.status == 'paid' %}مدفوعة{% elif sale.status == 'pending' %}معلقة{% else %}ملغية{% endif %}
                            </span>
                        </p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-section">
                        <h6 class="fw-bold text-success mb-3">معلومات العميل</h6>
                        {% if sale.customer %}
                        <p class="mb-2"><strong>اسم العميل:</strong> {{ sale.customer.name }}</p>
                        <p class="mb-2"><strong>الهاتف:</strong> {{ sale.customer.phone or '-' }}</p>
                        <p class="mb-2"><strong>البريد الإلكتروني:</strong> {{ sale.customer.email or '-' }}</p>
                        <p class="mb-0"><strong>العنوان:</strong> {{ sale.customer.address or '-' }}</p>
                        {% else %}
                        <p class="mb-0 text-muted">عميل نقدي</p>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- أصناف الفاتورة -->
            <div class="mb-4">
                <h6 class="fw-bold text-dark mb-3">تفاصيل الأصناف</h6>
                <table class="table items-table mb-0">
                    <thead>
                        <tr>
                            <th width="5%">#</th>
                            <th width="30%">اسم الصنف</th>
                            <th width="25%">الوصف</th>
                            <th width="10%">الكمية</th>
                            <th width="15%">سعر الوحدة</th>
                            <th width="15%">الإجمالي</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td class="text-center">{{ loop.index }}</td>
                            <td><strong>{{ item.product_name }}</strong></td>
                            <td>{{ item.description or '-' }}</td>
                            <td class="text-center">{{ "%.3f"|format(item.quantity) }}</td>
                            <td class="text-end">{{ "%.2f"|format(item.unit_price) }} ر.س</td>
                            <td class="text-end fw-bold">{{ "%.2f"|format(item.total_price) }} ر.س</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <!-- ملخص المبالغ -->
            <div class="row">
                <div class="col-md-6">
                    {% if sale.notes %}
                    <div class="info-section">
                        <h6 class="fw-bold text-secondary mb-2">ملاحظات</h6>
                        <p class="mb-0">{{ sale.notes }}</p>
                    </div>
                    {% endif %}
                </div>
                <div class="col-md-6">
                    <div class="totals-section">
                        <div class="d-flex justify-content-between mb-2">
                            <span>المبلغ الفرعي:</span>
                            <span class="fw-bold">{{ "%.2f"|format(sale.subtotal) }} ر.س</span>
                        </div>
                        {% if sale.has_tax %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>الضريبة ({{ "%.1f"|format(sale.tax_rate) }}%):</span>
                            <span class="fw-bold">{{ "%.2f"|format(sale.tax_amount) }} ر.س</span>
                        </div>
                        {% endif %}
                        <hr class="my-2">
                        <div class="d-flex justify-content-between">
                            <span class="fs-5 fw-bold">الإجمالي:</span>
                            <span class="fs-4 fw-bold text-primary">{{ "%.2f"|format(sale.total) }} ر.س</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تذييل الفاتورة -->
            <div class="text-center mt-4 pt-4 border-top">
                <p class="text-muted mb-2">شكراً لتعاملكم معنا</p>
                <p class="small text-muted mb-0">هذه فاتورة إلكترونية صادرة من نظام المحاسبة الاحترافي</p>
            </div>

            <!-- أزرار الطباعة -->
            <div class="text-center mt-4 no-print">
                <button class="btn btn-primary btn-lg me-2" onclick="window.print()">
                    <i class="fas fa-print me-2"></i>طباعة الفاتورة
                </button>
                <button class="btn btn-secondary btn-lg" onclick="window.close()">
                    <i class="fas fa-times me-2"></i>إغلاق
                </button>
            </div>
        </div>

        <script>
            // طباعة تلقائية عند فتح الصفحة
            window.onload = function() {
                // يمكن تفعيل الطباعة التلقائية إذا رغبت
                // window.print();
            }
        </script>
    </body>
    </html>
    ''', sale=sale, items=items, company_info=company_info)

@app.route('/print_purchase/<int:purchase_id>')
@login_required
def print_purchase(purchase_id):
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    items = PurchaseInvoiceItem.query.filter_by(invoice_id=purchase_id).all()

    # معلومات الشركة
    company_info = {
        'name': 'شركة المحاسبة الاحترافية',
        'tax_number': '123456789012345',
        'address': 'الرياض، المملكة العربية السعودية',
        'phone': '+966 11 123 4567',
        'email': 'info@company.com'
    }

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة مشتريات - {{ purchase.invoice_number }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <style>
            @media print {
                .no-print { display: none !important; }
                body { margin: 0; padding: 20px; }
                .invoice-container { box-shadow: none !important; }
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }

            .invoice-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                padding: 30px;
                margin: 20px auto;
                max-width: 800px;
            }

            .company-header {
                border-bottom: 3px solid #6c757d;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }

            .invoice-title {
                background: linear-gradient(45deg, #6c757d, #495057);
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }

            .info-section {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }

            .items-table {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                overflow: hidden;
            }

            .items-table th {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                text-align: center;
                padding: 12px;
            }

            .items-table td {
                padding: 10px;
                border-bottom: 1px solid #dee2e6;
            }

            .totals-section {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border: 2px solid #6c757d;
            }
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <!-- رأس الشركة -->
            <div class="company-header">
                <div class="row">
                    <div class="col-md-8">
                        <h2 class="fw-bold text-secondary mb-2">{{ company_info.name }}</h2>
                        <p class="mb-1"><i class="fas fa-map-marker-alt me-2"></i>{{ company_info.address }}</p>
                        <p class="mb-1"><i class="fas fa-phone me-2"></i>{{ company_info.phone }}</p>
                        <p class="mb-1"><i class="fas fa-envelope me-2"></i>{{ company_info.email }}</p>
                        <p class="mb-0"><strong>الرقم الضريبي:</strong> {{ company_info.tax_number }}</p>
                    </div>
                </div>
            </div>

            <!-- عنوان الفاتورة -->
            <div class="invoice-title">
                <h3 class="mb-0">فاتورة مشتريات</h3>
                <h4 class="mb-0">{{ purchase.invoice_number }}</h4>
            </div>

            <!-- معلومات الفاتورة والمورد -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="info-section">
                        <h6 class="fw-bold text-secondary mb-3">معلومات الفاتورة</h6>
                        <p class="mb-2"><strong>رقم الفاتورة:</strong> {{ purchase.invoice_number }}</p>
                        <p class="mb-2"><strong>التاريخ:</strong> {{ purchase.date.strftime('%Y-%m-%d') }}</p>
                        <p class="mb-2"><strong>طريقة الدفع:</strong>
                            <span class="badge bg-secondary">
                                {% if purchase.payment_method == 'cash' %}نقدي
                                {% elif purchase.payment_method == 'mada' %}مدى
                                {% elif purchase.payment_method == 'visa' %}فيزا
                                {% elif purchase.payment_method == 'mastercard' %}ماستركارد
                                {% elif purchase.payment_method == 'stc' %}STC Pay
                                {% elif purchase.payment_method == 'gcc' %}GCC Pay
                                {% elif purchase.payment_method == 'aks' %}أكس
                                {% elif purchase.payment_method == 'bank' %}تحويل بنكي
                                {% else %}{{ purchase.payment_method }}{% endif %}
                            </span>
                        </p>
                        <p class="mb-0"><strong>الحالة:</strong>
                            <span class="badge {% if purchase.status == 'paid' %}bg-success{% elif purchase.status == 'pending' %}bg-warning{% else %}bg-danger{% endif %}">
                                {% if purchase.status == 'paid' %}مدفوعة{% elif purchase.status == 'pending' %}معلقة{% else %}ملغية{% endif %}
                            </span>
                        </p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-section">
                        <h6 class="fw-bold text-info mb-3">معلومات المورد</h6>
                        <p class="mb-2"><strong>اسم المورد:</strong> {{ purchase.supplier.name }}</p>
                        <p class="mb-2"><strong>الهاتف:</strong> {{ purchase.supplier.phone or '-' }}</p>
                        <p class="mb-2"><strong>البريد الإلكتروني:</strong> {{ purchase.supplier.email or '-' }}</p>
                        <p class="mb-0"><strong>العنوان:</strong> {{ purchase.supplier.address or '-' }}</p>
                    </div>
                </div>
            </div>

            <!-- أصناف الفاتورة -->
            <div class="mb-4">
                <h6 class="fw-bold text-dark mb-3">تفاصيل الأصناف</h6>
                <table class="table items-table mb-0">
                    <thead>
                        <tr>
                            <th width="5%">#</th>
                            <th width="30%">اسم الصنف</th>
                            <th width="25%">الوصف</th>
                            <th width="10%">الكمية</th>
                            <th width="15%">سعر الوحدة</th>
                            <th width="15%">الإجمالي</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td class="text-center">{{ loop.index }}</td>
                            <td><strong>{{ item.product_name }}</strong></td>
                            <td>{{ item.description or '-' }}</td>
                            <td class="text-center">{{ "%.3f"|format(item.quantity) }}</td>
                            <td class="text-end">{{ "%.2f"|format(item.unit_price) }} ر.س</td>
                            <td class="text-end fw-bold">{{ "%.2f"|format(item.total_price) }} ر.س</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <!-- ملخص المبالغ -->
            <div class="row">
                <div class="col-md-6">
                    {% if purchase.notes %}
                    <div class="info-section">
                        <h6 class="fw-bold text-secondary mb-2">ملاحظات</h6>
                        <p class="mb-0">{{ purchase.notes }}</p>
                    </div>
                    {% endif %}
                </div>
                <div class="col-md-6">
                    <div class="totals-section">
                        <div class="d-flex justify-content-between mb-2">
                            <span>المبلغ الفرعي:</span>
                            <span class="fw-bold">{{ "%.2f"|format(purchase.subtotal) }} ر.س</span>
                        </div>
                        {% if purchase.has_tax %}
                        <div class="d-flex justify-content-between mb-2">
                            <span>الضريبة ({{ "%.1f"|format(purchase.tax_rate) }}%):</span>
                            <span class="fw-bold">{{ "%.2f"|format(purchase.tax_amount) }} ر.س</span>
                        </div>
                        {% endif %}
                        <hr class="my-2">
                        <div class="d-flex justify-content-between">
                            <span class="fs-5 fw-bold">الإجمالي:</span>
                            <span class="fs-4 fw-bold text-secondary">{{ "%.2f"|format(purchase.total) }} ر.س</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تذييل الفاتورة -->
            <div class="text-center mt-4 pt-4 border-top">
                <p class="text-muted mb-2">فاتورة مشتريات معتمدة</p>
                <p class="small text-muted mb-0">هذه فاتورة إلكترونية صادرة من نظام المحاسبة الاحترافي</p>
            </div>

            <!-- أزرار الطباعة -->
            <div class="text-center mt-4 no-print">
                <button class="btn btn-secondary btn-lg me-2" onclick="window.print()">
                    <i class="fas fa-print me-2"></i>طباعة الفاتورة
                </button>
                <button class="btn btn-light btn-lg" onclick="window.close()">
                    <i class="fas fa-times me-2"></i>إغلاق
                </button>
            </div>
        </div>
    </body>
    </html>
    ''', purchase=purchase, items=items, company_info=company_info)

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
        <title>إدارة المصروفات - نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .expense-card {
                border-left: 4px solid #dc3545;
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
            }
            .expense-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }
            .btn-action {
                border-radius: 10px;
                padding: 0.5rem 1rem;
                margin: 0.2rem;
                transition: all 0.3s ease;
            }
            .btn-action:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .category-badge {
                font-size: 0.8em;
                padding: 0.5em 1em;
                border-radius: 20px;
            }
            .table-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
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
            <!-- عنوان الصفحة -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-danger">
                    <i class="fas fa-receipt me-3"></i>إدارة المصروفات
                </h1>
                <p class="lead text-muted">تتبع وإدارة جميع مصروفات الشركة</p>
            </div>

            <!-- إحصائيات المصروفات -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-danger mb-3">
                            <i class="fas fa-receipt fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-danger">{{ expenses|length }}</h3>
                        <p class="text-muted mb-0">إجمالي المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-money-bill-wave fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-warning">{{ "%.2f"|format(total_expenses) }}</h3>
                        <p class="text-muted mb-0">إجمالي القيمة (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-tags fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ expense_categories|length }}</h3>
                        <p class="text-muted mb-0">فئات المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-calculator fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ "%.2f"|format(total_expenses / (expenses|length) if expenses|length > 0 else 0) }}</h3>
                        <p class="text-muted mb-0">متوسط المصروف (ر.س)</p>
                    </div>
                </div>
            </div>

            <!-- تحليل الفئات -->
            {% if expense_categories %}
            <div class="stat-card mb-5">
                <div class="card-header bg-info text-white p-4">
                    <h5 class="mb-0 fw-bold"><i class="fas fa-chart-pie me-2"></i>تحليل المصروفات حسب الفئة</h5>
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        {% for category in expense_categories %}
                        <div class="col-md-6 col-lg-4">
                            <div class="d-flex justify-content-between align-items-center p-3 bg-light rounded">
                                <div>
                                    <span class="badge bg-info category-badge">{{ category.category }}</span>
                                    <div class="mt-1">
                                        <small class="text-muted">{{ category.count }} مصروف</small>
                                    </div>
                                </div>
                                <div class="text-end">
                                    <strong class="text-danger">{{ "%.2f"|format(category.total) }} ر.س</strong>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endif %}

            <div class="table-container">
                <div class="card-header bg-danger text-white p-4 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0 fw-bold"><i class="fas fa-receipt me-2"></i>قائمة المصروفات</h5>
                    <button type="button" class="btn btn-light btn-lg" data-bs-toggle="modal" data-bs-target="#addExpenseModal">
                        <i class="fas fa-plus me-2"></i>إضافة مصروف جديد
                    </button>
                </div>
                <div class="card-body p-0">
                    {% if expenses %}
                    <div class="table-responsive">
                        <table class="table table-hover mb-0" id="expensesTable">
                            <thead class="table-dark">
                                <tr>
                                    <th class="p-3">التاريخ</th>
                                    <th class="p-3">الوصف</th>
                                    <th class="p-3">الفئة</th>
                                    <th class="p-3">المبلغ</th>
                                    <th class="p-3">طريقة الدفع</th>
                                    <th class="p-3">رقم الإيصال</th>
                                    <th class="p-3">الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for expense in expenses %}
                                <tr>
                                    <td class="p-3">{{ expense.date.strftime('%Y-%m-%d') }}</td>
                                    <td class="p-3">
                                        <div>
                                            <strong>{{ expense.description }}</strong>
                                            {% if expense.notes %}
                                            <br><small class="text-muted">{{ expense.notes[:50] }}{% if expense.notes|length > 50 %}...{% endif %}</small>
                                            {% endif %}
                                        </div>
                                    </td>
                                    <td class="p-3">
                                        <span class="badge bg-info category-badge">{{ expense.category }}</span>
                                    </td>
                                    <td class="p-3">
                                        <strong class="text-danger fs-6">{{ "%.2f"|format(expense.amount) }} ر.س</strong>
                                    </td>
                                    <td class="p-3">
                                        {% if expense.payment_method == 'cash' %}
                                        <span class="badge bg-success"><i class="fas fa-money-bill me-1"></i>نقدي</span>
                                        {% elif expense.payment_method == 'card' %}
                                        <span class="badge bg-primary"><i class="fas fa-credit-card me-1"></i>بطاقة</span>
                                        {% elif expense.payment_method == 'bank' %}
                                        <span class="badge bg-info"><i class="fas fa-university me-1"></i>بنكي</span>
                                        {% else %}
                                        <span class="badge bg-secondary"><i class="fas fa-question me-1"></i>أخرى</span>
                                        {% endif %}
                                    </td>
                                    <td class="p-3">{{ expense.receipt_number or '-' }}</td>
                                    <td class="p-3">
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-sm btn-outline-primary btn-action" title="عرض التفاصيل" onclick="viewExpense({{ expense.id }})">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-warning btn-action" title="تعديل" onclick="editExpense({{ expense.id }})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger btn-action" title="حذف" onclick="deleteExpense({{ expense.id }}, '{{ expense.description }}')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="fas fa-receipt fa-4x text-muted mb-3"></i>
                            <h4 class="text-muted">لا توجد مصروفات مسجلة</h4>
                            <p class="text-muted">ابدأ بإضافة أول مصروف للشركة</p>
                        </div>
                        <button type="button" class="btn btn-danger btn-lg" data-bs-toggle="modal" data-bs-target="#addExpenseModal">
                            <i class="fas fa-plus me-2"></i>إضافة مصروف جديد
                        </button>
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
                        <h5 class="modal-title fw-bold"><i class="fas fa-plus me-2"></i>إضافة مصروف جديد</h5>
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
                                        <input type="date" class="form-control" id="date" name="date" value="{{ format_date('%Y-%m-%d') }}">
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
        <script>
            // وظائف إدارة المصروفات
            function viewExpense(expenseId) {
                alert('عرض تفاصيل المصروف رقم: ' + expenseId);
                // يمكن إضافة modal لعرض التفاصيل
            }

            function editExpense(expenseId) {
                alert('تعديل المصروف رقم: ' + expenseId);
                // يمكن إضافة modal للتعديل
            }

            function deleteExpense(expenseId, description) {
                if (confirm('هل أنت متأكد من حذف المصروف: ' + description + '؟')) {
                    fetch('/delete_expense/' + expenseId, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم حذف المصروف بنجاح');
                            location.reload();
                        } else {
                            alert('حدث خطأ أثناء الحذف: ' + (data.message || 'خطأ غير معروف'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('حدث خطأ أثناء الحذف');
                    });
                }
            }

            // تحسين تجربة المستخدم
            document.addEventListener('DOMContentLoaded', function() {
                // إضافة تأثيرات للبطاقات
                const cards = document.querySelectorAll('.stat-card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-10px)';
                    });

                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });

                // تحسين النموذج
                const form = document.querySelector('#addExpenseModal form');
                if (form) {
                    form.addEventListener('submit', function(e) {
                        const description = document.getElementById('description').value.trim();
                        const amount = document.getElementById('amount').value;
                        const category = document.getElementById('category').value;

                        if (!description || !amount || !category) {
                            e.preventDefault();
                            alert('يرجى ملء جميع الحقول المطلوبة');
                            return false;
                        }

                        if (parseFloat(amount) <= 0) {
                            e.preventDefault();
                            alert('يجب أن يكون المبلغ أكبر من صفر');
                            return false;
                        }
                    });
                }
            });
        </script>
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
                                    <th>الراتب الأساسي</th>
                                    <th>أيام العمل</th>
                                    <th>البدلات</th>
                                    <th>الاستقطاعات</th>
                                    <th>صافي الراتب</th>
                                    <th>الهاتف</th>
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
                                            <div>
                                                <strong>{{ employee.name }}</strong>
                                                {% if employee.email %}
                                                <br><small class="text-muted">{{ employee.email }}</small>
                                                {% endif %}
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="badge bg-info">{{ employee.position }}</span>
                                    </td>
                                    <td class="fw-bold text-primary">{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                    <td>
                                        <span class="badge bg-secondary">{{ employee.working_days or 30 }} يوم</span>
                                    </td>
                                    <td class="text-success">
                                        {% if employee.allowances and employee.allowances > 0 %}
                                        {{ "%.2f"|format(employee.allowances) }} ر.س
                                        {% else %}
                                        -
                                        {% endif %}
                                    </td>
                                    <td class="text-danger">
                                        {% if employee.deductions and employee.deductions > 0 %}
                                        {{ "%.2f"|format(employee.deductions) }} ر.س
                                        {% else %}
                                        -
                                        {% endif %}
                                    </td>
                                    <td class="fw-bold text-success">
                                        {{ "%.2f"|format((employee.salary or 0) + (employee.allowances or 0) - (employee.deductions or 0)) }} ر.س
                                    </td>
                                    <td>{{ employee.phone or '-' }}</td>
                                    <td>{{ employee.hire_date.strftime('%Y-%m-%d') }}</td>
                                    <td>
                                        {% if employee.status == 'active' %}
                                        <span class="badge bg-success">نشط</span>
                                        {% else %}
                                        <span class="badge bg-danger">غير نشط</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-sm btn-outline-info" title="عرض الملف" onclick="viewEmployee({{ employee.id }})">
                                                <i class="fas fa-user"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-success" title="كشف راتب" onclick="generatePayroll({{ employee.id }})">
                                                <i class="fas fa-money-check"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-warning" title="تعديل" onclick="editEmployee({{ employee.id }})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" title="حذف" onclick="deleteEmployee({{ employee.id }}, '{{ employee.name }}')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
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

                            <!-- إعدادات الراتب والعمل -->
                            <div class="card bg-light mb-3">
                                <div class="card-header">
                                    <h6 class="mb-0 fw-bold text-primary">
                                        <i class="fas fa-cogs me-2"></i>إعدادات الراتب والعمل
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="working_days" class="form-label">أيام العمل في الشهر *</label>
                                                <input type="number" class="form-control" id="working_days" name="working_days" value="30" min="1" max="31" required>
                                                <small class="form-text text-muted">عدد أيام العمل المقررة شهرياً</small>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="overtime_rate" class="form-label">معدل الساعة الإضافية (ر.س)</label>
                                                <input type="number" step="0.01" class="form-control" id="overtime_rate" name="overtime_rate" value="0" min="0">
                                                <small class="form-text text-muted">سعر الساعة الإضافية</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="allowances" class="form-label">البدلات الشهرية (ر.س)</label>
                                                <input type="number" step="0.01" class="form-control" id="allowances" name="allowances" value="0" min="0">
                                                <small class="form-text text-muted">البدلات الثابتة (نقل، سكن، إلخ)</small>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="deductions" class="form-label">الاستقطاعات الشهرية (ر.س)</label>
                                                <input type="number" step="0.01" class="form-control" id="deductions" name="deductions" value="0" min="0">
                                                <small class="form-text text-muted">الاستقطاعات الثابتة (تأمين، قروض، إلخ)</small>
                                            </div>
                                        </div>
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
        <script>
            // وظائف إدارة الموظفين
            function viewEmployee(employeeId) {
                window.location.href = '/view_employee/' + employeeId;
            }

            function editEmployee(employeeId) {
                alert('تعديل الموظف رقم: ' + employeeId + ' - قيد التطوير');
                // يمكن إضافة modal للتعديل لاحقاً
            }

            function deleteEmployee(employeeId, employeeName) {
                if (confirm('هل أنت متأكد من حذف الموظف: ' + employeeName + '؟')) {
                    fetch('/delete_employee/' + employeeId, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('تم حذف الموظف بنجاح');
                            location.reload();
                        } else {
                            alert('حدث خطأ أثناء الحذف: ' + (data.message || 'خطأ غير معروف'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('حدث خطأ أثناء الحذف');
                    });
                }
            }

            function generatePayroll(employeeId) {
                window.location.href = '/generate_payroll/' + employeeId;
            }
        </script>
    </body>
    </html>
    ''', employees=employees, active_employees=active_employees, total_salaries=total_salaries)

@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    try:
        from datetime import datetime
        hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()

        employee = Employee(
            name=request.form['name'],
            position=request.form['position'],
            salary=float(request.form['salary']),
            hire_date=hire_date,
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            working_days=int(request.form.get('working_days', 30)),
            overtime_rate=float(request.form.get('overtime_rate', 0)),
            allowances=float(request.form.get('allowances', 0)),
            deductions=float(request.form.get('deductions', 0)),
            status='active'
        )
        db.session.add(employee)
        db.session.commit()
        flash('تم إضافة الموظف بنجاح مع جميع إعدادات الراتب', 'success')
        return redirect(url_for('employees'))

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إضافة الموظف: {str(e)}', 'error')
        return redirect(url_for('employees'))

@app.route('/reports')
@login_required
def reports():
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>التقارير المالية التفصيلية - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .report-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .report-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .report-icon {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                color: white;
                margin: 0 auto 1rem;
            }
            .btn-report {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 15px;
                padding: 1rem 2rem;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-report:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
                color: white;
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
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-primary">التقارير المالية التفصيلية</h1>
                <p class="lead text-muted">تقارير شاملة ومفصلة لجميع العمليات المالية</p>
            </div>

            <div class="row g-4">
                <!-- تقرير المبيعات التفصيلي -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-success">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير المبيعات التفصيلي</h5>
                            <p class="card-text text-muted">تقرير شامل لجميع عمليات المبيعات مع التحليلات</p>
                            <a href="{{ url_for('sales_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>

                <!-- تقرير المشتريات التفصيلي -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-danger">
                                <i class="fas fa-shopping-cart"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير المشتريات التفصيلي</h5>
                            <p class="card-text text-muted">تقرير مفصل لجميع عمليات المشتريات والموردين</p>
                            <a href="{{ url_for('purchases_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>

                <!-- تقرير المصروفات التفصيلي -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-warning">
                                <i class="fas fa-receipt"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير المصروفات التفصيلي</h5>
                            <p class="card-text text-muted">تحليل شامل للمصروفات حسب الفئات والفترات</p>
                            <a href="{{ url_for('expenses_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>

                <!-- تقرير الأرباح والخسائر -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-info">
                                <i class="fas fa-balance-scale"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير الأرباح والخسائر</h5>
                            <p class="card-text text-muted">قائمة الدخل الشاملة والتحليل المالي</p>
                            <a href="{{ url_for('profit_loss_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>

                <!-- تقرير المخزون التفصيلي -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-primary">
                                <i class="fas fa-boxes"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير المخزون التفصيلي</h5>
                            <p class="card-text text-muted">حالة المخزون والمنتجات مع التنبيهات</p>
                            <a href="{{ url_for('inventory_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>

                <!-- تقرير الرواتب التفصيلي -->
                <div class="col-md-6 col-lg-4">
                    <div class="report-card h-100">
                        <div class="card-body text-center p-4">
                            <div class="report-icon bg-secondary">
                                <i class="fas fa-money-check-alt"></i>
                            </div>
                            <h5 class="card-title fw-bold">تقرير الرواتب التفصيلي</h5>
                            <p class="card-text text-muted">كشوف الرواتب والموظفين مع التحليلات</p>
                            <a href="{{ url_for('payroll_report') }}" class="btn btn-report">
                                <i class="fas fa-file-alt me-2"></i>عرض التقرير
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تقارير سريعة -->
            <div class="row mt-5">
                <div class="col-12">
                    <div class="report-card">
                        <div class="card-header bg-dark text-white">
                            <h5 class="mb-0"><i class="fas fa-tachometer-alt me-2"></i>التقارير السريعة</h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-3">
                                    <button class="btn btn-outline-primary w-100" onclick="generateQuickReport('daily')">
                                        <i class="fas fa-calendar-day me-2"></i>تقرير يومي
                                    </button>
                                </div>
                                <div class="col-md-3">
                                    <button class="btn btn-outline-success w-100" onclick="generateQuickReport('weekly')">
                                        <i class="fas fa-calendar-week me-2"></i>تقرير أسبوعي
                                    </button>
                                </div>
                                <div class="col-md-3">
                                    <button class="btn btn-outline-warning w-100" onclick="generateQuickReport('monthly')">
                                        <i class="fas fa-calendar-alt me-2"></i>تقرير شهري
                                    </button>
                                </div>
                                <div class="col-md-3">
                                    <button class="btn btn-outline-info w-100" onclick="generateQuickReport('yearly')">
                                        <i class="fas fa-calendar me-2"></i>تقرير سنوي
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function generateQuickReport(period) {
                alert('سيتم إنشاء التقرير ' + period + ' قريباً');
                // يمكن إضافة وظيفة AJAX هنا لإنشاء التقارير السريعة
            }
        </script>
    </body>
    </html>
    ''')

# تقرير المبيعات التفصيلي
@app.route('/sales_report')
@login_required
def sales_report():
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta

    # الحصول على بيانات المبيعات
    sales = SalesInvoice.query.order_by(SalesInvoice.date.desc()).all()
    total_sales = sum(sale.total for sale in sales)
    total_invoices = len(sales)

    # المبيعات حسب الشهر
    monthly_sales = db.session.query(
        extract('month', SalesInvoice.date).label('month'),
        extract('year', SalesInvoice.date).label('year'),
        func.sum(SalesInvoice.total).label('total'),
        func.count(SalesInvoice.id).label('count')
    ).group_by(extract('month', SalesInvoice.date), extract('year', SalesInvoice.date)).all()

    # أفضل العملاء
    top_customers = db.session.query(
        Customer.name,
        func.sum(SalesInvoice.total).label('total_sales'),
        func.count(SalesInvoice.id).label('invoice_count')
    ).join(SalesInvoice).group_by(Customer.id, Customer.name).order_by(func.sum(SalesInvoice.total).desc()).limit(10).all()

    # المبيعات حسب الحالة
    sales_by_status = db.session.query(
        SalesInvoice.status,
        func.sum(SalesInvoice.total).label('total'),
        func.count(SalesInvoice.id).label('count')
    ).group_by(SalesInvoice.status).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير المبيعات التفصيلي - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            .chart-container {
                position: relative;
                height: 400px;
                margin: 20px 0;
            }
            .table-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .btn-export {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                border: none;
                border-radius: 15px;
                padding: 0.75rem 1.5rem;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-export:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(17, 153, 142, 0.4);
                color: white;
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
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- عنوان التقرير -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-success">
                    <i class="fas fa-chart-line me-3"></i>تقرير المبيعات التفصيلي
                </h1>
                <p class="lead text-muted">تحليل شامل لجميع عمليات المبيعات والأداء</p>
            </div>

            <!-- الإحصائيات الرئيسية -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-chart-line fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ "%.2f"|format(total_sales) }}</h3>
                        <p class="text-muted mb-0">إجمالي المبيعات (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-file-invoice fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-primary">{{ total_invoices }}</h3>
                        <p class="text-muted mb-0">عدد الفواتير</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-calculator fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ "%.2f"|format(total_sales / total_invoices if total_invoices > 0 else 0) }}</h3>
                        <p class="text-muted mb-0">متوسط الفاتورة (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-users fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-warning">{{ top_customers|length }}</h3>
                        <p class="text-muted mb-0">العملاء النشطين</p>
                    </div>
                </div>
            </div>

            <!-- الرسوم البيانية -->
            <div class="row g-4 mb-5">
                <div class="col-md-8">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-bar me-2"></i>المبيعات الشهرية
                        </h5>
                        <div class="chart-container">
                            <canvas id="monthlySalesChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-pie me-2"></i>المبيعات حسب الحالة
                        </h5>
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- أفضل العملاء -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="table-container">
                        <div class="card-header bg-success text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-crown me-2"></i>أفضل العملاء (أعلى 10)
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>الترتيب</th>
                                            <th>اسم العميل</th>
                                            <th>إجمالي المبيعات</th>
                                            <th>عدد الفواتير</th>
                                            <th>متوسط الفاتورة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for customer in top_customers %}
                                        <tr>
                                            <td>
                                                <span class="badge bg-success">{{ loop.index }}</span>
                                            </td>
                                            <td class="fw-bold">{{ customer.name }}</td>
                                            <td class="text-success fw-bold">{{ "%.2f"|format(customer.total_sales) }} ر.س</td>
                                            <td>{{ customer.invoice_count }}</td>
                                            <td>{{ "%.2f"|format(customer.total_sales / customer.invoice_count) }} ر.س</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تفاصيل الفواتير -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="table-container">
                        <div class="card-header bg-primary text-white p-4 d-flex justify-content-between align-items-center">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-list me-2"></i>تفاصيل جميع الفواتير
                            </h5>
                            <div>
                                <button class="btn btn-export me-2" onclick="exportToPDF()">
                                    <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                                </button>
                                <button class="btn btn-export" onclick="exportToExcel()">
                                    <i class="fas fa-file-excel me-2"></i>تصدير Excel
                                </button>
                            </div>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0" id="salesTable">
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
                                            <td class="fw-bold">{{ sale.invoice_number }}</td>
                                            <td>{{ sale.customer.name if sale.customer else 'عميل نقدي' }}</td>
                                            <td>{{ sale.date.strftime('%Y-%m-%d') }}</td>
                                            <td>{{ "%.2f"|format(sale.subtotal) }} ر.س</td>
                                            <td>{{ "%.2f"|format(sale.tax_amount) }} ر.س</td>
                                            <td class="fw-bold text-success">{{ "%.2f"|format(sale.total) }} ر.س</td>
                                            <td>
                                                <span class="badge {{ 'bg-success' if sale.status == 'paid' else 'bg-warning' if sale.status == 'pending' else 'bg-danger' }}">
                                                    {{ 'مدفوعة' if sale.status == 'paid' else 'معلقة' if sale.status == 'pending' else 'ملغية' }}
                                                </span>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" onclick="printInvoice({{ sale.id }})">
                                                    <i class="fas fa-print"></i>
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
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
        <script>
            // رسم بياني للمبيعات الشهرية
            const monthlySalesCtx = document.getElementById('monthlySalesChart').getContext('2d');
            new Chart(monthlySalesCtx, {
                type: 'line',
                data: {
                    labels: [
                        {% for sale in monthly_sales %}
                        '{{ sale.month }}/{{ sale.year }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        label: 'المبيعات الشهرية',
                        data: [
                            {% for sale in monthly_sales %}
                            {{ sale.total }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        borderColor: 'rgb(25, 135, 84)',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'اتجاه المبيعات الشهرية'
                        }
                    }
                }
            });

            // رسم بياني للحالات
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: [
                        {% for status in sales_by_status %}
                        '{{ "مدفوعة" if status.status == "paid" else "معلقة" if status.status == "pending" else "ملغية" }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        data: [
                            {% for status in sales_by_status %}
                            {{ status.total }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        backgroundColor: [
                            '#28a745', '#ffc107', '#dc3545'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            // وظائف التصدير
            function exportToPDF() {
                window.print();
            }

            function exportToExcel() {
                const table = document.getElementById('salesTable');
                const wb = XLSX.utils.table_to_sheet(table);
                const wbout = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wbout, wb, 'تقرير المبيعات');
                XLSX.writeFile(wbout, 'sales_report.xlsx');
            }

            function printInvoice(invoiceId) {
                window.open('/print_invoice/' + invoiceId, '_blank');
            }
        </script>
    </body>
    </html>
    ''', sales=sales, total_sales=total_sales, total_invoices=total_invoices,
         monthly_sales=monthly_sales, top_customers=top_customers, sales_by_status=sales_by_status)

# تقرير المشتريات التفصيلي
@app.route('/purchases_report')
@login_required
def purchases_report():
    from sqlalchemy import func

    purchases = PurchaseInvoice.query.order_by(PurchaseInvoice.date.desc()).all()
    total_purchases = sum(purchase.total for purchase in purchases)

    # أفضل الموردين
    top_suppliers = db.session.query(
        Supplier.name,
        func.sum(PurchaseInvoice.total).label('total_purchases'),
        func.count(PurchaseInvoice.id).label('invoice_count')
    ).join(PurchaseInvoice).group_by(Supplier.id, Supplier.name).order_by(func.sum(PurchaseInvoice.total).desc()).limit(10).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير المشتريات التفصيلي - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
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
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-danger">
                    <i class="fas fa-shopping-cart me-3"></i>تقرير المشتريات التفصيلي
                </h1>
                <p class="lead text-muted">تحليل شامل لجميع عمليات المشتريات والموردين</p>
            </div>

            <!-- الإحصائيات الرئيسية -->
            <div class="row g-4 mb-5">
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-danger mb-3">
                            <i class="fas fa-shopping-cart fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-danger">{{ "%.2f"|format(total_purchases) }}</h3>
                        <p class="text-muted mb-0">إجمالي المشتريات (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-file-invoice fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-primary">{{ purchases|length }}</h3>
                        <p class="text-muted mb-0">عدد فواتير المشتريات</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-truck fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ top_suppliers|length }}</h3>
                        <p class="text-muted mb-0">الموردين النشطين</p>
                    </div>
                </div>
            </div>

            <!-- أفضل الموردين -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-danger text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-crown me-2"></i>أفضل الموردين
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>الترتيب</th>
                                            <th>اسم المورد</th>
                                            <th>إجمالي المشتريات</th>
                                            <th>عدد الفواتير</th>
                                            <th>متوسط الفاتورة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for supplier in top_suppliers %}
                                        <tr>
                                            <td>
                                                <span class="badge bg-danger">{{ loop.index }}</span>
                                            </td>
                                            <td class="fw-bold">{{ supplier.name }}</td>
                                            <td class="text-danger fw-bold">{{ "%.2f"|format(supplier.total_purchases) }} ر.س</td>
                                            <td>{{ supplier.invoice_count }}</td>
                                            <td>{{ "%.2f"|format(supplier.total_purchases / supplier.invoice_count) }} ر.س</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تفاصيل فواتير المشتريات -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-secondary text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-list me-2"></i>تفاصيل فواتير المشتريات
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>رقم الفاتورة</th>
                                            <th>المورد</th>
                                            <th>التاريخ</th>
                                            <th>المبلغ الفرعي</th>
                                            <th>الضريبة</th>
                                            <th>الإجمالي</th>
                                            <th>الحالة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for purchase in purchases %}
                                        <tr>
                                            <td class="fw-bold">{{ purchase.invoice_number }}</td>
                                            <td>{{ purchase.supplier.name if purchase.supplier else 'مورد غير محدد' }}</td>
                                            <td>{{ purchase.date.strftime('%Y-%m-%d') }}</td>
                                            <td>{{ "%.2f"|format(purchase.subtotal) }} ر.س</td>
                                            <td>{{ "%.2f"|format(purchase.tax_amount) }} ر.س</td>
                                            <td class="fw-bold text-danger">{{ "%.2f"|format(purchase.total) }} ر.س</td>
                                            <td>
                                                <span class="badge {{ 'bg-success' if purchase.status == 'paid' else 'bg-warning' if purchase.status == 'pending' else 'bg-danger' }}">
                                                    {{ 'مدفوعة' if purchase.status == 'paid' else 'معلقة' if purchase.status == 'pending' else 'ملغية' }}
                                                </span>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', purchases=purchases, total_purchases=total_purchases, top_suppliers=top_suppliers)

# تقرير الأرباح والخسائر
@app.route('/profit_loss_report')
@login_required
def profit_loss_report():
    from sqlalchemy import func

    # حساب الإيرادات
    total_sales = db.session.query(func.sum(SalesInvoice.total)).scalar() or 0

    # حساب التكاليف
    total_purchases = db.session.query(func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    total_salaries = db.session.query(func.sum(Employee.salary)).filter(Employee.status == 'active').scalar() or 0

    # حساب الأرباح
    gross_profit = total_sales - total_purchases
    net_profit = gross_profit - total_expenses - total_salaries

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير الأرباح والخسائر - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .profit-loss-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: none;
                overflow: hidden;
            }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .total-row {
                background: #f8f9fa;
                font-weight: bold;
                font-size: 1.1em;
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
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-info">
                    <i class="fas fa-balance-scale me-3"></i>تقرير الأرباح والخسائر
                </h1>
                <p class="lead text-muted">قائمة الدخل الشاملة والتحليل المالي</p>
            </div>

            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="profit-loss-card">
                        <div class="card-header bg-info text-white p-4">
                            <h4 class="mb-0 fw-bold text-center">
                                <i class="fas fa-chart-line me-2"></i>قائمة الدخل
                            </h4>
                        </div>
                        <div class="card-body p-4">
                            <table class="table table-borderless">
                                <tbody>
                                    <!-- الإيرادات -->
                                    <tr class="table-success">
                                        <td colspan="2" class="fw-bold fs-5">
                                            <i class="fas fa-plus-circle me-2"></i>الإيرادات
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="ps-4">إجمالي المبيعات</td>
                                        <td class="text-end positive fw-bold">{{ "%.2f"|format(total_sales) }} ر.س</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td class="ps-4 fw-bold">إجمالي الإيرادات</td>
                                        <td class="text-end positive fw-bold">{{ "%.2f"|format(total_sales) }} ر.س</td>
                                    </tr>

                                    <!-- تكلفة البضاعة المباعة -->
                                    <tr class="table-warning">
                                        <td colspan="2" class="fw-bold fs-5 pt-4">
                                            <i class="fas fa-minus-circle me-2"></i>تكلفة البضاعة المباعة
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="ps-4">إجمالي المشتريات</td>
                                        <td class="text-end negative fw-bold">{{ "%.2f"|format(total_purchases) }} ر.س</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td class="ps-4 fw-bold">الربح الإجمالي</td>
                                        <td class="text-end {{ 'positive' if gross_profit >= 0 else 'negative' }} fw-bold">
                                            {{ "%.2f"|format(gross_profit) }} ر.س
                                        </td>
                                    </tr>

                                    <!-- المصروفات التشغيلية -->
                                    <tr class="table-danger">
                                        <td colspan="2" class="fw-bold fs-5 pt-4">
                                            <i class="fas fa-receipt me-2"></i>المصروفات التشغيلية
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="ps-4">المصروفات العامة</td>
                                        <td class="text-end negative fw-bold">{{ "%.2f"|format(total_expenses) }} ر.س</td>
                                    </tr>
                                    <tr>
                                        <td class="ps-4">الرواتب والأجور</td>
                                        <td class="text-end negative fw-bold">{{ "%.2f"|format(total_salaries) }} ر.س</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td class="ps-4 fw-bold">إجمالي المصروفات التشغيلية</td>
                                        <td class="text-end negative fw-bold">{{ "%.2f"|format(total_expenses + total_salaries) }} ر.س</td>
                                    </tr>

                                    <!-- صافي الربح -->
                                    <tr class="table-primary">
                                        <td colspan="2" class="pt-4"></td>
                                    </tr>
                                    <tr class="table-primary">
                                        <td class="fw-bold fs-4">
                                            <i class="fas fa-trophy me-2"></i>صافي الربح (الخسارة)
                                        </td>
                                        <td class="text-end fw-bold fs-4 {{ 'positive' if net_profit >= 0 else 'negative' }}">
                                            {{ "%.2f"|format(net_profit) }} ر.س
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- مؤشرات الأداء -->
            <div class="row mt-5 g-4">
                <div class="col-md-3">
                    <div class="profit-loss-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-percentage fa-2x"></i>
                        </div>
                        <h5 class="fw-bold">هامش الربح الإجمالي</h5>
                        <h3 class="text-success">{{ "%.1f"|format((gross_profit / total_sales * 100) if total_sales > 0 else 0) }}%</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="profit-loss-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-chart-pie fa-2x"></i>
                        </div>
                        <h5 class="fw-bold">هامش الربح الصافي</h5>
                        <h3 class="{{ 'text-success' if net_profit >= 0 else 'text-danger' }}">
                            {{ "%.1f"|format((net_profit / total_sales * 100) if total_sales > 0 else 0) }}%
                        </h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="profit-loss-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-coins fa-2x"></i>
                        </div>
                        <h5 class="fw-bold">نسبة المصروفات</h5>
                        <h3 class="text-warning">{{ "%.1f"|format(((total_expenses + total_salaries) / total_sales * 100) if total_sales > 0 else 0) }}%</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="profit-loss-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-calculator fa-2x"></i>
                        </div>
                        <h5 class="fw-bold">العائد على المبيعات</h5>
                        <h3 class="text-info">{{ "%.1f"|format((net_profit / total_sales * 100) if total_sales > 0 else 0) }}%</h3>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', total_sales=total_sales, total_purchases=total_purchases, total_expenses=total_expenses,
         total_salaries=total_salaries, gross_profit=gross_profit, net_profit=net_profit)

# تقرير المصروفات التفصيلي
@app.route('/expenses_report')
@login_required
def expenses_report():
    from sqlalchemy import func, extract
    from datetime import datetime

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total_expenses = sum(expense.amount for expense in expenses)

    # المصروفات حسب الفئة
    expense_by_category = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).group_by(Expense.category).all()

    # المصروفات حسب طريقة الدفع
    expense_by_payment = db.session.query(
        Expense.payment_method,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).group_by(Expense.payment_method).all()

    # المصروفات الشهرية
    monthly_expenses = db.session.query(
        extract('month', Expense.date).label('month'),
        extract('year', Expense.date).label('year'),
        func.sum(Expense.amount).label('total')
    ).group_by(extract('month', Expense.date), extract('year', Expense.date)).all()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير المصروفات التفصيلي - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            .chart-container {
                position: relative;
                height: 400px;
                margin: 20px 0;
            }
            @media print {
                .no-print { display: none !important; }
                body { background: white !important; }
                .stat-card { box-shadow: none !important; border: 1px solid #ddd !important; }
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark no-print">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                <div class="navbar-nav ms-auto">
                    <button class="btn btn-light me-2" onclick="window.print()">
                        <i class="fas fa-print me-1"></i>طباعة
                    </button>
                    <div class="dropdown me-2">
                        <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-filter me-1"></i>فلترة
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="?period=weekly">أسبوعي</a></li>
                            <li><a class="dropdown-item" href="?period=monthly">شهري</a></li>
                            <li><a class="dropdown-item" href="?period=yearly">سنوي</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('expenses_report') }}">جميع الفترات</a></li>
                        </ul>
                    </div>
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-danger">
                    <i class="fas fa-receipt me-3"></i>تقرير المصروفات التفصيلي
                </h1>
                <p class="lead text-muted">تحليل شامل لجميع مصروفات الشركة</p>
            </div>

            <!-- الإحصائيات الرئيسية -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-danger mb-3">
                            <i class="fas fa-receipt fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-danger">{{ "%.2f"|format(total_expenses) }}</h3>
                        <p class="text-muted mb-0">إجمالي المصروفات (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-list fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-warning">{{ expenses|length }}</h3>
                        <p class="text-muted mb-0">عدد المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-info mb-3">
                            <i class="fas fa-tags fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-info">{{ expense_by_category|length }}</h3>
                        <p class="text-muted mb-0">فئات المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-calculator fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ "%.2f"|format(total_expenses / expenses|length if expenses|length > 0 else 0) }}</h3>
                        <p class="text-muted mb-0">متوسط المصروف (ر.س)</p>
                    </div>
                </div>
            </div>

            <!-- الرسوم البيانية -->
            <div class="row g-4 mb-5">
                <div class="col-md-6">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-pie me-2"></i>المصروفات حسب الفئة
                        </h5>
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="stat-card p-4">
                        <h5 class="fw-bold mb-4">
                            <i class="fas fa-chart-bar me-2"></i>المصروفات حسب طريقة الدفع
                        </h5>
                        <div class="chart-container">
                            <canvas id="paymentChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- تفاصيل المصروفات -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-danger text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-list me-2"></i>تفاصيل جميع المصروفات
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>التاريخ</th>
                                            <th>الوصف</th>
                                            <th>الفئة</th>
                                            <th>المبلغ</th>
                                            <th>طريقة الدفع</th>
                                            <th>رقم الإيصال</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for expense in expenses %}
                                        <tr>
                                            <td>{{ expense.date.strftime('%Y-%m-%d') }}</td>
                                            <td>
                                                <strong>{{ expense.description }}</strong>
                                                {% if expense.notes %}
                                                <br><small class="text-muted">{{ expense.notes }}</small>
                                                {% endif %}
                                            </td>
                                            <td>
                                                <span class="badge bg-info">{{ expense.category }}</span>
                                            </td>
                                            <td class="fw-bold text-danger">{{ "%.2f"|format(expense.amount) }} ر.س</td>
                                            <td>
                                                {% if expense.payment_method == 'cash' %}
                                                <span class="badge bg-success">نقدي</span>
                                                {% elif expense.payment_method == 'card' %}
                                                <span class="badge bg-primary">بطاقة</span>
                                                {% elif expense.payment_method == 'bank' %}
                                                <span class="badge bg-info">بنكي</span>
                                                {% else %}
                                                <span class="badge bg-secondary">أخرى</span>
                                                {% endif %}
                                            </td>
                                            <td>{{ expense.receipt_number or '-' }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // رسم بياني للفئات
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {
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
                    maintainAspectRatio: false
                }
            });

            // رسم بياني لطرق الدفع
            const paymentCtx = document.getElementById('paymentChart').getContext('2d');
            new Chart(paymentCtx, {
                type: 'bar',
                data: {
                    labels: [
                        {% for payment in expense_by_payment %}
                        '{{ "نقدي" if payment.payment_method == "cash" else "بطاقة" if payment.payment_method == "card" else "بنكي" if payment.payment_method == "bank" else "أخرى" }}'{{ ',' if not loop.last }}
                        {% endfor %}
                    ],
                    datasets: [{
                        label: 'المبلغ (ر.س)',
                        data: [
                            {% for payment in expense_by_payment %}
                            {{ payment.total }}{{ ',' if not loop.last }}
                            {% endfor %}
                        ],
                        backgroundColor: ['#28a745', '#007bff', '#17a2b8', '#6c757d']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        </script>
    </body>
    </html>
    ''', expenses=expenses, total_expenses=total_expenses, expense_by_category=expense_by_category,
         expense_by_payment=expense_by_payment, monthly_expenses=monthly_expenses)

@app.route('/inventory_report')
@login_required
def inventory_report():
    from sqlalchemy import func

    products = Product.query.all()
    total_products = len(products)
    total_value = sum(product.price * product.quantity for product in products)

    # المنتجات منخفضة المخزون
    low_stock_products = [p for p in products if p.quantity <= p.min_quantity]

    # المنتجات نفدت من المخزون
    out_of_stock_products = [p for p in products if p.quantity == 0]

    # المنتجات حسب الفئة
    products_by_category = {}
    for product in products:
        if product.category not in products_by_category:
            products_by_category[product.category] = []
        products_by_category[product.category].append(product)

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير المخزون التفصيلي - نظام المحاسبة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            .low-stock { background-color: #fff3cd !important; }
            .out-of-stock { background-color: #f8d7da !important; }
            @media print {
                .no-print { display: none !important; }
                body { background: white !important; }
                .stat-card { box-shadow: none !important; border: 1px solid #ddd !important; }
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark no-print">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة الاحترافي
                </a>
                <div class="navbar-nav ms-auto">
                    <button class="btn btn-light me-2" onclick="window.print()">
                        <i class="fas fa-print me-1"></i>طباعة
                    </button>
                    <div class="dropdown me-2">
                        <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-filter me-1"></i>فلترة
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="?filter=low_stock">مخزون منخفض</a></li>
                            <li><a class="dropdown-item" href="?filter=out_of_stock">نفد المخزون</a></li>
                            <li><a class="dropdown-item" href="?filter=available">متوفر</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('inventory_report') }}">جميع المنتجات</a></li>
                        </ul>
                    </div>
                    <a class="nav-link" href="{{ url_for('reports') }}">
                        <i class="fas fa-arrow-right me-1"></i>رجوع للتقارير
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-primary">
                    <i class="fas fa-boxes me-3"></i>تقرير المخزون التفصيلي
                </h1>
                <p class="lead text-muted">حالة المخزون والمنتجات مع التنبيهات</p>
            </div>

            <!-- الإحصائيات الرئيسية -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-primary mb-3">
                            <i class="fas fa-boxes fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-primary">{{ total_products }}</h3>
                        <p class="text-muted mb-0">إجمالي المنتجات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-success mb-3">
                            <i class="fas fa-dollar-sign fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-success">{{ "%.2f"|format(total_value) }}</h3>
                        <p class="text-muted mb-0">قيمة المخزون (ر.س)</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-warning mb-3">
                            <i class="fas fa-exclamation-triangle fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-warning">{{ low_stock_products|length }}</h3>
                        <p class="text-muted mb-0">منتجات منخفضة المخزون</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center p-4">
                        <div class="text-danger mb-3">
                            <i class="fas fa-times-circle fa-3x"></i>
                        </div>
                        <h3 class="fw-bold text-danger">{{ out_of_stock_products|length }}</h3>
                        <p class="text-muted mb-0">منتجات نفدت من المخزون</p>
                    </div>
                </div>
            </div>

            <!-- تنبيهات المخزون -->
            {% if low_stock_products or out_of_stock_products %}
            <div class="row mb-5">
                {% if out_of_stock_products %}
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="card-header bg-danger text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-times-circle me-2"></i>منتجات نفدت من المخزون
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>اسم المنتج</th>
                                            <th>الفئة</th>
                                            <th>السعر</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for product in out_of_stock_products %}
                                        <tr class="out-of-stock">
                                            <td><strong>{{ product.name }}</strong></td>
                                            <td><span class="badge bg-secondary">{{ product.category }}</span></td>
                                            <td>{{ "%.2f"|format(product.price) }} ر.س</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}

                {% if low_stock_products %}
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="card-header bg-warning text-dark p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-exclamation-triangle me-2"></i>منتجات منخفضة المخزون
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>اسم المنتج</th>
                                            <th>الكمية الحالية</th>
                                            <th>الحد الأدنى</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for product in low_stock_products %}
                                        <tr class="low-stock">
                                            <td><strong>{{ product.name }}</strong></td>
                                            <td><span class="badge bg-warning">{{ product.quantity }}</span></td>
                                            <td>{{ product.min_quantity }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
            {% endif %}

            <!-- جميع المنتجات -->
            <div class="row mb-5">
                <div class="col-12">
                    <div class="stat-card">
                        <div class="card-header bg-primary text-white p-4">
                            <h5 class="mb-0 fw-bold">
                                <i class="fas fa-list me-2"></i>جميع المنتجات في المخزون
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>اسم المنتج</th>
                                            <th>الفئة</th>
                                            <th>السعر</th>
                                            <th>التكلفة</th>
                                            <th>الكمية</th>
                                            <th>الحد الأدنى</th>
                                            <th>قيمة المخزون</th>
                                            <th>الحالة</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for product in products %}
                                        <tr class="{% if product.quantity == 0 %}out-of-stock{% elif product.quantity <= product.min_quantity %}low-stock{% endif %}">
                                            <td><strong>{{ product.name }}</strong></td>
                                            <td><span class="badge bg-info">{{ product.category }}</span></td>
                                            <td>{{ "%.2f"|format(product.price) }} ر.س</td>
                                            <td>{{ "%.2f"|format(product.cost or 0) }} ر.س</td>
                                            <td>
                                                <span class="badge {% if product.quantity == 0 %}bg-danger{% elif product.quantity <= product.min_quantity %}bg-warning{% else %}bg-success{% endif %}">
                                                    {{ product.quantity }}
                                                </span>
                                            </td>
                                            <td>{{ product.min_quantity }}</td>
                                            <td class="fw-bold">{{ "%.2f"|format(product.price * product.quantity) }} ر.س</td>
                                            <td>
                                                {% if product.quantity == 0 %}
                                                <span class="badge bg-danger">نفد المخزون</span>
                                                {% elif product.quantity <= product.min_quantity %}
                                                <span class="badge bg-warning">مخزون منخفض</span>
                                                {% else %}
                                                <span class="badge bg-success">متوفر</span>
                                                {% endif %}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', products=products, total_products=total_products, total_value=total_value,
         low_stock_products=low_stock_products, out_of_stock_products=out_of_stock_products,
         products_by_category=products_by_category)

@app.route('/payroll_report')
@login_required
def payroll_report():
    employees = Employee.query.filter_by(status='active').all()
    return render_template_string('<h1>تقرير الرواتب التفصيلي</h1><p>قيد التطوير</p>')
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
        <title>إعدادات النظام - نظام المحاسبة الاحترافي</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .navbar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .settings-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: none;
                overflow: hidden;
                margin-bottom: 30px;
            }
            .settings-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            .feature-icon {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                color: white;
                margin: 0 auto 20px;
            }
            .btn-settings {
                border-radius: 15px;
                padding: 1rem 2rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-settings:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
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
            <!-- عنوان الصفحة -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-secondary">
                    <i class="fas fa-cogs me-3"></i>إعدادات النظام
                </h1>
                <p class="lead text-muted">إدارة وتخصيص إعدادات نظام المحاسبة الاحترافي</p>
            </div>

            <!-- معلومات النظام -->
            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="settings-card text-center p-4">
                        <div class="feature-icon bg-primary">
                            <i class="fas fa-info-circle"></i>
                        </div>
                        <h5 class="fw-bold">معلومات النظام</h5>
                        <p class="text-muted mb-0">الإصدار 2.0.0 Professional</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="settings-card text-center p-4">
                        <div class="feature-icon bg-success">
                            <i class="fas fa-database"></i>
                        </div>
                        <h5 class="fw-bold">قاعدة البيانات</h5>
                        <p class="text-muted mb-0">SQLite متصلة وتعمل</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="settings-card text-center p-4">
                        <div class="feature-icon bg-warning">
                            <i class="fas fa-user"></i>
                        </div>
                        <h5 class="fw-bold">المستخدم الحالي</h5>
                        <p class="text-muted mb-0">{{ current_user.full_name }}</p>
                        <small class="text-muted">{{ 'مدير' if current_user.role == 'admin' else 'مستخدم' }}</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="settings-card text-center p-4">
                        <div class="feature-icon bg-info">
                            <i class="fas fa-cloud"></i>
                        </div>
                        <h5 class="fw-bold">منصة النشر</h5>
                        <p class="text-muted mb-0">Local Development</p>
                    </div>
                </div>
                </div>
            </div>

            <!-- إعدادات المستخدم والنظام -->
            <div class="row g-4 mb-5">
                <div class="col-md-6">
                    <div class="settings-card">
                        <div class="card-header bg-primary text-white p-4">
                            <h5 class="mb-0 fw-bold"><i class="fas fa-user-cog me-2"></i>إعدادات المستخدم</h5>
                        </div>
                        <div class="card-body p-4">
                            <form method="POST" action="{{ url_for('update_profile') }}">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">الاسم الكامل</label>
                                    <input type="text" class="form-control" name="full_name" value="{{ current_user.full_name }}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">اسم المستخدم</label>
                                    <input type="text" class="form-control" name="username" value="{{ current_user.username }}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">الدور</label>
                                    <input type="text" class="form-control" value="{{ 'مدير' if current_user.role == 'admin' else 'مستخدم' }}" readonly>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-primary btn-settings">
                                        <i class="fas fa-save me-2"></i>حفظ التغييرات
                                    </button>
                                    <button type="button" class="btn btn-warning btn-settings" data-bs-toggle="modal" data-bs-target="#changePasswordModal">
                                        <i class="fas fa-key me-2"></i>تغيير كلمة المرور
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="settings-card">
                        <div class="card-header bg-success text-white p-4">
                            <h5 class="mb-0 fw-bold"><i class="fas fa-cogs me-2"></i>إعدادات النظام</h5>
                        </div>
                        <div class="card-body p-4">
                            <form>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">اسم الشركة</label>
                                    <input type="text" class="form-control" value="شركة المحاسبة الاحترافية">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">معدل الضريبة (%)</label>
                                    <input type="number" class="form-control" value="15" step="0.01">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label fw-bold">العملة</label>
                                    <select class="form-select">
                                        <option selected>ريال سعودي (ر.س)</option>
                                        <option>دولار أمريكي ($)</option>
                                        <option>يورو (€)</option>
                                    </select>
                                </div>
                                <div class="d-grid">
                                    <button type="button" class="btn btn-success btn-settings" onclick="saveSystemSettings()">
                                        <i class="fas fa-save me-2"></i>حفظ الإعدادات
                                    </button>
                                </div>
                            </form>
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
                                            <td>{{ format_datetime('%Y-%m-%d %H:%M') }}</td>
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
            // وظائف إعدادات النظام
            function saveSystemSettings() {
                alert('تم حفظ إعدادات النظام بنجاح');
                // يمكن إضافة AJAX لحفظ الإعدادات
            }

            function confirmReset() {
                if (confirm('هل أنت متأكد من إعادة تعيين النظام؟ سيتم حذف جميع البيانات!')) {
                    alert('تم إلغاء العملية للحماية');
                }
            }

            // تحسين تجربة المستخدم
            document.addEventListener('DOMContentLoaded', function() {
                // التحقق من تطابق كلمة المرور
                const confirmPasswordInput = document.getElementById('confirm_password');
                if (confirmPasswordInput) {
                    confirmPasswordInput.addEventListener('input', function() {
                        const newPassword = document.getElementById('new_password').value;
                        const confirmPassword = this.value;

                        if (newPassword !== confirmPassword) {
                            this.setCustomValidity('كلمة المرور غير متطابقة');
                        } else {
                            this.setCustomValidity('');
                        }
                    });
                }

                // تحسين البطاقات
                const cards = document.querySelectorAll('.settings-card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-10px)';
                    });

                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });

                // تحسين الأزرار
                const buttons = document.querySelectorAll('.btn-settings');
                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        this.style.transform = 'scale(0.98)';
                        setTimeout(() => {
                            this.style.transform = 'scale(1)';
                        }, 100);
                    });
                });
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
