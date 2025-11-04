# 🚀 Quick Deployment Guide - UniTest

## ⚠️ Important Notes

### PDF OCR Considerations
- **EasyOCR** requires ~500MB of models which may exceed Vercel's function size limits
- For production, consider:
  1. Using a separate OCR service (Google Cloud Vision, AWS Textract)
  2. Removing EasyOCR from Vercel deployment (use only for local/testing)
  3. Using a lighter alternative

### Recommended Approach
For Vercel deployment, we'll use a **lightweight version** that excludes heavy OCR dependencies.

## 📋 Pre-Deployment Checklist

- [ ] GitHub repository set up
- [ ] Vercel account created
- [ ] NeonDB database set up
- [ ] Google AI API key obtained
- [ ] Environment variables ready

## 🚀 Deployment Steps

### Step 1: Update Requirements for Vercel

The `requirements_vercel.txt` should include only essential dependencies. Heavy packages like EasyOCR should be excluded or made optional.

### Step 2: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 3: Deploy to Vercel

#### Option A: Via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Import your GitHub repository
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
6. Add Environment Variables:
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_AI_API_KEY=your-google-api-key
   DATABASE_URL=your-neondb-connection-string
   VERCEL=1
   ```
7. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# For production
vercel --prod
```

### Step 4: Verify Deployment

1. Visit your deployment URL
2. Test basic functionality:
   - User registration
   - Login
   - Quiz creation
   - Quiz taking

## 🔧 Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-random-secret-key-32-chars` |
| `GOOGLE_AI_API_KEY` | Google Generative AI key | `AIza...` |
| `DATABASE_URL` | NeonDB connection string | `postgresql://...` |
| `VERCEL` | Indicates Vercel environment | `1` |

## 📦 Handling Large Dependencies

### Option 1: Remove EasyOCR for Production (Recommended)
Update `app.py` to make EasyOCR optional and gracefully handle its absence.

### Option 2: Use Cloud OCR Service
Replace EasyOCR with:
- Google Cloud Vision API
- AWS Textract
- Azure Computer Vision

### Option 3: External OCR Service
Create a separate microservice for OCR processing.

## 🐛 Troubleshooting

### Build Fails
- Check Vercel build logs
- Verify all dependencies in `requirements_vercel.txt`
- Ensure Python version compatibility

### Function Timeout
- Vercel free tier: 10 seconds
- Optimize slow operations
- Consider upgrading to Pro plan

### Database Connection Issues
- Verify `DATABASE_URL` format
- Ensure NeonDB project is active
- Check SSL mode in connection string

### Large Package Size
- Remove unnecessary dependencies
- Use lighter alternatives
- Split into multiple functions

## 📊 Post-Deployment

1. **Test All Features**
   - User registration/login
   - Quiz creation
   - Quiz taking
   - Results viewing

2. **Monitor Performance**
   - Check Vercel Analytics
   - Monitor function execution times
   - Check error rates

3. **Set Up Custom Domain** (Optional)
   - Go to Vercel Dashboard → Domains
   - Add your domain
   - Update DNS settings

## 🔄 Updates

To update your deployment:
```bash
git add .
git commit -m "Update description"
git push
# Vercel will automatically redeploy
```

## 📝 Notes

- PDF OCR with EasyOCR works locally but may not work on Vercel due to size limits
- Consider using a cloud OCR service for production
- All other features should work normally

