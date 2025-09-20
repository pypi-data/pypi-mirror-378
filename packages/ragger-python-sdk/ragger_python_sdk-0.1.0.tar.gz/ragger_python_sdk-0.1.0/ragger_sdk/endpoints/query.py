
import logging

from typing import Dict
from typing import Any
from typing import Optional

logger = logging.getLogger(__name__)

class QueryAPI:
    """
    Interface for AI-powered natural language querying in the Ragger API.

    This class represents the culmination of the RAG workflow - the moment where
    users can ask natural language questions about their documents and receive
    intelligent, source-backed answers from AI.

    Think of this as your "smart search assistant" that not only finds relevant
    information but also synthesizes it into coherent answers and tells you
    exactly where the information came from.

    Core Capabilities:
    =================

    **Natural Language Understanding:**
    Ask questions in plain language without needing to know specific keywords
    or document structure. The system understands context, synonyms, and intent.

    **Intelligent Response Generation:**
    Get coherent, well-structured answers that synthesize information from
    multiple sources rather than just returning raw document chunks.

    **Source Attribution:**
    Every answer includes citations showing exactly which documents and text
    sections were used, enabling verification and further exploration.

    **Conversation Continuity:**
    Maintain context across multiple questions using session IDs, enabling
    natural follow-up questions and conversational interactions.

    **Usage Transparency:**
    Detailed token usage and cost tracking helps monitor AI service consumption
    and optimize for both quality and efficiency.

    Query Types Supported:
    =====================

    **Factual Questions:**
    - "What is the return policy?"
    - "Who is the CEO of the company?"
    - "What are the system requirements?"

    **Analytical Questions:**
    - "What are the main benefits mentioned?"
    - "Compare the different pricing plans"
    - "Summarize the key findings"

    **Procedural Questions:**
    - "How do I set up the integration?"
    - "What steps are needed to deploy?"
    - "Can you walk me through the process?"

    **Contextual Follow-ups:**
    - "Tell me more about that" (after a previous answer)
    - "What are some examples?" (building on context)
    - "How does this relate to our earlier discussion?"

    Session Management:
    ==================

    Sessions enable conversational interactions where the AI remembers context
    from previous questions in the same conversation. This allows for:

    - Natural follow-up questions using pronouns ("What about it?")
    - Building on previous topics ("Tell me more about that feature")
    - Maintaining conversation flow across multiple queries
    - User-specific conversation history for personalization

    Example Usage:
        >>> # Start a new conversation
        >>> client = RaggerClient(base_url="...", token="...")
        >>>
        >>> # Ask initial question
        >>> response = client.query.ask(
        ...     query="What is machine learning?",
        ...     organization="ai-company",
        ...     project="research-docs",
        ...     user="researcher@company.com"
        ... )
        >>>
        >>> print(response['answer'])  # AI-generated explanation
        >>> print(f"Sources: {len(response['metadata']['source_nodes'])}")
        >>>
        >>> # Ask follow-up using the same session
        >>> follow_up = client.query.ask(
        ...     query="What are practical applications?",
        ...     organization="ai-company",
        ...     project="research-docs",
        ...     user="researcher@company.com",
        ...     session_id=response['session_id']  # Continue conversation
        ... )
        >>>
        >>> # AI understands "applications" refers to ML applications
    """

    def __init__(self, client):
        """
        Initialize QueryAPI with reference to the main RaggerClient.

        This constructor is typically called by the RaggerClient during
        initialization. The client reference is used to make authenticated
        HTTP requests to the Ragger API query endpoint.

        Args:
            client (RaggerClient): The main RaggerClient instance that provides
                                 HTTP request capabilities and authentication.
                                 Must be properly initialized with valid credentials.

        Example:
            >>> # Typically done automatically by RaggerClient
            >>> client = RaggerClient(base_url="...", token="...")
            >>> # client.query is now a QueryAPI instance
            >>>
            >>> # Manual instantiation (advanced usage)
            >>> from ragger_sdk.endpoints import QueryAPI
            >>> query_api = QueryAPI(client)
        """
        # Store the client reference for making authenticated API requests
        self.client = client
        # Define the endpoint for all query operations
        self.endpoint = "/query/"

    def ask(
        self,
        query: str,
        organization: str,
        project: str,
        user: str,
        session_id: Optional[str] = None,
        is_strict: bool = False
    ) -> Dict[str, Any]:
        """
        Ask a natural language question about your indexed documents.

        This is the core method of the RAG system - where natural language questions
        are transformed into intelligent, source-backed answers using your document
        collection. The process involves sophisticated AI techniques but is exposed
        through this simple interface.

        How It Works:
        ============

        1. **Query Processing**: Your question is analyzed and converted to vectors
        2. **Semantic Search**: Relevant document chunks are found using vector similarity
        3. **Context Assembly**: The most relevant text is gathered as context
        4. **AI Generation**: A language model generates an answer using the context
        5. **Citation**: Sources are provided for verification and follow-up
        6. **Session Tracking**: Conversation context is maintained for follow-ups

        This ensures answers are both intelligent and grounded in your actual data.

        Args:
            query (str): The natural language question to be answered.
            organization (str): The name of the organization.
            project (str): The name of the project containing the indexed documents.
            user (str): The identifier for the user making the query. Recommended to use an email.
            session_id (str, optional): The ID of an existing chat session for context.
            is_strict (bool, optional): If true, only use documents from the project

        Returns:
            dict: Comprehensive response containing:
                - 'session_id' (str): Session identifier for conversation continuity
                - 'query' (str): Your original question (echoed back)
                - 'answer' (str): AI-generated response with source references
                - 'num_messages' (int): Total messages in this session
                - 'metadata' (dict): Detailed processing information:
                  - 'token_usage': Token counts and cost breakdown
                  - 'model': AI model used for response generation
                  - 'embedding_model': Model used for document search
                  - 'source_nodes': List of source documents with:
                    - Document names and metadata
                    - Relevant text chunks that were used
                    - Relevance scores and citations
                  - 'processing_time': How long the query took to process
                  - 'retrieval_method': Search strategy used

        Raises:
            RaggerAPIError: For all types of errors. Use boolean methods to check:
                           - .is_validation_error() for empty or invalid parameters
                           - .is_auth_error() for invalid or expired authentication tokens
                           - .is_not_found() for missing organization, project, or index
                           - .is_server_error() for network errors, server issues, or processing failures

        Examples:
            >>> # Simple question-answer
            >>> response = client.query.ask(
            ...     query="What is the company's mission statement?",
            ...     organization="acme-corp",
            ...     project="company-docs",
            ...     user="employee@acme.com"
            ... )
            >>> print(f"Answer: {response['answer']}")
            >>> print(f"Based on {len(response['metadata']['source_nodes'])} sources")
            >>>
            >>> # Conversational follow-up
            >>> follow_up = client.query.ask(
            ...     query="How does this relate to our values?",  # "this" refers to mission
            ...     organization="acme-corp",
            ...     project="company-docs",
            ...     user="employee@acme.com",
            ...     session_id=response['session_id']  # Continue the conversation
            ... )
            >>>
            >>> # Complex analytical query
            >>> analysis = client.query.ask(
            ...     query="Compare the Q3 and Q4 sales performance and identify key trends",
            ...     organization="acme-corp",
            ...     project="financial-reports",
            ...     user="analyst@acme.com"
            ... )
            >>>
            >>> # Access detailed source information
            >>> for i, source in enumerate(analysis['metadata']['source_nodes']):
            ...     print(f"Source {i+1}: {source['metadata']['file_name']}")
            ...     print(f"  Relevance: {source['score']:.2f}")
            ...     print(f"  Text: {source['text'][:100]}...")

        Tips for Better Results:
            - Be specific in your questions for more targeted answers
            - Use follow-up questions to dive deeper into topics
            - Check the source_nodes to verify and explore further
            - Monitor token_usage to understand AI service consumption
            - Use descriptive user identifiers for better session management

        Prerequisites:
            - Documents must be uploaded to the specified project
            - A vector index must be created for the project
            - The index must be in 'created' status (not 'creating' or 'failed')
        """
        # Prepare the API request payload
        # Clean whitespace from all parameters to avoid parsing issues
        data = {
            "query": query.strip(),
            "organization": organization.strip(),
            "project": project.strip(),
            "user": user.strip(),
            "session_id": session_id.strip() if session_id else None,
            "is_strict": is_strict,
        }

        # Log the query operation for debugging and monitoring
        session_info = f"(continuing session {session_id})" if session_id else "(new session)"
        logger.debug(
            f"Processing query for {organization}/{project} "
            f"(user: {user}) {session_info}"
        )

        # Make the API request to process the query
        response = self.client.request(
            method="POST",           # POST to submit query data
            endpoint=self.endpoint,  # /query/ endpoint
            data=data               # Query and context parameters
        )

        # Log successful completion and return the response
        session_id_result = response.get('session_id', 'N/A')
        logger.debug(
            f"Query processed successfully for {organization}/{project} "
            f"(session: {session_id_result})"
        )
        return response
