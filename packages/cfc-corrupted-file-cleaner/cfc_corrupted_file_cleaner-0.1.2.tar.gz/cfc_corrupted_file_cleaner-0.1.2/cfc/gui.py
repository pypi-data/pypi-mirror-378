"""GUI application (packaged FileCleanerApp)."""

from __future__ import annotations
import os, json, threading, subprocess, time, shutil, hashlib, io, queue, contextlib
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, Menu
from PIL import Image, UnidentifiedImageError
from send2trash import send2trash
from .controller import ScanController
from .manifest import SCHEMA_VERSION

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FileCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Corrupted File Cleaner")
        self.geometry("960x820")
        # State
        self.folder_path = ""
        self.corrupted_files: list[dict] = []
        self.encrypted_files: list[dict] = []
        self._lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self.scan_thread: threading.Thread | None = None
        self.progress_var = ctk.DoubleVar(value=0.0)
        self.total_files = 0
        self.scanned_files = 0
        self.result_queue: queue.Queue | None = None

        # Controller
        self.controller = ScanController()

        # Dynamic locale loading
        self.language_var = ctk.StringVar(value="English")
        self.translations: dict[str, dict] = {}
        self._load_locales()

        # UI Elements
        self.language_menu = ctk.CTkOptionMenu(
            self, values=list(self.translations.keys()), variable=self.language_var,
            command=lambda *_: self.update_ui_texts())
        self.language_menu.pack(pady=6)

        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(fill="x", padx=20, pady=(0,10))
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="")
        self.filter_label.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0,6))

        self.filetype_options = {
            "Images": ('.jpg','.jpeg','.png','.bmp','.gif','.tiff','.psd'),
            "Text":   ('.txt',),
            "PDF":    ('.pdf',),
            "Word":   ('.docx',),
            "Excel":  ('.xlsx',),
            "PowerPoint": ('.pptx',),
            "Audio":  ('.mp3',)
        }
        self.filetype_vars = {k: ctk.BooleanVar(value=True) for k in self.filetype_options}
        col = 0
        for label, var in self.filetype_vars.items():
            ctk.CTkCheckBox(self.filter_frame, text=label, variable=var).grid(row=1, column=col, padx=4, pady=2, sticky="w")
            col += 1

        self.dry_run_var = ctk.BooleanVar(value=True)
        self.dry_run_check = ctk.CTkCheckBox(self, text="Dry Run", variable=self.dry_run_var)
        self.dry_run_check.pack(pady=(0,6))

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=20, pady=(0,10))
        self.select_button = ctk.CTkButton(btn_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side="left", padx=5)
        self.scan_button = ctk.CTkButton(btn_frame, text="Scan", command=self.start_scan)
        self.scan_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(btn_frame, text="Stop", command=self.cancel_scan)
        self.stop_button.pack(side="left", padx=5)
        self.export_button = ctk.CTkButton(btn_frame, text="Export", command=self.export_report, state="disabled")
        self.export_button.pack(side="left", padx=5)

        # Action mode (Preview / Quarantine / Delete)
        self.action_mode_var = ctk.StringVar(value="preview")
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=20, pady=(0,6))
        self.mode_preview_rb = ctk.CTkRadioButton(mode_frame, text="Preview", variable=self.action_mode_var, value="preview")
        self.mode_quarantine_rb = ctk.CTkRadioButton(mode_frame, text="Quarantine", variable=self.action_mode_var, value="quarantine")
        self.mode_delete_rb = ctk.CTkRadioButton(mode_frame, text="Delete", variable=self.action_mode_var, value="delete")
        self.mode_preview_rb.pack(side="left", padx=4)
        self.mode_quarantine_rb.pack(side="left", padx=4)
        self.mode_delete_rb.pack(side="left", padx=4)

        # Hashing & manifest options
        opts_frame = ctk.CTkFrame(self)
        opts_frame.pack(fill="x", padx=20, pady=(0,6))
        self.hash_var = ctk.BooleanVar(value=False)
        self.manifest_var = ctk.BooleanVar(value=False)
        self.hash_check = ctk.CTkCheckBox(opts_frame, text="Hashes", variable=self.hash_var)
        self.manifest_check = ctk.CTkCheckBox(opts_frame, text="Manifest", variable=self.manifest_var)
        self.hash_check.pack(side="left", padx=4)
        self.manifest_check.pack(side="left", padx=4)

        # Quarantine folder path (under scanned root by default)
        self.quarantine_subdir = "_quarantine"

        # Live counts bar
        self.counts_label = ctk.CTkLabel(self, text="")
        self.counts_label.pack(fill="x", padx=20)

        self.progress = ctk.CTkProgressBar(self, variable=self.progress_var)
        self.progress.pack(fill="x", padx=20, pady=(0,10))

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20, pady=(0,6))
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.search_var.trace_add('write', lambda *_: self.display_files())
        self.pause_button = ctk.CTkButton(search_frame, text="Pause", width=80, command=self.toggle_pause)
        self.pause_button.pack(side="left")

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(fill="x", padx=20, pady=(0,10))

        # Results frame
        main_split = ctk.CTkFrame(self)
        main_split.pack(fill="both", expand=True, padx=20, pady=(0,10))
        self.scroll_container = ctk.CTkScrollableFrame(main_split, label_text="")
        self.scroll_container.pack(side="left", fill="both", expand=True, padx=(0,10))
        self.file_frame = self.scroll_container

        # Preview panel
        self.preview_panel = ctk.CTkFrame(main_split, width=320)
        self.preview_panel.pack(side="right", fill="y")
        self.preview_title = ctk.CTkLabel(self.preview_panel, text="Preview", font=("TkDefaultFont", 14, "bold"))
        self.preview_title.pack(fill="x", pady=(4,4))
        self.preview_meta = ctk.CTkLabel(self.preview_panel, text="", justify="left")
        self.preview_meta.pack(fill="x", padx=4)
        btn_row = ctk.CTkFrame(self.preview_panel)
        btn_row.pack(fill="x", pady=(4,4))
        self.preview_open_btn = ctk.CTkButton(btn_row, text="Open", command=self._preview_open, width=90)
        self.preview_open_btn.pack(side="left", padx=2)
        self.preview_copy_path_btn = ctk.CTkButton(btn_row, text="Copy Path", command=self._preview_copy_path, width=90)
        self.preview_copy_path_btn.pack(side="left", padx=2)
        self.preview_copy_hash_btn = ctk.CTkButton(btn_row, text="Copy Hash", command=self._preview_copy_hash, width=90)
        self.preview_copy_hash_btn.pack(side="left", padx=2)
        self.preview_textbox = ctk.CTkTextbox(self.preview_panel, height=300, wrap='word')
        self.preview_textbox.pack(fill="both", expand=True, padx=4, pady=(4,4))
        self.preview_image_label = ctk.CTkLabel(self.preview_panel, text="")
        self.preview_image_label.pack(fill="x", padx=4, pady=(2,4))
        self.current_preview_record = None

        # Settings & localization
        self._settings_path = Path("settings.json")
        self.log_path = Path("scan.log")
        self.update_ui_texts()
        self.load_settings()
        self.update_ui_texts()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._locale_mtimes: dict[Path, float] = {}
        self._init_locale_mtimes()
        self.after(1500, self._poll_locale_changes)

    # ---- Locale loading / hot reload ----
    def _load_locales(self):
        """Load locale files.

        Precedence order:
          1. Packaged locales bundled inside the cfc package (read-only)
          2. External overrides from a ./locales directory next to the executable

        External files with the same stem overwrite packaged ones, which allows
        users to customize translations without modifying the installation.
        """
        mapping = {'en':'English','tr':'Türkçe','ku':'Kurdî'}
        # First load packaged locales
        try:
            import importlib.resources as res
            with contextlib.suppress(Exception):
                pkg_files = list(res.files(__package__).joinpath('locales').glob('*.json'))  # type: ignore[attr-defined]
                for pf in pkg_files:
                    try:
                        data = json.loads(pf.read_text(encoding='utf-8'))
                        key = mapping.get(pf.stem.lower(), pf.stem)
                        self.translations.setdefault(key, data)  # don't override if already set by earlier call
                    except Exception:
                        continue
        except Exception:
            pass

        # Then load external overrides
        loc_dir = Path('locales')
        if loc_dir.exists():
            for fp in loc_dir.glob('*.json'):
                try:
                    data = json.loads(fp.read_text(encoding='utf-8'))
                    key = mapping.get(fp.stem.lower(), fp.stem)
                    self.translations[key] = data  # override packaged
                except Exception:
                    continue
        if 'English' not in self.translations and self.translations:
            some_key = next(iter(self.translations))
            self.translations['English'] = self.translations[some_key]

    def _init_locale_mtimes(self):
        # Only watch external override directory for changes (packaged files are read-only)
        loc_dir = Path('locales')
        self._locale_mtimes.clear()
        if not loc_dir.exists():
            return
        for fp in loc_dir.glob('*.json'):
            try:
                self._locale_mtimes[fp] = fp.stat().st_mtime
            except Exception:
                continue

    def _poll_locale_changes(self):
        changed = False
        loc_dir = Path('locales')
        if loc_dir.exists():
            for fp in loc_dir.glob('*.json'):
                try:
                    mt = fp.stat().st_mtime
                except Exception:
                    continue

                old = self._locale_mtimes.get(fp)
                if old is None:
                    changed = True
                    self._locale_mtimes[fp] = mt
                elif mt != old:
                    changed = True
                    self._locale_mtimes[fp] = mt
        if changed:
            prev_lang = self.language_var.get()
            # Rebuild translations from scratch to ensure removed override files revert to packaged versions
            self.translations.clear()
            self._load_locales()
            try:
                self.language_menu.configure(values=list(self.translations.keys()))
            except Exception:
                pass
            if prev_lang not in self.translations:
                self.language_var.set('English')
            self.update_ui_texts()
        self.after(1500, self._poll_locale_changes)

    def update_ui_texts(self):
        t = self.translations.get(self.language_var.get(), self.translations.get('English', {}))
        if not t:
            return
        self.filter_label.configure(text=t.get('mode','File-type Filter'))
        self.select_button.configure(text=t.get('select_folder','Select Folder'))
        self.scan_button.configure(text=t.get('scan','Scan'))
        self.stop_button.configure(text=t.get('stop','Stop'))
        self.pause_button.configure(text=t.get('pause','Pause'))
        self.export_button.configure(text=t.get('export','Export'))
        self.dry_run_check.configure(text=t.get('dry_run','Dry Run'))
        self.mode_preview_rb.configure(text=t.get('mode_preview','Preview Only'))
        self.mode_quarantine_rb.configure(text=t.get('mode_quarantine','Quarantine'))
        self.mode_delete_rb.configure(text=t.get('mode_delete','Delete Corrupted'))
        self.hash_check.configure(text=t.get('hashing','Compute Hashes'))
        self.manifest_check.configure(text=t.get('manifest','Write Manifest'))
        self.preview_title.configure(text=t.get('preview_panel','Preview'))
        self.preview_open_btn.configure(text=t.get('preview_open','Open Location'))
        self.preview_copy_path_btn.configure(text=t.get('preview_copy_path','Copy Path'))
        self.preview_copy_hash_btn.configure(text=t.get('preview_copy_hash','Copy Hash'))
        try:
            self.scroll_container.configure(label_text=t.get('results','Results'))
        except Exception:
            pass
        try:
            self.search_entry.configure(placeholder_text=t.get('filter_placeholder','Filter…'))
        except Exception:
            pass
        self.display_files()
        if not self.status_label.cget('text'):
            self.status_label.configure(text=t.get('status_no_folder','No folder selected.'))
        else:
            variants = {lang_dict.get('status_no_folder') for lang_dict in self.translations.values()}
            if self.status_label.cget('text') in variants:
                self.status_label.configure(text=t.get('status_no_folder','No folder selected.'))

    # ---- Settings ----
    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            t = self.translations[self.language_var.get()]
            self.status_label.configure(text=t.get('title_searching','Searching: {path}').format(path=path))
            self.counts_label.configure(text=t.get('counts_bar','Corrupted: {cor} | Encrypted: {enc}').format(cor=0, enc=0))

    def load_settings(self):
        try:
            if Path('settings.json').exists():
                data = json.loads(Path('settings.json').read_text(encoding='utf-8'))
                lang = data.get('language')
                if lang in self.translations:
                    self.language_var.set(lang)
                self.dry_run_var.set(bool(data.get('dry_run', True)))
                enabled = set(data.get('enabled_types', []))
                if enabled:
                    for k, var in self.filetype_vars.items():
                        var.set(k in enabled)
                self.action_mode_var.set(data.get('action_mode', 'preview'))
                self.hash_var.set(bool(data.get('hashing', False)))
                self.manifest_var.set(bool(data.get('manifest', False)))
        except Exception:
            pass

    def save_settings(self):
        try:
            data = {
                'language': self.language_var.get(),
                'dry_run': bool(self.dry_run_var.get()),
                'enabled_types': [k for k,v in self.filetype_vars.items() if v.get()],
                'action_mode': self.action_mode_var.get(),
                'hashing': bool(self.hash_var.get()),
                'manifest': bool(self.manifest_var.get()),
            }
            Path('settings.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception:
            pass

    def on_close(self):
        self.save_settings()
        self.destroy()

    # ---- Control ----
    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return
        if not self.folder_path:
            t = self.translations[self.language_var.get()]
            self.status_label.configure(text=t['status_no_folder'])
            return
        self.stop_flag.clear()
        self.pause_flag.clear()
        self.progress_var.set(0)
        self.total_files = 0
        self.scanned_files = 0
        self.corrupted_files.clear()
        self.encrypted_files.clear()
        self.scan_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.result_queue = queue.Queue()
        self.scan_thread = threading.Thread(target=self.scan_files, daemon=True)
        self.scan_thread.start()
        self.after(100, self._drain_queue_periodic)
        t = self.translations[self.language_var.get()]
        self.counts_label.configure(text=t.get('counts_bar','Corrupted: {cor} | Encrypted: {enc}').format(cor=0, enc=0))

    def cancel_scan(self):
        self.stop_flag.set()

    def toggle_pause(self):
        if not self.scan_thread or not self.scan_thread.is_alive():
            return
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            self.pause_button.configure(text="Pause")
        else:
            self.pause_flag.set()
            self.pause_button.configure(text="Resume")

    # ---- Scanning ----
    def scan_files(self):
        t = self.translations[self.language_var.get()]
        if self.result_queue:
            self.result_queue.put(('reset_ui', t['status_scanning']))
        allowed = []
        for cat, exts in self.filetype_options.items():
            if self.filetype_vars[cat].get():
                allowed.extend(exts)
        self.controller.scan(self.folder_path, allowed, self.stop_flag, self.pause_flag, self.result_queue, self.log_detection)

    # ---- Display ----
    def display_files(self):
        self.clear_file_frame()
        term = self.search_var.get().strip().lower()
        def match(item):
            if not term:
                return True
            return term in str(item['path']).lower() or term in str(item.get('reason','')).lower()
        t = self.translations[self.language_var.get()]
        if self.encrypted_files:
            hdr = ctk.CTkLabel(self.file_frame, text=t['hdr_encrypted'].format(count=len(self.encrypted_files)), anchor='w')
            hdr.pack(fill='x', padx=5, pady=(4,2))
            for it in self.encrypted_files:
                if not match(it):
                    continue
                self._add_file_row(it, kind='encrypted')
        if self.corrupted_files:
            hdr2 = ctk.CTkLabel(self.file_frame, text=t['hdr_corrupted'].format(count=len(self.corrupted_files)), anchor='w')
            hdr2.pack(fill='x', padx=5, pady=(4,2))
            for it in self.corrupted_files:
                if not match(it):
                    continue
                self._add_file_row(it, kind='corrupted')

    def clear_file_frame(self):
        for w in self.file_frame.winfo_children():
            try: w.destroy()
            except Exception: pass

    def _add_file_row(self, rec: dict, kind: str):
        frame = ctk.CTkFrame(self.file_frame)
        frame.pack(fill='x', padx=5, pady=2)
        lbl = ctk.CTkLabel(frame, text=os.path.basename(str(rec['path'])), anchor='w')
        lbl.pack(side='left', fill='x', expand=True)
        reason = ctk.CTkLabel(frame, text=rec.get('reason',''), text_color=('red' if kind=='corrupted' else 'orange'))
        reason.pack(side='left', padx=6)
        def on_click(event=None, r=rec):
            self.show_preview(r)
        lbl.bind('<Button-1>', on_click)
        lbl.bind('<Double-Button-1>', lambda e, p=rec['path']: self._open_explorer(p))
        reason.bind('<Button-1>', on_click)

    # ---- Preview panel ----
    def show_preview(self, rec: dict):
        self.current_preview_record = rec
        self.preview_textbox.delete('1.0','end')
        self.preview_image_label.configure(image=None, text='')
        p = Path(rec['path'])
        size = rec.get('size','')
        hashv = rec.get('hash','') or ''
        meta_lines = [f"Path: {p}", f"Size: {size}"]
        if hashv:
            meta_lines.append(f"SHA256: {hashv}")
        self.preview_meta.configure(text='\n'.join(meta_lines))
        # If image attempt to display
        if p.suffix.lower() in ('.jpg','.jpeg','.png','.bmp','.gif','.tiff') and p.exists():
            try:
                from PIL import ImageTk
                with Image.open(p) as img:
                    img.thumbnail((300,300))
                    tk_img = ImageTk.PhotoImage(img)
                self.preview_image_label.configure(image=tk_img)
                self.preview_image_label.image = tk_img
            except Exception:
                pass
        # If text attempt partial read
        elif p.suffix.lower() in ('.txt','.log','.md') and p.exists():
            try:
                data = p.read_bytes()[:8192]
                for enc in ('utf-8','utf-8-sig','cp1252','latin-1'):
                    try:
                        txt = data.decode(enc)
                        self.preview_textbox.insert('end', txt)
                        break
                    except Exception:
                        continue
            except Exception:
                pass
        else:
            # hex dump first 256 bytes
            try:
                raw = p.read_bytes()[:256]
                hex_lines = []
                for i in range(0,len(raw),16):
                    chunk = raw[i:i+16]
                    hex_part = ' '.join(f"{b:02X}" for b in chunk)
                    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                    hex_lines.append(f"{i:04X}  {hex_part:<47}  {ascii_part}")
                self.preview_textbox.insert('end','\n'.join(hex_lines))
            except Exception:
                pass

    def _open_explorer(self, path):
        try:
            if os.name == 'nt':
                subprocess.Popen(['explorer', '/select,', str(Path(path).resolve())])
            else:
                subprocess.Popen(['xdg-open', str(Path(path).parent)])
        except Exception:
            pass

    def _preview_open(self):
        if self.current_preview_record:
            self._open_explorer(self.current_preview_record['path'])

    def _preview_copy_path(self):
        if self.current_preview_record:
            self.clipboard_clear()
            self.clipboard_append(str(self.current_preview_record['path']))

    def _preview_copy_hash(self):
        if self.current_preview_record and self.current_preview_record.get('hash'):
            self.clipboard_clear()
            self.clipboard_append(str(self.current_preview_record['hash']))

    # ---- Queue / logging ----
    def _drain_queue_periodic(self):
        if not self.result_queue:
            return
        updated = False
        while True:
            try:
                kind, payload = self.result_queue.get_nowait()
            except queue.Empty:
                break
            if kind == 'progress':
                self.progress_var.set(payload['ratio'])
                self.scanned_files = payload.get('scanned', self.scanned_files)
                self.total_files = payload.get('total', self.total_files)
            elif kind == 'corrupted':
                self.corrupted_files.append(payload)
                updated = True
            elif kind == 'encrypted':
                self.encrypted_files.append(payload)
                updated = True
            elif kind == 'reset_ui':
                self.status_label.configure(text=payload)
            elif kind == 'done':
                t = self.translations[self.language_var.get()]
                if self.stop_flag.is_set():
                    self.status_label.configure(text=t.get('status_stopped','Scan stopped.'))
                else:
                    self.status_label.configure(text=t.get('status_done','Scan complete.'))
                self.scan_button.configure(state="normal")
                # Post-scan actions
                if self.corrupted_files and self.action_mode_var.get() != 'preview':
                    self._apply_action_mode()
                # Hashing & manifest after actions (so manifest reflects final paths for quarantine)
                if self.hash_var.get() or self.manifest_var.get():
                    self._post_scan_hash_manifest()
                self.export_button.configure(state="normal")
                break
        if updated:
            t = self.translations[self.language_var.get()]
            self.counts_label.configure(text=t.get('counts_bar','Corrupted: {cor} | Encrypted: {enc}').format(cor=len(self.corrupted_files), enc=len(self.encrypted_files)))
            self.display_files()
        if self.scan_thread and self.scan_thread.is_alive():
            self.after(200, self._drain_queue_periodic)

    def log_detection(self, rec: dict):
        try:
            rec_out = dict(rec)
            rec_out['ts'] = time.time()
            with self._lock:
                with self.log_path.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(rec_out, ensure_ascii=False) + '\n')
        except Exception:
            pass

    def _apply_action_mode(self):
        mode = self.action_mode_var.get()
        if mode == 'delete':
            for rec in list(self.corrupted_files):
                p = Path(rec['path'])
                if not p.exists():
                    continue
                try:
                    send2trash(str(p.resolve()))
                except Exception:
                    pass
        elif mode == 'quarantine':
            root = Path(self.folder_path)
            qroot = root / self.quarantine_subdir
            for rec in list(self.corrupted_files):
                p = Path(rec['path'])
                if not p.exists():
                    continue
                try:
                    rel = p.relative_to(root)
                except Exception:
                    rel = Path(p.name)
                target = qroot / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    stem, suf = target.stem, target.suffix
                    idx = 1
                    while target.exists():
                        target = target.with_name(f"{stem}_{idx}{suf}")
                        idx += 1
                try:
                    shutil.move(str(p), str(target))
                    rec['path'] = target
                except Exception:
                    pass

    def _post_scan_hash_manifest(self):
        if self.hash_var.get():
            for coll in (self.corrupted_files, self.encrypted_files):
                for rec in coll:
                    if not rec.get('hash'):
                        h = self._hash_file(Path(rec['path']))
                        rec['hash'] = h or ''
        if self.manifest_var.get():
            manifest = {
                'folder': self.folder_path,
                'generated': datetime.now().isoformat(timespec='seconds'),
                'schema_version': SCHEMA_VERSION,
                'action_mode': self.action_mode_var.get(),
                'counts': {
                    'corrupted': len(self.corrupted_files),
                    'encrypted': len(self.encrypted_files)
                },
                'items': []
            }
            for coll, kind in ((self.corrupted_files,'corrupted'), (self.encrypted_files,'encrypted')):
                for rec in coll:
                    manifest['items'].append({
                        'path': str(rec['path']),
                        'kind': kind,
                        'reason': rec.get('reason'),
                        'size': rec.get('size'),
                        'hash': rec.get('hash','')
                    })
            name = f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                Path(name).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            except Exception:
                pass

    def _hash_file(self, path: Path) -> str | None:
        h = hashlib.sha256()
        try:
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def export_report(self):
        t = self.translations[self.language_var.get()]
        lines = [
            f"Corrupted Report Generated: {datetime.now().isoformat(timespec='seconds')}\n",
            f"Folder: {self.folder_path}\n",
            f"Encrypted: {len(self.encrypted_files)}  |  Corrupted: {len(self.corrupted_files)}\n"
        ]
        if self.encrypted_files:
            lines.append(f"=== Encrypted ({len(self.encrypted_files)}) ===\n")
            for rec in self.encrypted_files:
                lines.append(f"[ENC] {rec['path']}\t{rec.get('reason','')}\t{rec.get('size','')} bytes\n")
            lines.append('\n')
        if self.corrupted_files:
            lines.append(f"=== Corrupted ({len(self.corrupted_files)}) ===\n")
            for rec in self.corrupted_files:
                lines.append(f"[BAD] {rec['path']}\t{rec.get('reason','')}\t{rec.get('size','')} bytes\n")
        export_name = f"corrupted_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            Path(export_name).write_text(''.join(lines), encoding='utf-8')
            self.status_label.configure(text=t.get('status_exported','Exported report: {name}').format(name=export_name))
        except Exception:
            pass

    def log_detection(self, rec: dict):  # duplicate name kept intentionally (GUI logging)
        try:
            rec_out = dict(rec)
            rec_out['ts'] = time.time()
            with self._lock:
                with self.log_path.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(rec_out, ensure_ascii=False) + '\n')
        except Exception:
            pass

def main():  # GUI entry point
    app = FileCleanerApp()
    app.mainloop()

__all__ = ["FileCleanerApp","main"]
