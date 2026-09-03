@echo off
rem agent-acceptance: one-click release = check + package(zip) + install to local CodeBuddy
cd /d "%~dp0.."
python scripts\release.py all %*
pause
