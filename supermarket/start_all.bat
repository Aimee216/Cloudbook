@echo off
echo ==================================================
echo      ?????? - ????
echo ==================================================
echo.
echo ?? API:  http://localhost:8000
echo ????:  http://localhost:3000
echo ????:  admin / admin123
echo.
echo ? Ctrl+C ??????
echo ==================================================
echo.

cd /d E:\Cloudbook_git\supermarket\backend
start "SupermarketAPI-Backend" "D:\Python\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000

cd /d E:\Cloudbook_git\supermarket\frontend
start "SupermarketAPI-Frontend" "D:\Python\python.exe" -m http.server 3000

echo ?????????????? http://localhost:3000
echo.
pause
