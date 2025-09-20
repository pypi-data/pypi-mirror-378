"""
Response models and utilities for GLIMPS Admin API.

This module provides response validation, parsing utilities, and
data models for API responses.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


local_tz = datetime.now(tz=timezone.utc).astimezone().tzinfo


@dataclass
class BaseResponse:
    """Base response model for all API responses."""
    status: bool
    error: str | None = None
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseResponse":
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
    def from_dict(cls, data: dict[str, Any]) -> "LoginResponse":
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
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["UserDates"]:
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
    ignore_cache: bool = False
    disable_cache: bool = False
    force_dynamic: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "UserPermissions":
        """Create permissions from dictionary."""
        if not data:
            return cls()
        return cls(
            use_services=data.get("use_services", []),
            daily_quota=data.get("daily_quota", 0),
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
    def from_dict(cls, data: dict[str, Any]) -> "User":
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
    def from_dict(cls, data: dict[str, Any]) -> "UsersListResponse":
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
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
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
    def from_dict(cls, data: dict[str, Any]) -> "ProfilesListResponse":
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
    def from_dict(cls, data: dict[str, Any]) -> "Service":
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
    def from_dict(cls, data: dict[str, Any]) -> "ServicesListResponse":
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
    def from_dict(cls, data: dict[str, Any]) -> "Role":
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
    def from_dict(cls, data: dict[str, Any]) -> "RolesResponse":
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
    def from_dict(cls, data: dict[str, Any]) -> "Permission":
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
    def from_dict(cls, data: dict[str, Any]) -> "PermissionsResponse":
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
            "profiles_list": ProfilesListResponse,
            "profile": Profile,
            "services_list": ServicesListResponse,
            "service": Service,
            "roles": RolesResponse,
            "permissions": PermissionsResponse,
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


# Export all public classes and functions
__all__ = [
    "BaseResponse",
    "LoginResponse",
    "Permission",
    "PermissionsResponse",
    "Profile",
    "ProfilesListResponse",
    "ResponseParser",
    "Role",
    "RolesResponse",
    "Service",
    "ServicesListResponse",
    "User",
    "UserDates",
    "UserPermissions",
    "UsersListResponse",
    "validate_login_response",
    "validate_profile_response",
    "validate_user_response",
]
