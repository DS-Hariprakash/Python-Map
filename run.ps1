# PowerShell helper. Usage: .\run.ps1 [path\to\file]
if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }
python python_map\app.py $args
