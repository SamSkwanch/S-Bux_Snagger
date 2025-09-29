@echo off
REM Build S-Bux Snagger as a standalone Windows executable
pyinstaller --onefile --windowed --name "S-Bux Snagger" --add-data "assets\sbux.png;assets" main.py

REM Output will be in the dist folder as S-Bux Snagger.exe
pause
