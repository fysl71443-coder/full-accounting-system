#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 تكامل نظام الحماية مع النظام الرئيسي
Security System Integration with Main Application
"""

from security_system import init_security, require_auth, admin_required, generate_csrf_token, validate_csrf_token
from flask import request, session, jsonify, render_template_string
import json
from datetime import datetime

def integrate_security_with_app(app):
    """دمج نظام الحماية مع التطبيق الرئيسي"""
    
    # تهيئة نظام الحماية
    security_system = init_security(app)
    
    # إضافة مسارات إدارة الأمان
    @app.route('/security/dashboard')
    @admin_required
    def security_dashboard():
        """لوحة تحكم الأمان"""
        return render_template_string('''
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🛡️ لوحة تحكم الأمان</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .security-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .threat-high { border-left: 5px solid #dc3545; }
                .threat-medium { border-left: 5px solid #ffc107; }
                .threat-low { border-left: 5px solid #28a745; }
                .security-log {
                    max-height: 400px;
                    overflow-y: auto;
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                }
            </style>
        </head>
        <body class="bg-light">
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="#">
                        <i class="fas fa-shield-alt me-2"></i>نظام الحماية المتقدم
                    </a>
                    <div class="navbar-nav ms-auto">
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
                            <i class="fas fa-home me-1"></i>الرئيسية
                        </a>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <div class="row">
                    <div class="col-md-3">
                        <div class="security-card text-center">
                            <i class="fas fa-ban fa-3x mb-3"></i>
                            <h3 id="blocked-ips">{{ blocked_count }}</h3>
                            <p>عناوين IP محظورة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="security-card text-center">
                            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                            <h3 id="threats-detected">{{ threats_count }}</h3>
                            <p>تهديدات مكتشفة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="security-card text-center">
                            <i class="fas fa-eye fa-3x mb-3"></i>
                            <h3 id="requests-monitored">{{ requests_count }}</h3>
                            <p>طلبات مراقبة</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="security-card text-center">
                            <i class="fas fa-clock fa-3x mb-3"></i>
                            <h3 id="uptime">{{ uptime }}</h3>
                            <p>وقت التشغيل</p>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-danger text-white">
                                <h5><i class="fas fa-list me-2"></i>عناوين IP المحظورة</h5>
                            </div>
                            <div class="card-body">
                                <div id="blocked-ips-list">
                                    {% for ip in blocked_ips %}
                                    <div class="alert alert-danger">
                                        <i class="fas fa-ban me-2"></i>{{ ip }}
                                        <button class="btn btn-sm btn-outline-danger float-end" onclick="unblockIP('{{ ip }}')">
                                            إلغاء الحظر
                                        </button>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h5><i class="fas fa-chart-line me-2"></i>إحصائيات الأمان</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="securityChart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-info text-white">
                                <h5><i class="fas fa-history me-2"></i>سجل الأحداث الأمنية</h5>
                                <button class="btn btn-light btn-sm float-end" onclick="refreshLogs()">
                                    <i class="fas fa-sync-alt me-1"></i>تحديث
                                </button>
                            </div>
                            <div class="card-body">
                                <div class="security-log" id="security-logs">
                                    <!-- سيتم تحميل السجلات هنا -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                // تحديث البيانات كل 30 ثانية
                setInterval(updateSecurityData, 30000);
                
                function updateSecurityData() {
                    fetch('/security/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('blocked-ips').textContent = data.blocked_count;
                        document.getElementById('threats-detected').textContent = data.threats_count;
                        document.getElementById('requests-monitored').textContent = data.requests_count;
                    });
                }
                
                function unblockIP(ip) {
                    if (confirm('هل أنت متأكد من إلغاء حظر هذا العنوان؟')) {
                        fetch('/security/api/unblock', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ip: ip})
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert('فشل في إلغاء الحظر');
                            }
                        });
                    }
                }
                
                function refreshLogs() {
                    fetch('/security/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsContainer = document.getElementById('security-logs');
                        logsContainer.innerHTML = '';
                        
                        data.logs.forEach(log => {
                            const logDiv = document.createElement('div');
                            logDiv.className = `alert threat-${log.level.toLowerCase()}`;
                            logDiv.innerHTML = `
                                <div class="d-flex justify-content-between">
                                    <div>
                                        <strong>${log.timestamp}</strong> - ${log.message}
                                    </div>
                                    <span class="badge bg-${log.level === 'HIGH' ? 'danger' : log.level === 'MEDIUM' ? 'warning' : 'success'}">
                                        ${log.level}
                                    </span>
                                </div>
                            `;
                            logsContainer.appendChild(logDiv);
                        });
                    });
                }
                
                // تحميل السجلات عند فتح الصفحة
                document.addEventListener('DOMContentLoaded', refreshLogs);
                
                // رسم بياني للإحصائيات
                const ctx = document.getElementById('securityChart').getContext('2d');
                const securityChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['الساعة الماضية', 'منذ ساعتين', 'منذ 3 ساعات', 'منذ 4 ساعات', 'منذ 5 ساعات'],
                        datasets: [{
                            label: 'التهديدات المكتشفة',
                            data: [12, 19, 3, 5, 2],
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'إحصائيات التهديدات'
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        ''', 
        blocked_count=len(security_system.blocked_ips),
        threats_count=0,  # يمكن إضافة عداد التهديدات
        requests_count=sum(len(requests) for requests in security_system.rate_limits.values()),
        uptime="24:00:00",  # يمكن حساب الوقت الفعلي
        blocked_ips=list(security_system.blocked_ips)
        )
    
    @app.route('/security/api/stats')
    @admin_required
    def security_stats():
        """إحصائيات الأمان API"""
        return jsonify({
            'blocked_count': len(security_system.blocked_ips),
            'threats_count': 0,
            'requests_count': sum(len(requests) for requests in security_system.rate_limits.values()),
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/security/api/unblock', methods=['POST'])
    @admin_required
    def unblock_ip():
        """إلغاء حظر IP"""
        data = request.get_json()
        ip = data.get('ip')
        
        if ip and ip in security_system.blocked_ips:
            security_system.blocked_ips.remove(ip)
            security_system.logger.info(f"✅ تم إلغاء حظر IP بواسطة المدير: {ip}")
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'IP not found'})
    
    @app.route('/security/api/logs')
    @admin_required
    def security_logs():
        """سجلات الأمان API"""
        # قراءة آخر 50 سطر من ملف السجل
        try:
            with open('security.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()[-50:]
            
            logs = []
            for line in lines:
                if line.strip():
                    parts = line.strip().split(' - ', 2)
                    if len(parts) >= 3:
                        logs.append({
                            'timestamp': parts[0],
                            'level': parts[1],
                            'message': parts[2]
                        })
            
            return jsonify({'logs': logs})
        except FileNotFoundError:
            return jsonify({'logs': []})
    
    # إضافة CSRF token لجميع النماذج
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf_token)
    
    return security_system
