#!/usr/bin/env python
"""Validate locale JSON files for key consistency.

Usage:
  python locale_validate.py [--dir locales]

Reports:
  - Master key set (union)
  - Missing keys per locale
  - Extra keys per locale
Exit code 1 if any missing keys.
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path

def load(dir_path: Path):
    locs = {}
    for fp in dir_path.glob('*.json'):
        try:
            locs[fp.stem] = json.loads(fp.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"ERROR reading {fp}: {e}")
    return locs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='locales', help='Locale directory path')
    args = ap.parse_args()
    d = Path(args.dir)
    if not d.exists():
        print(f"Directory not found: {d}")
        sys.exit(2)
    locs = load(d)
    if not locs:
        print('No locale files found.')
        sys.exit(2)
    all_keys = set()
    for data in locs.values():
        all_keys.update(data.keys())
    print(f"Total master keys: {len(all_keys)}")
    missing_any = False
    for name, data in locs.items():
        missing = sorted(all_keys - set(data.keys()))
        extra = sorted(set(data.keys()) - all_keys)
        if missing:
            missing_any = True
        print(f"Locale {name}: {len(missing)} missing, {len(extra)} extra")
        if missing:
            print('  Missing:', ', '.join(missing))
        if extra:
            print('  Extra:', ', '.join(extra))
    if missing_any:
        print('Validation FAILED: missing keys present.')
        sys.exit(1)
    else:
        print('Validation OK: no missing keys.')

if __name__ == '__main__':
    main()
