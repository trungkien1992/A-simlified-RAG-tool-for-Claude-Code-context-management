#!/usr/bin/env python3
"""
Debug script for ChromaDB collection analysis
Helps identify issues with commit document indexing and search functionality
"""

import os
import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from .config import settings  # Import settings


def print_separator(title: str):
    """Print a visual separator with title"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def analyze_chromadb_collection():
    """Main debug function to analyze the ChromaDB collection"""

    # Configuration (matching your config.py)
    chroma_db_path = str(settings.chroma_db_path)
    collection_name = settings.collection_name
    embedding_model = settings.embedding_model

    print_separator("ChromaDB Collection Debug Analysis")
    print(f"ChromaDB Path: {Path(chroma_db_path).resolve()}")
    print(f"Collection Name: {collection_name}")
    print(f"Embedding Model: {embedding_model}")

    try:
        # Initialize ChromaDB client
        print_separator("1. Connecting to ChromaDB")
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        print("✅ Successfully connected to ChromaDB")

        # List all collections
        collections = chroma_client.list_collections()
        print(f"📦 Total collections found: {len(collections)}")
        for col in collections:
            print(f"   - {col.name}")

        # Get the specific collection
        print_separator("2. Accessing Target Collection")
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )

        try:
            collection = chroma_client.get_collection(
                name=collection_name, embedding_function=embedding_function
            )
            print(f"✅ Successfully accessed collection: {collection_name}")
        except Exception as e:
            print(f"❌ Failed to access collection: {e}")
            return

        # Get basic collection stats
        print_separator("3. Collection Statistics")
        total_count = collection.count()
        print(f"📊 Total documents in collection: {total_count}")

        if total_count == 0:
            print("⚠️ Collection is empty! No documents to analyze.")
            return

        # Get all documents with metadata
        print_separator("4. Fetching All Documents")
        all_docs = collection.get(include=["documents", "metadatas", "embeddings"])
        print(f"📄 Retrieved {len(all_docs['ids'])} documents")

        # Analyze categories
        print_separator("5. Category Analysis")
        categories = {}
        commit_docs = []

        for i, (doc_id, metadata) in enumerate(
            zip(all_docs["ids"], all_docs["metadatas"])
        ):
            category = metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

            # Collect commit documents
            if category == "commit_history":
                commit_docs.append(
                    {
                        "id": doc_id,
                        "metadata": metadata,
                        "content": all_docs["documents"][i][:100] + "..."
                        if len(all_docs["documents"][i]) > 100
                        else all_docs["documents"][i],
                    }
                )

        print("📊 Documents by category:")
        for category, count in categories.items():
            print(f"   - {category}: {count} documents")

        # Analyze commit documents specifically
        print_separator("6. Commit History Documents Analysis")
        print(f"🔍 Found {len(commit_docs)} commit documents")

        if commit_docs:
            print("\n📋 Commit Documents Details:")
            for i, commit_doc in enumerate(commit_docs[:10]):  # Show first 10
                print(f"\n--- Commit {i + 1} ---")
                print(f"ID: {commit_doc['id']}")
                print(f"Content (first 100 chars): {commit_doc['content']}")
                print("Metadata:")
                for key, value in commit_doc["metadata"].items():
                    print(f"  {key}: {value}")
                if i >= 9 and len(commit_docs) > 10:
                    print(f"\n... and {len(commit_docs) - 10} more commit documents")
                    break
        else:
            print("❌ No commit documents found!")

            # Check for any documents that might be commits with different categories
            print(
                "\n🔍 Searching for potential commit documents with other categories..."
            )
            for i, (doc_id, metadata, content) in enumerate(
                zip(all_docs["ids"], all_docs["metadatas"], all_docs["documents"])
            ):
                if any(
                    keyword in content.lower()
                    for keyword in ["commit", "git", "hash", "diff"]
                ):
                    print("\nPotential commit document found:")
                    print(f"ID: {doc_id}")
                    print(f"Category: {metadata.get('category', 'unknown')}")
                    print(f"Content preview: {content[:100]}...")

        # Test where filtering
        print_separator("7. Testing Where Filtering")

        # Test filtering by category
        try:
            commit_filter_results = collection.get(
                where={"category": "commit_history"}, include=["documents", "metadatas"]
            )
            print("✅ Where filter test successful")
            print(
                f"   Documents with category='commit_history': {len(commit_filter_results['ids'])}"
            )

            if commit_filter_results["ids"]:
                print(f"   Sample IDs: {commit_filter_results['ids'][:3]}")
        except Exception as e:
            print(f"❌ Where filter test failed: {e}")

        # Test different category values that might exist
        for test_category in ["commits", "commit", "git", "general_documentation"]:
            try:
                test_results = collection.get(
                    where={"category": test_category}, include=["metadatas"]
                )
                if test_results["ids"]:
                    print(
                        f"   Found {len(test_results['ids'])} documents with category='{test_category}'"
                    )
            except Exception:  # Fixed E722
                pass

        # Test embedding search for commit content
        print_separator("8. Testing Embedding Search")

        # Initialize embedding model for search
        try:
            _ = SentenceTransformer(embedding_model)  # Fixed F841
            print(f"✅ Loaded embedding model: {embedding_model}")

            # Test queries related to commits
            test_queries = [
                "git commit changes",
                "code changes diff",
                "commit history",
                "repository commits",
            ]

            for query in test_queries:
                print(f"\n🔍 Testing query: '{query}'")
                try:
                    # Test with no filters
                    results = collection.query(
                        query_texts=[query],
                        n_results=3,
                        include=["documents", "metadatas", "distances"],
                    )

                    print(f"   Results found: {len(results['ids'][0])}")
                    for i, (doc_id, distance) in enumerate(
                        zip(results["ids"][0], results["distances"][0])
                    ):
                        similarity = 1 - distance
                        metadata = results["metadatas"][0][i]
                        category = metadata.get("category", "unknown")
                        print(
                            f"   {i + 1}. ID: {doc_id}, Category: {category}, Similarity: {similarity:.3f}"
                        )

                except Exception as e:
                    print(f"   ❌ Query failed: {e}")

                # Test with commit category filter
                try:
                    filtered_results = collection.query(
                        query_texts=[query],
                        n_results=3,
                        where={"category": "commit_history"},
                        include=["documents", "metadatas", "distances"],
                    )
                    print(
                        f"   Filtered results (commit_history): {len(filtered_results['ids'][0])}"
                    )

                except Exception as e:
                    print(f"   ❌ Filtered query failed: {e}")

        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")

        print_separator("9. Checking Source Data")
        print(
            f"🔍 Checking commit directory: {settings.commit_cache_dir}"
        )  # Fixed F821

        if settings.commit_cache_dir.exists():  # Fixed F821
            commit_files = list(
                settings.commit_cache_dir.glob("commit_*.json")
            )  # Fixed F821
            print(f"✅ Found {len(commit_files)} commit files in source directory")

            if commit_files:
                # Sample a commit file
                sample_file = commit_files[0]
                try:
                    with open(sample_file, "r", encoding="utf-8") as f:
                        sample_commit = json.load(f)
                    print(f"\n📄 Sample commit file ({sample_file.name}):")
                    print(f"   Structure: {list(sample_commit.keys())}")
                    if "metadata" in sample_commit:
                        print(
                            f"   Metadata keys: {list(sample_commit['metadata'].keys())}"
                        )
                    if "what_changed" in sample_commit:
                        print(
                            f"   Commit message: {sample_commit['what_changed'][:100]}..."
                        )
                except Exception as e:
                    print(f"   ❌ Failed to read sample commit: {e}")
        else:
            print(
                f"❌ Commit directory not found: {settings.commit_cache_dir}"
            )  # Fixed F821

        # Summary and recommendations
        print_separator("10. Summary and Recommendations")

        if len(commit_docs) > 0:
            print("✅ Commit documents are properly indexed in ChromaDB")
            print(f"   - {len(commit_docs)} commit documents found")
            print("   - Category filtering appears to be working")
            print(
                "   - If search API isn't finding them, check the search endpoint logic"
            )
        else:
            print("❌ No commit documents found in ChromaDB")
            print("   Possible issues:")
            print("   1. Commit indexing script hasn't run successfully")
            print("   2. Category field is set incorrectly during indexing")
            print("   3. Commits were indexed with a different category name")
            print("   4. Collection was cleared after indexing")

        print("\n📈 Collection Health:")
        print(f"   - Total documents: {total_count}")
        print(f"   - Categories found: {len(categories)}")
        print(f"   - Commit documents: {len(commit_docs)}")

        if total_count > 0 and len(commit_docs) == 0:
            print("\n🔧 Recommended actions:")
            print("   1. Re-run the commit indexing process")
            print("   2. Check the ingest_commits.py script for errors")
            print("   3. Verify the .rag_commits directory contains commit files")
            print("   4. Check the indexing logs for any errors")

    except Exception as e:
        print(f"❌ Critical error in debug analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🐛 ChromaDB Debug Script")
    print(
        "This script will analyze your ChromaDB collection to identify commit indexing issues."
    )
    print()

    # Change to the script's directory to ensure relative paths work
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    analyze_chromadb_collection()

    print("\n" + "=" * 60)
    print(" Debug analysis complete!")
    print("=" * 60)
