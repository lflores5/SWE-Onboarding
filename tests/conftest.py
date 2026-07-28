"""Pytest configuration and fixtures for the Support Tickets API tests.

This file configures the test environment to use an in-memory repository
instead of connecting to Azure Cosmos DB.
"""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def disable_cosmos_for_tests():
    """Disable Cosmos DB for all tests to force using the in-memory repository.

    This fixture runs automatically for all tests and ensures that Cosmos DB
    credentials are not available, forcing the app to use InMemoryTicketRepository.
    """
    # Clear Cosmos DB environment variables for the duration of the test session
    with patch.dict(
        os.environ,
        {
            "COSMOS_DB_ENDPOINT": "",
            "COSMOS_DB_KEY": "",
        },
        clear=False,
    ):
        # Also update the settings instance that may have already been loaded
        from app.config import Settings

        original_endpoint = Settings.cosmos_endpoint
        original_key = Settings.cosmos_key

        Settings.cosmos_endpoint = ""
        Settings.cosmos_key = ""

        yield

        # Restore original values after tests
        Settings.cosmos_endpoint = original_endpoint
        Settings.cosmos_key = original_key


@pytest.fixture(autouse=True)
def reset_repository():
    """Reset the repository between tests.

    This ensures that each test starts with a clean state by recreating
    the in-memory repository.
    """
    # Import here to ensure settings are already patched
    from app import main
    from app.db import InMemoryTicketRepository

    # Replace the repository with a fresh in-memory instance
    main.repository = InMemoryTicketRepository()

    yield

    # Cleanup (repository will be replaced in next test)
