@echo off
REM Build S-Bux Snagger as a standalone Windows executable
REM Using --windowed for no console window (GUI app)
pyinstaller --onefile --windowed --name "S-Bux Snagger" sbux_snagger.py

REM Output will be in the dist folder as "S-Bux Snagger.exe"
echo.
echo Build complete! Executable is in the 'dist' folder.
pause
