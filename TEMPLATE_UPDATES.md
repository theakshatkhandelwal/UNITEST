# 🎨 Template Updates for UNITEST-EXAM Repository

This file contains all template updates needed for the new features.

---

## 1. UPDATE `templates/dashboard.html`

### Find the "Your Shared Quiz History" section and update it:

**REPLACE** the results display section with:

```html
<td>
    {% if s.review_unlocked_at %}
        {% set remaining_seconds = (s.review_unlocked_at - current_time).total_seconds() %}
        {% if remaining_seconds > 0 %}
            {% set remaining_mins = (remaining_seconds / 60)|round(0, 'ceil')|int %}
            <small class="text-muted">Available in {{ remaining_mins }} min</small>
        {% else %}
            <a class="btn btn-sm btn-outline-primary" href="{{ url_for('view_quiz_result', submission_id=s.id) }}">
                <i class="fas fa-eye me-1"></i>View Results
            </a>
        {% endif %}
    {% else %}
        <small class="text-muted">Available after 15 min</small>
    {% endif %}
</td>
```

**IMPORTANT:** Make sure your `dashboard` route passes `current_time` to the template:
```python
current_time = datetime.utcnow()
return render_template('dashboard.html', current_time=current_time, ...)
```

---

## 2. UPDATE `templates/create_quiz_simple.html`

### Add Question Type dropdown:

Find where you have difficulty/num_questions fields and **ADD** this:

```html
<div class="mb-3">
    <label class="form-label">Question Type</label>
    <select class="form-select" name="question_type" id="question_type" required>
        <option value="mcq" selected>Multiple Choice (MCQ)</option>
        <option value="subjective">Subjective</option>
        <option value="coding">Coding Problems</option>
    </select>
    <div class="form-text">Select coding problems to create programming questions with test cases.</div>
</div>
```

---

## 3. CREATE `templates/shared_quiz_results.html`

Create this new file in your `templates/` folder:

```html
{% extends "base.html" %}

{% block title %}Quiz Results - {{ quiz.title }}{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <!-- Results Header -->
            <div class="card mb-4">
                <div class="card-header text-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <h2 class="mb-2">
                        <i class="fas fa-trophy me-2"></i>Quiz Results
                    </h2>
                    <h4 class="mb-0">{{ quiz.title }}</h4>
                    <small class="text-white-50">Submitted: {{ submission.submitted_at.strftime('%Y-%m-%d %H:%M') }}</small>
                </div>
            </div>

            <!-- Score Summary -->
            <div class="card mb-4">
                <div class="card-body text-center">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="border-end">
                                <h3 class="text-primary fw-bold">{{ final_score }}</h3>
                                <p class="text-muted mb-0">Final Score</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="border-end">
                                <h3 class="text-{% if passed %}success{% else %}danger{% endif %} fw-bold">{{ "%.1f"|format(percentage) }}%</h3>
                                <p class="text-muted mb-0">Percentage</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h3 class="text-{% if passed %}success{% else %}warning{% endif %} fw-bold">
                                {% if passed %}
                                    <i class="fas fa-check-circle me-2"></i>PASSED
                                {% else %}
                                    <i class="fas fa-times-circle me-2"></i>NOT PASSED
                                {% endif %}
                            </h3>
                            <p class="text-muted mb-0">Result</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Detailed Results -->
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">
                        <i class="fas fa-list-alt me-2"></i>Question-by-Question Analysis
                    </h4>
                </div>
                <div class="card-body">
                    {% for result in results %}
                        <div class="border-bottom pb-4 mb-4">
                            <h5 class="fw-bold mb-3">
                                <span class="badge bg-primary me-2">Q{{ loop.index }}</span>
                                {{ result.question }}
                                <span class="badge bg-secondary ms-2">{{ result.marks }} marks</span>
                            </h5>

                            {% if result.type == 'mcq' %}
                                <!-- MCQ Result -->
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-2">
                                            <strong>Your Answer:</strong>
                                            <span class="ms-2 {% if result.is_correct %}text-success{% else %}text-danger{% endif %}">
                                                {{ result.user_answer }}
                                            </span>
                                        </div>
                                        {% if not result.is_correct %}
                                            <div class="mb-2">
                                                <strong>Correct Answer:</strong>
                                                <span class="ms-2 text-success">{{ result.correct_answer }}</span>
                                            </div>
                                        {% endif %}
                                    </div>
                                    <div class="col-md-6 text-md-end">
                                        <span class="badge {% if result.is_correct %}bg-success{% else %}bg-danger{% endif %} fs-6">
                                            {% if result.is_correct %}
                                                <i class="fas fa-check me-1"></i>Correct
                                            {% else %}
                                                <i class="fas fa-times me-1"></i>Incorrect
                                            {% endif %}
                                        </span>
                                    </div>
                                </div>
                            {% elif result.type == 'subjective' %}
                                <!-- Subjective Result -->
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="mb-2">
                                            <strong>Your Answer:</strong>
                                            <div class="mt-2 p-3 bg-light rounded">
                                                {{ result.user_answer }}
                                            </div>
                                        </div>
                                        <div class="mb-2">
                                            <strong>Sample Answer:</strong>
                                            <div class="mt-2 p-3 bg-light rounded">
                                                {{ result.sample_answer }}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 text-md-end">
                                        <div class="text-center">
                                            <div class="mb-2">
                                                <span class="badge bg-info fs-6">{{ result.marks }} marks</span>
                                            </div>
                                            <div class="mb-2">
                                                <strong>AI Score:</strong><br>
                                                <span class="text-primary fw-bold">{{ "%.1f"|format(result.scored_marks) }}/{{ result.marks }}</span>
                                            </div>
                                            <div>
                                                <small class="text-muted">({{ "%.0f"|format(result.ai_score * 100) }}%)</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            {% elif result.type == 'coding' %}
                                <!-- Coding Result -->
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="mb-2">
                                            <strong>Language Used:</strong>
                                            <span class="badge bg-secondary ms-2">{{ result.code_language|upper }}</span>
                                        </div>
                                        <div class="mb-2">
                                            <strong>Your Code:</strong>
                                            <pre class="mt-2 p-3 bg-dark text-light rounded" style="max-height: 300px; overflow-y: auto;"><code>{{ result.user_answer }}</code></pre>
                                        </div>
                                        {% if result.sample_input %}
                                            <div class="mb-2">
                                                <strong>Sample Input:</strong>
                                                <pre class="mt-2 p-2 bg-light rounded">{{ result.sample_input }}</pre>
                                            </div>
                                        {% endif %}
                                        {% if result.sample_output %}
                                            <div class="mb-2">
                                                <strong>Sample Output:</strong>
                                                <pre class="mt-2 p-2 bg-light rounded">{{ result.sample_output }}</pre>
                                            </div>
                                        {% endif %}
                                    </div>
                                    <div class="col-md-4 text-md-end">
                                        <div class="text-center">
                                            <div class="mb-2">
                                                <span class="badge bg-info fs-6">{{ result.marks }} marks</span>
                                            </div>
                                            <div class="mb-2">
                                                <strong>Test Cases:</strong><br>
                                                <span class="text-primary fw-bold">{{ result.passed_test_cases }}/{{ result.total_test_cases }}</span>
                                            </div>
                                            <div class="mb-2">
                                                <strong>Score:</strong><br>
                                                <span class="text-primary fw-bold">{{ "%.1f"|format(result.scored_marks) }}/{{ result.marks }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {% if result.test_results %}
                                    <div class="mt-3">
                                        <strong>Test Case Results:</strong>
                                        <div class="mt-2">
                                            {% for test_result in result.test_results %}
                                                <div class="mb-2 p-2 rounded {% if test_result.is_correct %}bg-success bg-opacity-10{% else %}bg-danger bg-opacity-10{% endif %}">
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span>
                                                            <i class="fas fa-{% if test_result.is_correct %}check{% else %}times{% endif %} me-2"></i>
                                                            Test Case {{ loop.index }}
                                                            {% if test_result.is_hidden %}
                                                                <span class="badge bg-secondary ms-2">Hidden</span>
                                                            {% endif %}
                                                        </span>
                                                        <span class="badge {% if test_result.is_correct %}bg-success{% else %}bg-danger{% endif %}">
                                                            {% if test_result.is_correct %}Passed{% else %}Failed{% endif %}
                                                        </span>
                                                    </div>
                                                    {% if not test_result.is_hidden %}
                                                        <div class="mt-2 small">
                                                            <strong>Input:</strong> <code>{{ test_result.input[:100] }}</code><br>
                                                            <strong>Expected:</strong> <code>{{ test_result.expected_output }}</code>
                                                            {% if test_result.actual_output %}
                                                                <br><strong>Your Output:</strong> <code>{{ test_result.actual_output }}</code>
                                                            {% endif %}
                                                        </div>
                                                    {% endif %}
                                                </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                {% endif %}
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="text-center mt-4">
                <a href="{{ url_for('dashboard') }}" class="btn btn-primary btn-lg">
                    <i class="fas fa-tachometer-alt me-2"></i>Back to Dashboard
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 4. UPDATE `templates/take_shared_quiz.html`

Your template should already support coding questions if it has CodeMirror. Make sure it:
- Has language selection dropdown
- Has CodeMirror editor for code input
- Has "Run Test Cases" button
- Sends code data as `code_{question_id}` and language as `language_{question_id}`

If it doesn't have coding support, you'll need to add a coding question section similar to the MCQ/subjective sections.

---

## 5. UPDATE `templates/teacher_results.html`

Make sure it has the "Allow Retake" button (it should already be there based on the code):

```html
{% if s.completed %}
  <form method="POST" action="{{ url_for('allow_student_retake', code=quiz.code, submission_id=s.id) }}" 
        style="display: inline;" 
        onsubmit="return confirm('Are you sure you want to allow this student to retake the quiz? This will reset their submission.');">
    <button type="submit" class="btn btn-sm btn-warning" title="Allow student to retake the quiz">
      <i class="fas fa-redo me-1"></i>Allow Retake
    </button>
  </form>
{% endif %}
```

---

## ✅ Summary

After updating all templates:
1. ✅ Dashboard shows countdown timer
2. ✅ Create quiz has question type dropdown
3. ✅ Results page shows coding question details
4. ✅ Teacher can allow retake

---

## 🚀 Next Steps

1. Update `dashboard.html` - Add countdown display
2. Update `create_quiz_simple.html` - Add question type dropdown
3. Create `shared_quiz_results.html` - New results template
4. Test all features!

