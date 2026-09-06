@echo off
setlocal
set "TOOL043_DIR=%~dp0"
set "TOOL043_PY=C:\Users\obk36\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "TOOL043_URL=http://127.0.0.1:8043/index.html"
if not exist "%TOOL043_PY%" goto snapshot
start "TOOL043 local server" /min "%TOOL043_PY%" -m http.server 8043 --bind 127.0.0.1 --directory "%TOOL043_DIR%"
ping 127.0.0.1 -n 2 >nul
start "" "%TOOL043_URL%"
exit /b 0
:snapshot
start "" "%TOOL043_DIR%index.html"
exit /b 0
