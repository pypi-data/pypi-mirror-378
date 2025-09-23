"""
Response models and utilities for GLIMPS Admin API.

This module provides response validation, parsing utilities, and
data models for API responses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


local_tz = datetime.now(tz=timezone.utc).astimezone().tzinfo


@dataclass
class BaseResponse:
    """Base response model for all API responses."""
    status: bool
    error: str | None = None
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseResponse:
        """Create response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
        )

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.status and not self.error


@dataclass
class LoginResponse(BaseResponse):
    """Login response model."""
    token: str | None = None
    validity: int | None = None
    require_totp: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoginResponse:
        """Create login response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
            token=data.get("token"),
            validity=data.get("validity"),
            require_totp=data.get("require_totp", False),
        )

    @property
    def expiry_datetime(self) -> datetime | None:
        """Get token expiry as datetime."""
        if self.validity:
            return datetime.fromtimestamp(self.validity / 1000, tz=local_tz)
        return None


@dataclass
class UserDates:
    """User dates information."""
    creation: int | None = None
    last_modification: int | None = None
    last_login: int | None = None
    scheduled_deactivation: int | None = None
    deactivation: int | None = None
    scheduled_deletion: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> UserDates | None:
        """Create user dates from dictionary."""
        if not data:
            return None
        return cls(
            creation=data.get("creation"),
            last_modification=data.get("last_modification"),
            last_login=data.get("last_login"),
            scheduled_deactivation=data.get("scheduled_deactivation"),
            deactivation=data.get("deactivation"),
            scheduled_deletion=data.get("scheduled_deletion"),
        )


@dataclass
class UserPermissions:
    """User permissions model."""
    use_services: list[str] = field(default_factory=list)
    daily_quota: int = 0
    hourly_quota: int = 0
    monthly_quota: int = 0
    global_access: bool = False
    has_accepted_eula: int = 0
    has_changed_password: int = 0
    # Submission permissions
    submit: bool = False
    submit_url: bool = False
    delete_submission: bool = False
    export_submission: bool = False
    export_function_match: bool = False
    generate_yara_rule: bool = False
    download_file: bool = False
    view_file: bool = False
    list_submissions: bool = False
    view_statistics: bool = False
    view_result: bool = False
    view_errors: bool = False
    view_datasets: bool = False
    generate_view_token: bool = False
    search_results: bool = False
    # Analysis permissions
    capa: bool = False
    safeviewer: bool = False
    # Whitelist permissions
    post_whitelist: bool = False
    delete_whitelist: bool = False
    # Legacy fields for backward compatibility
    ignore_cache: bool = False
    disable_cache: bool = False
    force_dynamic: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> UserPermissions:
        """Create permissions from dictionary."""
        if not data:
            return cls()
        return cls(
            use_services=data.get("use_services", []),
            daily_quota=data.get("daily_quota", 0),
            hourly_quota=data.get("hourly_quota", 0),
            monthly_quota=data.get("monthly_quota", 0),
            global_access=data.get("global_access", False),
            has_accepted_eula=data.get("has_accepted_eula", 0),
            has_changed_password=data.get("has_changed_password", 0),
            submit=data.get("submit", False),
            submit_url=data.get("submit_url", False),
            delete_submission=data.get("delete_submission", False),
            export_submission=data.get("export_submission", False),
            export_function_match=data.get("export_function_match", False),
            generate_yara_rule=data.get("generate_yara_rule", False),
            download_file=data.get("download_file", False),
            view_file=data.get("view_file", False),
            list_submissions=data.get("list_submissions", False),
            view_statistics=data.get("view_statistics", False),
            view_result=data.get("view_result", False),
            view_errors=data.get("view_errors", False),
            view_datasets=data.get("view_datasets", False),
            generate_view_token=data.get("generate_view_token", False),
            search_results=data.get("search_results", False),
            capa=data.get("capa", False),
            safeviewer=data.get("safeviewer", False),
            post_whitelist=data.get("post_whitelist", False),
            delete_whitelist=data.get("delete_whitelist", False),
            ignore_cache=data.get("ignore_cache", False),
            disable_cache=data.get("disable_cache", False),
            force_dynamic=data.get("force_dynamic", False),
        )


@dataclass
class User:
    """User model."""
    username: str
    name: str
    active: bool = True
    types: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    permissions: UserPermissions | None = None
    dates: UserDates | None = None
    roles: list[str] = field(default_factory=list)
    totp_enabled: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create user from dictionary."""
        return cls(
            username=data.get("username", ""),
            name=data.get("name", ""),
            active=data.get("active", True),
            types=data.get("types", []),
            groups=data.get("groups", []),
            tags=data.get("tags", []),
            permissions=UserPermissions.from_dict(data.get("permissions")),
            dates=UserDates.from_dict(data.get("dates")),
            roles=data.get("roles", []),
            totp_enabled=data.get("totp_enabled", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary."""
        result = {
            "username": self.username,
            "name": self.name,
            "active": self.active,
            "types": self.types,
            "groups": self.groups,
            "tags": self.tags,
            "roles": self.roles,
            "totp_enabled": self.totp_enabled,
        }
        if self.permissions:
            result["permissions"] = {
                "use_services": self.permissions.use_services,
                "daily_quota": self.permissions.daily_quota,
                "hourly_quota": self.permissions.hourly_quota,
                "monthly_quota": self.permissions.monthly_quota,
                "global_access": self.permissions.global_access,
                "has_accepted_eula": self.permissions.has_accepted_eula,
                "has_changed_password": self.permissions.has_changed_password,
                "submit": self.permissions.submit,
                "submit_url": self.permissions.submit_url,
                "delete_submission": self.permissions.delete_submission,
                "export_submission": self.permissions.export_submission,
                "export_function_match": self.permissions.export_function_match,
                "generate_yara_rule": self.permissions.generate_yara_rule,
                "download_file": self.permissions.download_file,
                "view_file": self.permissions.view_file,
                "list_submissions": self.permissions.list_submissions,
                "view_statistics": self.permissions.view_statistics,
                "view_result": self.permissions.view_result,
                "view_errors": self.permissions.view_errors,
                "view_datasets": self.permissions.view_datasets,
                "generate_view_token": self.permissions.generate_view_token,
                "search_results": self.permissions.search_results,
                "capa": self.permissions.capa,
                "safeviewer": self.permissions.safeviewer,
                "post_whitelist": self.permissions.post_whitelist,
                "delete_whitelist": self.permissions.delete_whitelist,
                "ignore_cache": self.permissions.ignore_cache,
                "disable_cache": self.permissions.disable_cache,
                "force_dynamic": self.permissions.force_dynamic,
            }
        return result


@dataclass
class UsersListResponse(BaseResponse):
    """Users list response model."""
    count: int = 0
    users: list[User] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsersListResponse:
        """Create users list response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            count=data.get("count", 0),
            users=[User.from_dict(u) for u in data.get("users", [])],
        )


@dataclass
class Profile:
    """Profile model."""
    name: str
    group: str
    token: str | None = None
    al_login: str | None = None
    daily_quota: int = 0
    ignore_cache: bool = False
    al_ttl: int = 0
    result_ttl: int = 365
    services: list[str] = field(default_factory=list)
    force_dynamic: bool = False
    malware_threshold: int = 100
    priority: int = 0
    disable_cache: bool = False
    dates: UserDates | None = None
    roles: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Profile:
        """Create profile from dictionary."""
        return cls(
            name=data.get("name", ""),
            group=data.get("group", ""),
            token=data.get("token"),
            al_login=data.get("al_login"),
            daily_quota=data.get("daily_quota", 0),
            ignore_cache=data.get("ignore_cache", False),
            al_ttl=data.get("al_ttl", 0),
            result_ttl=data.get("result_ttl", 365),
            services=data.get("services", []),
            force_dynamic=data.get("force_dynamic", False),
            malware_threshold=data.get("malware_threshold", 100),
            priority=data.get("priority", 0),
            disable_cache=data.get("disable_cache", False),
            dates=UserDates.from_dict(data.get("dates")),
            roles=data.get("roles", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "name": self.name,
            "group": self.group,
            "daily_quota": self.daily_quota,
            "ignore_cache": self.ignore_cache,
            "al_ttl": self.al_ttl,
            "result_ttl": self.result_ttl,
            "services": self.services,
            "force_dynamic": self.force_dynamic,
            "malware_threshold": self.malware_threshold,
            "priority": self.priority,
            "disable_cache": self.disable_cache,
            "roles": self.roles,
        }


@dataclass
class ProfilesListResponse(BaseResponse):
    """Profiles list response model."""
    count: int = 0
    profiles: list[Profile] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfilesListResponse:
        """Create profiles list response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            count=data.get("count", 0),
            profiles=[Profile.from_dict(p) for p in data.get("profiles", [])],
        )


@dataclass
class Service:
    """Service model."""
    name: str
    version: str = ""
    enabled: bool = True
    category: str = ""
    stage: str = ""
    description: str = ""
    accept: str = ".*"
    rejects: str = ""
    classpath: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Service:
        """Create service from dictionary."""
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            enabled=data.get("enabled", True),
            category=data.get("category", ""),
            stage=data.get("stage", ""),
            description=data.get("description", ""),
            accept=data.get("accept", ".*"),
            rejects=data.get("rejects", ""),
            classpath=data.get("classpath", ""),
        )


@dataclass
class ServicesListResponse(BaseResponse):
    """Services list response model."""
    services: list[Service] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServicesListResponse:
        """Create services list response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            services=[Service.from_dict(s) for s in data.get("services", [])],
        )


@dataclass
class Role:
    """Role model."""
    id: str
    label: str
    description: str = ""
    is_technical: bool = False
    is_default: bool = False
    requires_global_access: bool = False
    permissions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Role:
        """Create role from dictionary."""
        return cls(
            id=data.get("id", ""),
            label=data.get("label", ""),
            description=data.get("description", ""),
            is_technical=data.get("is_technical", False),
            is_default=data.get("is_default", data.get("default_value", False)),
            requires_global_access=data.get("requires_global_access", False),
            permissions=data.get("permissions", []),
        )


@dataclass
class RolesResponse(BaseResponse):
    """Roles response model."""
    roles: list[Role] = field(default_factory=list)
    technical_roles: list[Role] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RolesResponse:
        """Create roles response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            roles=[Role.from_dict(r) for r in data.get("roles", [])],
            technical_roles=[Role.from_dict(r) for r in data.get("technical_roles", [])],
        )


@dataclass
class Permission:
    """Permission model."""
    id: str
    label: str
    description: str = ""
    require_global_access: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Permission:
        """Create permission from dictionary."""
        return cls(
            id=data.get("id", ""),
            label=data.get("label", ""),
            description=data.get("description", ""),
            require_global_access=data.get("require_global_access", False),
        )


@dataclass
class PermissionsResponse(BaseResponse):
    """Permissions response model."""
    permissions: dict[str, Permission] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PermissionsResponse:
        """Create permissions response from dictionary."""
        perms = {}
        for key, value in data.get("permissions", {}).items():
            if isinstance(value, dict):
                perms[key] = Permission.from_dict(value)
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            permissions=perms,
        )


@dataclass
class AddUserResponse(BaseResponse):
    """Add user response model."""
    message: str | None = None
    password: str | None = None
    login: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AddUserResponse:
        """Create add user response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
            password=data.get("password"),
            login=data.get("login"),
        )


@dataclass
class UpdateUserResponse(BaseResponse):
    """Update user response model."""
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UpdateUserResponse:
        """Create update user response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
        )


@dataclass
class AddProfileResponse(BaseResponse):
    """Add profile response model."""
    message: str | None = None
    token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AddProfileResponse:
        """Create add profile response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
            token=data.get("token"),
        )


@dataclass
class UpdateProfileResponse(BaseResponse):
    """Update profile response model."""
    message: str | None = None
    token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UpdateProfileResponse:
        """Create update profile response from dictionary."""
        return cls(
            status=data.get("status", False),
            error=data.get("error"),
            message=data.get("message"),
            token=data.get("token"),
        )


@dataclass
class VersionResponse:
    """Version response model."""
    version: str

    @classmethod
    def from_dict(cls, data: str | dict[str, Any]) -> VersionResponse:
        """Create version response from string or dictionary."""
        if isinstance(data, str):
            return cls(version=data)
        return cls(version=data.get("version", ""))


@dataclass
class CommunityEntry:
    """Community entry model."""
    id: str
    group: str
    name: str
    domains: list[str] = field(default_factory=list)
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommunityEntry:
        """Create community entry from dictionary."""
        return cls(
            id=data.get("id", ""),
            group=data.get("group", ""),
            name=data.get("name", ""),
            domains=data.get("domains", []),
            enabled=data.get("enabled", True),
        )


@dataclass
class Community(CommunityEntry):
    """Community model."""
    registration_template: str = ""
    public_url: str | None = None
    token: str | None = None
    dynamic_token: str | None = None
    upload_max_file_size: int = 0
    forbidden_extensions: list[str] = field(default_factory=list)
    alert_message: str = ""
    authentication: str = ""
    oidc: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Community:
        """Create community from dictionary."""
        return cls(
            id=data.get("id", ""),
            group=data.get("group", ""),
            name=data.get("name", ""),
            domains=data.get("domains", []),
            enabled=data.get("enabled", True),
            registration_template=data.get("registration_template", ""),
            public_url=data.get("public_url"),
            token=data.get("token"),
            dynamic_token=data.get("dynamic_token"),
            upload_max_file_size=data.get("upload_max_file_size", 0),
            forbidden_extensions=data.get("forbidden_extensions", []),
            alert_message=data.get("alert_message", ""),
            authentication=data.get("authentication", ""),
            oidc=data.get("oidc"),
        )


@dataclass
class DefaultCommunity:
    """Default community model."""
    name: str
    alert_message: str = ""
    forbidden_extensions: list[str] = field(default_factory=list)
    registration_template: str = ""
    upload_max_file_size: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DefaultCommunity:
        """Create default community from dictionary."""
        return cls(
            name=data.get("name", ""),
            alert_message=data.get("alert_message", ""),
            forbidden_extensions=data.get("forbidden_extensions", []),
            registration_template=data.get("registration_template", ""),
            upload_max_file_size=data.get("upload_max_file_size", 0),
        )


@dataclass
class CommunitiesListResponse(BaseResponse):
    """Communities list response model."""
    count: int = 0
    communities: list[CommunityEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommunitiesListResponse:
        """Create communities list response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            count=data.get("count", 0),
            communities=[CommunityEntry.from_dict(c) for c in data.get("communities", [])],
        )


@dataclass
class WhitelistEntry:
    """Whitelist entry model."""
    sha256: str
    comment: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WhitelistEntry:
        """Create whitelist entry from dictionary."""
        return cls(
            sha256=data.get("sha256", ""),
            comment=data.get("comment", ""),
        )


@dataclass
class WhitelistGroup:
    """Whitelist group model."""
    name: str
    list: list[WhitelistEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WhitelistGroup:
        """Create whitelist group from dictionary."""
        return cls(
            name=data.get("name", ""),
            list=[WhitelistEntry.from_dict(e) for e in data.get("list", [])],
        )


@dataclass
class WhitelistResponse(BaseResponse):
    """Whitelist response model."""
    groups: list[WhitelistGroup] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WhitelistResponse:
        """Create whitelist response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            groups=[WhitelistGroup.from_dict(g) for g in data.get("groups", [])],
        )


@dataclass
class WhitelistGroupsResponse(BaseResponse):
    """Whitelist groups response model."""
    groups: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WhitelistGroupsResponse:
        """Create whitelist groups response from dictionary."""
        return cls(
            status=data.get("status", True),
            error=data.get("error"),
            groups=data.get("groups", []),
        )


@dataclass
class EventUser:
    """Event user model."""
    name: str
    groups: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_admin: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EventUser:
        """Create event user from dictionary."""
        return cls(
            name=data.get("name", ""),
            groups=data.get("groups", []),
            tags=data.get("tags", []),
            is_admin=data.get("is_admin", False),
        )


@dataclass
class EventEntry:
    """Event entry model."""
    user: EventUser
    kind: str
    event: str
    details: list[str] = field(default_factory=list)
    level: str = "Info"
    timestamp: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EventEntry:
        """Create event entry from dictionary."""
        return cls(
            user=EventUser.from_dict(data.get("user", {})),
            kind=data.get("kind", ""),
            event=data.get("event", ""),
            details=data.get("details", []),
            level=data.get("level", "Info"),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class EventsResponse:
    """Events response model."""
    total: int = 0
    events: list[EventEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EventsResponse:
        """Create events response from dictionary."""
        return cls(
            total=data.get("total", 0),
            events=[EventEntry.from_dict(e) for e in data.get("events", [])],
        )


class ResponseParser:
    """Utility class for parsing API responses."""

    @staticmethod
    def parse_response(response_data: dict | list | str, response_type: str = "base") -> Any:
        """
        Parse API response based on type.

        Args:
            response_data: Raw response data
            response_type: Type of response to parse

        Returns:
            Parsed response object
        """
        if not isinstance(response_data, dict):
            return response_data

        parsers = {
            "base": BaseResponse,
            "login": LoginResponse,
            "users_list": UsersListResponse,
            "user": User,
            "add_user": AddUserResponse,
            "update_user": UpdateUserResponse,
            "profiles_list": ProfilesListResponse,
            "profile": Profile,
            "add_profile": AddProfileResponse,
            "update_profile": UpdateProfileResponse,
            "services_list": ServicesListResponse,
            "service": Service,
            "roles": RolesResponse,
            "permissions": PermissionsResponse,
            "version": VersionResponse,
            "communities_list": CommunitiesListResponse,
            "community": Community,
            "default_community": DefaultCommunity,
            "whitelist": WhitelistResponse,
            "whitelist_groups": WhitelistGroupsResponse,
            "events": EventsResponse,
        }

        parser_class = parsers.get(response_type, BaseResponse)

        try:
            return parser_class.from_dict(response_data)
        except AttributeError as e:
            # If parsing fails, return raw data
            print(f"Warning: Failed to parse response as {response_type}: {e}")
            return response_data

    @staticmethod
    def validate_response(response_data: dict[str, Any]) -> bool:
        """
        Validate if response is successful.

        Args:
            response_data: Response dictionary

        Returns:
            bool: True if response is successful
        """
        if not isinstance(response_data, dict):
            return False

        # Check for explicit error
        if response_data.get("error"):
            return False

        # Check status field if present
        if "status" in response_data:
            return response_data["status"] is True

        # If no status field, assume success if no error
        return True

    @staticmethod
    def extract_error(response_data: dict | str) -> str:
        """
        Extract error message from response.

        Args:
            response_data: Response data

        Returns:
            str: Error message or empty string
        """
        if isinstance(response_data, str):
            return response_data

        if isinstance(response_data, dict):
            # Try different error field names
            error = response_data.get("error", "")
            if not error:
                error = response_data.get("message", "")
            if not error:
                error = response_data.get("detail", "")
            if not error and response_data.get("details"):
                # Handle detailed errors
                details = response_data["details"]
                if isinstance(details, list) and details:
                    errors = []
                    for detail in details:
                        if isinstance(detail, dict):
                            for key, value in detail.items():
                                errors.append(f"{key}: {value}")
                    error = "; ".join(errors)
            return str(error)

        return ""


# Response validation functions

def validate_login_response(data: dict[str, Any]) -> bool:
    """
    Validate login response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid login response
    """
    required_fields = ["status"]
    success_fields = ["token", "validity"]

    if not all(field in data for field in required_fields):
        return False

    if data.get("status") and not data.get("require_totp"):
        # Successful login should have token and validity
        return all(field in data for field in success_fields)

    return True


def validate_user_response(data: dict[str, Any]) -> bool:
    """
    Validate user response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid user response
    """
    required_fields = ["username", "name"]
    return all(field in data for field in required_fields)


def validate_profile_response(data: dict[str, Any]) -> bool:
    """
    Validate profile response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid profile response
    """
    required_fields = ["name", "group"]
    return all(field in data for field in required_fields)


def validate_community_response(data: dict[str, Any]) -> bool:
    """
    Validate community response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid community response
    """
    required_fields = ["id", "name", "group", "domains"]
    return all(field in data for field in required_fields)


def validate_whitelist_response(data: dict[str, Any]) -> bool:
    """
    Validate whitelist response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid whitelist response
    """
    if not isinstance(data, dict):
        return False

    if "groups" not in data:
        return False

    groups = data["groups"]
    if not isinstance(groups, list):
        return False

    for group in groups:
        if not isinstance(group, dict):
            return False
        if "name" not in group or "list" not in group:
            return False

    return True


def validate_events_response(data: dict[str, Any]) -> bool:
    """
    Validate events response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid events response
    """
    required_fields = ["total", "events"]
    if not all(field in data for field in required_fields):
        return False

    events = data["events"]
    if not isinstance(events, list):
        return False

    for event in events:
        if not isinstance(event, dict):
            return False
        event_required = ["user", "kind", "event"]
        if not all(field in event for field in event_required):
            return False

    return True


def validate_roles_response(data: dict[str, Any]) -> bool:
    """
    Validate roles response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid roles response
    """
    if not isinstance(data, dict):
        return False

    # Check for required fields
    if "roles" not in data or "technical_roles" not in data:
        return False

    # Validate roles structure
    for role_list in [data["roles"], data["technical_roles"]]:
        if not isinstance(role_list, list):
            return False
        for role in role_list:
            if not isinstance(role, dict):
                return False
            role_required = ["id", "label", "description"]
            if not all(field in role for field in role_required):
                return False

    return True


def validate_permissions_response(data: dict[str, Any]) -> bool:
    """
    Validate permissions response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid permissions response
    """
    if not isinstance(data, dict):
        return False

    if "permissions" not in data:
        return False

    permissions = data["permissions"]
    if not isinstance(permissions, dict):
        return False

    for _perm_id, perm in permissions.items():
        if not isinstance(perm, dict):
            return False
        perm_required = ["id", "label", "description"]
        if not all(field in perm for field in perm_required):
            return False

    return True


def validate_services_response(data: dict[str, Any]) -> bool:
    """
    Validate services response structure.

    Args:
        data: Response data

    Returns:
        bool: True if valid services response
    """
    if not isinstance(data, dict):
        return False

    if "services" not in data:
        return False

    services = data["services"]
    if not isinstance(services, list):
        return False

    for service in services:
        if not isinstance(service, dict):
            return False
        service_required = ["name", "enabled"]
        if not all(field in service for field in service_required):
            return False

    return True


class ResponseValidator:
    """Advanced response validation class with schema checking."""

    @staticmethod
    def validate_response_structure(data: dict[str, Any], response_type: str) -> tuple[bool, str]:
        """
        Validate response structure against expected schema.

        Args:
            data: Response data
            response_type: Type of response to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        validators = {
            "login": validate_login_response,
            "user": validate_user_response,
            "profile": validate_profile_response,
            "community": validate_community_response,
            "whitelist": validate_whitelist_response,
            "events": validate_events_response,
            "roles": validate_roles_response,
            "permissions": validate_permissions_response,
            "services": validate_services_response,
        }

        validator = validators.get(response_type)
        if not validator:
            return True, ""  # No specific validator, assume valid

        try:
            if validator(data):
                return True, ""
            return False, f"Response structure validation failed for {response_type}"  # noqa: TRY300
        except Exception as e:
            return False, f"Validation error for {response_type}: {e}"

    @staticmethod
    def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> tuple[bool, str]:
        """
        Validate that all required fields are present.

        Args:
            data: Response data
            required_fields: List of required field names

        Returns:
            tuple: (is_valid, error_message)
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        return True, ""

    @staticmethod
    def validate_field_types(data: dict[str, Any], field_types: dict[str, type]) -> tuple[bool, str]:
        """
        Validate field types in response data.

        Args:
            data: Response data
            field_types: Dictionary mapping field names to expected types

        Returns:
            tuple: (is_valid, error_message)
        """
        for field_name, expected_type in field_types.items():
            if field_name in data:
                actual_value = data[field_name]
                if not isinstance(actual_value, expected_type):
                    return (
                        False,
                        f"Field '{field_name}' expected type {expected_type.__name__}, "
                        f"got {type(actual_value).__name__}",
                    )
        return True, ""

    @staticmethod
    def validate_openapi_compliance(data: dict[str, Any], response_type: str) -> tuple[bool, list[str]]:
        """
        Validate response compliance with OpenAPI specification.

        Args:
            data: Response data
            response_type: Type of response

        Returns:
            tuple: (is_valid, list_of_issues)
        """
        issues = []

        # Define OpenAPI schema requirements for each response type
        openapi_schemas = {
            "login": {
                "required": ["status"],
                "types": {"status": bool, "token": str, "validity": int},
            },
            "user": {
                "required": ["username", "name"],
                "types": {"username": str, "name": str, "active": bool},
            },
            "profile": {
                "required": ["name", "group"],
                "types": {"name": str, "group": str, "daily_quota": int},
            },
            "users_list": {
                "required": ["status", "count", "users"],
                "types": {"status": bool, "count": int, "users": list},
            },
            "profiles_list": {
                "required": ["status", "count", "profiles"],
                "types": {"status": bool, "count": int, "profiles": list},
            },
        }

        schema = openapi_schemas.get(response_type)
        if not schema:
            return True, []  # No schema defined, assume valid

        # Check required fields
        is_valid, error = ResponseValidator.validate_required_fields(data, schema.get("required", []))
        if not is_valid:
            issues.append(error)

        # Check field types
        is_valid, error = ResponseValidator.validate_field_types(data, schema.get("types", {}))
        if not is_valid:
            issues.append(error)

        return len(issues) == 0, issues


# Export all public classes and functions
__all__ = [
    "AddProfileResponse",
    "AddUserResponse",
    "BaseResponse",
    "CommunitiesListResponse",
    "Community",
    "CommunityEntry",
    "DefaultCommunity",
    "EventEntry",
    "EventUser",
    "EventsResponse",
    "LoginResponse",
    "Permission",
    "PermissionsResponse",
    "Profile",
    "ProfilesListResponse",
    "ResponseParser",
    "ResponseValidator",
    "Role",
    "RolesResponse",
    "Service",
    "ServicesListResponse",
    "UpdateProfileResponse",
    "UpdateUserResponse",
    "User",
    "UserDates",
    "UserPermissions",
    "UsersListResponse",
    "VersionResponse",
    "WhitelistEntry",
    "WhitelistGroup",
    "WhitelistGroupsResponse",
    "WhitelistResponse",
    "validate_community_response",
    "validate_events_response",
    "validate_login_response",
    "validate_permissions_response",
    "validate_profile_response",
    "validate_roles_response",
    "validate_services_response",
    "validate_user_response",
    "validate_whitelist_response",
]
