"""Unit tests for the _make_api_request_impl tool."""

import pytest
import json
from unittest.mock import Mock, patch
from requests.exceptions import (
    Timeout,
    ConnectionError as RequestsConnectionError,
    RequestException,
)

from openapi_navigator.server import _make_api_request_impl


class TestMakeApiRequest:
    """Test the _make_api_request_impl tool."""

    @patch("openapi_navigator.server.requests.request")
    def test_successful_get_request(self, mock_request):
        """Test a successful GET request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"message": "success"}'
        mock_response.url = "https://api.example.com/test"
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response

        result = _make_api_request_impl("https://api.example.com/test")

        assert result["status_code"] == 200
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["body"] == '{"message": "success"}'
        assert result["json"] == {"message": "success"}
        assert result["url"] == "https://api.example.com/test"
        assert result["method"] == "GET"
        assert "elapsed_ms" in result
        assert isinstance(result["elapsed_ms"], int)

        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="GET", url="https://api.example.com/test", timeout=30
        )

    @patch("openapi_navigator.server.requests.request")
    def test_post_request_with_data_and_headers(self, mock_request):
        """Test a POST request with data and headers."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Location": "/api/resource/123"}
        mock_response.text = '{"id": 123, "created": true}'
        mock_response.url = "https://api.example.com/resource"
        mock_response.json.return_value = {"id": 123, "created": True}
        mock_request.return_value = mock_response

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123",
        }
        data = '{"name": "test", "value": 42}'

        result = _make_api_request_impl(
            url="https://api.example.com/resource",
            method="POST",
            headers=headers,
            data=data,
        )

        assert result["status_code"] == 201
        assert result["method"] == "POST"
        assert result["json"] == {"id": 123, "created": True}

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.example.com/resource",
            timeout=30,
            headers=headers,
            data=data,
        )

    @patch("openapi_navigator.server.requests.request")
    def test_request_with_url_params(self, mock_request):
        """Test request with URL parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "[]"
        mock_response.url = "https://api.example.com/search?q=test&limit=10"
        mock_response.json.return_value = []
        mock_request.return_value = mock_response

        params = {"q": "test", "limit": "10"}

        result = _make_api_request_impl(
            url="https://api.example.com/search", params=params
        )

        assert result["status_code"] == 200
        assert result["json"] == []

        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/search",
            timeout=30,
            params=params,
        )

    @patch("openapi_navigator.server.requests.request")
    def test_different_http_methods(self, mock_request):
        """Test different HTTP methods."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.text = ""
        mock_response.url = "https://api.example.com/resource/123"
        mock_request.return_value = mock_response

        methods = ["PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in methods:
            result = _make_api_request_impl(
                url="https://api.example.com/resource/123", method=method
            )
            assert result["method"] == method
            assert result["status_code"] == 204

    @patch("openapi_navigator.server.requests.request")
    def test_non_json_response(self, mock_request):
        """Test handling of non-JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_response.url = "https://api.example.com/text"
        mock_response.json.side_effect = json.JSONDecodeError("Not JSON", "", 0)
        mock_request.return_value = mock_response

        result = _make_api_request_impl("https://api.example.com/text")

        assert result["status_code"] == 200
        assert result["body"] == "Plain text response"
        assert result["json"] is None

    @patch("openapi_navigator.server.requests.request")
    def test_empty_response_body(self, mock_request):
        """Test handling of empty response body."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.text = ""
        mock_response.url = "https://api.example.com/empty"
        mock_request.return_value = mock_response

        result = _make_api_request_impl("https://api.example.com/empty")

        assert result["status_code"] == 204
        assert result["body"] == ""
        assert result["json"] is None

    @patch("openapi_navigator.server.requests.request")
    def test_custom_timeout(self, mock_request):
        """Test custom timeout parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com/slow"
        mock_request.return_value = mock_response

        _make_api_request_impl("https://api.example.com/slow", timeout=60)

        mock_request.assert_called_once_with(
            method="GET", url="https://api.example.com/slow", timeout=60
        )

    def test_invalid_http_method(self):
        """Test validation of invalid HTTP method."""
        with pytest.raises(ValueError, match="Invalid HTTP method: INVALID"):
            _make_api_request_impl("https://api.example.com", method="INVALID")

    def test_empty_url(self):
        """Test validation of empty URL."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            _make_api_request_impl("")

    def test_none_url(self):
        """Test validation of None URL."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            _make_api_request_impl(None)

    @patch("openapi_navigator.server.requests.request")
    def test_timeout_error(self, mock_request):
        """Test handling of timeout errors."""
        mock_request.side_effect = Timeout("Request timed out")

        with pytest.raises(TimeoutError, match="Request timed out after 30 seconds"):
            _make_api_request_impl("https://api.example.com/slow")

    @patch("openapi_navigator.server.requests.request")
    def test_connection_error(self, mock_request):
        """Test handling of connection errors."""
        mock_request.side_effect = RequestsConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            _make_api_request_impl("https://api.nonexistent.com")

    @patch("openapi_navigator.server.requests.request")
    def test_general_request_exception(self, mock_request):
        """Test handling of general request exceptions."""
        mock_request.side_effect = RequestException("Something went wrong")

        with pytest.raises(Exception, match="Request failed"):
            _make_api_request_impl("https://api.example.com")

    @patch("openapi_navigator.server.requests.request")
    def test_unexpected_exception(self, mock_request):
        """Test handling of unexpected exceptions."""
        mock_request.side_effect = ValueError("Unexpected error")

        with pytest.raises(Exception, match="Unexpected error"):
            _make_api_request_impl("https://api.example.com")

    @patch("openapi_navigator.server.requests.request")
    def test_case_insensitive_method(self, mock_request):
        """Test that HTTP methods are case insensitive."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com"
        mock_request.return_value = mock_response

        # Test lowercase method
        result = _make_api_request_impl("https://api.example.com", method="post")
        assert result["method"] == "POST"

        mock_request.assert_called_with(
            method="POST", url="https://api.example.com", timeout=30
        )

    @patch("openapi_navigator.server.requests.request")
    @patch("openapi_navigator.server.time.time")
    def test_elapsed_time_calculation(self, mock_time, mock_request):
        """Test that elapsed time is calculated correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com"
        mock_request.return_value = mock_response

        # Mock time.time() to return predictable values
        mock_time.side_effect = [1000.0, 1000.5]  # 500ms elapsed

        result = _make_api_request_impl("https://api.example.com")

        assert result["elapsed_ms"] == 500

    @patch("openapi_navigator.server.requests.request")
    def test_response_headers_conversion(self, mock_request):
        """Test that response headers are properly converted to dict."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com"

        # Mock requests response headers (CaseInsensitiveDict-like behavior)
        mock_headers = {"Content-Type": "text/plain", "X-Custom": "value"}
        mock_response.headers = mock_headers
        mock_request.return_value = mock_response

        result = _make_api_request_impl("https://api.example.com")

        assert isinstance(result["headers"], dict)
        assert result["headers"] == mock_headers

    @patch("openapi_navigator.server.requests.request")
    def test_all_parameters_together(self, mock_request):
        """Test request with all parameters provided."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"success": true}'
        mock_response.url = "https://api.example.com/endpoint?param=value"
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = _make_api_request_impl(
            url="https://api.example.com/endpoint",
            method="PUT",
            headers={"Authorization": "Bearer token"},
            params={"param": "value"},
            data='{"update": "data"}',
            timeout=45,
        )

        assert result["status_code"] == 200
        assert result["method"] == "PUT"
        assert result["json"] == {"success": True}

        mock_request.assert_called_once_with(
            method="PUT",
            url="https://api.example.com/endpoint",
            timeout=45,
            headers={"Authorization": "Bearer token"},
            params={"param": "value"},
            data='{"update": "data"}',
        )
