@echo off
cd /d "%~dp0"
if "%~1"=="" (
  start "" "%~dp0index.html"
) else (
  python scripts\serve.py --port %1
)
