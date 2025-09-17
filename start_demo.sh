#!/bin/bash

echo "========================================"
echo "🎬 CONTAINER AUTO-SCALING DEMO LAUNCHER"
echo "========================================"
echo

echo "🚀 Starting the complete demo system..."
echo

echo "1️⃣ Building and starting backend services..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start backend services"
    exit 1
fi

echo "✅ Backend services started successfully!"
echo

echo "2️⃣ Waiting for services to be ready..."
sleep 5

echo "3️⃣ Starting frontend web server..."
cd frontend
python3 server.py &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend server starting on http://localhost:3000"
echo

echo "4️⃣ Running demo script..."
python3 demo_script.py

echo
echo "🎉 Demo completed!"
echo
echo "📊 What you just saw:"
echo "   ✅ Dynamic container creation"
echo "   ✅ Auto-scaling based on load"
echo "   ✅ Load balancing across containers"
echo "   ✅ Real-time monitoring"
echo "   ✅ Auto-cleanup during low load"
echo "   ✅ Interactive web dashboard"
echo
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo
echo "💡 To stop the demo:"
echo "   - Close the frontend browser tab"
echo "   - Kill frontend server: kill $FRONTEND_PID"
echo "   - Run: docker-compose down"
echo

# Keep script running
read -p "Press Enter to stop the demo and cleanup..."
echo "🛑 Stopping demo..."
kill $FRONTEND_PID 2>/dev/null
docker-compose down
echo "✅ Demo stopped and cleaned up"
