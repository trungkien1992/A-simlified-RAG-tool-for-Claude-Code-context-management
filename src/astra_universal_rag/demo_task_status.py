#!/usr/bin/env python3
"""
Demo script showing the task status tracking system
"""

import time
import requests
import json

BASE_URL = "http://localhost:8000"


def demo_task_status():
    """Demonstrate the task status tracking system"""
    print("🚀 Task Status Tracking Demo")
    print("=" * 40)

    # Step 1: Start a task
    print("1. Starting a code-aware indexing task...")
    response = requests.post(f"{BASE_URL}/index/code_aware")

    if response.status_code == 200:
        task_info = response.json()
        task_id = task_info["task_id"]
        print(f"   ✅ Task started with ID: {task_id}")
        print(f"   📝 Response: {json.dumps(task_info, indent=2)}")

        # Step 2: Check initial status
        print("\n2. Checking initial task status...")
        status_response = requests.get(f"{BASE_URL}/status/{task_id}")

        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   📊 Status: {json.dumps(status, indent=2)}")

            # Step 3: Wait and check final status
            print("\n3. Waiting for task completion...")
            time.sleep(1)

            final_status_response = requests.get(f"{BASE_URL}/status/{task_id}")
            if final_status_response.status_code == 200:
                final_status = final_status_response.json()
                print(f"   📊 Final Status: {json.dumps(final_status, indent=2)}")

                if final_status["status"] == "completed":
                    print(
                        f"   ✅ Task completed in {final_status.get('time_taken', 'unknown')}s"
                    )
                elif final_status["status"] == "failed":
                    print(f"   ❌ Task failed: {final_status.get('error', 'unknown')}")
                else:
                    print("   ⏳ Task still in progress")
            else:
                print(
                    f"   ❌ Failed to get final status: {final_status_response.status_code}"
                )
        else:
            print(f"   ❌ Failed to get initial status: {status_response.status_code}")
    else:
        print(f"   ❌ Failed to start task: {response.status_code}")

    # Step 4: Test invalid task ID
    print("\n4. Testing invalid task ID handling...")
    invalid_response = requests.get(f"{BASE_URL}/status/invalid-task-id")
    if invalid_response.status_code == 404:
        print("   ✅ Correctly returned 404 for invalid task ID")
        print(f"   📝 Response: {json.dumps(invalid_response.json(), indent=2)}")
    else:
        print(f"   ❌ Expected 404, got {invalid_response.status_code}")

    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    demo_task_status()
