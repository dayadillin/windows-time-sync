@echo off
:: run_sync_time.bat
:: Silently runs sync_time.py without showing a console window.
:: Place this .bat in the same folder as sync_time.py
:: Task Scheduler points to this file.

cd /d "%~dp0"
pythonw sync_time.py
