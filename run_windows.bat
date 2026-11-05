@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo در حال اجرای نرم افزار نظریه یار...
call .venv\Scripts\activate

python -m uvicorn app:app --host 127.0.0.1 --port 8083

echo.
echo ===================================================
echo اگر برنامه متوقف شد، متن بالای همین صفحه خطای اصلی است!
echo ===================================================
pause