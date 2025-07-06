#!/bin/bash

# Mobile-Friendly Receipt OCR App Startup Script
echo "📱 Starting Receipt OCR App - Mobile & Desktop"
echo "==============================================="

# Get local IP address for mobile access
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Could not determine local IP address"
    LOCAL_IP="YOUR_IP_ADDRESS"
fi

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
        echo "⚠️  Port $1 is already in use - killing existing process"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Check and clear ports
check_port 8000
check_port 3000

echo ""
echo "🚀 Starting services for mobile access..."
echo "📍 Your local IP: $LOCAL_IP"

# Start backend
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

# Start frontend with network binding
echo "🎨 Starting React frontend (mobile-friendly)..."
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "   Installing frontend dependencies..."
    npm install
fi

# Start with network access
npm run dev &
FRONTEND_PID=$!
echo "   Frontend started with PID: $FRONTEND_PID"

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access your app:"
echo "   💻 Desktop: http://localhost:3000"
echo "   📱 Mobile:  http://$LOCAL_IP:3000"
echo "   🔗 API:     http://localhost:8000"
echo "   📚 Docs:    http://localhost:8000/docs"
echo ""
echo "📋 Mobile Testing Instructions:"
echo "   1. Ensure your phone is on the same WiFi network"
echo "   2. Open http://$LOCAL_IP:3000 on your mobile browser"
echo "   3. Look for green 'API Connected' status"
echo "   4. Test camera upload and touch editing"
echo ""
echo "🛑 To stop services:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Create a trap to kill both processes when script is terminated
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for any process to exit
wait