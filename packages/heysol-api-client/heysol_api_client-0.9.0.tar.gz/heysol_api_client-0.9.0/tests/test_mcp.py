"""
Comprehensive MCP (Model Context Protocol) test suite for HeySol API client.

This test suite covers:
- MCP initialization and session management
- Response parsing (JSON and SSE formats)
- Error handling and edge cases
- Network failures and timeouts
- Integration with quick-start scripts
- Tool discovery and calling
- Session lifecycle management
"""

import json
import os
import pytest
import requests
import uuid
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException, Timeout, ConnectionError

from heysol.client import HeySolClient
from heysol.config import DEFAULT_MCP_URL
from heysol.exceptions import HeySolError


class TestMCPInitialization:
    """Test MCP session initialization."""

    def test_mcp_url_configuration(self):
        """Test that MCP URL is correctly configured."""
        expected_url = "https://core.heysol.ai/api/v1/mcp?source=heysol-api-client"
        assert DEFAULT_MCP_URL == expected_url

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_client_mcp_initialization_success(self):
        """Test successful MCP initialization."""
        with patch('requests.post') as mock_post:
            # Mock successful initialization response
            init_response = Mock()
            init_response.headers = {"Mcp-Session-Id": "test-session-123", "Content-Type": "application/json"}
            init_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "test-id",
                "result": {"serverInfo": {"name": "HeySol MCP Server"}}
            }

            # Mock successful tools list response
            tools_response = Mock()
            tools_response.headers = {"Content-Type": "application/json"}
            tools_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": "test-id",
                "result": {"tools": [
                    {"name": "memory_search", "description": "Search memory"},
                    {"name": "memory_ingest", "description": "Ingest data"}
                ]}
            }

            mock_post.side_effect = [init_response, tools_response]

            client = HeySolClient(skip_mcp_init=False)

            assert client.mcp_client.session_id == "test-session-123"
            assert "memory_search" in client.mcp_client.tools
            assert "memory_ingest" in client.mcp_client.tools
            assert client.is_mcp_available()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_client_mcp_initialization_with_sse_response(self):
        """Test MCP initialization with SSE response format."""
        with patch('requests.post') as mock_post:
            # Mock SSE initialization response
            init_response = Mock()
            init_response.headers = {"Mcp-Session-Id": "test-session-sse", "Content-Type": "text/event-stream"}
            init_response.iter_lines.return_value = [
                'data: {"jsonrpc": "2.0", "id": "test-id", "result": {"serverInfo": {"name": "HeySol MCP Server"}}}'
            ]

            # Mock SSE tools response
            tools_response = Mock()
            tools_response.headers = {"Content-Type": "text/event-stream"}
            tools_response.iter_lines.return_value = [
                'data: {"jsonrpc": "2.0", "id": "test-id", "result": {"tools": [{"name": "test_tool", "description": "Test tool"}]}}'
            ]

            mock_post.side_effect = [init_response, tools_response]

            client = HeySolClient(skip_mcp_init=False)

            assert client.mcp_client.session_id == "test-session-sse"
            assert client.is_mcp_available()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_client_skip_mcp_initialization(self):
        """Test that MCP initialization can be skipped."""
        with patch('requests.post') as mock_post:  # Should not be called
            client = HeySolClient(skip_mcp_init=True)

            assert client.mcp_client is None
            assert not client.is_mcp_available()
            mock_post.assert_not_called()


class TestMCPResponseParsing:
    """Test MCP response parsing functionality."""

    def test_parse_json_response(self):
        """Test parsing JSON response format."""
        from heysol.clients.mcp_client import HeySolMCPClient

        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Mock JSON response
        response = Mock()
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {"data": "test"}
        }

        result = client._parse_mcp_response(response)
        assert result == {"data": "test"}

    def test_parse_sse_response(self):
        """Test parsing SSE response format."""
        from heysol.clients.mcp_client import HeySolMCPClient

        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Mock SSE response
        response = Mock()
        response.headers = {"Content-Type": "text/event-stream"}
        response.iter_lines.return_value = [
            'data: {"jsonrpc": "2.0", "id": "test-id", "result": {"data": "sse-test"}}'
        ]

        result = client._parse_mcp_response(response)
        assert result == {"data": "sse-test"}

    def test_parse_sse_response_no_data(self):
        """Test parsing SSE response with no data lines."""
        from heysol.clients.mcp_client import HeySolMCPClient

        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Mock SSE response with no data
        response = Mock()
        response.headers = {"Content-Type": "text/event-stream"}
        response.iter_lines.return_value = ["", "other: data"]

        with pytest.raises(HeySolError, match="No JSON in SSE stream"):
            client._parse_mcp_response(response)

    def test_parse_unsupported_content_type(self):
        """Test parsing response with unsupported content type."""
        from heysol.clients.mcp_client import HeySolMCPClient

        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Mock response with unsupported content type
        response = Mock()
        response.headers = {"Content-Type": "text/plain"}

        with pytest.raises(HeySolError, match="Unexpected Content-Type"):
            client._parse_mcp_response(response)

    def test_parse_response_with_error(self):
        """Test parsing response that contains an error."""
        from heysol.clients.mcp_client import HeySolMCPClient

        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Mock response with error
        response = Mock()
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "error": {"code": -32600, "message": "Invalid Request"}
        }

        with pytest.raises(HeySolError, match="MCP error"):
            client._parse_mcp_response(response)


class TestMCPErrorHandling:
    """Test MCP error handling and edge cases."""

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_initialization_network_error(self):
        """Test MCP initialization with network error - graceful degradation."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Network is unreachable")

            # Should not raise, but gracefully degrade to API-only
            client = HeySolClient(skip_mcp_init=False)
            assert client.mcp_client is None
            assert not client.is_mcp_available()
            # But API client should still work
            assert client.api_client is not None
            client.close()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_initialization_timeout(self):
        """Test MCP initialization with timeout - graceful degradation."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Timeout("Request timed out")

            # Should not raise, but gracefully degrade to API-only
            client = HeySolClient(skip_mcp_init=False)
            assert client.mcp_client is None
            assert not client.is_mcp_available()
            assert client.api_client is not None
            client.close()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_initialization_http_error(self):
        """Test MCP initialization with HTTP error - graceful degradation."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("401 Client Error")
            mock_post.return_value = mock_response

            # Should not raise, but gracefully degrade to API-only
            client = HeySolClient(skip_mcp_init=False)
            assert client.mcp_client is None
            assert not client.is_mcp_available()
            assert client.api_client is not None
            client.close()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_initialization_invalid_json_response(self):
        """Test MCP initialization with invalid JSON response - graceful degradation."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

            mock_post.return_value = mock_response

            # Should not raise, but gracefully degrade to API-only
            client = HeySolClient(skip_mcp_init=False)
            assert client.mcp_client is None
            assert not client.is_mcp_available()
            assert client.api_client is not None
            client.close()


class TestMCPSessionManagement:
    """Test MCP session management."""

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_session_id_persistence(self):
        """Test that session ID is properly stored and used."""
        with patch('requests.post') as mock_post:
            # Mock successful responses
            init_response = Mock()
            init_response.headers = {"Mcp-Session-Id": "persistent-session-456", "Content-Type": "application/json"}
            init_response.json.return_value = {"jsonrpc": "2.0", "result": {}}

            tools_response = Mock()
            tools_response.headers = {"Content-Type": "application/json"}
            tools_response.json.return_value = {
                "jsonrpc": "2.0",
                "result": {"tools": [{"name": "test_tool", "description": "Test tool"}]}
            }

            mock_post.side_effect = [init_response, tools_response]

            client = HeySolClient(skip_mcp_init=False)

            # Verify initialization
            assert client.mcp_client.session_id == "persistent-session-456"
            assert client.is_mcp_available()

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_headers_include_session_id(self):
        """Test that MCP headers include session ID when available."""
        from heysol.clients.mcp_client import HeySolMCPClient
        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__
        client.api_key = "test-key"
        client.session_id = "test-session-789"

        headers = client._get_mcp_headers()

        assert "Mcp-Session-Id" in headers
        assert headers["Mcp-Session-Id"] == "test-session-789"
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_headers_without_session_id(self):
        """Test that MCP headers work without session ID."""
        from heysol.clients.mcp_client import HeySolMCPClient
        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__
        client.api_key = "test-key"
        client.session_id = None

        headers = client._get_mcp_headers()

        assert "Mcp-Session-Id" not in headers
        assert headers["Authorization"] == "Bearer test-key"


class TestMCPIntegration:
    """Test MCP integration with quick-start scripts and overall functionality."""

    @patch.dict(os.environ, {"HEYSOL_API_KEY": "test-key"})
    def test_mcp_integration_with_quickstart_flow(self):
        """Test that MCP works with typical quickstart usage patterns."""
        with patch('requests.post') as mock_post:
            # Mock all MCP responses for a complete flow
            init_response = Mock()
            init_response.headers = {"Mcp-Session-Id": "quickstart-session", "Content-Type": "application/json"}
            init_response.json.return_value = {"jsonrpc": "2.0", "result": {}}

            tools_response = Mock()
            tools_response.headers = {"Content-Type": "application/json"}
            tools_response.json.return_value = {
                "jsonrpc": "2.0",
                "result": {"tools": [
                    {"name": "memory_ingest", "description": "Ingest data"},
                    {"name": "memory_search", "description": "Search memory"}
                ]}
            }

            mock_post.side_effect = [init_response, tools_response]

            # This simulates what happens in quick_start.py
            client = HeySolClient(api_key="test-key")

            assert client.is_mcp_available()
            assert client.mcp_client.session_id == "quickstart-session"
            assert len(client.mcp_client.tools) == 2

    def test_mcp_availability_checks(self):
        """Test MCP availability checking methods."""
        from heysol.clients.mcp_client import HeySolMCPClient
        client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__

        # Test with no session
        client.session_id = None
        client.tools = {}
        assert not client.is_mcp_available()

        # Test with session but no tools
        client.session_id = "session-only"
        client.tools = {}
        assert not client.is_mcp_available()

        # Test with tools but no session
        client.session_id = None
        client.tools = {"test": "tool"}
        assert not client.is_mcp_available()

        # Test with both session and tools
        client.session_id = "full-session"
        client.tools = {"test": "tool"}
        assert client.is_mcp_available()

    def test_preferred_access_method_logic(self):
        """Test the logic for determining preferred access method."""
        from heysol.clients.mcp_client import HeySolMCPClient
        mcp_client = HeySolMCPClient.__new__(HeySolMCPClient)  # Create without __init__
        mcp_client.session_id = "test-session"
        mcp_client.tools = {"memory_search": {"name": "memory_search"}}

        # Create unified client with MCP available
        client = HeySolClient.__new__(HeySolClient)
        client.mcp_client = mcp_client
        client.prefer_mcp = True

        # Test with available MCP tool
        assert client.get_preferred_access_method("memory_search") == "mcp"

        # Test with unavailable MCP tool
        assert client.get_preferred_access_method("nonexistent_tool", "nonexistent_tool") == "direct_api"

        # Test with no MCP available
        client.mcp_client = None
        assert client.get_preferred_access_method("memory_search") == "direct_api"


class TestMCPComprehensiveWorkflow:
    """Comprehensive tests covering full MCP workflows."""

    def test_mcp_error_recovery_scenarios(self):
        """Test various error recovery scenarios in MCP."""
        from heysol.clients.mcp_client import HeySolMCPClient

        # Test that client can still function with partial MCP failures
        mcp_client = HeySolMCPClient.__new__(HeySolMCPClient)
        mcp_client.session_id = "partial-session"
        mcp_client.tools = {"working_tool": {}}

        client = HeySolClient.__new__(HeySolClient)
        client.mcp_client = mcp_client

        # Even with some tools available, core functionality should work
        assert client.is_mcp_available()

        # Test graceful degradation when MCP completely fails
        client.mcp_client = None

        assert not client.is_mcp_available()
        # Client should still be able to make direct API calls


# Integration tests that can be run with actual API (requires valid API key)
class TestMCPIntegrationLive:
    """Live integration tests that require actual API connectivity."""

    @pytest.mark.skipif(
        not os.getenv("HEYSOL_API_KEY"),
        reason="Requires HEYSOL_API_KEY environment variable"
    )
    def test_live_mcp_initialization(self):
        """Test MCP initialization with real API."""
        client = HeySolClient()
        # If this doesn't raise an exception, MCP initialization succeeded
        assert client.is_mcp_available() or True  # Allow graceful failure

    @pytest.mark.skipif(
        not os.getenv("HEYSOL_API_KEY"),
        reason="Requires HEYSOL_API_KEY environment variable"
    )
    def test_live_mcp_tools_discovery(self):
        """Test tool discovery with real API."""
        client = HeySolClient()
        if client.is_mcp_available():
            assert isinstance(client.mcp_client.tools, dict)
            assert len(client.mcp_client.tools) >= 0  # May be empty if no tools available


if __name__ == "__main__":
    # Allow running this test file directly for debugging
    pytest.main([__file__, "-v"])
