@echo off
title Discord Bot Auto-Restarter
:loop
echo =========================================
echo [SYS] Starting bot...
echo =========================================
python main.py
echo.
echo [SYS] Bot went offline! Restarting in 3 seconds... 
echo [SYS] (Press CTRL+C if you want to stop it completely)
timeout /t 3
goto loop
