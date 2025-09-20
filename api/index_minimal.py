# Minimal Vercel serverless function
import os
import json
from flask import Flask, request, jsonify

# Create minimal Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

# Basic routes only
@app.route('/')
def home():
    return jsonify({
        'message': 'UniTest API is running',
        'status': 'success',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working'})

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Export for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)
