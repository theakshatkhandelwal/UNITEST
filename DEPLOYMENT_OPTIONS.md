# 🚀 Deployment Options for UniTest

## Option 1: Render.com

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

## Option 2: PythonAnywhere

Good for Python apps, free tier available.

### Steps:
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account
3. Upload code via Git or files
4. Configure WSGI file
5. Set up database

## Option 3: Heroku (Paid, but Reliable)

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

## Option 4: DigitalOcean App Platform

### Steps:
1. Go to [digitalocean.com](https://www.digitalocean.com)
2. Create account (free trial)
3. App Platform → Create App
4. Connect GitHub
5. Auto-detects Python
6. Configure environment variables
7. Deploy!

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

### Render:
- Needs explicit build/start commands
- Good for Python apps
- Free tier available

### DigitalOcean:
- Auto-detects most things
- Good documentation
- Free trial available

## ✅ Which to Choose?

1. **Render** - Good free tier, straightforward
2. **DigitalOcean** - Professional, good scaling
3. **Heroku** - Established, but paid now
4. **PythonAnywhere** - Python-focused, free tier available

