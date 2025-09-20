from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Literal
import importlib.util, sys, inspect, zipfile, hashlib
from PIL import Image, UnidentifiedImageError
import pikepdf
from mutagen import File as MutagenFile

TEXT_READ_CHUNK = 1 * 1024 * 1024
StatusType = Literal['ok','corrupted','encrypted']

@dataclass
class DetectionResult:
    path: Path
    status: StatusType
    reason: str = ''
    size: int = 0
    sha256: str | None = None

class Detector(Protocol):
    name: str
    extensions: set[str]
    def analyze(self, path: Path) -> DetectionResult: ...

def hash_file(path: Path, algo='sha256', chunk_size=1024*512) -> str | None:
    h = hashlib.new(algo)
    try:
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

class ImageDetector:
    name = 'image'
    extensions = {'.jpg','.jpeg','.png','.bmp','.gif','.tiff','.psd'}
    def analyze(self, path: Path) -> DetectionResult:
        try:
            with Image.open(path) as img:
                img.verify()
            with Image.open(path) as img:
                img.load()
            return DetectionResult(path, 'ok', size=path.stat().st_size)
        except (UnidentifiedImageError, OSError) as e:
            msg = str(e).lower()
            if any(k in msg for k in ['cannot identify image file','truncated','corrupt','damaged']):
                return DetectionResult(path,'corrupted',reason=f'Image unreadable: {msg[:120]}', size=path.stat().st_size)
            return DetectionResult(path,'corrupted',reason=f'Image error: {msg[:120]}', size=path.stat().st_size)

class TextDetector:
    name = 'text'
    extensions = {'.txt'}
    encodings = ('utf-8','utf-8-sig','cp1252','latin-1')
    def analyze(self, path: Path) -> DetectionResult:
        try:
            data = path.read_bytes()[:TEXT_READ_CHUNK]
            for enc in self.encodings:
                try:
                    data.decode(enc)
                    return DetectionResult(path,'ok', size=path.stat().st_size)
                except UnicodeDecodeError:
                    continue
            return DetectionResult(path,'corrupted',reason='Text decode failure', size=path.stat().st_size)
        except Exception as e:
            return DetectionResult(path,'corrupted',reason=f'Text read error: {e}', size=path.stat().st_size)

class PdfDetector:
    name = 'pdf'
    extensions = {'.pdf'}
    def analyze(self, path: Path) -> DetectionResult:
        try:
            with pikepdf.Pdf.open(str(path)) as pdf:
                if pdf.is_encrypted:
                    return DetectionResult(path,'encrypted',reason='PDF is password protected', size=path.stat().st_size)
                _ = len(pdf.pages)
            return DetectionResult(path,'ok', size=path.stat().st_size)
        except pikepdf.PasswordError:
            return DetectionResult(path,'encrypted',reason='PDF is password protected', size=path.stat().st_size)
        except pikepdf.PdfError as e:  # generic structural/parse error
            return DetectionResult(path,'corrupted',reason=f'PDF error: {e}'[:160], size=path.stat().st_size)
        except Exception as e:
            return DetectionResult(path,'corrupted',reason=f'PDF error: {e}'[:160], size=path.stat().st_size)

class OoxmlDetector:
    name = 'ooxml'
    extensions = {'.docx','.xlsx','.pptx'}
    core_map = {
        '.docx':'word/document.xml',
        '.xlsx':'xl/workbook.xml',
        '.pptx':'ppt/presentation.xml'
    }
    def analyze(self, path: Path) -> DetectionResult:
        try:
            with zipfile.ZipFile(str(path),'r') as z:
                names = set(z.namelist())
                if 'EncryptedPackage' in names:
                    return DetectionResult(path,'encrypted',reason='OOXML password protected', size=path.stat().st_size)
                z.getinfo(self.core_map[path.suffix.lower()])
            return DetectionResult(path,'ok', size=path.stat().st_size)
        except KeyError:
            return DetectionResult(path,'corrupted',reason='OOXML missing core xml', size=path.stat().st_size)
        except Exception as e:
            msg = str(e)
            if 'password' in msg.lower():
                return DetectionResult(path,'encrypted',reason='OOXML password protected', size=path.stat().st_size)
            return DetectionResult(path,'corrupted',reason=f'OOXML error: {msg[:160]}', size=path.stat().st_size)

class Mp3Detector:
    name = 'mp3'
    extensions = {'.mp3'}
    def analyze(self, path: Path) -> DetectionResult:
        try:
            audio = MutagenFile(str(path))
            if audio is None:
                return DetectionResult(path,'corrupted',reason='Unreadable MP3 (no frames)', size=path.stat().st_size)
            return DetectionResult(path,'ok', size=path.stat().st_size)
        except Exception as e:
            return DetectionResult(path,'corrupted',reason=f'MP3 error: {e}'[:160], size=path.stat().st_size)

DETECTORS: list[Detector] = [
    ImageDetector(),
    TextDetector(),
    PdfDetector(),
    OoxmlDetector(),
    Mp3Detector(),
]

def _load_plugins():
    # Candidate plugin dirs: local working dir + user home.
    candidates = [Path('detectors_plugins')]
    try:
        home = Path.home() / '.cfc' / 'plugins'
        candidates.append(home)
    except Exception:
        pass
    seen: set[Path] = set()
    for plugins_dir in candidates:
        if not plugins_dir.is_dir():
            continue
        for py in plugins_dir.glob('*.py'):
            if py in seen:
                continue
            seen.add(py)
            try:
                spec = importlib.util.spec_from_file_location(py.stem, py)
                if not spec or not spec.loader:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"cfc_plugin_{py.stem}"] = module
                spec.loader.exec_module(module)  # type: ignore
                dets = getattr(module, 'DETECTORS', None)
                if dets:
                    for d in dets:
                        if hasattr(d,'extensions') and hasattr(d,'analyze') and d not in DETECTORS:
                            DETECTORS.append(d)
                for name, obj in inspect.getmembers(module):
                    if name == 'DETECTORS':
                        continue
                    if hasattr(obj, 'extensions') and hasattr(obj,'analyze') and obj not in DETECTORS:
                        DETECTORS.append(obj)
            except Exception:
                continue

_load_plugins()

SUFFIX_MAP = {}
for d in DETECTORS:
    for ext in d.extensions:
        SUFFIX_MAP[ext] = d

def get_detector(ext: str) -> Detector | None:
    return SUFFIX_MAP.get(ext.lower())