@echo off
echo ========================================
echo 🎬 CONTAINER AUTO-SCALING DEMO LAUNCHER
echo ========================================
echo.

echo 🚀 Starting the complete demo system...
echo.

echo 1️⃣ Building and starting backend services...
call docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start backend services
    pause
    exit /b 1
)

echo ✅ Backend services started successfully!
echo.

echo 2️⃣ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

echo 3️⃣ Starting frontend web server...
cd frontend
start "Frontend Server" python server.py
cd ..

echo ✅ Frontend server starting on http://localhost:3000
echo.

echo 4️⃣ Running demo script...
python demo_script.py

echo.
echo 🎉 Demo completed!
echo.
echo 📊 What you just saw:
echo    ✅ Dynamic container creation
echo    ✅ Auto-scaling based on load  
echo    ✅ Load balancing across containers
echo    ✅ Real-time monitoring
echo    ✅ Auto-cleanup during low load
echo    ✅ Interactive web dashboard
echo.
echo 🌐 Frontend Dashboard: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo.
echo 💡 To stop the demo:
echo    - Close the frontend browser tab
echo    - Press Ctrl+C to stop frontend server
echo    - Run: docker-compose down
echo.
pause
