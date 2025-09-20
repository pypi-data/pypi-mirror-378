"""
Ragger SDK - Constants and Configuration
"""

from typing import Dict, List, Final


class APIEndpoints:
    """API endpoint paths."""

    DOCUMENTS_FILE: Final[str] = "/documents/file/"
    DOCUMENTS_TEXT: Final[str] = "/documents/text/"
    INDEX: Final[str] = "/index/"
    QUERY: Final[str] = "/query/"
    CHAT_HISTORY: Final[str] = "/history/"


class SupportedEmbeddingModels:
    """Supported embedding models."""

    TEXT_EMBEDDING_3_SMALL: Final[str] = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE: Final[str] = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002: Final[str] = "text-embedding-ada-002"

    @classmethod
    def get_all_models(cls) -> List[str]:
        """Get list of all supported embedding models."""
        return [
            cls.TEXT_EMBEDDING_3_SMALL,
            cls.TEXT_EMBEDDING_3_LARGE,
            cls.TEXT_EMBEDDING_ADA_002
        ]


class ErrorCodes:
    """API error codes."""

    INVALID_SETTINGS = "invalid_settings"
    MISSING_REQUIRED_PARAMETERS = "missing_required_parameters"
    RESOURCE_CONFLICT = "resource_conflict"
    RESOURCE_NOT_FOUND = "resource_not_found"
    UNEXPECTED_ERROR = "unexpected_error"


class FileConstants:
    """File upload constants."""

    SUPPORTED_EXTENSIONS: Final[List[str]] = [
        ".pdf", ".txt", ".docx", ".doc", ".rtf", ".md", ".html", ".csv", ".json"
    ]
    MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100 MB


class LoggingConfig:
    """Logging configuration."""

    DEFAULT_LOG_LEVEL: Final[str] = "INFO"
    INDEX_LOGGER_NAME: Final[str] = "ragger_sdk.index"
