# Vercel Serverless Function Handler - Ultra-robust error handling
import os
import sys
import traceback

# Set VERCEL environment variable FIRST
os.environ['VERCEL'] = '1'

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Create a minimal Flask app FIRST as fallback
minimal_app = None
try:
    from flask import Flask, jsonify
    minimal_app = Flask(__name__)
    minimal_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    @minimal_app.route('/')
    def minimal_home():
        return jsonify({
            'status': 'minimal_app',
            'message': 'Main app failed to load, using minimal app',
            'check': '/health for details'
        }), 200
    
    @minimal_app.route('/health')
    def minimal_health():
        return jsonify({
            'status': 'minimal_app',
            'error': 'Main app failed to import',
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'vercel': bool(os.environ.get('VERCEL')),
                'python_path': sys.path[:3],  # First 3 paths only
                'current_dir': os.getcwd()
            }
        }), 200
except Exception as flask_error:
    print(f"CRITICAL: Cannot even create minimal Flask app: {flask_error}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    minimal_app = None

# Now try to import the main app
app = None
import_error = None

try:
    print("Attempting to import app.py...", file=sys.stderr)
    from app import app as main_app
    app = main_app
    print("✅ App imported successfully!", file=sys.stderr)
except ImportError as e:
    import_error = e
    error_msg = f"❌ ImportError importing app.py: {str(e)}\n"
    error_msg += f"Error type: {type(e).__name__}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Current dir: {os.getcwd()}\n"
    error_msg += f"Parent dir: {parent_dir}\n"
    print(error_msg, file=sys.stderr)
except Exception as e:
    import_error = e
    error_msg = f"❌ Exception importing app.py: {str(e)}\n"
    error_msg += f"Error type: {type(e).__name__}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    print(error_msg, file=sys.stderr)

# Use main app if available, otherwise use minimal app
if app:
    handler = app
    application = app
    print("Using main app", file=sys.stderr)
else:
    # Create error app that shows the import error
    if minimal_app:
        @minimal_app.route('/')
        def error_home():
            return jsonify({
                'error': 'App import failed',
                'message': str(import_error) if import_error else 'Unknown error',
                'type': type(import_error).__name__ if import_error else 'Unknown',
                'traceback': traceback.format_exc().split('\n')[-20:] if import_error else [],
                'environment': {
                    'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                    'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                    'has_database_url': bool(os.environ.get('DATABASE_URL')),
                    'vercel': bool(os.environ.get('VERCEL')),
                    'python_path': sys.path[:5],
                    'current_dir': os.getcwd()
                },
                'help': 'Check Vercel Function Logs for full traceback'
            }), 500
        
        @minimal_app.route('/health')
        def error_health():
            return jsonify({
                'status': 'error',
                'error': 'App import failed',
                'message': str(import_error) if import_error else 'Unknown error',
                'type': type(import_error).__name__ if import_error else 'Unknown',
                'environment': {
                    'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                    'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                    'has_database_url': bool(os.environ.get('DATABASE_URL')),
                    'vercel': bool(os.environ.get('VERCEL'))
                }
            }), 500
        
        handler = minimal_app
        application = minimal_app
        print("Using minimal error app", file=sys.stderr)
    else:
        # Last resort - raise the error so Vercel shows it
        print("FATAL: Cannot create any app, raising error", file=sys.stderr)
        if import_error:
            raise import_error
        else:
            raise RuntimeError("Failed to import app and cannot create minimal app")
