"""Integration tests for GLIMPS Admin API client.

These tests run against a real GLIMPS server and require:
1. A running GLIMPS server instance
2. Valid credentials (username/password)
3. Network connectivity to the server

Environment variables for configuration:
- GLIMPS_API_URL: Base URL of the GLIMPS server (default: https://admin.gmalware.tld)
- GLIMPS_USERNAME: Username for authentication (required)
- GLIMPS_PASSWORD: Password for authentication (required)
- GLIMPS_INSECURE: Skip SSL verification (default: false)

Run with: pytest tests/test_integration.py -m integration
"""

import contextlib
import os
import random
import string
from datetime import datetime, timedelta

import pytest

from gmadmin.client import APIError, GlimpsAdminClient
from gmadmin.responses import local_tz


# Test configuration from environment variables
GLIMPS_API_URL = os.getenv("GLIMPS_API_URL", "https://admin.gmalware.tld")
GLIMPS_USERNAME = os.getenv("GLIMPS_USERNAME")
GLIMPS_PASSWORD = os.getenv("GLIMPS_PASSWORD")
GLIMPS_INSECURE = os.getenv("GLIMPS_INSECURE", "false").lower() in ("true", "1", "yes")

# Skip all integration tests if credentials are not provided
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.skipif(
        not GLIMPS_USERNAME or not GLIMPS_PASSWORD,
        reason="Integration tests require GLIMPS_USERNAME and GLIMPS_PASSWORD environment variables",
    ),
]


@pytest.fixture(scope="module")
def integration_client() -> GlimpsAdminClient:
    """Create a client configured for integration testing."""
    return GlimpsAdminClient(
        url=GLIMPS_API_URL,
        insecure=GLIMPS_INSECURE,
    )


@pytest.fixture(scope="module")
def authenticated_client(integration_client: GlimpsAdminClient) -> GlimpsAdminClient:
    """Authenticate the client and return it."""
    try:
        login_response = integration_client.login(GLIMPS_USERNAME, GLIMPS_PASSWORD)
        if not login_response.is_success():
            pytest.skip(f"Authentication failed: {login_response.error}")
        else:
            return integration_client
    except APIError as e:
        pytest.skip(f"Authentication failed with API error: {e}")
    except Exception as e:
        pytest.skip(f"Authentication failed with unexpected error: {e}")


class TestIntegrationAuthentication:
    """Integration tests for authentication."""

    def test_login_success(self, integration_client: GlimpsAdminClient) -> None:
        """Test successful login with valid credentials."""
        response = integration_client.login(GLIMPS_USERNAME, GLIMPS_PASSWORD)

        assert response.is_success(), f"Login failed: {response.error}"
        assert response.token is not None, "No token received"
        assert response.validity is not None, "No token validity received"

        # Verify token is valid for reasonable time (at least 1 hour)
        expiry_time = datetime.fromtimestamp(response.validity / 1000, tz=local_tz)
        min_expiry = datetime.now(tz=local_tz) + timedelta(hours=1)
        assert expiry_time > min_expiry, f"Token expires too soon: {expiry_time}"

    def test_login_invalid_credentials(self, integration_client: GlimpsAdminClient) -> None:
        """Test login with invalid credentials."""
        with pytest.raises(APIError) as exc_info:
            integration_client.login("invalid_user", "invalid_password")

        assert "Unauthorized" in str(exc_info.value) or "Forbidden" in str(exc_info.value)

    def test_token_validation(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test token validation."""
        assert authenticated_client.is_token_valid(), "Valid token should be recognized as valid"

        # Test with invalid token by creating a copy of the client
        test_client = GlimpsAdminClient(url=GLIMPS_API_URL, insecure=GLIMPS_INSECURE)
        test_client.token = ""
        assert not test_client.is_token_valid(), "Invalid token should be recognized as invalid"


class TestIntegrationUserManagement:
    """Integration tests for user management."""

    def test_get_users(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test listing users."""
        response = authenticated_client.get_users()

        assert response.is_success(), f"Get users failed: {response.error}"
        assert response.count >= 0, "User count should be non-negative"
        assert isinstance(response.users, list), "Users should be a list"

        # If there are users, validate the first one
        if response.users:
            user = response.users[0]
            assert user.username, "User should have a username"
            assert user.name, "User should have a name"
            assert isinstance(user.active, bool), "User active status should be boolean"

    def test_get_users_with_filters(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test listing users with filters."""
        # Test with size parameter
        response = authenticated_client.get_users(size=5)
        assert response.is_success(), f"Get users with size filter failed: {response.error}"
        assert len(response.users) <= 5, "Response should respect size limit"

    def test_get_user_details(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting specific user details."""
        # First get list of users to find a valid username
        users_response = authenticated_client.get_users(size=1)
        if not users_response.users:
            pytest.skip("No users available for testing")

        username = users_response.users[0].username
        user = authenticated_client.get_user(username)

        assert user.username == username, f"Returned user should match requested username {username} {user}"
        assert user.name, "User should have a name"


class TestIntegrationProfileManagement:
    """Integration tests for profile management."""

    def test_get_profiles(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test listing profiles."""
        response = authenticated_client.get_profiles()

        assert response.is_success(), f"Get profiles failed: {response.error}"
        assert response.count >= 0, "Profile count should be non-negative"
        assert isinstance(response.profiles, list), "Profiles should be a list"

    def test_get_profiles_with_filters(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test listing profiles with filters."""
        response = authenticated_client.get_profiles(size=3)
        assert response.is_success(), f"Get profiles with filter failed: {response.error}"
        assert len(response.profiles) <= 3, "Response should respect size limit"

    def test_get_profile_details(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting specific profile details."""
        # First get list of profiles to find a valid name
        profiles_response = authenticated_client.get_profiles(size=1)
        if not profiles_response.profiles:
            pytest.skip("No profiles available for testing")

        profile_name = profiles_response.profiles[0].name
        profile = authenticated_client.get_profile(profile_name)

        assert profile.name == profile_name, "Returned profile should match requested name"
        assert profile.group, "Profile should have a group"


class TestIntegrationServiceManagement:
    """Integration tests for service management."""

    def test_get_services(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test listing services."""
        response = authenticated_client.get_services()

        assert response.is_success(), f"Get services failed: {response.error}"
        assert isinstance(response.services, list), "Services should be a list"

        # If there are services, validate the first one
        if response.services:
            service = response.services[0]
            assert service.name, "Service should have a name"
            assert service.version, "Service should have a version"
            assert isinstance(service.enabled, bool), "Service enabled status should be boolean"


class TestIntegrationConfiguration:
    """Integration tests for configuration endpoints."""

    def test_get_roles_expert(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting expert roles configuration."""
        response = authenticated_client.get_roles_expert()

        assert response.is_success(), f"Get expert roles failed: {response.error}"
        assert isinstance(response.roles, list), "Roles should be a list"
        assert isinstance(response.technical_roles, list), "Technical roles should be a list"

    def test_get_roles_detect(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting detect roles configuration."""
        response = authenticated_client.get_roles_detect()

        assert response.is_success(), f"Get detect roles failed: {response.error}"
        assert isinstance(response.roles, list), "Roles should be a list"
        assert isinstance(response.technical_roles, list), "Technical roles should be a list"

    def test_get_permissions_expert(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting expert permissions configuration."""
        response = authenticated_client.get_permissions_expert()

        assert response.is_success(), f"Get expert permissions failed: {response.error}"
        assert isinstance(response.permissions, dict), "Permissions should be a dictionary"

    def test_get_permissions_detect(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting detect permissions configuration."""
        response = authenticated_client.get_permissions_detect()

        assert response.is_success(), f"Get detect permissions failed: {response.error}"
        assert isinstance(response.permissions, dict), "Permissions should be a dictionary"


class TestIntegrationErrorHandling:
    """Integration tests for error handling."""

    def test_unauthorized_request(self) -> None:
        """Test that unauthorized requests are properly handled."""
        # Create a new unauthenticated client
        unauthenticated_client = GlimpsAdminClient(url=GLIMPS_API_URL, insecure=GLIMPS_INSECURE)
        with pytest.raises(APIError) as exc_info:
            unauthenticated_client.get_users()

        assert "Unauthorized" in str(exc_info.value) or "Forbidden" in str(exc_info.value)

    def test_not_found_user(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test handling of non-existent user."""
        with pytest.raises(APIError) as exc_info:
            authenticated_client.get_user("nonexistent_user_12345")

        assert "404" in str(exc_info.value), f"value: {exc_info.value}"

    def test_not_found_profile(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test handling of non-existent profile."""
        with pytest.raises(APIError) as exc_info:
            authenticated_client.get_profile("nonexistent_profile_12345")

        assert "404" in str(exc_info.value), f"exc_info: {exc_info}"


class TestIntegrationConnectivity:
    """Integration tests for basic connectivity."""

    def test_server_reachable(self, integration_client: GlimpsAdminClient) -> None:
        """Test that the server is reachable."""
        try:
            # Try to make a request that should work even without auth
            # (this might fail with 401, but shouldn't fail with connection errors)
            integration_client.get_users()
        except APIError as e:
            # 401/403 are expected for unauthenticated requests
            if "Unauthorized" not in str(e) and "Forbidden" not in str(e):
                pytest.fail(f"Server connectivity issue: {e}")
        except Exception as e:
            pytest.fail(f"Server connectivity issue: {e}")

    def test_ssl_configuration(self, integration_client: GlimpsAdminClient) -> None:
        """Test SSL configuration if using HTTPS."""
        if not GLIMPS_API_URL.startswith("https://"):
            pytest.skip("SSL test only applies to HTTPS endpoints")

        # This test ensures SSL works correctly
        # The actual request may fail with auth errors, but SSL should work
        try:
            integration_client.get_users()
        except APIError as e:
            # Auth errors are fine, SSL errors are not
            if "SSL" in str(e) or "certificate" in str(e).lower():
                pytest.fail(f"SSL configuration issue: {e}")
        except Exception as e:
            if "SSL" in str(e) or "certificate" in str(e).lower():
                pytest.fail(f"SSL configuration issue: {e}")


# Cleanup tests that can modify data (these are more dangerous)
class TestIntegrationWriteOperations:
    """Integration tests for write operations.

    WARNING: These tests may modify server data and should be run
    against test environments only!
    """

    @pytest.mark.skipif(
        os.getenv("GLIMPS_ALLOW_WRITE_TESTS", "false").lower() not in ("true", "1", "yes"),
        reason="Write tests disabled. Set GLIMPS_ALLOW_WRITE_TESTS=true to enable.",
    )
    def test_version_info(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test getting version information (safe read-only operation)."""
        try:
            response = authenticated_client.get_version()
            assert response.version, "Version should not be empty"
        except APIError as e:
            # Some servers might not have this endpoint
            if "404" not in str(e):
                raise


def _generate_test_username() -> str:
    """Generate a random test username."""
    chars = string.ascii_lowercase + string.digits
    random_suffix = "".join(random.choices(chars, k=8))  # noqa: S311
    return f"test_user_{random_suffix}@integration.test"


def _generate_test_profile_name() -> str:
    """Generate a random test profile name."""
    chars = string.ascii_lowercase + string.digits
    random_suffix = "".join(random.choices(chars, k=8))  # noqa: S311
    return f"test_profile_{random_suffix}"


class TestIntegrationUserLifecycleDetect:
    """Integration tests for complete user lifecycle in detect context."""

    def test_detect_user_lifecycle(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test complete user lifecycle for detect user: create, validate, update, delete."""
        test_username = _generate_test_username()
        test_profile_name = _generate_test_profile_name()

        try:
            # Step 1: Verify user doesn't exist
            with pytest.raises(APIError) as exc_info:
                authenticated_client.get_user(test_username)
            assert "404" in str(exc_info.value), "User should not exist initially"

            # Step 2: Create detect profile first
            profile_params = {
                "name": test_profile_name,
                "group": "detect_analysts",
                "daily_quota": 500,
                "al_ttl": 30,
                "result_ttl": 7,
                "malware_threshold": 800,
                "priority": 1500,
                "services": ["Scalpel"],
            }

            profile_response = authenticated_client.add_profile(**profile_params)
            assert profile_response.is_success(), f"Profile creation failed: {profile_response.error}"

            # Step 3: Validate profile creation
            profile = authenticated_client.get_profile(test_profile_name)
            assert profile.name == test_profile_name, "Profile name should match"
            assert profile.group == "detect_analysts", "Profile group should match"
            assert profile.daily_quota == 500, "Profile daily quota should match"
            assert profile.malware_threshold == 800, "Profile malware threshold should match"
            assert profile.priority == 1500, "Profile malware priority should match"
            assert profile.services == ["Scalpel"]

            # Step 4: Update profile parameters
            profile_update_params = {
                "name": test_profile_name,
                "daily_quota": 1000,
                "malware_threshold": 900,
                "priority": 500,
                "services": ["Extract"],
            }

            profile_update_response = authenticated_client.update_profile(**profile_update_params)
            assert profile_update_response.is_success(), f"Profile update failed: {profile_update_response.error}"

            # Step 5: Validate profile updates
            updated_profile = authenticated_client.get_profile(test_profile_name)
            assert updated_profile.daily_quota == 1000, "Profile daily quota should be updated"
            assert updated_profile.malware_threshold == 900, "Profile malware threshold should be updated"
            assert updated_profile.priority == 500, "Profile priority should be updated"
            assert updated_profile.services == ["Extract"]

            # Step 6: Delete profile
            profile_delete_response = authenticated_client.delete_profile(test_profile_name)
            assert profile_delete_response.is_success(), f"Profile deletion failed: {profile_delete_response.error}"

            # Step 7: Verify profile no longer exists
            with pytest.raises(APIError) as exc_info:
                authenticated_client.get_profile(test_profile_name)
            assert "404" in str(exc_info.value), "Profile should not exist after deletion"

        except Exception:
            # Cleanup: Always try to delete the test user and profile if something goes wrong
            with contextlib.suppress(APIError):
                authenticated_client.delete_user(test_username)
            with contextlib.suppress(APIError):
                authenticated_client.delete_profile(test_profile_name)
            raise  # Re-raise the original exception


class TestIntegrationUserLifecycleExpert:
    """Integration tests for complete user lifecycle in expert context."""

    def test_expert_user_lifecycle(self, authenticated_client: GlimpsAdminClient) -> None:
        """Test complete user lifecycle for expert user: create, validate, update, delete."""
        test_username = _generate_test_username()

        try:
            # Step 1: Verify user doesn't exist
            with pytest.raises(APIError) as exc_info:
                authenticated_client.get_user(test_username)
            assert "404" in str(exc_info.value), "User should not exist initially"

            # Step 2: Create expert user with custom parameters
            initial_params = {
                "name": "Test Expert User",
                "username": test_username,
                "groups": ["expert_analysts", "malware_researchers"],
                "types": ["user"],
                "tags": ["integration_test", "expert", "researcher"],
                "active": True,
                "roles": ["analysis_submitter"],
            }

            create_response = authenticated_client.add_user(**initial_params)
            assert create_response.is_success(), f"User creation failed: {create_response.error}"
            assert create_response.login == test_username, "Created user login should match"
            assert create_response.password, "Temporary password should be provided"

            # Step 3: Get and validate initial user parameters
            user = authenticated_client.get_user(test_username)
            assert user.username == test_username, "Username should match"
            assert user.name == "Test Expert User", "Name should match"
            assert user.active is True, "User should be active"
            assert "expert_analysts" in user.groups, "User should be in expert_analysts group"
            assert "malware_researchers" in user.groups, "User should be in malware_researchers group"
            assert "integration_test" in user.tags, "User should have integration_test tag"
            assert "expert" in user.tags, "User should have expert tag"
            assert "researcher" in user.tags, "User should have researcher tag"

            # Step 4: Update user with different parameters
            update_params = {
                "username": test_username,
                "types": ["admin"],
                "groups": ["expert_analysts", "senior_researchers", "threat_hunters"],
                "tags": ["integration_test", "expert", "senior", "threat_hunting"],
                "active": True,  # Keep active but change other params
            }

            update_response = authenticated_client.update_user(**update_params)
            assert update_response.is_success(), f"User update failed: {update_response.error}"

            # Step 5: Get and validate updated parameters
            updated_user = authenticated_client.get_user(test_username)
            assert updated_user.username == test_username, "Username should remain same"
            assert updated_user.active is True, "User should remain active"
            assert "admin" in updated_user.types, "User should have super_admin type"
            assert "senior_researchers" in updated_user.groups, "User should be in senior_researchers group"
            assert "threat_hunters" in updated_user.groups, "User should be in threat_hunters group"
            assert "senior" in updated_user.tags, "User should have senior tag"
            assert "threat_hunting" in updated_user.tags, "User should have threat_hunting tag"

            # Step 6: Delete user
            delete_response = authenticated_client.delete_user(test_username)
            assert delete_response.is_success(), f"User deletion failed: {delete_response.error}"

            # Step 7: Verify user no longer exists
            with pytest.raises(APIError) as exc_info:
                authenticated_client.get_user(test_username)
            assert "404" in str(exc_info.value), "User should not exist after deletion"

        except Exception:
            # Cleanup: Always try to delete the test user if something goes wrong
            with contextlib.suppress(APIError):
                authenticated_client.delete_user(test_username)
            raise
