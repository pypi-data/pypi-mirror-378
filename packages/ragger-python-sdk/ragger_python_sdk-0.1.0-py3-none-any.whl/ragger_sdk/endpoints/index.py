import logging

from typing import Dict
from typing import Any

from ragger_sdk.exceptions import RaggerAPIError
from ragger_sdk.constants import ErrorCodes

logger = logging.getLogger(__name__)


class IndexAPI:
    """
    Interface for vector index creation and management in the Ragger API.

    This class provides methods for creating searchable vector indices from
    your processed documents. Vector indices are what enable semantic search
    and AI-powered question answering in the RAG system.

    Think of vector indexing as creating a "smart search engine" for your documents.
    Unlike traditional keyword search, vector search understands the meaning and
    context of your content, allowing for more intelligent information retrieval.

    Key Responsibilities:
    ====================

    **Index Creation:**
    - Convert processed documents into searchable vector representations
    - Support multiple embedding models with different quality/cost tradeoffs
    - Handle large document collections through asynchronous processing

    **Status Monitoring:**
    - Track index creation progress and completion
    - Provide detailed metadata about created indices
    - Report document counts and processing statistics

    **Index Management:**
    - Support index recreation with force_overwrite option
    - Maintain multi-tenant isolation by organization/project
    - Validate embedding model compatibility

    Workflow Integration:
    ====================

    This class fits into the broader RAG workflow:
    1. Documents uploaded → processed (documents.py)
    2. **Vector indices created** (this class)
    3. Natural language queries answered (query.py)
    4. Conversation history tracked (chat_history.py)

    Example Usage:
        >>> # Basic index creation
        >>> client = RaggerClient(base_url="...", token="...")
        >>>
        >>> # Create index with default settings
        >>> result = client.index.create_index(
        ...     organization="my-company",
        ...     project="documentation"
        ... )
        >>>
        >>> # Monitor creation progress
        >>> status = client.index.get_status(
        ...     organization="my-company",
        ...     project="documentation"
        ... )
        >>> print(f"Status: {status['status']}")
        >>> print(f"Documents: {status.get('document_count', 0)}")
    """

    def __init__(self, client):
        """
        Initialize IndexAPI with reference to the main RaggerClient.

        This constructor is typically called by the RaggerClient during
        initialization. The client reference is used to make authenticated
        HTTP requests to the Ragger API endpoints.

        Args:
            client (RaggerClient): The main RaggerClient instance that provides
                                 HTTP request capabilities and authentication.
                                 Must be properly initialized with valid credentials.

        Example:
            >>> # Typically done automatically by RaggerClient
            >>> client = RaggerClient(base_url="...", token="...")
            >>> # client.index is now an IndexAPI instance
            >>>
            >>> # Manual instantiation (advanced usage)
            >>> from ragger_sdk.endpoints import IndexAPI
            >>> index_api = IndexAPI(client)
        """
        # Store the client reference for making authenticated API requests
        self.client = client
        # Define the base endpoint for all index operations
        self.endpoint = "/index/"

    def create_index(
        self,
        organization: str,
        project: str,
        force_overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Create a vector index from processed documents in the specified project.

        This method initiates the creation of a searchable vector index using all
        processed documents in the given organization/project. The process involves:

        1. **Document Retrieval**: Collect all processed documents from the project
        2. **Text Chunking**: Split documents into searchable chunks (if not already done)
        3. **Vector Generation**: Convert text chunks to vectors using the embedding model
        4. **Index Storage**: Store vectors in the database for fast retrieval
        5. **Metadata Indexing**: Create additional indices for filtering and organization

        The entire process is asynchronous and runs in the background. Use get_status()
        to monitor progress and determine when the index is ready for querying.

        Embedding Model Selection:
        =========================

        **text-embedding-3-small (default):**
        - 1536 dimensions
        - Fast and cost-effective
        - Good for most use cases
        - Recommended for getting started

        **text-embedding-3-large:**
        - 3072 dimensions
        - Higher quality semantic understanding
        - More expensive and slower
        - Best for critical applications requiring maximum accuracy

        **text-embedding-ada-002:**
        - 1536 dimensions
        - Legacy model but still reliable
        - Good compatibility and proven performance

        Args:
            organization (str): Organization identifier for multi-tenant isolation.
                              Must match an organization you have access to.

            project (str): Project name within the organization. The index will
                         include all processed documents from this project.

            embedding_model (str, optional): Embedding model to use for vectorization.
                                           If not provided, the server uses its configured
                                           default (typically text-embedding-3-small).
                                           See method docstring for model comparison.

            force_overwrite (bool, optional): Whether to overwrite an existing index.
                                             Default is False to prevent accidental
                                             index recreation. Set to True to:
                                             - Update index with new documents
                                             - Change embedding model
                                             - Fix corrupted indices

        Returns:
            dict: API response containing index creation details:
                - 'task_id' (str): Celery task ID for tracking progress
                - 'status' (str): Initial status (typically "initiated" or "creating")
                - 'message' (str): Human-readable status description
                - 'organization' (str): Confirmed organization identifier
                - 'project' (str): Confirmed project identifier
                - 'embedding_model' (str): Embedding model being used
                - Additional metadata about the indexing process

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty organization/project or invalid settings
                           - .is_auth_error() for invalid or expired authentication tokens
                           - .is_not_found() for missing organization or project
                           - .is_server_error() for network errors, server issues, or API problems

        Examples:
            >>> # Basic index creation with default embedding model
            >>> result = client.index.create_index(
            ...     organization="acme-corp",
            ...     project="product-documentation"
            ... )
            >>> print(f"Index creation started, task ID: {result['task_id']}")
            >>>
            >>> # Create high-quality index with specific model
            >>> result = client.index.create_index(
            ...     organization="acme-corp",
            ...     project="legal-documents",
            ...     embedding_model="text-embedding-3-large",  # Higher quality
            ...     force_overwrite=True  # Replace existing index
            ... )
            >>>
            >>> # Monitor creation progress
            >>> task_id = result['task_id']
            >>> while True:
            ...     status = client.index.get_status(
            ...         organization="acme-corp",
            ...         project="product-documentation"
            ...     )
            ...     if status['status'] == 'created':
            ...         print("✅ Index ready for querying!")
            ...         break
            ...     elif status['status'] == 'failed':
            ...         print("❌ Index creation failed")
            ...         break
            ...     print(f"⏳ Status: {status['status']}")
            ...     time.sleep(10)

        Important Notes:
            - Only documents with is_processed=True are included in the index
            - Index creation time scales with document count and size
            - Large indices (1000+ documents) may take several minutes to create
            - The index must be created before any querying can be performed
            - Each organization/project combination has at most one index
            - Changing embedding models requires force_overwrite=True
        """

        # Prepare the API request payload
        # Clean whitespace from string parameters to avoid issues
        data = {
            "organization": organization.strip(),
            "project": project.strip(),
            "force_overwrite": force_overwrite
        }

        # Make the API request to initiate index creation
        response = self.client.request(
            method="POST",           # POST to create new resources
            endpoint=self.endpoint,  # /index/ endpoint
            data=data               # Request payload
        )

        # Step 6: Log successful initiation and return response
        logger.debug(f"Index creation initiated successfully for {organization}/{project}")
        return response

    def get_status(
        self,
        organization: str,
        project: str
    ) -> Dict[str, Any]:
        """
        Get the current status and metadata of a vector index.

        This method retrieves comprehensive information about the vector index for
        the specified organization and project. Use this to monitor index creation
        progress, check when an index is ready for querying, and get metadata
        about your indexed document collection.

        Index Status Values:
        ===================

        **"not_found"**: No index exists for this organization/project
        - Indicates you need to call create_index() first
        - Or the index creation failed and needs to be retried

        **"creating"**: Index creation is currently in progress
        - Background processing is converting documents to vectors
        - Check again periodically until status changes
        - Creation time depends on document count and complexity

        **"created"**: Index is ready for querying
        - All documents have been processed and vectorized
        - You can now use query.ask() to search the index
        - This is the target state for a successful index

        **"failed"**: Index creation encountered an error
        - Check the response message for error details
        - May need to retry with create_index(force_overwrite=True)
        - Common causes: no processed documents, server issues

        Args:
            organization (str): Organization identifier for multi-tenant isolation.
                              Must match an organization you have access to.

            project (str): Project name within the organization.
                         Must match a project that exists in your organization.

        Returns:
            dict: Comprehensive index information containing:
                - 'status' (str): Current index status (see status values above)
                - 'document_count' (int): Number of documents included in the index
                - 'embedding_model' (str): Embedding model used for vectorization
                - 'created_at' (str): ISO timestamp when index was created
                - 'updated_at' (str): ISO timestamp when index was last modified
                - 'organization' (str): Confirmed organization identifier
                - 'project' (str): Confirmed project identifier
                - 'index_size' (int): Approximate index size metrics
                - 'vector_dimensions' (int): Number of dimensions in each vector
                - Additional metadata and statistics about the index

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty organization or project parameters
                           - .is_auth_error() for invalid or expired authentication tokens
                           - .is_not_found() for missing organization or project
                           - .is_server_error() for network errors, server issues, or API problems

        Examples:
            >>> # Basic status check
            >>> status = client.index.get_status(
            ...     organization="acme-corp",
            ...     project="documentation"
            ... )
            >>> print(f"Index status: {status['status']}")
            >>> print(f"Documents indexed: {status.get('document_count', 0)}")
            >>>
            >>> # Wait for index creation to complete
            >>> import time
            >>> print("Waiting for index creation...")
            >>> while True:
            ...     status = client.index.get_status(
            ...         organization="acme-corp",
            ...         project="documentation"
            ...     )
            ...
            ...     if status['status'] == 'created':
            ...         print("✅ Index ready for querying!")
            ...         print(f"📊 {status['document_count']} documents indexed")
            ...         print(f"🤖 Using model: {status.get('embedding_model', 'unknown')}")
            ...         break
            ...     elif status['status'] == 'failed':
            ...         print("❌ Index creation failed")
            ...         print(f"Error details: {status.get('message', 'No details available')}")
            ...         break
            ...     else:
            ...         print(f"⏳ Status: {status['status']}")
            ...         time.sleep(10)  # Wait 10 seconds before checking again
            >>>
            >>> # Check index metadata
            >>> status = client.index.get_status(organization="acme-corp", project="docs")
            >>> if status['status'] == 'created':
            ...     print(f"Created: {status.get('created_at')}")
            ...     print(f"Model: {status.get('embedding_model')}")
            ...     print(f"Dimensions: {status.get('vector_dimensions')}")

        Monitoring Best Practices:
            - Check status before attempting to query an index
            - Use exponential backoff when polling during creation
            - Log status changes for debugging and monitoring
            - Handle both successful creation and failure cases
            - Consider the document_count to verify all expected documents were indexed
        """
        # Prepare query parameters for the GET request
        # Clean whitespace to avoid parameter parsing issues
        params = {
            "organization": organization.strip(),
            "project": project.strip()
        }

        # Step 3: Log the status check for debugging and monitoring
        logger.debug(f"Getting index status for {organization}/{project}")

        # Step 4: Make the API request to retrieve index status
        response = self.client.request(
            method="GET",           # GET request to retrieve information
            endpoint=self.endpoint, # /index/ endpoint
            params=params          # Query parameters for organization and project
        )

        # Step 5: Log successful retrieval and return the status information
        logger.debug(f"Index status retrieved successfully for {organization}/{project}")
        return response
