# 🔧 Vercel Runtime Error Fix Guide

## Current Issue:
✅ **Build Succeeded** (21s)
❌ **Runtime Error**: "Serverless Function has crashed" - 500 Internal Server Error
❌ **Error Code**: FUNCTION_INVOCATION_FAILED

## Common Causes & Fixes:

### 1. Missing Environment Variables (MOST LIKELY)
**Check if these are set in Vercel:**
- `SECRET_KEY` - Required for Flask sessions
- `GOOGLE_AI_API_KEY` - Required for AI features
- `DATABASE_URL` - Required for database connection

**Fix:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add all 3 variables for Production, Preview, and Development
3. Redeploy

### 2. Database Connection Issue
**If DATABASE_URL is missing or incorrect:**
- App tries to use SQLite (which doesn't work on Vercel)
- PostgreSQL connection fails

**Fix:**
- Set `DATABASE_URL` to your NeonDB connection string
- Format: `postgresql://user:pass@host/db?sslmode=require`

### 3. Import Errors
**If a module is missing:**
- Check Vercel build logs for import errors
- Verify all packages in requirements.txt are installed

### 4. Template/Static File Path Issues
**If templates or static files aren't found:**
- Check if templates/ and static/ folders are in the repo
- Verify Flask app paths are correct

## 🔍 How to Debug:

1. **Check Vercel Function Logs:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on the failed deployment
   - Click "Functions" tab
   - Check the logs for the specific error

2. **Check Build Logs:**
   - Look for any warnings or errors during build
   - Check if all packages installed correctly

3. **Test Locally:**
   - Set environment variables locally
   - Run the app and check for errors

## 🚀 Quick Fix Steps:

1. **Verify Environment Variables:**
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_AI_API_KEY=AIzaSyBKYJLje8mR0VP5XxmrpG3PfXAleNXU_-c
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   ```

2. **Check Vercel Logs:**
   - Go to deployment → Functions → Logs
   - Look for the actual error message

3. **Redeploy:**
   - After fixing environment variables
   - Trigger a new deployment

## Most Likely Issue:
**Missing `DATABASE_URL` environment variable** - The app is trying to connect to a database that doesn't exist.

