# PowerShell Script to Push Unitest to GitHub
# Run this script after creating a new GitHub repository

Write-Host "🚀 Unitest GitHub Push Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get repository details
$username = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter your repository name (e.g., unitest)"

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($repoName)) {
    Write-Host "❌ Error: Username and repository name are required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Yellow
Write-Host "   Username: $username"
Write-Host "   Repository: $repoName"
Write-Host "   Remote URL: https://github.com/$username/$repoName.git"
Write-Host ""

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "❌ Cancelled by user" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔧 Step 1: Removing old remote (if exists)..." -ForegroundColor Yellow
git remote remove origin 2>$null
Write-Host "✅ Done" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Step 2: Adding new remote..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/$repoName.git"
Write-Host "✅ Done" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Step 3: Verifying remote..." -ForegroundColor Yellow
git remote -v
Write-Host "✅ Done" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Step 4: Setting main branch..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Done" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Step 5: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   (You may be prompted for credentials)" -ForegroundColor Gray
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Success! Your code has been pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 View your repository at: https://github.com/$username/$repoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Add repository description: 'Unitest - AI-Powered Learning Platform'"
    Write-Host "   2. Add topics: unitest, ai-learning, quiz-generator, education"
    Write-Host "   3. Update GitHub Pages settings if needed"
    Write-Host "   4. Submit sitemap to Google Search Console"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error: Push failed. Please check:" -ForegroundColor Red
    Write-Host "   1. Repository exists on GitHub"
    Write-Host "   2. You have write access"
    Write-Host "   3. You're using correct credentials (use Personal Access Token)"
    Write-Host ""
    Write-Host "💡 Tip: Use Personal Access Token instead of password" -ForegroundColor Yellow
    Write-Host "   GitHub → Settings → Developer settings → Personal access tokens"
    Write-Host ""
}

