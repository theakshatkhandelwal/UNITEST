# 📝 app.py Updates for UNITEST-EXAM Repository

This file contains all the code you need to add/update in your `app.py` file.

---

## 1. UPDATE DATABASE MODELS

### QuizQuestion Model - Add these fields:
```python
class QuizQuestion(db.Model):
    # ... your existing fields ...
    
    # ADD THESE:
    test_cases_json = db.Column(db.Text)  # JSON array of test cases
    language_constraints = db.Column(db.Text)  # JSON array: ["python", "java", "cpp", "c"]
    time_limit_seconds = db.Column(db.Integer)
    memory_limit_mb = db.Column(db.Integer)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    starter_code = db.Column(db.Text)  # JSON object with starter code per language
```

### QuizAnswer Model - Add these fields:
```python
class QuizAnswer(db.Model):
    # ... your existing fields ...
    
    # ADD THESE:
    code_language = db.Column(db.String(20))  # Language used: python, java, cpp, c
    test_results_json = db.Column(db.Text)  # JSON array of test case results
    passed_test_cases = db.Column(db.Integer, default=0)
    total_test_cases = db.Column(db.Integer, default=0)
```

### QuizSubmission Model - Add these fields:
```python
class QuizSubmission(db.Model):
    # ... your existing fields ...
    
    # ADD THESE:
    review_unlocked_at = db.Column(db.DateTime)  # unlock review after 15 minutes
    fullscreen_exit_flag = db.Column(db.Boolean, default=False)
    answered_count = db.Column(db.Integer, default=0)
    question_count = db.Column(db.Integer, default=0)
    is_full_completion = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
```

---

## 2. ADD CODE EXECUTION FUNCTIONS

Add these functions after your existing helper functions (before routes):

```python
def execute_code(code, language, test_input, time_limit=2, memory_limit=256):
    """Execute code using Piston API (free, no API key needed)"""
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
                        'output': run_result.get('stdout', '').strip(),
                        'stderr': run_result.get('stderr', '').strip()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Runtime Error',
                        'output': run_result.get('stdout', '').strip(),
                        'stderr': run_result.get('stderr', '').strip() or run_result.get('stdout', '')
                    }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Network error: {str(e)}',
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
            'input': test_input,
            'expected_output': expected_output,
            'actual_output': actual_output,
            'is_correct': is_correct,
            'is_hidden': is_hidden
        })
    
    total = len(test_cases)
    percentage = (passed / total * 100) if total > 0 else 0
    
    return {
        'results': results,
        'passed': passed,
        'total': total,
        'percentage': percentage
    }
```

---

## 3. UPDATE ROUTES

### 3.1 Update `dashboard` route:

Add `current_time` to template context:

```python
@app.route('/dashboard')
@login_required
def dashboard():
    # ... your existing code ...
    current_time = datetime.utcnow()  # ADD THIS LINE
    return render_template('dashboard.html', 
                          current_time=current_time,  # ADD THIS
                          # ... your other variables ...
                          )
```

### 3.2 Update `take_shared_quiz` route:

Add one-attempt check and coding question parsing:

```python
@app.route('/quiz/take/<code>')
@login_required
def take_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # ✅ FEATURE: Check if student has already completed this quiz
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    
    # ... your existing code to load questions ...
    
    # ADD: Parse coding question data
    for q in q_rows:
        question_data = {
            'id': q.id,
            'question': q.question,
            'qtype': q.qtype,
            'marks': q.marks,
            'options': json.loads(q.options_json) if q.options_json else [],
        }
        
        # ✅ FEATURE: Add coding question data
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
    
    # Ensure a started submission exists
    existing = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=False
    ).first()
    if not existing:
        existing = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id, question_count=len(q_rows))
        db.session.add(existing)
        db.session.commit()
    
    return render_template('take_shared_quiz.html', quiz=quiz, questions=parsed_questions)
```

### 3.3 Update `submit_shared_quiz` route:

Add coding question handling and 15-minute unlock:

```python
@app.route('/quiz/submit/<code>', methods=['POST'])
@login_required
def submit_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # ✅ FEATURE: Check if already completed
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    
    # Get or create submission
    from datetime import timedelta
    submission = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=False
    ).first()
    if not submission:
        submission = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id)
        db.session.add(submission)
        db.session.flush()
    
    total_marks = 0.0
    scored_marks = 0.0
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
            # ✅ FEATURE: Handle coding questions
            code_data = request.form.get(f'code_{q.id}', '').strip()
            language = request.form.get(f'language_{q.id}', 'python')
            
            if code_data:
                try:
                    test_cases = json.loads(q.test_cases_json) if q.test_cases_json else []
                    time_limit = q.time_limit_seconds or 2
                    memory_limit = q.memory_limit_mb or 256
                    
                    test_results = run_test_cases(code_data, language, test_cases, time_limit, memory_limit)
                    
                    passed_test_cases = test_results['passed']
                    total_test_cases = test_results['total']
                    percentage_passed = test_results['percentage'] / 100.0
                    
                    gained = float(q.marks or 1) * percentage_passed
                    is_correct = percentage_passed == 1.0
                    code_language = language
                    test_results_json = json.dumps(test_results['results'])
                    user_ans = code_data
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
    # ✅ FEATURE: Set 15-minute review unlock
    submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
    submission.fullscreen_exit_flag = request.form.get('fullscreen_exit') == 'true'
    submission.answered_count = answered_count
    submission.question_count = len(questions)
    submission.is_full_completion = (answered_count == len(questions)) and (not submission.fullscreen_exit_flag)
    submission.completed = True
    db.session.commit()
    
    flash(f'Submitted. Score: {scored_marks:.1f}/{total_marks} ({percentage:.0f}%).', 'success')
    return redirect(url_for('dashboard'))
```

### 3.4 Add `view_quiz_result` route (NEW):

```python
# ✅ FEATURE: Student view quiz result (after 15 minutes)
@app.route('/quiz/result/<int:submission_id>')
@login_required
def view_quiz_result(submission_id):
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id, 
        student_id=current_user.id
    ).first()
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('dashboard'))
    
    # ✅ FEATURE: Check if 15 minutes have passed
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
    
    answer_map = {ans.question_id: ans for ans in answers}
    
    # Format results for template
    results = []
    for q in questions:
        ans = answer_map.get(q.id)
        if q.qtype == 'mcq':
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
```

### 3.5 Add `allow_student_retake` route (NEW):

```python
# ✅ FEATURE: Teacher allow student to retake quiz
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
    
    # Get submission
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id, 
        quiz_id=quiz.id
    ).first()
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('teacher_quiz_results', code=code))
    
    # Get student name
    student = db.session.query(User).filter_by(id=submission.student_id).first()
    student_name = student.username if student else f"Student {submission.student_id}"
    
    # Delete all answers
    db.session.query(QuizAnswer).filter_by(submission_id=submission.id).delete()
    
    # Delete submission
    db.session.delete(submission)
    db.session.commit()
    
    flash(f'Successfully allowed {student_name} to retake the quiz. Their previous submission has been reset.', 'success')
    return redirect(url_for('teacher_quiz_results', code=code))
```

### 3.6 Add API endpoints for code testing:

```python
@app.route('/api/test_code', methods=['POST'])
@login_required
def test_code():
    """Test code execution for coding questions"""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    test_input = data.get('test_input', '')
    time_limit = data.get('time_limit', 2)
    memory_limit = data.get('memory_limit', 256)
    
    result = execute_code(code, language, test_input, time_limit, memory_limit)
    return jsonify(result)

@app.route('/api/run_test_cases', methods=['POST'])
@login_required
def api_run_test_cases():
    """Run test cases for coding questions"""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    test_cases = data.get('test_cases', [])
    time_limit = data.get('time_limit', 2)
    memory_limit = data.get('memory_limit', 256)
    
    result = run_test_cases(code, language, test_cases, time_limit, memory_limit)
    return jsonify(result)
```

---

## 4. UPDATE QUIZ GENERATION

Update your `generate_quiz` function to support coding questions. When `question_type == "coding"`, use a prompt that generates coding problems with test cases, starter code, etc.

---

## ✅ That's it!

After adding all this code, your app will have:
1. ✅ 15-minute review unlock
2. ✅ Coding integration
3. ✅ One attempt per student
4. ✅ Teacher allow retake

