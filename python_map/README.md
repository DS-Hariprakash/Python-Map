# Python Map Viewer 🔧

Advanced map viewer with zoom controls, field selection, and filters by City/District/State.

## Features ✅
- Load data from Excel (.xlsx/.xls) or CSV (.csv)
- Select which columns to show in marker popups
- Filter rows by State, District, City (multi-select)
- Zoom in / Zoom out controls
- Export filtered data to Excel

## Requirements
Install dependencies:

pip install -r requirements.txt

## Quick start — simple run commands ⚡

1. Use the Windows helper (recommended on Windows):

`run.bat [path\to\file]`

Examples:
- `run.bat` — launches GUI and prompts for a file
- `run.bat python_map\sample_data.csv` — launches GUI and loads sample data

2. PowerShell helper:

`.\run.ps1 [path\to\file]`

3. Unix / WSL helper (if applicable):

`./run.sh [path/to/file]`

4. Headless (creates HTML map without GUI):

`run-headless.bat path\to\file.csv` or `python python_map\app.py --headless path/to/file.csv`

5. Screenshot mode (captures a GUI screenshot to a PNG):

`run-screenshot.bat out.png [path\to\file]` or `python python_map\app.py --screenshot out.png path/to/file`

Notes:
- Supported input types: **CSV**, **Excel** (.xls/.xlsx). Column names for coordinates accepted: `Latitude`/`Longitude`, `lat`/`lon`/`lng` (case-insensitive).
- The GUI also allows field selection, multi-select filters (State/District/City), and exporting filtered data.

## Notes
- If your dataset does not include coordinates but does include an address column, you can pre-geocode addresses to add `Latitude` and `Longitude` columns.
- This is a starting point — further features like clickable rows to focus markers, clustering, or on-map filtering can be added.
