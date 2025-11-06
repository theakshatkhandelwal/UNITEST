# Vercel Serverless Function Handler for Unitest
# Optimized version that imports only what's needed

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set VERCEL environment variable for app detection
os.environ['VERCEL'] = '1'

# Import app with error handling
try:
    from app import app
    handler = app
    application = app
except Exception as e:
    # Better error handling - create a minimal app that shows the error
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    error_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
    
    @error_app.route('/')
    def error_home():
        import traceback
        error_details = {
            'error': 'App import failed',
            'message': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        return jsonify(error_details), 500
    
    @error_app.route('/health')
    def error_health():
        return jsonify({
            'status': 'error',
            'error': 'App import failed',
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'vercel': bool(os.environ.get('VERCEL'))
            }
        }), 500
    
    handler = error_app
    application = error_app
