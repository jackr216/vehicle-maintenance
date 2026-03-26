"""
run_all.py - Fleet Maintenance Report Refresh Script
=====================================================
Runs notebooks 02 through 06 in sequence to regenerate
the Fleet_Maintenance_Schedule.xlsx from updated raw data.

Usage:
    python run_all.py

Before running:
    1. Replace files in data/raw_anon/ with updated exports, then re-run anonymise_data.py
    2. Activate your virtual environment
    3. Run from the project root directory

Requirements (one-time install):
    pip install nbconvert
"""

import subprocess
import sys
import os
import time
from datetime import datetime

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

def run_notebook(notebook_path):
    cmd = [
    r'C:\Users\jack.roberts\Documents\VSC - Python\Vehicle_Maintenance\venv\Scripts\python.exe',
    '-m', 'nbconvert',
        '--to', 'notebook',
        '--execute',
        '--inplace',
        '--ExecutePreprocessor.timeout=600',
        '--ExecutePreprocessor.kernel_name=vehicle_maintenance',
        notebook_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def main():
    print()
    print('=' * 60)
    print('  Fleet Maintenance Report - Refresh Pipeline')
    print('  Started: {}'.format(datetime.now().strftime('%d %B %Y %H:%M')))
    print('=' * 60)
    print()

    if not os.path.exists('data/raw_anon'):
        print('ERROR: data/raw_anon/ not found.')
        print('Run from the project root directory.')
        sys.exit(1)

    missing = [f for f in RAW_FILES if not os.path.exists('data/raw_anon/{}'.format(f))]
    if missing:
        print('ERROR: Missing raw data files in data/raw_anon/:')
        for f in missing:
            print('  {}'.format(f))
        print('\nUpdate the raw files and try again.')
        sys.exit(1)

    print('  Raw data files confirmed. Running pipeline...')
    print()

    total_start = time.time()

    for num, path in NOTEBOOKS:
        name = path.split('/')[-1].replace('.ipynb', '').split('_', 2)[-1].replace('_', ' ').title()
        print('  [ ] Notebook {} - {}'.format(num, name), end='', flush=True)

        start = time.time()
        success, stderr = run_notebook(path)
        elapsed = time.time() - start

        status = 'OK' if success else '!!'
        print('\r  [{}] Notebook {} - {:<35} {:.0f}s'.format(status, num, name, elapsed))

        if not success:
            print()
            print('  Pipeline stopped at notebook {}.'.format(num))
            print('  Last error lines:')
            error_lines = [l for l in stderr.strip().split('\n') if l.strip()][-15:]
            for line in error_lines:
                print('    {}'.format(line))
            print()
            print('  Fix the error above and run again.')
            sys.exit(1)

    total_elapsed = time.time() - total_start
    print()
    print('=' * 60)
    if os.path.exists(OUTPUT_FILE):
        size_kb = os.path.getsize(OUTPUT_FILE) / 1024
        print('  Done! Report generated in {:.0f}s'.format(total_elapsed))
        print('  {}  ({:.0f} KB)'.format(OUTPUT_FILE, size_kb))
    else:
        print('  Pipeline complete but output file not found.')
        print('  Expected: {}'.format(OUTPUT_FILE))
    print('  Finished: {}'.format(datetime.now().strftime('%d %B %Y %H:%M')))
    print('=' * 60)
    print()

if __name__ == '__main__':
    main()
