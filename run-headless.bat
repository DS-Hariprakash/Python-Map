@echo off
REM Create HTML map without launching GUI. Usage: run-headless.bat path\to\file.csv
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
python python_map\app.py --headless %1
