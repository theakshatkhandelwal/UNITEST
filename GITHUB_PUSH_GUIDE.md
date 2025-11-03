# 🚀 GitHub Repository Setup Guide

This guide will help you push your Unitest project to a new GitHub repository.

## 📋 Prerequisites

1. GitHub account created
2. Git installed on your system
3. Terminal/PowerShell access

## 🔧 Step-by-Step Instructions

### Step 1: Create a New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `unitest` (or any name you prefer)
   - **Description**: `AI-Powered Learning Platform - Smart Quiz Generator with Google Gemini AI`
   - **Visibility**: Choose Public (recommended for SEO) or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### Step 2: Prepare Your Local Repository

Open PowerShell/Terminal in your project directory (`D:\UNITEST`) and run:

```powershell
# Check current status
git status

# Add all files (including new ones)
git add .

# Commit all changes
git commit -m "Initial commit: Unitest AI Learning Platform with SEO optimization"
```

### Step 3: Connect to New GitHub Repository

Replace `YOUR_USERNAME` with your GitHub username and `REPO_NAME` with your repository name:

```powershell
# Remove old remote if exists
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Verify remote was added
git remote -v
```

**Example:**
```powershell
git remote add origin https://github.com/theakshatkhandelwal/unitest.git
```

### Step 4: Push to GitHub

```powershell
# Push to main branch
git branch -M main
git push -u origin main
```

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your GitHub password)

### Step 5: Create Personal Access Token (if needed)

If you need to create a token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Give it a name: `Unitest Push Token`
4. Select scopes: Check `repo` (full control)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

## 🔍 Verify Your Push

1. Go to your GitHub repository page
2. You should see all your files
3. Check that the README.md displays correctly
4. Verify all files are present

## 📝 Next Steps for SEO

After pushing to GitHub:

1. **Update Repository Description**: Add "Unitest - AI Learning Platform" in the repo description
2. **Add Topics**: Add topics like: `unitest`, `ai-learning`, `quiz-generator`, `education`, `flask`, `python`
3. **Enable GitHub Pages** (optional): Settings → Pages → Enable GitHub Pages
4. **Update README**: Ensure it's optimized for "unitest" keyword
5. **Submit to Google Search Console**: Once deployed, submit your sitemap

## 🎯 SEO Checklist

- ✅ SEO-optimized meta tags
- ✅ "Unitest" keyword in titles and descriptions
- ✅ Updated sitemap.xml
- ✅ robots.txt configured
- ✅ Structured data (JSON-LD)
- ✅ Open Graph tags
- ✅ Google Site Verification

## 🚨 Troubleshooting

### Issue: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Issue: "Authentication failed"
- Use Personal Access Token instead of password
- Or use SSH instead of HTTPS

### Issue: "Large files" error
- Check `.gitignore` includes large files
- Use Git LFS for large files if needed

## 📞 Need Help?

If you encounter any issues:
1. Check the error message carefully
2. Verify your GitHub credentials
3. Ensure repository name matches exactly
4. Check internet connection

---

**Happy Coding! 🎉**

