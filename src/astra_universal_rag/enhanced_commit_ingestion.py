#!/usr/bin/env python3
"""
Enhanced Commit Ingestion with Knowledge Graph Entity Extraction
Processes Git commits to create both RAG documents and knowledge graph entities/relationships
"""

import sys
import asyncio
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import logging
from .config import settings

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import knowledge_graph, Developer, Commit, File, Feature

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Feature detection patterns
FEATURE_PATTERNS = [
    r"FE-GAME-(\d+)",  # Ticket numbers like FE-GAME-01
    r"FEAT-(\d+)",  # Feature tickets
    r"BUG-(\d+)",  # Bug tickets
    r"#(\d+)",  # GitHub issue numbers
]

# Common feature keywords to extract
FEATURE_KEYWORDS = [
    "authentication",
    "auth",
    "login",
    "signup",
    "web3auth",
    "leaderboard",
    "ranking",
    "score",
    "points",
    "xp",
    "trading",
    "exchange",
    "api",
    "trade",
    "order",
    "wallet",
    "payment",
    "transaction",
    "starknet",
    "ui",
    "interface",
    "component",
    "screen",
    "page",
    "database",
    "storage",
    "persistence",
    "cache",
    "security",
    "encryption",
    "validation",
    "sanitization",
    "notification",
    "alert",
    "message",
    "toast",
    "game",
    "level",
    "achievement",
    "progress",
    "social",
    "friend",
    "chat",
    "community",
]


def is_important_file(filepath_str: str) -> bool:
    """Check if a file is important for ingestion"""
    if any(pattern in filepath_str for pattern in EXCLUDE_PATTERNS):
        return False
    p = Path(filepath_str)
    return p.name in IMPORTANT_FILENAMES or p.suffix in IMPORTANT_EXTENSIONS


def detect_file_language(filepath: str) -> Optional[str]:
    """Detect programming language based on file extension"""
    ext_to_lang = {
        ".dart": "dart",
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".sh": "bash",
        ".toml": "toml",
    }
    return ext_to_lang.get(Path(filepath).suffix.lower())


def extract_features_from_message(commit_message: str) -> List[str]:
    """Extract feature names and ticket IDs from commit message"""
    features = []
    message_lower = commit_message.lower()

    # Extract ticket numbers
    for pattern in FEATURE_PATTERNS:
        matches = re.findall(pattern, commit_message, re.IGNORECASE)
        for match in matches:
            features.append(f"ticket_{match}")

    # Extract feature keywords
    for keyword in FEATURE_KEYWORDS:
        if keyword in message_lower:
            features.append(keyword)

    # Extract quoted features (e.g., "User Authentication")
    quoted_features = re.findall(r'"([^"]+)"', commit_message)
    for feature in quoted_features:
        if len(feature.split()) <= 3:  # Only short feature names
            features.append(feature.lower().replace(" ", "_"))

    return list(set(features))  # Remove duplicates


def get_all_commits() -> List[Dict]:
    """Get all commits with hash, author, date, and full message"""
    cmd = [
        "git",
        "log",
        "--pretty=format:%H%x00%an%x00%ae%x00%ct%x00%s%x00%b",
        "--date=unix",
    ]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    commits = []

    for entry in result.stdout.strip().split("\n\n"):
        parts = entry.split("\x00", 5)
        if len(parts) >= 5:
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": int(parts[3]),
                    "message": f"{parts[4]}\n\n{parts[5]}".strip()
                    if len(parts) > 5
                    else parts[4],
                }
            )
    return commits


def get_commit_diff(commit_hash: str) -> Tuple[str, List[str]]:
    """Get the raw diff and list of changed files for a commit"""
    # Get diff
    cmd = ["git", "show", commit_hash, "--unified=0", "--pretty=", "--no-color"]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    diff = result.stdout

    # Get list of changed files
    cmd = ["git", "show", "--name-only", "--pretty=format:", commit_hash]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

    return diff, files


async def process_commit_for_graph(
    commit_data: Dict, diff: str, files_changed: List[str]
) -> Dict:
    """Process a single commit to extract entities and create relationships"""
    commit_hash = commit_data["hash"]
    author_name = commit_data["author"]
    author_email = commit_data["email"]
    message = commit_data["message"]
    timestamp = datetime.fromtimestamp(commit_data["date"])

    logger.info(f"🔄 Processing commit {commit_hash[:8]} by {author_name}")

    # Create entities

    # 1. Create Developer entity
    developer = Developer(name=author_name, email=author_email)
    dev_id = await knowledge_graph.create_developer(developer)

    # 2. Create Commit entity
    commit_obj = Commit(
        hash=commit_hash, message=message, author=author_name, timestamp=timestamp
    )
    commit_id = await knowledge_graph.create_commit(commit_obj)

    # 3. Create File entities for important files
    file_ids = []
    important_files = [f for f in files_changed if is_important_file(f)]

    for file_path in important_files:
        file_obj = File(path=file_path, language=detect_file_language(file_path))
        file_id = await knowledge_graph.create_file(file_obj)
        file_ids.append(file_id)

    # 4. Extract and create Feature entities
    features = extract_features_from_message(message)
    feature_ids = []

    for feature_name in features:
        # Check if it looks like a ticket ID
        ticket_id = None
        if feature_name.startswith("ticket_"):
            ticket_id = feature_name.replace("ticket_", "")
            feature_name = f"Feature {ticket_id}"

        feature_obj = Feature(
            name=feature_name,
            ticket_id=ticket_id,
            description=f"Feature extracted from commit: {message[:100]}...",
        )
        feature_id = await knowledge_graph.create_feature(feature_obj)
        feature_ids.append(feature_id)

    # Create relationships

    # Developer AUTHORED Commit
    await knowledge_graph.author_commit(dev_id, commit_id)

    # Commit MODIFIED Files
    for file_id in file_ids:
        await knowledge_graph.commit_modifies_file(commit_id, file_id)

    # Commit IMPLEMENTS Features
    for feature_id in feature_ids:
        await knowledge_graph.commit_implements_feature(commit_id, feature_id)

    return {
        "commit_id": commit_id,
        "developer_id": dev_id,
        "file_ids": file_ids,
        "feature_ids": feature_ids,
        "entities_created": len(file_ids)
        + len(feature_ids)
        + 2,  # +2 for dev and commit
        "relationships_created": 1
        + len(file_ids)
        + len(feature_ids),  # AUTHORED + MODIFIED + IMPLEMENTS
    }


async def create_memory_card(
    commit_data: Dict, diff: str, files_changed: List[str]
) -> Dict:
    """Create enhanced memory card with graph metadata"""
    commit_hash = commit_data["hash"]

    # Filter diff to only important files
    filtered_diff_lines = []
    current_file_is_important = False

    for line in diff.splitlines():
        if line.startswith("diff --git"):
            filepath = line.split(" b/")[-1]
            current_file_is_important = is_important_file(filepath)

        if current_file_is_important:
            filtered_diff_lines.append(line)

    filtered_diff = "\n".join(filtered_diff_lines)
    important_files = [f for f in files_changed if is_important_file(f)]

    # Extract features for metadata
    features = extract_features_from_message(commit_data["message"])

    # Create enhanced memory card
    memory_card = {
        "what_changed": commit_data["message"],
        "code_changes": filtered_diff,
        "metadata": {
            "special_code": commit_hash,
            "author": commit_data["author"],
            "author_email": commit_data["email"],
            "date": commit_data["date"],
            "timestamp_iso": datetime.fromtimestamp(commit_data["date"]).isoformat(),
            "files_changed": important_files,
            "total_files": len(files_changed),
            "important_files_count": len(important_files),
            "extracted_features": features,
            "has_graph_entities": True,
            "graph_processed_at": datetime.now().isoformat(),
        },
    }

    return memory_card


async def main():
    """Main enhanced ingestion function"""
    print("🚀 Starting Enhanced Commit Ingestion with Knowledge Graph...")
    print(f"Repository: {REPO_ROOT}")
    print(f"Output Directory: {OUTPUT_DIR}")

    # Initialize knowledge graph
    if not await knowledge_graph.connect():
        print("❌ Failed to initialize knowledge graph")
        return

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all commits
    commits = get_all_commits()
    print(f"📊 Found {len(commits)} total commits to process")

    processed_count = 0
    graph_entities_created = 0
    graph_relationships_created = 0

    for i, commit in enumerate(commits, 1):
        commit_hash = commit["hash"]

        try:
            print(f"🔄 Processing commit {i}/{len(commits)}: {commit_hash[:8]}")

            # Get commit diff and changed files
            diff, files_changed = get_commit_diff(commit_hash)

            # Filter to only important files
            important_files = [f for f in files_changed if is_important_file(f)]

            if not important_files:
                print(f"   ⏭️  Skipping {commit_hash[:8]} - no important files changed")
                continue

            # Process for knowledge graph
            graph_result = await process_commit_for_graph(commit, diff, files_changed)
            graph_entities_created += graph_result["entities_created"]
            graph_relationships_created += graph_result["relationships_created"]

            # Create enhanced memory card
            memory_card = await create_memory_card(commit, diff, files_changed)

            # Save memory card
            output_path = OUTPUT_DIR / f"commit_{commit_hash}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(memory_card, f, indent=2, ensure_ascii=False)

            processed_count += 1
            print(
                f"   ✅ Processed {commit_hash[:8]} - {len(important_files)} files, {len(graph_result['feature_ids'])} features"
            )

        except Exception as e:
            print(f"   ❌ Failed to process commit {commit_hash[:8]}: {e}")
            logger.error(f"Error processing commit {commit_hash}: {e}", exc_info=True)

    # Get final graph statistics
    graph_stats = await knowledge_graph.get_graph_stats()

    print("\n" + "=" * 60)
    print("📊 ENHANCED INGESTION SUMMARY")
    print("=" * 60)
    print(f"✅ Total commits processed: {processed_count}")
    print(f"📄 Memory cards created: {processed_count}")
    print(f"🔗 Graph entities created: {graph_entities_created}")
    print(f"🔗 Graph relationships created: {graph_relationships_created}")
    print("\n📈 Knowledge Graph Statistics:")
    for node_type, count in graph_stats["nodes"].items():
        if node_type != "total":
            print(f"   {node_type}: {count}")
    print(f"   Total relationships: {graph_stats['relationships']['total']}")
    print(f"\n💾 Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
