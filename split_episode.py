#!/usr/bin/env python3
"""
split_episode.py
Splits long videos/movies into multiple episodic parts (e.g., 3-min, 5-min clips for TikTok/Reels) using FFmpeg.
Author: R4in8ow (https://www.facebook.com/R4in8owLay)
"""

import os
import sys
import math
import shutil
import subprocess
import argparse
import re
import json

def check_tools():
    if not shutil.which("ffmpeg"):
        print("[!] Error: 'ffmpeg' is not installed or not found in PATH.")
        print("[!] Install via: sudo apt install ffmpeg")
        sys.exit(1)

def get_video_duration(file_path):
    """
    Robust multi-method duration detector:
    1. ffmpeg -i header parsing (works on corrupted/odd subtitle tracks)
    2. ffprobe JSON query
    3. ffprobe csv query
    """
    # Method 1: ffmpeg stderr inspection (အမှားအယွင်းမရှိ အတိကျဆုံး နည်းလမ်း)
    try:
        cmd = ["ffmpeg", "-i", file_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
        if match:
            h, m, s = match.groups()
            dur = int(h) * 3600 + int(m) * 60 + float(s)
            if dur > 0:
                return dur
    except Exception:
        pass

    # Method 2: ffprobe JSON
    if shutil.which("ffprobe"):
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout:
                data = json.loads(res.stdout)
                if "format" in data and "duration" in data["format"]:
                    return float(data["format"]["duration"])
                for stream in data.get("streams", []):
                    if "duration" in stream:
                        return float(stream["duration"])
        except Exception:
            pass

    # Method 3: ffprobe format=duration
    if shutil.which("ffprobe"):
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprivate=1:nokey=1", file_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception:
            pass

    return None

def parse_time_str(time_str):
    """HH:MM:SS သို့မဟုတ် MM:SS ကို စက္ကန့်အဖြစ် ပြောင်းလဲခြင်း"""
    time_str = time_str.strip()
    parts = time_str.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts) * 60 + float(parts)
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts)
        else:
            return float(parts[0])
    except ValueError:
        return None

def format_seconds(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def split_video(input_file, part_duration_minutes=3.0, output_dir=None):
    input_file = os.path.abspath(input_file.strip().strip("'\""))
    if not os.path.isfile(input_file):
        print(f"[!] File not found: {input_file}")
        return False

    duration_sec = get_video_duration(input_file)
    if not duration_sec or duration_sec <= 0:
        print(f"[!] Auto-detect duration could not parse length for: {input_file}")
        manual_input = input("Please enter total video duration (e.g. 01:38:10 or minutes): ").strip()
        duration_sec = parse_time_str(manual_input)
        if not duration_sec:
            print("[!] Invalid duration entered. Aborting.")
            return False

    part_duration_sec = part_duration_minutes * 60
    total_parts = math.ceil(duration_sec / part_duration_sec)

    dirname, filename = os.path.split(input_file)
    name, ext = os.path.splitext(filename)

    if not output_dir:
        output_dir = os.path.join(dirname, f"{name}_parts")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 65)
    print(f"[*] Input Video     : {filename}")
    print(f"[*] Total Duration  : {format_seconds(duration_sec)} ({duration_sec:.1f}s)")
    print(f"[*] Clip Length     : {part_duration_minutes} min ({part_duration_sec}s)")
    print(f"[*] Total Parts     : {total_parts} episodes")
    print(f"[*] Output Directory: {output_dir}")
    print("=" * 65)

    for i in range(total_parts):
        part_num = i + 1
        start_time = i * part_duration_sec
        actual_duration = min(part_duration_sec, duration_sec - start_time)
        out_filename = f"Part_{part_num:02d}_{name}{ext}"
        out_path = os.path.join(output_dir, out_filename)

        print(f"[+] Creating Part {part_num:02d}/{total_parts:02d} [{format_seconds(start_time)} -> {format_seconds(start_time + actual_duration)}]...")

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", input_file,
            "-t", str(actual_duration),
            "-map", "0:v:0?",
            "-map", "0:a:0?",
            "-c", "copy",
            "-map_metadata", "-1",
            "-map_chapters", "-1",
            out_path
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            fallback_cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start_time),
                "-i", input_file,
                "-t", str(actual_duration),
                "-map", "0:v:0?",
                "-map", "0:a:0?",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "22",
                "-c:a", "aac",
                "-map_metadata", "-1",
                out_path
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print("=" * 65)
    print(f"[+] All {total_parts} episodes generated successfully in:")
    print(f"    {output_dir}")
    print("=" * 65)
    return True

def main():
    check_tools()
    
    parser = argparse.ArgumentParser(description="Split long video into TikTok episodes")
    parser.add_argument("video_path", nargs="?", default="", help="Path to video file")
    parser.add_argument("-m", "--minutes", type=float, default=3.0, help="Duration per episode in minutes (default: 3.0)")
    args = parser.parse_args()

    target = args.video_path.strip().strip("'\"") if args.video_path else ""
    if not target:
        target = input("Enter video file path (or drag & drop here): ").strip().strip("'\"")

    if not target:
        print("[!] No input file specified.")
        return

    part_len = args.minutes
    if not args.video_path:
        part_len_input = input(f"Enter duration per part in minutes [Default: {part_len}]: ").strip()
        if part_len_input:
            try:
                part_len = float(part_len_input)
            except ValueError:
                part_len = 3.0

    split_video(target, part_duration_minutes=part_len)

if __name__ == "__main__":
    main()
