#!/bin/bash

# Deploy script - builds and prepares for deployment

set -e

echo "Building ChatApp for production..."

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt --quiet
cd ..

echo "Build complete!"
echo ""
echo "To run in production:"
echo "  Backend: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "  Frontend: Serve the 'frontend/dist' folder"