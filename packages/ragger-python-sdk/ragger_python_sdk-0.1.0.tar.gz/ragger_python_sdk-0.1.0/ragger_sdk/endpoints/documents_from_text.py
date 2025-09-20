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

from typing import Optional
from typing import Dict
from typing import Any
from io import BytesIO

from ragger_sdk.exceptions import RaggerAPIError
from ragger_sdk.constants import ErrorCodes
from ragger_sdk.endpoints.documents_base import DocumentsBaseAPI


class DocumentsFromTextAPI(DocumentsBaseAPI):
    """

    Example Usage:
        >>> # Initialize the API through the main client
        >>> client = RaggerClient(base_url="...", token="...")
        >>> docs_api = client.documents
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
        text_content: str,
        name: str,
        organization: str,
        project: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force_overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Upload text content directly without creating a physical file.

        This method allows you to upload text content directly as a document
        without having to save it to a file first. This is useful for:
        - Programmatically generated content
        - Text extracted from APIs or databases
        - Content created dynamically in your application
        - Small text snippets that don't warrant file creation

        The text is uploaded as a virtual file and processed the same way
        as uploaded files, going through the same text extraction and
        chunking pipeline.

        Args:
            text_content (str): The text content to upload. Must be non-empty
                              and contain meaningful content for processing.

            name (str): Unique identifier for this document within the project.
                       Choose descriptive names that reflect the content.

            organization (str): Organization identifier for multi-tenant isolation.

            project (str): Project identifier within the organization.

            filename (str, optional): Filename to assign to the virtual file.
                                    Defaults to "{name}.txt" if not provided.
                                    The extension helps with content type detection.

            metadata (dict, optional): Additional key-value pairs to associate
                                     with the document for organization and filtering.

            force_overwrite (bool, optional): Whether to replace an existing document
                                            with the same name. Default is False.

        Returns:
            dict: API response containing upload confirmation and processing information,
                 including task_id for monitoring processing progress.

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty text_content or invalid parameters
                           - .is_server_error() for network errors, server issues, or API problems

        Examples:
            >>> # Upload meeting notes
            >>> response = client.documents.upload(
            ...     text_content='''
            ...     Meeting Notes - Product Planning Session
            ...     Date: January 15, 2024
            ...
            ...     Key Decisions:
            ...     - Launch new feature Q2 2024
            ...     - Increase development team by 2 engineers
            ...     - Beta testing starts March 1st
            ...     ''',
            ...     name="meeting-notes-2024-01-15",
            ...     organization="acme-corp",
            ...     project="product-planning"
            ... )

            >>> # Upload API documentation
            >>> api_docs = get_api_documentation_from_system()  # Your function
            >>> response = client.documents.upload(
            ...     text_content=api_docs,
            ...     name="api-documentation-v2",
            ...     organization="acme-corp",
            ...     project="technical-docs",
            ...     filename="api-docs-v2.md",  # Markdown format
            ...     metadata={
            ...         "version": "2.0",
            ...         "auto_generated": True,
            ...         "last_updated": "2024-01-15"
            ...     }
            ... )
        """

        # Set default filename if not provided
        # Use .txt extension to indicate plain text content
        if not filename:
            filename = f"{name.strip()}.txt"

        # Prepare form data for the API request
        form_data = {
            'name': name.strip(),
            'organization': organization.strip(),
            'project': project.strip(),
            'force_overwrite': str(force_overwrite).lower(),  # Convert boolean to string
            'metadata': json.dumps(metadata) if metadata else "{}"
        }

        # Convert text to a file-like object for upload
        # This allows us to upload text content using the same multipart mechanism as files
        text_bytes = text_content.encode('utf-8')  # Convert string to bytes
        text_file = BytesIO(text_bytes)            # Create file-like object

        # Prepare file data for multipart upload
        files = {
            'document': (filename, text_file, 'text/plain')  # Use plain text MIME type
        }

        # Make the API request (same endpoint as file uploads)
        response = self._client.post(
            endpoint='/documents/file/',  # Same endpoint handles both files and text
            data=form_data,              # Form fields
            files=files                  # Text content as virtual file
        )

        return response
