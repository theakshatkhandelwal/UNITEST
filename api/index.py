# Vercel Serverless Function Handler - Maximum error visibility
import os
import sys
import traceback

# Force stderr to be unbuffered so errors show immediately
sys.stderr.reconfigure(line_buffering=True)

# Set VERCEL environment variable FIRST
os.environ['VERCEL'] = '1'

# Log that we're starting
print("=" * 80, file=sys.stderr)
print("VERCEL FUNCTION STARTING", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
print(f"Added parent dir to path: {parent_dir}", file=sys.stderr)
print(f"Python path: {sys.path[:3]}", file=sys.stderr)

# Try to import Flask first
flask_available = False
try:
    print("Attempting to import Flask...", file=sys.stderr)
    from flask import Flask, jsonify
    flask_available = True
    print("✅ Flask imported successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Flask import failed: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

# Create minimal Flask app as fallback
minimal_app = None
if flask_available:
    try:
        print("Creating minimal Flask app...", file=sys.stderr)
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
                    'python_path': sys.path[:3],
                    'current_dir': os.getcwd()
                }
            }), 200
        
        print("✅ Minimal Flask app created", file=sys.stderr)
    except Exception as e:
        print(f"❌ Failed to create minimal Flask app: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

# Now try to import the main app
app = None
import_error = None

try:
    print("=" * 80, file=sys.stderr)
    print("Attempting to import app.py...", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    from app import app as main_app
    app = main_app
    print("=" * 80, file=sys.stderr)
    print("✅ App imported successfully!", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
except ImportError as e:
    import_error = e
    print("=" * 80, file=sys.stderr)
    print("❌ IMPORT ERROR", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Error: {str(e)}", file=sys.stderr)
    print(f"Type: {type(e).__name__}", file=sys.stderr)
    print("Full traceback:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Current dir: {os.getcwd()}", file=sys.stderr)
    print(f"Parent dir: {parent_dir}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
except Exception as e:
    import_error = e
    print("=" * 80, file=sys.stderr)
    print("❌ EXCEPTION DURING IMPORT", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Error: {str(e)}", file=sys.stderr)
    print(f"Type: {type(e).__name__}", file=sys.stderr)
    print("Full traceback:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    print("=" * 80, file=sys.stderr)

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
                'help': 'Check Vercel Function Logs (not Deployment Logs) for full traceback'
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
        print("=" * 80, file=sys.stderr)
        print("FATAL: Cannot create any app", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        if import_error:
            print(f"Raising import error: {import_error}", file=sys.stderr)
            raise import_error
        else:
            raise RuntimeError("Failed to import app and cannot create minimal app")

print("=" * 80, file=sys.stderr)
print("FUNCTION HANDLER READY", file=sys.stderr)
print("=" * 80, file=sys.stderr)
