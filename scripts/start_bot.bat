@echo off
title Canvas Automation Bot Server
cd /d C:\Users\bryso\.claude\automations\auto_canvas
echo Starting Canvas Automation Bot...
echo.
python bots\telegram-bot-listener.py
pause
