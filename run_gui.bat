@echo off
cd /d "%~dp0"
if exist "C:\Windows\System32\soc-env\Scripts\python.exe" (
    "C:\Windows\System32\soc-env\Scripts\python.exe" -m operate.gui
) else (
    python -m operate.gui
)
pause