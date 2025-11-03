# Vercel Serverless Function Handler for Unitest
# This file imports the Flask app from app.py and exports it for Vercel

import os
import sys

# Add parent directory to path to import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app

# Vercel Python runtime expects the Flask app to be exported
# The handler function will be automatically created by Vercel
handler = app

# Also export as application for compatibility
application = app
