#!/usr/bin/env python3
"""
Generic Git commit ingestion script for RAG/AI backend.
Extracts commit history from any git repository and outputs JSON memory cards to .rag_commits/.
"""

import os
import json
import subprocess
from pathlib import Path
from ..config import settings


def get_commits(repo_path: Path):
    os.chdir(repo_path)
    log_format = "%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b%x1e"
    result = subprocess.run(
        ["git", "log", f"--pretty=format:{log_format}", "--date=iso"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git log failed: {result.stderr}")
    raw_commits = result.stdout.strip().split("\x1e")
    commits = []
    for raw in raw_commits:
        if not raw.strip():
            continue
        parts = raw.strip().split("\x1f")
        if len(parts) < 6:
            continue
        commit = {
            "hash": parts[0],
            "author": parts[1],
            "email": parts[2],
            "date": parts[3],
            "subject": parts[4],
            "body": parts[5],
        }
        commits.append(commit)
    return commits


def save_commits(commits, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for commit in commits:
        out_path = output_dir / f"commit_{commit['hash']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(commit, f, indent=2)


def main():
    repo_path = (
        settings.project_root
    )  # Assuming the current working directory is the repo root
    output_dir = settings.commit_cache_dir
    commits = get_commits(repo_path)
    save_commits(commits, output_dir)
    print(f"Ingested {len(commits)} commits from {repo_path} to {output_dir}")
