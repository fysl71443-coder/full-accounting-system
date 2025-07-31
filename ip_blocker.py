#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚫 نظام حظر IP المتقدم
Advanced IP Blocking System
"""

from flask import Flask, request, abort, jsonify
import logging
from datetime import datetime, timedelta
import json
import os

class IPBlocker:
    """نظام حظر IP المتقدم"""
    
    def __init__(self, app=None):
        self.app = app
        
        # قائمة الـ IPs المحظورة (يمكن إضافة المزيد)
        self.BLOCKED_IPS = {
            '144.86.9.109',  # IP المطلوب حظره
            '192.168.1.100', # مثال لـ IP آخر
            '10.0.0.50',     # مثال لـ IP محلي مشبوه
        }
        
        # IPs مشبوهة (تحت المراقبة)
        self.SUSPICIOUS_IPS = {
            '185.220.101.182',  # Tor exit node
            '185.220.102.8',    # Tor exit node
            '199.87.154.255',   # Known scanner
        }
        
        # عدادات المحاولات لكل IP
        self.attempt_counts = {}
        
        # إعداد نظام السجلات
        self.setup_logging()
        
        if app:
            self.init_app(app)
    
    def setup_logging(self):
        """إعداد نظام السجلات"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('blocked_ips.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IPBlocker')
    
    def init_app(self, app):
        """تهيئة النظام مع Flask"""
        self.app = app
        
        # تطبيق فحص IP على جميع الطلبات
        app.before_request(self.block_ips)
        
        # إضافة مسارات إدارة IP
        app.add_url_rule('/admin/blocked-ips', 'blocked_ips_admin', self.blocked_ips_admin, methods=['GET'])
        app.add_url_rule('/admin/unblock-ip', 'unblock_ip', self.unblock_ip, methods=['POST'])
        app.add_url_rule('/admin/block-ip', 'block_ip_manual', self.block_ip_manual, methods=['POST'])
    
    def get_real_ip(self):
        """الحصول على IP الحقيقي للعميل"""
        # فحص الهيدرز المختلفة للحصول على IP الحقيقي
        if request.headers.get('X-Forwarded-For'):
            # أخذ أول IP من القائمة (الأصلي)
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
            return request.headers.get('CF-Connecting-IP')
        else:
            return request.remote_addr
    
    def is_ip_blocked(self, ip):
        """فحص ما إذا كان IP محظور"""
        return ip in self.BLOCKED_IPS
    
    def is_ip_suspicious(self, ip):
        """فحص ما إذا كان IP مشبوه"""
        return ip in self.SUSPICIOUS_IPS
    
    def add_blocked_ip(self, ip, reason="Manual block"):
        """إضافة IP إلى قائمة المحظورين"""
        self.BLOCKED_IPS.add(ip)
        self.logger.warning(f"تم حظر IP جديد: {ip} - السبب: {reason}")
        self.save_blocked_ips()
    
    def remove_blocked_ip(self, ip):
        """إزالة IP من قائمة المحظورين"""
        if ip in self.BLOCKED_IPS:
            self.BLOCKED_IPS.remove(ip)
            self.logger.info(f"تم رفع الحظر عن IP: {ip}")
            self.save_blocked_ips()
            return True
        return False
    
    def save_blocked_ips(self):
        """حفظ قائمة IPs المحظورة في ملف"""
        try:
            with open('blocked_ips.json', 'w') as f:
                json.dump(list(self.BLOCKED_IPS), f, indent=2)
        except Exception as e:
            self.logger.error(f"خطأ في حفظ قائمة IPs المحظورة: {e}")
    
    def load_blocked_ips(self):
        """تحميل قائمة IPs المحظورة من ملف"""
        try:
            if os.path.exists('blocked_ips.json'):
                with open('blocked_ips.json', 'r') as f:
                    blocked_list = json.load(f)
                    self.BLOCKED_IPS.update(blocked_list)
                    self.logger.info(f"تم تحميل {len(blocked_list)} IP محظور من الملف")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل قائمة IPs المحظورة: {e}")
    
    def track_attempt(self, ip):
        """تتبع محاولات الوصول لكل IP"""
        now = datetime.now()
        
        if ip not in self.attempt_counts:
            self.attempt_counts[ip] = []
        
        # إضافة المحاولة الحالية
        self.attempt_counts[ip].append(now)
        
        # إزالة المحاولات القديمة (أكثر من ساعة)
        hour_ago = now - timedelta(hours=1)
        self.attempt_counts[ip] = [
            attempt for attempt in self.attempt_counts[ip] 
            if attempt > hour_ago
        ]
        
        # إذا تجاوز عدد المحاولات 50 في الساعة، احظر IP
        if len(self.attempt_counts[ip]) > 50:
            self.add_blocked_ip(ip, "Too many requests (>50/hour)")
            return True
        
        return False
    
    def block_ips(self):
        """الوظيفة الرئيسية لحظر IPs"""
        client_ip = self.get_real_ip()
        
        # تتبع المحاولة
        if self.track_attempt(client_ip):
            self.logger.critical(f"IP محظور تلقائياً بسبب كثرة الطلبات: {client_ip}")
        
        # فحص IP المحظور
        if self.is_ip_blocked(client_ip):
            self.logger.warning(f"محاولة وصول من IP محظور: {client_ip}")
            self.logger.error(f"وصول محظور من IP: {client_ip}")
            
            # تسجيل معلومات إضافية
            self.logger.info(f"تفاصيل الطلب المحظور:")
            self.logger.info(f"   - المسار: {request.path}")
            self.logger.info(f"   - الطريقة: {request.method}")
            self.logger.info(f"   - User-Agent: {request.headers.get('User-Agent', 'غير محدد')}")
            self.logger.info(f"   - Referer: {request.headers.get('Referer', 'غير محدد')}")
            
            abort(403)
        
        # فحص IP مشبوه
        if self.is_ip_suspicious(client_ip):
            self.logger.warning(f"وصول من IP مشبوه: {client_ip}")
            # يمكن إضافة إجراءات إضافية هنا مثل CAPTCHA
    
    def blocked_ips_admin(self):
        """صفحة إدارة IPs المحظورة"""
        blocked_count = len(self.BLOCKED_IPS)
        suspicious_count = len(self.SUSPICIOUS_IPS)
        attempts_count = len(self.attempt_counts)

        # إنشاء قائمة IPs
        ip_list = ""
        for ip in self.BLOCKED_IPS:
            ip_list += f'<div class="ip-card"><strong>{ip}</strong> <button class="btn btn-sm btn-light float-end" onclick="unblockIP(\'{ip}\')">إلغاء الحظر</button></div>'

        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>إدارة IPs المحظورة</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .ip-card {{
                    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                    color: white;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body class="bg-light">
            <div class="container mt-4">
                <h2 class="text-danger">إدارة عناوين IP المحظورة</h2>

                <div class="row mt-4">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-danger text-white">
                                <h5>قائمة IPs المحظورة ({blocked_count})</h5>
                            </div>
                            <div class="card-body">
                                {ip_list}
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h5>حظر IP جديد</h5>
                            </div>
                            <div class="card-body">
                                <input type="text" id="newIP" class="form-control mb-2" placeholder="192.168.1.100">
                                <input type="text" id="reason" class="form-control mb-2" placeholder="سبب الحظر">
                                <button class="btn btn-danger w-100" onclick="blockNewIP()">حظر IP</button>
                            </div>
                        </div>

                        <div class="card mt-3">
                            <div class="card-header bg-info text-white">
                                <h5>إحصائيات</h5>
                            </div>
                            <div class="card-body">
                                <p>IPs محظورة: <strong>{blocked_count}</strong></p>
                                <p>IPs مشبوهة: <strong>{suspicious_count}</strong></p>
                                <p>محاولات مراقبة: <strong>{attempts_count}</strong></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                function unblockIP(ip) {{
                    if (confirm('هل تريد إلغاء حظر ' + ip + '؟')) {{
                        fetch('/admin/unblock-ip', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{ip: ip}})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                location.reload();
                            }} else {{
                                alert('فشل في إلغاء الحظر');
                            }}
                        }});
                    }}
                }}

                function blockNewIP() {{
                    const ip = document.getElementById('newIP').value;
                    const reason = document.getElementById('reason').value || 'Manual block';

                    if (ip) {{
                        fetch('/admin/block-ip', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{ip: ip, reason: reason}})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                location.reload();
                            }} else {{
                                alert('فشل في حظر IP');
                            }}
                        }});
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return html_content
    
    def unblock_ip(self):
        """إلغاء حظر IP"""
        data = request.get_json()
        ip = data.get('ip')
        
        if self.remove_blocked_ip(ip):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'IP not found'})
    
    def block_ip_manual(self):
        """حظر IP يدوياً"""
        data = request.get_json()
        ip = data.get('ip')
        reason = data.get('reason', 'Manual block')
        
        self.add_blocked_ip(ip, reason)
        return jsonify({'success': True})

# إنشاء مثيل نظام حظر IP
ip_blocker = IPBlocker()

def init_ip_blocker(app):
    """تهيئة نظام حظر IP"""
    ip_blocker.init_app(app)
    ip_blocker.load_blocked_ips()  # تحميل قائمة IPs المحظورة
    return ip_blocker
