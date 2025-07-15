import typer
import uvicorn
from pathlib import Path
import os

from astra_universal_rag.config import settings
from astra_universal_rag.ingestion.ingest_commits import main as ingest_commits_main
from astra_universal_rag.ingestion.ingest_pull_requests import (
    main as ingest_pull_requests_main,
)
from astra_universal_rag.main import app as fastapi_app  # Import the FastAPI app

cli_app = typer.Typer(
    help="Astra - Universal RAG CLI. Manage ingestion, run the API, and more."
)


@cli_app.command(name="ingest-commits")
def ingest_commits(
    repo_path: str = typer.Option(
        ...,
        "--repo-path",
        "-r",
        help="Path to the Git repository to ingest commits from.",
    ),
    output_dir: Path = typer.Option(
        settings.commit_cache_dir,
        "--output-dir",
        "-o",
        help="Output directory for memory cards. Defaults to configured commit cache directory.",
    ),
):
    """
    Ingests commit history from a Git repository.
    """
    typer.echo(f"Ingesting commits from: {repo_path}")
    typer.echo(f"Outputting to: {output_dir}")

    # Temporarily change the current working directory to the repo_path
    original_cwd = os.getcwd()
    try:
        os.chdir(repo_path)
        # Call the main function from ingest_commits.py
        # Note: ingest_commits_main expects no arguments as it uses global config
        ingest_commits_main()
    except Exception as e:
        typer.echo(f"Error during commit ingestion: {e}", err=True)
    finally:
        os.chdir(original_cwd)  # Change back to original CWD


@cli_app.command(name="ingest-pull-requests")
def ingest_pull_requests(
    repo_url: str = typer.Option(
        ...,
        "--repo-url",
        "-u",
        help="URL of the Git repository (e.g., GitHub) to ingest pull requests from.",
    ),
    output_dir: Path = typer.Option(
        settings.commit_cache_dir,
        "--output-dir",
        "-o",  # Reusing commit_cache_dir for PRs for now
        help="Output directory for pull request memory cards. Defaults to configured commit cache directory.",
    ),
):
    """
    Ingests pull request data from a Git repository (e.g., GitHub).
    """
    typer.echo(f"Ingesting pull requests from: {repo_url}")
    typer.echo(f"Outputting to: {output_dir}")

    # Call the main function from ingest_pull_requests.py
    # Note: ingest_pull_requests_main expects no arguments as it uses global config
    ingest_pull_requests_main()


@cli_app.command(name="run-api")
def run_api(
    host: str = typer.Option(
        "0.0.0.0", "--host", "-h", help="Host for the API server."
    ),
    port: int = typer.Option(8000, "--port", "-p", help="Port for the API server."),
    reload: bool = typer.Option(
        False, "--reload", help="Enable auto-reload for development."
    ),
):
    """
    Runs the FastAPI application.
    """
    typer.echo(f"Starting FastAPI server on http://{host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli_app()
