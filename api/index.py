# Vercel Serverless Function Handler for Unitest
# This file imports the Flask app from app.py and exports it for Vercel

import os
import sys

# Add parent directory to path to import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app

# Vercel expects 'handler' for serverless functions
# Export the Flask app as the handler
handler = app

# For direct testing
if __name__ == '__main__':
    app.run(debug=True)
