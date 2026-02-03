@echo off
REM Simple runner for Windows (cmd). Usage: run.bat [path/to/file]
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
python python_map\app.py %*
