# PowerShell script to deploy to Vercel with optimized requirements
# This temporarily uses requirements_vercel.txt to stay under 50MB limit

Write-Host "🚀 Preparing Vercel deployment with optimized requirements..." -ForegroundColor Cyan

# Backup original requirements.txt if it exists
if (Test-Path "requirements.txt") {
    Write-Host "📦 Backing up requirements.txt..." -ForegroundColor Yellow
    Copy-Item "requirements.txt" "requirements_full.txt" -Force
    Write-Host "✅ Backup saved as requirements_full.txt" -ForegroundColor Green
}

# Use optimized requirements for Vercel
if (Test-Path "requirements_vercel.txt") {
    Write-Host "📝 Using optimized requirements_vercel.txt..." -ForegroundColor Yellow
    Copy-Item "requirements_vercel.txt" "requirements.txt" -Force
    Write-Host "✅ requirements.txt updated for Vercel deployment" -ForegroundColor Green
} else {
    Write-Host "❌ Error: requirements_vercel.txt not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📊 Size optimization:" -ForegroundColor Cyan
Write-Host "  - Excluded: EasyOCR (~500MB), PyMuPDF (~50MB), pandas (~30MB)" -ForegroundColor Gray
Write-Host "  - Included: Flask, Google AI, PostgreSQL, PyPDF2, NLTK" -ForegroundColor Gray
Write-Host "  - Estimated size: ~15-20MB (under 50MB limit!)" -ForegroundColor Green
Write-Host ""

# Check if Vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelInstalled) {
    Write-Host "⚠️  Vercel CLI not found. Install with: npm i -g vercel" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Install Vercel CLI: npm i -g vercel" -ForegroundColor White
    Write-Host "  2. Run: vercel login" -ForegroundColor White
    Write-Host "  3. Run: vercel --prod" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Or deploy via Vercel dashboard:" -ForegroundColor Cyan
    Write-Host "  1. Push this code to GitHub" -ForegroundColor White
    Write-Host "  2. Import project in Vercel dashboard" -ForegroundColor White
    Write-Host "  3. Vercel will use requirements.txt automatically" -ForegroundColor White
} else {
    Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Cyan
    Write-Host ""
    vercel --prod
}

Write-Host ""
Write-Host "📝 After deployment:" -ForegroundColor Cyan
Write-Host "  To restore full requirements for local development:" -ForegroundColor Yellow
Write-Host "    Copy-Item requirements_full.txt requirements.txt -Force" -ForegroundColor White
Write-Host ""

