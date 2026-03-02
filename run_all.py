"""
run_all.py — Fleet Maintenance Report Refresh Script
=====================================================
Runs notebooks 02 through 06 in sequence to regenerate
the Fleet_Maintenance_Schedule.xlsx from updated raw data.

Usage:
    python run_all.py

Before running:
    1. Replace files in data/raw/ with updated exports
    2. Activate your virtual environment
    3. Run from the project root directory

Requirements (one-time install):
    pip install nbconvert


CODE TO RUN THIS SCRIPT:
cd C:\Users\jack.roberts\Documents\VSC - Python\Vehicle_Maintenance
.\venv\Scripts\activate
python run_all.py
"""

import subprocess
import sys
import os
import time
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

NOTEBOOKS = [
    ('02', 'notebooks/02_data_cleaning.ipynb'),
    ('03', 'notebooks/03_feature_engineering.ipynb'),
    ('04', 'notebooks/04_survival_analysis.ipynb'),
    ('05', 'notebooks/05_risk_classification.ipynb'),
    ('06', 'notebooks/06_maintenance_schedule_output.ipynb'),
]

OUTPUT_FILE = 'outputs/reports/Fleet_Maintenance_Schedule.xlsx'

RAW_FILES = [
    'Vehicle_Info.xlsx',
    'Vehicle_Driver.xlsx',
    'Vehicle_Mileage.xlsx',
    'Maintenance_Records.xlsx',
    'Driver_Scores.xlsx',
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def print_header():
    print()
    print('=' * 60)
    print('  Fleet Maintenance Report — Refresh Pipeline')
    print(f'  Started: {datetime.now().strftime("%d %B %Y %H:%M")}')
    print('=' * 60)
    print()

def run_notebook(notebook_path):
    """Execute a notebook in-place using nbconvert. Returns (success, stderr)."""
    cmd = [
        sys.executable, '-m', 'nbconvert',
        '--to', 'notebook',
        '--execute',
        '--inplace',
        '--ExecutePreprocessor.timeout=600',
        '--ExecutePreprocessor.kernel_name=vehicle_maintenance',
        notebook_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print_header()

    # Check working directory
    if not os.path.exists('data/raw'):
        print('ERROR: data/raw/ not found.')
        print('Run this script from the project root directory:')
        print('  cd C:\\Users\\jack.roberts\\Documents\\VSC - Python\\Vehicle_Maintenance')
        print('  python run_all.py')
        sys.exit(1)

    # Check raw data files
    missing = [f for f in RAW_FILES if not os.path.exists(f'data/raw/{f}')]
    if missing:
        print('ERROR: Missing raw data files in data/raw/:')
        for f in missing:
            print(f'  {f}')
        print('\nUpdate the raw files and try again.')
        sys.exit(1)

    print('  Raw data files confirmed. Running pipeline...')
    print()

    # Run each notebook in sequence
    total_start = time.time()

    for num, path in NOTEBOOKS:
        # Readable name from filename
        name = path.split('/')[-1].replace('.ipynb', '').split('_', 2)[-1].replace('_', ' ').title()
        print(f'  [ ] Notebook {num} — {name}', end='', flush=True)

        start = time.time()
        success, stderr = run_notebook(path)
        elapsed = time.time() - start

        status = 'OK' if success else 'FAILED'
        print(f'\r  [{"OK" if success else "!!"}] Notebook {num} — {name:<35} {elapsed:.0f}s')

        if not success:
            print()
            print(f'  Pipeline stopped at notebook {num}.')
            print('  Last error lines:')
            error_lines = [l for l in stderr.strip().split('\n') if l.strip()][-15:]
            for line in error_lines:
                print(f'    {line}')
            print()
            print('  Fix the error above and run again.')
            sys.exit(1)

    # Done
    total_elapsed = time.time() - total_start
    print()
    print('=' * 60)
    if os.path.exists(OUTPUT_FILE):
        size_kb = os.path.getsize(OUTPUT_FILE) / 1024
        print(f'  Done! Report generated in {total_elapsed:.0f}s')
        print(f'  {OUTPUT_FILE}  ({size_kb:.0f} KB)')
    else:
        print('  Pipeline complete but output file not found.')
        print(f'  Expected: {OUTPUT_FILE}')
    print(f'  Finished: {datetime.now().strftime("%d %B %Y %H:%M")}')
    print('=' * 60)
    print()

if __name__ == '__main__':
    main()
