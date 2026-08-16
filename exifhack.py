#!/usr/bin/env python3
"""
EXIFHACK v2.1 - Metadata Forensic Suite (ExifTool-compatible)
A hacker-themed forensic metadata viewer and cleaner built with Python & Tkinter.

Copyright (c) 2026 R4in8ow
Author: R4in8ow
Contact: https://www.facebook.com/R4in8owLay
"""

import os
import sys
import json
import shutil
import datetime
import subprocess
import threading
import webbrowser
import io
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

__author__ = "R4in8ow"
__author_link__ = "https://www.facebook.com/R4in8owLay"

# Thumbnail preview support
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class ExifHackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EXIFHACK // Metadata Forensic Suite — by R4in8ow")
        self.root.geometry("1120x760")
        self.root.minsize(850, 520)
        self.root.configure(bg="#050a05")

        # State Variables
        self.files_data = []
        self.current_selected_file = None
        self.exiftool_path = shutil.which("exiftool")

        # Cyberpunk / Retro Terminal Color Palette
        self.colors = {
            "bg_dark": "#050a05",
            "frame_bg": "#0a110a",
            "card_bg": "#0d160e",
            "accent_green": "#00ff66",
            "dim_green": "#008833",
            "border_green": "#1b382b",
            "text_green": "#00ff66",
            "text_white": "#d0ffd0",
            "danger_red": "#ff4444",
            "highlight_bg": "#003311",
            "header_bg": "#081c0d",
            "link_cyan": "#00f0ff",
        }

        self.setup_styles()
        self.build_ui()
        self.start_clock()
        self.initial_system_check()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        mono_font = ("Consolas" if os.name == "nt" else "DejaVu Sans Mono", 10)
        mono_bold = (mono_font[0], 10, "bold")
        mono_small = (mono_font[0], 9)

        self.fonts = {
            "mono": mono_font,
            "bold": mono_bold,
            "small": mono_small,
        }

        style.configure(
            "Treeview",
            background=self.colors["bg_dark"],
            foreground=self.colors["text_green"],
            fieldbackground=self.colors["bg_dark"],
            font=mono_font,
            rowheight=24,
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", self.colors["highlight_bg"])],
            foreground=[("selected", "#ffffff")]
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["header_bg"],
            foreground=self.colors["accent_green"],
            font=mono_bold,
            borderwidth=1,
            relief="solid"
        )
        style.map(
            "Treeview.Heading",
            background=[("active", self.colors["highlight_bg"])]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=self.colors["frame_bg"],
            troughcolor=self.colors["bg_dark"],
            bordercolor=self.colors["border_green"],
            arrowcolor=self.colors["accent_green"]
        )

    def build_ui(self):
        # 1. Top Header Banner
        self.header_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], padx=12, pady=8)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.lbl_title = tk.Label(
            self.header_frame,
            text="[ EXIFHACK v2.1 ]  ::  METADATA FORENSIC SUITE  ::  ExifTool-compatible ::",
            font=self.fonts["bold"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"]
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_clock = tk.Label(
            self.header_frame,
            text="",
            font=self.fonts["mono"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"]
        )
        self.lbl_clock.pack(side=tk.RIGHT)

        # 2. Action Toolbar Buttons
        self.toolbar_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], padx=10, pady=2)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.create_button(self.toolbar_frame, "OPEN FILE", self.open_file_dialog)
        self.create_button(self.toolbar_frame, "OPEN FOLDER", self.open_folder_dialog)
        self.create_button(self.toolbar_frame, "GPS MAP", self.open_gps_map)
        self.create_button(self.toolbar_frame, "THUMBNAIL", self.view_thumbnail)
        self.create_button(self.toolbar_frame, "SCRUB COPY", self.scrub_metadata_copy, is_danger=True)
        self.create_button(self.toolbar_frame, "EXPORT TXT", self.export_metadata_txt)
        self.create_button(self.toolbar_frame, "CLEAR", self.clear_all)

        # 3. Main Split Panes
        self.paned_main = tk.PanedWindow(self.root, orient=tk.VERTICAL, bg=self.colors["border_green"], bd=1, sashwidth=4)
        self.paned_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Upper section
        self.paned_upper = tk.PanedWindow(self.paned_main, orient=tk.HORIZONTAL, bg=self.colors["border_green"], bd=0, sashwidth=4)
        self.paned_main.add(self.paned_upper, height=460)

        # Left Pane: [ FILES ]
        self.files_frame = tk.LabelFrame(
            self.paned_upper,
            text=" [ FILES ] ",
            font=self.fonts["bold"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"],
            bd=1,
            relief="solid"
        )
        self.paned_upper.add(self.files_frame, width=320)

        self.files_tree = ttk.Treeview(
            self.files_frame,
            columns=("file", "size", "type"),
            show="headings",
            selectmode="browse"
        )
        self.files_tree.heading("file", text="FILE", anchor="w")
        self.files_tree.heading("size", text="SIZE", anchor="e")
        self.files_tree.heading("type", text="TYPE", anchor="center")

        self.files_tree.column("file", width=160, anchor="w")
        self.files_tree.column("size", width=80, anchor="e")
        self.files_tree.column("type", width=60, anchor="center")

        self.files_scroll = ttk.Scrollbar(self.files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=self.files_scroll.set)

        self.files_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_tree.pack(fill=tk.BOTH, expand=True)
        self.files_tree.bind("<<TreeviewSelect>>", self.on_file_selected)

        # Right Pane: [ METADATA ]
        self.meta_frame = tk.LabelFrame(
            self.paned_upper,
            text=" [ METADATA ] ",
            font=self.fonts["bold"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"],
            bd=1,
            relief="solid"
        )
        self.paned_upper.add(self.meta_frame, width=680)

        # Search Bar
        self.search_frame = tk.Frame(self.meta_frame, bg=self.colors["bg_dark"], padx=4, pady=3)
        self.search_frame.pack(side=tk.TOP, fill=tk.X)

        self.lbl_filter = tk.Label(self.search_frame, text="FILTER:", font=self.fonts["small"], fg=self.colors["accent_green"], bg=self.colors["bg_dark"])
        self.lbl_filter.pack(side=tk.LEFT, padx=3)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_metadata)
        self.search_entry = tk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            bg="#0d1f11",
            fg=self.colors["accent_green"],
            insertbackground=self.colors["accent_green"],
            font=self.fonts["mono"],
            relief="solid",
            bd=1
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.meta_tree = ttk.Treeview(
            self.meta_frame,
            columns=("tag", "value"),
            show="headings",
            selectmode="extended"
        )
        self.meta_tree.heading("tag", text="TAG", anchor="w")
        self.meta_tree.heading("value", text="VALUE", anchor="w")

        self.meta_tree.column("tag", width=240, anchor="w")
        self.meta_tree.column("value", width=420, anchor="w")

        self.meta_scroll_y = ttk.Scrollbar(self.meta_frame, orient=tk.VERTICAL, command=self.meta_tree.yview)
        self.meta_scroll_x = ttk.Scrollbar(self.meta_frame, orient=tk.HORIZONTAL, command=self.meta_tree.xview)
        self.meta_tree.configure(yscrollcommand=self.meta_scroll_y.set, xscrollcommand=self.meta_scroll_x.set)

        self.meta_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.meta_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.meta_tree.pack(fill=tk.BOTH, expand=True)

        # Lower section: [ CONSOLE ]
        self.console_frame = tk.LabelFrame(
            self.paned_main,
            text=" [ CONSOLE ] ",
            font=self.fonts["bold"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"],
            bd=1,
            relief="solid"
        )
        self.paned_main.add(self.console_frame, height=140)

        self.console_text = tk.Text(
            self.console_frame,
            bg="#020502",
            fg=self.colors["accent_green"],
            font=self.fonts["mono"],
            wrap=tk.WORD,
            bd=0,
            padx=6,
            pady=4,
            insertbackground=self.colors["accent_green"]
        )
        self.console_scroll = ttk.Scrollbar(self.console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=self.console_scroll.set)

        self.console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.pack(fill=tk.BOTH, expand=True)

        # 4. Status Bar at Bottom (With Clickable Author Copyright)
        self.status_frame = tk.Frame(self.root, bg=self.colors["bg_dark"], padx=10, pady=4)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(
            self.status_frame,
            text="[*] System Idle.",
            font=self.fonts["bold"],
            fg=self.colors["accent_green"],
            bg=self.colors["bg_dark"]
        )
        self.lbl_status.pack(side=tk.LEFT)

        # Copyright & Author Link on Right
        self.lbl_author = tk.Label(
            self.status_frame,
            text="Developed by: R4in8ow 🔗",
            font=self.fonts["small"],
            fg=self.colors["link_cyan"],
            bg=self.colors["bg_dark"],
            cursor="hand2"
        )
        self.lbl_author.pack(side=tk.RIGHT)
        self.lbl_author.bind("<Button-1>", lambda e: webbrowser.open(__author_link__))

    def create_button(self, parent, text, command, is_danger=False):
        fg_col = self.colors["danger_red"] if is_danger else self.colors["accent_green"]
        active_bg = "#441111" if is_danger else self.colors["highlight_bg"]

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts["bold"],
            fg=fg_col,
            bg=self.colors["frame_bg"],
            activeforeground="#ffffff",
            activebackground=active_bg,
            relief="solid",
            bd=1,
            padx=12,
            pady=3,
            cursor="hand2",
            highlightcolor=fg_col,
            highlightthickness=1
        )
        btn.pack(side=tk.LEFT, padx=3, pady=2)
        return btn

    def log(self, message, level="*"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{ts}] [{level}] {message}\n"
        self.console_text.insert(tk.END, log_line)
        self.console_text.see(tk.END)

    def start_clock(self):
        def update_time():
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.lbl_clock.config(text=now_str)
            self.root.after(1000, update_time)
        update_time()

    def initial_system_check(self):
        self.log("EXIFHACK v2.1 initialized.", "*")
        self.log("Author / Copyright: R4in8ow (fb.com/R4in8owLay)", "*")
        if self.exiftool_path:
            self.log(f"exiftool binary: {self.exiftool_path}", "*")
        else:
            self.log("exiftool binary NOT FOUND in PATH! Running in limited fallback mode.", "!")
            self.log("Tip: Install ExifTool to extract full forensic metadata.", "!")

        if PILLOW_AVAILABLE:
            self.log("Pillow module : OK", "*")
        else:
            self.log("Pillow module : NOT INSTALLED (Thumbnail preview disabled)", "!")

        self.log("Target file/folder select: Click OPEN FILE or OPEN FOLDER.", "!")

    def open_file_dialog(self):
        filetypes = [
            ("All Supported Media", "*.jpg *.jpeg *.png *.mp4 *.mov *.avi *.mkv *.pdf *.docx *.mp3 *.wav *.heic *.tiff *.raw *.dng"),
            ("Images", "*.jpg *.jpeg *.png *.heic *.tiff *.raw *.dng *.gif *.bmp *.webp"),
            ("Videos", "*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.m4v *.webm"),
            ("Audio", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a"),
            ("Documents", "*.pdf *.docx *.xlsx *.pptx *.doc *.zip"),
            ("All Files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Media Files", filetypes=filetypes)
        if files:
            threading.Thread(target=self.load_files_worker, args=(files,), daemon=True).start()

    def open_folder_dialog(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            file_list = []
            for root_dir, _, filenames in os.walk(folder):
                for f in filenames:
                    file_list.append(os.path.join(root_dir, f))
            if file_list:
                threading.Thread(target=self.load_files_worker, args=(file_list,), daemon=True).start()
            else:
                self.log(f"No files found in {folder}", "!")

    def load_files_worker(self, file_paths):
        new_count = 0
        for path in file_paths:
            if not os.path.isfile(path):
                continue
            name = os.path.basename(path)
            try:
                size_bytes = os.path.getsize(path)
                size_str = self.format_file_size(size_bytes)
            except Exception:
                size_str = "0 B"

            _, raw_ext = os.path.splitext(name)
            ext = raw_ext.lstrip(".").upper() if raw_ext else "FILE"

            file_entry = {
                "path": path,
                "name": name,
                "size_str": size_str,
                "type": ext,
                "metadata": None
            }
            self.files_data.append(file_entry)
            new_count += 1
            self.root.after(0, self._append_file_to_tree, file_entry)

        self.root.after(0, lambda count=new_count: self.log(f"{count} file(s) loaded.", "+"))
        if self.files_data and not self.current_selected_file:
            self.root.after(0, lambda: self.select_file_index(0))

    def _append_file_to_tree(self, entry):
        item_id = self.files_tree.insert("", tk.END, values=(entry["name"], entry["size_str"], entry["type"]))
        entry["tree_id"] = item_id

    def select_file_index(self, index):
        if 0 <= index < len(self.files_data):
            tree_id = self.files_data[index].get("tree_id")
            if tree_id:
                self.files_tree.selection_set(tree_id)
                self.files_tree.see(tree_id)
                self.on_file_selected()

    def format_file_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def on_file_selected(self, event=None):
        selected_items = self.files_tree.selection()
        if not selected_items:
            return
        selected_id = selected_items[0]
        match = next((f for f in self.files_data if f.get("tree_id") == selected_id), None)
        if match:
            self.current_selected_file = match
            threading.Thread(target=self.fetch_metadata_worker, args=(match,), daemon=True).start()

    def fetch_metadata_worker(self, file_entry):
        path = file_entry["path"]
        metadata_dict = {}

        if self.exiftool_path:
            try:
                cmd = [self.exiftool_path, "-j", "-G", path]
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                json_data = json.loads(res.stdout)
                if json_data and isinstance(json_data, list):
                    metadata_dict = json_data[0]
            except Exception as e:
                self.root.after(0, lambda err=str(e), n=file_entry['name']: self.log(f"ExifTool error on {n}: {err}", "!"))
                metadata_dict = self.get_basic_system_metadata(path)
        else:
            metadata_dict = self.get_basic_system_metadata(path)

        file_entry["metadata"] = metadata_dict
        self.root.after(0, lambda f=file_entry: self.display_metadata(f))

    def get_basic_system_metadata(self, path):
        try:
            stat = os.stat(path)
            file_size = self.format_file_size(stat.st_size)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y:%m:%d %H:%M:%S")
            atime = datetime.datetime.fromtimestamp(stat.st_atime).strftime("%Y:%m:%d %H:%M:%S")
        except Exception:
            file_size = "Unknown"
            mtime = "Unknown"
            atime = "Unknown"

        _, raw_ext = os.path.splitext(path)
        ext_part = raw_ext.lstrip(".").upper() if raw_ext else "UNKNOWN"

        return {
            "SourceFile": path,
            "System:FileName": os.path.basename(path),
            "System:Directory": os.path.dirname(path),
            "System:FileSize": file_size,
            "System:FileModifyDate": mtime,
            "System:FileAccessDate": atime,
            "File:FileType": ext_part
        }

    def display_metadata(self, file_entry):
        for item in self.meta_tree.get_children():
            self.meta_tree.delete(item)

        meta = file_entry.get("metadata") or {}
        tag_count = len(meta)

        for tag, value in meta.items():
            val_str = str(value)
            self.meta_tree.insert("", tk.END, values=(tag, val_str))

        self.lbl_status.config(text=f"[+] {tag_count} tags — {file_entry['name']}")
        self.log(f"Extracted {tag_count} tags from {file_entry['name']}", "+")

    def filter_metadata(self, *args):
        query = self.search_var.get().strip().lower()
        if not self.current_selected_file or not self.current_selected_file.get("metadata"):
            return

        for item in self.meta_tree.get_children():
            self.meta_tree.delete(item)

        meta = self.current_selected_file["metadata"]
        matches = 0
        for tag, value in meta.items():
            val_str = str(value)
            if query in tag.lower() or query in val_str.lower():
                self.meta_tree.insert("", tk.END, values=(tag, val_str))
                matches += 1

        self.lbl_status.config(text=f"[+] Showing {matches}/{len(meta)} tags — {self.current_selected_file['name']}")

    def open_gps_map(self):
        if not self.current_selected_file or not self.current_selected_file.get("metadata"):
            messagebox.showwarning("No File Selected", "Please select a file first.")
            return

        meta = self.current_selected_file["metadata"]
        lat_candidates = [
            meta.get("Composite:GPSLatitude"),
            meta.get("EXIF:GPSLatitude"),
            meta.get("GPS:GPSLatitude"),
            meta.get("GPSLatitude")
        ]
        lon_candidates = [
            meta.get("Composite:GPSLongitude"),
            meta.get("EXIF:GPSLongitude"),
            meta.get("GPS:GPSLongitude"),
            meta.get("GPSLongitude")
        ]

        lat_val = next((item for item in lat_candidates if item is not None), None)
        lon_val = next((item for item in lon_candidates if item is not None), None)

        lat = None
        lon = None
        if lat_val is not None and lon_val is not None:
            lat = self.parse_gps_coord(lat_val, meta.get("EXIF:GPSLatitudeRef"))
            lon = self.parse_gps_coord(lon_val, meta.get("EXIF:GPSLongitudeRef"))

        if lat is not None and lon is not None:
            url = f"https://www.google.com/maps?q={lat},{lon}"
            self.log(f"Opening GPS Coordinates [{lat:.6f}, {lon:.6f}] in Maps...", "+")
            webbrowser.open(url)
        else:
            self.log(f"No GPS coordinates found in {self.current_selected_file['name']}", "!")
            messagebox.showinfo("GPS Info", f"No GPS metadata found in {self.current_selected_file['name']}")

    def parse_gps_coord(self, coord_str, ref=None):
        if isinstance(coord_str, (int, float)):
            val = float(coord_str)
            if ref and str(ref).upper() in ['S', 'W']:
                val = -abs(val)
            return val

        coord_str = str(coord_str).strip()
        match = re.match(
            r"([+-]?\d+(?:\.\d+)?)\s*(?:deg|°)?\s*(\d+(?:\.\d+)?)?'?\s*(\d+(?:\.\d+)?)?\"?\s*([NSEW])?",
            coord_str,
            re.IGNORECASE
        )
        if match:
            deg, minutes, seconds, direction = match.groups()
            deg = float(deg) if deg else 0.0
            minutes = float(minutes) if minutes else 0.0
            seconds = float(seconds) if seconds else 0.0
            val = deg + minutes / 60.0 + seconds / 3600.0
            dir_val = direction or ref
            if dir_val and str(dir_val).upper() in ['S', 'W']:
                val = -abs(val)
            return val
        try:
            val = float(coord_str)
            if ref and str(ref).upper() in ['S', 'W']:
                val = -abs(val)
            return val
        except ValueError:
            return None

    def view_thumbnail(self):
        if not self.current_selected_file:
            messagebox.showwarning("No File", "Please select a file first.")
            return

        if not PILLOW_AVAILABLE:
            messagebox.showerror("Missing Module", "Pillow is required for thumbnail view. Please run: pip install pillow")
            return

        path = self.current_selected_file["path"]
        img = None

        if self.exiftool_path:
            try:
                res = subprocess.run([self.exiftool_path, "-b", "-ThumbnailImage", path], capture_output=True)
                if res.stdout and len(res.stdout) > 100:
                    img = Image.open(io.BytesIO(res.stdout))
            except Exception:
                pass

            if img is None:
                try:
                    res = subprocess.run([self.exiftool_path, "-b", "-PreviewImage", path], capture_output=True)
                    if res.stdout and len(res.stdout) > 100:
                        img = Image.open(io.BytesIO(res.stdout))
                except Exception:
                    pass

        if img is None:
            try:
                img = Image.open(path)
            except Exception as e:
                self.log(f"No thumbnail preview available for {self.current_selected_file['name']}", "!")
                messagebox.showinfo("Thumbnail", "No embedded thumbnail available for this file.")
                return

        thumb_win = tk.Toplevel(self.root)
        thumb_win.title(f"Thumbnail Preview — {self.current_selected_file['name']}")
        thumb_win.geometry("500x500")
        thumb_win.configure(bg=self.colors["bg_dark"])

        img.thumbnail((460, 460))
        photo = ImageTk.PhotoImage(img)

        lbl = tk.Label(thumb_win, image=photo, bg=self.colors["bg_dark"], bd=1, relief="solid")
        lbl.image = photo
        lbl.pack(expand=True, padx=10, pady=10)
        self.log(f"Thumbnail preview opened for {self.current_selected_file['name']}", "+")

    def scrub_metadata_copy(self):
        if not self.current_selected_file:
            messagebox.showwarning("No File", "Please select a file first.")
            return

        if not self.exiftool_path:
            messagebox.showerror("ExifTool Required", "ExifTool is required to scrub metadata.")
            return

        orig_path = self.current_selected_file["path"]
        dirname, filename = os.path.split(orig_path)
        name, ext = os.path.splitext(filename)

        save_path = filedialog.asksaveasfilename(
            title="Save Metadata-Scrubbed Copy",
            initialdir=dirname,
            initialfile=f"{name}_clean{ext}",
            defaultextension=ext
        )
        if not save_path:
            return

        def scrub_worker():
            try:
                self.root.after(0, lambda: self.log(f"Scrubbing metadata from {filename}...", "*"))
                cmd = [self.exiftool_path, "-all=", "-o", save_path, orig_path]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    self.root.after(0, lambda: self.log(f"Successfully scrubbed & saved to: {save_path}", "+"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Cleaned file saved successfully:\n{save_path}"))
                else:
                    self.root.after(0, lambda: self.log(f"Scrub error: {res.stderr}", "!"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to scrub: {res.stderr}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Scrub error: {str(e)}", "!"))
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=scrub_worker, daemon=True).start()

    def export_metadata_txt(self):
        if not self.current_selected_file or not self.current_selected_file.get("metadata"):
            messagebox.showwarning("No Metadata", "No metadata loaded to export.")
            return

        file_name = self.current_selected_file["name"]
        root_name, _ = os.path.splitext(file_name)
        default_txt = f"{root_name}_metadata.txt"

        save_path = filedialog.asksaveasfilename(
            title="Export Metadata",
            initialfile=default_txt,
            filetypes=[("Text File", "*.txt"), ("JSON File", "*.json"), ("All Files", "*.*")]
        )
        if not save_path:
            return

        try:
            meta = self.current_selected_file["metadata"]
            if save_path.endswith(".json"):
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=4, ensure_ascii=False)
            else:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("=" * 70 + "\n")
                    f.write(f" EXIFHACK FORENSIC REPORT: {file_name}\n")
                    f.write(f" Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f" Developed by: R4in8ow ({__author_link__})\n")
                    f.write("=" * 70 + "\n\n")
                    for k, v in meta.items():
                        f.write(f"{k:<35} : {v}\n")

            self.log(f"Metadata exported to {save_path}", "+")
            messagebox.showinfo("Exported", f"Metadata report saved to:\n{save_path}")
        except Exception as e:
            self.log(f"Export failed: {str(e)}", "!")
            messagebox.showerror("Export Failed", str(e))

    def clear_all(self):
        self.files_data.clear()
        self.current_selected_file = None
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        for item in self.meta_tree.get_children():
            self.meta_tree.delete(item)
        self.lbl_status.config(text="[*] Cleared all data.")
        self.log("Workspace cleared.", "*")


def main():
    root = tk.Tk()
    app = ExifHackApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
