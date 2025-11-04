# 🚀 Quick Deploy to Vercel - Step by Step

## Step 1: Prepare Your Code ✅

Your code is ready! I've already:
- ✅ Updated `requirements_vercel.txt` (excluded EasyOCR for size limits)
- ✅ Made EasyOCR optional (disabled on Vercel)
- ✅ Verified `vercel.json` configuration
- ✅ Verified `api/index.py` handler

## Step 2: Push to GitHub

```bash
# If you haven't initialized git yet:
git init
git add .
git commit -m "Ready for Vercel deployment"

# If you have a GitHub repo:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Vercel

### Option A: Using Vercel Website (Easiest)

1. **Go to [vercel.com](https://vercel.com)**
   - Sign in with GitHub

2. **Click "New Project"**
   - Import your GitHub repository
   - Select your repository

3. **Configure Project:**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: (leave empty - Vercel auto-detects)

4. **Add Environment Variables** (Click "Environment Variables"):
   
   | Variable Name | Value | Environment |
   |--------------|-------|-------------|
   | `SECRET_KEY` | `generate-random-32-chars` | All (Production, Preview, Development) |
   | `GOOGLE_AI_API_KEY` | `your-google-api-key` | All |
   | `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | All |
   | `VERCEL` | `1` | All |

5. **Click "Deploy"**
   - Wait 2-5 minutes
   - Your app will be live!

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (from your project directory)
cd D:\UNITEST
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? unittest (or your choice)
# - Directory? ./
# - Override settings? No

# For production deployment
vercel --prod
```

## Step 4: Set Up NeonDB (If Not Done)

1. Go to [neon.tech](https://neon.tech)
2. Sign up for free account
3. Create new project
4. Copy connection string
5. Add to Vercel environment variables as `DATABASE_URL`

## Step 5: Verify Deployment

After deployment, visit your URL:
- `https://your-project-name.vercel.app`

Test:
- ✅ Homepage loads
- ✅ User registration works
- ✅ Login works
- ✅ Quiz creation works
- ✅ Quiz taking works

## 🔑 Generate Secret Key

Run this in Python to generate a secure secret key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📝 Important Notes

1. **PDF OCR**: EasyOCR is disabled on Vercel due to size limits. Text-based PDFs will still work with PyPDF2. For image PDFs, consider using a cloud OCR service.

2. **Database**: Tables will auto-create on first run. No manual setup needed.

3. **API Keys**: Make sure your Google AI API key has sufficient quota.

4. **Updates**: Just push to GitHub and Vercel will auto-deploy!

## 🐛 Troubleshooting

### Build Fails
- Check Vercel build logs
- Verify Python version (should be 3.11+)
- Check requirements_vercel.txt

### Database Connection Error
- Verify DATABASE_URL format: `postgresql://...` (not `postgres://`)
- Check SSL mode: `?sslmode=require`
- Ensure NeonDB project is active

### Function Timeout
- Vercel free tier: 10 seconds max
- Optimize slow operations
- Consider Pro plan for longer timeouts

### 500 Errors
- Check Vercel function logs
- Verify all environment variables are set
- Check database connection

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Vercel project created
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Homepage loads
- [ ] User registration works
- [ ] Database connection works
- [ ] Quiz creation works

## 🎉 You're Live!

Your app is now deployed at: `https://your-project-name.vercel.app`

Share it with your users and start testing!

