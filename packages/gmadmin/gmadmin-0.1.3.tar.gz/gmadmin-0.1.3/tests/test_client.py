"""Unit tests for GLIMPS Admin API client."""

from datetime import datetime, timedelta

import pytest
import responses

from gmadmin.client import APIError, GlimpsAdminClient
from gmadmin.responses import (
    AddUserResponse,
    BaseResponse,
    LoginResponse,
    Profile,
    ProfilesListResponse,
    ServicesListResponse,
    UpdateUserResponse,
    User,
    UsersListResponse,
    local_tz,
)
from tests.utils import (
    create_mock_login_response,
    create_mock_profile_response,
    create_mock_service_response,
    create_mock_user_response,
)


@pytest.fixture
def client() -> GlimpsAdminClient:
    """Create a test client."""
    return GlimpsAdminClient(url="https://test.api", insecure=True)


@pytest.fixture
def auth_client() -> GlimpsAdminClient:
    """Create an authenticated test client."""
    client = GlimpsAdminClient(url="https://test.api", insecure=True)
    client.token = "test-token-123"
    client.token_expiry = datetime.now(tz=local_tz) + timedelta(hours=1)
    return client


class TestAuthentication:
    """Test authentication endpoints."""

    @responses.activate
    def test_login_success(self, client: GlimpsAdminClient) -> None:
        """Test successful login."""
        responses.add(
            responses.POST,
            "https://test.api/api/v1/login",
            json=create_mock_login_response(),
            status=200,
        )

        result = client.login("admin", "password")

        assert isinstance(result, LoginResponse)
        assert result.status is True
        assert result.token is not None
        assert client.token is not None
        assert client.token_expiry is not None

    @responses.activate
    def test_login_with_totp(self, client: GlimpsAdminClient) -> None:
        """Test login with TOTP requirement."""
        # First login returns TOTP requirement
        responses.add(
            responses.POST,
            "https://test.api/api/v1/login",
            json={"status": True, "require_totp": True, "token": "temp-token"},
            status=200,
        )

        # TOTP submission
        responses.add(
            responses.POST,
            "https://test.api/api/v1/login_totp",
            json=create_mock_login_response(),
            status=200,
        )

        result = client.login("admin", "password", totp_code="123456")

        assert isinstance(result, LoginResponse)
        assert result.status is True
        assert client.token is not None

    @responses.activate
    def test_login_failure(self, client: GlimpsAdminClient) -> None:
        """Test failed login."""
        responses.add(
            responses.POST,
            "https://test.api/api/v1/login",
            json={"status": False, "error": "unauthorized"},
            status=401,
        )

        with pytest.raises(APIError) as exc_info:
            client.login("admin", "wrong-password")

        assert exc_info.value.status_code == 401

    def test_is_token_valid(self, auth_client: GlimpsAdminClient) -> None:
        """Test token validity check."""
        assert auth_client.is_token_valid() is True

        # Test with expired token
        auth_client.token_expiry = datetime.now(tz=local_tz) - timedelta(hours=1)
        assert auth_client.is_token_valid() is False

        # Test with no token
        auth_client.token = None
        assert auth_client.is_token_valid() is False


class TestUserManagement:
    """Test user management endpoints."""

    @responses.activate
    def test_get_users(self, auth_client: GlimpsAdminClient) -> None:
        """Test getting users list."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/users",
            json={
                "status": True,
                "count": 1,
                "users": [create_mock_user_response()],
            },
            status=200,
        )

        result = auth_client.get_users(size=25)

        assert isinstance(result, UsersListResponse)
        assert result.count == 1
        assert len(result.users) == 1
        assert result.users[0].username == "test@example.com"

    @responses.activate
    def test_add_user(self, auth_client: GlimpsAdminClient) -> None:
        """Test adding a new user."""
        responses.add(
            responses.POST,
            "https://test.api/api/v1/users",
            json={
                "status": True,
                "login": "test@example.com",
                "password": "temp-password-123",
                "message": "User created successfully",
            },
            status=200,
        )

        result = auth_client.add_user(
            username="test@example.com",
            name="Test User",
            groups=["analysts"],
            types=["user"],
        )

        assert isinstance(result, AddUserResponse)
        assert result.login == "test@example.com"
        assert result.password is not None

    @responses.activate
    def test_get_user(self, auth_client: GlimpsAdminClient) -> None:
        """Test getting specific user."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/users/test@example.com",
            json={"user": create_mock_user_response()},
            status=200,
        )

        result = auth_client.get_user("test@example.com")

        assert isinstance(result, User)
        assert result.username == "test@example.com"
        assert result.active is True

    @responses.activate
    def test_update_user(self, auth_client: GlimpsAdminClient) -> None:
        """Test updating user."""
        responses.add(
            responses.PUT,
            "https://test.api/api/v1/users/test@example.com",
            json={
                "status": True,
                "message": "User updated successfully",
            },
            status=200,
        )

        result = auth_client.update_user(
            username="test@example.com",
            active=False,
            types=["admin"],
        )

        assert isinstance(result, UpdateUserResponse)
        assert result.is_success()

    @responses.activate
    def test_delete_user(self, auth_client: GlimpsAdminClient) -> None:
        """Test deleting user."""
        responses.add(
            responses.DELETE,
            "https://test.api/api/v1/users/test@example.com",
            json={"status": True, "message": "user deleted"},
            status=200,
        )

        result = auth_client.delete_user("test@example.com")

        assert result.is_success()

    @responses.activate
    def test_reset_user_password(self, auth_client: GlimpsAdminClient) -> None:
        """Test resetting user password."""
        responses.add(
            responses.POST,
            "https://test.api/api/v1/users/test@example.com/password/reset",
            json={"status": True, "password": "new-temp-password"},
            status=200,
        )

        result = auth_client.reset_user_password("test@example.com")

        assert isinstance(result, AddUserResponse)
        assert result.is_success()
        assert result.password is not None


class TestProfileManagement:
    """Test profile management endpoints."""

    @responses.activate
    def test_get_profiles(self, auth_client: GlimpsAdminClient) -> None:
        """Test getting profiles list."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/profiles",
            json={
                "status": True,
                "count": 1,
                "profiles": [create_mock_profile_response()],
            },
            status=200,
        )

        result = auth_client.get_profiles(size=25)

        assert isinstance(result, ProfilesListResponse)
        assert result.count == 1
        assert len(result.profiles) == 1
        assert result.profiles[0].name == "test_profile"

    @responses.activate
    def test_add_profile(self, auth_client: GlimpsAdminClient) -> None:
        """Test adding a new profile."""
        responses.add(
            responses.POST,
            "https://test.api/api/v1/profiles",
            json={
                "status": True,
                "message": "Profile test_profile created successfully",
                "token": "profile-token-123",
            },
            status=200,
        )

        result = auth_client.add_profile(
            name="test_profile",
            group="test_group",
            daily_quota=1001,
        )

        assert result.is_success()
        if result.message:
            assert "test_profile" in result.message

    @responses.activate
    def test_get_profile(self, auth_client: GlimpsAdminClient) -> None:
        """Test getting specific profile."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/profiles/test_profile",
            json={
                "profile": create_mock_profile_response(),
            },
            status=200,
        )

        result = auth_client.get_profile("test_profile")

        assert isinstance(result, Profile)
        expected = create_mock_profile_response()
        assert result.name == expected["name"]
        assert result.group == expected["group"]
        assert result.daily_quota == expected["daily_quota"]

    @responses.activate
    def test_delete_profile(self, auth_client: GlimpsAdminClient) -> None:
        """Test deleting profile."""
        responses.add(
            responses.DELETE,
            "https://test.api/api/v1/profiles/test_profile",
            json={"status": True, "message": "profile deleted"},
            status=200,
        )

        result = auth_client.delete_profile("test_profile")

        assert isinstance(result, BaseResponse)
        assert result.is_success()


class TestServiceManagement:
    """Test service management endpoints."""

    @responses.activate
    def test_get_services(self, auth_client: GlimpsAdminClient) -> None:
        """Test getting services list."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/services",
            json={
                "status": True,
                "services": [create_mock_service_response()],
            },
            status=200,
        )

        result = auth_client.get_services()

        assert isinstance(result, ServicesListResponse)
        assert len(result.services) == 1
        assert result.services[0].name == "GlimpsCorrelate"


class TestErrorHandling:
    """Test error handling."""

    @responses.activate
    def test_api_error_401(self, client: GlimpsAdminClient) -> None:
        """Test handling 401 Unauthorized."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/users",
            json={"status": False, "error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_users()

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    @responses.activate
    def test_api_error_403(self, auth_client: GlimpsAdminClient) -> None:
        """Test handling 403 Forbidden."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/users",
            json={"status": False, "error": "Forbidden"},
            status=403,
        )

        with pytest.raises(APIError) as exc_info:
            auth_client.get_users()

        assert exc_info.value.status_code == 403
        assert "Forbidden" in str(exc_info.value)

    @responses.activate
    def test_api_error_500(self, auth_client: GlimpsAdminClient) -> None:
        """Test handling 500 Internal Server Error."""
        responses.add(
            responses.GET,
            "https://test.api/api/v1/users",
            json={"status": False, "error": "Internal server error"},
            status=500,
        )

        with pytest.raises(APIError) as exc_info:
            auth_client.get_users()

        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
