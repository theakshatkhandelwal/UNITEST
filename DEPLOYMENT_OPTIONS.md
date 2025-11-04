# 🚀 Deployment Options for UniTest

## Option 1: Fly.io (Current - Requires Verification)

### Account Verification
1. Go to: https://fly.io/high-risk-unlock
2. Follow the verification steps
3. May require:
   - Phone number verification
   - Credit card (free tier, no charges)
   - Email verification
   - Identity verification

Once verified, continue with:
```bash
fly launch
fly secrets set SECRET_KEY=your-key
fly secrets set GOOGLE_AI_API_KEY=your-key
fly secrets set DATABASE_URL=your-neondb-url
fly deploy
```

## Option 2: Railway (Recommended Alternative)

Railway is similar to Fly.io, easier signup, and supports all features.

### Steps:
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (easiest)
3. Create new project
4. Connect your GitHub repo
5. Add environment variables
6. Deploy!

### Railway Configuration:

Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

Railway automatically:
- Detects Python
- Installs from requirements.txt
- Runs the Procfile command
- Provides PostgreSQL (or use NeonDB)

## Option 3: Render.com

### Steps:
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New → Web Service
4. Connect GitHub repo
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
   - **Environment**: Python 3
6. Add environment variables
7. Deploy!

## Option 4: PythonAnywhere

Good for Python apps, free tier available.

### Steps:
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account
3. Upload code via Git or files
4. Configure WSGI file
5. Set up database

## Option 5: Heroku (Paid, but Reliable)

### Steps:
1. Go to [heroku.com](https://heroku.com)
2. Create account
3. Install Heroku CLI
4. Deploy:
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-key
heroku config:set GOOGLE_AI_API_KEY=your-key
heroku config:set DATABASE_URL=your-neondb-url
git push heroku main
```

## Option 6: DigitalOcean App Platform

### Steps:
1. Go to [digitalocean.com](https://www.digitalocean.com)
2. Create account (free trial)
3. App Platform → Create App
4. Connect GitHub
5. Auto-detects Python
6. Configure environment variables
7. Deploy!

## 🎯 Recommended: Railway (Easiest)

Railway is the easiest alternative:
- ✅ No credit card required initially
- ✅ Easy GitHub integration
- ✅ Auto-detects Python
- ✅ Supports all dependencies
- ✅ Free tier available
- ✅ Simple deployment

## 📝 Common Setup for All Platforms

### Environment Variables Needed:
```
SECRET_KEY=your-secret-key-32-chars-minimum
GOOGLE_AI_API_KEY=your-google-ai-api-key
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Generate Secret Key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🔧 Platform-Specific Notes

### Railway:
- Uses `Procfile` for start command
- Auto-detects Python version
- Provides PostgreSQL (optional)

### Render:
- Needs explicit build/start commands
- Good for Python apps
- Free tier available

### DigitalOcean:
- Auto-detects most things
- Good documentation
- Free trial available

## ✅ Which to Choose?

1. **Railway** - Easiest, best for beginners
2. **Render** - Good free tier, straightforward
3. **Fly.io** - After verification, most flexible
4. **DigitalOcean** - Professional, good scaling
5. **Heroku** - Established, but paid now

## 🚀 Quick Start with Railway

1. Visit: https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select your repo
5. Add environment variables
6. Deploy!

That's it! Railway handles everything else.

