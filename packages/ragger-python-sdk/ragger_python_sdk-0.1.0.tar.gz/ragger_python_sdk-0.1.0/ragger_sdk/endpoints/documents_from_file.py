"""
Documents API module for the Ragger SDK.

This module provides functionality for uploading and managing documents through
the Ragger API's document endpoints. It's the first step in the RAG workflow:
you upload your source documents here, which are then processed and made
searchable by the vector indexing system.

Key Features:
============

**Multiple Upload Methods:**
- File uploads from local storage with automatic content-type detection
- Direct text content uploads without creating temporary files
- Support for various document formats (PDF, Word, text, markdown, etc.)

**Smart Validation:**
- Pre-upload file validation with detailed feedback
- File size and format checking with recommendations
- Clear error messages for common upload issues

**Rich Metadata Support:**
- Attach custom metadata to documents for filtering and organization
- JSON-encoded metadata that's preserved through the processing pipeline
- Metadata becomes available in search results and citations

**Async Processing Integration:**
- Returns task IDs for tracking document processing status
- Handles large documents that require background processing
- Integrates with the task monitoring system

**Organization and Project Management:**
- Multi-tenant document isolation by organization and project
- Force overwrite capabilities for document updates
- Consistent naming and identification across the system

Common Use Cases:
================

1. **Knowledge Base Building:**
   Upload company documentation, manuals, and wikis to create a searchable
   knowledge base for customer support or internal teams.

2. **Research Document Processing:**
   Upload academic papers, research notes, and reports to enable
   research question answering and citation tracking.

3. **Legal Document Management:**
   Upload contracts, policies, and legal documents for compliance
   and legal research applications.

4. **Content Management:**
   Upload blog posts, articles, and marketing content for content
   discovery and automated summarization.

Document Processing Pipeline:
============================

1. **Upload** (this module) - Documents are uploaded with metadata
2. **Processing** (server-side) - Text is extracted and cleaned
3. **Chunking** (server-side) - Documents are split into searchable chunks
4. **Embedding** (server-side) - Chunks are converted to vector representations
5. **Indexing** (index module) - Vectors are stored in searchable database
6. **Querying** (query module) - Natural language queries find relevant chunks

Best Practices:
===============

- **Use Descriptive Names**: Choose clear, unique names for documents
- **Add Metadata**: Include relevant metadata for better organization
- **Validate First**: Use validate_file() to check documents before upload
- **Monitor Tasks**: Check processing status for large documents
- **Organize by Project**: Use organization/project hierarchy effectively
"""

import json
import mimetypes
import logging

from typing import Optional
from typing import Dict
from typing import Any
from typing import Union
from pathlib import Path

from ragger_sdk.exceptions import RaggerAPIError
from ragger_sdk.constants import ErrorCodes
from ragger_sdk.endpoints.documents_base import DocumentsBaseAPI

logger = logging.getLogger(__name__)

class DocumentsFromFileAPI(DocumentsBaseAPI):
    """
    Interface for document-related operations in the Ragger API.

    This class handles all document upload and management operations. It provides
    a high-level interface for the most common document operations while handling
    the technical details of file uploads, metadata encoding, and error handling.

    The DocumentsFromFileAPI is designed to be:
    - **Easy to Use**: Simple method calls with clear parameters
    - **Robust**: Comprehensive validation and error handling
    - **Flexible**: Support for both file and text uploads
    - **Informative**: Detailed feedback and recommendations

    Key Concepts:
    ============

    **Document Names:**
    Each document has a unique name within a project. This name is used for
    identification, deduplication, and retrieval. Choose descriptive names
    that will help you identify documents later.

    **Organizations and Projects:**
    Documents are organized in a hierarchical structure:
    Organization → Project → Documents

    This provides multi-tenant isolation and logical grouping of related documents.

    **Metadata:**
    Optional key-value pairs that provide additional context about documents.
    Metadata is preserved through processing and can be used for filtering
    and organization in search results.

    **Force Overwrite:**
    By default, uploading a document with an existing name will fail.
    Set force_overwrite=True to replace existing documents.

    Workflow Integration:
    ====================

    Documents uploaded through this API are processed asynchronously:
    1. Upload returns immediately with a task ID
    2. Server extracts text and metadata in the background
    3. Use the task monitoring system to check processing status
    4. Once processed, documents are ready for vector indexing

    Example Usage:
        >>> # Initialize the API through the main client
        >>> client = RaggerClient(base_url="...", token="...")
        >>> docs_api = client.documents
        >>>
        >>> # Upload a local file
        >>> result = docs_api.upload(
        ...     file_path="/docs/manual.pdf",
        ...     name="user-manual",
        ...     organization="my-company",
        ...     project="product-docs",
        ...     metadata={"version": "2.1", "department": "engineering"}
        ... )
        >>>
        >>> # Upload text content directly
        >>> result = docs_api.upload(
        ...     text_content="Important meeting notes from today...",
        ...     name="meeting-notes-2024-01-15",
        ...     organization="my-company",
        ...     project="internal-docs"
        ... )
    """


    def upload(
        self,
        file_path: Union[str, Path],
        name: str,
        organization: str,
        project: str,
        system_prompt: Optional[str] = None,
        text_search_config: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Any]:

        # Convert file path to Path object for robust file handling
        # This provides better cross-platform compatibility and error handling
        file_path = Path(file_path)

        # Verify file exists and is accessible
        # Check both existence and that it's actually a file (not a directory)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise RaggerAPIError(f"Path is not a file: {file_path}")

        # Detect MIME content type for proper HTTP upload
        # This helps the server understand how to process the file
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            # Fall back to binary if we can't detect the type
            # Server will attempt to detect format based on content
            content_type = 'application/octet-stream'

        # Prepare form data for multipart upload
        # The API expects specific field names and formats
        form_data = {
            'name': name.strip(),                           # Clean whitespace from name
            'organization': organization.strip(),           # Clean whitespace from organization
            'project': project.strip(),                     # Clean whitespace from project
            'system_prompt': system_prompt.strip() if system_prompt else "", # Optional system prompt
            'text_search_config': text_search_config.strip() if text_search_config else "",  # Optional text search config
            'metadata': json.dumps(metadata) if metadata else "{}",  # JSON-encode metadata dictionary
            'force_overwrite': str(force_overwrite).lower(), # Convert boolean to string ("true"/"false")

        }

        # Debug: Log the exact form data being sent
        logger.debug(f"📤 Form data being sent to server:")
        for key, value in form_data.items():
            if key == 'metadata':
                logger.debug(f"   {key} = {value[:100]}{'...' if len(str(value)) > 100 else ''}")
            else:
                logger.debug(f"   {key} = '{value}' (length: {len(str(value))})")

        # Perform the actual file upload
        # Use a context manager to ensure the file is properly closed
        try:
            with open(file_path, 'rb') as f:
                # Prepare file data for multipart upload
                # Format: (filename, file_object, content_type)
                files = {
                    'document': (file_path.name, f, content_type)
                }

                # Make the API request using the client's POST method
                # This handles authentication, URL building, and error processing
                response = self._client.post(
                    endpoint='/documents/file/',  # Document upload endpoint
                    data=form_data,              # Form fields (name, org, project, etc.)
                    files=files,                  # File data for upload
                )

                return response

        except IOError as e:
            # Handle file reading errors (permissions, disk issues, etc.)
            raise RaggerAPIError(f"Failed to read file {file_path}: {str(e)}")
