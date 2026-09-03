@echo off
rem agent-acceptance: one-click check (wrapper of docs/verify.py)
cd /d "%~dp0.."
python docs\verify.py %*
pause
