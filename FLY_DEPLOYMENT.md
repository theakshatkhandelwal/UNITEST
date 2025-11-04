# 🚀 Fly.io Deployment Guide for UniTest

Fly.io is perfect for this application as it supports larger dependencies and has no strict size limits like Vercel.

## 📋 Prerequisites

- Fly.io account (free tier available)
- GitHub repository
- NeonDB database (or any PostgreSQL)
- Google AI API key

## 🔧 Step 1: Install Fly CLI

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# macOS/Linux
curl -L https://fly.io/install.sh | sh
```

## 🚀 Step 2: Create Fly.io App

```bash
# Login to Fly.io
fly auth login

# Create new app (from your project directory)
cd D:\UNITEST
fly launch

# Follow prompts:
# - App name: unittest (or your choice)
# - Region: Choose closest to you
# - PostgreSQL: No (we'll use NeonDB)
# - Redis: No
```

## 📝 Step 3: Create fly.toml

Create `fly.toml` in your project root:

```toml
app = "your-app-name"
primary_region = "iad"  # or your preferred region

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  FLASK_ENV = "production"
  PYTHONUNBUFFERED = "1"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[services]]
  protocol = "tcp"
  internal_port = 5000
  processes = ["app"]

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"
```

## 🐳 Step 4: Create Dockerfile

Create `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

## 📦 Step 5: Create requirements.txt for Fly.io

Ensure `requirements.txt` includes all dependencies:

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
google-generativeai==0.8.3
python-dotenv==1.0.1
psycopg2-binary==2.9.9
Werkzeug==3.0.1
PyPDF2==3.0.1
pdf2image==1.16.3
pytesseract==0.3.10
easyocr==1.7.0
PyMuPDF==1.23.8
Pillow==10.1.0
nltk==3.8.1
pandas==2.1.3
requests==2.31.0
gunicorn==21.2.0
openpyxl==3.1.2
```

## 🔐 Step 6: Set Environment Variables

```bash
fly secrets set SECRET_KEY=your-secret-key-here
fly secrets set GOOGLE_AI_API_KEY=your-google-api-key
fly secrets set DATABASE_URL=your-neondb-connection-string
```

Or use Fly.io dashboard:
1. Go to your app on fly.io dashboard
2. Settings → Secrets
3. Add all environment variables

## 🚀 Step 7: Deploy

```bash
# Deploy to Fly.io
fly deploy

# Check status
fly status

# View logs
fly logs
```

## ✅ Step 8: Verify Deployment

1. Visit your app: `https://your-app-name.fly.dev`
2. Test all features:
   - User registration
   - Quiz creation
   - Coding questions
   - PDF processing
   - All exports

## 📊 Fly.io Advantages

✅ **No Size Limits**: Can include all dependencies (EasyOCR, pandas, etc.)
✅ **System Binaries**: Can install Poppler, Tesseract in Docker
✅ **Longer Timeouts**: Better for AI processing
✅ **Better for Python**: Native Python support
✅ **More Flexible**: Full Docker control

## 🔧 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check Fly.io build logs: `fly logs`

### App Crashes
- Check logs: `fly logs`
- Verify environment variables: `fly secrets list`
- Check database connection

### Slow Startup
- EasyOCR models download on first run (~500MB)
- Subsequent starts are faster
- Consider pre-downloading models in Dockerfile

## 📈 Scaling

```bash
# Scale up machines
fly scale count 2

# Scale memory
fly scale vm shared-cpu-2x --memory 2048
```

## 🔄 Updates

```bash
# Deploy updates
git push
fly deploy

# Or automatic from GitHub
# Connect GitHub repo in Fly.io dashboard for auto-deploy
```

## 💰 Pricing

Fly.io free tier includes:
- 3 shared-cpu-256 VMs
- 3GB persistent volume
- 160GB outbound data transfer

Perfect for getting started!

## 🎉 You're Live!

Your app is now deployed at: `https://your-app-name.fly.dev`

All features work including:
- ✅ Full PDF OCR (EasyOCR + PyMuPDF)
- ✅ All coding features
- ✅ CSV/XLSX exports
- ✅ All quiz features

