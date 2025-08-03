# 🌐 دليل نظام الترجمة الثنائي - Bilingual Translation System Guide

## 📋 نظرة عامة - Overview

تم تطوير نظام ترجمة ثنائي كامل للتطبيق يدعم العربية والإنجليزية مع تبديل فوري بين اللغات.

A complete bilingual translation system has been developed for the application supporting Arabic and English with instant language switching.

## 🚀 التثبيت والإعداد - Installation & Setup

### 1. تثبيت المتطلبات - Install Requirements

```bash
pip install -r meal_requirements.txt
```

المكتبات المطلوبة - Required Libraries:
- Flask==2.3.3
- Flask-SQLAlchemy==3.0.5
- Flask-Babel==4.0.0
- Babel==2.12.1

### 2. تجميع ملفات الترجمة - Compile Translation Files

```bash
python compile_translations.py
```

أو يدوياً - Or manually:

```bash
# استخراج النصوص - Extract strings
pybabel extract -F meal_babel.cfg -k _l -o messages.pot .

# تحديث الترجمات - Update translations
pybabel update -i messages.pot -d translations -l ar
pybabel update -i messages.pot -d translations -l en

# تجميع الترجمات - Compile translations
pybabel compile -d translations -l ar
pybabel compile -d translations -l en
```

## 📁 هيكل الملفات - File Structure

```
meal_costs_app/
├── meal_costs_app.py          # التطبيق الرئيسي مع دعم Babel
├── meal_babel.cfg             # إعدادات Babel
├── compile_translations.py    # سكريبت تجميع الترجمات
├── meal_requirements.txt      # المتطلبات
├── templates/
│   ├── meal_base.html        # القالب الأساسي مع مبدل اللغة
│   └── meal_costs.html       # الصفحة الرئيسية مع الترجمة
└── translations/
    ├── ar/LC_MESSAGES/
    │   ├── messages.po       # ملف الترجمة العربية
    │   └── messages.mo       # ملف الترجمة المجمع
    └── en/LC_MESSAGES/
        ├── messages.po       # ملف الترجمة الإنجليزية
        └── messages.mo       # ملف الترجمة المجمع
```

## 🔧 الميزات المطبقة - Implemented Features

### 1. دعم اللغات - Language Support
- ✅ العربية (ar) مع دعم RTL
- ✅ الإنجليزية (en) مع دعم LTR
- ✅ تبديل فوري بين اللغات
- ✅ حفظ تفضيل اللغة في الجلسة

### 2. واجهة المستخدم - User Interface
- ✅ مبدل اللغة في الشريط العلوي
- ✅ Bootstrap RTL/LTR تلقائي
- ✅ أيقونات وتخطيط متجاوب
- ✅ رسائل فلاش مترجمة

### 3. الترجمة الشاملة - Complete Translation
- ✅ جميع النصوص في Python
- ✅ جميع النصوص في القوالب
- ✅ رسائل النجاح والخطأ
- ✅ تسميات النماذج والأزرار

## 🎯 كيفية الاستخدام - How to Use

### 1. تشغيل التطبيق - Run Application

```bash
python meal_costs_app.py
```

### 2. تبديل اللغة - Switch Language

- انقر على مبدل اللغة في الشريط العلوي
- اختر العربية أو English
- سيتم تحديث الصفحة فوراً

### 3. إضافة ترجمات جديدة - Add New Translations

#### في Python:
```python
# استخدم وظيفة _() للترجمة
flash(_('رسالة جديدة'), 'success')

# للرسائل مع متغيرات
flash(_('تم إضافة %(name)s بنجاح', name=item_name), 'success')
```

#### في القوالب:
```html
<!-- للنصوص العادية -->
<h1>{{ _('عنوان الصفحة') }}</h1>

<!-- للخصائص -->
<input placeholder="{{ _('أدخل النص هنا') }}">

<!-- مع متغيرات -->
<p>{{ _('مرحباً %(name)s', name=user.name) }}</p>
```

### 4. تحديث الترجمات - Update Translations

1. أضف النصوص الجديدة في الكود
2. شغل سكريبت التحديث:
```bash
python compile_translations.py
```
3. حدث ملفات .po في مجلد translations
4. أعد تشغيل التطبيق

## 🔍 اختبار النظام - Testing System

```bash
# اختبار سريع
python -c "from meal_costs_app import app, _; print('✅ Babel working')"

# اختبار شامل
python -c "
with app.app_context():
    print(_('تكاليف الوجبات'))  # يجب أن يطبع الترجمة
"
```

## 🌐 المسارات المتاحة - Available Routes

- `/` - الصفحة الرئيسية
- `/meal_costs` - صفحة تكاليف الوجبات
- `/change_lang/ar` - تغيير للعربية
- `/change_lang/en` - تغيير للإنجليزية

## 🎨 التخصيص - Customization

### إضافة لغة جديدة - Add New Language

1. أضف اللغة في `LANGUAGES`:
```python
LANGUAGES = {
    'ar': 'العربية',
    'en': 'English',
    'fr': 'Français'  # لغة جديدة
}
```

2. أنشئ مجلد الترجمة:
```bash
mkdir -p translations/fr/LC_MESSAGES
```

3. أنشئ ملف الترجمة:
```bash
pybabel init -i messages.pot -d translations -l fr
```

4. حدث القالب لإضافة اللغة في المبدل

## 🐛 حل المشاكل - Troubleshooting

### مشكلة: الترجمة لا تعمل
```bash
# تأكد من تجميع الترجمات
pybabel compile -d translations -l ar
pybabel compile -d translations -l en
```

### مشكلة: RTL لا يعمل
- تأكد من `dir="{{ 'rtl' if g.locale == 'ar' else 'ltr' }}"` في HTML
- تأكد من استخدام Bootstrap RTL للعربية

### مشكلة: مبدل اللغة لا يظهر
- تأكد من `g.locale` و `g.language_name` في `before_request`
- تأكد من Bootstrap JavaScript

## 📞 الدعم - Support

للمساعدة أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

For help or to report issues, please contact the development team.

---

🎉 **نظام الترجمة الثنائي جاهز للاستخدام!**
🎉 **Bilingual Translation System Ready to Use!**
