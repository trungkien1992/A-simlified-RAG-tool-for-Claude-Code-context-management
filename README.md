# Astra - Universal RAG

Astra - Universal RAG is a cutting-edge Retrieval-Augmented Generation (RAG) system designed to provide intelligent, context-aware responses by leveraging diverse data sources, including Git repositories, pull requests, and more. It aims to be a "god-level" project, offering unparalleled insights and a seamless developer experience.

## Features

*   **Universal Data Ingestion:** Ingests data from various sources, including Git commit history and pull requests.
*   **Code-Aware Chunking:** Intelligently processes code and documentation for optimal retrieval.
*   **Knowledge Graph Integration:** Builds and leverages a knowledge graph for enhanced context and relationships.
*   **Proactive Context Engine:** Anticipates user needs and provides relevant information proactively.
*   **Quality Assessment:** Ensures the accuracy and relevance of generated responses.
*   **Containerized Deployment:** Easily deployable using Docker.
*   **Unified CLI:** A single command-line interface for all operations.

## Quick Start

Follow these steps to get Astra - Universal RAG up and running on your local machine.

### Prerequisites

*   Python 3.9+ (recommended: use `pyenv` or `conda`)
*   Poetry (for dependency management)
*   Docker and Docker Compose (for running the application)
*   Git

### 1. Clone the Repository

```bash
git clone <repository_url>
cd astra-universal-rag
```

### 2. Install Dependencies

We use Poetry for dependency management. If you don't have Poetry installed, you can install it via `pip`:

```bash
pip install poetry
```

Then, install the project dependencies:

```bash
poetry install
```

### 3. Environment Configuration

Create a `.env` file in the project root based on `.env.example` and fill in your API keys and other configurations.

```bash
cp .env.example .env
# Open .env and add your API_KEY
```

### 4. Run the Application

Use the provided `Makefile` for easy management:

```bash
# Setup the environment (installs dependencies, creates virtual env)
make setup

# Run the FastAPI API server
make run
```

The API will be accessible at `http://localhost:8000`.

### 5. Ingest Data

Ingest commit history from a local Git repository (e.g., the current project):

```bash
make ingest-commits
```

### 6. Run Tests

```bash
make test
```

## CLI Usage

The project provides a unified command-line interface (`main.py`) for various operations. You can run it using `poetry run python main.py <command> [options]` or by activating the virtual environment and running `python main.py <command> [options]`.

```bash
# Get help for the CLI
poetry run python main.py --help

# Ingest commits from a specific repository path
poetry run python main.py ingest-commits --repo-path /path/to/your/git/repo

# Run the API server
poetry run python main.py run-api --host 0.0.0.0 --port 8000 --reload
```

## Project Structure

```
astra-universal-rag/
├── data/                 # Persistent data (ChromaDB, commit cache)
├── src/                  # Main application source code
│   └── astra_universal_rag/
│       ├── cli.py        # Unified CLI entrypoint
│       ├── config.py     # Centralized configuration
│       ├── ingestion/    # Data ingestion scripts
│       ├── ...           # Other core modules
├── .env.example          # Example environment variables
├── .gitignore            # Specifies intentionally untracked files to ignore
├── Makefile              # Convenient commands for development
├── pyproject.toml        # Poetry project configuration and dependencies
├── poetry.lock           # Poetry lock file for deterministic builds
├── README.md             # Project overview and quick start guide
└── main.py               # Main CLI entrypoint
```

## Contributing

We welcome contributions! Please see our `CONTRIBUTING.md` (coming soon) for guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
