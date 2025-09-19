"""Tests for GHSA client."""

import pytest
import logging
from unittest.mock import patch, MagicMock

from ghsa_client import GHSAClient, GHSA_ID, RateLimitExceeded


class TestGHSAClient:
    def test_initialization_without_token(self) -> None:
        """Test client initialization without GitHub token."""
        logger = logging.getLogger(__name__)
        client = GHSAClient(logger=logger)
        assert client.base_url == "https://api.github.com"
        assert "Authorization" not in client.session.headers
    
    def test_initialization_with_token(self) -> None:
        """Test client initialization with GitHub token."""
        logger = logging.getLogger(__name__)
        with patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}):
            client = GHSAClient(logger=logger)
            assert client.session.headers["Authorization"] == "Bearer test-token"
    
    def test_initialization_with_custom_url(self) -> None:
        """Test client initialization with custom base URL."""
        logger = logging.getLogger(__name__)
        client = GHSAClient(logger=logger, base_url="https://custom.github.com")
        assert client.base_url == "https://custom.github.com"
    
    @patch('ghsa_client.client.requests.Session.get')
    def test_get_advisory_success(self, mock_get: MagicMock) -> None:
        """Test successful advisory retrieval."""
        logger = logging.getLogger(__name__)
        client = GHSAClient(logger=logger)
        
        # Mock rate limit response
        mock_rate_limit_response = MagicMock()
        mock_rate_limit_response.json.return_value = {
            "resources": {
                "core": {
                    "remaining": 5000,
                    "reset": 1234567890
                }
            }
        }
        mock_rate_limit_response.raise_for_status.return_value = None
        
        # Mock advisory response
        mock_advisory_response = MagicMock()
        mock_advisory_response.json.return_value = {
            "ghsa_id": "GHSA-gq96-8w38-hhj2",
            "summary": "Test advisory",
            "severity": "high",
            "published_at": "2024-01-01T00:00:00Z",
            "vulnerabilities": []
        }
        mock_advisory_response.raise_for_status.return_value = None
        
        # Configure mock to return different responses for different URLs
        def side_effect(*args: object, **kwargs: object) -> MagicMock:
            url = str(args[0]) if args else ""
            if "rate_limit" in url:
                return mock_rate_limit_response
            else:
                return mock_advisory_response
        
        mock_get.side_effect = side_effect
        
        # Test
        ghsa_id = GHSA_ID("GHSA-gq96-8w38-hhj2")
        advisory = client.get_advisory(ghsa_id)
        
        assert advisory.ghsa_id.id == "GHSA-gq96-8w38-hhj2"
        assert advisory.summary == "Test advisory"
        assert advisory.severity == "high"
