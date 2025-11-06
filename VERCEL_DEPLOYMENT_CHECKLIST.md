# ✅ Vercel Deployment Checklist

## Pre-Deployment Verification

### ✅ Code Changes Made
- [x] Created `requirements_vercel.txt` (optimized, ~15-20MB)
- [x] Made pandas optional (CSV uses built-in csv module)
- [x] Updated code to handle missing dependencies gracefully
- [x] Fixed duplicate imports
- [x] Flask app configured with `instance_relative_config=False` (Vercel-compatible)

### ⚠️ Potential Issues to Check

#### 1. Environment Variables (CRITICAL)
Before deploying, ensure these are set in Vercel dashboard:
- [ ] `SECRET_KEY` - Random secret key (32+ characters)
- [ ] `GOOGLE_AI_API_KEY` - Your Google AI API key
- [ ] `DATABASE_URL` - PostgreSQL connection string (NeonDB)

**How to set:**
1. Go to Vercel project → Settings → Environment Variables
2. Add each variable for Production, Preview, and Development
3. Make sure `DATABASE_URL` uses `postgresql://` (not `postgres://`)

#### 2. Database Initialization
- [x] `init_database()` function exists
- [x] Auto-initializes on first request
- [ ] **Action Required**: Visit `/init-db` after first deployment to create tables

#### 3. File System Operations
- [x] No SQLite file writes (uses PostgreSQL on Vercel)
- [x] PDF uploads handled via temporary files (should work)
- [ ] **Note**: File uploads may have size limits on Vercel

#### 4. Static Files & Templates
- [x] `vercel.json` routes static files correctly
- [x] Templates folder should be accessible
- [ ] **Verify**: Check if templates/static folders are in repo

#### 5. Dependencies
- [x] `requirements_vercel.txt` excludes heavy packages
- [x] All optional dependencies handled gracefully
- [ ] **Action Required**: Use `requirements_vercel.txt` as `requirements.txt` for deployment

## 🚀 Deployment Steps

### Step 1: Prepare Requirements
```powershell
# Backup original
Copy-Item requirements.txt requirements_full.txt

# Use optimized version
Copy-Item requirements_vercel.txt requirements.txt
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push
```

### Step 3: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. **IMPORTANT**: Set environment variables BEFORE deploying
4. Click "Deploy"

### Step 4: Initialize Database
After deployment, visit:
```
https://your-app.vercel.app/init-db
```

Or just visit the homepage - it will auto-initialize.

### Step 5: Verify
1. Visit your app URL
2. Check `/health` endpoint for system status
3. Test login/signup
4. Test quiz creation

## 🔍 Post-Deployment Checks

### Test These Features:
- [ ] Homepage loads
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard loads
- [ ] Quiz creation works
- [ ] Quiz taking works
- [ ] Coding questions work
- [ ] CSV export works
- [ ] Text PDF upload works

### Expected Limitations:
- ⚠️ Image PDF processing will show error (EasyOCR excluded)
- ⚠️ XLSX export redirects to CSV (pandas excluded)

## 🐛 Common Issues & Fixes

### Issue: "Module not found"
**Fix**: Make sure `requirements_vercel.txt` is used as `requirements.txt`

### Issue: "Database connection failed"
**Fix**: 
1. Check `DATABASE_URL` is set correctly
2. Ensure it uses `postgresql://` not `postgres://`
3. Check NeonDB connection string includes `?sslmode=require`

### Issue: "Secret key not set"
**Fix**: Add `SECRET_KEY` environment variable in Vercel

### Issue: "Templates not found"
**Fix**: Ensure `templates/` folder is in repository root

### Issue: "Static files not loading"
**Fix**: Check `vercel.json` routes static files correctly

## ✅ Final Checklist

Before going live:
- [ ] All environment variables set
- [ ] Database initialized (`/init-db` visited)
- [ ] Homepage loads correctly
- [ ] User can register/login
- [ ] Quiz features work
- [ ] No critical errors in Vercel logs

## 📊 Size Verification

Expected deployment size: **~15-20MB** ✅
- Flask & extensions: ~5MB
- Google AI: ~2MB
- PostgreSQL driver: ~3MB
- Other dependencies: ~5-10MB

**Total: Under 50MB limit!** ✅

