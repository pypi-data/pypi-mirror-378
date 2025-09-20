from typing import Dict
from typing import Any
from ragger_sdk.exceptions import RaggerAPIError
from ragger_sdk.constants import ErrorCodes


class DocumentsBaseAPI:

    def __init__(self, client):
        """
        Initialize the DocumentsFromXAPI with a reference to the main client.

        This constructor is typically called by the RaggerClient during
        initialization. The client reference is used to make authenticated
        HTTP requests to the Ragger API.

        Args:
            client (RaggerClient): The main RaggerClient instance that provides
                                 HTTP request capabilities and authentication.
                                 This client must be properly initialized with
                                 a valid base URL and authentication token.

        Example:
            >>> # Typically done automatically by RaggerClient
            >>> client = RaggerClient(base_url="...", token="...")
            >>> # client.documents is now a DocumentsFromTextAPI instance
            >>>
            >>> # Manual instantiation (advanced usage)
            >>> from ragger_sdk.endpoints import DocumentsFromXAPI
            >>> docs_api = DocumentsFromXAPI(client)
        """
        # Store the client reference for making API requests
        # This client handles authentication, URL building, and HTTP communication
        self._client = client

    def get_status(
            self,
            task_id: str,
            organization: str
            ) -> Dict[str, Any]:
        """
        Get the processing status of an uploaded text document.

        This method retrieves the current status of a document upload
        task using its task ID. It allows you to monitor the progress
        of text extraction, chunking, and indexing for documents
        uploaded via the upload() method.

        Args:
            task_id (str): The unique identifier for the document upload task.
                           This ID is returned in the response from the upload() method.

        Returns:
            dict: API response containing the current status of the document processing,
                 including fields like 'status', 'progress', and any error messages.

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_not_found() if the task_id does not exist
                            - .is_server_error() for network errors, server issues, or API problems

        Examples:
            >>> # After uploading a document, check its status
            >>> response = client.documents_from_file.upload(
            ...     text_content="Some important text content...",
            ...     name="important-doc",
            ...     organization="my-org",
            ...     project="my-project"
            ... )
            >>> task_id = response.get('task_id')
            >>>
            >>> # Periodically check the status
            >>> import time
            >>> while True:
            ...     status_response = client.documents_from_file.get_status(task_id)
            ...     print(f"Status: {status_response.get('status')}, Progress: {status_response.get('progress')}%")
            ...     if status_response.get('status') in ['completed', 'failed']:
            ...         break
            ...     time.sleep(10)  # Wait before checking again
        """
        if not task_id or not task_id.strip():
            raise RaggerAPIError(
                "task_id cannot be empty",
                ErrorCodes.MISSING_REQUIRED_PARAMETERS
            )

        response = self._client.get(
            # re_path(r'^task-status/?$', TaskStatusView.as_view(), name='task_status'),
            endpoint='/task-status/',
            params={
                'task_id': task_id.strip(),
                'organization': organization.strip()
                }
        )

        return response
