#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# next-exam-timeline-json-creator.py
#
# Creates timeline JSON files from Next-Exam backup snapshots.
#
# Copyright (C) 2026 Stefan Kugler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see:
# https://www.gnu.org/licenses/gpl-3.0.html
#
# Repository:
# https://github.com/stefankugler/next-exam-timeline-diff
# =============================================================================

"""
Creates timeline JSON files from Next-Exam backup snapshots.

USAGE
===============================================================================

1. Process multiple exams (teacher mode)

    python next-exam-timeline-json-creator.py teacher [DIRECTORY]

    Example:
    python next-exam-timeline-json-creator.py teacher D:\Exams

    Structure:
    DIRECTORY/
    ├── Exam1/
    ├── Exam2/
    ├── Exam3/


2. Process a single exam (exam mode)

    python next-exam-timeline-json-creator.py exam [DIRECTORY]

    Example:
    python next-exam-timeline-json-creator.py exam D:\Exams\Math_2026

    Structure:
    DIRECTORY/
    ├── Student1/
    ├── Student2/


If no DIRECTORY is specified:
-> current working directory


FEATURES
===============================================================================

- Only processes exams using .bak backup files
- Automatically skips unsupported exam types
- Removes HTML tags from backup files
- Preserves paragraphs and line breaks
- Generates chronological timeline JSON files
- Overwrites existing JSON files
- Supports continuously updated backup folders
"""

import html
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

# =============================================================================
# TIMESTAMP PATTERN
# =============================================================================

TIMESTAMP_PATTERN = re.compile(r"^\d{8}_\d{2}_\d{2}_\d{2}$")


class HTMLTextExtractor(HTMLParser):
    """
    Extracts readable text from HTML while preserving line breaks.
    """

    BLOCK_TAGS = {
        "p", "div", "br", "tr",
        "li", "ul", "ol",
        "h1", "h2", "h3", "h4", "h5", "h6"
    }

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):

        text = "".join(self.parts)

        # Decode HTML entities
        text = html.unescape(text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Reduce multiple spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)

        # Reduce excessive empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


def print_usage():
    print("""
Usage:

  Multiple exams:
    python next-exam-timeline-json-creator.py teacher [DIRECTORY]

  Single exam:
    python next-exam-timeline-json-creator.py exam [DIRECTORY]

If no DIRECTORY is specified:
-> current working directory
""")


def get_args():
    """
    Reads:
    - mode (teacher/exam)
    - base directory
    """

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode not in ("teacher", "exam"):
        print("Invalid mode:", mode)
        print_usage()
        sys.exit(1)

    if len(sys.argv) >= 3:
        base_dir = Path(sys.argv[2]).resolve()
    else:
        base_dir = Path.cwd()

    return mode, base_dir


def parse_timestamp(timestamp_str: str) -> str:
    """
    Converts YYYYMMDD_HH_MM_SS to ISO timestamp.
    """

    dt = datetime.strptime(timestamp_str, "%Y%m%d_%H_%M_%S")
    return dt.isoformat()


def html_to_text(content: str) -> str:
    """
    Removes HTML tags while preserving formatting.
    """

    parser = HTMLTextExtractor()
    parser.feed(content)

    return parser.get_text()


def read_bak_file(file_path: Path) -> str:
    """
    Reads backup file content using multiple encodings
    and removes HTML.
    """

    encodings = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            raw = file_path.read_text(encoding=enc)

            return html_to_text(raw)

        except Exception:
            pass

    return ""


def get_timestamp_dirs(student_dir: Path):
    """
    Returns sorted timestamp directories.
    """

    return sorted([
        d for d in student_dir.iterdir()
        if d.is_dir() and TIMESTAMP_PATTERN.match(d.name)
    ])


def is_supported_exam(exam_dir: Path) -> bool:
    """
    Checks whether an exam uses .bak backup files.

    Only checks the first student/timestamp folder.
    """

    student_dirs = sorted([
        d for d in exam_dir.iterdir()
        if d.is_dir()
    ])

    if not student_dirs:
        return False

    first_student = student_dirs[0]

    timestamp_dirs = get_timestamp_dirs(first_student)

    if not timestamp_dirs:
        return False

    first_timestamp_dir = timestamp_dirs[0]

    bak_files = list(first_timestamp_dir.glob("*.bak"))

    return len(bak_files) > 0


def process_student_folder(student_dir: Path):
    """
    Processes a student folder.
    """

    print(f"\nProcessing student: {student_dir.name}")

    timestamp_dirs = get_timestamp_dirs(student_dir)

    if not timestamp_dirs:
        print("  No timestamp folders found.")
        return

    bak_data = {}

    for ts_dir in timestamp_dirs:

        timestamp_name = ts_dir.name

        try:
            timestamp_iso = parse_timestamp(timestamp_name)
        except Exception:
            print(f"  Invalid timestamp: {timestamp_name}")
            continue

        bak_files = list(ts_dir.glob("*.bak"))

        if not bak_files:
            continue

        for bak_file in bak_files:

            bak_name = bak_file.name
            text = read_bak_file(bak_file)

            if bak_name not in bak_data:
                bak_data[bak_name] = []

            bak_data[bak_name].append({
                "timestamp_name": timestamp_name,
                "timestamp": timestamp_iso,
                "text": text
            })

    # No .bak files found
    if not bak_data:
        print("  No .bak files found.")
        return

    # Write JSON files
    for bak_name, entries in bak_data.items():

        if not entries:
            continue

        bak_stem = Path(bak_name).stem

        output_name = f"{student_dir.name}_{bak_stem}.json"
        output_path = student_dir / output_name

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        print(f"  JSON written: {output_name}")


def process_exam(exam_dir: Path):
    """
    Processes a single exam directory.
    """

    print(f"\n=== Exam: {exam_dir.name} ===")

    if not is_supported_exam(exam_dir):
        print("  Skipped (no .bak files in first snapshot folder).")
        return

    student_dirs = sorted([
        d for d in exam_dir.iterdir()
        if d.is_dir()
    ])

    for student_dir in student_dirs:
        process_student_folder(student_dir)


def main():

    mode, base_dir = get_args()

    print(f"Mode: {mode}")
    print(f"Base directory: {base_dir}")

    if not base_dir.exists():
        print("Directory does not exist.")
        return

    # =========================================================================
    # teacher mode
    # =========================================================================

    if mode == "teacher":

        exam_dirs = sorted([
            d for d in base_dir.iterdir()
            if d.is_dir()
        ])

        for exam_dir in exam_dirs:
            process_exam(exam_dir)

    # =========================================================================
    # exam mode
    # =========================================================================

    elif mode == "exam":

        process_exam(base_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()