@echo off
echo Starting Backend Server...
cd /d %~dp0
py -3 app.py
pause

