"""
anonymise_data.py — Raw Data Anonymisation Script
==================================================
Reads the five raw data files from data/raw/ and writes
anonymised versions to data/raw_anon/.

What gets anonymised:
  - Registration numbers  → VAN_001, VAN_002 etc
  - Driver names          → Driver_001, Driver_002 etc
  - Branch names          → Branch_A, Branch_B etc

What stays the same:
  - All numeric columns (mileage, costs, scores, dates)
  - Vehicle make, model, asset type
  - All other columns

Usage:
    python anonymise_data.py

Run from the project root directory.
"""

import pandas as pd
import numpy as np
import os
import re

RAW_DIR  = 'data/raw/'
ANON_DIR = 'data/raw_anon/'

# ── Build lookup tables ────────────────────────────────────────────────────────

def build_registration_lookup(file_paths):
    """Collect all unique registrations across all files and assign VAN_XXX codes."""
    all_regs = set()
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            # Find registration column — handles different capitalisation
            reg_col = next((c for c in df.columns if 'registration' in c.lower()), None)
            if reg_col:
                all_regs.update(df[reg_col].dropna().unique())
        except Exception:
            pass

    sorted_regs = sorted(all_regs)
    return {reg: f'VAN_{str(i+1).zfill(3)}' for i, reg in enumerate(sorted_regs)}


def build_driver_lookup(file_paths):
    """Collect all unique driver names across all files and assign Driver_XXX codes."""
    all_drivers = set()
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            driver_col = next((c for c in df.columns if 'driver' in c.lower() and 'score' not in c.lower()), None)
            if driver_col:
                all_drivers.update(df[driver_col].dropna().unique())
        except Exception:
            pass

    sorted_drivers = sorted(all_drivers)
    return {driver: f'Driver_{str(i+1).zfill(3)}' for i, driver in enumerate(sorted_drivers)}


def build_branch_lookup(file_paths):
    """Collect all unique branch names across all files and assign Branch_X codes."""
    all_branches = set()
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            branch_col = next((c for c in df.columns if 'branch' in c.lower()), None)
            if branch_col:
                all_branches.update(df[branch_col].dropna().unique())
        except Exception:
            pass

    sorted_branches = sorted(all_branches)
    # Use letters for branches: Branch_A, Branch_B etc
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if len(sorted_branches) <= 26:
        return {branch: f'Branch_{letters[i]}' for i, branch in enumerate(sorted_branches)}
    else:
        return {branch: f'Branch_{str(i+1).zfill(2)}' for i, branch in enumerate(sorted_branches)}


# ── Anonymise each file ────────────────────────────────────────────────────────

def anonymise_df(df, reg_lookup, driver_lookup, branch_lookup):
    """Apply anonymisation lookups to a dataframe."""
    df = df.copy()

    for col in df.columns:
        col_lower = col.lower()

        if 'registration' in col_lower:
            df[col] = df[col].map(lambda x: reg_lookup.get(x, x) if pd.notna(x) else x)

        elif 'driver' in col_lower and 'score' not in col_lower:
            df[col] = df[col].map(lambda x: driver_lookup.get(x, x) if pd.notna(x) else x)

        elif 'branch' in col_lower:
            df[col] = df[col].map(lambda x: branch_lookup.get(x, x) if pd.notna(x) else x)

    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print()
    print('=' * 55)
    print('  Data Anonymisation Script')
    print('=' * 55)
    print()

    # Check raw directory exists
    if not os.path.exists(RAW_DIR):
        print(f'ERROR: {RAW_DIR} not found.')
        print('Run from the project root directory.')
        return

    # Find all Excel files in raw/
    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.xlsx')]
    if not raw_files:
        print(f'ERROR: No .xlsx files found in {RAW_DIR}')
        return

    file_paths = [os.path.join(RAW_DIR, f) for f in raw_files]
    print(f'  Found {len(raw_files)} raw files:')
    for f in raw_files:
        print(f'    {f}')
    print()

    # Build lookup tables from all files combined
    print('  Building anonymisation lookups...')
    reg_lookup    = build_registration_lookup(file_paths)
    driver_lookup = build_driver_lookup(file_paths)
    branch_lookup = build_branch_lookup(file_paths)

    print(f'    Registrations: {len(reg_lookup):,} unique → VAN_001 to VAN_{len(reg_lookup):03d}')
    print(f'    Drivers:       {len(driver_lookup):,} unique → Driver_001 to Driver_{len(driver_lookup):03d}')
    print(f'    Branches:      {len(branch_lookup):,} unique → Branch_A to Branch_{chr(64+len(branch_lookup)) if len(branch_lookup) <= 26 else str(len(branch_lookup))}')
    print()

    # Create output directory
    os.makedirs(ANON_DIR, exist_ok=True)

    # Process each file
    print('  Anonymising files...')
    for filename in raw_files:
        input_path  = os.path.join(RAW_DIR, filename)
        output_path = os.path.join(ANON_DIR, filename)

        try:
            # Read — use sheet_name=None to preserve all sheets
            sheets = pd.read_excel(input_path, sheet_name=None)
            anon_sheets = {}

            for sheet_name, df in sheets.items():
                anon_sheets[sheet_name] = anonymise_df(df, reg_lookup, driver_lookup, branch_lookup)

            # Write
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in anon_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            total_rows = sum(len(df) for df in anon_sheets.values())
            print(f'    [OK] {filename:<40} ({total_rows:,} rows)')

        except Exception as e:
            print(f'    [!!] {filename:<40} ERROR: {e}')

    # Save lookup tables for reference
    lookup_path = os.path.join(RAW_DIR, '_lookup_tables.xlsx')
    with pd.ExcelWriter(lookup_path, engine='openpyxl') as writer:
        pd.DataFrame(list(reg_lookup.items()),    columns=['Original', 'Anonymised']).to_excel(writer, sheet_name='Registrations', index=False)
        pd.DataFrame(list(driver_lookup.items()), columns=['Original', 'Anonymised']).to_excel(writer, sheet_name='Drivers',       index=False)
        pd.DataFrame(list(branch_lookup.items()), columns=['Original', 'Anonymised']).to_excel(writer, sheet_name='Branches',       index=False)

    print()
    print(f'  Lookup tables saved to: {lookup_path}')
    print('  (Keep this file private — it maps real data to anonymised codes)')
    print()
    print('=' * 55)
    print('  Done! Anonymised files written to data/raw_anon/')
    print()
    print('  Next steps:')
    print('  1. Check the files in data/raw_anon/ look correct')
    print('  2. Add data/raw/ and data/raw_anon/_lookup_tables.xlsx')
    print('     to .gitignore')
    print('  3. Push data/raw_anon/ (without the lookup) to GitHub')
    print('=' * 55)
    print()

if __name__ == '__main__':
    main()
