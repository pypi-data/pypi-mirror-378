#!/usr/bin/env python3
"""
Unit Tests for HeySol API Client - API Endpoints

Tests individual API endpoints with mock responses, covering:
- User endpoints
- Memory endpoints
- Spaces endpoints
- Webhook endpoints
- Response parsing and validation
"""

import json
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest
import requests_mock

from heysol.client import HeySolClient
from heysol.exceptions import ValidationError


class TestAPIEndpoints:
    """Unit tests for individual API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return HeySolClient(api_key="test-api-key", skip_mcp_init=True)

    @pytest.fixture
    def mock_setup(self, requests_mock):
        """Set up comprehensive mocks for all API endpoints."""
        # User endpoints
        requests_mock.get(
            "https://core.heysol.ai/api/v1/user/profile",
            json={
                "id": "user-123",
                "name": "Test User",
                "email": "test@example.com",
                "role": "admin",
                "created_at": "2024-01-01T00:00:00Z",
            },
        )

        # Memory endpoints
        requests_mock.post(
            "https://core.heysol.ai/api/v1/search", json={"episodes": [], "total": 0}
        )

        # Spaces endpoints
        requests_mock.get("https://core.heysol.ai/api/v1/spaces", json={"spaces": []})

        requests_mock.post(
            "https://core.heysol.ai/api/v1/spaces",
            json={"space": {"id": "space-123", "name": "Test Space"}},
        )

        # Webhook endpoints
        requests_mock.post(
            "https://core.heysol.ai/api/v1/webhooks",
            json={"id": "webhook-123", "url": "https://example.com/webhook"},
        )

        requests_mock.get("https://core.heysol.ai/api/v1/webhooks", json=[])

        return requests_mock

    def test_check_ingestion_status_success(self, client, requests_mock):
        """Test successful check_ingestion_status method."""
        # Mock logs endpoint to return empty (simulating unavailable)
        requests_mock.get(
            "https://core.heysol.ai/api/v1/logs?limit=5&offset=0",
            exc=Exception("Endpoint not available"),
        )

        # Mock search endpoint to return data
        requests_mock.post(
            "https://core.heysol.ai/api/v1/search",
            json={"episodes": [{"content": "test data", "id": "ep-123"}], "total": 1},
        )

        result = client.check_ingestion_status()

        assert result["ingestion_status"] == "no_logs_found"
        assert result["search_status"] == "data_available"
        assert len(result["recommendations"]) > 0
        assert "search" in result["available_methods"]

    def test_check_ingestion_status_with_space_id(self, client, requests_mock):
        """Test check_ingestion_status with space ID."""
        # Mock logs endpoint to return empty
        requests_mock.get(
            "https://core.heysol.ai/api/v1/logs?limit=5&offset=0&spaceId=space-123",
            exc=Exception("Endpoint not available"),
        )

        # Mock search endpoint with space filter
        requests_mock.post(
            "https://core.heysol.ai/api/v1/search", json={"episodes": [], "total": 0}
        )

        result = client.check_ingestion_status(space_id="space-123")

        assert result["ingestion_status"] == "no_logs_found"
        assert result["search_status"] == "no_search_results"
        assert result["space_id"] == "space-123"

    def test_get_ingestion_logs_with_status_filter(self, client, requests_mock):
        """Test get_ingestion_logs with status filtering."""
        requests_mock.get(
            "https://core.heysol.ai/api/v1/logs?limit=100&offset=0&status=success",
            json={"logs": [{"id": "log-1", "status": "success"}]},
        )

        result = client.get_ingestion_logs(status="success")

        assert len(result) == 1
        assert result[0]["status"] == "success"

    def test_get_ingestion_logs_endpoint_unavailable(self, client, requests_mock):
        """Test get_ingestion_logs when endpoint is unavailable."""
        requests_mock.get(
            "https://core.heysol.ai/api/v1/logs?limit=100&offset=0",
            exc=Exception("Service unavailable"),
        )

        result = client.get_ingestion_logs()

        assert result == []  # Should return empty list

    def test_get_specific_log_error_handling(self, client, requests_mock):
        """Test get_specific_log error handling."""
        requests_mock.get(
            "https://core.heysol.ai/api/v1/logs/log-123", exc=Exception("Log not found")
        )

        result = client.get_specific_log("log-123")

        assert "error" in result
        assert result["log_id"] == "log-123"
        assert "Log retrieval failed" in result["error"]

    def test_list_webhooks_endpoint_unavailable(self, client, requests_mock):
        """Test list_webhooks when endpoint is unavailable."""
        requests_mock.get(
            "https://core.heysol.ai/api/v1/webhooks?limit=100&offset=0",
            exc=Exception("Webhooks endpoint unavailable"),
        )

        result = client.list_webhooks()

        assert result == []  # Should return empty list

    def test_get_logs_by_source_mcp_unavailable(self, client):
        """Test get_logs_by_source when MCP is unavailable."""
        # Client is created with skip_mcp_init=True, so MCP is not available
        result = client.get_logs_by_source("test-source")

        assert result["logs"] == []
        assert result["total_count"] == 0
        assert result["source"] == "test-source"
        assert "note" in result
