# Astra - Universal RAG: Architecture Overview

This document provides a high-level overview of the architecture of Astra - Universal RAG, outlining its core components and their interactions.

## 1. Core Philosophy

Astra - Universal RAG is designed as a modular, extensible, and data-agnostic Retrieval-Augmented Generation system. Its primary goal is to provide intelligent, context-rich responses by integrating information from diverse sources, particularly focusing on software engineering data (Git commits, pull requests, codebases).

## 2. High-Level Components

![Astra RAG Architecture Diagram Placeholder](https://via.placeholder.com/800x400?text=Astra+RAG+Architecture+Diagram)

### 2.1. Data Ingestion Layer

This layer is responsible for collecting raw data from various sources and transforming it into a structured format suitable for the RAG system.

*   **Sources:** Git repositories (commits, diffs), Pull Request APIs (GitHub, GitLab), potentially documentation, wikis, issue trackers, etc.
*   **Components:**
    *   `ingest_commits.py`: Extracts commit history, messages, and diffs.
    *   `ingest_pull_requests.py`: (Placeholder) Will fetch PR data.
    *   **Code-Aware Chunker (`code_aware_chunker.py`):** A critical component that intelligently splits code and text into meaningful chunks, preserving context (e.g., not splitting a function definition across chunks).

### 2.2. Knowledge Base Layer

This layer stores and manages the processed data, making it efficiently retrievable.

*   **ChromaDB:** The primary vector store for storing document embeddings and metadata. It allows for semantic search and retrieval of relevant information.
*   **Commit Cache (`.rag_commits`):** A local cache of processed commit JSON files, serving as the ground truth for ingestion and debugging.
*   **Knowledge Graph (`graph_models.py`, `graph_search.py`):** A Neo4j-based (or similar) graph database that stores entities (e.g., Developers, Commits, Files, Features) and their relationships. This enables complex queries and contextual understanding beyond simple keyword matching.

### 2.3. RAG Core Layer

This is the heart of the system, orchestrating the retrieval and generation processes.

*   **RAG System (`rag_system.py`):** The main orchestrator. It receives user queries, determines relevant data sources, retrieves information from the Knowledge Base, and passes it to the LLM for generation.
*   **Embedding Models:** Used to convert text (queries, documents) into numerical vectors for semantic search in ChromaDB.
*   **LLM Integration:** Interfaces with large language models (e.g., Claude, OpenAI GPT) to generate human-like responses based on retrieved context.
*   **Proactive Context Engine (`proactive_context_engine.py`):** (Future/Advanced) A component designed to anticipate user needs and pre-fetch or pre-process relevant context, improving response time and relevance.

### 2.4. API & CLI Layer

This layer provides interfaces for users and other applications to interact with the RAG system.

*   **FastAPI (`main.py`):** Provides a RESTful API for programmatic access to the RAG system, enabling integration with other applications.
*   **Typer CLI (`cli.py`):** A unified command-line interface for managing the system, including data ingestion, running the API, and debugging.

## 3. Data Flow (Simplified)

1.  **Ingestion:** Raw data (e.g., Git commits) is fed into the Data Ingestion Layer.
2.  **Processing:** The data is chunked, relevant entities are extracted for the Knowledge Graph, and text is embedded.
3.  **Storage:** Embeddings and metadata are stored in ChromaDB. Graph entities and relationships are stored in the Knowledge Graph.
4.  **Query:** A user submits a query via the CLI or API.
5.  **Retrieval:** The RAG Core Layer uses the query to retrieve relevant documents from ChromaDB (semantic search) and contextual information from the Knowledge Graph (relationship traversal).
6.  **Augmentation & Generation:** The retrieved context is combined with the user's query and sent to an LLM. The LLM generates a coherent and informed response.
7.  **Response:** The generated response is returned to the user.

## 4. Future Enhancements

*   **Advanced Ingestion:** Support for more data sources (e.g., Confluence, Jira, Slack).
*   **Feedback Loop:** Incorporating user feedback to improve retrieval and generation quality.
*   **Multi-modal RAG:** Handling and integrating non-textual data (e.g., images, diagrams).
*   **Deployment Automation:** More sophisticated deployment scripts and CI/CD integration.

This architecture provides a robust foundation for building an intelligent and highly effective RAG system.
