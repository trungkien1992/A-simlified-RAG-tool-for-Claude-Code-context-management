#!/usr/bin/env python3
"""
Test Commit RAG Integration

This script verifies that the commit memory cards are correctly indexed and retrievable by the RAG system.

It performs the following steps:
1. Triggers a full re-index of the knowledge base, including the new commit history.
2. Waits for the indexing task to complete.
3. Performs a series of targeted searches against the indexed commits.
4. Prints the results to validate that commit messages, authors, and code changes are found.
"""

import sys
import requests
import time

# --- Configuration ---
# This is where you would place your actual API key.
API_KEY = "Astra_rag_9e2f4c7b8a1d4e5fbc2a7d6e3c1b0a9f"
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json", "X-API-KEY": API_KEY}


def trigger_reindex() -> str:
    """Triggers the RAG system's indexing endpoint and returns the task ID."""
    print("[INFO] Triggering full re-index of the RAG system...")
    payload = {"force_reindex": True}
    response = requests.post(f"{BASE_URL}/index", headers=HEADERS, json=payload)

    if response.status_code == 403:
        print(
            "[FATAL] API Key is invalid or missing. Please update the API_KEY in this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    response.raise_for_status()  # Raise an exception for other HTTP errors

    task_id = response.json().get("task_id")
    if not task_id:
        print(
            "[FATAL] Failed to get a task ID from the indexing endpoint.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[SUCCESS] Indexing task started with ID: {task_id}")
    return task_id


def wait_for_task(task_id: str):
    """Polls the status endpoint until the task is completed."""
    print(f"[INFO] Waiting for task {task_id} to complete...")
    while True:
        try:
            response = requests.get(f"{BASE_URL}/status/{task_id}")
            response.raise_for_status()
            status_data = response.json()

            if status_data.get("status") == "completed":
                print("[SUCCESS] Task completed.")
                print(f"  - Time taken: {status_data.get('time_taken', 'N/A'):.2f}s")
                print(
                    f"  - Documents indexed: {status_data.get('documents_indexed', 'N/A')}"
                )
                break
            elif status_data.get("status") == "failed":
                print(
                    f"[FATAL] Task failed: {status_data.get('error', 'Unknown error')}",
                    file=sys.stderr,
                )
                sys.exit(1)

            time.sleep(2)  # Wait 2 seconds before polling again
        except requests.RequestException as e:
            print(
                f"[WARN] Could not get task status: {e}. Retrying...", file=sys.stderr
            )
            time.sleep(5)


def run_test_queries():
    """Runs a series of test queries to validate commit ingestion."""
    print("\n" + "=" * 50)
    print("[INFO] Running test queries against commit history...")
    print("=" * 50 + "\n")

    test_queries = [
        {
            "description": "Search for a specific commit message about the leaderboard.",
            "query": "Implement the Leaderboard Screen & XP System",
            "expected_in_content": ["leaderboard.dart", "leaderboard_provider.dart"],
        },
        {
            "description": "Search for an author.",
            "query": "trungkien1992",
            "expected_in_content": ["author"],
        },
        {
            "description": "Search for a specific code change (a new function).",
            "query": "class TestConfig",
            "expected_in_content": ["test_config.dart", "test_client_id"],
        },
    ]

    all_passed = True
    for test in test_queries:
        print(f"--- Running Test: {test['description']} ---")
        print(f"  -> Querying for: '{test['query']}'")

        payload = {"query": test["query"], "max_results": 1}
        try:
            response = requests.post(
                f"{BASE_URL}/search", headers=HEADERS, json=payload
            )
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results:
                print("  [FAIL] No results returned.")
                all_passed = False
                continue

            top_result = results[0]
            content = top_result.get("content", "").lower()
            metadata = top_result.get("metadata", {})

            print(
                f"  -> Found doc type: '{metadata.get('type', 'N/A')}' with similarity {top_result.get('similarity', 0):.2f}"
            )

            passed = True
            for expected in test["expected_in_content"]:
                if expected.lower() not in content and expected not in metadata:
                    print(
                        f"  [FAIL] Expected to find '{expected}' in the result, but it was missing."
                    )
                    passed = False
                    all_passed = False

            if passed:
                print("  [PASS] All expected content found in the top result.")

        except requests.RequestException as e:
            print(f"  [FAIL] API request failed: {e}")
            all_passed = False
        print("-" * (len(test["description"]) + 20) + "\n")

    return all_passed


def main():
    """Main execution flow."""
    # Step 1: Trigger re-indexing
    task_id = trigger_reindex()

    # Step 2: Wait for indexing to finish
    wait_for_task(task_id)

    # Step 3: Run validation queries
    if run_test_queries():
        print(
            "\n✅ All integration tests passed! Commit history is successfully integrated into the RAG system."
        )
    else:
        print("\n❌ Some integration tests failed. Please review the output.")


if __name__ == "__main__":
    main()
