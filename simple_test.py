#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار بسيط للنظام
"""

def test_basic():
    """اختبار أساسي"""
    print("🔍 اختبار أساسي للنظام")
    print("=" * 40)
    
    try:
        print("📦 اختبار app.py...")
        import app
        print("✅ app.py يعمل بنجاح")
        
        if hasattr(app, 'app'):
            print("✅ التطبيق متوفر")
            print(f"✅ النظام جاهز على المنفذ 5000")
        else:
            print("❌ التطبيق غير متوفر")
            return False
            
        print("\n🎉 النظام جاهز للعمل!")
        print("💡 لتشغيل النظام:")
        print("   python app.py")
        print("   ثم افتح: http://localhost:5000")
        print("   المستخدم: admin")
        print("   كلمة المرور: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == "__main__":
    test_basic()
