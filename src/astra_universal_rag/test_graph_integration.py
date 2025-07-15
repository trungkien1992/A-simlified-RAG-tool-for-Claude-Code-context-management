#!/usr/bin/env python3
"""
Test the integration between enhanced commit ingestion and graph search
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import knowledge_graph
from enhanced_commit_ingestion import main as run_ingestion


async def test_full_integration():
    """Test the complete integration pipeline"""

    print("🔄 Testing Full Knowledge Graph Integration")
    print("=" * 60)

    # Step 1: Run enhanced ingestion
    print("1. Running enhanced commit ingestion...")
    try:
        await run_ingestion()
        print("   ✅ Ingestion completed")
    except Exception as e:
        print(f"   ❌ Ingestion failed: {e}")
        return

    # Step 2: Connect to the same graph instance
    print("\n2. Connecting to knowledge graph...")
    if not await knowledge_graph.connect():
        print("   ❌ Failed to connect to knowledge graph")
        return

    # Step 3: Check graph statistics
    print("\n3. Checking graph statistics...")
    stats = await knowledge_graph.get_graph_stats()
    print(f"   📊 Total Nodes: {stats['nodes']['total']}")
    for node_type, count in stats["nodes"].items():
        if node_type != "total":
            print(f"      {node_type}: {count}")
    print(f"   🔗 Total Relationships: {stats['relationships']['total']}")

    # Step 4: Test specific queries
    print("\n4. Testing specific graph queries...")

    # Find all developers
    all_devs = list(knowledge_graph.nodes["developers"].keys())
    print(f"   👥 Developers in graph: {all_devs}")

    if all_devs:
        # Test with the first developer
        dev_key = all_devs[0]
        dev_data = knowledge_graph.nodes["developers"][dev_key]
        dev_name = dev_data["name"]

        print(f"\n   🔍 Testing queries for developer: {dev_name}")

        # Find their work
        work_results = await knowledge_graph.find_developer_work(dev_name)
        print(f"      Work items: {len(work_results)}")

        if work_results:
            sample_work = work_results[0]
            print(f"      Sample commit: {sample_work['commit']['hash'][:8]}")
            print(f"      Message: {sample_work['commit']['message'][:50]}...")
            print(f"      Files modified: {len(sample_work['files'])}")

    # Step 5: Test the graph search system
    print("\n5. Testing graph search system...")
    from graph_search import graph_search

    if await graph_search.initialize():
        # Test a simple query
        results = await graph_search.search(
            "Peter's work on game features", max_results=3
        )
        print(f"   🔍 Search results: {len(results['combined_results'])}")
        print(f"   ⏱️  Execution time: {results['execution_time']:.3f}s")

        if results["combined_results"]:
            print(f"   📝 Sample result type: {results['combined_results'][0]['type']}")

    print("\n" + "=" * 60)
    print("✅ Integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_full_integration())
