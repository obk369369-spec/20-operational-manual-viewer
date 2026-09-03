@echo off
chcp 65001 >nul
"C:\Users\obk36\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -X utf8 "%~dp0tool044_acquire.py" --production --workspace "I:\오부장 AI (인공지능)\WIC34_C_REBUILD\_work16_persistent_feedback_reconcile"
exit /b %errorlevel%
