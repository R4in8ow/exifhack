# EXIFHACK // Metadata Forensic Suite

A self-built GUI forensic toolkit for deep EXIF & metadata analysis, designed for cybersecurity researchers, OSINT investigators, and digital forensic analysts.

---

## 👨‍💻 Author & Copyright
- **Developer**: [R4in8ow](https://www.facebook.com/R4in8owLay)
- **Linkedin**: [PyaeSoneMyo](https://www.linkedin.com/in/pyae-sone-myo-74b34133b/)
- **License**: MIT License (© 2026 R4in8ow. All Rights Reserved.)

---

## 🚀 Key Features

- 🔍 **Deep EXIF & Metadata Extraction**: Reads EXIF, XMP, IPTC, QuickTime, GPS & System tags via the ExifTool engine.
- 🛰️ **GPS Mapping**: Extracts geographic coordinates and opens locations directly in Google Maps.
- 📷 **Thumbnail Inspector**: Preview embedded thumbnails and media preview frames.
- 🛡️ **Metadata Scrubbing (Sanitization)**: Strip all metadata and export clean copies for privacy.
- 📄 **Export Reports**: Save forensic tag dumps directly to TXT or JSON formats.
- ⚡ **Hacker Terminal UI**: Dark phosphor green cyberpunk UI built with Python & Tkinter.

---

## 📦 Prerequisites & Installation

### 1. Install System Dependencies (ExifTool & FFmpeg)

- **Ubuntu / Debian / Kali Linux:**
  ```bash
  sudo apt update && sudo apt install -y libimage-exiftool-perl ffmpeg python3-tk
  ```

- **macOS (Homebrew):**
  ```bash
  brew install exiftool ffmpeg
  ```

- **Windows:**
  - Download `exiftool.exe` from exiftool.org and add to your System PATH.
  - Download `ffmpeg` from ffmpeg.org and add to your System PATH.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 🎮 Tools & Usage

### 1. GUI Forensic Suite (`exifhack.py`)
Launch the full graphic user interface:
```bash
python3 exifhack.py
```

### 2. Fast Metadata & Subtitle Stripper (`remove_metadata.py`)
Remove all embedded metadata, download tags, and extra subtitle tracks instantly:
```bash
python3 remove_metadata.py input_video.mp4
```

### 3. Video Episode Splitter for TikTok/Reels (`split_episode.py`)
Split long movies into multiple episodic parts (default: 3-minute clips):
```bash
python3 split_episode.py input_video.mp4 -m 3
```

---

## 📁 Repository Structure

```text
exifhack/
├── exifhack.py         # Main GUI Forensic Application
├── remove_metadata.py  # CLI Fast Metadata & Track Stripper
├── split_episode.py    # CLI Video Episode Splitter for TikTok
├── requirements.txt    # Python Dependencies
├── .gitignore          # Git Ignore Rules
└── README.md           # Documentation
```

---

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
