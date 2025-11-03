# 🚀 Neon DB + Vercel Deployment Guide for Unitest

Complete step-by-step guide to deploy Unitest AI Learning Platform using **Neon DB** (PostgreSQL) and **Vercel** (serverless hosting).

## 📋 Prerequisites

- ✅ GitHub account (already done - your repo is at https://github.com/theakshatkhandelwal/UNITEST)
- ✅ Google AI API key (for Gemini AI)
- ⏳ Neon DB account (free tier available)
- ⏳ Vercel account (free tier available)

---

## 🗄️ PART 1: Set Up Neon Database

### Step 1.1: Create Neon Account & Project

1. Go to **[Neon.tech](https://neon.tech/)** and sign up (free tier available)
2. Click **"Create Project"**
3. Choose:
   - **Project Name**: `unitest` (or any name)
   - **Region**: Choose closest to your users (e.g., `US East`)
   - **PostgreSQL Version**: `15` or `16` (recommended)
4. Click **"Create Project"**

### Step 1.2: Get Connection String

1. In your Neon dashboard, go to your project
2. Click on **"Connection Details"** or **"Connection String"**
3. You'll see a connection string like:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Copy this connection string** - you'll need it in Vercel

### Step 1.3: Test Connection (Optional)

You can test the connection using any PostgreSQL client or Python:
```python
import psycopg2
conn = psycopg2.connect("your-neon-connection-string")
print("Connected successfully!")
```

---

## 🚀 PART 2: Deploy to Vercel

### Step 2.1: Connect GitHub to Vercel

1. Go to **[Vercel.com](https://vercel.com/)** and sign up/login
2. Click **"Add New Project"**
3. **Import Git Repository**:
   - Select **"Import Git Repository"**
   - Choose **GitHub** and authorize
   - Select your repository: `theakshatkhandelwal/UNITEST`
   - Click **"Import"**

### Step 2.2: Configure Project Settings

1. **Project Name**: `unitest` (or your preferred name)
2. **Framework Preset**: Select **"Other"** (we're using Flask)
3. **Root Directory**: `./` (leave as default)
4. **Build Command**: Leave empty (no build needed)
5. **Output Directory**: Leave empty

### Step 2.3: Add Environment Variables

**⚠️ CRITICAL**: Add these environment variables in Vercel before deploying:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `SECRET_KEY` | `your-super-secret-random-key-here` | Flask secret key (generate a random string) |
| `GOOGLE_AI_API_KEY` | `your-google-ai-api-key` | Your Google Gemini API key |
| `DATABASE_URL` | `your-neon-connection-string` | Neon PostgreSQL connection string |

**How to add:**
1. In Vercel project settings, go to **"Environment Variables"**
2. Click **"Add"** for each variable
3. Set for all environments: **Production, Preview, Development**
4. **Important**: Make sure `DATABASE_URL` uses `postgresql://` (not `postgres://`)

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

Or use online tool: https://randomkeygen.com/

### Step 2.4: Deploy

1. Click **"Deploy"** button
2. Wait for deployment (usually 2-5 minutes)
3. Your app will be live at: `https://your-project-name.vercel.app`

---

## ✅ PART 3: Initialize Database Tables

### Option A: Automatic (Recommended)

The app will automatically create tables on first request. Just visit:
- `https://your-project-name.vercel.app/init-db`

Or visit the homepage and it will auto-initialize.

### Option B: Manual (SQL Script)

If you prefer manual setup, run this SQL in Neon SQL Editor:

```sql
-- Create Users table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Progress table
CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    bloom_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Quiz tables
CREATE TABLE IF NOT EXISTS quiz (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    created_by INTEGER REFERENCES "user"(id) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'beginner',
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_question (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quiz(id) NOT NULL,
    question TEXT NOT NULL,
    options_json TEXT,
    answer VARCHAR(10),
    qtype VARCHAR(20) DEFAULT 'mcq',
    marks INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS quiz_submission (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quiz(id) NOT NULL,
    student_id INTEGER REFERENCES "user"(id) NOT NULL,
    score FLOAT DEFAULT 0.0,
    total FLOAT DEFAULT 0.0,
    percentage FLOAT DEFAULT 0.0,
    passed BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_unlocked_at TIMESTAMP,
    fullscreen_exit_flag BOOLEAN DEFAULT FALSE,
    answered_count INTEGER DEFAULT 0,
    question_count INTEGER DEFAULT 0,
    is_full_completion BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS quiz_answer (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES quiz_submission(id) NOT NULL,
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN,
    ai_score FLOAT,
    scored_marks FLOAT DEFAULT 0.0
);
```

---

## 🧪 PART 4: Test Your Deployment

### 4.1: Basic Tests

1. **Homepage**: Visit `https://your-project-name.vercel.app`
2. **Health Check**: Visit `https://your-project-name.vercel.app/health`
3. **Database Check**: Visit `https://your-project-name.vercel.app/debug`
4. **Sign Up**: Create a test account
5. **Create Quiz**: Test quiz creation functionality

### 4.2: Database Connection Test

Check the `/health` endpoint - it should show:
```json
{
  "status": "OK",
  "database": "OK",
  "dependencies": {...},
  "environment": {
    "has_database_url": true,
    ...
  }
}
```

---

## 🔧 PART 5: Troubleshooting

### Issue: Database Connection Failed

**Symptoms**: Error like "could not connect to server" or "connection refused"

**Solutions**:
1. ✅ Verify `DATABASE_URL` is correct in Vercel
2. ✅ Ensure connection string uses `postgresql://` (not `postgres://`)
3. ✅ Check Neon project is active (not paused)
4. ✅ Verify connection string includes `?sslmode=require`

### Issue: Tables Not Created

**Solutions**:
1. Visit `/init-db` endpoint
2. Check Vercel function logs for errors
3. Verify database permissions in Neon

### Issue: Build/Deployment Fails

**Solutions**:
1. Check `requirements.txt` includes all dependencies
2. Verify Python version compatibility
3. Check Vercel build logs for specific errors
4. Ensure `vercel.json` is correct

### Issue: Function Timeout

**Solutions**:
1. Increase `maxDuration` in `vercel.json` (currently 60s)
2. Optimize slow queries
3. Use connection pooling (already configured)

---

## 📊 PART 6: Monitoring & Maintenance

### Vercel Dashboard

- **Deployments**: Monitor each deployment
- **Analytics**: Track performance
- **Logs**: View function execution logs
- **Function Logs**: Real-time error tracking

### Neon Dashboard

- **Database Usage**: Monitor storage and compute
- **Connection Pooling**: Automatic with Neon
- **Backups**: Automatic daily backups
- **Query Performance**: Monitor slow queries

### Google Search Console

1. Submit your site: `https://your-domain.com`
2. Submit sitemap: `https://your-domain.com/sitemap.xml`
3. Monitor search performance

---

## 🎯 PART 7: SEO Optimization (Already Done!)

Your app already includes:
- ✅ SEO-optimized meta tags
- ✅ "Unitest" keyword targeting
- ✅ Structured data (JSON-LD)
- ✅ Sitemap.xml
- ✅ Robots.txt
- ✅ Open Graph tags
- ✅ Mobile-responsive design

**Next Steps:**
1. Submit to Google Search Console
2. Add custom domain (optional)
3. Build backlinks
4. Share on social media

---

## 📝 Environment Variables Summary

Make sure these are set in Vercel:

```env
SECRET_KEY=your-super-secret-key-here
GOOGLE_AI_API_KEY=your-google-ai-api-key
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
FLASK_ENV=production
```

---

## 🚀 Quick Deploy Checklist

- [ ] Created Neon DB account and project
- [ ] Copied Neon connection string
- [ ] Created Vercel account
- [ ] Connected GitHub repository
- [ ] Added all environment variables in Vercel
- [ ] Deployed project
- [ ] Initialized database tables
- [ ] Tested all functionality
- [ ] Submitted to Google Search Console

---

## 🎉 Success!

Your Unitest platform is now live with:
- ✅ Neon PostgreSQL database (serverless, scalable)
- ✅ Vercel hosting (global CDN, fast)
- ✅ SEO optimization for "unitest" keyword
- ✅ Automatic scaling
- ✅ Free tier available for both services

**Your Live URL**: `https://your-project-name.vercel.app`

---

## 📞 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Flask + Vercel**: Check Vercel Flask examples
- **GitHub Issues**: Open issue in your repository

---

**Last Updated**: 2025-01-21

