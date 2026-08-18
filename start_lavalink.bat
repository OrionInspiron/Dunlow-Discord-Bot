@echo off
cd /d "%~dp0"
title Local Lavalink Server
color 0A
echo Starting Local Lavalink Server...
echo Make sure you keep this window open while the bot is running!
echo =======================================================
java -jar Lavalink.jar
pause
