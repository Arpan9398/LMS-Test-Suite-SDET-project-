@echo off
REM Windows: run pytest then build the report
cd /d "%~dp0\.."
python -m pytest %*
set STATUS=%ERRORLEVEL%
python scripts\generate_report.py
exit /b %STATUS%
