#!/usr/bin/env python
"""Restore quarantined files back to original locations using a manifest.

Usage:
  python restore_from_manifest.py --manifest manifest_20250919_123456.json [--dry-run]

Behavior:
  - For each item with 'quarantined_path' and original 'path' different, move file back if original path absent.
  - Creates parent directories as needed.
  - Skips if original path already exists (reports conflict).
  - Honors --dry-run (no changes, just report planned moves).

Exit codes:
  0 success, 2 error.
"""
from __future__ import annotations
import json, argparse, sys, shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Restore quarantined files from manifest")
    ap.add_argument('--manifest', required=True, help='Manifest JSON path')
    ap.add_argument('--dry-run', action='store_true', help='Show actions only')
    args = ap.parse_args()

    mp = Path(args.manifest)
    try:
        data = json.loads(mp.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"ERROR reading manifest: {e}", file=sys.stderr)
        sys.exit(2)

    items = data.get('items', [])
    planned = 0
    restored = 0
    conflicts = 0
    missing = 0

    for it in items:
        q = it.get('quarantined_path')
        orig = it.get('path')
        if not q or not orig:
            continue
        q_path = Path(q)
        o_path = Path(orig)
        if not q_path.exists():
            missing += 1
            print(f"MISSING quarantine file: {q}")
            continue
        if o_path.exists():
            conflicts += 1
            print(f"CONFLICT original exists: {orig}")
            continue
        planned += 1
        print(f"RESTORE {q}  ->  {orig}")
        if not args.dry_run:
            try:
                o_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(q_path), str(o_path))
                restored += 1
            except Exception as e:
                print(f"ERROR restoring {q}: {e}")

    print("=== Restore Summary ===")
    print(f"Planned: {planned} | Restored: {restored} | Conflicts: {conflicts} | Missing: {missing}")
    if args.dry_run:
        print("(dry run - no changes applied)")

if __name__ == '__main__':
    main()
