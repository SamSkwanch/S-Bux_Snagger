@echo off
REM Build S-Bux Snagger as a standalone Windows executable
pyinstaller --onefile --windowed --add-data "assets\sbux.png;assets" main.py

REM Output will be in the dist folder
pause
