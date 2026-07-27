"""Configuration management for the Support Tickets API.

This module loads environment variables from a .env file and provides
a centralized Settings class for accessing application configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables.

    Attributes:
        cosmos_endpoint: Azure Cosmos DB endpoint URL
        cosmos_key: Azure Cosmos DB master key
        cosmos_database_id: Cosmos DB database name
        cosmos_container_id: Cosmos DB container name
    """

    # Azure Cosmos DB credentials
    cosmos_endpoint: str = os.getenv("COSMOS_DB_ENDPOINT", "")
    cosmos_key: str = os.getenv("COSMOS_DB_KEY", "")
    cosmos_database_id: str = os.getenv("COSMOS_DB_NAME", "support")
    cosmos_container_id: str = os.getenv("COSMOS_CONTAINER_NAME", "tickets")

    @classmethod
    def is_cosmos_configured(cls) -> bool:
        """Check if Cosmos DB credentials are configured.

        Returns:
            True if both endpoint and key are set, False otherwise.
        """
        return bool(cls.cosmos_endpoint and cls.cosmos_key)


# Create a singleton instance of the Settings class
settings = Settings()
