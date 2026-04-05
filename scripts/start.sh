#!/bin/bash

# Start script - runs both backend and frontend

echo "Starting ChatApp..."

# Start backend
echo "Starting backend..."
cd backend
python -m pip install -r requirements.txt 2>/dev/null || pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm install 2>/dev/null || true
npm run dev &
FRONTEND_PID=$!

echo "ChatApp started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait