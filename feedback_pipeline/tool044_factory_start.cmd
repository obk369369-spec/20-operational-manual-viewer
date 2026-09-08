@echo off
chcp 65001 >nul
set "FACTORY_ROOT=%~dp0"
set "FACTORY_PYTHON=%LOCALAPPDATA%\..\..\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%FACTORY_PYTHON%" exit /b 3
set "PYTHONPATH=%FACTORY_ROOT%external_candidate_pool\doit-0.37.0-py3-none-any.whl;%PYTHONPATH%"
"%FACTORY_PYTHON%" -m doit -f "%FACTORY_ROOT%dodo_tool044_factory.py" --continue -n 2
exit /b %errorlevel%
