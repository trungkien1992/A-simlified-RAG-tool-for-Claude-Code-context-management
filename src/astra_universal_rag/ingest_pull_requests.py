import os
import sys
import requests
import json
from pathlib import Path

# --- Configuration ---
REPO_OWNER = "trungkien1992"
REPO_NAME = "Astra-Project"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Securely load your token
OUTPUT_DIR = Path(__file__).resolve().parent.parent / ".rag_pull_requests"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_pull_requests():
    """Fetches all pull requests from the repository."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=all&per_page=100"
    prs = []
    page = 1
    while True:
        paged_url = url + f"&page={page}"
        response = requests.get(paged_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        prs.extend(data)
        page += 1
    return prs


def get_pr_comments(pr_number: int):
    """Fetches comments for a specific pull request."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_number}/comments"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def main():
    """Main execution function."""
    if not GITHUB_TOKEN:
        print("[FATAL] GITHUB_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    print("[INFO] Ingesting pull request history for RAG...")

    pull_requests = get_pull_requests()
    print(f"[INFO] Found {len(pull_requests)} pull requests to process.")

    for pr in pull_requests:
        pr_number = pr["number"]
        try:
            comments = get_pr_comments(pr_number)

            comment_text = "\n".join(
                [f"Comment by {c['user']['login']}:\n{c['body']}" for c in comments]
            )

            content = (
                f"Pull Request #{pr_number}: {pr['title']}\n\n"
                f"Author: {pr['user']['login']}\n"
                f"Status: {pr['state']}\n"
                f"Date: {pr['created_at']}\n\n"
                f"Description:\n{pr['body']}\n\n"
                f"--- Comments ---\n{comment_text}"
            )

            memory_card = {
                "content": content,
                "metadata": {
                    "doc_type": "pull_request",
                    "pr_number": pr_number,
                    "author": pr["user"]["login"],
                    "url": pr["html_url"],
                    "state": pr["state"],
                    "created_at": pr["created_at"],
                    "merged_at": pr.get("merged_at"),
                },
            }

            out_path = OUTPUT_DIR / f"pr_{pr_number}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(memory_card, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[WARN] Failed to process PR #{pr_number}: {e}", file=sys.stderr)

    print(f"[DONE] Pull request memory cards saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
