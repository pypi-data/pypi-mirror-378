import json
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import sys

"""Analyze scan.log JSONL file and summarize detections.

Outputs:
 - Total records
 - Counts by status (encrypted / corrupted / other)
 - Top reasons (truncated to first 60 chars) for corrupted
 - Per-extension statistics (counts per status)
Optionally emit JSON via --json for programmatic use.
"""

def load_records(path: Path):
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue

def main():
    ap = argparse.ArgumentParser(description='Analyze scan.log (JSONL)')
    ap.add_argument('--log', default='scan.log', help='Path to log file (default scan.log)')
    ap.add_argument('--json', action='store_true', help='Emit JSON summary instead of text table')
    ap.add_argument('--top', type=int, default=10, help='Top N reasons (default 10)')
    args = ap.parse_args()

    p = Path(args.log)
    if not p.exists():
        print('Log file not found', file=sys.stderr)
        return 2

    status_counter = Counter()
    reason_counter = Counter()
    ext_status = defaultdict(lambda: Counter())
    total = 0

    for rec in load_records(p):
        total += 1
        status = rec.get('status') or rec.get('action') or 'unknown'
        status_counter[status] += 1
        path_str = str(rec.get('path',''))
        # Extract extension if path present
        ext = ''
        if path_str:
            dot = path_str.rfind('.')
            if dot != -1 and dot < len(path_str)-1:
                ext = path_str[dot:].lower()
        if ext:
            ext_status[ext][status] += 1
        # Reasons only for corrupted status
        if status == 'corrupted':
            reason = (rec.get('reason') or '').strip()
            if reason:
                # Collapse to at most 60 chars for grouping
                reason_counter[reason[:60]] += 1

    summary = {
        'total_records': total,
        'counts_by_status': dict(status_counter),
        'top_reasons': reason_counter.most_common(args.top),
        'per_extension': {ext: dict(cnt) for ext, cnt in sorted(ext_status.items(), key=lambda kv: kv[0])}
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Total records: {summary['total_records']}")
    print('\nCounts by status:')
    for k,v in summary['counts_by_status'].items():
        print(f"  {k:12} {v}")
    print('\nTop reasons:')
    for reason, cnt in summary['top_reasons']:
        print(f"  {cnt:4}  {reason}")
    print('\nPer-extension counts:')
    for ext, cnts in summary['per_extension'].items():
        line = ', '.join(f"{k}={v}" for k,v in cnts.items())
        print(f"  {ext}: {line}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
