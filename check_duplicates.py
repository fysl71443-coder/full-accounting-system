#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص شامل للتعريفات المكررة في النظام
"""

import re
import sys

def check_duplicate_routes():
    """البحث عن routes مكررة"""
    print("🔍 فحص Routes المكررة...")
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع الـ routes
    route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"]'
    routes = re.findall(route_pattern, content)
    
    # البحث عن المكررات
    route_counts = {}
    for route in routes:
        route_counts[route] = route_counts.get(route, 0) + 1
    
    duplicates = {route: count for route, count in route_counts.items() if count > 1}
    
    if duplicates:
        print("❌ تم العثور على routes مكررة:")
        for route, count in duplicates.items():
            print(f"   - {route}: {count} مرات")
        return False
    else:
        print("✅ لا توجد routes مكررة")
        return True

def check_duplicate_functions():
    """البحث عن وظائف مكررة"""
    print("\n🔍 فحص الوظائف المكررة...")
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # البحث عن جميع الوظائف مع أرقام الأسطر
    function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    functions = {}
    
    for line_num, line in enumerate(lines, 1):
        match = re.search(function_pattern, line)
        if match:
            func_name = match.group(1)
            if func_name not in functions:
                functions[func_name] = []
            functions[func_name].append(line_num)
    
    # البحث عن المكررات
    duplicates = {func: lines for func, lines in functions.items() if len(lines) > 1}
    
    if duplicates:
        print("❌ تم العثور على وظائف مكررة:")
        for func, line_nums in duplicates.items():
            print(f"   - {func}: في الأسطر {line_nums}")
        return False
    else:
        print("✅ لا توجد وظائف مكررة")
        return True

def check_specific_functions():
    """فحص وظائف محددة قد تكون مكررة"""
    print("\n🔍 فحص وظائف محددة...")
    
    critical_functions = [
        'delete_employee',
        'print_invoice', 
        'print_purchase',
        'add_sale',
        'add_purchase',
        'add_employee'
    ]
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_good = True
    
    for func_name in critical_functions:
        pattern = rf'def\s+{func_name}\s*\('
        matches = re.findall(pattern, content)
        count = len(matches)
        
        if count > 1:
            print(f"❌ {func_name}: {count} تعريفات")
            all_good = False
        elif count == 1:
            print(f"✅ {func_name}: تعريف واحد")
        else:
            print(f"⚠️  {func_name}: غير موجود")
    
    return all_good

def check_route_function_mapping():
    """فحص تطابق Routes مع الوظائف"""
    print("\n🔍 فحص تطابق Routes مع الوظائف...")
    
    with open('accounting_system_complete.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    route_function_pairs = []
    current_route = None
    
    for i, line in enumerate(lines):
        # البحث عن route
        route_match = re.search(r'@app\.route\([\'"]([^\'"]+)[\'"]', line)
        if route_match:
            current_route = route_match.group(1)
        
        # البحث عن الوظيفة التالية
        func_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
        if func_match and current_route:
            func_name = func_match.group(1)
            route_function_pairs.append((current_route, func_name, i+1))
            current_route = None
    
    # فحص التكرارات
    route_funcs = {}
    for route, func, line_num in route_function_pairs:
        key = f"{route} -> {func}"
        if key not in route_funcs:
            route_funcs[key] = []
        route_funcs[key].append(line_num)
    
    duplicates = {key: lines for key, lines in route_funcs.items() if len(lines) > 1}
    
    if duplicates:
        print("❌ تم العثور على تطابقات مكررة:")
        for mapping, line_nums in duplicates.items():
            print(f"   - {mapping}: في الأسطر {line_nums}")
        return False
    else:
        print("✅ جميع التطابقات فريدة")
        return True

def main():
    """الوظيفة الرئيسية"""
    print("🔍 فحص شامل للتعريفات المكررة")
    print("=" * 50)
    
    checks = [
        check_duplicate_routes(),
        check_duplicate_functions(), 
        check_specific_functions(),
        check_route_function_mapping()
    ]
    
    all_passed = all(checks)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 جميع الفحوصات نجحت!")
        print("✅ لا توجد تعريفات مكررة")
        print("✅ النظام جاهز للتشغيل")
    else:
        print("❌ توجد مشاكل تحتاج إصلاح!")
        print("💡 يرجى مراجعة التعريفات المكررة أعلاه")
    
    print("=" * 50)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
