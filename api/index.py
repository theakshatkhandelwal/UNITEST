# Vercel Serverless Function Handler - Minimal working version
import os
import sys

# Set VERCEL environment variable
os.environ['VERCEL'] = '1'

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import and create app
try:
    from flask import Flask, jsonify
    from app import app
    
    handler = app
    application = app
    
except Exception as e:
    # If main app fails, create minimal error app
    try:
        from flask import Flask, jsonify
        
        error_app = Flask(__name__)
        error_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
        
        @error_app.route('/')
        @error_app.route('/<path:path>')
        def error_handler(path=''):
            import traceback
            return jsonify({
                'error': 'App import failed',
                'message': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc().split('\n')[-10:],
                'env_check': {
                    'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                    'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                    'has_database_url': bool(os.environ.get('DATABASE_URL')),
                    'vercel': bool(os.environ.get('VERCEL'))
                }
            }), 500
        
        handler = error_app
        application = error_app
        
    except Exception as flask_error:
        # Even Flask failed - create absolute minimal app
        from flask import Flask, jsonify
        minimal = Flask(__name__)
        minimal.config['SECRET_KEY'] = 'minimal'
        
        @minimal.route('/')
        @minimal.route('/<path:path>')
        def minimal_handler(path=''):
            return jsonify({
                'status': 'minimal',
                'error': 'Both main app and error handler failed',
                'original_error': str(e),
                'flask_error': str(flask_error)
            }), 500
        
        handler = minimal
        application = minimal
