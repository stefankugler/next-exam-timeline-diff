# next-exam Timeline Diff

Creates timeline JSON files from next-exam backup snapshots and visualizes changes between revisions over time.

The project helps analyze how student texts evolve during digital exams by converting all backup snapshots into structured chronological JSON data.

next-exam:
https://github.com/Bildungsportal/next-exam

---

# Features

- Parses next-exam backup snapshots (`.bak`)
- Automatically detects valid Next-Exam exams
- Extracts text from HTML-based backups
- Removes HTML tags
- Preserves paragraphs and line breaks
- Generates chronological JSON timelines
- Supports multiple exams and students
- Automatically detects newly appearing files
- Overwrites outdated JSON files on rerun
- Works well for recurring background processing

---

# Supported Folder Structure

## Teacher Mode

```text
EXAM-TEACHER/
├── Exam1/
│   ├── StudentA/
│   │   ├── 20260514_08_00_00/
│   │   ├── 20260514_08_05_00/
│   │   └── ...
│   ├── StudentB/
│   └── ...
│
├── Exam2/
└── ...
```

## Exam Mode

```text
Exam1/
├── StudentA/
├── StudentB/
└── ...
```

---

# Installation

Requires Python 3.10+.

Clone repository:

```bash
git clone https://github.com/stefankugler/next-exam-timeline-diff.git
cd next-exam-timeline-diff
```

No additional dependencies required.

---

# Usage

## Process Multiple Exams

```bash
python next-exam-timeline-json-creator.py teacher /path/to/exams
```

Example:

```bash
python next-exam-timeline-json-creator.py teacher /data/exams
```

---

## Process Single Exam

```bash
python next-exam-timeline-json-creator.py exam /path/to/exam
```

Example:

```bash
python next-exam-timeline-json-creator.py exam /data/exams/math_exam
```

---

## Use Current Directory

```bash
python next-exam-timeline-json-creator.py teacher
```

or

```bash
python next-exam-timeline-json-creator.py exam
```

---

# Generated JSON Structure

For every `.bak` file, one JSON timeline file is created inside the student directory.

Example output file:

```text
StudentA_Essay.json
```

Example content:

```json
[
  {
    "timestamp_name": "20260514_08_00_00",
    "timestamp": "2026-05-14T08:00:00",
    "text": "First version of the text."
  },
  {
    "timestamp_name": "20260514_08_05_00",
    "timestamp": "2026-05-14T08:05:00",
    "text": "Updated version of the text."
  }
]
```

---

# Behavior

## Automatically Skips Unsupported Exams

The script checks the first student snapshot folder.

If no `.bak` file exists there:
- the entire exam is skipped
- no JSON files are generated

This allows coexistence with other exam types using different file formats.

---

# HTML Cleanup

The script automatically:
- removes HTML tags
- decodes HTML entities
- preserves paragraphs
- preserves line breaks
- normalizes whitespace

---

# Typical Use Cases

- Exam documentation
- Writing process analysis
- AI usage analysis
- Plagiarism investigations
- Revision tracking
- Visualization of writing development
- Educational research

---

# License

GPL-3.0 License

This project is licensed under the GNU General Public License v3.0.

See:
https://www.gnu.org/licenses/gpl-3.0.html

---

# Author

Stefan Kugler
