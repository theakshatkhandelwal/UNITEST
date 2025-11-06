# 🎯 Features to Add to Your Working Version

This document lists all the features that need to be added to your working hosted version.

## ✅ Features to Add:

### 1. **15-Minute Review Unlock** ⏰
- Students can view results only after 15 minutes
- Shows countdown timer on dashboard
- Auto-unlocks after 15 minutes

### 2. **Coding Question Integration** 💻
- Support for coding questions with test cases
- Code execution using Piston API
- Multiple language support (Python, Java, C++, C)
- Test case evaluation
- Starter code templates

### 3. **One Attempt Per Student** 🔒
- Students can only take quiz once per code
- Shows "Already attempted" message if tried again
- Teacher can reset/allow retake

### 4. **Teacher Allow Retake** 👨‍🏫
- Teacher can reset a student's submission
- Allows student to retake the quiz

---

## 📋 Step-by-Step Implementation Guide

### Step 1: Database Schema Updates

Add these columns to your database:

#### `quiz_question` table:
```sql
ALTER TABLE quiz_question ADD COLUMN test_cases_json TEXT;
ALTER TABLE quiz_question ADD COLUMN language_constraints TEXT;
ALTER TABLE quiz_question ADD COLUMN time_limit_seconds INTEGER;
ALTER TABLE quiz_question ADD COLUMN memory_limit_mb INTEGER;
ALTER TABLE quiz_question ADD COLUMN sample_input TEXT;
ALTER TABLE quiz_question ADD COLUMN sample_output TEXT;
ALTER TABLE quiz_question ADD COLUMN starter_code TEXT;
```

#### `quiz_answer` table:
```sql
ALTER TABLE quiz_answer ADD COLUMN code_language VARCHAR(20);
ALTER TABLE quiz_answer ADD COLUMN test_results_json TEXT;
ALTER TABLE quiz_answer ADD COLUMN passed_test_cases INTEGER DEFAULT 0;
ALTER TABLE quiz_answer ADD COLUMN total_test_cases INTEGER DEFAULT 0;
```

#### `quiz_submission` table:
```sql
ALTER TABLE quiz_submission ADD COLUMN review_unlocked_at DATETIME;
ALTER TABLE quiz_submission ADD COLUMN fullscreen_exit_flag BOOLEAN DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN answered_count INTEGER DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN question_count INTEGER DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN is_full_completion BOOLEAN DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN started_at DATETIME;
ALTER TABLE quiz_submission ADD COLUMN completed BOOLEAN DEFAULT 0;
```

---

### Step 2: Code Functions to Add

I'll provide the complete code files in separate documents.

---

## 🚀 Quick Implementation

**Option 1:** I can create a patch file with all changes
**Option 2:** I can provide the complete updated files
**Option 3:** I can create a migration script

**Which option do you prefer?**

Also, please share:
1. Your working GitHub repository URL
2. Or tell me which files you want updated

Then I'll provide the exact code changes needed!

