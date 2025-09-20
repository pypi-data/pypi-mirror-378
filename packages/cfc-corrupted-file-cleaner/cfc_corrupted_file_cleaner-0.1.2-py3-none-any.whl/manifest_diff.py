#!/usr/bin/env python
"""Compare two manifest JSON files and report differences.

Usage:
  python manifest_diff.py --old manifest_old.json --new manifest_new.json [--json out.json]

Output (human):
  - Summary counts
  - Added corrupted/encrypted items (path)
  - Removed items
  - Hash changes (old -> new)

Exit codes:
  0 success (even if differences found)
  2 error (bad arguments or IO)
"""
from __future__ import annotations
import json, argparse, sys, hashlib
from pathlib import Path
from typing import Dict, Any


def load_manifest(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"ERROR reading {path}: {e}", file=sys.stderr)
        sys.exit(2)


def index_items(m: Dict[str, Any]):
    idx = {}
    for item in m.get('items', []):
        idx[item.get('path')] = item
    return idx


def main():
    ap = argparse.ArgumentParser(description="Diff two manifest JSON snapshots.")
    ap.add_argument('--old', required=True, help='Older (baseline) manifest JSON')
    ap.add_argument('--new', required=True, help='Newer manifest JSON')
    ap.add_argument('--json', help='Optional write JSON diff summary file')
    args = ap.parse_args()

    old = load_manifest(Path(args.old))
    new = load_manifest(Path(args.new))

    old_idx = index_items(old)
    new_idx = index_items(new)

    added = []
    removed = []
    changed_hash = []

    for path, it in new_idx.items():
        if path not in old_idx:
            added.append(it)
        else:
            prev = old_idx[path]
            if prev.get('hash') and it.get('hash') and prev.get('hash') != it.get('hash'):
                changed_hash.append({'path': path, 'old_hash': prev.get('hash'), 'new_hash': it.get('hash')})

    for path in old_idx:
        if path not in new_idx:
            removed.append(old_idx[path])

    summary = {
        'old_counts': old.get('counts'),
        'new_counts': new.get('counts'),
        'added': added,
        'removed': removed,
        'changed_hash': changed_hash,
        'added_count': len(added),
        'removed_count': len(removed),
        'changed_hash_count': len(changed_hash)
    }

    # Human output
    print("=== Manifest Diff Summary ===")
    print(f"Old corrupted: {old.get('counts',{}).get('corrupted')} | New corrupted: {new.get('counts',{}).get('corrupted')}")
    print(f"Old encrypted: {old.get('counts',{}).get('encrypted')} | New encrypted: {new.get('counts',{}).get('encrypted')}")
    print(f"Added: {len(added)} | Removed: {len(removed)} | Hash changes: {len(changed_hash)}")
    if added:
        print("-- Added Items --")
        for a in added:
            print(f"+ {a.get('kind')} {a.get('path')} ({a.get('reason','')})")
    if removed:
        print("-- Removed Items --")
        for r in removed:
            print(f"- {r.get('kind')} {r.get('path')} ({r.get('reason','')})")
    if changed_hash:
        print("-- Hash Changes --")
        for ch in changed_hash:
            print(f"* {ch['path']}\n    old: {ch['old_hash']}\n    new: {ch['new_hash']}")

    if args.json:
        try:
            Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"JSON diff written: {args.json}")
        except Exception as e:
            print(f"ERROR writing JSON diff: {e}", file=sys.stderr)
            sys.exit(2)

if __name__ == '__main__':
    main()
