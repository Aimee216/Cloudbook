@echo off
cd /d E:\Cloudbook_git\supermarket\backend
echo ================================================
echo        ?????? - ????
echo ================================================
echo.
echo ????: http://localhost:8000/login
echo API??:  http://localhost:8000/docs
echo.
echo ??: admin / admin123
echo.
echo ? Ctrl+C ????
echo ================================================
echo.
"D:\Python\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000
pause
