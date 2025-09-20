"""
Ragger SDK - Python client for the Ragger RAG (Retrieval Augmented Generation) API.

This SDK provides a simple and intuitive interface to interact with Ragger's
document processing, vector indexing, and query capabilities. It's designed to be
beginner-friendly while offering the full power of the Ragger platform.

What is RAG (Retrieval Augmented Generation)?
============================================
RAG is an AI technique that combines information retrieval with text generation.
Instead of relying solely on a language model's training data, RAG systems:

1. **Retrieve** relevant information from your documents
2. **Augment** the AI's context with that information
3. **Generate** responses that are grounded in your actual data

This makes AI responses more accurate, up-to-date, and specific to your domain.

Core Concepts:
==============
- **Organization**: A top-level container for all your projects
- **Project**: A collection of related documents and their vector index
- **Document**: Individual files (PDF, Word, text, etc.) that contain your data
- **Index**: A searchable vector representation of your documents
- **Query**: A natural language question that gets answered using your documents
- **Session**: A conversation thread that maintains context across multiple queries

Basic Usage Example:
===================
    # Import the main client class
    from ragger_sdk import RaggerClient

    # Initialize the client with your API details
    client = RaggerClient(
        base_url="http://ragger.local:8025/rag/api/v1",  # Your Ragger server URL
        token="your-api-token"  # Your authentication token
    )

    # Step 1: Upload documents to create your knowledge base
    upload_result = client.documents.upload(
        organization="my-company",     # Your organization name
        project="product-docs",        # Project to organize documents
        name="user-manual",           # Descriptive name for the document
        file_path="/path/to/manual.pdf"  # Path to your document file
    )

    # Step 2: Create a searchable index from your documents
    index_result = client.index.create_index(
        organization="my-company",
        project="product-docs"
    )

    # Step 3: Ask questions about your documents
    answer = client.query.ask(
        query="How do I reset my password?",  # Your question in natural language
        organization="my-company",
        project="product-docs",
        user="support@company.com"  # User identifier for conversation tracking
    )

    print(f"Answer: {answer['answer']}")
    print(f"Based on {len(answer['metadata']['source_nodes'])} sources")

Advanced Usage:
===============
The SDK supports conversation continuity, metadata filtering, custom AI models,
and comprehensive error handling. See individual module documentation for details.
"""

# Import the main client class - this is the primary entry point for the SDK
from .client import RaggerClient
from .endpoints.documents_from_file import DocumentsFromFileAPI
from .endpoints.index import IndexAPI
from .endpoints.query import QueryAPI
from .exceptions import RaggerAPIError

# Package metadata - version and author information
__version__ = "0.1.0"
__author__ = "Ragger Team"
__description__ = "Python SDK for Ragger RAG API"

# Define what gets imported when someone does "from ragger_sdk import *"
# This follows Python best practices by explicitly controlling the public API
__all__ = [
    # Main client class - the primary interface most users will need
    "RaggerClient",
    "RaggerAPIError"
]
