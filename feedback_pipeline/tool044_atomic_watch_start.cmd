@echo off
set "TOOL044_TRIGGER_SOURCE=MANUAL"
if /I "%~1"=="--scheduled" set "TOOL044_TRIGGER_SOURCE=SCHEDULED"
set "TOOL044_PYTHON=%LOCALAPPDATA%\..\..\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%TOOL044_PYTHON%" set "TOOL044_PYTHON=py"
"%TOOL044_PYTHON%" -X utf8 "%~dp0tool044_atomic_watch.py" --external --trigger-source "%TOOL044_TRIGGER_SOURCE%"
exit /b %errorlevel%
