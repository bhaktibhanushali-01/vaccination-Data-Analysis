@echo off
REM Double-click this file to run the entire project pipeline.
REM It changes into this file's own folder first, so it works no matter
REM where the folder is on your computer.

cd /d "%~dp0"
python RUN_ME.py

echo.
echo Press any key to close this window...
pause >nul
