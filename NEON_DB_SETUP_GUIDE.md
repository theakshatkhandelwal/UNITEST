# 🗄️ NeonDB Setup Guide

## ✅ Do You Need to Manually Update NeonDB?

**NO - The app will automatically create tables!**

### How It Works:

1. **Automatic Table Creation:**
   - When you visit `/init-db` on your deployed app, it automatically creates all required tables
   - No manual SQL needed!

2. **What Happens:**
   - App connects to your NeonDB database (using `DATABASE_URL`)
   - Calls `db.create_all()` which creates all tables from your models
   - Tables are created automatically based on your SQLAlchemy models

### Steps:

1. **Set `DATABASE_URL` in Vercel:**
   - Go to Vercel → Settings → Environment Variables
   - Add `DATABASE_URL` with your NeonDB connection string
   - Format: `postgresql://user:pass@host/db?sslmode=require`

2. **After Deployment:**
   - Visit: `https://your-app.vercel.app/init-db`
   - This will automatically create all tables

3. **That's It!**
   - No manual SQL needed
   - No manual table creation
   - Everything is automatic!

### What Tables Are Created:

The app automatically creates:
- `user` - User accounts
- `progress` - Learning progress
- `quiz` - Quizzes
- `quiz_question` - Quiz questions
- `quiz_submission` - Quiz submissions
- `quiz_answer` - Quiz answers

All with proper relationships and constraints!

### If You Want to Check:

After visiting `/init-db`, you can check in NeonDB SQL Editor:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

This will show all created tables.

## 🎯 Summary:

**You don't need to manually update NeonDB!** Just:
1. Set `DATABASE_URL` in Vercel
2. Visit `/init-db` after deployment
3. Done! ✅

