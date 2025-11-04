# ✅ Pre-Deployment Checklist

## Before Deploying

### 1. Code Preparation
- [x] All features implemented
- [x] Code tested locally
- [x] Dependencies updated
- [x] Environment variables documented

### 2. GitHub Setup
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] `.gitignore` configured (excludes venv, instance, etc.)

### 3. Database Setup
- [ ] NeonDB account created
- [ ] Database project created
- [ ] Connection string copied
- [ ] Database tables will auto-create on first run

### 4. API Keys
- [ ] Google AI API key obtained
- [ ] API key added to environment variables

### 5. Vercel Configuration
- [ ] Vercel account created
- [ ] `vercel.json` configured
- [ ] `requirements_vercel.txt` updated
- [ ] Environment variables ready

### 6. Deployment
- [ ] GitHub repo connected to Vercel
- [ ] Environment variables added in Vercel
- [ ] Initial deployment successful
- [ ] Basic functionality tested

### 7. Post-Deployment
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Monitoring set up
- [ ] Error tracking configured

## Quick Commands

```bash
# 1. Initialize Git (if not done)
git init
git add .
git commit -m "Initial commit"

# 2. Push to GitHub
git remote add origin YOUR_REPO_URL
git branch -M main
git push -u origin main

# 3. Deploy to Vercel (via CLI)
npm i -g vercel
vercel login
vercel
```

## Environment Variables Template

```env
SECRET_KEY=generate-a-random-32-character-secret-key
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
VERCEL=1
```

## Important Notes

⚠️ **EasyOCR**: Not included in Vercel deployment due to size limits. PDF OCR will work locally but may need cloud OCR service for production.

✅ **All other features**: Will work normally on Vercel.

