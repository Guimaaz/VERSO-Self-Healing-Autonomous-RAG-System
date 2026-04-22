Project VERSO
Self-Healing Autonomous RAG System

VERSO is a localized Intelligence Engine built to bridge the gap between static technical manuals and dynamic user memory. Powered by Ollama, it utilizes a dual-layer retrieval strategy to ensure high-fidelity responses, preventing hallucinations through a "Judge" mechanism and "Self-Healing" search loops.
Architecture Overview

VERSO operates on a Decoupled RAG Pipeline, separating the heavy processing of knowledge from the real-time execution of the AI.

    The Ingestor (ingest.py): The "Restorer." It processes Markdown files using a hierarchical split strategy (MarkdownHeader + RecursiveCharacter) to preserve semantic anchors.

    The Engine (engine.py): The "Operator." It handles real-time queries, manages conversation memory, and performs "Self-Healing" searches when initial data retrieval is insufficient.

    The Truth Layer: A persistent .md storage system where all long-term memory is kept in human-readable format.

Key Features
1. Hierarchical Semantic Split

Unlike standard RAG systems that cut text blindly, VERSO respects the structure of your data.

    Header Splitting: Uses # and ## as metadata anchors.

    Recursive Refinement: Ensures no chunk exceeds 600 tokens, maintaining optimal performance for local LLMs like Llama-3.

2. Self-Healing Retrieval

If the initial search yields low-relevance results, VERSO doesn't just guess. It triggers a Self-Healing Loop:

    Re-Querying: The system rewrites the search term to find better matches.

    Metadata Expansion: It uses the ## anchors to pull surrounding context from specific conversation IDs or manual chapters.

3. Local-First & Privacy-Focused

    Embeddings: Powered by nomic-embed-text via Ollama (8k context window).

    LLM: Optimized for Llama-3 8B running locally.

    Database: High-performance vector storage using ChromaDB.

Tech Stack
Component	Technology
Brain	Llama-3 (Ollama)
Embeddings	Nomic-Embed-Text
Vector Store	ChromaDB
Orchestration	LangChain
Format	Markdown (Structured)

    VERSO/
    ├── backend/
    │   ├── Data/
    │   │   └── Md/
    │   │       ├── manual.md      # Static technical knowledge
    │   │       └── memoria.md    # Dynamic persistent memory
    │   ├── db/                   # ChromaDB Vector Store (Persistent)
    │   ├── ingest.py             # Database builder & synchronizer
    │   └── engine.py             # Main AI Agent & Self-Healing logic
    └── README.md


Getting Started
1. Prepare the Knowledge

Place your technical manuals ( .md format ) and an empty memoria.md inside backend/Data/Md/. Ensure you use ## for sub-headers.
2. Build the "brain"

Run the ingestion script to transform your text into searchable vectors:

    python backend/ingest.py
3. Run VERSO

Start the engine to begin the interactive session:

    python backend/engine.py

