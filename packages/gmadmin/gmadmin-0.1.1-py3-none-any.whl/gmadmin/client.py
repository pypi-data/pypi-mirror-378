"""
GLIMPS Malware Admin API Client.

A Python client for interacting with the GLIMPS Admin API v1.1.0
"""

import json
from datetime import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import urljoin

import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .responses import local_tz


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, message:str, status_code:int | None=None, response: Any | None=None) -> None:
        """
        Initialize Error exception.

        Args:
            message: message string
            status_code: http status
            response: http request response
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class GlimpsAdminClient:
    """Client for GLIMPS Admin API."""

    def __init__(self, url: str = "https://gmalware.glimps.re", *, insecure: bool = False) -> None:
        """
        Initialize GLIMPS Admin API client.

        Args:
            url: Base URL for the API (without /api/v1)
            insecure: Whether to verify SSL certificates
        """
        self.base_url = url
        if not self.base_url.endswith("/api/v1/"):
            self.base_url = f"{self.base_url}/api/v1/"

        self.insecure = insecure
        self.token = None
        self.token_expiry = None
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Disable SSL warnings if verify_ssl is False
        if not self.insecure:

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        json_data: dict | None = None,
        files: dict | None = None,
        params: dict | None = None,
        *,
        stream: bool = False,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL)
            data: Form data to send
            json_data: JSON data to send
            files: Files to upload
            params: Query parameters
            stream: Whether to stream the response

        Returns:
            Response object

        Raises:
            APIError: If the request fails
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        headers = {}
        if self.token:
            headers["X-Authorization"] = f"Bearer {self.token}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                json=json_data,
                files=files,
                params=params,
                headers=headers,
                verify=not self.insecure,
                stream=stream,
            )

            # Check for errors
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise APIError("Unauthorized", status_code=HTTPStatus.UNAUTHORIZED, response=response)
            if response.status_code == HTTPStatus.FORBIDDEN:
                raise APIError("Forbidden", status_code=HTTPStatus.FORBIDDEN, response=response)
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                error_msg = f"API Error {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = f"{error_msg}: {error_data['error']}"
                    if "details" in error_data:
                        error_msg = f"{error_msg}\ndetails: {error_data['details']}"
                except requests.exceptions.JSONDecodeError:
                    error_msg = f"{error_msg}: {response.text}"
                raise APIError(error_msg, status_code=response.status_code, response=response)
            return response # noqa

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e!s}") from e

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and return parsed data."""
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    # Authentication Endpoints

    def login(self, login: str, password: str, totp_code: str | None = None) -> dict[str, Any]:
        """
        Login to the API.

        Args:
            login: Admin username
            password: Admin password
            totp_code: Optional TOTP code for 2FA

        Returns:
            Login response with token and validity
        """
        data = {"login": login, "password": password}
        response = self._make_request("POST", "/login", json_data=data)
        result = self._handle_response(response)

        # Check if TOTP is required
        if result.get("require_totp"):
            if not totp_code:
                raise APIError("TOTP code required for authentication")
            return self.login_totp(totp_code)

        # Store token and expiry
        if "token" in result:
            self.token = result["token"]
            if "validity" in result:
                self.token_expiry = datetime.fromtimestamp(result["validity"] / 1000, tz=local_tz)

        return result

    def login_totp(self, totp_code: str) -> dict[str, Any]:
        """
        Complete login with TOTP code.

        Args:
            totp_code: TOTP authentication code

        Returns:
            Login response with final token
        """
        data = {"totp": totp_code}
        response = self._make_request("POST", "/login_totp", json_data=data)
        result = self._handle_response(response)

        # Store token and expiry
        if "token" in result:
            self.token = result["token"]
            if "validity" in result:
                self.token_expiry = datetime.fromtimestamp(result["validity"] / 1000, tz=local_tz)

        return result

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self.token or not self.token_expiry:
            return False
        return datetime.now(tz=local_tz) < self.token_expiry

    def ensure_authenticated(self) -> None:
        """Ensure the client is authenticated."""
        if not self.is_token_valid():
            raise APIError("Not authenticated. Please login first.")

    # User Management Endpoints

    def get_users(
        self,
        query_filter: str | None = None,
        size: int = 25,
        from_index: int = 0,
        types: list[str] | None = None,
        groups: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get list of users.

        Args:
            query_filter: Filter users by name/username
            size: Number of users to retrieve (max 1000)
            from_index: Starting index for pagination
            types: Filter by user types (user, admin)
            groups: Filter by groups
            tags: Filter by tags

        Returns:
            Users list with count and user details
        """
        params = {"size": size, "from": from_index}
        if query_filter:
            params["filter"] = query_filter
        if types:
            params["types"] = types
        if groups:
            params["groups"] = groups
        if tags:
            params["tags"] = tags

        response = self._make_request("GET", "/users", params=params)
        return self._handle_response(response)

    def add_user(
        self,
        name: str,
        username: str,
        groups: list[str],
        types: list[str] | None = None,
        tags: list[str] | None = None,
        permissions: dict[str, Any] | None = None,
        roles: list[str] | None = None,
        *,
        active: bool = True,
    ) -> dict[str, Any]:
        """
        Add a new user.

        Args:
            name: User display name
            username: User login (email)
            groups: User groups (minimum 1)
            active: Whether account is active
            types: User types (user, admin, etc.)
            tags: User tags
            permissions: User permissions
            roles: User roles

        Returns:
            Created user details
        """
        data = {
            "name": name,
            "username": username,
            "groups": groups,
            "active": active,
        }
        if types:
            data["types"] = types
        if tags:
            data["tags"] = tags
        if permissions:
            data["permissions"] = permissions
        if roles:
            data["roles"] = roles

        response = self._make_request("POST", "/users", json_data=data)
        return self._handle_response(response)

    def get_user(self, username: str) -> dict[str, Any]:
        """
        Get specific user details.

        Args:
            username: User's username

        Returns:
            User details
        """
        response = self._make_request("GET", f"/users/{username}")
        return self._handle_response(response)

    def update_user(
        self,
        username: str,
        types: list[str] | None = None,
        groups: list[str] | None = None,
        tags: list[str] | None = None,
        permissions: dict[str, Any] | None = None,
        roles: list[str] | None = None,
        *,
        active: bool | None = None,
        totp_enabled: bool | None = None,
    ) -> dict[str, Any]:
        """
        Update user details.

        Args:
            username: User's username
            active: Whether account is active
            types: User types
            groups: User groups
            tags: User tags
            permissions: User permissions
            roles: User roles
            totp_enabled: Whether TOTP is enabled

        Returns:
            Updated user details
        """
        data = {}
        if active is not None:
            data["active"] = active
        if types:
            data["types"] = types
        if groups:
            data["groups"] = groups
        if tags:
            data["tags"] = tags
        if permissions:
            data["permissions"] = permissions
        if roles:
            data["roles"] = roles
        if totp_enabled is not None:
            data["totp_enabled"] = totp_enabled

        response = self._make_request("PUT", f"/users/{username}", json_data=data)
        return self._handle_response(response)

    def delete_user(self, username: str) -> dict[str, Any]:
        """
        Delete a user.

        Args:
            username: User's username

        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/users/{username}")
        return self._handle_response(response)

    def reset_user_password(self, username: str) -> dict[str, Any]:
        """
        Reset user's password.

        Args:
            username: User's username

        Returns:
            New temporary password
        """
        response = self._make_request("POST", f"/users/{username}/password/reset")
        return self._handle_response(response)

    # Profile Management Endpoints

    def get_profiles(
        self,
        query_filter: str | None = None,
        size: int = 25,
        from_index: int = 0,
        rights: list[str] | None = None,
        roles: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get list of profiles.

        Args:
            query_filter: Filter profiles by name
            size: Number of profiles to retrieve (max 1000)
            from_index: Starting index for pagination
            rights: Filter by rights
            roles: Filter by role IDs

        Returns:
            Profiles list with count
        """
        params = {"size": size, "from": from_index}
        if query_filter:
            params["filter"] = query_filter
        if rights:
            params["rights"] = rights
        if roles:
            params["roles"] = roles

        response = self._make_request("GET", "/profiles", params=params)
        return self._handle_response(response)

    def add_profile(
        self,
        name: str,
        group: str,
        daily_quota: int = 0,
        al_ttl: int = 0,
        result_ttl: int = 365,
        services: list[str] | None = None,
        malware_threshold: int = 100,
        priority: int = 0,
        roles: list[str] | None = None,
        *,
        ignore_cache: bool = False,
        force_dynamic: bool = False,
        disable_cache: bool = False,
    ) -> dict[str, Any]:
        """
        Add a new profile.

        Args:
            name: Profile name
            group: Profile group
            daily_quota: Daily submission quota (0 = unlimited)
            ignore_cache: Ignore cache
            al_ttl: Analysis TTL
            result_ttl: Result TTL in days
            services: Allowed services
            force_dynamic: Force dynamic analysis
            malware_threshold: Malware detection threshold
            priority: Submission priority
            disable_cache: Disable cache
            roles: Profile roles

        Returns:
            Created profile details
        """
        data = {
            "name": name,
            "group": group,
            "daily_quota": daily_quota,
            "ignore_cache": ignore_cache,
            "al_ttl": al_ttl,
            "result_ttl": result_ttl,
            "force_dynamic": force_dynamic,
            "malware_threshold": malware_threshold,
            "priority": priority,
            "disable_cache": disable_cache,
        }
        if services:
            data["services"] = services
        if roles:
            data["roles"] = roles

        response = self._make_request("POST", "/profiles", json_data=data)
        return self._handle_response(response)

    def get_profile(self, name: str) -> dict[str, Any]:
        """
        Get specific profile details.

        Args:
            name: Profile name

        Returns:
            Profile details
        """
        response = self._make_request("GET", f"/profiles/{name}")
        return self._handle_response(response)

    def update_profile(
        self,
        name: str,
        group: str | None = None,
        daily_quota: int | None = None,
        al_ttl: int | None = None,
        result_ttl: int | None = None,
        services: list[str] | None = None,
        malware_threshold: int | None = None,
        priority: int | None = None,
        roles: list[str] | None = None,
        *,
        ignore_cache: bool | None = None,
        force_dynamic: bool | None = None,
        disable_cache: bool | None = None,
    ) -> dict[str, Any]:
        """
        Update profile details.

        Args:
            name: Profile name
            group: Profile group
            daily_quota: Daily submission quota
            ignore_cache: Ignore cache
            al_ttl: Analysis TTL
            result_ttl: Result TTL
            services: Allowed services
            force_dynamic: Force dynamic analysis
            malware_threshold: Malware threshold
            priority: Priority
            disable_cache: Disable cache
            roles: Profile roles

        Returns:
            Updated profile details
        """
        # Get all local variables except 'self' and 'name'
        params = locals()
        params.pop("self")
        params.pop("name")

        # Build data dict with non-None values
        data = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("PUT", f"/profiles/{name}", json_data=data)
        return self._handle_response(response)

    def delete_profile(self, name: str) -> dict[str, Any]:
        """
        Delete a profile.

        Args:
            name: Profile name

        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/profiles/{name}")
        return self._handle_response(response)

    # Configuration Endpoints

    def get_roles_expert(self) -> dict[str, Any]:
        """
        Get expert roles configuration.

        Returns:
            Expert roles and technical roles
        """
        response = self._make_request("GET", "/config/roles/expert")
        return self._handle_response(response)

    def get_roles_detect(self) -> dict[str, Any]:
        """
        Get detect roles configuration.

        Returns:
            Detect roles and technical roles
        """
        response = self._make_request("GET", "/config/roles/detect")
        return self._handle_response(response)

    def get_permissions_detect(self) -> dict[str, Any]:
        """
        Get detect permissions configuration.

        Returns:
            Available permissions
        """
        response = self._make_request("GET", "/config/permissions/detect")
        return self._handle_response(response)

    def get_permissions_expert(self) -> dict[str, Any]:
        """
        Get expert permissions configuration.

        Returns:
            Available permissions
        """
        response = self._make_request("GET", "/config/permissions/expert")
        return self._handle_response(response)

    # Service Management Endpoints

    def get_services(self) -> dict[str, Any]:
        """
        Get available services.

        Returns:
            List of available services
        """
        response = self._make_request("GET", "/services")
        return self._handle_response(response)

    def get_service(self, service_name: str) -> dict[str, Any]:
        """
        Get specific service details.

        Args:
            service_name: Service name

        Returns:
            Service configuration
        """
        response = self._make_request("GET", f"/services/{service_name}")
        return self._handle_response(response)

    def update_service(self, service_name: str, *, enabled: bool) -> dict[str, Any]:
        """
        Enable or disable a service.

        Args:
            service_name: Service name
            enabled: Whether to enable the service

        Returns:
            Updated service status
        """
        data = {"enabled": enabled}
        response = self._make_request("PUT", f"/services/{service_name}", json_data=data)
        return self._handle_response(response)
