#!/usr/bin/env bash
# Unix helper. Usage: ./run.sh [path/to/file]
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi
python python_map/app.py "$@"
