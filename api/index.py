# Vercel Serverless Function Handler - Direct import from app.py
import os
import sys
import traceback

# Set VERCEL environment variable
os.environ['VERCEL'] = '1'

# Add parent directory to path to import app.py directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Try to import app directly
try:
    # Import app directly from app.py
    from app import app
    handler = app
    application = app
    print("✅ App imported successfully from app.py", file=sys.stderr)
except Exception as e:
    # Log detailed error
    error_msg = f"❌ Failed to import app.py: {str(e)}\n"
    error_msg += f"Error type: {type(e).__name__}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Current dir: {os.getcwd()}\n"
    error_msg += f"Parent dir: {parent_dir}\n"
    print(error_msg, file=sys.stderr)
    
    # Create minimal error app
    try:
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        error_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret')
        
        @error_app.route('/')
        def error_home():
            return jsonify({
                'error': 'App import failed',
                'message': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc().split('\n')[-15:],
                'environment': {
                    'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                    'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                    'has_database_url': bool(os.environ.get('DATABASE_URL')),
                    'vercel': bool(os.environ.get('VERCEL')),
                    'python_path': sys.path,
                    'current_dir': os.getcwd()
                }
            }), 500
        
        @error_app.route('/health')
        def error_health():
            return jsonify({
                'status': 'error',
                'error': 'App import failed',
                'message': str(e),
                'type': type(e).__name__,
                'environment': {
                    'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                    'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                    'has_database_url': bool(os.environ.get('DATABASE_URL')),
                    'vercel': bool(os.environ.get('VERCEL'))
                }
            }), 500
        
        handler = error_app
        application = error_app
    except Exception as flask_error:
        # Even Flask import failed - this is critical
        print(f"CRITICAL: Even Flask import failed: {flask_error}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise  # Re-raise to see the error
