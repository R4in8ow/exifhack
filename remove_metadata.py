#!/usr/bin/env python3
"""
remove_metadata.py
Cleans and strips all embedded metadata, chapters, and unnecessary subtitle tracks from video/media files using FFmpeg.
Author: R4in8ow (https://www.facebook.com/R4in8owLay)
"""

import os
import sys
import shutil
import subprocess
import argparse

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("[!] Error: 'ffmpeg' is not installed or not found in PATH.")
        print("[!] Install via: sudo apt install ffmpeg")
        sys.exit(1)

def remove_metadata(input_file, output_file=None):
    input_file = os.path.abspath(input_file.strip().strip("'\""))
    if not os.path.isfile(input_file):
        print(f"[!] File not found: {input_file}")
        return False

    dirname, filename = os.path.split(input_file)
    name, ext = os.path.splitext(filename)

    if not output_file:
        output_file = os.path.join(dirname, f"{name}_clean{ext}")

    print(f"[*] Processing: {filename}")
    print(f"[*] Stripping metadata, chapters & extra subtitle streams...")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:v:0?",
        "-map", "0:a:0?",
        "-c", "copy",
        "-map_metadata", "-1",
        "-map_chapters", "-1",
        output_file
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            orig_size = os.path.getsize(input_file) / (1024 * 1024)
            clean_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"[+] Success! Cleaned file saved: {output_file}")
            print(f"    Original Size: {orig_size:.2f} MB | Cleaned Size: {clean_size:.2f} MB\n")
            return True
        else:
            print(f"[!] FFmpeg Error:\n{res.stderr}")
            return False
    except Exception as e:
        print(f"[!] Execution failed: {str(e)}")
        return False

def main():
    check_ffmpeg()
    
    parser = argparse.ArgumentParser(description="Strip all metadata and extra tracks from video")
    parser.add_argument("path", nargs="?", default="", help="Video file or folder path")
    args = parser.parse_args()

    target = args.path.strip().strip("'\"") if args.path else ""
    if not target:
        target = input("Enter video file path (or drag & drop here): ").strip().strip("'\"")

    if not target:
        print("[!] No input file specified.")
        return

    target = os.path.abspath(target)

    if os.path.isdir(target):
        valid_exts = ('.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.ts')
        files = [os.path.join(target, f) for f in os.listdir(target) if f.lower().endswith(valid_exts)]
        if not files:
            print(f"[!] No supported video files found in {target}")
            return
        print(f"[*] Found {len(files)} media files in directory.")
        for f in files:
            remove_metadata(f)
    else:
        remove_metadata(target)

if __name__ == "__main__":
    main()
