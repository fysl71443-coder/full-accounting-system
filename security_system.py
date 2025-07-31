#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ نظام الحماية المتقدم ضد الهاكرز
Advanced Security System Against Hackers

يوفر حماية شاملة ضد:
- هجمات SQL Injection
- هجمات XSS (Cross-Site Scripting)
- هجمات CSRF (Cross-Site Request Forgery)
- هجمات Brute Force
- هجمات DDoS
- محاولات الاختراق
- تسريب البيانات
"""

import os
import re
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from flask import request, abort, session, jsonify, redirect, url_for
try:
    import ipaddress
except ImportError:
    ipaddress = None

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    generate_password_hash = None

try:
    import jwt
except ImportError:
    jwt = None

class SecuritySystem:
    """نظام الحماية الرئيسي"""
    
    def __init__(self, app=None):
        self.app = app
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_activities = defaultdict(list)
        self.rate_limits = defaultdict(list)
        self.security_tokens = {}
        
        # إعدادات الحماية
        self.MAX_LOGIN_ATTEMPTS = 5
        self.BLOCK_DURATION = 3600  # ساعة واحدة
        self.RATE_LIMIT_REQUESTS = 100
        self.RATE_LIMIT_WINDOW = 300  # 5 دقائق
        self.SESSION_TIMEOUT = 1800  # 30 دقيقة
        
        # إعداد نظام السجلات
        self.setup_logging()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة النظام مع Flask"""
        self.app = app
        
        # إعدادات الأمان
        app.config.update({
            'SECRET_KEY': self.generate_secure_key(),
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'PERMANENT_SESSION_LIFETIME': timedelta(minutes=30),
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 3600
        })
        
        # تطبيق الحماية على جميع الطلبات
        app.before_request(self.security_check)
        app.after_request(self.add_security_headers)
        
        # معالج الأخطاء الأمنية
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(429)(self.handle_rate_limit)
    
    def setup_logging(self):
        """إعداد نظام السجلات الأمنية"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecuritySystem')
    
    def generate_secure_key(self):
        """إنشاء مفتاح أمان قوي"""
        return secrets.token_urlsafe(64)
    
    def get_client_ip(self):
        """الحصول على IP العميل الحقيقي"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr
    
    def is_ip_blocked(self, ip):
        """فحص ما إذا كان IP محظور"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip, reason="Suspicious activity"):
        """حظر IP مع تسجيل السبب"""
        self.blocked_ips.add(ip)
        self.logger.warning(f"🚫 IP محظور: {ip} - السبب: {reason}")
        
        # إزالة الحظر بعد فترة
        def unblock_later():
            time.sleep(self.BLOCK_DURATION)
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
                self.logger.info(f"✅ تم رفع الحظر عن IP: {ip}")
        
        import threading
        threading.Thread(target=unblock_later, daemon=True).start()
    
    def check_rate_limit(self, ip):
        """فحص حد المعدل للطلبات"""
        now = time.time()
        window_start = now - self.RATE_LIMIT_WINDOW
        
        # تنظيف الطلبات القديمة
        self.rate_limits[ip] = [
            timestamp for timestamp in self.rate_limits[ip]
            if timestamp > window_start
        ]
        
        # إضافة الطلب الحالي
        self.rate_limits[ip].append(now)
        
        # فحص تجاوز الحد
        if len(self.rate_limits[ip]) > self.RATE_LIMIT_REQUESTS:
            self.block_ip(ip, "Rate limit exceeded")
            return False
        
        return True
    
    def detect_sql_injection(self, data):
        """كشف محاولات SQL Injection"""
        if not data:
            return False
        
        # أنماط SQL Injection الشائعة
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\bUNION\s+SELECT\b)",
            r"(\b(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)\b)",
            r"([\'\"];?\s*(DROP|DELETE|INSERT|UPDATE))",
            r"(\b(EXEC|EXECUTE)\s*\()",
            r"(\b(SP_|XP_)\w+)",
            r"(WAITFOR\s+DELAY)"
        ]
        
        data_str = str(data).upper()
        for pattern in sql_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        
        return False
    
    def detect_xss(self, data):
        """كشف محاولات XSS"""
        if not data:
            return False
        
        # أنماط XSS الشائعة
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"vbscript:",
            r"expression\s*\(",
            r"@import",
            r"<svg[^>]*>.*?</svg>",
            r"<img[^>]*onerror",
            r"<body[^>]*onload"
        ]
        
        data_str = str(data)
        for pattern in xss_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        
        return False
    
    def detect_path_traversal(self, data):
        """كشف محاولات Path Traversal"""
        if not data:
            return False
        
        dangerous_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
            r"..%2f",
            r"..%5c",
            r"%252e%252e%252f",
            r"....//",
            r"....\\\\",
        ]
        
        data_str = str(data).lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, data_str):
                return True
        
        return False
    
    def validate_input(self, data):
        """فحص شامل للمدخلات"""
        threats = []
        
        if self.detect_sql_injection(data):
            threats.append("SQL Injection")
        
        if self.detect_xss(data):
            threats.append("XSS Attack")
        
        if self.detect_path_traversal(data):
            threats.append("Path Traversal")
        
        return threats
    
    def security_check(self):
        """فحص الأمان الرئيسي لكل طلب"""
        ip = self.get_client_ip()
        
        # فحص IP المحظور
        if self.is_ip_blocked(ip):
            self.logger.warning(f"🚫 محاولة وصول من IP محظور: {ip}")
            abort(403)
        
        # فحص حد المعدل
        if not self.check_rate_limit(ip):
            self.logger.warning(f"⚡ تجاوز حد المعدل من IP: {ip}")
            abort(429)
        
        # فحص المدخلات في جميع البيانات
        all_data = []
        
        # فحص معاملات URL
        for key, value in request.args.items():
            all_data.extend([key, value])
        
        # فحص بيانات النموذج
        for key, value in request.form.items():
            all_data.extend([key, value])
        
        # فحص JSON data
        if request.is_json:
            try:
                json_data = request.get_json()
                if json_data:
                    all_data.append(str(json_data))
            except:
                pass
        
        # فحص الهيدرز المشبوهة
        suspicious_headers = ['User-Agent', 'Referer', 'X-Forwarded-For']
        for header in suspicious_headers:
            if request.headers.get(header):
                all_data.append(request.headers.get(header))
        
        # تحليل جميع البيانات
        for data in all_data:
            threats = self.validate_input(data)
            if threats:
                threat_str = ", ".join(threats)
                self.logger.critical(f"🚨 هجوم مكتشف من IP {ip}: {threat_str} - البيانات: {data[:100]}")
                self.block_ip(ip, f"Attack detected: {threat_str}")
                abort(403)
        
        # فحص جلسة المستخدم
        self.check_session_security()
    
    def check_session_security(self):
        """فحص أمان الجلسة"""
        if 'user_id' in session:
            # فحص انتهاء صلاحية الجلسة
            if 'last_activity' in session:
                last_activity = datetime.fromisoformat(session['last_activity'])
                if datetime.now() - last_activity > timedelta(seconds=self.SESSION_TIMEOUT):
                    session.clear()
                    self.logger.info("🕐 انتهت صلاحية الجلسة")
                    return
            
            # تحديث وقت النشاط الأخير
            session['last_activity'] = datetime.now().isoformat()
            
            # فحص IP الجلسة
            if 'session_ip' in session:
                if session['session_ip'] != self.get_client_ip():
                    session.clear()
                    self.logger.warning(f"🔄 تغيير IP في الجلسة: {session['session_ip']} -> {self.get_client_ip()}")
                    return
            else:
                session['session_ip'] = self.get_client_ip()
    
    def add_security_headers(self, response):
        """إضافة هيدرز الأمان"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' https://cdnjs.cloudflare.com;",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def handle_forbidden(self, error):
        """معالج الوصول المحظور"""
        ip = self.get_client_ip()
        self.logger.error(f"🚫 وصول محظور من IP: {ip}")
        
        return jsonify({
            'error': 'Access Forbidden',
            'message': 'تم رفض الوصول لأسباب أمنية',
            'code': 403,
            'timestamp': datetime.now().isoformat()
        }), 403
    
    def handle_rate_limit(self, error):
        """معالج تجاوز حد المعدل"""
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'تم تجاوز حد الطلبات المسموح',
            'code': 429,
            'retry_after': self.RATE_LIMIT_WINDOW,
            'timestamp': datetime.now().isoformat()
        }), 429

# دالات مساعدة للحماية
def require_auth(f):
    """ديكوريتر للتحقق من المصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token():
    """إنشاء رمز CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """التحقق من رمز CSRF"""
    return token and session.get('csrf_token') == token

# إنشاء مثيل النظام
security = SecuritySystem()

class AdvancedThreatDetection:
    """نظام كشف التهديدات المتقدم"""

    def __init__(self):
        self.threat_patterns = {
            'command_injection': [
                r';\s*(rm|del|format|shutdown|reboot)',
                r'\|\s*(nc|netcat|telnet|ssh)',
                r'`[^`]*`',
                r'\$\([^)]*\)',
                r'&&\s*(rm|del|format)',
                r'\|\|\s*(rm|del|format)'
            ],
            'ldap_injection': [
                r'\*\)\(\|',
                r'\*\)\(\&',
                r'\)\(\|',
                r'\)\(\&',
                r'\*\)\(\w+=\*'
            ],
            'xml_injection': [
                r'<!ENTITY',
                r'<!DOCTYPE',
                r'&\w+;',
                r'<!\[CDATA\[',
                r']]>'
            ],
            'nosql_injection': [
                r'\$where',
                r'\$ne',
                r'\$gt',
                r'\$lt',
                r'\$regex',
                r'\$or',
                r'\$and'
            ]
        }

    def detect_advanced_threats(self, data):
        """كشف التهديدات المتقدمة"""
        if not data:
            return []

        detected_threats = []
        data_str = str(data).lower()

        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    detected_threats.append(threat_type)
                    break

        return detected_threats

class HoneypotSystem:
    """نظام الفخاخ الأمنية"""

    def __init__(self):
        self.honeypot_urls = [
            '/admin.php',
            '/wp-admin/',
            '/phpmyadmin/',
            '/.env',
            '/config.php',
            '/database.sql',
            '/backup.zip',
            '/admin/login.php'
        ]
        self.trapped_ips = set()

    def is_honeypot_request(self, path):
        """فحص ما إذا كان الطلب لفخ أمني"""
        return any(honeypot in path.lower() for honeypot in self.honeypot_urls)

    def trap_attacker(self, ip):
        """حبس المهاجم في الفخ"""
        self.trapped_ips.add(ip)
        return "Access Denied - Suspicious Activity Detected"

class SecurityMonitor:
    """مراقب الأمان المتقدم"""

    def __init__(self):
        self.attack_signatures = []
        self.security_events = []
        self.threat_level = 'LOW'

    def log_security_event(self, event_type, ip, details):
        """تسجيل حدث أمني"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'ip': ip,
            'details': details,
            'threat_level': self.calculate_threat_level(event_type)
        }
        self.security_events.append(event)

        # إرسال تنبيه إذا كان التهديد عالي
        if event['threat_level'] == 'HIGH':
            self.send_security_alert(event)

    def calculate_threat_level(self, event_type):
        """حساب مستوى التهديد"""
        high_threat_events = [
            'SQL_INJECTION',
            'COMMAND_INJECTION',
            'BRUTE_FORCE',
            'MULTIPLE_ATTACKS'
        ]

        if event_type in high_threat_events:
            return 'HIGH'
        elif event_type in ['XSS', 'CSRF', 'PATH_TRAVERSAL']:
            return 'MEDIUM'
        else:
            return 'LOW'

    def send_security_alert(self, event):
        """إرسال تنبيه أمني"""
        alert_message = f"""
        🚨 تنبيه أمني عاجل 🚨

        نوع التهديد: {event['type']}
        مستوى الخطر: {event['threat_level']}
        عنوان IP: {event['ip']}
        الوقت: {event['timestamp']}
        التفاصيل: {event['details']}

        يرجى اتخاذ الإجراءات اللازمة فوراً!
        """

        # يمكن إضافة إرسال بريد إلكتروني أو رسالة نصية هنا
        print(alert_message)

# إنشاء مثيلات الأنظمة المتقدمة
advanced_detection = AdvancedThreatDetection()
honeypot = HoneypotSystem()
security_monitor = SecurityMonitor()

def init_security(app):
    """تهيئة نظام الحماية الشامل"""
    security.init_app(app)

    # إضافة الفحوصات المتقدمة
    @app.before_request
    def advanced_security_check():
        ip = security.get_client_ip()
        path = request.path

        # فحص الفخاخ الأمنية
        if honeypot.is_honeypot_request(path):
            security_monitor.log_security_event('HONEYPOT_TRIGGERED', ip, f'Path: {path}')
            security.block_ip(ip, "Honeypot triggered")
            return honeypot.trap_attacker(ip), 403

        # فحص التهديدات المتقدمة
        all_data = []
        for key, value in request.args.items():
            all_data.extend([key, value])
        for key, value in request.form.items():
            all_data.extend([key, value])

        for data in all_data:
            threats = advanced_detection.detect_advanced_threats(data)
            if threats:
                threat_str = ", ".join(threats)
                security_monitor.log_security_event('ADVANCED_THREAT', ip, f'Threats: {threat_str}')
                security.block_ip(ip, f"Advanced threat: {threat_str}")
                abort(403)

    return security
