#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WSGI entry point for the accounting system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from accounting_system_complete import app, init_db
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # WSGI application
    application = app
    
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        
except Exception as e:
    print(f"Error starting application: {e}")
    raise
