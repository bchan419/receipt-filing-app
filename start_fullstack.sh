#!/bin/bash

# Full Stack Receipt OCR App Startup Script
echo "🧾 Starting Receipt OCR App - Full Stack"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run the following first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
if ! check_port 8000; then
    echo "   Backend may already be running on http://localhost:8000"
fi

if ! check_port 3000; then
    echo "   Frontend may already be running on http://localhost:3000"
fi

echo ""
echo "🚀 Starting services..."

# Start backend in background
echo "📡 Starting FastAPI backend..."
cd "$(dirname "$0")"
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/google-credentials.json"
export GOOGLE_CLOUD_PROJECT=receipt-filing-app
cd src
python main.py &
BACKEND_PID=$!
echo "   Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting React frontend..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "   Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "   Frontend started with PID: $FRONTEND_PID"

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access your app:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop services:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Create a trap to kill both processes when script is terminated
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for any process to exit
wait