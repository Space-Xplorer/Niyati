#!/bin/bash

# Niyati Deployment Script
# This script helps you deploy Niyati to various platforms

set -e

echo "🚀 Niyati Deployment Helper"
echo "============================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cat > .env << EOF
# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)

# LLM API Keys
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Neo4j Configuration (get from https://neo4j.com/cloud/aura/)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Database (use SQLite for simplicity or PostgreSQL for production)
DATABASE_URL=sqlite:///./instance/niyati.db

# Frontend URL (update after deployment)
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ Created .env file. Please update it with your credentials."
    echo ""
fi

echo "Select deployment option:"
echo "1) Docker Compose (Local/VPS)"
echo "2) Railway (Backend)"
echo "3) Vercel (Frontend)"
echo "4) Full Stack (Railway + Vercel)"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "🐳 Deploying with Docker Compose..."
        echo ""
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        # Build and start containers
        docker-compose up -d --build
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "Services running at:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        echo "  Neo4j:    http://localhost:7474"
        echo ""
        echo "Next steps:"
        echo "1. Initialize database: curl -X POST http://localhost:8000/init-db"
        echo "2. Create admin user: curl -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"SecurePass123!\",\"role\":\"Admin\"}'"
        echo ""
        ;;
        
    2)
        echo ""
        echo "🚂 Deploying Backend to Railway..."
        echo ""
        
        # Check if Railway CLI is installed
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        railway login
        railway init
        railway up
        
        echo ""
        echo "✅ Backend deployed to Railway!"
        echo "Don't forget to set environment variables in Railway dashboard."
        ;;
        
    3)
        echo ""
        echo "▲ Deploying Frontend to Vercel..."
        echo ""
        
        # Check if Vercel CLI is installed
        if ! command -v vercel &> /dev/null; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi
        
        cd frontend
        vercel login
        vercel --prod
        cd ..
        
        echo ""
        echo "✅ Frontend deployed to Vercel!"
        ;;
        
    4)
        echo ""
        echo "🎯 Full Stack Deployment..."
        echo ""
        
        # Deploy backend to Railway
        echo "Step 1: Deploying Backend to Railway..."
        if ! command -v railway &> /dev/null; then
            npm install -g @railway/cli
        fi
        railway login
        railway init
        railway up
        
        echo ""
        read -p "Enter your Railway backend URL (e.g., https://your-app.railway.app): " BACKEND_URL
        
        # Update frontend env
        echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > frontend/.env.local
        
        # Deploy frontend to Vercel
        echo ""
        echo "Step 2: Deploying Frontend to Vercel..."
        if ! command -v vercel &> /dev/null; then
            npm install -g vercel
        fi
        cd frontend
        vercel login
        vercel --prod
        cd ..
        
        echo ""
        echo "✅ Full stack deployment complete!"
        echo ""
        echo "Next steps:"
        echo "1. Set environment variables in Railway dashboard"
        echo "2. Initialize database: curl -X POST $BACKEND_URL/init-db"
        echo "3. Create admin user via API"
        ;;
        
    5)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
