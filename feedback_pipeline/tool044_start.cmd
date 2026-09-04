@echo off
chcp 65001 >nul
set "TOOL044_ROOT=%~dp0.."
set "TOOL044_PYTHON=%LOCALAPPDATA%\..\..\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%TOOL044_PYTHON%" set "TOOL044_PYTHON=py"
set "TOOL044_MANIFEST=%~1"
if "%TOOL044_MANIFEST%"=="" set "TOOL044_MANIFEST=%TOOL044_ROOT%\feedback_pipeline\tool044_manifests\fastjsonschema_fixture.json"
"%TOOL044_PYTHON%" -X utf8 "%TOOL044_ROOT%\feedback_pipeline\tool044_mechanical.py" --manifest "%TOOL044_MANIFEST%" --workspace "%TOOL044_ROOT%" --evidence "%TOOL044_ROOT%\feedback_pipeline\evidence\tool044_mechanical_deployed.json" --deployed-mode
exit /b %errorlevel%
