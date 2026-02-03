@echo off
REM Capture a screenshot of the GUI. Usage: run-screenshot.bat out.png [path\to\file]
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
python python_map\app.py --screenshot %1 %2
