#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تحديث قاعدة البيانات لإضافة الحقول الجديدة
"""

import sqlite3
import os
from datetime import datetime

def update_database():
    """تحديث قاعدة البيانات بالحقول الجديدة"""
    
    db_path = 'accounting_system.db'
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 بدء تحديث قاعدة البيانات...")
        
        # تحديث جدول SalesInvoice
        print("📝 تحديث جدول فواتير المبيعات...")
        
        # إضافة الحقول الجديدة لجدول SalesInvoice
        new_sales_columns = [
            ('tax_rate', 'NUMERIC(5, 2) DEFAULT 15.0'),
            ('has_tax', 'BOOLEAN DEFAULT 1'),
            ('payment_method', 'VARCHAR(20) DEFAULT "cash"')
        ]
        
        for column_name, column_def in new_sales_columns:
            try:
                cursor.execute(f'ALTER TABLE sales_invoice ADD COLUMN {column_name} {column_def}')
                print(f"✅ تم إضافة العمود {column_name} لجدول فواتير المبيعات")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  العمود {column_name} موجود مسبقاً")
                else:
                    print(f"❌ خطأ في إضافة العمود {column_name}: {e}")
        
        # إنشاء جدول أصناف فواتير المبيعات
        print("📝 إنشاء جدول أصناف فواتير المبيعات...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_invoice_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name VARCHAR(200) NOT NULL,
                description TEXT,
                quantity NUMERIC(10, 3) NOT NULL DEFAULT 1.0,
                unit_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                total_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                FOREIGN KEY (invoice_id) REFERENCES sales_invoice (id),
                FOREIGN KEY (product_id) REFERENCES product (id)
            )
        ''')
        print("✅ تم إنشاء جدول أصناف فواتير المبيعات")
        
        # تحديث جدول PurchaseInvoice
        print("📝 تحديث جدول فواتير المشتريات...")
        
        # إضافة الحقول الجديدة لجدول PurchaseInvoice
        new_purchase_columns = [
            ('tax_rate', 'NUMERIC(5, 2) DEFAULT 15.0'),
            ('has_tax', 'BOOLEAN DEFAULT 1'),
            ('payment_method', 'VARCHAR(20) DEFAULT "cash"')
        ]
        
        for column_name, column_def in new_purchase_columns:
            try:
                cursor.execute(f'ALTER TABLE purchase_invoice ADD COLUMN {column_name} {column_def}')
                print(f"✅ تم إضافة العمود {column_name} لجدول فواتير المشتريات")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  العمود {column_name} موجود مسبقاً")
                else:
                    print(f"❌ خطأ في إضافة العمود {column_name}: {e}")
        
        # إنشاء جدول أصناف فواتير المشتريات
        print("📝 إنشاء جدول أصناف فواتير المشتريات...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_invoice_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name VARCHAR(200) NOT NULL,
                description TEXT,
                quantity NUMERIC(10, 3) NOT NULL DEFAULT 1.0,
                unit_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                total_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                FOREIGN KEY (invoice_id) REFERENCES purchase_invoice (id),
                FOREIGN KEY (product_id) REFERENCES product (id)
            )
        ''')
        print("✅ تم إنشاء جدول أصناف فواتير المشتريات")
        
        # تحديث جدول Employee
        print("📝 تحديث جدول الموظفين...")
        
        # إضافة الحقول الجديدة لجدول Employee
        new_employee_columns = [
            ('working_days', 'INTEGER DEFAULT 30'),
            ('overtime_rate', 'NUMERIC(10, 2) DEFAULT 0.0'),
            ('allowances', 'NUMERIC(10, 2) DEFAULT 0.0'),
            ('deductions', 'NUMERIC(10, 2) DEFAULT 0.0')
        ]
        
        for column_name, column_def in new_employee_columns:
            try:
                cursor.execute(f'ALTER TABLE employee ADD COLUMN {column_name} {column_def}')
                print(f"✅ تم إضافة العمود {column_name} لجدول الموظفين")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️  العمود {column_name} موجود مسبقاً")
                else:
                    print(f"❌ خطأ في إضافة العمود {column_name}: {e}")
        
        # إنشاء جدول كشوف الرواتب
        print("📝 إنشاء جدول كشوف الرواتب...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_payroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                basic_salary NUMERIC(10, 2) NOT NULL,
                working_days INTEGER DEFAULT 30,
                actual_working_days INTEGER DEFAULT 30,
                overtime_hours NUMERIC(8, 2) DEFAULT 0.0,
                overtime_amount NUMERIC(10, 2) DEFAULT 0.0,
                allowances NUMERIC(10, 2) DEFAULT 0.0,
                deductions NUMERIC(10, 2) DEFAULT 0.0,
                gross_salary NUMERIC(10, 2) NOT NULL,
                net_salary NUMERIC(10, 2) NOT NULL,
                notes TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                payment_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employee (id)
            )
        ''')
        print("✅ تم إنشاء جدول كشوف الرواتب")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حفظ جميع التغييرات بنجاح!")
        
        # عرض إحصائيات الجداول
        print("\n📊 إحصائيات قاعدة البيانات:")
        
        tables = [
            'sales_invoice', 'sales_invoice_item', 
            'purchase_invoice', 'purchase_invoice_item',
            'employee', 'employee_payroll'
        ]
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"   📋 {table}: {count} سجل")
            except sqlite3.OperationalError:
                print(f"   ❌ الجدول {table} غير موجود")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("🚀 تحديث قاعدة البيانات - نظام المحاسبة الاحترافي")
    print("=" * 50)
    
    success = update_database()
    
    if success:
        print("\n🎉 تم تحديث قاعدة البيانات بنجاح!")
        print("✅ يمكنك الآن تشغيل النظام باستخدام: python run_system.py")
    else:
        print("\n❌ فشل في تحديث قاعدة البيانات!")
        print("💡 تأكد من وجود ملف accounting_system.db")
    
    print("=" * 50)
