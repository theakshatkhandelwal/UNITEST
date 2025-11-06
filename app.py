import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import json
import re
import requests
import time
import csv
import io
# Conditional imports for optional dependencies - REMOVED FOR VERCEL
# All optional dependencies removed to prevent import crashes
HAS_PANDAS = False
pd = None
HAS_PYPDF2 = False
HAS_PDF2IMAGE = False
HAS_TESSERACT = False
HAS_EASYOCR = False
_easyocr_reader = None
HAS_NLTK = False
HAS_REPORTLAB = False

def get_easyocr_reader():
    return None

from collections import Counter
from datetime import datetime

# Download NLTK data only when needed
def ensure_nltk_data():
    if not HAS_NLTK:
        return
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception:
            # NLTK download failed, skip
            pass

# Configure Flask for Vercel (no instance folder)
# Explicitly set paths to ensure templates/static are found on Vercel
app = Flask(__name__, 
            instance_relative_config=False,
            static_folder='static',
            template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration - use PostgreSQL on Vercel/NeonDB, SQLite locally
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Fix for Vercel/NeonDB PostgreSQL URL format
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif database_url and database_url.startswith('postgresql://'):
    # Already in correct format for NeonDB
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unittest.db'

# Enhanced database configuration for Vercel/NeonDB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Only apply PostgreSQL-specific SSL settings if using PostgreSQL
if database_url and ('postgresql://' in database_url or 'postgres://' in database_url):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'max_overflow': 5,
        'pool_size': 5,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10,
            'application_name': 'unittest-app'
        }
    }
else:
    # SQLite configuration (no SSL settings) - increased pool for better concurrency
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'max_overflow': 5,
        'pool_size': 5
    }

# Initialize database with error handling to prevent crashes
# Use lazy initialization - don't connect until actually needed
try:
    # Create SQLAlchemy instance without connecting
    db = SQLAlchemy()
    db.init_app(app)
    # Don't connect to database during import - only when actually used
except Exception as e:
    print(f"Error creating SQLAlchemy instance: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    # Create minimal db to prevent crash
    db = SQLAlchemy()
    try:
        db.init_app(app)
    except Exception as e2:
        print(f"Error initializing db with app: {e2}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

# Initialize login manager with error handling
try:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
except Exception as e:
    print(f"Error initializing login manager: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    # Create minimal login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

# Configure Google AI (with error handling) - DEFER to avoid import-time issues
_google_ai_configured = False
def configure_google_ai():
    global _google_ai_configured
    if _google_ai_configured:
        return
    try:
        google_api_key = os.environ.get('GOOGLE_AI_API_KEY', 'AIzaSyBKYJLje8mR0VP5XxmrpG3PfXAleNXU_-c')
        genai.configure(api_key=google_api_key)
        _google_ai_configured = True
        print("Google AI configured successfully", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Google AI configuration failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Continue without AI features if key is invalid

# Configure immediately but with error handling
configure_google_ai()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    bloom_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Shared Quiz Models
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner/intermediate/advanced
    duration_minutes = db.Column(db.Integer)  # optional time limit for test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text)  # JSON array for MCQ options like ["A. ...","B. ...","C. ...","D. ..."]
    answer = db.Column(db.String(10))  # For MCQ store letter like 'A'; for subjective can store sample answer
    qtype = db.Column(db.String(20), default='mcq')  # 'mcq', 'subjective', or 'coding'
    marks = db.Column(db.Integer, default=1)
    # For coding questions
    test_cases_json = db.Column(db.Text)  # JSON array of test cases: [{"input": "...", "expected_output": "...", "is_hidden": false}]
    language_constraints = db.Column(db.Text)  # JSON array of allowed languages: ["python", "java", "cpp", "c"]
    time_limit_seconds = db.Column(db.Integer)  # Time limit per test case
    memory_limit_mb = db.Column(db.Integer)  # Memory limit in MB
    sample_input = db.Column(db.Text)  # Sample input for display
    sample_output = db.Column(db.Text)  # Sample output for display
    starter_code = db.Column(db.Text)  # Optional starter code template

class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    # unlock review after 15 minutes
    review_unlocked_at = db.Column(db.DateTime)
    # flag if student exited fullscreen during test
    fullscreen_exit_flag = db.Column(db.Boolean, default=False)
    # counts to determine clean vs hold
    answered_count = db.Column(db.Integer, default=0)
    question_count = db.Column(db.Integer, default=0)
    is_full_completion = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

class QuizAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('quiz_submission.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    ai_score = db.Column(db.Float)  # 0..1 for subjective
    scored_marks = db.Column(db.Float, default=0.0)
    # For coding questions
    code_language = db.Column(db.String(20))  # Language used: python, java, cpp, c
    test_results_json = db.Column(db.Text)  # JSON array of test case results
    passed_test_cases = db.Column(db.Integer, default=0)
    total_test_cases = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def evaluate_subjective_answer(question, student_answer, model_answer):
    """Use AI to evaluate subjective answers"""
    if not genai or not student_answer.strip():
        return 0.0

    try:
        configure_google_ai()  # Ensure Google AI is configured
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Evaluate this student's answer for the given question:

        Question: {question}
        Student Answer: {student_answer}
        Model Answer: {model_answer}

        Rate the student's answer on a scale of 0.0 to 1.0 based on:
        - Accuracy and correctness
        - Completeness
        - Understanding demonstrated
        - Relevance to the question

        Return only a number between 0.0 and 1.0 (e.g., 0.8 for 80% correct)
        """

        response = model.generate_content(prompt)
        score_text = response.text.strip()

        # Extract number from response
        score_match = re.search(r'(\d*\.?\d+)', score_text)
        if score_match:
            score = float(score_match.group(1))
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1

        return 0.5  # Default if can't parse
    except Exception as e:
        print(f"Error in evaluate_subjective_answer: {str(e)}")
        return 0.5  # Default on error

def execute_code(code, language, test_input, time_limit=2, memory_limit=256):
    """
    Execute code using Piston API (free, no API key needed)
    Alternative: Judge0 API
    """
    # Try Piston API first (simpler, free)
    piston_url = "https://emkc.org/api/v2/piston/execute"
    
    # Piston language mapping
    piston_languages = {
        'python': 'python3',
        'python3': 'python3',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c'
    }
    
    piston_lang = piston_languages.get(language.lower(), 'python3')
    
    try:
        payload = {
            "language": piston_lang,
            "version": "*",
            "files": [
                {
                    "content": code
                }
            ],
            "stdin": test_input,
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": time_limit * 1000,
            "compile_memory_limit": memory_limit * 1024 * 1024,
            "run_memory_limit": memory_limit * 1024 * 1024
        }
        
        response = requests.post(piston_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('run'):
                run_result = result['run']
                if run_result.get('code') == 0:
                    return {
                        'status': 'success',
                        'output': run_result.get('output', '').strip(),
                        'stderr': run_result.get('stderr', '').strip(),
                        'time': '',
                        'memory': ''
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Runtime Error',
                        'output': run_result.get('output', '').strip(),
                        'stderr': run_result.get('stderr', '').strip() or run_result.get('stdout', '')
                    }
            elif result.get('compile'):
                compile_result = result['compile']
                if compile_result.get('code') != 0:
                    return {
                        'status': 'error',
                        'message': 'Compilation Error',
                        'output': '',
                        'stderr': compile_result.get('stderr', '').strip() or compile_result.get('stdout', '')
                    }
            
            # If we get here but no result, try fallback
            return execute_code_judge0(code, language, test_input, time_limit, memory_limit)
        else:
            # Fallback: Try Judge0 if Piston fails
            return execute_code_judge0(code, language, test_input, time_limit, memory_limit)
        
    except requests.exceptions.RequestException:
        # Fallback to Judge0
        return execute_code_judge0(code, language, test_input, time_limit, memory_limit)
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Execution error: {str(e)}',
            'output': '',
            'stderr': ''
        }

def execute_code_judge0(code, language, test_input, time_limit=2, memory_limit=256):
    """Fallback: Execute code using Judge0 API"""
    language_map = {
        'python': 71,
        'python3': 71,
        'java': 62,
        'cpp': 54,
        'c': 50
    }
    
    language_id = language_map.get(language.lower(), 71)
    
    # Use Judge0 CE (free community edition)
    judge0_url = os.environ.get('JUDGE0_API_URL', 'https://ce.judge0.com')
    
    try:
        # Submit
        submit_url = f"{judge0_url}/submissions"
        payload = {
            "source_code": code,
            "language_id": language_id,
            "stdin": test_input,
            "cpu_time_limit": time_limit,
            "memory_limit": memory_limit * 1024
        }
        
        response = requests.post(submit_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        
        if response.status_code not in [201, 200]:
            return {
                'status': 'error',
                'message': f'API Error: {response.status_code}',
                'output': '',
                'stderr': response.text
            }
        
        submission_data = response.json()
        token = submission_data.get('token')
        
        if not token:
            return {
                'status': 'error',
                'message': 'No token received',
                'output': '',
                'stderr': ''
            }
        
        # Poll for results
        for attempt in range(10):
            time.sleep(0.5)
            
            result_url = f"{judge0_url}/submissions/{token}"
            result_response = requests.get(result_url, timeout=10)
            
            if result_response.status_code == 200:
                result = result_response.json()
                status_id = result.get('status', {}).get('id', 0)
                
                if status_id == 3:  # Accepted
                    return {
                        'status': 'success',
                        'output': result.get('stdout', '').strip(),
                        'stderr': result.get('stderr', '').strip(),
                        'time': result.get('time', ''),
                        'memory': result.get('memory', '')
                    }
                elif status_id in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
                    return {
                        'status': 'error',
                        'message': result.get('status', {}).get('description', 'Execution Error'),
                        'output': result.get('stdout', '').strip(),
                        'stderr': result.get('stderr', '').strip() or result.get('compile_output', '').strip()
                    }
        
        return {
            'status': 'error',
            'message': 'Timeout waiting for execution result',
            'output': '',
            'stderr': ''
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Execution error: {str(e)}',
            'output': '',
            'stderr': ''
        }

def run_test_cases(code, language, test_cases, time_limit=2, memory_limit=256):
    """Run multiple test cases and return results"""
    results = []
    passed = 0
    
    for test_case in test_cases:
        test_input = test_case.get('input', '')
        expected_output = test_case.get('expected_output', '').strip()
        is_hidden = test_case.get('is_hidden', False)
        
        exec_result = execute_code(code, language, test_input, time_limit, memory_limit)
        
        if exec_result['status'] == 'success':
            actual_output = exec_result['output'].strip()
            is_correct = actual_output == expected_output
            if is_correct:
                passed += 1
        else:
            actual_output = exec_result.get('stderr', exec_result.get('message', 'Error'))
            is_correct = False
        
        results.append({
            'input': test_input if not is_hidden else 'Hidden',
            'expected_output': expected_output if not is_hidden else 'Hidden',
            'actual_output': actual_output,
            'is_correct': is_correct,
            'is_hidden': is_hidden,
            'error': exec_result.get('message', '') if exec_result['status'] == 'error' else None
        })
    
    return {
        'results': results,
        'passed': passed,
        'total': len(test_cases),
        'percentage': (passed / len(test_cases) * 100) if test_cases else 0
    }

def get_difficulty_from_bloom_level(bloom_level):
    """Map Bloom's taxonomy level to difficulty level"""
    if bloom_level <= 2:
        return "beginner"
    elif bloom_level <= 4:
        return "intermediate"
    else:
        return "difficult"

def generate_quiz(topic, difficulty_level, question_type="mcq", num_questions=5):
    if not genai:
        return None

    try:
        configure_google_ai()  # Ensure Google AI is configured
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Map difficulty levels to Bloom's taxonomy levels and descriptions
        difficulty_mapping = {
            "beginner": {
                "bloom_level": 1,
                "description": "Remembering and Understanding level - basic facts, definitions, and simple concepts"
            },
            "intermediate": {
                "bloom_level": 3,
                "description": "Applying and Analyzing level - practical application and analysis of concepts"
            },
            "difficult": {
                "bloom_level": 5,
                "description": "Evaluating and Creating level - critical thinking, evaluation, and synthesis"
            }
        }
        
        difficulty_info = difficulty_mapping.get(difficulty_level, difficulty_mapping["beginner"])
        bloom_level = difficulty_info["bloom_level"]
        level_description = difficulty_info["description"]
        
        # Add randomization seed to prompt for variety
        import random
        random_seed = random.randint(1000, 9999)

        if question_type == "mcq":
            prompt = f"""
                Generate a multiple-choice quiz on {topic} at {difficulty_level.upper()} level ({level_description}).
                - Include exactly {num_questions} questions.
                - Each question should have 4 answer choices.
                - Make questions diverse and varied - avoid repetitive patterns.
                - Use randomization seed {random_seed} to ensure variety.
                - Include a "level" key specifying the Bloom's Taxonomy level (Remembering, Understanding, Applying, etc.).
                - Return output in valid JSON format: 
                [
                    {{"question": "What is AI?", "options": ["A. option1", "B. option2", "C. option3", "D. option4"], "answer": "A", "type": "mcq"}},
                    ...
                ]
            """
        elif question_type == "coding":
            prompt = f"""
CRITICAL: You MUST generate exactly {num_questions} coding programming problems on the topic: {topic}

Difficulty Level: {difficulty_level.upper()} ({level_description})

IMPORTANT REQUIREMENTS:
1. Generate EXACTLY {num_questions} coding problems (not MCQ, not subjective, but actual programming problems)
2. Each problem MUST have the following structure:
   - "question": A clear problem statement describing what the student needs to code
   - "type": MUST be exactly "coding" (not "mcq" or anything else)
   - "sample_input": Sample input that demonstrates the problem
   - "sample_output": Expected output for the sample input
   - "test_cases": An array with at least 3-5 test cases, each with:
     * "input": The test input as a string
     * "expected_output": The expected output as a string
     * "is_hidden": boolean (false for visible test cases, true for hidden ones)
   - "time_limit_seconds": 2 (default)
   - "memory_limit_mb": 256 (default)
   - "starter_code": An object with starter code templates for each language:
     * "python": Python starter code
     * "java": Java starter code  
     * "cpp": C++ starter code
     * "c": C starter code

3. Problems should be diverse and test different programming concepts related to {topic}
4. Use randomization seed {random_seed} to ensure variety

EXAMPLE FORMAT (follow this EXACT structure):
[
    {{
        "question": "Write a function to find the maximum element in an array. The function should take an array of integers and return the maximum value.",
        "type": "coding",
        "sample_input": "5\n1 3 5 2 4",
        "sample_output": "5",
        "test_cases": [
            {{"input": "3\n1 2 3", "expected_output": "3", "is_hidden": false}},
            {{"input": "4\n10 5 8 12", "expected_output": "12", "is_hidden": false}},
            {{"input": "5\n-1 -5 -3 -2 -4", "expected_output": "-1", "is_hidden": true}},
            {{"input": "1\n42", "expected_output": "42", "is_hidden": true}}
        ],
        "time_limit_seconds": 2,
        "memory_limit_mb": 256,
        "starter_code": {{
            "python": "def find_max(arr):\\n    # Your code here\\n    pass",
            "java": "public class Solution {{\\n    public static int findMax(int[] arr) {{\\n        // Your code here\\n        return 0;\\n    }}\\n}}",
            "cpp": "#include <iostream>\\n#include <vector>\\nusing namespace std;\\n\\nint findMax(vector<int>& arr) {{\\n    // Your code here\\n    return 0;\\n}}",
            "c": "#include <stdio.h>\\n\\nint findMax(int arr[], int n) {{\\n    // Your code here\\n    return 0;\\n}}"
        }}
    }}
]

Return ONLY valid JSON array. Do NOT include any markdown code blocks, explanations, or text outside the JSON array.
            """
        else:  # subjective
            prompt = f"""
                Generate subjective questions on {topic} at {difficulty_level.upper()} level ({level_description}).
                - Include exactly {num_questions} questions.
                - Questions should be open-ended and require detailed answers.
                - Make questions diverse and varied - avoid repetitive patterns.
                - Use randomization seed {random_seed} to ensure variety.
                - Include a "level" key specifying the Bloom's Taxonomy level.
                - Vary the marks between 5, 10, 15, and 20 marks for different questions.
                - Return output in valid JSON format: 
                [
                    {{"question": "Explain the concept of AI and its applications", "answer": "Sample answer explaining AI...", "type": "subjective", "marks": 10}},
                    ...
                ]
            """

        response = model.generate_content(prompt)

        if not response.text:
            raise ValueError("Empty response from AI")

        json_match = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(1))
        else:
            try:
                questions = json.loads(response.text)
            except:
                raise ValueError("Invalid response format from AI")

        # Validate that questions match the requested type
        if questions:
            # Ensure all questions have the correct type
            for q in questions:
                if 'type' not in q:
                    q['type'] = question_type
                elif q.get('type') != question_type:
                    print(f"WARNING: Question type mismatch. Expected {question_type}, got {q.get('type')}")
                    q['type'] = question_type  # Force correct type
            
            print(f"DEBUG: Validated {len(questions)} questions, all have type: {question_type}")

        return questions

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return None

def process_document(file_path):
    """Process uploaded document to extract content - SIMPLIFIED FOR VERCEL"""
    try:
        
        content = ""
        if file_path.lower().endswith('.pdf'):
            # Try text extraction first (faster for text-based PDFs)
            text_content = ""
            if HAS_PYPDF2:
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"PyPDF2 extraction failed: {e}")
            
            # If text extraction failed or returned empty, try OCR for image-based PDFs
            if not text_content or not text_content.strip():
                # Try EasyOCR first (works better for web deployment, no system binaries needed)
                if HAS_EASYOCR:
                    try:
                        print("Attempting OCR extraction using EasyOCR...")
                        reader = get_easyocr_reader()
                        images = []
                        
                        # Try to convert PDF pages to images
                        if HAS_PDF2IMAGE:
                            try:
                                images = convert_from_path(file_path, dpi=200, first_page=1, last_page=3)
                                print(f"Converted {len(images)} PDF pages to images using pdf2image")
                            except Exception as pdf_err:
                                print(f"pdf2image failed (may need Poppler): {pdf_err}")
                                # Try alternative: use pdf2image with BytesIO
                                try:
                                    from pdf2image import convert_from_bytes
                                    with open(file_path, 'rb') as f:
                                        pdf_bytes = f.read()
                                    images = convert_from_bytes(pdf_bytes, dpi=200, first_page=1, last_page=3)
                                    print(f"Converted {len(images)} PDF pages using convert_from_bytes")
                                except Exception as bytes_err:
                                    print(f"convert_from_bytes also failed: {bytes_err}")
                        
                        # If still no images, try PyMuPDF (fitz) as alternative
                        if not images:
                            try:
                                import fitz  # PyMuPDF
                                pdf_document = fitz.open(file_path)
                                for page_num in range(min(3, len(pdf_document))):
                                    page = pdf_document[page_num]
                                    # Convert page to image
                                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                                    pix = page.get_pixmap(matrix=mat)
                                    img_data = pix.tobytes("png")
                                    from PIL import Image
                                    import io
                                    image = Image.open(io.BytesIO(img_data))
                                    images.append(image)
                                pdf_document.close()
                                print(f"Converted {len(images)} PDF pages using PyMuPDF")
                            except ImportError:
                                print("PyMuPDF not available. Install with: pip install PyMuPDF")
                            except Exception as fitz_err:
                                print(f"PyMuPDF conversion failed: {fitz_err}")
                        
                        # Process images with EasyOCR
                        if images:
                            import numpy as np
                            for i, image in enumerate(images):
                                print(f"Processing page {i+1}/{len(images)} with EasyOCR...")
                                try:
                                    # Convert PIL Image to numpy array for EasyOCR
                                    import numpy as np
                                    if isinstance(image, Image.Image):
                                        image_array = np.array(image)
                                    else:
                                        image_array = image
                                    
                                    # EasyOCR returns list of (bbox, text, confidence)
                                    results = reader.readtext(image_array)
                                    page_text = " ".join([result[1] for result in results])
                                    text_content += page_text + "\n"
                                    print(f"Extracted {len(page_text)} characters from page {i+1}")
                                except Exception as ocr_err:
                                    print(f"EasyOCR failed on page {i+1}: {ocr_err}")
                                    import traceback
                                    traceback.print_exc()
                                    continue
                            
                            print(f"EasyOCR extraction completed. Extracted {len(text_content)} characters.")
                        else:
                            print("Could not convert PDF to images. EasyOCR requires images.")
                    except Exception as e:
                        print(f"EasyOCR extraction failed: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fall through to try Tesseract if available
                
                # Fallback to Tesseract if EasyOCR failed or not available
                if (not text_content or not text_content.strip()) and HAS_PDF2IMAGE and HAS_TESSERACT:
                    try:
                        print("Attempting OCR extraction using Tesseract...")
                        # Convert PDF pages to images
                        images = convert_from_path(file_path, dpi=200, first_page=1, last_page=3)
                        
                        # Extract text from each image using OCR
                        for i, image in enumerate(images):
                            print(f"Processing page {i+1}/{len(images)} with Tesseract...")
                            try:
                                page_text = pytesseract.image_to_string(image, lang='eng')
                                text_content += page_text + "\n"
                            except Exception as ocr_err:
                                print(f"Tesseract failed on page {i+1}: {ocr_err}")
                                continue
                        
                        print(f"Tesseract extraction completed. Extracted {len(text_content)} characters.")
                    except FileNotFoundError as e:
                        error_msg = "Poppler not found. Please install Poppler or use EasyOCR. See PDF_INSTALLATION.md for details."
                        print(f"OCR extraction failed: {error_msg}")
                        if not HAS_PYPDF2 and not HAS_EASYOCR:
                            return error_msg
                    except Exception as e:
                        error_msg = f"Tesseract OCR failed: {str(e)}. Try installing EasyOCR (pip install easyocr) for better compatibility."
                        print(error_msg)
                        if not HAS_PYPDF2 and not HAS_EASYOCR:
                            return error_msg
                
                # If still no content extracted
                if not text_content or not text_content.strip():
                    missing = []
                    if not HAS_PDF2IMAGE:
                        missing.append("pdf2image")
                    if not HAS_EASYOCR and not HAS_TESSERACT:
                        missing.append("easyocr or pytesseract")
                    if not HAS_PYPDF2:
                        missing.append("PyPDF2")
                    
                    if missing:
                        return f"PDF processing not available. Please install: {', '.join(missing)}. For web deployment, use: pip install easyocr pdf2image"
            
            content = text_content
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

        if not content or not content.strip():
            return None

        if HAS_NLTK:
            tokens = word_tokenize(content.lower())
            stop_words = set(stopwords.words('english'))
            meaningful_words = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 2]

            if not meaningful_words:
                return None

            word_freq = Counter(meaningful_words)
            # Get top 3 most common words and combine them
            top_words = word_freq.most_common(3)
            main_topic = " ".join([word[0].capitalize() for word in top_words])
            return main_topic
        else:
            # Fallback: return first meaningful words as topic
            words = content.split()[:5]
            return " ".join(words).strip()[:100]

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Routes
@app.route('/')
def home():
    # Initialize database if needed (for Vercel)
    if os.environ.get('VERCEL'):
        try:
            init_database()
        except Exception as e:
            print(f"Database init warning: {e}")
    
    return render_template('home.html')

@app.route('/debug')
def debug_info():
    """Debug endpoint for Vercel troubleshooting"""
    try:
        # Check if we're on Vercel
        is_vercel = bool(os.environ.get('VERCEL'))
        return {
            'status': 'ok',
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'is_vercel': bool(os.environ.get('VERCEL')),
                'python_version': sys.version,
                'database_url_preview': os.environ.get('DATABASE_URL', 'Not set')[:50] + '...' if os.environ.get('DATABASE_URL') else 'Not set'
            },
            'database_config': {
                'sqlalchemy_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50] + '...' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Not set',
                'track_modifications': app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
            }
        }
    except Exception as e:
        return {'error': str(e), 'status': 'error'}, 500

@app.route('/health')
def health_check():
    """Health check endpoint - doesn't require database"""
    try:
        return jsonify({
            'status': 'ok',
            'app_loaded': True,
            'environment': {
                'has_secret_key': bool(os.environ.get('SECRET_KEY')),
                'has_google_api': bool(os.environ.get('GOOGLE_AI_API_KEY')),
                'has_database_url': bool(os.environ.get('DATABASE_URL')),
                'vercel': bool(os.environ.get('VERCEL')),
                'database_uri_set': bool(app.config.get('SQLALCHEMY_DATABASE_URI'))
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/init-db')
def init_database():
    """Initialize database tables for Vercel deployment"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Fix password_hash column size if needed
            try:
                # Check if we're using PostgreSQL (NeonDB)
                if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                    # First, check if the table exists and get current column info
                    result = db.session.execute("""
                        SELECT column_name, data_type, character_maximum_length 
                        FROM information_schema.columns 
                        WHERE table_name = 'user' AND column_name = 'password_hash'
                    """).fetchone()
                    
                    if result:
                        current_length = result[2] if result[2] else 0
                        print(f"Current password_hash column length: {current_length}")
                        
                        if current_length < 255:
                            # Alter the password_hash column to be longer
                            db.session.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)')
                            db.session.commit()
                            print("Successfully updated password_hash column to VARCHAR(255)")
                        else:
                            print("password_hash column is already the correct size")
                    else:
                        print("password_hash column not found, will be created with correct size")
                        
            except Exception as alter_error:
                print(f"Column alter error: {alter_error}")
                # Try alternative approach - drop and recreate if needed
                try:
                    db.session.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)')
                    db.session.commit()
                except Exception as e2:
                    print(f"Alternative alter failed: {e2}")
            
            return jsonify({
                "status": "success",
                "message": "Database tables created and updated successfully"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database initialization failed: {str(e)}"
        }), 500

@app.route('/fix-password-column')
def fix_password_column():
    """Fix the password_hash column size specifically"""
    try:
        with app.app_context():
            if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                # Force update the password_hash column
                db.session.execute('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)')
                db.session.commit()
                
                # Verify the change
                result = db.session.execute("""
                    SELECT character_maximum_length 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND column_name = 'password_hash'
                """).fetchone()
                
                new_length = result[0] if result else 0
                
                return jsonify({
                    "status": "success",
                    "message": f"password_hash column updated to VARCHAR({new_length})"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Not using PostgreSQL database"
                })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fix password column: {str(e)}"
        }), 500

@app.route('/test-db')
def test_database():
    """Test database connection and show connection info"""
    try:
        with app.app_context():
            # Test basic connection
            result = db.session.execute('SELECT 1 as test').fetchone()
            
            # Get connection info
            engine = db.engine
            connection_info = {
                'database_url': app.config['SQLALCHEMY_DATABASE_URI'][:50] + '...' if len(app.config['SQLALCHEMY_DATABASE_URI']) > 50 else app.config['SQLALCHEMY_DATABASE_URI'],
                'pool_size': engine.pool.size(),
                'checked_in': engine.pool.checkedin(),
                'checked_out': engine.pool.checkedout(),
                'overflow': engine.pool.overflow(),
                'test_query_result': result[0] if result else None
            }
            
            return jsonify({
                "status": "success",
                "message": "Database connection successful",
                "connection_info": connection_info
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500

@app.route('/sitemap.xml')
def sitemap():
    return send_file('static/sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt', mimetype='text/plain')

@app.route('/api/test_code', methods=['POST'])
@login_required
def test_code():
    """API endpoint to test code execution"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        test_input = data.get('test_input', '')
        time_limit = int(data.get('time_limit', 2))
        memory_limit = int(data.get('memory_limit', 256))
        
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
        
        result = execute_code(code, language, test_input, time_limit, memory_limit)
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run_test_cases', methods=['POST'])
@login_required
def run_test_cases_api():
    """API endpoint to run test cases for a coding question"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        test_cases = data.get('test_cases', [])
        time_limit = int(data.get('time_limit', 2))
        memory_limit = int(data.get('memory_limit', 256))
        
        if not code or not test_cases:
            return jsonify({'success': False, 'error': 'Code and test cases required'}), 400
        
        result = run_test_cases(code, language, test_cases, time_limit, memory_limit)
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/google77cd707098d48f23.html')
def google_verification():
    return send_file('static/google77cd707098d48f23.html', mimetype='text/html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            role = request.form.get('role', 'student')

            if not all([username, email, password, confirm_password]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('signup'))

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('signup'))

            if db.session.query(User).filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('signup'))

            if db.session.query(User).filter_by(email=email).first():
                flash('Email already exists', 'error')
                return redirect(url_for('signup'))

            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role if role in ['student','teacher'] else 'student'
            )
            db.session.add(user)
            db.session.commit()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            db.session.rollback()
            
            # Handle specific database connection errors
            error_msg = str(e)
            if 'SSL connection has been closed' in error_msg:
                flash('Database connection issue. Please try again.', 'error')
            elif 'connection' in error_msg.lower():
                flash('Database connection problem. Please try again.', 'error')
            else:
                flash(f'Signup failed: {error_msg}', 'error')
            
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            user = db.session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            print(f"Error in login: {str(e)}")
            flash('An error occurred. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    progress_records = db.session.query(Progress).filter_by(user_id=current_user.id).all()
    # Teacher's quizzes
    my_quizzes = []
    if getattr(current_user, 'role', 'student') == 'teacher':
        my_quizzes = db.session.query(Quiz).filter_by(created_by=current_user.id).all()
    # Student shared quiz history
    my_submissions = []
    if getattr(current_user, 'role', 'student') == 'student':
        my_submissions = db.session.query(QuizSubmission).filter_by(student_id=current_user.id).order_by(QuizSubmission.submitted_at.desc()).all()
    # Pass current time for checking if review is unlocked
    from datetime import datetime
    current_time = datetime.utcnow()
    return render_template('dashboard.html', progress_records=progress_records, my_quizzes=my_quizzes, my_submissions=my_submissions, current_time=current_time)

def generate_quiz_code(length=6):
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def require_teacher():
    if getattr(current_user, 'role', 'student') != 'teacher':
        flash('Teacher access required', 'error')
        return redirect(url_for('dashboard'))
    return None

# Teacher: create quiz (form + post)
@app.route('/teacher/quiz/new', methods=['GET', 'POST'])
@login_required
def teacher_create_quiz():
    guard = require_teacher()
    if guard:
        return guard

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            questions_raw = request.form.get('questions_json', '').strip()
            if not title or not questions_raw:
                flash('Title and questions are required', 'error')
                return redirect(url_for('teacher_create_quiz'))

            # parse questions json
            questions = json.loads(questions_raw)
            # generate unique code
            code = generate_quiz_code()
            while db.session.query(Quiz).filter_by(code=code).first() is not None:
                code = generate_quiz_code()

            quiz = Quiz(title=title, code=code, created_by=current_user.id)
            db.session.add(quiz)
            db.session.flush()  # get quiz.id

            for q in questions:
                qtype = q.get('type', 'mcq')
                opts = q.get('options', []) if qtype == 'mcq' else []
                qq = QuizQuestion(
                    quiz_id=quiz.id,
                    question=q.get('question', ''),
                    options_json=json.dumps(opts) if opts else None,
                    answer=q.get('answer', ''),
                    qtype=qtype,
                    marks=int(q.get('marks', 1))
                )
                # Handle coding questions
                if qtype == 'coding':
                    qq.test_cases_json = json.dumps(q.get('test_cases', []))
                    qq.language_constraints = json.dumps(q.get('language_constraints', ['python', 'java', 'cpp', 'c']))
                    qq.time_limit_seconds = q.get('time_limit_seconds', 2)
                    qq.memory_limit_mb = q.get('memory_limit_mb', 256)
                    qq.sample_input = q.get('sample_input', '')
                    qq.sample_output = q.get('sample_output', '')
                    starter_code = q.get('starter_code', {})
                    qq.starter_code = json.dumps(starter_code) if starter_code else None
                db.session.add(qq)

            db.session.commit()
            flash(f'Quiz created! Share code: {code}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating quiz: {str(e)}")
            flash('Error creating quiz. Ensure valid JSON.', 'error')
            return redirect(url_for('teacher_create_quiz'))

    return render_template('create_quiz.html')

# Teacher: simple create by topic and number of questions
@app.route('/teacher/quiz/new_simple', methods=['GET', 'POST'])
@login_required
def teacher_create_quiz_simple():
    guard = require_teacher()
    if guard:
        return guard

    if request.method == 'POST':
        try:
            topic = request.form.get('topic', '').strip()
            count = int(request.form.get('count', '0') or 0)
            title = request.form.get('title', '').strip()
            difficulty = request.form.get('difficulty', 'beginner').strip()
            marks = int(request.form.get('marks', '1') or 1)
            duration = request.form.get('duration', '').strip()
            duration_minutes = int(duration) if duration else None

            if not topic or count <= 0:
                flash('Please provide topic and number of questions (>0).', 'error')
                return redirect(url_for('teacher_create_quiz_simple'))

            # If PDF uploaded, extract better topic context
            if 'notes_pdf' in request.files and request.files['notes_pdf'].filename:
                file = request.files['notes_pdf']
                if file and file.filename.lower().endswith('.pdf'):
                    import tempfile, os
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        file.save(tmp.name)
                        extracted = process_document(tmp.name)
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
                    if extracted:
                        topic = f"{topic} - {extracted}"

            question_type = request.form.get('question_type', 'mcq').strip()
            print(f"DEBUG: Generating {question_type} questions for topic: {topic}, count: {count}")
            questions = generate_quiz(topic, difficulty if difficulty in ['beginner','intermediate','advanced'] else 'beginner', question_type, count) or []
            if not questions:
                flash('Failed to generate questions. Try again.', 'error')
                return redirect(url_for('teacher_create_quiz_simple'))
            print(f"DEBUG: Generated {len(questions)} questions, first question type: {questions[0].get('type', 'unknown') if questions else 'none'}")

            if not title:
                title = f"{topic} Quiz"

            # Default marks fill
            for q in questions:
                q['marks'] = marks

            # Store in session for preview
            session['preview_quiz'] = {
                'title': title,
                'topic': topic,
                'difficulty': difficulty,
                'duration_minutes': duration_minutes,
                'question_type': question_type,
                'questions': questions
            }
            return render_template('preview_quiz.html', data=session['preview_quiz'])
        except Exception as e:
            db.session.rollback()
            print(f"Error creating simple quiz: {str(e)}")
            flash('Error creating quiz. Please try again.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))

    return render_template('create_quiz_simple.html')

# Preview step for teacher to adjust marks before finalizing
@app.route('/teacher/quiz/preview', methods=['POST'])
@login_required
def teacher_quiz_preview():
    guard = require_teacher()
    if guard:
        return guard
    try:
        # Rebuild inputs
        title = request.form.get('title', '').strip()
        topic = request.form.get('topic', '').strip()
        count = int(request.form.get('count', '0') or 0)
        difficulty = request.form.get('difficulty', 'beginner').strip()
        marks = int(request.form.get('marks', '1') or 1)
        duration = request.form.get('duration', '').strip()
        duration_minutes = int(duration) if duration else None

        if not topic or count <= 0:
            flash('Provide topic and number of questions.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))

        question_type = request.form.get('question_type', 'mcq').strip()
        print(f"DEBUG: Preview - Generating {question_type} questions for topic: {topic}, count: {count}")
        questions = generate_quiz(topic, difficulty if difficulty in ['beginner','intermediate','advanced'] else 'beginner', question_type, count) or []
        if not questions:
            flash('Failed to generate questions.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))
        print(f"DEBUG: Preview - Generated {len(questions)} questions, first question type: {questions[0].get('type', 'unknown') if questions else 'none'}")

        # Default marks fill
        for q in questions:
            q['marks'] = marks

        # Store in session for finalize
        session['preview_quiz'] = {
            'title': title or f"{topic} Quiz",
            'topic': topic,
            'difficulty': difficulty,
            'duration_minutes': duration_minutes,
            'question_type': question_type,
            'questions': questions
        }
        return render_template('preview_quiz.html', data=session['preview_quiz'])
    except Exception as e:
        print(f"Preview error: {e}")
        flash('Error preparing preview.', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))

@app.route('/teacher/quiz/finalize', methods=['POST'])
@login_required
def teacher_quiz_finalize():
    guard = require_teacher()
    if guard:
        return guard
    data = session.get('preview_quiz')
    if not data:
        flash('No quiz in preview.', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))
    try:
        # Read marks overrides
        q_overrides = []
        for i, q in enumerate(data['questions']):
            new_marks = request.form.get(f'marks_{i}')
            try:
                q['marks'] = int(new_marks)
            except Exception:
                pass
            q_overrides.append(q)

        code = generate_quiz_code()
        while db.session.query(Quiz).filter_by(code=code).first() is not None:
            code = generate_quiz_code()

        quiz = Quiz(title=data['title'], code=code, created_by=current_user.id, difficulty=data['difficulty'], duration_minutes=data['duration_minutes'])
        db.session.add(quiz)
        db.session.flush()

        for q in q_overrides:
            qtype = q.get('type', 'mcq')
            opts = q.get('options', []) if qtype == 'mcq' else []
            qq = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get('question', ''),
                options_json=json.dumps(opts) if opts else None,
                answer=q.get('answer', ''),
                qtype=qtype,
                marks=int(q.get('marks', 1))
            )
            # Handle coding questions
            if qtype == 'coding':
                try:
                    test_cases = q.get('test_cases', [])
                    qq.test_cases_json = json.dumps(test_cases) if test_cases else None
                    
                    language_constraints = q.get('language_constraints', ['python', 'java', 'cpp', 'c'])
                    qq.language_constraints = json.dumps(language_constraints) if language_constraints else json.dumps(['python', 'java', 'cpp', 'c'])
                    
                    qq.time_limit_seconds = q.get('time_limit_seconds', 2) or 2
                    qq.memory_limit_mb = q.get('memory_limit_mb', 256) or 256
                    qq.sample_input = q.get('sample_input', '') or ''
                    qq.sample_output = q.get('sample_output', '') or ''
                    
                    starter_code = q.get('starter_code', {})
                    if starter_code and isinstance(starter_code, dict):
                        qq.starter_code = json.dumps(starter_code)
                    elif starter_code:
                        qq.starter_code = json.dumps(starter_code)
                    else:
                        qq.starter_code = None
                except Exception as coding_error:
                    print(f"Error processing coding question fields: {coding_error}")
                    print(f"Question data: {q}")
                    raise
            db.session.add(qq)

        db.session.commit()
        session.pop('preview_quiz', None)
        flash(f'Quiz created! Share code: {code}', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Finalize error: {e}")
        print(f"Full traceback:\n{error_details}")
        flash(f'Error finalizing quiz: {str(e)}', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))

# Student: join quiz by code
@app.route('/quiz/join', methods=['GET', 'POST'])
@login_required
def join_quiz():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        quiz = db.session.query(Quiz).filter_by(code=code).first()
        if not quiz:
            flash('Invalid quiz code', 'error')
            return redirect(url_for('join_quiz'))
        
        # Check if student has already completed this quiz
        existing_completed = db.session.query(QuizSubmission).filter_by(
            quiz_id=quiz.id, 
            student_id=current_user.id, 
            completed=True
        ).first()
        
        if existing_completed:
            flash('You have already attempted this quiz. You can only take it once.', 'error')
            return redirect(url_for('dashboard'))
        
        return redirect(url_for('take_shared_quiz', code=code))
    return render_template('join_quiz.html')

# Take shared quiz
@app.route('/quiz/take/<code>')
@login_required
def take_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # Check if student has already completed this quiz
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    
    q_rows = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    # Parse options JSON server-side to avoid template errors
    parsed_questions = []
    for q in q_rows:
        try:
            options = json.loads(q.options_json) if q.options_json else []
        except Exception:
            options = []
        
        question_data = {
            'id': q.id,
            'question': q.question,
            'qtype': q.qtype,
            'marks': q.marks,
            'options': options,
        }
        
        # Add coding question data
        if q.qtype == 'coding':
            try:
                question_data['test_cases'] = json.loads(q.test_cases_json) if q.test_cases_json else []
                question_data['language_constraints'] = json.loads(q.language_constraints) if q.language_constraints else ['python', 'java', 'cpp', 'c']
                question_data['time_limit_seconds'] = q.time_limit_seconds or 2
                question_data['memory_limit_mb'] = q.memory_limit_mb or 256
                question_data['sample_input'] = q.sample_input or ''
                question_data['sample_output'] = q.sample_output or ''
                question_data['starter_code'] = json.loads(q.starter_code) if q.starter_code else {}
            except Exception as e:
                print(f"Error parsing coding question data: {e}")
                question_data['test_cases'] = []
                question_data['language_constraints'] = ['python', 'java', 'cpp', 'c']
        
        parsed_questions.append(question_data)
    # Ensure a started submission exists (one per student/quiz if not completed)
    existing = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
    if not existing:
        existing = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id, question_count=len(q_rows))
        db.session.add(existing)
        db.session.commit()
    return render_template('take_shared_quiz.html', quiz=quiz, questions=parsed_questions)

# Submit shared quiz
@app.route('/quiz/submit/<code>', methods=['POST'])
@login_required
def submit_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # Check if student has already completed this quiz
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()

    total_marks = 0.0
    scored_marks = 0.0
    from datetime import timedelta
    submission = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
    if not submission:
        submission = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id)
        db.session.add(submission)
        db.session.flush()

    answered_count = 0
    for q in questions:
        total_marks += float(q.marks or 1)
        key = f'q_{q.id}'
        user_ans = request.form.get(key, '').strip()
        is_correct = None
        ai_score = None
        gained = 0.0
        code_language = None
        test_results_json = None
        passed_test_cases = 0
        total_test_cases = 0

        if q.qtype == 'mcq':
            is_correct = (user_ans.split('. ')[0] == (q.answer or '')) if user_ans else False
            gained = float(q.marks or 1) if is_correct else 0.0
        elif q.qtype == 'coding':
            # Handle coding question submission
            code_data = request.form.get(f'code_{q.id}', '').strip()
            language = request.form.get(f'language_{q.id}', 'python')
            
            if code_data:
                try:
                    # Parse test cases
                    test_cases = json.loads(q.test_cases_json) if q.test_cases_json else []
                    time_limit = q.time_limit_seconds or 2
                    memory_limit = q.memory_limit_mb or 256
                    
                    # Run test cases
                    test_results = run_test_cases(code_data, language, test_cases, time_limit, memory_limit)
                    
                    # Calculate score based on passed test cases
                    passed_test_cases = test_results['passed']
                    total_test_cases = test_results['total']
                    percentage_passed = test_results['percentage'] / 100.0
                    
                    gained = float(q.marks or 1) * percentage_passed
                    is_correct = percentage_passed == 1.0  # Perfect score
                    code_language = language
                    test_results_json = json.dumps(test_results['results'])
                    user_ans = code_data  # Store code as answer
                except Exception as e:
                    print(f"Error evaluating coding question: {e}")
                    gained = 0.0
                    is_correct = False
                    code_language = language
                    test_results_json = json.dumps([])
                    user_ans = code_data
        else:
            # subjective via AI
            if user_ans:
                ai_score = evaluate_subjective_answer(q.question, user_ans, q.answer or '')
                gained = float(q.marks or 1) * float(ai_score or 0.0)
                is_correct = (ai_score or 0.0) >= 0.6
            else:
                ai_score = 0.0
                is_correct = False

        scored_marks += gained
        ans = QuizAnswer(
            submission_id=submission.id,
            question_id=q.id,
            user_answer=user_ans,
            is_correct=is_correct,
            ai_score=ai_score,
            scored_marks=gained,
            code_language=code_language,
            test_results_json=test_results_json,
            passed_test_cases=passed_test_cases,
            total_test_cases=total_test_cases
        )
        db.session.add(ans)
        if user_ans:
            answered_count += 1

    percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
    passed = percentage >= 60
    submission.score = scored_marks
    submission.total = total_marks
    submission.percentage = percentage
    submission.passed = passed
    # set review unlock time 15 minutes after submission
    submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
    # check if student exited fullscreen during test
    submission.fullscreen_exit_flag = request.form.get('fullscreen_exit') == 'true'
    submission.answered_count = answered_count
    submission.question_count = len(questions)
    submission.is_full_completion = (answered_count == len(questions)) and (not submission.fullscreen_exit_flag)
    submission.completed = True
    db.session.commit()

    flash(f'Submitted. Score: {scored_marks:.1f}/{total_marks} ({percentage:.0f}%).', 'success')
    return redirect(url_for('dashboard'))

# Auto-submit partial answers on fullscreen exit or tab close
@app.route('/quiz/auto_submit/<code>', methods=['POST'])
@login_required
def auto_submit_partial(code):
    try:
        quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
        if not quiz:
            return ('', 204)
        questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
        submission = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
        if not submission:
            submission = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id)
            db.session.add(submission)
            db.session.flush()

        total_marks = 0.0
        scored_marks = 0.0
        answered_count = 0
        data = request.get_json(silent=True) or {}

        for q in questions:
            total_marks += float(q.marks or 1)
            key = f'q_{q.id}'
            user_ans = (data.get(key) or '').strip()
            is_correct = None
            ai_score = None
            gained = 0.0
            if q.qtype == 'mcq':
                is_correct = (user_ans.split('. ')[0] == (q.answer or '')) if user_ans else False
                gained = float(q.marks or 1) if is_correct else 0.0
            else:
                if user_ans:
                    ai_score = evaluate_subjective_answer(q.question, user_ans, q.answer or '')
                    gained = float(q.marks or 1) * float(ai_score or 0.0)
                    is_correct = (ai_score or 0.0) >= 0.6
                else:
                    ai_score = 0.0
                    is_correct = False
            if user_ans:
                answered_count += 1
            # Upsert answer
            existing_ans = db.session.query(QuizAnswer).filter_by(submission_id=submission.id, question_id=q.id).first()
            if existing_ans:
                existing_ans.user_answer = user_ans
                existing_ans.is_correct = is_correct
                existing_ans.ai_score = ai_score
                existing_ans.scored_marks = gained
            else:
                db.session.add(QuizAnswer(
                    submission_id=submission.id,
                    question_id=q.id,
                    user_answer=user_ans,
                    is_correct=is_correct,
                    ai_score=ai_score,
                    scored_marks=gained
                ))

        submission.score = scored_marks
        submission.total = total_marks
        submission.percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        submission.passed = submission.percentage >= 60
        from datetime import timedelta
        submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
        submission.fullscreen_exit_flag = True
        submission.answered_count = answered_count
        submission.question_count = len(questions)
        submission.is_full_completion = False
        submission.completed = True
        db.session.commit()
        return ('', 204)
    except Exception as e:
        db.session.rollback()
        return ('', 204)

# Student: view quiz result (after 15 minutes)
@app.route('/quiz/result/<int:submission_id>')
@login_required
def view_quiz_result(submission_id):
    submission = db.session.query(QuizSubmission).filter_by(id=submission_id, student_id=current_user.id).first()
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if review is unlocked (15 minutes have passed)
    from datetime import datetime
    current_time = datetime.utcnow()
    if submission.review_unlocked_at and submission.review_unlocked_at > current_time:
        flash('Results will be available 15 minutes after submission', 'info')
        return redirect(url_for('dashboard'))
    
    # Get quiz and questions
    quiz = db.session.query(Quiz).filter_by(id=submission.quiz_id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).order_by(QuizQuestion.id).all()
    answers = db.session.query(QuizAnswer).filter_by(submission_id=submission.id).all()
    
    # Create answer map
    answer_map = {ans.question_id: ans for ans in answers}
    
    # Format results for template
    results = []
    for q in questions:
        ans = answer_map.get(q.id)
        if q.qtype == 'mcq':
            # Parse options
            options = json.loads(q.options_json) if q.options_json else []
            user_answer = ans.user_answer if ans else ''
            correct_option = next((opt for opt in options if opt.startswith(f"{q.answer}.")), '') if q.answer else ''
            
            results.append({
                'question': q.question,
                'user_answer': user_answer,
                'correct_answer': correct_option,
                'is_correct': ans.is_correct if ans else False,
                'type': 'mcq',
                'marks': q.marks
            })
        elif q.qtype == 'subjective':
            results.append({
                'question': q.question,
                'user_answer': ans.user_answer if ans else '',
                'sample_answer': q.answer or 'N/A',
                'ai_score': ans.ai_score if ans else 0.0,
                'scored_marks': ans.scored_marks if ans else 0.0,
                'marks': q.marks,
                'type': 'subjective'
            })
        elif q.qtype == 'coding':
            # Parse test results
            test_results = json.loads(ans.test_results_json) if ans and ans.test_results_json else []
            results.append({
                'question': q.question,
                'user_answer': ans.user_answer if ans else '',
                'code_language': ans.code_language if ans else '',
                'passed_test_cases': ans.passed_test_cases if ans else 0,
                'total_test_cases': ans.total_test_cases if ans else 0,
                'test_results': test_results,
                'scored_marks': ans.scored_marks if ans else 0.0,
                'marks': q.marks,
                'type': 'coding',
                'sample_input': q.sample_input,
                'sample_output': q.sample_output
            })
    
    final_score = f"{submission.score:.1f}/{submission.total:.1f}"
    percentage = submission.percentage
    passed = submission.passed
    
    return render_template('shared_quiz_results.html', 
                         quiz=quiz,
                         submission=submission,
                         results=results,
                         final_score=final_score,
                         percentage=percentage,
                         passed=passed)

# Teacher: view results
@app.route('/teacher/quiz/<code>/results')
@login_required
def teacher_quiz_results(code):
    guard = require_teacher()
    if guard:
        return guard
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    submissions = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id).order_by(QuizSubmission.submitted_at.desc()).all()
    # Join with users
    student_map = {u.id: u for u in db.session.query(User).filter(User.id.in_([s.student_id for s in submissions])).all()}
    return render_template('teacher_results.html', quiz=quiz, submissions=submissions, student_map=student_map)

# Teacher: allow student to retake quiz
@app.route('/teacher/quiz/<code>/allow-retake/<int:submission_id>', methods=['POST'])
@login_required
def allow_student_retake(code, submission_id):
    guard = require_teacher()
    if guard:
        return guard
    
    # Verify quiz ownership
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found or you do not have permission', 'error')
        return redirect(url_for('dashboard'))
    
    # Get the submission and verify it belongs to this quiz
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id,
        quiz_id=quiz.id
    ).first()
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('teacher_quiz_results', code=code))
    
    # Reset the submission to allow retake
    # Delete old answers so student starts fresh
    db.session.query(QuizAnswer).filter_by(submission_id=submission.id).delete()
    
    # Reset submission status
    submission.completed = False
    submission.score = 0.0
    submission.total = 0.0
    submission.percentage = 0.0
    submission.passed = False
    submission.review_unlocked_at = None
    submission.answered_count = 0
    submission.fullscreen_exit_flag = False
    submission.is_full_completion = False
    
    db.session.commit()
    
    # Get student username for message
    student = db.session.query(User).filter_by(id=submission.student_id).first()
    student_name = student.username if student else f"Student ID {submission.student_id}"
    
    flash(f'Successfully allowed {student_name} to retake the quiz. Their previous submission has been reset.', 'success')
    return redirect(url_for('teacher_quiz_results', code=code))

# Temporary helper: run lightweight migration for SQLite (adds missing columns/tables)
@app.route('/dev/migrate')
def dev_migrate():
    try:
        # Only for SQLite local use
        from sqlalchemy import text
        with db.engine.begin() as conn:
            # Check if 'role' column exists on user
            has_role = False
            try:
                res = conn.execute(text("PRAGMA table_info(user);"))
                for row in res:
                    if str(row[1]) == 'role':
                        has_role = True
                        break
            except Exception:
                pass

            if not has_role:
                try:
                    conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student';"))
                except Exception as e:
                    print(f"ALTER TABLE role add failed (may already exist): {e}")

            # Add difficulty and duration to quiz if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz);"))
                cols = [str(r[1]) for r in res]
                if 'difficulty' not in cols:
                    conn.execute(text("ALTER TABLE quiz ADD COLUMN difficulty VARCHAR(20) DEFAULT 'beginner';"))
                if 'duration_minutes' not in cols:
                    conn.execute(text("ALTER TABLE quiz ADD COLUMN duration_minutes INTEGER;"))
            except Exception as e:
                print(f"ALTER TABLE quiz add columns failed (may exist): {e}")

            # Add review_unlocked_at and fullscreen_exit_flag to quiz_submission if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz_submission);"))
                cols = [str(r[1]) for r in res]
                if 'review_unlocked_at' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN review_unlocked_at DATETIME;"))
                if 'fullscreen_exit_flag' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN fullscreen_exit_flag BOOLEAN DEFAULT 0;"))
                if 'answered_count' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN answered_count INTEGER DEFAULT 0;"))
                if 'question_count' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN question_count INTEGER DEFAULT 0;"))
                if 'is_full_completion' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN is_full_completion BOOLEAN DEFAULT 0;"))
                if 'started_at' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN started_at DATETIME;"))
                if 'completed' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN completed BOOLEAN DEFAULT 0;"))
            except Exception as e:
                print(f"ALTER TABLE quiz_submission add columns failed (may exist): {e}")

            # Add coding question columns to quiz_question if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz_question);"))
                cols = [str(r[1]) for r in res]
                if 'test_cases_json' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN test_cases_json TEXT;"))
                if 'language_constraints' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN language_constraints TEXT;"))
                if 'time_limit_seconds' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN time_limit_seconds INTEGER;"))
                if 'memory_limit_mb' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN memory_limit_mb INTEGER;"))
                if 'sample_input' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN sample_input TEXT;"))
                if 'sample_output' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN sample_output TEXT;"))
                if 'starter_code' not in cols:
                    conn.execute(text("ALTER TABLE quiz_question ADD COLUMN starter_code TEXT;"))
            except Exception as e:
                print(f"ALTER TABLE quiz_question add coding columns failed (may exist): {e}")

            # Add coding answer columns to quiz_answer if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz_answer);"))
                cols = [str(r[1]) for r in res]
                if 'code_language' not in cols:
                    conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN code_language VARCHAR(20);"))
                if 'test_results_json' not in cols:
                    conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN test_results_json TEXT;"))
                if 'passed_test_cases' not in cols:
                    conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN passed_test_cases INTEGER DEFAULT 0;"))
                if 'total_test_cases' not in cols:
                    conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN total_test_cases INTEGER DEFAULT 0;"))
            except Exception as e:
                print(f"ALTER TABLE quiz_answer add coding columns failed (may exist): {e}")

        # Create any new tables
        db.create_all()
        flash('Migration completed. If you were logged in, reload the page. Next, visit /dev/promote_me.', 'success')
    except Exception as e:
        print(f"Migration error: {e}")
        flash('Migration failed. See server logs.', 'error')
    return redirect(url_for('dashboard'))

# Temporary helper: promote current user to teacher (local/dev use)
@app.route('/dev/promote_me')
@login_required
def dev_promote_me():
    try:
        current_user.role = 'teacher'
        db.session.commit()
        flash('Your account is now a Teacher. You can create shared quizzes.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Promote error: {e}")
        flash('Failed to promote user.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET':
        # Handle topic parameter from AI learning modal or next/retry level
        topic = request.args.get('topic', '')
        difficulty = request.args.get('difficulty', '')
        action = request.args.get('action', '')
        
        if topic:
            return render_template('quiz.html', 
                                 prefill_topic=topic, 
                                 prefill_difficulty=difficulty,
                                 action=action)
    
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        question_type = request.form.get('question_type', 'mcq')
        mcq_count = int(request.form.get('mcq_count', 3))
        subj_count = int(request.form.get('subj_count', 2))
        difficulty_level = request.form.get('difficulty_level', 'beginner')
        
        # Check if PDF file was uploaded
        if 'file_upload' in request.files and request.files['file_upload'].filename:
            file = request.files['file_upload']
            if file and file.filename.lower().endswith('.pdf'):
                try:
                    # Save file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        file.save(tmp_file.name)
                        tmp_path = tmp_file.name
                    
                    # Process the PDF to extract topic
                    extracted_topic = process_document(tmp_path)
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    if extracted_topic:
                        topic = extracted_topic
                        flash(f'Topic extracted from PDF: {topic}', 'success')
                    else:
                        flash('Could not extract topic from PDF. Please enter a topic manually.', 'error')
                        return redirect(url_for('quiz'))
                        
                except Exception as e:
                    flash(f'Error processing PDF: {str(e)}', 'error')
                    return redirect(url_for('quiz'))
        
        # Ensure we have a topic
        if not topic:
            flash('Please either enter a topic OR upload a PDF file.', 'error')
            return redirect(url_for('quiz'))

        # Get user's current bloom level for this topic (for progress tracking)
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
        bloom_level = progress.bloom_level if progress else 1

        # Generate questions using difficulty level
        questions = []
        if question_type == "both":
            mcq_questions = generate_quiz(topic, difficulty_level, "mcq", mcq_count)
            subj_questions = generate_quiz(topic, difficulty_level, "subjective", subj_count)
            if mcq_questions and subj_questions:
                questions = mcq_questions + subj_questions
        else:
            num_q = mcq_count if question_type == "mcq" else subj_count
            questions = generate_quiz(topic, difficulty_level, question_type, num_q)

        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': bloom_level,
                'difficulty_level': difficulty_level
            }
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate quiz questions', 'error')

    return render_template('quiz.html')

@app.route('/take_quiz')
@login_required
def take_quiz():
    quiz_data = session.get('current_quiz')
    if not quiz_data:
        flash('No quiz available', 'error')
        return redirect(url_for('quiz'))
    
    return render_template('take_quiz.html', quiz_data=quiz_data)

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    quiz_data = session.get('current_quiz')
    if not quiz_data:
        return jsonify({'error': 'No quiz available'})

    questions = quiz_data['questions']
    topic = quiz_data['topic']
    bloom_level = quiz_data['bloom_level']
    difficulty_level = quiz_data.get('difficulty_level', 'beginner')
    
    # Get answers for each question
    user_answers = []
    for i in range(len(questions)):
        question = questions[i]
        if question.get('type') == 'mcq':
            # For MCQ questions, get from question group
            answer = request.form.get(f'question_{i}')
        else:
            # For subjective questions, get from subjective_answers array
            answer = request.form.get(f'subjective_answers[{i}]')
        
        if not answer:
            return jsonify({'error': f'Please answer question {i+1}'})
        user_answers.append(answer)

    # Calculate scores
    correct_answers = 0
    total_marks = 0
    scored_marks = 0
    results = []

    for i, (q, user_ans) in enumerate(zip(questions, user_answers)):
        if q.get('type') == 'mcq':
            user_choice = user_ans.split(". ")[0] if user_ans else ""
            is_correct = user_choice == q["answer"]
            if is_correct:
                correct_answers += 1
            results.append({
                'question': q['question'],
                'user_answer': user_ans,
                'correct_answer': next((opt for opt in q["options"] if opt.startswith(f"{q['answer']}.")), ""),
                'is_correct': is_correct,
                'type': 'mcq'
            })
        else:  # subjective
            marks = q.get('marks', 10)
            total_marks += marks
            
            if user_ans.strip():
                ai_score = evaluate_subjective_answer(q['question'], user_ans, q.get('answer', ''))
                scored_marks += ai_score * marks
                if ai_score >= 0.6:
                    correct_answers += 1
            else:
                ai_score = 0.0

            results.append({
                'question': q['question'],
                'user_answer': user_ans,
                'sample_answer': q.get('answer', 'N/A'),
                'marks': marks,
                'ai_score': ai_score,
                'scored_marks': ai_score * marks,
                'type': 'subjective'
            })

    # Calculate final score
    has_subjective = any(q.get('type') == 'subjective' for q in questions)
    
    if has_subjective:
        percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        passed = percentage >= 60
        final_score = f"{scored_marks:.1f}/{total_marks} marks"
    else:
        percentage = (correct_answers / len(questions)) * 100 if questions else 0
        passed = percentage >= 60
        final_score = f"{correct_answers}/{len(questions)}"

    # Update progress
    progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
    if progress:
        if passed and bloom_level + 1 > progress.bloom_level:
            progress.bloom_level = bloom_level + 1
    else:
        new_progress = Progress(
            user_id=current_user.id,
            topic=topic,
            bloom_level=bloom_level + 1 if passed else bloom_level
        )
        db.session.add(new_progress)
    
    db.session.commit()

    # Clear quiz session
    session.pop('current_quiz', None)

    return render_template('quiz_results.html', 
                         results=results, 
                         final_score=final_score, 
                         percentage=percentage, 
                         passed=passed,
                         topic=topic,
                         bloom_level=bloom_level,
                         difficulty_level=difficulty_level)

@app.route('/next_level', methods=['POST'])
@login_required
def next_level():
    """Automatically generate next level quiz and redirect to take_quiz"""
    try:
        topic = request.form.get('topic', '').strip()
        difficulty_level = request.form.get('difficulty_level', 'beginner').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('quiz'))
        
        # Determine next difficulty level
        difficulty_mapping = {
            "beginner": "intermediate",
            "intermediate": "difficult", 
            "difficult": "difficult"  # Stay at difficult if already at highest level
        }
        next_difficulty = difficulty_mapping.get(difficulty_level, "intermediate")
        
        # Generate questions for next level
        questions = generate_quiz(topic, next_difficulty, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': 1,  # This will be updated based on difficulty
                'difficulty_level': next_difficulty
            }
            flash(f'Generated {next_difficulty.title()} level quiz for {topic}!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate next level quiz', 'error')
            return redirect(url_for('quiz'))
    except Exception as e:
        print(f"Error in next_level: {str(e)}")
        flash('An error occurred while generating the next level quiz', 'error')
        return redirect(url_for('quiz'))

@app.route('/retry_level', methods=['POST'])
@login_required
def retry_level():
    """Automatically generate retry quiz and redirect to take_quiz"""
    try:
        topic = request.form.get('topic', '').strip()
        difficulty_level = request.form.get('difficulty_level', 'beginner').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('quiz'))
        
        # Generate questions for the same level
        questions = generate_quiz(topic, difficulty_level, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': 1,  # This will be updated based on difficulty
                'difficulty_level': difficulty_level
            }
            flash(f'Generated new {difficulty_level.title()} level quiz for {topic}!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate retry quiz', 'error')
            return redirect(url_for('quiz'))
    except Exception as e:
        print(f"Error in retry_level: {str(e)}")
        flash('An error occurred while generating the retry quiz', 'error')
        return redirect(url_for('quiz'))

@app.route('/continue_learning', methods=['POST'])
@login_required
def continue_learning():
    """Continue learning from where user left off based on their progress"""
    try:
        topic = request.form.get('topic', '').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('dashboard'))
        
        # Get user's current progress for this topic
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
        
        if not progress:
            flash('No progress found for this topic', 'error')
            return redirect(url_for('dashboard'))
        
        # Map bloom level to difficulty level
        difficulty_level = get_difficulty_from_bloom_level(progress.bloom_level)
        
        # Generate questions for the current level
        questions = generate_quiz(topic, difficulty_level, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': progress.bloom_level,
                'difficulty_level': difficulty_level
            }
            flash(f'Continuing {topic} at {difficulty_level.title()} level (Bloom Level {progress.bloom_level})!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate quiz for continuing learning', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error in continue_learning: {str(e)}")
        flash('An error occurred while continuing your learning', 'error')
        return redirect(url_for('dashboard'))

@app.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Handle PDF upload and extract topic"""
    if 'file_upload' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file_upload']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Save file temporarily
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Process the PDF to extract topic
            topic = process_document(tmp_path)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            if topic:
                return jsonify({'success': True, 'topic': topic})
            else:
                return jsonify({'success': False, 'error': 'Could not extract topic from PDF'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error processing PDF: {str(e)}'})
    
    return jsonify({'success': False, 'error': 'Invalid file format. Please upload a PDF.'})

@app.route('/ai_learn', methods=['POST'])
@login_required
def ai_learn():
    """AI-powered learning content generation"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        level = data.get('level', 'intermediate')
        style = data.get('style', 'theoretical')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'})
        
        # Generate learning content using AI
        configure_google_ai()  # Ensure Google AI is configured
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Create a personalized learning path for {topic} at {level} level, 
        focusing on {style} learning style.
        
        IMPORTANT: You MUST use this EXACT format with these EXACT section headers:
        
        ## OVERVIEW
        [Write a brief 2-3 sentence overview of the topic here]
        
        ## KEY CONCEPTS
        • [Write concept 1 with brief explanation here]
        • [Write concept 2 with brief explanation here]
        • [Write concept 3 with brief explanation here]
        
        ## LEARNING OBJECTIVES
        ✓ [Write objective 1 here]
        ✓ [Write objective 2 here]
        ✓ [Write objective 3 here]
        
        ## STUDY APPROACH
        [Write practical study recommendations based on {style} learning style here]
        
        ## COMMON MISCONCEPTIONS
        ⚠️ [Write misconception 1 and why it's wrong here]
        ⚠️ [Write misconception 2 and why it's wrong here]
        
        ## NEXT STEPS
        [Write what to do after understanding these basics here]
        
        CRITICAL: Start your response immediately with "## OVERVIEW" and follow the exact format above. Do not add any introductory text or explanations before the sections.
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        return jsonify({'success': True, 'content': content})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating learning content: {str(e)}'})

@app.route('/download_pdf')
@login_required
def download_pdf():
    # PDF download disabled for Vercel - requires reportlab
    return jsonify({'error': 'PDF download not available on Vercel'}), 503

# Download quiz results as CSV
@app.route('/teacher/quiz/<code>/results/download/csv')
@login_required
def download_quiz_results_csv(code):
    guard = require_teacher()
    if guard:
        return guard
    
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    
    submissions = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id).order_by(QuizSubmission.submitted_at.desc()).all()
    student_map = {u.id: u for u in db.session.query(User).filter(User.id.in_([s.student_id for s in submissions])).all()}
    
    # Prepare data for CSV
    data = []
    for s in submissions:
        student = student_map.get(s.student_id)
        data.append({
            'Student': student.username if student else str(s.student_id),
            'Score': f"{s.score:.1f}/{s.total:.1f}",
            'Percentage': f"{s.percentage:.0f}%",
            'Status': 'Passed' if s.passed else 'Failed',
            'Integrity': 'Clean' if s.is_full_completion else 'Hold',
            'Answered Questions': f"{s.answered_count}/{s.question_count}",
            'Exited Fullscreen': 'Yes' if s.fullscreen_exit_flag else 'No',
            'Submitted At': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create CSV (use pandas if available, otherwise use csv module)
    if HAS_PANDAS:
        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
    else:
        # Use built-in csv module
        csv_buffer = io.StringIO()
        if data:
            writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        csv_data = csv_buffer.getvalue()
    
    # Create BytesIO for send_file
    output = io.BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"Quiz_Results_{quiz.title}_{code}.csv",
        mimetype='text/csv'
    )

# Download quiz results as XLSX
@app.route('/teacher/quiz/<code>/results/download/xlsx')
@login_required
def download_quiz_results_xlsx(code):
    guard = require_teacher()
    if guard:
        return guard
    
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    
    submissions = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id).order_by(QuizSubmission.submitted_at.desc()).all()
    student_map = {u.id: u for u in db.session.query(User).filter(User.id.in_([s.student_id for s in submissions])).all()}
    
    # Prepare data for XLSX
    data = []
    for s in submissions:
        student = student_map.get(s.student_id)
        data.append({
            'Student': student.username if student else str(s.student_id),
            'Score': f"{s.score:.1f}/{s.total:.1f}",
            'Percentage': f"{s.percentage:.0f}%",
            'Status': 'Passed' if s.passed else 'Failed',
            'Integrity': 'Clean' if s.is_full_completion else 'Hold',
            'Answered Questions': f"{s.answered_count}/{s.question_count}",
            'Exited Fullscreen': 'Yes' if s.fullscreen_exit_flag else 'No',
            'Submitted At': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create XLSX (requires pandas and openpyxl)
    if not HAS_PANDAS:
        flash('XLSX export requires pandas. Please use CSV export instead.', 'error')
        return redirect(url_for('teacher_quiz_results', code=code))
    
    df = pd.DataFrame(data)
    xlsx_buffer = io.BytesIO()
    with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Quiz Results', index=False)
    
    xlsx_buffer.seek(0)
    
    return send_file(
        xlsx_buffer,
        as_attachment=True,
        download_name=f"Quiz_Results_{quiz.title}_{code}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page Not Found"), 404

# Database initialization function
def init_database():
    """Initialize database tables - called when needed"""
    try:
        with app.app_context():
            db.create_all()
            print("Database initialized successfully!")
            print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # Continue running the app even if database fails

# Initialize database only if not in Vercel environment
if not os.environ.get('VERCEL'):
    init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

