#!/usr/bin/env python
"""Export a template JSON containing union of all locale keys with empty string values.

Usage:
  python locale_export_template.py --out template_locale.json [--dir locales]

If no locales directory exists, exits with error.
"""
from __future__ import annotations
import json, argparse, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description='Export union-of-keys locale template')
    ap.add_argument('--dir', default='locales')
    ap.add_argument('--out', required=True, help='Output JSON path')
    args = ap.parse_args()
    d = Path(args.dir)
    if not d.exists():
        print(f"Locale directory not found: {d}", file=sys.stderr)
        sys.exit(2)
    keys = set()
    for fp in d.glob('*.json'):
        try:
            data = json.loads(fp.read_text(encoding='utf-8'))
            keys.update(data.keys())
        except Exception as e:
            print(f"WARN: Could not read {fp}: {e}")
    if not keys:
        print('No keys discovered.', file=sys.stderr)
        sys.exit(2)
    template = {k: "" for k in sorted(keys)}
    Path(args.out).write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Template written: {args.out} ({len(template)} keys)")

if __name__ == '__main__':
    main()
