# 🚀 Quick Start Guide - Update UNITEST-EXAM Repository

**Target:** https://github.com/theakshatkhandelwal/UNITEST-EXAM.git

## ✅ Features to Add:

1. **15-Minute Review Unlock** ⏰
2. **Coding Integration** 💻
3. **One Attempt Per Student** 🔒
4. **Teacher Allow Retake** 👨‍🏫

---

## 📋 Step-by-Step Instructions:

### STEP 1: Clone Your Working Repository
```bash
git clone https://github.com/theakshatkhandelwal/UNITEST-EXAM.git
cd UNITEST-EXAM
```

### STEP 2: Run Database Migration
1. Copy `migrate_new_features.py` from this repository to your UNITEST-EXAM folder
2. Run: `python migrate_new_features.py`
3. This adds all required database columns

### STEP 3: Update app.py
1. Open `APP_PY_UPDATES.md` (in this repository)
2. Follow the instructions to:
   - Update database models
   - Add code execution functions
   - Update routes
   - Add new routes

### STEP 4: Update Templates
1. Open `TEMPLATE_UPDATES.md` (in this repository)
2. Update your templates as shown

### STEP 5: Test Locally
```bash
python app.py
```
Test each feature:
- Create a quiz with coding questions
- Take quiz (should prevent second attempt)
- Submit quiz (should set 15-min unlock)
- Check dashboard (should show countdown)
- Wait 15 min or manually set `review_unlocked_at` to past time
- View results
- As teacher, allow retake

### STEP 6: Commit and Push
```bash
git add .
git commit -m "Add 15-min review unlock, coding integration, one attempt per student, and teacher allow retake features"
git push
```

---

## 📁 Files You Need:

From this repository, copy these files to your UNITEST-EXAM repo:

1. **`migrate_new_features.py`** - Database migration script
2. **`APP_PY_UPDATES.md`** - All app.py code updates
3. **`TEMPLATE_UPDATES.md`** - All template updates

---

## 🎯 What Each Feature Does:

### 1. 15-Minute Review Unlock
- Students can't see results immediately
- Dashboard shows countdown: "Available in X min"
- After 15 minutes, "View Results" button appears
- Results page shows detailed answers

### 2. Coding Integration
- Teachers can create coding questions
- Students write code in CodeMirror editor
- Code is executed with test cases
- Score based on passed test cases
- Supports Python, Java, C++, C

### 3. One Attempt Per Student
- Students can only take quiz once per code
- Shows "Already attempted" if tried again
- Prevents multiple submissions

### 4. Teacher Allow Retake
- Teacher sees "Allow Retake" button in results
- Clicking it resets student's submission
- Student can take quiz again

---

## ⚠️ Important Notes:

1. **Database Migration:** Run migration FIRST before updating code
2. **Backup:** Make a backup of your working repository before changes
3. **Test Locally:** Test all features locally before deploying
4. **Environment Variables:** Make sure `GOOGLE_AI_API_KEY` is set for coding question generation

---

## 🆘 Need Help?

If you encounter issues:
1. Check that migration ran successfully
2. Verify all model fields are added
3. Check that routes are added correctly
4. Verify templates are updated
5. Check browser console for JavaScript errors

---

## ✅ Checklist:

- [ ] Database migration completed
- [ ] Models updated with new fields
- [ ] Code execution functions added
- [ ] Routes updated/added
- [ ] Templates updated
- [ ] Tested locally
- [ ] Committed and pushed

---

**Good luck! 🚀**

