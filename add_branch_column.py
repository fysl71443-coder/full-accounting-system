#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def add_branch_column():
    """إضافة عمود branch لجدول sales_invoice"""
    
    db_path = 'instance/accounting_complete.db'
    
    if not os.path.exists(db_path):
        print('❌ قاعدة البيانات غير موجودة')
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص إذا كان العمود موجود
        cursor.execute('PRAGMA table_info(sales_invoice)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'branch' not in columns:
            print('🔧 إضافة عمود branch لجدول sales_invoice...')
            
            # إضافة العمود
            cursor.execute('ALTER TABLE sales_invoice ADD COLUMN branch VARCHAR(50) DEFAULT "Place India"')
            
            # تحديث جميع السجلات الموجودة
            cursor.execute('UPDATE sales_invoice SET branch = "Place India" WHERE branch IS NULL OR branch = ""')
            
            conn.commit()
            print('✅ تم إضافة عمود branch بنجاح')
            print('✅ تم تحديث جميع السجلات الموجودة إلى Place India')
        else:
            print('✅ عمود branch موجود مسبقاً')
        
        # فحص النتيجة
        cursor.execute('SELECT COUNT(*) FROM sales_invoice')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sales_invoice WHERE branch = "Place India"')
        place_india_count = cursor.fetchone()[0]
        
        print(f'📊 إجمالي الفواتير: {total_count}')
        print(f'📊 فواتير Place India: {place_india_count}')
        
        return True
        
    except Exception as e:
        print(f'❌ خطأ: {e}')
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print('🏢 إضافة دعم الفروع لقاعدة البيانات')
    print('=' * 50)
    
    success = add_branch_column()
    
    if success:
        print('\n🎉 تم تحديث قاعدة البيانات بنجاح!')
        print('🏢 النظام الآن يدعم فرعي Place India و China Town')
    else:
        print('\n❌ فشل في تحديث قاعدة البيانات')
