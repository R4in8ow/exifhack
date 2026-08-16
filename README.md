# EXIFHACK // Metadata Forensic Suite

A self-built GUI forensic toolkit for deep EXIF & metadata analysis, designed for cybersecurity researchers, OSINT investigators, and digital forensic analysts.

## 🚀 Features
- 🔍 **Deep Metadata Extraction**: Reads EXIF, XMP, IPTC, QuickTime, GPS & System tags via ExifTool engine.
- 🛰️ **GPS Mapping**: Extracts coordinates and opens locations directly in Google Maps.
- 📷 **Thumbnail Inspector**: Preview embedded thumbnails and media images.
- 🛡️ **Metadata Scrubbing (Sanitization)**: Strip all metadata and export clean copies for privacy.
- 📄 **Export Reports**: Save forensic tag dumps to TXT or JSON format.
- ⚡ **Hacker Terminal UI**: Dark phosphor green cyberpunk UI built on Python Tkinter.

## 📦 Prerequisites & Installation

### 1. Install ExifTool
- **Ubuntu / Debian / Kali:**
  ```bash
  sudo apt update && sudo apt install -y libimage-exiftool-perl python3-tk

- **MacOS**
  ```bash
  brew install exiftool

- **Window**
  ```bash
  Download exiftool.exe from exiftool.org and add it to your System PATH.

###2. Install Python Dependencies
  ```bash
  pip install -r requirements.txt

###3. Usage
  ```bash
  python3 exifhack.py
