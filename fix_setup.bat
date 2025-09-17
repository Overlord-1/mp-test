@echo off
echo Fixing the setup - building main-server image...

REM Build main-server image
echo Building main-server image...
cd main-server
docker build -t main-server:latest .
if %ERRORLEVEL% neq 0 (
    echo Error building main-server image!
    pause
    exit /b 1
)
cd ..

echo Main-server image built successfully!
echo.
echo Now you can test the /work endpoint again:
echo curl -X POST http://localhost:8000/work -H "Content-Type: application/json" -d "{\"intensity\": 2}"
echo.
echo Or restart the routing server:
echo docker-compose down
echo docker-compose up -d
pause
