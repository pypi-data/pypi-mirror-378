import os
import time
from pathlib import Path
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Sequence, Callable
from .detectors import get_detector, DetectionResult

class ScanController:
    """Headless scanning/controller logic (packaged version)."""
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers
        self.total_files: int = 0
        self.scanned_files: int = 0

    def scan(self,
             folder_path: str,
             allowed_exts: Sequence[str],
             stop_flag,
             pause_flag,
             result_queue: Queue,
             log_callback: Callable[[dict], None] | None = None):
        start = time.time()
        self.scanned_files = 0
        self.total_files = 0
        allowed = {e.lower() for e in allowed_exts}
        candidates: list[Path] = []
        for root, _, files in os.walk(folder_path):
            if stop_flag.is_set():
                break
            for fname in files:
                p = Path(root) / fname
                if p.suffix.lower() in allowed and not p.name.startswith('._'):
                    candidates.append(p)
        self.total_files = len(candidates)
        if self.total_files == 0:
            result_queue.put(('progress', {'ratio': 1.0, 'scanned': 0, 'total': 0}))

        max_workers = self.max_workers or min(8, max(2, (os.cpu_count() or 4)))

        def _analyze(p: Path):
            if stop_flag.is_set():
                return None
            det = get_detector(p.suffix.lower())
            if not det:
                return None
            try:
                return det.analyze(p)
            except Exception as e:
                size = 0
                try:
                    size = p.stat().st_size
                except Exception:
                    pass
                from .detectors import DetectionResult as DR
                return DR(p, 'corrupted', reason=f'Unhandled detector error: {e}', size=size)

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='scan') as pool:
            futures = [pool.submit(_analyze, p) for p in candidates]
            for fut in as_completed(futures):
                if stop_flag.is_set():
                    break
                while pause_flag.is_set() and not stop_flag.is_set():
                    time.sleep(0.1)
                result = fut.result()
                self.scanned_files += 1
                ratio = (self.scanned_files / self.total_files) if self.total_files else 1.0
                result_queue.put(('progress', {
                    'ratio': ratio,
                    'scanned': self.scanned_files,
                    'total': self.total_files
                }))
                if not result:
                    continue
                rec = {
                    'path': result.path,
                    'reason': result.reason,
                    'size': result.size,
                    'hash': ''
                }
                if result.status == 'encrypted':
                    result_queue.put(('encrypted', rec))
                    if log_callback:
                        log_callback({'status': 'encrypted', **{k: str(v) if k == 'path' else v for k, v in rec.items()}})
                elif result.status == 'corrupted':
                    result_queue.put(('corrupted', rec))
                    if log_callback:
                        log_callback({'status': 'corrupted', **{k: str(v) if k == 'path' else v for k, v in rec.items()}})

        result_queue.put(('done', {
            'elapsed': time.time() - start,
            'stopped': stop_flag.is_set()
        }))