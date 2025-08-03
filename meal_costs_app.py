#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق تكاليف الوجبات - Meal Costs Application
تطبيق Flask لإدارة المكونات والوجبات وحساب التكاليف
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext, ngettext, lazy_gettext, get_locale
from datetime import datetime
import os

# إنشاء التطبيق
app = Flask(__name__)

# إعدادات التطبيق
app.config['SECRET_KEY'] = 'meal-costs-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meal_costs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات
db = SQLAlchemy(app)

# اللغات المدعومة
LANGUAGES = {
    'ar': 'العربية',
    'en': 'English'
}

# إعداد Babel للترجمة
babel = Babel()

def get_user_locale():
    """تحديد اللغة المطلوبة للمستخدم"""
    # 1. فحص اللغة المحفوظة في الجلسة
    if 'language' in session:
        language = session['language']
        if language in LANGUAGES.keys():
            return language

    # 2. فحص اللغة المفضلة في المتصفح
    return request.accept_languages.best_match(LANGUAGES.keys()) or 'ar'

# تهيئة Babel مع التطبيق
babel.init_app(app, locale_selector=get_user_locale)

# وظائف الترجمة المساعدة
def _(string):
    """وظيفة الترجمة المختصرة"""
    return gettext(string)

def _n(singular, plural, num):
    """وظيفة الترجمة للجمع"""
    return ngettext(singular, plural, num)

def _l(string):
    """وظيفة الترجمة المتأخرة"""
    return lazy_gettext(string)

@app.before_request
def before_request():
    """تنفيذ قبل كل طلب - تحديد اللغة الحالية"""
    g.locale = str(get_locale())
    g.language_name = LANGUAGES.get(g.locale, 'العربية')

# ===== النماذج (Models) =====

class Inventory(db.Model):
    """نموذج المخزون - المكونات"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    unit_cost = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    recipes = db.relationship('Recipe', backref='ingredient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inventory {self.name}>'

class Meal(db.Model):
    """نموذج الوجبات"""
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    recipes = db.relationship('Recipe', backref='meal', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Meal {self.name}>'
    
    def calculate_total_cost(self):
        """حساب التكلفة الإجمالية للوجبة"""
        total = 0.0
        for recipe in self.recipes:
            total += recipe.ingredient.unit_cost * recipe.quantity_required
        return total
    
    def check_stock_availability(self):
        """فحص توفر المخزون للوجبة"""
        insufficient_stock = []
        for recipe in self.recipes:
            if recipe.ingredient.stock_quantity < recipe.quantity_required:
                insufficient_stock.append({
                    'ingredient': recipe.ingredient.name,
                    'required': recipe.quantity_required,
                    'available': recipe.ingredient.stock_quantity
                })
        return insufficient_stock

class Recipe(db.Model):
    """نموذج الوصفات - ربط الوجبات بالمكونات"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # فهرس فريد لمنع تكرار المكون في نفس الوجبة
    __table_args__ = (db.UniqueConstraint('meal_id', 'ingredient_id', name='unique_meal_ingredient'),)
    
    def __repr__(self):
        return f'<Recipe {self.meal.name} - {self.ingredient.name}>'

# ===== المسارات (Routes) =====

@app.route('/')
def index():
    """الصفحة الرئيسية - إعادة توجيه لصفحة تكاليف الوجبات"""
    return redirect(url_for('meal_costs'))

@app.route('/change_lang/<language>')
def change_lang(language=None):
    """تغيير لغة التطبيق"""
    if language and language in LANGUAGES.keys():
        session['language'] = language
        flash(_('تم تغيير اللغة بنجاح') if language == 'ar' else _('Language changed successfully'), 'success')
    else:
        flash(_('اللغة المطلوبة غير مدعومة') if g.locale == 'ar' else _('Requested language is not supported'), 'error')

    # العودة للصفحة السابقة أو الصفحة الرئيسية
    return redirect(request.referrer or url_for('meal_costs'))

@app.route('/meal_costs', methods=['GET', 'POST'])
def meal_costs():
    """الصفحة الرئيسية لإدارة تكاليف الوجبات"""
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # إضافة مكون جديد
        if action == 'add_ingredient':
            name = request.form.get('ingredient_name', '').strip()
            unit_cost = request.form.get('unit_cost', 0)
            stock_quantity = request.form.get('stock_quantity', 0)
            
            try:
                unit_cost = float(unit_cost)
                stock_quantity = float(stock_quantity)
                
                if not name:
                    flash(_('❌ يرجى إدخال اسم المكون'), 'error')
                elif unit_cost <= 0:
                    flash(_('❌ يجب أن تكون تكلفة الوحدة أكبر من صفر'), 'error')
                elif stock_quantity < 0:
                    flash(_('❌ يجب أن تكون الكمية في المخزون صفر أو أكبر'), 'error')
                else:
                    # فحص عدم تكرار الاسم
                    existing = Inventory.query.filter_by(name=name).first()
                    if existing:
                        flash(_('❌ المكون "%(name)s" موجود بالفعل', name=name), 'error')
                    else:
                        ingredient = Inventory(
                            name=name,
                            unit_cost=unit_cost,
                            stock_quantity=stock_quantity
                        )
                        db.session.add(ingredient)
                        db.session.commit()
                        flash(_('✅ تم إضافة مكون جديد: %(name)s', name=name), 'success')

            except ValueError:
                flash(_('❌ يرجى إدخال قيم صحيحة للتكلفة والكمية'), 'error')
        
        # إضافة وجبة جديدة
        elif action == 'add_meal':
            name = request.form.get('meal_name', '').strip()

            if not name:
                flash(_('❌ يرجى إدخال اسم الوجبة'), 'error')
            else:
                # فحص عدم تكرار الاسم
                existing = Meal.query.filter_by(name=name).first()
                if existing:
                    flash(_('❌ الوجبة "%(name)s" موجودة بالفعل', name=name), 'error')
                else:
                    meal = Meal(name=name)
                    db.session.add(meal)
                    db.session.commit()
                    flash(_('✅ تم إضافة وجبة جديدة: %(name)s', name=name), 'success')
        
        # إضافة مكون للوصفة
        elif action == 'add_recipe':
            meal_id = request.form.get('meal_id')
            ingredient_id = request.form.get('ingredient_id')
            quantity_required = request.form.get('quantity_required', 0)
            
            try:
                meal_id = int(meal_id) if meal_id else 0
                ingredient_id = int(ingredient_id) if ingredient_id else 0
                quantity_required = float(quantity_required)
                
                if meal_id <= 0:
                    flash('❌ يرجى اختيار وجبة', 'error')
                elif ingredient_id <= 0:
                    flash('❌ يرجى اختيار مكون', 'error')
                elif quantity_required <= 0:
                    flash('❌ يجب أن تكون الكمية المطلوبة أكبر من صفر', 'error')
                else:
                    # فحص وجود الوجبة والمكون
                    meal = Meal.query.get(meal_id)
                    ingredient = Inventory.query.get(ingredient_id)
                    
                    if not meal:
                        flash('❌ الوجبة المختارة غير موجودة', 'error')
                    elif not ingredient:
                        flash('❌ المكون المختار غير موجود', 'error')
                    else:
                        # فحص عدم تكرار المكون في نفس الوجبة
                        existing = Recipe.query.filter_by(meal_id=meal_id, ingredient_id=ingredient_id).first()
                        if existing:
                            flash(f'❌ المكون "{ingredient.name}" موجود بالفعل في وصفة "{meal.name}"', 'error')
                        else:
                            recipe = Recipe(
                                meal_id=meal_id,
                                ingredient_id=ingredient_id,
                                quantity_required=quantity_required
                            )
                            db.session.add(recipe)
                            db.session.commit()
                            flash(f'✅ تم إضافة مكون "{ingredient.name}" للوصفة "{meal.name}"', 'success')
                            
            except ValueError:
                flash('❌ يرجى إدخال قيم صحيحة', 'error')
        
        # حساب تكلفة الوجبة
        elif action == 'calculate_cost':
            meal_id = request.form.get('calc_meal_id')

            try:
                meal_id = int(meal_id) if meal_id else 0

                if meal_id <= 0:
                    flash('❌ يرجى اختيار وجبة لحساب التكلفة', 'error')
                else:
                    meal = Meal.query.get(meal_id)
                    if not meal:
                        flash('❌ الوجبة المختارة غير موجودة', 'error')
                    elif not meal.recipes:
                        flash(f'❌ لا توجد وصفة للوجبة "{meal.name}"', 'error')
                    else:
                        # فحص توفر المخزون
                        insufficient_stock = meal.check_stock_availability()

                        if insufficient_stock:
                            for item in insufficient_stock:
                                flash(f'❌ لا يوجد مخزون كافي من {item["ingredient"]} (مطلوب: {item["required"]}, متوفر: {item["available"]})', 'error')
                        else:
                            # خصم المكونات من المخزون
                            cost_breakdown = []
                            total_cost = 0.0

                            for recipe in meal.recipes:
                                ingredient = recipe.ingredient
                                quantity_used = recipe.quantity_required
                                unit_cost = ingredient.unit_cost
                                ingredient_total_cost = quantity_used * unit_cost

                                # خصم من المخزون
                                ingredient.stock_quantity -= quantity_used

                                cost_breakdown.append({
                                    'ingredient_name': ingredient.name,
                                    'quantity_used': quantity_used,
                                    'unit_cost': unit_cost,
                                    'total_cost': ingredient_total_cost,
                                    'remaining_stock': ingredient.stock_quantity
                                })

                                total_cost += ingredient_total_cost

                            db.session.commit()

                            flash(f'✅ تم خصم المكونات من المخزون بنجاح', 'success')
                            flash(f'💰 التكلفة الإجمالية للوجبة "{meal.name}": {total_cost:.2f}', 'info')

                            # عرض تفاصيل التكلفة
                            for item in cost_breakdown:
                                flash(f'📊 {item["ingredient_name"]}: {item["quantity_used"]} × {item["unit_cost"]:.2f} = {item["total_cost"]:.2f} (متبقي: {item["remaining_stock"]:.2f})', 'info')

            except ValueError:
                flash('❌ يرجى اختيار وجبة صحيحة', 'error')

        return redirect(url_for('meal_costs'))

    # جلب البيانات للعرض
    ingredients = Inventory.query.order_by(Inventory.name).all()
    meals = Meal.query.order_by(Meal.name).all()
    recipes = Recipe.query.join(Meal).join(Inventory).order_by(Meal.name, Inventory.name).all()

    return render_template('meal_costs.html',
                         ingredients=ingredients,
                         meals=meals,
                         recipes=recipes)

# ===== تهيئة قاعدة البيانات =====

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    with app.app_context():
        db.create_all()
        print("✅ تم إنشاء جداول قاعدة البيانات")

        # إضافة بيانات تجريبية إذا لم تكن موجودة
        if Inventory.query.count() == 0:
            sample_ingredients = [
                Inventory(name='أرز', unit_cost=2.5, stock_quantity=100.0),
                Inventory(name='دجاج', unit_cost=15.0, stock_quantity=50.0),
                Inventory(name='خضار مشكلة', unit_cost=3.0, stock_quantity=30.0),
                Inventory(name='زيت طبخ', unit_cost=8.0, stock_quantity=20.0),
                Inventory(name='بهارات', unit_cost=5.0, stock_quantity=25.0)
            ]

            sample_meals = [
                Meal(name='كبسة دجاج'),
                Meal(name='أرز بالخضار'),
                Meal(name='دجاج مشوي')
            ]

            db.session.add_all(sample_ingredients + sample_meals)
            db.session.commit()

            # إضافة وصفات تجريبية
            sample_recipes = [
                Recipe(meal_id=1, ingredient_id=1, quantity_required=2.0),  # كبسة دجاج - أرز
                Recipe(meal_id=1, ingredient_id=2, quantity_required=1.0),  # كبسة دجاج - دجاج
                Recipe(meal_id=1, ingredient_id=5, quantity_required=0.5),  # كبسة دجاج - بهارات
                Recipe(meal_id=2, ingredient_id=1, quantity_required=1.5),  # أرز بالخضار - أرز
                Recipe(meal_id=2, ingredient_id=3, quantity_required=2.0),  # أرز بالخضار - خضار
                Recipe(meal_id=2, ingredient_id=4, quantity_required=0.3),  # أرز بالخضار - زيت
            ]

            db.session.add_all(sample_recipes)
            db.session.commit()

            print("✅ تم إضافة البيانات التجريبية")

if __name__ == '__main__':
    init_db()
    print("🚀 تشغيل تطبيق تكاليف الوجبات")
    print("🌐 الرابط: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
