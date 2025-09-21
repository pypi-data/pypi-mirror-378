"""
Main client for the Rose Python SDK.
"""

import json
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import raise_for_status
from .services import (
    AccountService,
    RoleService,
    DatasetService,
    PipelineService,
    RecommendationService,
)


class RoseClient:
    """
    Main client for interacting with the Rose Recommendation Service API.

    Args:
        base_url: The base URL of the Rose API server
        access_token: The access token for authentication
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
    """

    def __init__(
        self,
        base_url: str,
        access_token: Optional[str] = None,
        root_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.root_token = root_token
        self.timeout = timeout

        # Create session with retry strategy
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        if self.access_token:
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

        # Initialize services
        self.accounts = AccountService(self)
        self.roles = RoleService(self)
        self.datasets = DatasetService(self)
        self.pipelines = PipelineService(self)
        self.recommendations = RecommendationService(self)

    def set_access_token(self, access_token: str) -> None:
        """Set or update the access token."""
        self.access_token = access_token
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def _make_request(  # type: ignore[misc]
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_basic_auth: bool = False,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            headers: Additional headers
            use_basic_auth: If True, use Basic Auth instead of Bearer Auth

        Returns:
            Response data as dictionary

        Raises:
            RoseAPIError: For API errors
        """
        url = f"{self.base_url}{endpoint}"

        request_headers = {}
        if headers:
            request_headers.update(headers)

        # Handle authentication - override session headers
        if use_basic_auth and self.root_token:
            # Use Basic Auth for root operations
            request_headers["Authorization"] = f"Basic {self.root_token}"
        elif not use_basic_auth and self.access_token:
            # Use Bearer Auth for regular operations
            request_headers["Authorization"] = f"Bearer {self.access_token}"

        # Remove any existing Authorization header from session to avoid conflicts
        if "Authorization" in self.session.headers:
            # Create a copy of session headers without Authorization
            session_headers = {k: v for k, v in self.session.headers.items() if k.lower() != "authorization"}
        else:
            session_headers = dict(self.session.headers)

        # Merge session headers with request headers (request headers take precedence)
        final_headers = {**session_headers, **request_headers}

        try:
            # Handle different data types
            if data is None:
                request_data = None
            elif isinstance(data, (str, bytes)):
                request_data = data
            else:
                request_data = json.dumps(data)

            response = self.session.request(
                method=method, url=url, params=params, data=request_data, headers=final_headers, timeout=self.timeout
            )

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"message": response.text}

            # Check for errors (but handle 207 as a special case)
            if not response.ok and response.status_code != 207:
                raise_for_status(response.status_code, response_data)

            # Handle 207 Multi-Status responses
            if response.status_code == 207:
                raise_for_status(response.status_code, response_data)

            return response_data

        except requests.exceptions.Timeout:
            raise_for_status(504, {"message": "Gateway Timeout", "error": "request timed out"})
        except requests.exceptions.ConnectionError:
            raise_for_status(500, {"message": "Internal Server Error", "error": "connection failed"})
        except requests.exceptions.RequestException as e:
            raise_for_status(500, {"message": "Internal Server Error", "error": str(e)})

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, params=params)

    def post_with_basic_auth(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request with Basic Auth."""
        return self._make_request("POST", endpoint, data=data, params=params, headers=headers, use_basic_auth=True)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data)

    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint)

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the service."""
        return self.get("/healthcheck")
