# Vercel Serverless Function Handler for Unitest
# Optimized version that imports only what's needed

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app with lazy loading to reduce initial bundle size
# Import only when needed
try:
    from app import app
    handler = app
    application = app
except ImportError as e:
    # Fallback: Create minimal app if import fails
    from flask import Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
    
    @app.route('/')
    def home():
        return {'error': 'App import failed', 'message': str(e)}, 500
    
    handler = app
    application = app
