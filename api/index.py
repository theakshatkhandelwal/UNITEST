# Vercel Serverless Function Handler for Unitest
# Optimized version that imports only what's needed

import os
import sys
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set VERCEL environment variable for app detection
os.environ['VERCEL'] = '1'

# Capture any errors during import
try:
    # Try importing app
    from app import app
    handler = app
    application = app
    print("✅ App imported successfully")
except Exception as e:
    # Log the error to stderr so it appears in Vercel logs
    error_msg = f"❌ App import failed: {str(e)}\n"
    error_msg += f"Error type: {type(e).__name__}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
    # Create a minimal error app
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    error_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
    
    @error_app.route('/')
    def error_home():
        return jsonify({
            'error': 'App import failed',
            'message': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc().split('\n')[-10:],  # Last 10 lines
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'vercel': bool(os.environ.get('VERCEL'))
            }
        }), 500
    
    @error_app.route('/health')
    def error_health():
        return jsonify({
            'status': 'error',
            'error': 'App import failed',
            'message': str(e),
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'vercel': bool(os.environ.get('VERCEL'))
            }
        }), 500
    
    handler = error_app
    application = error_app
