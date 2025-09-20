"""
Ragger SDK API Endpoints Package

This package contains all the API endpoint implementations for the Ragger SDK.
Each module in this package handles a specific domain of operations in the
Ragger RAG (Retrieval Augmented Generation) system.

Package Organization:
====================

The endpoints are organized by functionality, following the main RAG workflow:

1. **documents.py** - Document Upload and Management
   - Upload files from local storage or URLs
   - Upload text content directly
   - Manage document metadata and validation
   - Handle async document processing tasks

2. **index.py** - Vector Index Creation and Management
   - Create searchable vector indices from uploaded documents
   - Monitor indexing progress and status
   - Configure embedding models and parameters
   - Manage index lifecycle and updates

3. **query.py** - Natural Language Querying and RAG
   - Ask questions using natural language
   - Get AI-generated answers grounded in your documents
   - Maintain conversation context across queries
   - Access source citations and metadata

4. **chat_history.py** - Chat Session and History Management
   - Retrieve conversation sessions for users
   - Access detailed message history
   - Get session summaries and statistics
   - Manage conversation context and continuity

Design Principles:
=================

**Separation of Concerns:**
Each endpoint module focuses on one specific area of functionality.
This makes the code easier to understand, maintain, and test.

**Consistent Interface:**
All endpoint classes follow the same pattern:
- Accept a RaggerClient instance in their constructor
- Provide high-level methods that handle common operations
- Include comprehensive parameter validation
- Return structured data from API responses

**Error Handling:**
All endpoint methods use the same exception hierarchy for consistent
error handling across the entire SDK.

**Documentation:**
Each method includes detailed docstrings with examples, parameter
descriptions, and usage guidance for developers.

Usage Pattern:
==============

These endpoint classes are typically accessed through the main RaggerClient:

    >>> from ragger_sdk import RaggerClient
    >>>
    >>> client = RaggerClient(base_url="...", token="...")
    >>>
    >>> # Access endpoints through the client
    >>> client.documents.upload(...)     # DocumentsFromFileAPI
    >>> client.index.create_index(...)        # IndexAPI
    >>> client.query.ask(...)                 # QueryAPI
    >>> client.chat_history.get_sessions(...) # ChatHistoryAPI

Advanced Usage:
==============

For advanced use cases, you can also instantiate endpoint classes directly:

    >>> from ragger_sdk import RaggerClient
    >>> from ragger_sdk.endpoints import DocumentsFromFileAPI
    >>>
    >>> client = RaggerClient(base_url="...", token="...")
    >>> documents_api = DocumentsFromFileAPI(client)
    >>>
    >>> # Use the endpoint directly
    >>> result = documents_api.upload(...)

This can be useful for:
- Creating specialized wrappers around specific functionality
- Building custom integrations that only need certain endpoints
- Testing individual endpoint functionality in isolation
"""

# Import all endpoint classes for easy access
# These are the main API interfaces that developers will use

from ragger_sdk.endpoints.documents_from_file import DocumentsFromFileAPI       # Document upload and management operations
from ragger_sdk.endpoints.documents_from_text import DocumentsFromTextAPI       # Document creation from text content
from ragger_sdk.endpoints.index import IndexAPI                                 # Vector index creation and management
from ragger_sdk.endpoints.query import QueryAPI                                 # Natural language querying and RAG functionality
from ragger_sdk.endpoints.chat_history import ChatHistoryAPI                    # Chat session and conversation history

# Define the public API for this package
# This controls what gets imported when someone does "from ragger_sdk.endpoints import *"
__all__ = [
    'DocumentsFromFileAPI',    # Handle document uploads and file management
    'DocumentsFromTextAPI',    # Handle text content uploads
    'IndexAPI',        # Create and manage vector indices for semantic search
    'QueryAPI',        # Process natural language queries and generate RAG responses
    'ChatHistoryAPI'   # Access and manage chat conversation history
]
