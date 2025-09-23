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

from .responses import (
    AddProfileResponse,
    AddUserResponse,
    BaseResponse,
    CommunitiesListResponse,
    Community,
    DefaultCommunity,
    EventsResponse,
    LoginResponse,
    PermissionsResponse,
    Profile,
    ProfilesListResponse,
    RolesResponse,
    ServicesListResponse,
    UpdateProfileResponse,
    UpdateUserResponse,
    User,
    UsersListResponse,
    VersionResponse,
    WhitelistGroupsResponse,
    WhitelistResponse,
    local_tz,
)


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


class ProfileNotFoundError(Exception):
    """Profile not found."""


class UserNotFoundError(Exception):
    """User not found."""


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
        if self.insecure:
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

    def login(self, login: str, password: str, totp_code: str | None = None) -> LoginResponse:
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

        # Parse into structured response
        login_response = LoginResponse.from_dict(result)

        # Check if TOTP is required
        if login_response.require_totp:
            if not totp_code:
                raise APIError("TOTP code required for authentication")
            return self.login_totp(totp_code)

        # Store token and expiry
        if login_response.token:
            self.token = login_response.token
            if login_response.validity:
                self.token_expiry = datetime.fromtimestamp(login_response.validity / 1000, tz=local_tz)

        return login_response

    def login_totp(self, totp_code: str) -> LoginResponse:
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

        # Parse into structured response
        login_response = LoginResponse.from_dict(result)

        # Store token and expiry
        if login_response.token:
            self.token = login_response.token
            if login_response.validity:
                self.token_expiry = datetime.fromtimestamp(login_response.validity / 1000, tz=local_tz)

        return login_response

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
    ) -> UsersListResponse:
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
        result = self._handle_response(response)
        return UsersListResponse.from_dict(result)

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
    ) -> AddUserResponse:
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
        result = self._handle_response(response)
        return AddUserResponse.from_dict(result)

    def get_user(self, username: str) -> User:
        """
        Get specific user details.

        Args:
            username: User's username

        Returns:
            User details
        """
        response = self._make_request("GET", f"/users/{username}")
        result = self._handle_response(response)
        return User.from_dict(result.get("user", {}))

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
    ) -> UpdateUserResponse:
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
        result = self._handle_response(response)
        return UpdateUserResponse.from_dict(result)

    def delete_user(self, username: str) -> BaseResponse:
        """
        Delete a user.

        Args:
            username: User's username

        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/users/{username}")
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def reset_user_password(self, username: str) -> AddUserResponse:
        """
        Reset user's password.

        Args:
            username: User's username

        Returns:
            New temporary password
        """
        response = self._make_request("POST", f"/users/{username}/password/reset")
        result = self._handle_response(response)
        return AddUserResponse.from_dict(result)

    # Profile Management Endpoints

    def get_profiles(
        self,
        query_filter: str | None = None,
        size: int = 25,
        from_index: int = 0,
        rights: list[str] | None = None,
        roles: list[str] | None = None,
    ) -> ProfilesListResponse:
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
        result = self._handle_response(response)
        return ProfilesListResponse.from_dict(result)

    def add_profile(
        self,
        name: str,
        group: str,
        daily_quota: int = 1000,
        al_ttl: int = 30,
        result_ttl: int = 7,
        services: list[str] | None = None,
        malware_threshold: int = 1000,
        priority: int = 500,
        roles: list[str] | None = None,
        *,
        ignore_cache: bool = False,
        force_dynamic: bool = False,
        disable_cache: bool = False,
    ) -> AddProfileResponse:
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
        result = self._handle_response(response)
        return AddProfileResponse.from_dict(result)

    def get_profile(self, name: str) -> Profile:
        """
        Get specific profile details.

        Args:
            name: Profile name

        Returns:
            Profile details
        """
        response = self._make_request("GET", f"/profiles/{name}")
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ProfileNotFoundError
        result = self._handle_response(response)
        return Profile.from_dict(result["profile"])

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
    ) -> UpdateProfileResponse:
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
        result = self._handle_response(response)
        return UpdateProfileResponse.from_dict(result)

    def delete_profile(self, name: str) -> BaseResponse:
        """
        Delete a profile.

        Args:
            name: Profile name

        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/profiles/{name}")
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    # Configuration Endpoints

    def get_roles_expert(self) -> RolesResponse:
        """
        Get expert roles configuration.

        Returns:
            Expert roles and technical roles
        """
        response = self._make_request("GET", "/config/roles/expert")
        result = self._handle_response(response)
        return RolesResponse.from_dict(result)

    def get_roles_detect(self) -> RolesResponse:
        """
        Get detect roles configuration.

        Returns:
            Detect roles and technical roles
        """
        response = self._make_request("GET", "/config/roles/detect")
        result = self._handle_response(response)
        return RolesResponse.from_dict(result)

    def get_permissions_detect(self) -> PermissionsResponse:
        """
        Get detect permissions configuration.

        Returns:
            Available permissions
        """
        response = self._make_request("GET", "/config/permissions/detect")
        result = self._handle_response(response)
        return PermissionsResponse.from_dict(result)

    def get_permissions_expert(self) -> PermissionsResponse:
        """
        Get expert permissions configuration.

        Returns:
            Available permissions
        """
        response = self._make_request("GET", "/config/permissions/expert")
        result = self._handle_response(response)
        return PermissionsResponse.from_dict(result)

    # Service Management Endpoints

    def get_services(self) -> ServicesListResponse:
        """
        Get available services.

        Returns:
            List of available services
        """
        response = self._make_request("GET", "/services")
        result = self._handle_response(response)
        return ServicesListResponse.from_dict(result)

    def get_service(self, service_name: str) -> BaseResponse:
        """
        Get specific service details.

        Args:
            service_name: Service name

        Returns:
            Service configuration
        """
        response = self._make_request("GET", f"/services/{service_name}")
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    # Version Endpoint

    def get_version(self) -> VersionResponse:
        """
        Get GLIMPS Malware version.

        Returns:
            Version information
        """
        response = self._make_request("GET", "/version")
        result = self._handle_response(response)
        return VersionResponse.from_dict(result)

    # Community Management Endpoints

    def get_communities(
        self,
        from_index: int = 0,
        size: int = 10,
        filter_query: str | None = None,
        sort: str | None = None,
    ) -> CommunitiesListResponse:
        """
        Get list of communities.

        Args:
            from_index: Starting index for pagination
            size: Number of communities to retrieve (max 10000)
            filter_query: Filter communities
            sort: Sort communities

        Returns:
            Communities list with count
        """
        params = {"from": from_index, "size": size}
        if filter_query:
            params["filter"] = filter_query
        if sort:
            params["sort"] = sort

        response = self._make_request("GET", "/communities", params=params)
        result = self._handle_response(response)
        return CommunitiesListResponse.from_dict(result)

    def add_community(
        self,
        name: str,
        group: str,
        domains: list[str],
        *,
        enabled: bool = True,
        registration_template: str = "",
        public_url: str | None = None,
        upload_max_file_size: int = 0,
        forbidden_extensions: list[str] | None = None,
        alert_message: str = "",
        authentication: str = "",
        oidc: dict[str, Any] | None = None,
    ) -> BaseResponse:
        """
        Create new community.

        Args:
            name: Community name
            group: Community group
            domains: Community domains
            enabled: Whether community is enabled
            registration_template: Registration template
            public_url: Public URL
            upload_max_file_size: Maximum file size for uploads
            forbidden_extensions: Forbidden file extensions
            alert_message: Alert message
            authentication: Authentication method
            oidc: OIDC configuration

        Returns:
            Created community details
        """
        data = {
            "name": name,
            "group": group,
            "domains": domains,
            "enabled": enabled,
            "registration_template": registration_template,
            "alert_message": alert_message,
            "authentication": authentication,
            "upload_max_file_size": upload_max_file_size,
        }
        if public_url:
            data["public_url"] = public_url
        if forbidden_extensions:
            data["forbidden_extensions"] = forbidden_extensions
        if oidc:
            data["oidc"] = oidc

        response = self._make_request("POST", "/communities", json_data=data)
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def get_community(self, community_id: str) -> Community:
        """
        Get specific community details.

        Args:
            community_id: Community ID

        Returns:
            Community details
        """
        response = self._make_request("GET", f"/communities/{community_id}")
        result = self._handle_response(response)
        return Community.from_dict(result["community"])

    def update_community(  # noqa: C901
        self,
        community_id: str,
        name: str | None = None,
        group: str | None = None,
        domains: list[str] | None = None,
        *,
        enabled: bool | None = None,
        registration_template: str | None = None,
        public_url: str | None = None,
        upload_max_file_size: int | None = None,
        forbidden_extensions: list[str] | None = None,
        alert_message: str | None = None,
        authentication: str | None = None,
        oidc: dict[str, Any] | None = None,
    ) -> BaseResponse:
        """
        Update community.

        Args:
            community_id: Community ID
            name: Community name
            group: Community group
            domains: Community domains
            enabled: Whether community is enabled
            registration_template: Registration template
            public_url: Public URL
            upload_max_file_size: Maximum file size for uploads
            forbidden_extensions: Forbidden file extensions
            alert_message: Alert message
            authentication: Authentication method
            oidc: OIDC configuration

        Returns:
            Update confirmation
        """
        data = {}
        if name is not None:
            data["name"] = name
        if group is not None:
            data["group"] = group
        if domains is not None:
            data["domains"] = domains
        if enabled is not None:
            data["enabled"] = enabled
        if registration_template is not None:
            data["registration_template"] = registration_template
        if public_url is not None:
            data["public_url"] = public_url
        if upload_max_file_size is not None:
            data["upload_max_file_size"] = upload_max_file_size
        if forbidden_extensions is not None:
            data["forbidden_extensions"] = forbidden_extensions
        if alert_message is not None:
            data["alert_message"] = alert_message
        if authentication is not None:
            data["authentication"] = authentication
        if oidc is not None:
            data["oidc"] = oidc

        response = self._make_request("PUT", f"/communities/{community_id}", json_data=data)
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def delete_community(self, community_id: str) -> BaseResponse:
        """
        Delete community.

        Args:
            community_id: Community ID

        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/communities/{community_id}")
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def get_default_community(self) -> DefaultCommunity:
        """
        Get default community.

        Returns:
            Default community configuration
        """
        response = self._make_request("GET", "/communities/_default")
        result = self._handle_response(response)
        return DefaultCommunity.from_dict(result["default"])

    def update_default_community(
        self,
        name: str,
        alert_message: str,
        registration_template: str,
        forbidden_extensions: list[str] | None = None,
        upload_max_file_size: int = 0,
    ) -> BaseResponse:
        """
        Update default community.

        Args:
            name: Community name
            alert_message: Alert message
            registration_template: Registration template
            forbidden_extensions: Forbidden file extensions
            upload_max_file_size: Maximum file size for uploads

        Returns:
            Update confirmation
        """
        data = {
            "name": name,
            "alert_message": alert_message,
            "registration_template": registration_template,
            "upload_max_file_size": upload_max_file_size,
        }
        if forbidden_extensions:
            data["forbidden_extensions"] = forbidden_extensions

        response = self._make_request("PUT", "/communities/_default", json_data=data)
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    # Whitelist Endpoints

    def get_whitelist(self, groups: str) -> WhitelistResponse:
        """
        Get whitelist entries for groups.

        Args:
            groups: Group name

        Returns:
            Whitelist entries
        """
        params = {"groups": groups}
        response = self._make_request("GET", "/whitelist", params=params)
        result = self._handle_response(response)
        return WhitelistResponse.from_dict(result)

    def update_whitelist(
        self,
        sha256: str,
        groups: list[str],
        comment: str = "",
    ) -> BaseResponse:
        """
        Create or update whitelist entry.

        Args:
            sha256: File SHA256 hash
            groups: Groups to whitelist for
            comment: Comment for the entry

        Returns:
            Update confirmation
        """
        data = {"groups": groups, "comment": comment}
        response = self._make_request("PUT", f"/whitelist/{sha256}", json_data=data)
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def delete_whitelist(self, sha256: str, groups: str) -> BaseResponse:
        """
        Remove entry from whitelist.

        Args:
            sha256: File SHA256 hash
            groups: Group name

        Returns:
            Deletion confirmation
        """
        params = {"groups": groups}
        response = self._make_request("DELETE", f"/whitelist/{sha256}", params=params)
        result = self._handle_response(response)
        return BaseResponse.from_dict(result)

    def get_whitelist_groups(self) -> WhitelistGroupsResponse:
        """
        Get list of whitelist groups.

        Returns:
            List of whitelist groups
        """
        response = self._make_request("GET", "/whitelistgroups")
        result = self._handle_response(response)
        return WhitelistGroupsResponse.from_dict(result)

    # Events Endpoint

    def get_events(
        self,
        filter_query: str | None = None,
        sort: str | None = None,
        from_index: int = 0,
        size: int = 50,
        start: str | None = None,
        end: str | None = None,
    ) -> EventsResponse:
        """
        Get events.

        Args:
            filter_query: Filter events
            sort: Sort events
            from_index: Starting index for pagination
            size: Number of events to retrieve
            start: Start time filter
            end: End time filter

        Returns:
            Events list
        """
        params = {"from": from_index, "size": size}
        if filter_query:
            params["filter"] = filter_query
        if sort:
            params["sort"] = sort
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        response = self._make_request("GET", "/events", params=params)
        result = self._handle_response(response)
        return EventsResponse.from_dict(result)
