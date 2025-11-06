# 📝 Complete Feature Implementation Guide

## Features to Add:

1. ✅ 15-Minute Review Unlock
2. ✅ Coding Question Support  
3. ✅ One Attempt Per Student
4. ✅ Teacher Allow Retake

---

## 🔧 Implementation Steps

### 1. Update Database Models

Add to your `app.py` in the model definitions:

```python
# In QuizQuestion model:
test_cases_json = db.Column(db.Text)  # JSON array of test cases
language_constraints = db.Column(db.Text)  # JSON array: ["python", "java", "cpp", "c"]
time_limit_seconds = db.Column(db.Integer)
memory_limit_mb = db.Column(db.Integer)
sample_input = db.Column(db.Text)
sample_output = db.Column(db.Text)
starter_code = db.Column(db.Text)  # JSON object with starter code per language

# In QuizAnswer model:
code_language = db.Column(db.String(20))
test_results_json = db.Column(db.Text)  # JSON array of test results
passed_test_cases = db.Column(db.Integer, default=0)
total_test_cases = db.Column(db.Integer, default=0)

# In QuizSubmission model:
review_unlocked_at = db.Column(db.DateTime)
fullscreen_exit_flag = db.Column(db.Boolean, default=False)
answered_count = db.Column(db.Integer, default=0)
question_count = db.Column(db.Integer, default=0)
is_full_completion = db.Column(db.Boolean, default=False)
started_at = db.Column(db.DateTime)
completed = db.Column(db.Boolean, default=False)
```

### 2. Add Code Execution Functions

Add these functions to `app.py`:

```python
def execute_code(code, language, test_input, time_limit=2, memory_limit=256):
    """Execute code using Piston API"""
    piston_url = "https://emkc.org/api/v2/piston/execute"
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
            "files": [{"content": code}],
            "stdin": test_input,
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": time_limit * 1000,
            "memory_limit": memory_limit * 1024 * 1024
        }
        response = requests.post(piston_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return {
                'status': 'success',
                'output': result.get('run', {}).get('stdout', '').strip(),
                'stderr': result.get('run', {}).get('stderr', '').strip()
            }
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'output': '', 'stderr': ''}
    return {'status': 'error', 'message': 'Execution failed', 'output': '', 'stderr': ''}

def run_test_cases(code, language, test_cases, time_limit=2, memory_limit=256):
    """Run multiple test cases and return results"""
    results = []
    passed = 0
    for test_case in test_cases:
        test_input = test_case.get('input', '')
        expected_output = test_case.get('expected_output', '').strip()
        exec_result = execute_code(code, language, test_input, time_limit, memory_limit)
        if exec_result['status'] == 'success':
            actual_output = exec_result['output'].strip()
            is_correct = actual_output == expected_output
            if is_correct:
                passed += 1
        else:
            is_correct = False
            actual_output = exec_result.get('stderr', exec_result.get('message', 'Error'))
        results.append({
            'input': test_input,
            'expected_output': expected_output,
            'actual_output': actual_output,
            'is_correct': is_correct,
            'is_hidden': test_case.get('is_hidden', False)
        })
    return results, passed, len(test_cases)
```

### 3. Update Quiz Generation

In your `generate_quiz` function, add support for coding questions:

```python
# When question_type == "coding", generate coding questions with:
# - Problem statement
# - Sample input/output
# - Test cases (some hidden)
# - Starter code for multiple languages
```

### 4. Update Quiz Taking Route

In `take_shared_quiz` route, add:

```python
# Check if student already completed
existing_completed = db.session.query(QuizSubmission).filter_by(
    quiz_id=quiz.id, 
    student_id=current_user.id, 
    completed=True
).first()

if existing_completed:
    flash('You have already attempted this quiz. Contact teacher for retake.', 'warning')
    return redirect(url_for('dashboard'))
```

### 5. Update Quiz Submission Route

In `submit_shared_quiz` route:

```python
# For coding questions:
if q.qtype == 'coding':
    code_data = data.get(f'code_{q.id}', '')
    language = data.get(f'language_{q.id}', 'python')
    test_cases = json.loads(q.test_cases_json) if q.test_cases_json else []
    test_results, passed, total = run_test_cases(code_data, language, test_cases)
    gained = float(q.marks or 1) * (passed / total) if total > 0 else 0.0
    is_correct = passed == total
    test_results_json = json.dumps(test_results)
    # ... save to QuizAnswer

# Set review unlock time
from datetime import timedelta
submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
submission.completed = True
```

### 6. Add View Results Route

```python
@app.route('/quiz/result/<int:submission_id>')
@login_required
def view_quiz_result(submission_id):
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id, 
        student_id=current_user.id
    ).first()
    if not submission:
        flash('Result not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if 15 minutes passed
    current_time = datetime.utcnow()
    if submission.review_unlocked_at and submission.review_unlocked_at > current_time:
        flash('Results will be available 15 minutes after submission', 'info')
        return redirect(url_for('dashboard'))
    
    # ... load quiz, questions, answers and render results template
```

### 7. Add Allow Retake Route

```python
@app.route('/teacher/quiz/<code>/allow-retake/<int:submission_id>', methods=['POST'])
@login_required
def allow_student_retake(code, submission_id):
    # Verify teacher owns quiz
    quiz = db.session.query(Quiz).filter_by(
        code=code.upper(), 
        created_by=current_user.id
    ).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete submission and answers
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id, 
        quiz_id=quiz.id
    ).first()
    if submission:
        db.session.query(QuizAnswer).filter_by(submission_id=submission.id).delete()
        db.session.delete(submission)
        db.session.commit()
        flash('Student can now retake the quiz', 'success')
    
    return redirect(url_for('teacher_quiz_results', code=code))
```

### 8. Update Dashboard Template

In `dashboard.html`, add countdown logic:

```html
{% if s.review_unlocked_at %}
    {% set remaining_seconds = (s.review_unlocked_at - current_time).total_seconds() %}
    {% if remaining_seconds > 0 %}
        {% set remaining_mins = (remaining_seconds / 60)|round(0, 'ceil')|int %}
        <small class="text-muted">Available in {{ remaining_mins }} min</small>
    {% else %}
        <a href="{{ url_for('view_quiz_result', submission_id=s.id) }}">View Results</a>
    {% endif %}
{% endif %}
```

---

## 📁 Files That Need Updates:

1. `app.py` - Add functions, routes, models
2. `templates/dashboard.html` - Add countdown display
3. `templates/take_shared_quiz.html` - Add coding question UI
4. `templates/shared_quiz_results.html` - Add results display (create if doesn't exist)
5. `templates/create_quiz_simple.html` - Add question type dropdown

---

## 🎯 Next Steps:

**Please share:**
1. Your working GitHub repository URL, OR
2. Tell me which specific files you want me to update

Then I'll provide the complete updated code!

