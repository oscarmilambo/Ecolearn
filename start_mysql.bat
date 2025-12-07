@echo off
echo ========================================
echo Starting MySQL Server via XAMPP
echo ========================================
echo.

REM Check if XAMPP exists
if not exist "C:\xampp\mysql_start.bat" (
    echo ERROR: XAMPP not found at C:\xampp\
    echo Please install XAMPP or start MySQL manually
    pause
    exit /b 1
)

echo Starting MySQL...
cd C:\xampp
call mysql_start.bat

echo.
echo ========================================
echo MySQL should now be running!
echo ========================================
echo.
echo Next steps:
echo 1. Keep this window open
echo 2. Open a new terminal
echo 3. Run: python manage.py runserver
echo.
pause
