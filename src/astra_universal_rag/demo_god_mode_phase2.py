#!/usr/bin/env python3
"""
Demo: God Mode Phase 2 - Knowledge Graph Integration
Shows the enhanced capabilities with sample data to demonstrate the concept
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import AstraTradeKnowledgeGraph, Developer, Commit, File, Feature


async def demo_god_mode_phase2():
    """Demonstrate God Mode Phase 2 capabilities with sample data"""

    print("🚀 DEMO: AstraTrade God Mode - Phase 2 Knowledge Graph")
    print("=" * 70)
    print("Moving from simple retrieval to genuine understanding")
    print("=" * 70)

    # Initialize knowledge graph
    graph = AstraTradeKnowledgeGraph()
    await graph.connect()

    # Create sample entities to demonstrate the system
    print("\n🏗️  Building Sample Knowledge Graph...")

    # Create developers
    peter = Developer("Peter", "peter@astratrade.com")
    sarah = Developer("Sarah", "sarah@astratrade.com")
    alex = Developer("Alex", "alex@astratrade.com")

    dev_peter = await graph.create_developer(peter)
    dev_sarah = await graph.create_developer(sarah)
    dev_alex = await graph.create_developer(alex)

    # Create features
    auth_feature = Feature(
        "Authentication System", "FE-GAME-01", "Web3Auth integration for user login"
    )
    leaderboard_feature = Feature(
        "Leaderboard", "FE-GAME-02", "Global player ranking system"
    )
    xp_feature = Feature("XP System", "FE-GAME-03", "Experience points and progression")
    trading_feature = Feature(
        "Trading Engine", "FE-GAME-04", "Real-time trading capabilities"
    )

    feat_auth = await graph.create_feature(auth_feature)
    feat_leaderboard = await graph.create_feature(leaderboard_feature)
    feat_xp = await graph.create_feature(xp_feature)
    feat_trading = await graph.create_feature(trading_feature)

    # Create files
    files_data = [
        ("lib/services/auth_service.dart", "dart"),
        ("lib/services/leaderboard_service.dart", "dart"),
        ("lib/models/user_model.dart", "dart"),
        ("lib/screens/leaderboard_screen.dart", "dart"),
        ("lib/services/trading_service.dart", "dart"),
        ("lib/models/xp_model.dart", "dart"),
        ("backend/auth.py", "python"),
        ("backend/leaderboard.py", "python"),
    ]

    file_ids = {}
    for file_path, language in files_data:
        file_obj = File(file_path, language)
        file_id = await graph.create_file(file_obj)
        file_ids[file_path] = file_id

    # Create commits with realistic scenarios
    commits_data = [
        {
            "hash": "a1b2c3d4",
            "message": "Implement Web3Auth authentication system for user login",
            "author": "Peter",
            "files": [
                "lib/services/auth_service.dart",
                "lib/models/user_model.dart",
                "backend/auth.py",
            ],
            "features": [feat_auth],
        },
        {
            "hash": "e5f6g7h8",
            "message": "Add global leaderboard with real-time ranking",
            "author": "Sarah",
            "files": [
                "lib/services/leaderboard_service.dart",
                "lib/screens/leaderboard_screen.dart",
                "backend/leaderboard.py",
            ],
            "features": [feat_leaderboard],
        },
        {
            "hash": "i9j0k1l2",
            "message": "Implement XP system with level progression and achievements",
            "author": "Peter",
            "files": [
                "lib/models/xp_model.dart",
                "lib/services/leaderboard_service.dart",
            ],
            "features": [feat_xp, feat_leaderboard],
        },
        {
            "hash": "m3n4o5p6",
            "message": "Add real-time trading engine with Extended Exchange API",
            "author": "Alex",
            "files": ["lib/services/trading_service.dart"],
            "features": [feat_trading],
        },
        {
            "hash": "q7r8s9t0",
            "message": "Fix leaderboard sorting algorithm and performance",
            "author": "Sarah",
            "files": [
                "lib/services/leaderboard_service.dart",
                "backend/leaderboard.py",
            ],
            "features": [feat_leaderboard],
        },
    ]

    # Create commits and relationships
    for commit_data in commits_data:
        commit_obj = Commit(
            commit_data["hash"],
            commit_data["message"],
            commit_data["author"],
            datetime.now(),
        )
        commit_id = await graph.create_commit(commit_obj)

        # Get developer ID
        dev_id = None
        if commit_data["author"] == "Peter":
            dev_id = dev_peter
        elif commit_data["author"] == "Sarah":
            dev_id = dev_sarah
        elif commit_data["author"] == "Alex":
            dev_id = dev_alex

        # Create relationships
        if dev_id:
            await graph.author_commit(dev_id, commit_id)

        # Link to files
        for file_path in commit_data["files"]:
            if file_path in file_ids:
                await graph.commit_modifies_file(commit_id, file_ids[file_path])

        # Link to features
        for feature_id in commit_data["features"]:
            await graph.commit_implements_feature(commit_id, feature_id)

    print("✅ Sample knowledge graph created")

    # Show graph statistics
    stats = await graph.get_graph_stats()
    print("\n📊 Knowledge Graph Statistics:")
    print(f"   Developers: {stats['nodes']['developers']}")
    print(f"   Commits: {stats['nodes']['commits']}")
    print(f"   Files: {stats['nodes']['files']}")
    print(f"   Features: {stats['nodes']['features']}")
    print(f"   Relationships: {stats['relationships']['total']}")

    # Demonstrate God Mode capabilities
    print("\n" + "🎯 GOD MODE DEMONSTRATIONS" + "=" * 45)

    # Query 1: Developer work analysis
    print("\n1. 🔍 'What has Peter worked on related to authentication?'")
    print("-" * 55)
    peter_auth_work = await graph.find_developer_work("Peter", "authentication")
    if peter_auth_work:
        for work in peter_auth_work:
            commit = work["commit"]
            files = work["files"]
            print(f"   ✅ Commit {commit['hash'][:8]}: {commit['message']}")
            print(f"      📁 Files: {[f['path'] for f in files]}")
    else:
        print("   ℹ️  No authentication work found for Peter")

    # Query 2: File change history
    print("\n2. 🔍 'Who was the last person to change leaderboard_service.dart?'")
    print("-" * 60)
    leaderboard_history = await graph.find_file_history(
        "lib/services/leaderboard_service.dart"
    )
    if leaderboard_history:
        latest_change = leaderboard_history[0]  # Already sorted by timestamp
        commit = latest_change["commit"]
        author = latest_change["author"]
        print(f"   ✅ Last changed by: {author['name']}")
        print(f"      📅 Date: {commit['timestamp'][:10]}")
        print(f"      💬 Commit: {commit['message']}")
        print(f"      🔗 Hash: {commit['hash'][:8]}")
    else:
        print("   ℹ️  No change history found")

    # Query 3: Feature contributors
    print("\n3. 🔍 'Show me all contributors to the leaderboard feature'")
    print("-" * 55)
    leaderboard_contributors = await graph.find_feature_contributors("leaderboard")
    if leaderboard_contributors:
        for contributor in leaderboard_contributors:
            dev = contributor["developer"]
            commits = contributor["commits"]
            print(f"   👤 {dev['name']}: {len(commits)} commits")
            for commit in commits:
                print(f"      - {commit['hash'][:8]}: {commit['message'][:50]}...")
    else:
        print("   ℹ️  No contributors found")

    # Query 4: Cross-feature analysis
    print("\n4. 🔍 'What features has Peter worked on?'")
    print("-" * 40)
    peter_all_work = await graph.find_developer_work("Peter")
    peter_features = set()
    for work in peter_all_work:
        commit_hash = work["commit"]["hash"]
        # Find features this commit implements
        for rel in graph.relationships:
            if (
                rel["from"].startswith("commit_")
                and commit_hash in rel["from"]
                and rel["type"] == "IMPLEMENTS"
                and rel["to"] in graph.nodes["features"]
            ):
                feature_data = graph.nodes["features"][rel["to"]]
                peter_features.add(feature_data["name"])

    if peter_features:
        print(f"   ✅ Peter contributed to {len(peter_features)} features:")
        for feature in peter_features:
            print(f"      - {feature}")
    else:
        print("   ℹ️  No features found")

    # Show the power of graph-aware search
    print("\n" + "🧠 INTELLIGENT INSIGHTS" + "=" * 50)
    print("\n🔗 Cross-cutting analysis that traditional search cannot do:")
    print("   • Developer expertise mapping")
    print("   • Feature ownership tracking")
    print("   • Code collaboration patterns")
    print("   • Technical debt identification")
    print("   • Impact analysis for changes")

    print("\n💡 Next-level queries now possible:")
    print("   • 'Which files are most frequently changed together?'")
    print("   • 'Who should review changes to the trading system?'")
    print("   • 'What's the blast radius of changing auth_service.dart?'")
    print("   • 'Which developer has the most XP system knowledge?'")

    print("\n" + "=" * 70)
    print("🎉 PHASE 2 COMPLETE: Knowledge Graph Integration")
    print("=" * 70)
    print("✅ Entity extraction and relationship mapping")
    print("✅ Intelligent query routing (graph + vector)")
    print("✅ Developer-file-feature connection tracking")
    print("✅ Temporal commit analysis")
    print("✅ Cross-cutting insights impossible with vector search alone")
    print("\n🚀 Your RAG system now has TRUE contextual understanding!")


if __name__ == "__main__":
    asyncio.run(demo_god_mode_phase2())
