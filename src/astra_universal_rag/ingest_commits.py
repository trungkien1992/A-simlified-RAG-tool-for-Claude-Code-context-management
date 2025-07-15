#!/usr/bin/env python3
"""
Ingest Git Commit History for RAG System (v3 - Robust Diff Parsing)

This script extracts the full commit history, filtering correctly for important files
and their associated diffs to create structured JSON "memory cards".
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set

# Import the centralized settings
from .config import settings

# --- Configuration ---
REPO_ROOT = settings.project_root
OUTPUT_DIR = settings.commit_cache_dir

IMPORTANT_EXTENSIONS: Set[str] = {
    ".dart",
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".cfg",
    ".ini",
    ".sh",
    ".txt",
}
IMPORTANT_FILENAMES: Set[str] = {"Dockerfile", "Makefile"}
EXCLUDE_PATTERNS: List[str] = [
    ".g.dart",
    ".freezed.dart",
    "/build/",
    "/.dart_tool/",
    "/.git/",
    "/node_modules/",
]


def is_important_file(filepath_str: str) -> bool:
    """Checks if a file is important for ingestion based on configuration."""
    if any(pattern in filepath_str for pattern in EXCLUDE_PATTERNS):
        return False
    p = Path(filepath_str)
    return p.name in IMPORTANT_FILENAMES or p.suffix in IMPORTANT_EXTENSIONS


def get_all_commits() -> List[Dict]:
    """Gets all commits with hash, author, date, and full message."""
    cmd = ["git", "log", "--pretty=format:%H%x00%an%x00%ct%x00%s%x00%b", "--date=unix"]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    commits = []
    # Use split('\n\ncommit ') for more robust parsing on some git versions
    for entry in result.stdout.strip().split("\n\n"):
        parts = entry.split("\x00", 4)
        if len(parts) >= 4:
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": int(parts[2]),
                    "message": f"{parts[3]}\n\n{parts[4]}".strip(),
                }
            )
    return commits


def get_commit_diff(commit_hash: str) -> str:
    """Gets the raw diff for a single commit."""
    cmd = ["git", "show", commit_hash, "--unified=0", "--pretty=", "--no-color"]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout


def main():
    """Main execution function with robust diff parsing."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"[INFO] Ingesting git commit history for RAG from {REPO_ROOT}...")
    commits = get_all_commits()
    print(f"[INFO] Found {len(commits)} commits to process.")

    total_processed_count = 0
    for commit in commits:
        commit_hash = commit["hash"]
        try:
            raw_diff = get_commit_diff(commit_hash)

            filtered_diff_lines = []
            current_file_is_important = False

            # Line-by-line parsing for robustness
            for line in raw_diff.splitlines():
                if line.startswith("diff --git"):
                    # A new file diff starts, check if this file is important
                    filepath = line.split(" b/")[-1]
                    current_file_is_important = is_important_file(filepath)

                if current_file_is_important:
                    filtered_diff_lines.append(line)

            # If after checking all files in the diff, we have nothing, skip the commit.
            if not filtered_diff_lines:
                continue

            # We have changes to important files, create the memory card.
            filtered_diff = "\n".join(filtered_diff_lines)

            # Extract only the file paths that were actually included in the final diff
            final_files_changed = []
            for line in filtered_diff_lines:
                if line.startswith("diff --git"):
                    final_files_changed.append(line.split(" b/")[-1])

            memory_card = {
                "content": f"Commit Message: {commit['message']}\n\nCode Changes:\n{filtered_diff}",
                "metadata": {
                    "doc_type": "commit",
                    "commit_hash": commit_hash,
                    "author": commit["author"],
                    "date": commit["date"],
                    "files_changed": list(
                        set(final_files_changed)
                    ),  # Use the filtered list
                },
            }

            out_path = OUTPUT_DIR / f"commit_{commit_hash}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(memory_card, f, indent=2, ensure_ascii=False)

            total_processed_count += 1

        except Exception as e:
            print(
                f"[WARN] Failed to process commit {commit_hash}: {e}", file=sys.stderr
            )

    print(
        f"[DONE] {total_processed_count} relevant commits processed. Memory cards saved in {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
