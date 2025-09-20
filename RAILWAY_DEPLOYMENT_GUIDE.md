# 🚀 Railway Deployment Guide for UniTest

Deploy your full UniTest application to Railway for the complete web interface experience.

## 📋 Prerequisites

- GitHub account
- Railway account (free tier available)
- Google AI API key
- NeonDB account (for database)

## 🚀 Step 1: Deploy to Railway

### 1.1 Connect to Railway
1. Go to [Railway](https://railway.app/)
2. Sign up/login with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `theakshatkhandelwal/UNITEST` repository

### 1.2 Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `SECRET_KEY` | `your-random-secret-key` | Flask secret key |
| `GOOGLE_AI_API_KEY` | `your-google-ai-api-key` | Google AI API key |
| `DATABASE_URL` | `your-neondb-connection-string` | Database URL |
| `FLASK_ENV` | `production` | Environment |

### 1.3 Deploy
Railway will automatically:
- Detect Python and install dependencies from `requirements.txt`
- Use `Procfile` to start the application
- Deploy your full application

## 🎯 Step 2: Set Up Database

### 2.1 Create NeonDB Database
1. Go to [NeonDB](https://neon.tech/)
2. Create a new project
3. Copy the connection string
4. Add it as `DATABASE_URL` in Railway

### 2.2 Database Initialization
The application will automatically create tables on first run.

## ✅ Step 3: Verify Deployment

Your application will be available at: `https://your-app-name.railway.app`

### Features Available:
- ✅ Beautiful landing page
- ✅ User registration/login
- ✅ AI-powered quiz generation
- ✅ PDF processing
- ✅ Progress tracking
- ✅ Dark/light theme
- ✅ Mobile responsive

## 🔧 Configuration Files

- `railway.json` - Railway deployment configuration
- `Procfile` - Process configuration
- `requirements.txt` - Python dependencies
- `app.py` - Main Flask application

## 🎉 Success!

Your full UniTest application is now deployed with all features working!
