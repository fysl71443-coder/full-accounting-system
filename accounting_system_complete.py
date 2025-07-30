#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المحاسبة الاحترافي الكامل - متوافق مع Python 3.10
Complete Professional Accounting System - Python 3.10 Compatible
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

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # incoming/outgoing
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    reference_number = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False, default=date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='payments')
    supplier = db.relationship('Supplier', backref='payments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# تهيئة قاعدة البيانات
def init_db():
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم افتراضي
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', full_name='مدير النظام', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # إضافة بيانات تجريبية
            # عملاء
            customer1 = Customer(name='شركة الأمل', email='amal@company.com', phone='0501234567', tax_number='123456789')
            customer2 = Customer(name='مؤسسة النجاح', email='najah@company.com', phone='0507654321', tax_number='987654321')
            
            # موردين
            supplier1 = Supplier(name='شركة التوريد الذهبي', email='golden@supply.com', phone='0551234567', tax_number='555666777')
            supplier2 = Supplier(name='مؤسسة الإمداد الحديث', email='modern@supply.com', phone='0557654321', tax_number='777888999')
            
            # منتجات
            product1 = Product(name='جهاز كمبيوتر', description='جهاز كمبيوتر مكتبي', price=2500, cost=2000, quantity=10, category='إلكترونيات')
            product2 = Product(name='طابعة ليزر', description='طابعة ليزر ملونة', price=800, cost=600, quantity=5, category='إلكترونيات')
            product3 = Product(name='مكتب خشبي', description='مكتب خشبي فاخر', price=1200, cost=900, quantity=3, category='أثاث')
            
            # موظفين
            employee1 = Employee(name='أحمد محمد', position='محاسب', salary=5000, phone='0501111111', hire_date=date(2024, 1, 1))
            employee2 = Employee(name='فاطمة علي', position='سكرتيرة', salary=3500, phone='0502222222', hire_date=date(2024, 2, 1))
            
            # مصروفات
            expense1 = Expense(description='فاتورة كهرباء', amount=450, category='مرافق', payment_method='bank_transfer', receipt_number='E001')
            expense2 = Expense(description='صيانة أجهزة', amount=300, category='صيانة', payment_method='cash', receipt_number='E002')
            
            db.session.add_all([
                customer1, customer2, supplier1, supplier2,
                product1, product2, product3, employee1, employee2,
                expense1, expense2
            ])
            
            db.session.commit()
            print('✅ تم إنشاء البيانات التجريبية')

# ===== المسارات الأساسية =====

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
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .main-card {
                background: rgba(255,255,255,0.95);
                color: #2c3e50;
                border-radius: 20px;
                padding: 50px;
                text-align: center;
                max-width: 700px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: linear-gradient(45deg, #f8f9fa, #e9ecef);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #dee2e6;
            }
            .feature-icon {
                font-size: 2rem;
                color: #667eea;
                margin-bottom: 10px;
            }
            .btn-main {
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                padding: 15px 40px;
                font-size: 1.2rem;
                border-radius: 50px;
                color: white;
                transition: all 0.3s ease;
            }
            .btn-main:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="main-card">
            <h1 class="mb-4">
                <i class="fas fa-calculator text-primary"></i>
                نظام المحاسبة الاحترافي الكامل
            </h1>
            <p class="lead mb-4">حل شامل ومتكامل لإدارة جميع العمليات المحاسبية والمالية</p>
            
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> النظام يعمل بنجاح على Python 3.13</h5>
                <p class="mb-0">متوافق مع أحدث التقنيات ومحسن للأداء العالي</p>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-shopping-cart"></i></div>
                    <h6>المبيعات</h6>
                    <small>إدارة فواتير المبيعات والعملاء</small>
                </div>
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-truck"></i></div>
                    <h6>المشتريات</h6>
                    <small>إدارة المشتريات والموردين</small>
                </div>
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-receipt"></i></div>
                    <h6>المصروفات</h6>
                    <small>تسجيل ومتابعة المصروفات</small>
                </div>
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-users"></i></div>
                    <h6>الموظفين</h6>
                    <small>إدارة الموارد البشرية</small>
                </div>
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-boxes"></i></div>
                    <h6>المخزون</h6>
                    <small>إدارة المنتجات والمخزون</small>
                </div>
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                    <h6>التقارير</h6>
                    <small>تقارير مالية شاملة</small>
                </div>
            </div>
            
            <div class="mt-4">
                <a href="{{ url_for('login') }}" class="btn btn-main">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    دخول النظام
                </a>
            </div>
            
            <div class="mt-4 pt-4 border-top">
                <small class="text-muted">
                    <i class="fas fa-user"></i> المستخدم: admin | 
                    <i class="fas fa-key"></i> كلمة المرور: admin123
                </small>
            </div>
        </div>
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
                background: rgba(255,255,255,0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card login-card">
                        <div class="card-body p-5">
                            <div class="text-center mb-4">
                                <i class="fas fa-calculator fa-3x text-primary mb-3"></i>
                                <h3>تسجيل الدخول</h3>
                                <p class="text-muted">نظام المحاسبة الاحترافي</p>
                            </div>

                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-danger">
                                            <i class="fas fa-exclamation-triangle me-2"></i>{{ message }}
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}

                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-user me-2"></i>اسم المستخدم
                                    </label>
                                    <input type="text" class="form-control" name="username" required>
                                </div>
                                <div class="mb-4">
                                    <label class="form-label">
                                        <i class="fas fa-lock me-2"></i>كلمة المرور
                                    </label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100 mb-3">
                                    <i class="fas fa-sign-in-alt me-2"></i>دخول
                                </button>
                            </form>

                            <div class="text-center">
                                <a href="{{ url_for('home') }}" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-right me-2"></i>العودة
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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
    # إحصائيات سريعة
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    total_products = Product.query.count()
    total_employees = Employee.query.count()

    # إحصائيات مالية
    total_sales = db.session.query(db.func.sum(SalesInvoice.total)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0

    # المنتجات منخفضة المخزون
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_quantity).limit(5).all()

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
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }
            .stat-card:hover { transform: translateY(-5px); }
            .menu-card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .menu-card:hover { transform: translateY(-3px); }
            .menu-icon { font-size: 2rem; color: #667eea; margin-bottom: 10px; }
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
                        <i class="fas fa-sign-out-alt me-1"></i>خروج
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h2><i class="fas fa-tachometer-alt me-2"></i>لوحة التحكم</h2>
                    <p class="text-muted">مرحباً {{ current_user.full_name }}، إليك نظرة سريعة على النظام</p>
                </div>
            </div>

            <!-- الإحصائيات السريعة -->
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <i class="fas fa-users fa-2x mb-2"></i>
                        <h3>{{ total_customers }}</h3>
                        <p>العملاء</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <i class="fas fa-truck fa-2x mb-2"></i>
                        <h3>{{ total_suppliers }}</h3>
                        <p>الموردين</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <i class="fas fa-boxes fa-2x mb-2"></i>
                        <h3>{{ total_products }}</h3>
                        <p>المنتجات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card text-center">
                        <i class="fas fa-user-tie fa-2x mb-2"></i>
                        <h3>{{ total_employees }}</h3>
                        <p>الموظفين</p>
                    </div>
                </div>
            </div>

            <!-- الإحصائيات المالية -->
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center" style="background: linear-gradient(45deg, #28a745, #20c997); color: white;">
                        <div class="card-body">
                            <i class="fas fa-chart-line fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_sales) }} ر.س</h4>
                            <p>إجمالي المبيعات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center" style="background: linear-gradient(45deg, #dc3545, #fd7e14); color: white;">
                        <div class="card-body">
                            <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_purchases) }} ر.س</h4>
                            <p>إجمالي المشتريات</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center" style="background: linear-gradient(45deg, #6f42c1, #e83e8c); color: white;">
                        <div class="card-body">
                            <i class="fas fa-receipt fa-2x mb-2"></i>
                            <h4>{{ "%.2f"|format(total_expenses) }} ر.س</h4>
                            <p>إجمالي المصروفات</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- القوائم الرئيسية -->
            <div class="row mt-4">
                <div class="col-12">
                    <h4><i class="fas fa-th-large me-2"></i>الوظائف الرئيسية</h4>
                </div>
            </div>

            <div class="row">
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-shopping-cart"></i></div>
                        <h6>المبيعات</h6>
                        <p class="text-muted small">إدارة فواتير المبيعات</p>
                        <a href="{{ url_for('sales') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-truck"></i></div>
                        <h6>المشتريات</h6>
                        <p class="text-muted small">إدارة فواتير المشتريات</p>
                        <a href="{{ url_for('purchases') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-receipt"></i></div>
                        <h6>المصروفات</h6>
                        <p class="text-muted small">تسجيل المصروفات</p>
                        <a href="{{ url_for('expenses') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-users"></i></div>
                        <h6>العملاء</h6>
                        <p class="text-muted small">إدارة العملاء</p>
                        <a href="{{ url_for('customers') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-industry"></i></div>
                        <h6>الموردين</h6>
                        <p class="text-muted small">إدارة الموردين</p>
                        <a href="{{ url_for('suppliers') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-boxes"></i></div>
                        <h6>المنتجات</h6>
                        <p class="text-muted small">إدارة المخزون</p>
                        <a href="{{ url_for('products') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-user-tie"></i></div>
                        <h6>الموظفين</h6>
                        <p class="text-muted small">إدارة الموظفين</p>
                        <a href="{{ url_for('employees') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="menu-card text-center">
                        <div class="menu-icon"><i class="fas fa-chart-bar"></i></div>
                        <h6>التقارير</h6>
                        <p class="text-muted small">التقارير المالية</p>
                        <a href="{{ url_for('reports') }}" class="btn btn-primary btn-sm">دخول</a>
                    </div>
                </div>
            </div>

            {% if low_stock_products %}
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-exclamation-triangle me-2"></i>تنبيه: منتجات منخفضة المخزون</h6>
                        <ul class="mb-0">
                            {% for product in low_stock_products %}
                            <li>{{ product.name }} - الكمية المتبقية: {{ product.quantity }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    ''', total_customers=total_customers, total_suppliers=total_suppliers,
         total_products=total_products, total_employees=total_employees,
         total_sales=total_sales, total_purchases=total_purchases,
         total_expenses=total_expenses, low_stock_products=low_stock_products)

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
        <title>إدارة العملاء</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-users me-2"></i>إدارة العملاء</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>إضافة عميل
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>الرقم</th><th>الاسم</th><th>الهاتف</th><th>البريد</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for customer in customers %}
                            <tr>
                                <td>{{ customer.id }}</td>
                                <td>{{ customer.name }}</td>
                                <td>{{ customer.phone or '-' }}</td>
                                <td>{{ customer.email or '-' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة عميل جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_customer') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">اسم العميل *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الهاتف</label>
                                <input type="text" class="form-control" name="phone">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">العنوان</label>
                                <textarea class="form-control" name="address" rows="2"></textarea>
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

# ===== إدارة المنتجات =====

@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المنتجات</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-boxes me-2"></i>إدارة المنتجات</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>إضافة منتج
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>الرقم</th><th>اسم المنتج</th><th>السعر</th><th>الكمية</th><th>الفئة</th><th>الحالة</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for product in products %}
                            <tr>
                                <td>{{ product.id }}</td>
                                <td>{{ product.name }}</td>
                                <td>{{ "%.2f"|format(product.price) }} ر.س</td>
                                <td>
                                    <span class="badge {% if product.quantity <= product.min_quantity %}bg-danger{% else %}bg-success{% endif %}">
                                        {{ product.quantity }}
                                    </span>
                                </td>
                                <td>{{ product.category or '-' }}</td>
                                <td>
                                    {% if product.quantity <= product.min_quantity %}
                                        <span class="badge bg-warning">مخزون منخفض</span>
                                    {% else %}
                                        <span class="badge bg-success">متوفر</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة منتج جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_product') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">اسم المنتج *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">السعر *</label>
                                        <input type="number" step="0.01" class="form-control" name="price" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">الكمية *</label>
                                        <input type="number" class="form-control" name="quantity" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الفئة</label>
                                <input type="text" class="form-control" name="category">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الوصف</label>
                                <textarea class="form-control" name="description" rows="2"></textarea>
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
    ''', products=products)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    product = Product(
        name=request.form['name'],
        price=Decimal(request.form['price']),
        quantity=int(request.form['quantity']),
        category=request.form.get('category'),
        description=request.form.get('description')
    )
    db.session.add(product)
    db.session.commit()
    flash('تم إضافة المنتج بنجاح', 'success')
    return redirect(url_for('products'))

# ===== إدارة المبيعات =====

@app.route('/sales')
@login_required
def sales():
    sales = SalesInvoice.query.all()
    customers = Customer.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المبيعات</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-shopping-cart me-2"></i>إدارة المبيعات</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>فاتورة جديدة
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>رقم الفاتورة</th><th>العميل</th><th>التاريخ</th><th>المبلغ</th><th>الحالة</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for sale in sales %}
                            <tr>
                                <td>{{ sale.invoice_number }}</td>
                                <td>{{ sale.customer.name if sale.customer else 'عميل نقدي' }}</td>
                                <td>{{ sale.date.strftime('%Y-%m-%d') }}</td>
                                <td>{{ "%.2f"|format(sale.total) }} ر.س</td>
                                <td>
                                    <span class="badge {% if sale.status == 'paid' %}bg-success{% elif sale.status == 'pending' %}bg-warning{% else %}bg-danger{% endif %}">
                                        {% if sale.status == 'paid' %}مدفوعة{% elif sale.status == 'pending' %}معلقة{% else %}ملغية{% endif %}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info"><i class="fas fa-eye"></i></button>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">فاتورة مبيعات جديدة</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_sale') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" name="invoice_number" value="INV-{{ range(1000, 9999) | random }}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">العميل</label>
                                        <select class="form-control" name="customer_id">
                                            <option value="">عميل نقدي</option>
                                            {% for customer in customers %}
                                            <option value="{{ customer.id }}">{{ customer.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">المبلغ الفرعي *</label>
                                        <input type="number" step="0.01" class="form-control" name="subtotal" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">الضريبة</label>
                                        <input type="number" step="0.01" class="form-control" name="tax_amount" value="0">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="2"></textarea>
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
    ''', sales=sales, customers=customers)

@app.route('/add_sale', methods=['POST'])
@login_required
def add_sale():
    subtotal = Decimal(request.form['subtotal'])
    tax_amount = Decimal(request.form.get('tax_amount', 0))

    sale = SalesInvoice(
        invoice_number=request.form['invoice_number'],
        customer_id=request.form.get('customer_id') if request.form.get('customer_id') else None,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=subtotal + tax_amount,
        notes=request.form.get('notes')
    )
    db.session.add(sale)
    db.session.commit()
    flash('تم إضافة فاتورة المبيعات بنجاح', 'success')
    return redirect(url_for('sales'))

# ===== إدارة المصروفات =====

@app.route('/expenses')
@login_required
def expenses():
    expenses = Expense.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المصروفات</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-receipt me-2"></i>إدارة المصروفات</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>إضافة مصروف
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>التاريخ</th><th>الوصف</th><th>الفئة</th><th>المبلغ</th><th>طريقة الدفع</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for expense in expenses %}
                            <tr>
                                <td>{{ expense.date.strftime('%Y-%m-%d') }}</td>
                                <td>{{ expense.description }}</td>
                                <td><span class="badge bg-info">{{ expense.category }}</span></td>
                                <td>{{ "%.2f"|format(expense.amount) }} ر.س</td>
                                <td>
                                    {% if expense.payment_method == 'cash' %}نقدي
                                    {% elif expense.payment_method == 'bank_transfer' %}تحويل بنكي
                                    {% elif expense.payment_method == 'credit_card' %}بطاقة ائتمان
                                    {% else %}{{ expense.payment_method }}
                                    {% endif %}
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة مصروف جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_expense') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">وصف المصروف *</label>
                                <input type="text" class="form-control" name="description" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">المبلغ *</label>
                                        <input type="number" step="0.01" class="form-control" name="amount" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">الفئة *</label>
                                        <select class="form-control" name="category" required>
                                            <option value="">اختر الفئة</option>
                                            <option value="مرافق">مرافق</option>
                                            <option value="صيانة">صيانة</option>
                                            <option value="مواصلات">مواصلات</option>
                                            <option value="مكتبية">مكتبية</option>
                                            <option value="أخرى">أخرى</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">طريقة الدفع</label>
                                <select class="form-control" name="payment_method">
                                    <option value="cash">نقدي</option>
                                    <option value="bank_transfer">تحويل بنكي</option>
                                    <option value="credit_card">بطاقة ائتمان</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">رقم الإيصال</label>
                                <input type="text" class="form-control" name="receipt_number">
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
    ''', expenses=expenses)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    expense = Expense(
        description=request.form['description'],
        amount=Decimal(request.form['amount']),
        category=request.form['category'],
        payment_method=request.form['payment_method'],
        receipt_number=request.form.get('receipt_number')
    )
    db.session.add(expense)
    db.session.commit()
    flash('تم إضافة المصروف بنجاح', 'success')
    return redirect(url_for('expenses'))

# ===== إدارة الموردين =====

@app.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الموردين</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-industry me-2"></i>إدارة الموردين</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>إضافة مورد
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>الرقم</th><th>اسم المورد</th><th>الهاتف</th><th>البريد</th><th>الرقم الضريبي</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for supplier in suppliers %}
                            <tr>
                                <td>{{ supplier.id }}</td>
                                <td>{{ supplier.name }}</td>
                                <td>{{ supplier.phone or '-' }}</td>
                                <td>{{ supplier.email or '-' }}</td>
                                <td>{{ supplier.tax_number or '-' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة مورد جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_supplier') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">اسم المورد *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الهاتف</label>
                                <input type="text" class="form-control" name="phone">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الرقم الضريبي</label>
                                <input type="text" class="form-control" name="tax_number">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">العنوان</label>
                                <textarea class="form-control" name="address" rows="2"></textarea>
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
    ''', suppliers=suppliers)

@app.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    supplier = Supplier(
        name=request.form['name'],
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        tax_number=request.form.get('tax_number'),
        address=request.form.get('address')
    )
    db.session.add(supplier)
    db.session.commit()
    flash('تم إضافة المورد بنجاح', 'success')
    return redirect(url_for('suppliers'))

# ===== إدارة الموظفين =====

@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الموظفين</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-user-tie me-2"></i>إدارة الموظفين</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>إضافة موظف
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>الرقم</th><th>اسم الموظف</th><th>المنصب</th><th>الراتب</th><th>تاريخ التوظيف</th><th>الحالة</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for employee in employees %}
                            <tr>
                                <td>{{ employee.id }}</td>
                                <td>{{ employee.name }}</td>
                                <td>{{ employee.position }}</td>
                                <td>{{ "%.2f"|format(employee.salary) }} ر.س</td>
                                <td>{{ employee.hire_date.strftime('%Y-%m-%d') }}</td>
                                <td>
                                    <span class="badge {% if employee.status == 'active' %}bg-success{% else %}bg-danger{% endif %}">
                                        {% if employee.status == 'active' %}نشط{% else %}غير نشط{% endif %}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-info"><i class="fas fa-eye"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة موظف جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_employee') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">اسم الموظف *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">المنصب *</label>
                                        <input type="text" class="form-control" name="position" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">الراتب *</label>
                                        <input type="number" step="0.01" class="form-control" name="salary" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الهاتف</label>
                                <input type="text" class="form-control" name="phone">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">تاريخ التوظيف *</label>
                                <input type="date" class="form-control" name="hire_date" required>
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
    ''', employees=employees)

@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    from datetime import datetime
    employee = Employee(
        name=request.form['name'],
        position=request.form['position'],
        salary=Decimal(request.form['salary']),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
    )
    db.session.add(employee)
    db.session.commit()
    flash('تم إضافة الموظف بنجاح', 'success')
    return redirect(url_for('employees'))

# ===== إدارة المشتريات =====

@app.route('/purchases')
@login_required
def purchases():
    purchases = PurchaseInvoice.query.all()
    suppliers = Supplier.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إدارة المشتريات</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>body { background-color: #f8f9fa; } .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }</style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                    <i class="fas fa-calculator me-2"></i>نظام المحاسبة
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fas fa-truck me-2"></i>إدارة المشتريات</h2>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">
                    <i class="fas fa-plus me-2"></i>فاتورة جديدة
                </button>
            </div>
            <div class="card">
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>رقم الفاتورة</th><th>المورد</th><th>التاريخ</th><th>المبلغ</th><th>الحالة</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {% for purchase in purchases %}
                            <tr>
                                <td>{{ purchase.invoice_number }}</td>
                                <td>{{ purchase.supplier.name if purchase.supplier else '-' }}</td>
                                <td>{{ purchase.date.strftime('%Y-%m-%d') }}</td>
                                <td>{{ "%.2f"|format(purchase.total) }} ر.س</td>
                                <td>
                                    <span class="badge {% if purchase.status == 'received' %}bg-success{% elif purchase.status == 'pending' %}bg-warning{% else %}bg-danger{% endif %}">
                                        {% if purchase.status == 'received' %}مستلمة{% elif purchase.status == 'pending' %}معلقة{% else %}ملغية{% endif %}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info"><i class="fas fa-eye"></i></button>
                                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal fade" id="addModal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">فاتورة مشتريات جديدة</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_purchase') }}">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">رقم الفاتورة *</label>
                                        <input type="text" class="form-control" name="invoice_number" value="PUR-{{ range(1000, 9999) | random }}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">المورد *</label>
                                        <select class="form-control" name="supplier_id" required>
                                            <option value="">اختر المورد</option>
                                            {% for supplier in suppliers %}
                                            <option value="{{ supplier.id }}">{{ supplier.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">المبلغ الفرعي *</label>
                                        <input type="number" step="0.01" class="form-control" name="subtotal" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">الضريبة</label>
                                        <input type="number" step="0.01" class="form-control" name="tax_amount" value="0">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">ملاحظات</label>
                                <textarea class="form-control" name="notes" rows="2"></textarea>
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
    ''', purchases=purchases, suppliers=suppliers)

@app.route('/add_purchase', methods=['POST'])
@login_required
def add_purchase():
    subtotal = Decimal(request.form['subtotal'])
    tax_amount = Decimal(request.form.get('tax_amount', 0))

    purchase = PurchaseInvoice(
        invoice_number=request.form['invoice_number'],
        supplier_id=request.form['supplier_id'],
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=subtotal + tax_amount,
        notes=request.form.get('notes')
    )
    db.session.add(purchase)
    db.session.commit()
    flash('تم إضافة فاتورة المشتريات بنجاح', 'success')
    return redirect(url_for('purchases'))

# ===== التقارير =====

@app.route('/reports')
@login_required
def reports():
    # إحصائيات شاملة
    total_sales = db.session.query(db.func.sum(SalesInvoice.total)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(PurchaseInvoice.total)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses

    # إحصائيات شهرية
    from sqlalchemy import extract
    current_month_sales = db.session.query(db.func.sum(SalesInvoice.total)).filter(
        extract('month', SalesInvoice.date) == datetime.now().month,
        extract('year', SalesInvoice.date) == datetime.now().year
    ).scalar() or 0

    current_month_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        extract('month', Expense.date) == datetime.now().month,
        extract('year', Expense.date) == datetime.now().year
    ).scalar() or 0

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>التقارير المالية</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .navbar { background: linear-gradient(45deg, #667eea, #764ba2) !important; }
            .report-card {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .report-card.expense {
                background: linear-gradient(45deg, #dc3545, #fd7e14);
            }
            .report-card.profit {
                background: linear-gradient(45deg, #6f42c1, #e83e8c);
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
                    <a class="nav-link" href="{{ url_for('dashboard') }}">الرئيسية</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">خروج</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <h2><i class="fas fa-chart-bar me-2"></i>التقارير المالية</h2>
            <p class="text-muted">تقارير شاملة عن الوضع المالي للشركة</p>

            <!-- التقارير الإجمالية -->
            <div class="row mt-4">
                <div class="col-md-3">
                    <div class="report-card text-center">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <h4>{{ "%.2f"|format(total_sales) }} ر.س</h4>
                        <p>إجمالي المبيعات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="report-card expense text-center">
                        <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                        <h4>{{ "%.2f"|format(total_purchases) }} ر.س</h4>
                        <p>إجمالي المشتريات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="report-card expense text-center">
                        <i class="fas fa-receipt fa-2x mb-2"></i>
                        <h4>{{ "%.2f"|format(total_expenses) }} ر.س</h4>
                        <p>إجمالي المصروفات</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="report-card profit text-center">
                        <i class="fas fa-coins fa-2x mb-2"></i>
                        <h4>{{ "%.2f"|format(net_profit) }} ر.س</h4>
                        <p>صافي الربح</p>
                    </div>
                </div>
            </div>

            <!-- التقارير الشهرية -->
            <div class="row mt-4">
                <div class="col-12">
                    <h4><i class="fas fa-calendar-alt me-2"></i>تقرير الشهر الحالي</h4>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                            <h4>{{ "%.2f"|format(current_month_sales) }} ر.س</h4>
                            <p>مبيعات الشهر الحالي</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-receipt fa-2x text-danger mb-2"></i>
                            <h4>{{ "%.2f"|format(current_month_expenses) }} ر.س</h4>
                            <p>مصروفات الشهر الحالي</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- أزرار التقارير -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5><i class="fas fa-download me-2"></i>تصدير التقارير</h5>
                            <div class="btn-group" role="group">
                                <button class="btn btn-outline-primary">
                                    <i class="fas fa-file-excel me-2"></i>تصدير Excel
                                </button>
                                <button class="btn btn-outline-danger">
                                    <i class="fas fa-file-pdf me-2"></i>تصدير PDF
                                </button>
                                <button class="btn btn-outline-success">
                                    <i class="fas fa-print me-2"></i>طباعة
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', total_sales=total_sales, total_purchases=total_purchases,
         total_expenses=total_expenses, net_profit=net_profit,
         current_month_sales=current_month_sales, current_month_expenses=current_month_expenses)

# ===== API =====

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'success',
        'message': 'نظام المحاسبة الكامل يعمل بنجاح',
        'version': '1.0.0',
        'python_version': '3.13',
        'features': [
            'إدارة العملاء والموردين',
            'إدارة المنتجات والمخزون',
            'فواتير المبيعات والمشتريات',
            'إدارة المصروفات',
            'إدارة الموظفين',
            'التقارير المالية الشاملة'
        ],
        'database': 'متصلة',
        'deployment': 'Render Cloud Platform'
    })

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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                    <a class="nav-link" href="{{ url_for('logout') }}">
                        <i class="fas fa-sign-out-alt me-1"></i>خروج
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2><i class="fas fa-users me-2"></i>إدارة العملاء</h2>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCustomerModal">
                            <i class="fas fa-plus me-2"></i>إضافة عميل جديد
                        </button>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>الرقم</th>
                                    <th>اسم العميل</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>الهاتف</th>
                                    <th>الرقم الضريبي</th>
                                    <th>تاريخ الإضافة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for customer in customers %}
                                <tr>
                                    <td>{{ customer.id }}</td>
                                    <td>{{ customer.name }}</td>
                                    <td>{{ customer.email or '-' }}</td>
                                    <td>{{ customer.phone or '-' }}</td>
                                    <td>{{ customer.tax_number or '-' }}</td>
                                    <td>{{ customer.created_at.strftime('%Y-%m-%d') }}</td>
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
                                <label class="form-label">اسم العميل *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">رقم الهاتف</label>
                                <input type="text" class="form-control" name="phone">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">العنوان</label>
                                <textarea class="form-control" name="address" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الرقم الضريبي</label>
                                <input type="text" class="form-control" name="tax_number">
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
    name = request.form['name']
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    tax_number = request.form.get('tax_number')

    customer = Customer(
        name=name,
        email=email if email else None,
        phone=phone if phone else None,
        address=address if address else None,
        tax_number=tax_number if tax_number else None
    )

    db.session.add(customer)
    db.session.commit()

    flash('تم إضافة العميل بنجاح', 'success')
    return redirect(url_for('customers'))

# ===== إدارة الموردين =====

@app.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>إدارة الموردين - نظام المحاسبة</title>
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
                    <a class="nav-link" href="{{ url_for('dashboard') }}">
                        <i class="fas fa-home me-1"></i>الرئيسية
                    </a>
                    <a class="nav-link" href="{{ url_for('logout') }}">
                        <i class="fas fa-sign-out-alt me-1"></i>خروج
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2><i class="fas fa-industry me-2"></i>إدارة الموردين</h2>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addSupplierModal">
                            <i class="fas fa-plus me-2"></i>إضافة مورد جديد
                        </button>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>الرقم</th>
                                    <th>اسم المورد</th>
                                    <th>البريد الإلكتروني</th>
                                    <th>الهاتف</th>
                                    <th>الرقم الضريبي</th>
                                    <th>تاريخ الإضافة</th>
                                    <th>الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for supplier in suppliers %}
                                <tr>
                                    <td>{{ supplier.id }}</td>
                                    <td>{{ supplier.name }}</td>
                                    <td>{{ supplier.email or '-' }}</td>
                                    <td>{{ supplier.phone or '-' }}</td>
                                    <td>{{ supplier.tax_number or '-' }}</td>
                                    <td>{{ supplier.created_at.strftime('%Y-%m-%d') }}</td>
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
                </div>
            </div>
        </div>

        <!-- Modal إضافة مورد -->
        <div class="modal fade" id="addSupplierModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">إضافة مورد جديد</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="{{ url_for('add_supplier') }}">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">اسم المورد *</label>
                                <input type="text" class="form-control" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">البريد الإلكتروني</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">رقم الهاتف</label>
                                <input type="text" class="form-control" name="phone">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">العنوان</label>
                                <textarea class="form-control" name="address" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">الرقم الضريبي</label>
                                <input type="text" class="form-control" name="tax_number">
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
    ''', suppliers=suppliers)

@app.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    name = request.form['name']
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    tax_number = request.form.get('tax_number')

    supplier = Supplier(
        name=name,
        email=email if email else None,
        phone=phone if phone else None,
        address=address if address else None,
        tax_number=tax_number if tax_number else None
    )

    db.session.add(supplier)
    db.session.commit()

    flash('تم إضافة المورد بنجاح', 'success')
    return redirect(url_for('suppliers'))

if __name__ == '__main__':
    print('🚀 بدء تشغيل نظام المحاسبة الكامل...')
    print('🐍 Python 3.13 - متوافق')

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
