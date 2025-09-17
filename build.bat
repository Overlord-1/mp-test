@echo off
echo Building Docker images...

REM Build main-server image first
echo Building main-server image...
cd main-server
docker build -t main-server:latest .
if %ERRORLEVEL% neq 0 (
    echo Error building main-server image!
    pause
    exit /b 1
)
cd ..

REM Build routing-server image
echo Building routing-server image...
cd routing-server
docker build -t routing-server:latest .
if %ERRORLEVEL% neq 0 (
    echo Error building routing-server image!
    pause
    exit /b 1
)
cd ..

echo All images built successfully!
echo.
echo To run the complete setup:
echo 1. Start the routing server: docker-compose up -d
echo 2. Test the /work endpoint: curl -X POST http://localhost:8000/work -H "Content-Type: application/json" -d "{\"intensity\": 2}"
echo 3. Check container status: curl http://localhost:8000/status
echo 4. Get graph data: curl http://localhost:8000/graph
echo.
echo IMPORTANT: Make sure Docker daemon is running!
pause
