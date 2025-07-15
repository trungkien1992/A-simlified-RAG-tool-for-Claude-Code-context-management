#!/usr/bin/env python3
"""
Test script to verify commit search functionality
Tests both direct ChromaDB queries and the RAG search API
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from rag_system import AstraRAG


async def test_search_api():
    """Test the search API specifically for commit documents"""

    print("🧪 Testing Astra RAG Search API for Commit Documents")
    print("=" * 60)

    # Initialize RAG system
    rag = AstraRAG()
    await rag.initialize()

    # Test queries for commits
    test_queries = [
        "git commit changes",
        "code changes diff",
        "commit history",
        "repository commits",
        "flutter authentication implementation",
        "security implementation",
        "initial commit",
    ]

    # Test different similarity thresholds
    similarity_thresholds = [0.0, 0.1, 0.3, 0.6]

    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 40)

        for threshold in similarity_thresholds:
            print(f"\n  📊 Min similarity threshold: {threshold}")

            # Test without category filter
            results = await rag.search(
                query=query, max_results=5, min_similarity=threshold
            )

            total_results = len(results["results"])
            commit_results = [
                r for r in results["results"] if r["category"] == "commit_history"
            ]

            print(f"    Total results: {total_results}")
            print(f"    Commit results: {len(commit_results)}")

            if commit_results:
                print("    Commit similarities:")
                for result in commit_results[:3]:
                    print(
                        f"      - {result['similarity']:.3f}: {result['title'][:50]}..."
                    )

            # Test with commit category filter
            commit_filtered = await rag.search(
                query=query,
                max_results=5,
                category="commit_history",
                min_similarity=threshold,
            )

            commit_filtered_count = len(commit_filtered["results"])
            print(f"    Filtered (commit_history): {commit_filtered_count}")

            if commit_filtered["results"]:
                print("    Filtered similarities:")
                for result in commit_filtered["results"][:3]:
                    print(
                        f"      - {result['similarity']:.3f}: {result['title'][:50]}..."
                    )

        print()

    # Test the issue with negative similarities
    print("\n🐛 Testing Raw ChromaDB Distance/Similarity Conversion")
    print("-" * 60)

    # Get raw results from ChromaDB
    raw_results = rag.collection.query(
        query_texts=["git commit changes"],
        n_results=5,
        where={"category": "commit_history"},
    )

    print("Raw ChromaDB results:")
    if raw_results["distances"] and raw_results["distances"][0]:
        for i, distance in enumerate(raw_results["distances"][0]):
            similarity = 1 - distance
            doc_id = raw_results["ids"][0][i]
            print(
                f"  {i + 1}. Distance: {distance:.3f}, Similarity: {similarity:.3f}, ID: {doc_id}"
            )

    # Test with different similarity calculation methods
    print("\n🔧 Testing Alternative Similarity Calculations")
    print("-" * 60)

    if raw_results["distances"] and raw_results["distances"][0]:
        for i, distance in enumerate(raw_results["distances"][0][:3]):
            # Method 1: Current (1 - distance)
            similarity_current = 1 - distance

            # Method 2: Normalize to 0-1 range
            # Assuming max distance could be around 2.0 for normalized embeddings
            similarity_normalized = max(0, 1 - (distance / 2.0))

            # Method 3: Exponential decay
            import math

            similarity_exp = math.exp(-distance)

            # Method 4: Inverse relationship
            similarity_inverse = 1 / (1 + distance)

            doc_id = raw_results["ids"][0][i]
            print(f"  Document {i + 1} ({doc_id[:8]}...):")
            print(f"    Distance: {distance:.3f}")
            print(f"    Current (1-d): {similarity_current:.3f}")
            print(f"    Normalized: {similarity_normalized:.3f}")
            print(f"    Exponential: {similarity_exp:.3f}")
            print(f"    Inverse: {similarity_inverse:.3f}")

    print("\n" + "=" * 60)
    print("🎯 Recommendations:")
    print("=" * 60)

    # Analyze results and provide recommendations
    low_threshold_results = await rag.search(
        query="git commit",
        max_results=10,
        category="commit_history",
        min_similarity=0.0,
    )

    if low_threshold_results["results"]:
        similarities = [r["similarity"] for r in low_threshold_results["results"]]
        max_sim = max(similarities)
        min_sim = min(similarities)
        avg_sim = sum(similarities) / len(similarities)

        print("📊 Commit similarity statistics:")
        print(f"   Max: {max_sim:.3f}")
        print(f"   Min: {min_sim:.3f}")
        print(f"   Avg: {avg_sim:.3f}")

        if max_sim < 0:
            print("\n❌ PROBLEM: All similarities are negative!")
            print("   🔧 Solutions:")
            print("   1. Use alternative similarity calculation")
            print("   2. Set min_similarity to a negative value (e.g., -0.5)")
            print("   3. Use normalized similarity scoring")
        elif max_sim < 0.6:
            print(
                f"\n⚠️  PROBLEM: Max similarity ({max_sim:.3f}) < default threshold (0.6)"
            )
            print(
                f"   🔧 Solution: Lower min_similarity to {max_sim - 0.1:.3f} or use alternative scoring"
            )
        else:
            print("\n✅ Similarities look good!")

    print("\n🔍 Next steps:")
    print("1. If similarities are negative, modify the RAG search method")
    print("2. Consider using a different similarity calculation")
    print("3. Adjust the default min_similarity threshold for commits")
    print("4. Test with the suggested changes")


if __name__ == "__main__":
    asyncio.run(test_search_api())
