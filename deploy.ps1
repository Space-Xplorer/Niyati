# Niyati Deployment Script for Windows

Write-Host "🚀 Niyati Deployment Helper" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    
    $jwtSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    
    @"
# JWT Configuration
JWT_SECRET_KEY=$jwtSecret

# LLM API Keys
GROQ_API_KEY=your-groq-api-key-here

# Neo4j Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Database
DATABASE_URL=sqlite:///./instance/niyati.db

# Frontend URL
FRONTEND_URL=http://localhost:3000
"@ | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "✅ Created .env file. Please update it with your credentials." -ForegroundColor Green
    Write-Host ""
}

Write-Host "Select deployment option:"
Write-Host "1) Railway (Backend)"
Write-Host "2) Vercel (Frontend)"
Write-Host "3) Full Stack (Railway + Vercel)"
Write-Host "4) Exit"
Write-Host ""
$choice = Read-Host "Enter choice [1-4]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚂 Deploying Backend to Railway..." -ForegroundColor Cyan
        railway login
        railway init
        railway up
        Write-Host "✅ Backend deployed!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host ""
        Write-Host "▲ Deploying Frontend to Vercel..." -ForegroundColor Cyan
        Set-Location frontend
        vercel login
        vercel --prod
        Set-Location ..
        Write-Host "✅ Frontend deployed!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "🎯 Full Stack Deployment..." -ForegroundColor Cyan
        railway login
        railway init
        railway up
        
        $backendUrl = Read-Host "Enter Railway backend URL"
        "NEXT_PUBLIC_API_URL=$backendUrl" | Out-File -FilePath "frontend/.env.local" -Encoding UTF8
        
        Set-Location frontend
        vercel login
        vercel --prod
        Set-Location ..
        Write-Host "✅ Deployment complete!" -ForegroundColor Green
    }
    
    "4" {
        exit 0
    }
}
