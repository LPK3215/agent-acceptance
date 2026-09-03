@echo off
rem agent-acceptance: one-click check (wrapper of scripts/verify.py)
cd /d "%~dp0.."
python scripts\verify.py %*
pause
