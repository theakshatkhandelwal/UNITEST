# Vercel Serverless Function Handler - Absolute minimal version
import os
import sys

# Set VERCEL environment variable
os.environ['VERCEL'] = '1'

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Flask first
from flask import Flask, jsonify

# Create a simple app that will definitely work
simple_app = Flask(__name__)
simple_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

@simple_app.route('/')
def home():
    # Try to import app and show status
    try:
        from app import app as main_app
        return jsonify({
            'status': 'success',
            'message': 'Main app imported successfully',
            'app_routes': len(main_app.url_map._rules) if hasattr(main_app, 'url_map') else 0
        }), 200
    except ImportError as e:
        return jsonify({
            'status': 'import_error',
            'error': 'ImportError',
            'message': str(e),
            'type': type(e).__name__,
            'help': 'Check if app.py exists and has no syntax errors'
        }), 500
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'error': 'Exception during import',
            'message': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc().split('\n')[-15:]
        }), 500

@simple_app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'handler': 'simple_app',
        'environment': {
            'has_secret_key': bool(os.environ.get('SECRET_KEY')),
            'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
            'has_database_url': bool(os.environ.get('DATABASE_URL')),
            'vercel': bool(os.environ.get('VERCEL'))
        }
    }), 200

@simple_app.route('/test-import')
def test_import():
    """Test importing app.py step by step"""
    results = []
    
    # Test 1: Basic imports
    try:
        import os
        import sys
        results.append({'test': 'basic_imports', 'status': 'ok'})
    except Exception as e:
        results.append({'test': 'basic_imports', 'status': 'error', 'message': str(e)})
        return jsonify({'results': results}), 500
    
    # Test 2: Flask imports
    try:
        from flask import Flask
        results.append({'test': 'flask_import', 'status': 'ok'})
    except Exception as e:
        results.append({'test': 'flask_import', 'status': 'error', 'message': str(e)})
        return jsonify({'results': results}), 500
    
    # Test 3: Try importing app.py
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", os.path.join(parent_dir, "app.py"))
        if spec is None:
            results.append({'test': 'app_import', 'status': 'error', 'message': 'Could not find app.py'})
            return jsonify({'results': results}), 500
        
        # Try to load the module
        module = importlib.util.module_from_spec(spec)
        results.append({'test': 'app_module_created', 'status': 'ok'})
        
        # Try to execute (this is where it might fail)
        spec.loader.exec_module(module)
        results.append({'test': 'app_module_executed', 'status': 'ok'})
        
        # Try to get the app object
        if hasattr(module, 'app'):
            results.append({'test': 'app_object_found', 'status': 'ok'})
        else:
            results.append({'test': 'app_object_found', 'status': 'error', 'message': 'app object not found in module'})
            
    except SyntaxError as e:
        results.append({'test': 'app_import', 'status': 'syntax_error', 'message': str(e), 'line': getattr(e, 'lineno', 'unknown')})
        return jsonify({'results': results}), 500
    except Exception as e:
        import traceback
        results.append({
            'test': 'app_import', 
            'status': 'error', 
            'message': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc().split('\n')[-10:]
        })
        return jsonify({'results': results}), 500
    
    return jsonify({'results': results, 'status': 'all_tests_passed'}), 200

# Try to import main app, but use simple_app as fallback
try:
    from app import app
    handler = app
    application = app
except:
    # Use simple app if main app fails
    handler = simple_app
    application = simple_app
