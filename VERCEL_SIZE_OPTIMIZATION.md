# 🚀 Vercel Deployment - Size Optimization Guide

## Problem
Vercel has a **50MB limit** for serverless functions. Your app includes heavy dependencies:
- EasyOCR: ~500MB (OCR models)
- PyMuPDF: ~50MB
- pandas: ~30MB
- pytesseract, pdf2image, Pillow: Additional size

**Total size exceeds Vercel's limit!**

## ✅ Solution: Optimized Requirements

I've created `requirements_vercel.txt` that **excludes heavy packages** while keeping all core features working.

### What's Included (Lightweight)
- ✅ Flask & Flask extensions (~5MB)
- ✅ Google Generative AI (~2MB)
- ✅ PostgreSQL driver (~3MB)
- ✅ PyPDF2 (text PDFs only, ~1MB)
- ✅ NLTK (~2MB, downloads data at runtime)
- ✅ requests (for external APIs)

**Total: ~15-20MB** ✅ Under Vercel's limit!

### What's Excluded (Too Large)
- ❌ EasyOCR (~500MB models)
- ❌ PyMuPDF (~50MB)
- ❌ pandas (~30MB)
- ❌ openpyxl (only for XLSX export)
- ❌ pytesseract (requires system binaries)
- ❌ pdf2image (requires Poppler)
- ❌ Pillow (only for advanced image processing)

## 🎯 Features Status

### ✅ Fully Working
- **All Quiz Features**: MCQ, Subjective, Coding Questions
- **Code Execution**: Uses external APIs (Piston/Judge0)
- **User Authentication**: Login, Signup, Dashboard
- **Text-based PDF Processing**: Using PyPDF2
- **CSV Export**: Using built-in `csv` module
- **All Coding Features**: Code editor, test cases, evaluation

### ⚠️ Limited Features
- **Image-based PDF Processing**: Will show error message (EasyOCR not available)
- **XLSX Export**: Will redirect to CSV export (pandas not available)

## 📝 Deployment Steps

### Option 1: Temporary Rename (Recommended)
1. **Before deploying to Vercel:**
   ```bash
   # Backup original requirements.txt
   git stash
   # Or create a backup
   cp requirements.txt requirements_full.txt
   
   # Use optimized version
   cp requirements_vercel.txt requirements.txt
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

3. **After deployment (optional):**
   ```bash
   # Restore original for local development
   git stash pop
   # Or restore from backup
   cp requirements_full.txt requirements.txt
   ```

### Option 2: Use Build Script
Create a `build.sh` script (but Vercel Python builder doesn't support custom build scripts easily).

### Option 3: Keep Two Versions
- Use `requirements_vercel.txt` for Vercel deployments
- Use `requirements.txt` for local development

## 🔧 Code Changes Made

The code now handles missing dependencies gracefully:

1. **Pandas**: Made optional, CSV export uses built-in `csv` module
2. **XLSX Export**: Shows error and redirects to CSV if pandas unavailable
3. **PDF Processing**: Already had conditional imports, will show error for image PDFs

## ✅ Verification

After deployment, verify:
1. ✅ Quiz creation works
2. ✅ Quiz taking works
3. ✅ Coding questions work
4. ✅ CSV export works
5. ⚠️ Image PDF upload shows helpful error
6. ⚠️ XLSX export redirects to CSV

## 📊 Size Comparison

| Package | Size | Status |
|---------|------|--------|
| Flask + extensions | ~5MB | ✅ Included |
| google-generativeai | ~2MB | ✅ Included |
| psycopg2-binary | ~3MB | ✅ Included |
| PyPDF2 | ~1MB | ✅ Included |
| NLTK | ~2MB | ✅ Included |
| requests | ~1MB | ✅ Included |
| **Total** | **~15MB** | ✅ **Under 50MB limit!** |
| EasyOCR | ~500MB | ❌ Excluded |
| PyMuPDF | ~50MB | ❌ Excluded |
| pandas | ~30MB | ❌ Excluded |

## 🎉 Result

Your app will deploy successfully on Vercel with **all core features working**!

Only minor limitations:
- Image PDFs won't process (text PDFs work fine)
- XLSX export unavailable (CSV export works)

## 💡 Alternative: Use Cloud OCR Service

If you need image PDF processing on Vercel, consider:
- Google Cloud Vision API
- AWS Textract
- Azure Computer Vision

These are external APIs (no size limit) and can be called from your Vercel function.

