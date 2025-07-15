.PHONY: setup run test clean

PYTHON := python3
PIP := $(PYTHON) -m pip
VENV_DIR := .venv

# Define the main CLI entrypoint
CLI := $(PYTHON) main.py

# Default target
all: setup run

# Setup the environment
setup:
	@echo "Setting up Python virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV_DIR)/bin/activate && $(PIP) install -r src/requirements.txt
	@echo "Environment setup complete. To activate: source $(VENV_DIR)/bin/activate"

# Run the FastAPI application
run:
	@echo "Starting the Astra - Universal RAG API..."
	. $(VENV_DIR)/bin/activate && $(CLI) run-api --host 0.0.0.0 --port 8000 --reload

# Ingest commits (example usage)
ingest-commits:
	@echo "Ingesting commits..."
	. $(VENV_DIR)/bin/activate && $(CLI) ingest-commits --repo-path .

# Ingest pull requests (example usage)
ingest-pull-requests:
	@echo "Ingesting pull requests (placeholder)..."
	. $(VENV_DIR)/bin/activate && $(CLI) ingest-pull-requests --repo-url "https://github.com/example/repo"

# Run tests
test:
	@echo "Running tests..."
	. $(VENV_DIR)/bin/activate && $(PYTHON) -m pytest

# Clean up generated files and directories
clean:
	@echo "Cleaning up generated files and directories..."
	rm -rf $(VENV_DIR)
	rm -rf data/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +
	rm -f server.log
	rm -f citation_accuracy_results.json
	rm -f performance_benchmark_results.json
	rm -f quality_assessment_test_results.json
	rm -f rag_categorization_test_results.json
	@echo "Cleanup complete."
