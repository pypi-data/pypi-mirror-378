import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from cfc.manifest import SCHEMA_VERSION
from cfc.controller import ScanController
import queue
import threading
import time
from send2trash import send2trash
import shutil
import hashlib


def compute_hash(path: Path) -> str | None:
    h = hashlib.sha256()
    try:
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def run_cli():
    parser = argparse.ArgumentParser(description='Corrupted file scanner (CLI)')
    parser.add_argument('path', help='Folder to scan')
    parser.add_argument('--types', nargs='*', default=['.jpg','.jpeg','.png','.bmp','.gif','.tiff','.psd','.txt','.pdf','.docx','.xlsx','.pptx','.mp3'],
                        help='File extensions to include (default: common set)')
    parser.add_argument('--mode', choices=['preview','quarantine','delete'], default='preview', help='Action mode for corrupted files')
    parser.add_argument('--hash', action='store_true', help='Compute SHA-256 hashes for detected files')
    parser.add_argument('--manifest', action='store_true', help='Write manifest JSON when done')
    parser.add_argument('--export', metavar='REPORT', help='Write text report file of findings')
    parser.add_argument('--quiet', action='store_true', help='Less verbose output')
    parser.add_argument('--jsonl', metavar='LOG', help='Append detections to JSONL log file')
    args = parser.parse_args()

    folder = Path(args.path)
    if not folder.is_dir():
        print('Path is not a directory', file=sys.stderr)
        sys.exit(2)

    q: queue.Queue = queue.Queue()
    stop_flag = threading.Event()
    pause_flag = threading.Event()  # not used in CLI but kept for interface
    controller = ScanController()

    log_file = Path(args.jsonl) if args.jsonl else None
    lock = threading.Lock()

    def log_cb(rec: dict):
        if not log_file:
            return
        try:
            rec['ts'] = time.time()
            with lock:
                with log_file.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        except Exception:
            pass

    t_start = time.time()
    controller.scan(str(folder), args.types, stop_flag, pause_flag, q, log_cb)

    corrupted = []
    encrypted = []
    # Drain queue items produced by scan
    while True:
        try:
            kind, payload = q.get(timeout=0.1)
        except queue.Empty:
            # 'done' is the terminating event
            continue
        if kind == 'corrupted':
            corrupted.append(payload)
            if not args.quiet:
                print(f"[CORRUPTED] {payload['path']} :: {payload.get('reason','')}")
        elif kind == 'encrypted':
            encrypted.append(payload)
            if not args.quiet:
                print(f"[ENCRYPTED] {payload['path']} :: {payload.get('reason','')}")
        elif kind == 'done':
            elapsed = payload.get('elapsed', 0.0)
            if not args.quiet:
                print(f"Scan complete in {elapsed:.2f}s - {len(corrupted)} corrupted, {len(encrypted)} encrypted")
            break
        # ignore progress events for quiet mode simplicity

    # Hashing (optional)
    if args.hash:
        for rec in corrupted + encrypted:
            h = compute_hash(Path(rec['path']))
            rec['hash'] = h or ''
            if log_file:
                log_cb({'action':'hash','path':str(rec['path']),'hash':rec['hash']})

    # Action modes
    if corrupted and args.mode != 'preview':
        if args.mode == 'delete':
            deleted = 0
            for rec in corrupted:
                try:
                    send2trash(str(Path(rec['path']).resolve()))
                    deleted += 1
                except Exception:
                    pass
            if not args.quiet:
                print(f"Deleted {deleted} corrupted files")
        elif args.mode == 'quarantine':
            quarantine_root = folder / '_quarantine'
            quarantined = 0
            for rec in corrupted:
                p = Path(rec['path'])
                if not p.exists():
                    continue
                try:
                    rel = p.relative_to(folder)
                except Exception:
                    rel = Path(p.name)
                target = quarantine_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    stem = target.stem
                    suffix = target.suffix
                    idx = 1
                    while target.exists():
                        target = target.with_name(f"{stem}_{idx}{suffix}")
                        idx += 1
                try:
                    shutil.move(str(p), str(target))
                    quarantined += 1
                except Exception:
                    pass
            if not args.quiet:
                print(f"Quarantined {quarantined} corrupted files")

    # Manifest
    if args.manifest:
        manifest = {
            'folder': str(folder),
            'generated': datetime.now().isoformat(timespec='seconds'),
            'schema_version': SCHEMA_VERSION,
            'action_mode': args.mode,
            'counts': {
                'corrupted': len(corrupted),
                'encrypted': len(encrypted)
            },
            'items': []
        }
        for coll, kind in ((corrupted,'corrupted'), (encrypted,'encrypted')):
            for rec in coll:
                manifest['items'].append({
                    'path': str(rec['path']),
                    'kind': kind,
                    'reason': rec.get('reason'),
                    'size': rec.get('size'),
                    'hash': rec.get('hash')
                })
        name = f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(name).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        if not args.quiet:
            print(f"Manifest written: {name}")

    # Export text report
    if args.export:
        lines = [
            f"Corrupted Report Generated: {datetime.now().isoformat(timespec='seconds')}\n",
            f"Folder: {folder}\n",
            f"Encrypted: {len(encrypted)}  |  Corrupted: {len(corrupted)}\n"
        ]
        if encrypted:
            lines.append(f"=== Encrypted ({len(encrypted)}) ===\n")
            for rec in encrypted:
                lines.append(f"[ENC] {rec['path']}\t{rec.get('reason','')}\t{rec.get('size','')} bytes\n")
            lines.append('\n')
        if corrupted:
            lines.append(f"=== Corrupted ({len(corrupted)}) ===\n")
            for rec in corrupted:
                lines.append(f"[BAD] {rec['path']}\t{rec.get('reason','')}\t{rec.get('size','')} bytes\n")
        Path(args.export).write_text(''.join(lines), encoding='utf-8')
        if not args.quiet:
            print(f"Report exported: {args.export}")

    return 0


if __name__ == '__main__':
    raise SystemExit(run_cli())
