@echo off
cd /d E:\Cloudbook_git\supermarket\backend
echo Starting Supermarket API Server...
echo.
echo Access URLs:
echo   API:    http://localhost:8000
echo   Swagger: http://localhost:8000/docs
echo.
"D:\Python\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000
pause
