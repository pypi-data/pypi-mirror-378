"""
Core RaggerClient implementation.

This module provides the main client class for interacting with the Ragger API.
It serves as the primary entry point for all SDK operations and handles the
foundational concerns that every API interaction needs:

1. **Authentication**: Manages API tokens and session security
2. **Request/Response Processing**: Converts Python data to HTTP requests and back
3. **Error Handling**: Translates API errors into meaningful Python exceptions
4. **Connection Management**: Handles HTTP sessions, timeouts, and cleanup
5. **URL Building**: Constructs proper API endpoints from base URL + paths

Key Design Principles:
- **Simple and Explicit**: Clear method names and parameter requirements
- **Consistent Error Handling**: All errors become informative exceptions
- **Resource Management**: Proper cleanup with context manager support
- **Debugging Friendly**: Extensive logging for troubleshooting

This follows the Zen of Python principles:
- "Simple is better than complex" - Clean, obvious API design
- "Explicit is better than implicit" - Clear parameter requirements
- "Readability counts" - Self-documenting method and variable names
"""

import json
import logging
import requests

from typing import Optional
from typing import Dict
from typing import Any
from urllib.parse import urljoin
from urllib.parse import urlparse
from importlib.metadata import version

# Local imports from our SDK modules
from ragger_sdk.exceptions import RaggerAPIError
from ragger_sdk.exceptions import create_exception_from_response

from ragger_sdk.constants import ErrorCodes

# Import all the endpoint-specific API classes
# # These handle the actual API operations for different features
from ragger_sdk.endpoints.documents_from_file import DocumentsFromFileAPI      # Document upload and management
from ragger_sdk.endpoints.documents_from_text import DocumentsFromTextAPI          # Document upload and management from text
from ragger_sdk.endpoints.index import IndexAPI             # Vector index creation and management
from ragger_sdk.endpoints.query import QueryAPI             # Natural language querying and RAG
from ragger_sdk.endpoints.chat_history import ChatHistoryAPI # Chat session history retrieval

logger = logging.getLogger(__name__)

class RaggerClient:
    """
    Main client for interacting with the Ragger RAG API.

    This is the primary class you'll use to interact with Ragger. Think of it as
    your "connection" to the Ragger server that handles all the technical details
    of making API calls, managing authentication, and organizing different types
    of operations.

    The client is organized around the main RAG workflow:
    1. **Documents** (client.documents) - Upload and manage your source documents
    2. **Index** (client.index) - Create searchable vector representations
    3. **Query** (client.query) - Ask questions and get AI-powered answers
    4. **Chat History** (client.chat_history) - Access conversation history

    Key Features:
    - **Automatic Authentication**: Set your token once, used for all requests
    - **Smart Error Handling**: Clear exceptions for different error types
    - **Session Management**: Efficient connection pooling and reuse
    - **Context Manager Support**: Automatic cleanup with 'with' statements
    - **Comprehensive Logging**: Debug information for troubleshooting

    Attributes:
        base_url (str): The base URL for your Ragger API server
        token (str): Your authentication token for API requests
        timeout (int): Request timeout in seconds (default: 30)
        session (requests.Session): HTTP session for connection pooling

        # API endpoint interfaces - these are where the actual work happens:
        documents (DocumentsFromFileAPI): Upload files, add text, manage documents
        index (IndexAPI): Create and manage vector indices for search
        query (QueryAPI): Ask questions and get AI-generated answers
        chat_history (ChatHistoryAPI): Retrieve conversation history

    Example - Basic Usage:
        >>> # Initialize the client
        >>> client = RaggerClient(
        ...     base_url="http://ragger.local:8025/rag/api/v1",
        ...     token="your-api-token"
        ... )
        >>>
        >>> # Test that everything works
        >>> result = client.test_connection()
        >>> print(result['status'])  # Should print 'success'

    Example - Context Manager (Recommended):
        >>> # Automatically handles cleanup when done
        >>> with RaggerClient(base_url="...", token="...") as client:
        ...     # Your API operations here
        ...     client.documents.upload(...)
        ...     client.index.create_index(...)
        ...     response = client.query.ask(...)
        ... # Client automatically cleaned up here

    Example - Manual Cleanup:
        >>> client = RaggerClient(base_url="...", token="...")
        >>> try:
        ...     # Your API operations
        ...     pass
        ... finally:
        ...     client.close()  # Always clean up resources
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize the RaggerClient with connection details.

        This sets up everything needed to communicate with your Ragger API server.
        The client will validate your inputs and set up an efficient HTTP session
        for making multiple API calls.

        Args:
            base_url (str): The complete base URL for your Ragger API server.
                          For example: "http://ragger.local:8025/rag/api/v1"
                          or "https://your-ragger-server.com/api/v1"

            token (str): Your authentication token from the Ragger server.
                        This is typically generated in the Ragger web interface
                        under API settings or user profile.

            timeout (int, optional): How long to wait for API requests to complete,
                                   in seconds. Default is 30 seconds. Increase this
                                   if you're working with large documents or slow
                                   network connections.

            verify_ssl (bool, optional): Whether to verify SSL certificates.
                                       Default is True (recommended for security).
                                       Set to False only for development/testing
                                       with self-signed certificates.

        Raises:
            RaggerAPIError: If the base_url is not a valid URL format,
                           or if token is empty/invalid format.
                           Use .is_validation_error() to check for validation issues.

        Example:
            >>> # Production setup with SSL verification
            >>> client = RaggerClient(
            ...     base_url="https://api.ragger.ai/v1",
            ...     token="your-production-token-here"
            ... )

            >>> # Development setup with longer timeout
            >>> client = RaggerClient(
            ...     base_url="http://localhost:8025/rag/api/v1",
            ...     token="dev-token-123",
            ...     timeout=60,  # 60 seconds for slow development server
            ...     verify_ssl=False  # OK for local development only
            ... )
        """
        # Step 1: Validate that we have valid inputs before proceeding
        # This prevents confusing errors later when making API calls
        if not base_url or not isinstance(base_url, str):
            raise RaggerAPIError(
                detail="base_url must be a non-empty string",
                code=ErrorCodes.MISSING_REQUIRED_PARAMETERS,
                status_code=400
            )

        if not token or not isinstance(token, str):
            raise RaggerAPIError(
                detail="token must be a non-empty string",
                code=ErrorCodes.MISSING_REQUIRED_PARAMETERS,
                status_code=400
            )

        # Normalize base URL (remove trailing slash)
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout

        # Step 3: Validate that the base URL is actually a valid URL format
        # This catches common mistakes like missing http:// or malformed URLs
        try:
            parsed = urlparse(self.base_url)
            if not parsed.scheme or not parsed.netloc:
                raise RaggerAPIError(
                    detail=f"Invalid base_url format: {base_url}",
                    code=ErrorCodes.INVALID_SETTINGS,
                    status_code=400
                )
        except Exception as e:
            raise RaggerAPIError(
                detail=f"Invalid base_url: {e}",
                code=ErrorCodes.INVALID_SETTINGS,
                status_code=400
            )

        # Step 4: Set up HTTP session with authentication and sensible defaults
        # Using a session allows connection pooling and reuse for better performance
        self.session = requests.Session()

        # Configure authentication header that will be sent with every request
        # The Ragger API uses Token-based authentication
        try:
            ragger_sdk_version = version("ragger_sdk")
        except Exception:
            ragger_sdk_version = "unknown"

        self.session.headers.update({
            'Authorization': f'Token {self.token}',  # Format required by Ragger API
            'User-Agent': f'RaggerSDK/{ragger_sdk_version}' # Identify our SDK to the server
        })

        # Configure SSL verification setting
        self.session.verify = verify_ssl

        # Step 5: Initialize all the endpoint-specific API interfaces
        # These objects handle the actual API operations for different features
        # Each one gets a reference to this client so they can make HTTP requests
        self.documents_from_file = DocumentsFromFileAPI(self)      # Document upload and management
        self.documents_from_text = DocumentsFromTextAPI(self)          # Document upload and management from text
        self.index = IndexAPI(self)             # Vector index creation and management
        self.query = QueryAPI(self)             # Natural language querying and RAG
        self.chat_history = ChatHistoryAPI(self) # Chat session history retrieval

        # Log successful initialization for debugging
        logger.debug(
            f"Initialized RaggerClient. "
            f"I will connect to '{self.base_url}'"
        )

    def _build_url(self, endpoint: str) -> str:
        """
        Build a complete URL for an API endpoint.

        This helper method takes an endpoint path (like "/documents/file/") and
        combines it with the base URL to create a complete URL for making requests.
        It handles edge cases like missing slashes and ensures consistent URL format.

        Args:
            endpoint (str): API endpoint path (e.g., "/documents/file/" or "documents/file/")
                          Can start with or without a leading slash

        Returns:
            str: Complete URL ready for HTTP requests

        Example:
            >>> client = RaggerClient(base_url="http://api.example.com/v1", token="...")
            >>> url = client._build_url("/documents/file/")
            >>> print(url)  # "http://api.example.com/v1/documents/file/"
            >>>
            >>> # Also works without leading slash
            >>> url = client._build_url("documents/file/")
            >>> print(url)  # "http://api.example.com/v1/documents/file/"
        """
        # Ensure endpoint starts with / for consistent URL building
        # This prevents issues like "base.com/v1documents" instead of "base.com/v1/documents"
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        # Use urljoin for proper URL combination that handles edge cases
        # The '+ /' ensures there's always a slash before the endpoint path
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))

    def _prepare_request_data(self, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Prepare request data for logging and debugging.

        This method creates a sanitized copy of request data that's safe to log.
        It removes sensitive information like passwords and tokens so they don't
        appear in log files, which could be a security risk.

        Args:
            data (dict, optional): Request data dictionary that might contain
                                 sensitive information

        Returns:
            dict or None: Sanitized copy of the data with sensitive fields masked,
                         or None if no data was provided

        Example:
            >>> original_data = {"username": "john", "password": "example123", "email": "john@example.com"}  # pragma: allowlist secret
            >>> sanitized = client._prepare_request_data(original_data)
            >>> print(sanitized)
            >>> # {"username": "john", "password": "***REDACTED***", "email": "john@example.com"}
        """
        if not data:
            return None

        # Create a copy so we don't modify the original data
        # This is important because the original data is still needed for the actual API call
        sanitized = data.copy()

        # List of field names that might contain sensitive information
        # These will be replaced with a placeholder in the sanitized version
        sensitive_fields = [
            'token',
            'password',
            'secret',  # pragma: allowlist secret
            'api_key',
            'apikey',
            'access_token',
            'auth_token',
        ]

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'

        return sanitized

    def _handle_response(
        self,
        response: requests.Response,
        request_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle API response and convert errors to appropriate exceptions.

        This method is the central point for processing all responses from the
        Ragger API. It handles both successful responses and various error conditions,
        converting HTTP status codes into meaningful Python exceptions that
        developers can catch and handle appropriately.

        The method follows this logic:
        1. Check if the response indicates success (status 200-299)
        2. If successful, parse the JSON and return it
        3. If error, create an appropriate exception with context

        Args:
            response (requests.Response): The HTTP response object from the API call
            request_data (dict, optional): Original request data for error context.
                                         This helps with debugging by showing what
                                         data caused the error.

        Returns:
            dict: Parsed JSON response data for successful requests

        Raises:
            RaggerAPIError: For all API errors. Use boolean methods to check error types:
                           - .is_auth_error() for authentication/authorization errors (401, 403)
                           - .is_not_found() for resource not found errors (404)
                           - .is_validation_error() for request validation errors (400, 422)
                           - .is_server_error() for server-side errors (500+)

        Example:
            >>> # This method is used internally by the request() method
            >>> # You typically won't call it directly, but it's what handles
            >>> # converting this:
            >>> #   HTTP 404 Not Found
            >>> # Into this:
            >>> #   RaggerAPIError("Organization 'missing-org' not found")
            >>> #   where error.is_not_found() returns True
        """
        # Prepare sanitized request data for error context (removes sensitive info)
        sanitized_request = self._prepare_request_data(request_data)

        # Log the response status for debugging
        # This helps developers understand what's happening with their API calls
        logger.debug(f"API Response: {response.status_code} {response.reason}")

        # Handle successful responses (HTTP status 200-299)
        if 200 <= response.status_code < 300:
            try:
                # Most API responses are JSON, so try to parse them
                return response.json()
            except (json.JSONDecodeError, ValueError) as e:
                # Some endpoints might return non-JSON responses (rare)
                # In this case, return the raw response text for the caller to handle
                logger.warning(f"Non-JSON response: {response.text[:200]}")
                return {'raw_response': response.text, 'status_code': response.status_code}

        # Handle error responses (HTTP status 400+)
        # Log the error for debugging - developers often need this information
        logger.error(f"API Error: {response.status_code} {response.reason}")

        # Create and raise an appropriate exception based on the status code
        # The create_exception_from_response function determines the right exception type
        raise create_exception_from_response(response, sanitized_request)

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to the Ragger API.

        This is the core method that all other API calls use. It handles the low-level
        details of HTTP communication, including authentication, data encoding,
        error handling, and response parsing.

        The method supports two main types of requests:
        1. **JSON Requests**: Regular API calls with JSON data (most common)
        2. **File Uploads**: Multipart form uploads for document uploads

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE). Case-insensitive.

            endpoint (str): API endpoint path (e.g., "/documents/file/").
                          Can start with or without leading slash.

            data (dict, optional): Request body data. For file uploads, this becomes
                                 form data. For regular requests, this becomes JSON.

            files (dict, optional): Files for multipart uploads. Format:
                                   {"file": open("document.pdf", "rb")}
                                   When provided, 'data' becomes form data instead of JSON.

            params (dict, optional): URL query parameters. These get appended to
                                   the URL as ?key=value&key2=value2

            headers (dict, optional): Additional HTTP headers. These are merged
                                    with the default authentication headers.

            **kwargs: Additional arguments passed directly to requests.request().
                     Use this for advanced options like custom timeout values.

        Returns:
            dict: Parsed JSON response data from the API

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_server_error() for connection, timeout, or request failures
                           - .is_auth_error() for authentication/authorization errors (401, 403)
                           - .is_not_found() for resource not found errors (404)
                           - .is_validation_error() for request validation errors (400, 422)
                           - .is_server_error() for server-side errors (500+)

        Example - JSON Request:
            >>> response = client.request(
            ...     method='POST',
            ...     endpoint='/index/',
            ...     data={'organization': 'my-org', 'project': 'my-project'}
            ... )

        Example - File Upload:
            >>> with open('document.pdf', 'rb') as f:
            ...     response = client.request(
            ...         method='POST',
            ...         endpoint='/documents/file/',
            ...         data={'organization': 'my-org', 'project': 'my-project'},
            ...         files={'file': f}
            ...     )

        Example - Query Parameters:
            >>> response = client.request(
            ...     method='GET',
            ...     endpoint='/history/',
            ...     params={'organization': 'my-org', 'user': 'john@example.com'}
            ... )
        """
        # Step 1: Build the complete URL from base URL + endpoint
        url = self._build_url(endpoint)

        # Step 2: Prepare headers by merging defaults with any custom headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        # Step 3: Set content type for JSON requests (but not for file uploads)
        # File uploads need multipart/form-data which requests sets automatically
        if data and not files:  # If we have data but no files, it's a JSON request
            request_headers['Content-Type'] = 'application/json'

        # Step 4: Log the request for debugging purposes
        # Could be helpful to see what requests are being made
        logger.debug(f"API Request: {method.upper()} {url}")
        if params:
            logger.debug(f"Query params: {params}")
        if data:
            # Log the keys of the data (not the values, for security)
            logger.debug(f"Request data keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")

        try:
            # Step 5: Determine request type and prepare data accordingly
            # The requests library handles JSON and multipart uploads differently
            if files:
                # File upload mode: use 'data' parameter for form data + 'files' for files
                # Don't use 'json' parameter as it conflicts with multipart uploads
                request_kwargs = {
                    'data': data,  # Form data (will be form-encoded)
                    'files': files,  # Files (creates multipart/form-data request)
                    'json': None   # Explicitly None to avoid conflicts
                }
            else:
                # Regular API call mode: use 'json' parameter for JSON data
                # This automatically sets Content-Type and encodes data as JSON
                request_kwargs = {
                    'json': data,  # JSON payload (automatically encoded)
                    'data': None,  # Explicitly None for clarity
                    'files': None  # Explicitly None for non-upload requests
                }

            # Step 6: Make the actual HTTP request
            response = self.session.request(
                method=method.upper(),     # Normalize HTTP method to uppercase
                url=url,                   # Complete URL we built earlier
                params=params,             # Query parameters
                headers=request_headers,   # Headers (including authentication)
                timeout=self.timeout,      # Request timeout from client configuration
                **request_kwargs,          # Data/files configuration from above
                **kwargs                   # Any additional arguments from caller
            )

            # Step 7: Process the response and return parsed data
            return self._handle_response(response, data)

        # Step 8: Handle various types of request failures
        # Convert low-level network errors into meaningful SDK exceptions
        except requests.exceptions.Timeout:
            raise RaggerAPIError(
                f"Request timed out after {self.timeout} seconds",
                request_data=self._prepare_request_data(data)
            )
        except requests.exceptions.ConnectionError as e:
            raise RaggerAPIError(
                f"Connection error: {str(e)}",
                request_data=self._prepare_request_data(data)
            )
        except requests.exceptions.RequestException as e:
            raise RaggerAPIError(
                f"Request failed: {str(e)}",
                request_data=self._prepare_request_data(data)
            )

    def get(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            **kwargs
        ) -> Dict[str, Any]:
        """
        Make a GET request to the API.

        GET requests are used to retrieve information from the API without making
        any changes. They're safe to repeat and don't modify any data on the server.

        Args:
            endpoint (str): API endpoint path (e.g., "/history/" or "/index/")
            params (dict, optional): URL query parameters to filter or specify the request
            **kwargs: Additional arguments passed to the underlying request() method

        Returns:
            dict: Parsed JSON response data

        Example:
            >>> # Get chat history for a specific user
            >>> history = client.get('/history/', params={
            ...     'organization': 'my-org',
            ...     'project': 'my-project',
            ...     'user': 'john@example.com'
            ... })
            >>>
            >>> # Check index status
            >>> status = client.get('/index/', params={
            ...     'organization': 'my-org',
            ...     'project': 'my-project'
            ... })
        """
        return self.request('GET', endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API.

        POST requests are used to create new resources or trigger actions.
        They can modify data on the server and are not safe to repeat
        (repeating might create duplicate resources).

        Args:
            endpoint (str): API endpoint path (e.g., "/documents/file/" or "/query/")
            data (dict, optional): Request body data - either JSON data or form data
            files (dict, optional): Files for multipart uploads (e.g., document uploads)
            **kwargs: Additional arguments passed to the underlying request() method

        Returns:
            dict: Parsed JSON response data

        Example:
            >>> # Create a new vector index
            >>> result = client.post('/index/', data={
            ...     'organization': 'my-org',
            ...     'project': 'my-project'
            ... })
            >>>
            >>> # Upload a document file
            >>> with open('document.pdf', 'rb') as f:
            ...     result = client.post('/documents/file/',
            ...         data={'organization': 'my-org', 'project': 'my-project'},
            ...         files={'file': f}
            ...     )
            >>>
            >>> # Ask a question
            >>> answer = client.post('/query/', data={
            ...     'query': 'What is the main topic?',
            ...     'organization': 'my-org',
            ...     'project': 'my-project',
            ...     'user': 'john@example.com'
            ... })
        """
        return self.request('POST', endpoint, data=data, files=files, **kwargs)

    def put(
            self,
            endpoint: str,
            data: Optional[Dict[str, Any]] = None,
            **kwargs
        ) -> Dict[str, Any]:
        """
        Make a PUT request to the API.

        PUT requests are used to update existing resources or create resources
        with a specific identifier. They are idempotent, meaning you can repeat
        them safely - the result should be the same.

        Args:
            endpoint (str): API endpoint path
            data (dict, optional): Request body data (sent as JSON)
            **kwargs: Additional arguments passed to the underlying request() method

        Returns:
            dict: Parsed JSON response data

        Note:
            PUT is not used in the current Ragger API.
        """
        return self.request('PUT', endpoint, data=data, **kwargs)

    def delete(
            self,
            endpoint: str,
            **kwargs
        ) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.

        DELETE requests are used to remove resources from the server.
        They are idempotent - deleting something that's already deleted
        typically returns the same result.

        Args:
            endpoint (str): API endpoint path
            **kwargs: Additional arguments passed to the underlying request() method

        Returns:
            dict: Parsed JSON response data

        Note:
            DELETE is less commonly used in the current Ragger API compared to
            GET and POST.
        """
        return self.request('DELETE', endpoint, **kwargs)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the Ragger API.

        This method verifies that everything is set up correctly for making API calls.
        It checks three important things:
        1. **Network Connectivity**: Can we reach the Ragger server?
        2. **Authentication**: Is our API token valid?
        3. **API Compatibility**: Is the server responding as expected?

        How it works:
        We make a minimal request to the /task-status/ endpoint without required
        parameters. A 400 error with "organization parameter is required" means
        we're successfully connected and authenticated - the API understood our
        request and is just telling us we need more parameters.

        Returns:
            dict: Connection test results with these fields:
                - status (str): 'success', 'auth_error', 'validation_error', or 'error'
                - message (str): Human-readable description of the result
                - base_url (str): The base URL that was tested

        Raises:
            This method catches exceptions and returns them in the result dict
            instead of raising them. This makes it easier to handle connection
            testing in user interfaces or setup scripts.

        Example:
            >>> result = client.test_connection()
            >>> if result['status'] == 'success':
            ...     print("✅ Ready to make API calls!")
            ... elif result['status'] == 'auth_error':
            ...     print("❌ Invalid API token")
            ... else:
            ...     print(f"❌ Connection problem: {result['message']}")

        Example - Using with exception handling:
            >>> try:
            ...     result = client.test_connection()
            ...     if result['status'] == 'success':
            ...         print("Connection successful!")
            ... except RaggerAPIError as e:
            ...     if e.is_server_error():
            ...         print("Server error")
            ...     else:
            ...         print(f"Connection failed: {e}")
        """
        try:
            # Strategy: Make a minimal request that we expect to fail gracefully
            # /task-status/ will return 400 "organization parameter is required"
            # but this confirms: 1) API is reachable, 2) Auth token is valid, 3) API is responding
            response = self.get('/task-status/')

            # If we somehow get a success response, that's also good
            # (This could happen if the API changes in the future)
            return {
                'status': 'success',
                'message': 'Connection to Ragger API successful',
                'base_url': self.base_url
            }

        except RaggerAPIError as e:
            # Check error types using simple boolean methods
            if e.is_validation_error():
                # Expected: "organization parameter is required" or similar
                # This actually means we're successfully connected and authenticated
                if 'organization' in e.detail.lower() or 'parameter' in e.detail.lower():
                    return {
                        'status': 'success',
                        'message': 'Connection to Ragger API successful (validated via parameter check)',
                        'base_url': self.base_url
                    }
                else:
                    # Different validation error - report it
                    return {
                        'status': 'validation_error',
                        'message': f'API validation error: {e.detail}',
                        'base_url': self.base_url
                    }
            elif e.is_server_error():
                # Server errors
                return {
                    'status': 'server_error',
                    'message': f'Server error: {e.detail}',
                    'base_url': self.base_url
                }
            else:
                # Other API errors
                return {
                    'status': 'api_error',
                    'message': f'API error: {e.detail} (code: {e.code})',
                    'base_url': self.base_url
                }

        except Exception as e:
            # Network, connection, or other errors
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'base_url': self.base_url
            }

    def close(self):
        """
        Close the HTTP session and clean up resources.

        This method properly closes the underlying HTTP session, which frees up
        network connections and other system resources. It's important to call this
        when you're done using the client, especially in long-running applications.

        The client automatically calls this method when used as a context manager
        (with the 'with' statement), but you should call it manually if you're
        not using context manager syntax.

        Example - Manual cleanup:
            >>> client = RaggerClient(base_url="...", token="...")
            >>> try:
            ...     # Your API operations here
            ...     client.documents.upload(...)
            ...     client.query.ask(...)
            ... finally:
            ...     client.close()  # Always clean up, even if an error occurred

        Example - Automatic cleanup (preferred):
            >>> with RaggerClient(base_url="...", token="...") as client:
            ...     # Your API operations here
            ...     client.documents.upload(...)
            ...     client.query.ask(...)
            ... # client.close() is called automatically here
        """
        if hasattr(self, 'session'):
            self.session.close()
            logger.debug("RaggerClient session closed")

    def __enter__(self):
        """
        Context manager entry.

        This allows the client to be used with the 'with' statement for automatic
        resource management. When you enter the 'with' block, this method is called
        and returns the client instance.

        Returns:
            RaggerClient: The client instance (self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.

        This is called when exiting a 'with' block, whether normally or due to
        an exception. It automatically calls close() to clean up resources.

        Args:
            exc_type: Exception type (if an exception occurred)
            exc_val: Exception value (if an exception occurred)
            exc_tb: Exception traceback (if an exception occurred)

        Note:
            This method doesn't suppress exceptions - if an exception occurred
            in the 'with' block, it will still be raised after cleanup.
        """
        self.close()

    def __repr__(self) -> str:
        """
        String representation of the client.

        This provides a useful string representation when the client is printed
        or displayed in debugging tools. It shows the key configuration without
        revealing sensitive information like the API token.

        Returns:
            str: String representation showing base URL and timeout

        Example:
            >>> client = RaggerClient(base_url="http://api.example.com", token="...")
            >>> print(client)
            >>> # RaggerClient(base_url='http://api.example.com', timeout=30)
        """
        return f"RaggerClient(base_url='{self.base_url}', timeout={self.timeout})"
