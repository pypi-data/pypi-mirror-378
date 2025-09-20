"""
Chat History API module for the Ragger SDK.

This module provides comprehensive access to conversation history and session
management in the Ragger RAG system. It's the final piece of the RAG workflow,
enabling users to review, analyze, and continue previous conversations with
the AI system.

What is Chat History?
====================

Chat history represents the complete record of conversations between users and
the AI system. Every query and response is stored in sessions, creating a
searchable record of interactions that can be:

- **Reviewed**: Look back at previous questions and answers
- **Continued**: Resume conversations where you left off
- **Analyzed**: Understand usage patterns and common questions
- **Shared**: Access conversations across team members (with permissions)

Key Concepts:
============

**Sessions:**
A session represents a single conversation thread between a user and the AI.
Sessions maintain context, allowing for natural follow-up questions and
maintaining conversation flow.

**Messages:**
Individual queries and responses within a session. Each message includes:
- Timestamp of when it was created
- User who asked the question
- AI-generated response
- Source documents that were referenced
- Token usage and processing metadata

**User Isolation:**
Chat history is isolated by user, ensuring privacy and personal conversation
tracking. Users can only access their own conversation history.

**Project Organization:**
Conversations are organized by project, allowing users to maintain separate
conversation threads for different document collections.

Common Use Cases:
================

**Conversation Review:**
- "What did I ask about the API documentation last week?"
- "Can I see all my conversations about pricing?"
- "What sources were cited in my previous research session?"

**Session Continuation:**
- Resume complex research sessions
- Pick up multi-part conversations
- Maintain context across work sessions

**Usage Analytics:**
- Track team question patterns
- Identify commonly requested information
- Monitor AI system usage and effectiveness

**Knowledge Management:**
- Save important Q&A sessions for team reference
- Build internal FAQ from actual user questions
- Document research processes and findings

API Structure:
=============

The chat history API provides three main access patterns:

1. **get_sessions()**: List all chat sessions for a user
2. **get_session()**: Get detailed conversation for a specific session
3. **get_user_sessions_summary()**: Get statistics and overview

Each method respects organization/project boundaries and user permissions.

Example Workflow:
================

    # Get overview of all conversations
    sessions = client.chat_history.get_sessions(
        organization="research-org",
        project="literature-review",
        user="researcher@university.edu"
    )

    # Find a specific conversation
    target_session = None
    for session in sessions:
        if "machine learning" in session['preview'].lower():
            target_session = session['session_id']
            break

    # Get full conversation details
    if target_session:
        conversation = client.chat_history.get_session(
            organization="research-org",
            project="literature-review",
            user="researcher@university.edu",
            session_id=target_session
        )

        # Review the complete conversation
        for message in conversation['messages']:
            print(f"Q: {message['user_message']}")
            print(f"A: {message['assistant_message']}")
            print("---")
"""

# Standard library imports
from typing import Dict, Any, Optional, List  # Type hints for better code clarity
import logging                               # For debug and status logging

from ..exceptions import RaggerAPIError
from ..constants import ErrorCodes

# Set up logging for this module
# This helps with debugging and monitoring chat history operations
logger = logging.getLogger(__name__)


class ChatHistoryAPI:
    """
    Interface for accessing conversation history and session management.

    This class provides comprehensive access to chat history in the Ragger system,
    enabling users to review past conversations, continue sessions, and analyze
    interaction patterns. It's designed to support both individual users looking
    up their own conversations and administrators analyzing usage patterns.

    Think of this as your "conversation memory" - it remembers every interaction
    with the AI system and makes that history searchable and accessible.

    Key Responsibilities:
    ====================

    **Session Management:**
    - List all conversation sessions for a user
    - Retrieve complete conversation details
    - Provide session metadata and summaries

    **Message Access:**
    - Access individual questions and answers
    - Include timestamps and processing metadata
    - Maintain chronological conversation order

    **Privacy & Security:**
    - Enforce user-based access control
    - Respect organization and project boundaries
    - Ensure conversation privacy between users

    **Analytics Support:**
    - Provide conversation statistics and summaries
    - Enable usage pattern analysis
    - Support conversation search and filtering

    Data Structure:
    ==============

    **Sessions** contain:
    - Unique session identifier (UUID)
    - Creation timestamp
    - User identifier
    - Preview of conversation content
    - Message count and metadata

    **Messages** within sessions contain:
    - User question text
    - AI-generated response
    - Source document citations
    - Token usage information
    - Processing timestamps

    Example Usage:
        >>> # Get overview of all conversations
        >>> client = RaggerClient(base_url="...", token="...")
        >>>
        >>> sessions = client.chat_history.get_sessions(
        ...     organization="my-company",
        ...     project="support-docs",
        ...     user="support@company.com"
        ... )
        >>>
        >>> print(f"Found {len(sessions)} conversation sessions")
        >>> for session in sessions[:5]:  # Show first 5
        ...     print(f"Session {session['session_id']}: {session['preview']}")
        >>>
        >>> # Get detailed conversation
        >>> if sessions:
        ...     conversation = client.chat_history.get_session(
        ...         organization="my-company",
        ...         project="support-docs",
        ...         user="support@company.com",
        ...         session_id=sessions[0]['session_id']
        ...     )
        ...
        ...     print(f"Conversation has {len(conversation['messages'])} messages")
    """

    def __init__(self, client):
        """
        Initialize ChatHistoryAPI with reference to the main RaggerClient.

        This constructor is typically called by the RaggerClient during
        initialization. The client reference is used to make authenticated
        HTTP requests to the Ragger API chat history endpoints.

        Args:
            client (RaggerClient): The main RaggerClient instance that provides
                                 HTTP request capabilities and authentication.
                                 Must be properly initialized with valid credentials.

        Example:
            >>> # Typically done automatically by RaggerClient
            >>> client = RaggerClient(base_url="...", token="...")
            >>> # client.chat_history is now a ChatHistoryAPI instance
            >>>
            >>> # Manual instantiation (advanced usage)
            >>> from ragger_sdk.endpoints import ChatHistoryAPI
            >>> chat_api = ChatHistoryAPI(client)
        """
        # Store the client reference for making authenticated API requests
        self.client = client
        # Define the endpoint for all chat history operations
        self.endpoint = "/history/"

    def get_sessions(
        self,
        organization: str,
        project: str,
        user: str
    ) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user within a project.

        This method retrieves all conversation sessions between a specific user
        and the AI system within a project, including all messages, timestamps,
        and metadata for each session.

        Args:
            organization (str): Organization identifier for multi-tenant isolation
            project (str): Project name containing the chat sessions
            user (str): User identifier (email, UUID, etc.) for session filtering

        Returns:
            List[Dict[str, Any]]: List of chat sessions, each containing:
                - session_id: Unique session identifier (UUID)
                - messages: List of conversation messages with:
                  - role: Message role (user, assistant, system)
                  - content: Message content text
                  - timestamp: Message timestamp
                  - metadata: Additional message metadata
                  - order: Message order in conversation
                - created_at: Session creation timestamp (ISO format)
                - updated_at: Session last update timestamp (ISO format)

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty/invalid parameters
                           - .is_auth_error() for invalid authentication tokens
                           - .is_not_found() for missing organization/project/user
                           - .is_server_error() for API request failures

        Example:
            ```python
            # Get all sessions for a user
            sessions = client.chat_history.get_sessions(
                organization="tech-startup",
                project="product-docs",
                user="analyst@company.com"
            )

            for session in sessions:
                print(f"Session {session['session_id']}: {len(session['messages'])} messages")
                for message in session['messages']:
                    print(f"  {message['role']}: {message['content'][:50]}...")
            ```

        Notes:
            - Returns all sessions for the user in chronological order
            - Each session contains complete conversation history
            - Messages include role information (user, assistant, system)
            - Timestamps are in ISO format for easy parsing
            - Empty list returned if user has no chat sessions
        """
        # Validate required parameters
        if not organization or not organization.strip():
            raise RaggerAPIError("Organization parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        if not project or not project.strip():
            raise RaggerAPIError("Project parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        if not user or not user.strip():
            raise RaggerAPIError("User parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        # Prepare query parameters
        params = {
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip()
        }

        logger.debug(
            f"Retrieving all chat sessions for {organization}/{project} "
            f"(user: {user})"
        )

        # Make API request to get all sessions
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint,
            params=params
        )

        logger.debug(
            f"Retrieved {len(response)} chat sessions for {organization}/{project} "
            f"(user: {user})"
        )
        return response

    def get_session(
        self,
        organization: str,
        project: str,
        user: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific chat session by session ID.

        This method retrieves a single conversation session with all its messages,
        timestamps, and metadata. Useful for getting detailed information about
        a specific conversation.

        Args:
            organization (str): Organization identifier for multi-tenant isolation
            project (str): Project name containing the chat session
            user (str): User identifier (email, UUID, etc.) for session access
            session_id (str): Unique session identifier (UUID) to retrieve

        Returns:
            Dict[str, Any]: Single chat session containing:
                - session_id: Unique session identifier (UUID)
                - messages: List of conversation messages with:
                  - role: Message role (user, assistant, system)
                  - content: Message content text
                  - timestamp: Message timestamp
                  - metadata: Additional message metadata
                  - order: Message order in conversation
                - created_at: Session creation timestamp (ISO format)
                - updated_at: Session last update timestamp (ISO format)

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty/invalid parameters
                           - .is_auth_error() for invalid authentication tokens
                           - .is_not_found() for missing organization/project/user/session
                           - .is_server_error() for API request failures

        Example:
            ```python
            # Get specific session details
            session = client.chat_history.get_session(
                organization="tech-startup",
                project="product-docs",
                user="analyst@company.com",
                session_id="550e8400-e29b-41d4-a716-446655440000"
            )

            print(f"Session created: {session['created_at']}")
            print(f"Total messages: {len(session['messages'])}")

            # Show conversation flow
            for message in session['messages']:
                role_emoji = "🤖" if message['role'] == 'assistant' else "👤"
                print(f"{role_emoji} {message['content']}")
            ```

        Notes:
            - Returns single session as first item in list (API returns array)
            - Session ID must be a valid UUID format
            - Access restricted to session owner and organization members
            - Messages ordered by timestamp/order field
            - Includes complete conversation context
        """
        # Validate required parameters
        if not organization or not organization.strip():
            raise RaggerAPIError("Organization parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        if not project or not project.strip():
            raise RaggerAPIError("Project parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        if not user or not user.strip():
            raise RaggerAPIError("User parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        if not session_id or not session_id.strip():
            raise RaggerAPIError("Session ID parameter is required and cannot be empty", ErrorCodes.MISSING_REQUIRED_PARAMETERS)

        # Prepare query parameters
        params = {
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip(),
            "session": session_id.strip()
        }

        logger.debug(
            f"Retrieving chat session {session_id} for {organization}/{project} "
            f"(user: {user})"
        )

        # Make API request to get specific session
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint,
            params=params
        )

        # API returns array even for single session, extract first item
        if isinstance(response, list) and len(response) > 0:
            session_data = response[0]
            logger.debug(
                f"Retrieved chat session {session_id} with {len(session_data.get('messages', []))} messages"
            )
            return session_data
        else:
            # This shouldn't happen if API is working correctly, but handle gracefully
            logger.warning(f"Unexpected response format for session {session_id}")
            return response

    def get_user_sessions_summary(
        self,
        organization: str,
        project: str,
        user: str
    ) -> Dict[str, Any]:
        """
        Get a summary of all chat sessions for a user.

        This is a convenience method that retrieves all sessions and provides
        a summary with session count, total messages, and recent activity.

        Args:
            organization (str): Organization identifier
            project (str): Project name
            user (str): User identifier

        Returns:
            Dict[str, Any]: Summary information containing:
                - total_sessions: Number of chat sessions
                - total_messages: Total messages across all sessions
                - sessions: List of session summaries with:
                  - session_id: Session identifier
                  - message_count: Number of messages in session
                  - created_at: Session creation time
                  - last_activity: Most recent message time

        Example:
            ```python
            summary = client.chat_history.get_user_sessions_summary(
                organization="tech-startup",
                project="product-docs",
                user="analyst@company.com"
            )

            print(f"User has {summary['total_sessions']} sessions")
            print(f"Total messages: {summary['total_messages']}")
            ```
        """
        # Get all sessions for the user
        sessions = self.get_sessions(organization, project, user)

        total_sessions = len(sessions)
        total_messages = 0
        session_summaries = []

        for session in sessions:
            messages = session.get('messages', [])
            message_count = len(messages)
            total_messages += message_count

            # Find last activity (most recent message timestamp)
            last_activity = session.get('created_at')
            if messages:
                # Get the timestamp of the last message
                last_message = max(messages, key=lambda m: m.get('timestamp', 0))
                last_activity = last_message.get('timestamp', session.get('created_at'))

            session_summaries.append({
                'session_id': session.get('session_id'),
                'message_count': message_count,
                'created_at': session.get('created_at'),
                'last_activity': last_activity
            })

        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'sessions': session_summaries
        }
