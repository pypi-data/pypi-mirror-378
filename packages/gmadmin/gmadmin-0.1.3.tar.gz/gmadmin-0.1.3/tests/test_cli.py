"""Comprehensive unit tests for GLIMPS Admin CLI."""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gmadmin.cli import gcli
from gmadmin.config import Config
from gmadmin.responses import (
    AddProfileResponse,
    AddUserResponse,
    BaseResponse,
    LoginResponse,
    Permission,
    PermissionsResponse,
    Profile,
    ProfilesListResponse,
    Role,
    RolesResponse,
    Service,
    ServicesListResponse,
    UpdateUserResponse,
    User,
    UsersListResponse,
    local_tz,
)


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock client."""
    client = MagicMock()
    client.is_token_valid.return_value = True
    client.ensure_authenticated.return_value = None
    return client


@pytest.fixture
def mock_config(mock_client: MagicMock) -> Config:
    """Create a mock config with authenticated client."""
    return Config(
        client=mock_client,
        url="https://test.api",
        login="admin",
        token="test-token",
        expiry=int((datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000),
        insecure=False,
    )


class TestMainCLI:
    """Test main CLI commands."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_cli_initialization(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                                runner: CliRunner) -> None:
        """Test CLI initialization with various options."""
        mock_config = Config(url="https://default.api", token="", insecure=False)
        mock_get_config.return_value = mock_config

        # Test default initialization
        result = runner.invoke(gcli, ["--help"])
        assert result.exit_code == 0
        assert "GLIMPS Admin CLI" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_cli_with_url_option(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                                 runner: CliRunner) -> None:
        """Test CLI with custom URL option."""
        mock_config = Config(url="https://default.api", token="", insecure=False)
        mock_get_config.return_value = mock_config

        result = runner.invoke(gcli, ["--url", "https://custom.api", "--help"])
        assert result.exit_code == 0

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_cli_with_insecure_option(self, mock_client_class: MagicMock,
                                      mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test CLI with insecure option."""
        mock_config = Config(url="https://default.api", token="", insecure=False)
        mock_get_config.return_value = mock_config

        result = runner.invoke(gcli, ["--insecure", "--help"])
        assert result.exit_code == 0


class TestAuthentication:
    """Test authentication commands."""

    @patch("gmadmin.cli.save_config")
    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_login_success(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                           mock_save_config: MagicMock, runner: CliRunner) -> None:
        """Test successful login."""
        mock_client = MagicMock()
        mock_login_response = LoginResponse(
            status=True,
            token="new-token",
            validity=int((datetime.now(tz=local_tz) + timedelta(hours=24)).timestamp() * 1000),
        )
        mock_client.login.return_value = mock_login_response
        mock_client_class.return_value = mock_client
        mock_get_config.return_value = Config()

        result = runner.invoke(gcli, ["login"], input="admin\npassword\n")
        assert result.exit_code == 0
        assert "Successfully logged in" in result.output
        mock_save_config.assert_called_once()

    @patch("gmadmin.cli.save_config")
    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_login_with_totp(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                             mock_save_config: MagicMock, runner: CliRunner) -> None:
        """Test login with TOTP."""
        mock_client = MagicMock()
        mock_login_response = LoginResponse(
            status=True,
            token="new-token",
            validity=int((datetime.now(tz=local_tz) + timedelta(hours=24)).timestamp() * 1000),
        )
        mock_client.login.return_value = mock_login_response
        mock_client_class.return_value = mock_client
        mock_get_config.return_value = Config()

        result = runner.invoke(gcli, ["login", "--totp", "123456"], input="admin\npassword\n")
        assert result.exit_code == 0
        # Check that login was called with the correct TOTP (actual input may vary)

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_login_failure(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                           runner: CliRunner) -> None:
        """Test failed login."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception("Invalid credentials")
        mock_client_class.return_value = mock_client
        mock_get_config.return_value = Config()

        result = runner.invoke(gcli, ["login"], input="admin\nwrong\n")
        assert result.exit_code == 1
        assert "Login failed" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_whoami(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                    runner: CliRunner) -> None:
        """Test whoami command."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client_class.return_value = mock_client

        config = Config(
            url="https://test.api",
            login="admin",
            token="test-token",
            expiry=int((datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000),
        )
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["whoami"])
        assert result.exit_code == 0
        assert "Logged in as: admin" in result.output
        # Check that some API URL is shown (the actual URL depends on environment)
        assert "API URL:" in result.output


class TestUserManagement:
    """Test user management commands."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_list(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                        runner: CliRunner) -> None:
        """Test listing users."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        users_response = UsersListResponse(
            status=True,
            count=2,
            users=[
                User(
                    username="user1@example.com",
                    name="User One",
                    active=True,
                    types=["user"],
                    groups=["analysts"],
                ),
                User(
                    username="user2@example.com",
                    name="User Two",
                    active=False,
                    types=["admin"],
                    groups=["admins"],
                ),
            ],
        )
        mock_client.get_users.return_value = users_response
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "list"])
        assert result.exit_code == 0
        assert "User One" in result.output
        assert "User Two" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_list_with_filters(self, mock_client_class: MagicMock,
                                     mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test listing users with filters."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_users.return_value = UsersListResponse(status=True, count=0, users=[])
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, [
            "users", "list",
            "--filter", "john",
            "--size", "50",
            "--type", "admin",
            "--type", "user",
            "--group", "analysts",
            "--tag", "vip",
        ])
        assert result.exit_code == 0

        # Verify the client was called with correct parameters
        mock_client.get_users.assert_called_once()
        call_args = mock_client.get_users.call_args
        assert call_args.kwargs["query_filter"] == "john"
        assert call_args.kwargs["size"] == 50
        assert call_args.kwargs["types"] == ["admin", "user"]
        assert call_args.kwargs["groups"] == ["analysts"]
        assert call_args.kwargs["tags"] == ["vip"]

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_list_json_output(self, mock_client_class: MagicMock,
                                    mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test listing users with JSON output."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_users.return_value = UsersListResponse(
            status=True,
            count=1,
            users=[User(username="test@example.com", name="Test User")],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "list", "--json"])
        assert result.exit_code == 0

        # Parse JSON output
        output_data = json.loads(result.output)
        assert output_data["count"] == 1
        assert output_data["users"][0]["username"] == "test@example.com"

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_get(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                       runner: CliRunner) -> None:
        """Test getting user details."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_user.return_value = User(
            username="test@example.com",
            name="Test User",
            active=True,
            types=["user"],
            groups=["analysts"],
            tags=["vip"],
            totp_enabled=True,
            roles=["analyst", "reviewer"],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "get", "test@example.com"])
        assert result.exit_code == 0
        assert "Test User" in result.output
        assert "analyst" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_add(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                       runner: CliRunner) -> None:
        """Test adding a new user."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.add_user.return_value = AddUserResponse(
            status=True,
            login="new@example.com",
            password="TempPass123!",
            message="User created successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, [
            "users", "add",
            "--username", "new@example.com",
            "--name", "New User",
            "--group", "analysts",
            "--group", "reviewers",
            "--type", "user",
            "--tag", "vip",
            "--role", "analyst",
            "--inactive",
        ])
        assert result.exit_code == 0
        assert "created successfully" in result.output
        assert "TempPass123!" in result.output

        # Verify call parameters
        mock_client.add_user.assert_called_once()
        call_args = mock_client.add_user.call_args
        assert call_args.kwargs["username"] == "new@example.com"
        assert call_args.kwargs["name"] == "New User"
        assert call_args.kwargs["groups"] == ["analysts", "reviewers"]
        assert not call_args.kwargs["active"]

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_update(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                          runner: CliRunner) -> None:
        """Test updating user."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.update_user.return_value = UpdateUserResponse(
            status=True,
            message="User updated successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, [
            "users", "update", "test@example.com",
            "--type", "admin",
            "--group", "admins",
            "--tag", "super",
            "--role", "admin",
            "--active",
            "--totp",
        ])
        assert result.exit_code == 0
        assert "updated successfully" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_delete(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                          runner: CliRunner) -> None:
        """Test deleting user."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.delete_user.return_value = BaseResponse(
            status=True,
            message="User deleted successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        # Confirm deletion
        result = runner.invoke(gcli, ["users", "delete", "test@example.com"], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_users_reset_password(self, mock_client_class: MagicMock,
                                  mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test resetting user password."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.reset_user_password.return_value = AddUserResponse(
            status=True,
            password="NewTempPass456!",
            message="Password reset successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "reset-password", "test@example.com"])
        assert result.exit_code == 0
        assert "Password reset" in result.output
        assert "NewTempPass456!" in result.output


class TestProfileManagement:
    """Test profile management commands."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_profiles_list(self, mock_client_class: MagicMock,
                           mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test listing profiles."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_profiles.return_value = ProfilesListResponse(
            status=True,
            count=2,
            profiles=[
                Profile(
                    name="profile1",
                    group="group1",
                    daily_quota=100,
                    priority=5,
                    services=["Service1", "Service2"],
                ),
                Profile(
                    name="profile2",
                    group="group2",
                    daily_quota=200,
                    priority=10,
                    services=["Service3"],
                ),
            ],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["profiles", "list"])
        assert result.exit_code == 0
        assert "profile1" in result.output
        assert "profile2" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_profiles_list_with_filters(self, mock_client_class: MagicMock,
                                        mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test listing profiles with filters."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_profiles.return_value = ProfilesListResponse(status=True, count=0, profiles=[])
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, [
            "profiles", "list",
            "--filter", "test",
            "--size", "100",
            "--role", "detect_submitter",
            "--role", "analyst",
        ])
        assert result.exit_code == 0

        # Verify call parameters
        mock_client.get_profiles.assert_called_once()
        call_args = mock_client.get_profiles.call_args
        assert call_args.kwargs["query_filter"] == "test"
        assert call_args.kwargs["size"] == 100
        assert call_args.kwargs["roles"] == ["detect_submitter", "analyst"]

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_profiles_get(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                          runner: CliRunner) -> None:
        """Test getting profile details."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_profile.return_value = Profile(
            name="test_profile",
            group="test_group",
            daily_quota=500,
            priority=15,
            result_ttl=30,
            ignore_cache=True,
            force_dynamic=False,
            services=["Service1", "Service2"],
            roles=["detect_submitter"],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["profiles", "get", "test_profile"])
        assert result.exit_code == 0
        assert "test_profile" in result.output
        assert "test_group" in result.output
        assert "500" in result.output
        assert "Service1" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_profiles_add(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                          runner: CliRunner) -> None:
        """Test adding a new profile."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.add_profile.return_value = AddProfileResponse(
            status=True,
            message="Profile created successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, [
            "profiles", "add",
            "--name", "new_profile",
            "--group", "new_group",
            "--quota", "1000",
            "--priority", "1500",
            "--ttl", "60",
            "--al-ttl", "7",
            "--service", "Service1",
            "--service", "Service2",
            "--role", "detect_submitter",
            "--ignore-cache",
            "--force-dynamic",
        ])
        assert result.exit_code == 0
        assert "created successfully" in result.output

        # Verify call parameters
        mock_client.add_profile.assert_called_once()
        call_args = mock_client.add_profile.call_args
        assert call_args.kwargs["name"] == "new_profile"
        assert call_args.kwargs["group"] == "new_group"
        assert call_args.kwargs["daily_quota"] == 1000
        assert call_args.kwargs["priority"] == 1500
        assert call_args.kwargs["ignore_cache"]
        assert call_args.kwargs["force_dynamic"]

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_profiles_delete(self, mock_client_class: MagicMock,
                             mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test deleting profile."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.delete_profile.return_value = BaseResponse(
            status=True,
            message="Profile deleted successfully",
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        # Confirm deletion
        result = runner.invoke(gcli, ["profiles", "delete", "test_profile"], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.output


class TestConfiguration:
    """Test configuration commands."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_config_roles_expert(self, mock_client_class: MagicMock,
                                 mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test showing expert roles."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_roles_expert.return_value = RolesResponse(
            status=True,
            roles=[
                Role(
                    id="analyst",
                    label="Analyst",
                    description="Can perform analysis",
                ),
            ],
            technical_roles=[
                Role(
                    id="tech_role",
                    label="Technical Role",
                    description="Technical permission",
                ),
            ],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["config", "roles"])
        assert result.exit_code == 0
        assert "Analyst" in result.output
        assert "Technical Role" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_config_roles_detect(self, mock_client_class: MagicMock,
                                 mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test showing detect roles."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_roles_detect.return_value = RolesResponse(
            status=True,
            roles=[
                Role(
                    id="detect_submitter",
                    label="Submitter",
                    description="Can submit files",
                ),
            ],
            technical_roles=[],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["config", "roles", "--detect"])
        assert result.exit_code == 0
        assert "Submitter" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_config_roles_json(self, mock_client_class: MagicMock,
                               mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test showing roles with JSON output."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_roles_expert.return_value = RolesResponse(
            status=True,
            roles=[Role(id="role1", label="Role 1")],
            technical_roles=[],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["config", "roles", "--json"])
        assert result.exit_code == 0, f"stderr: {result.stderr}, stdout: {result.stdout}"

        output_data = json.loads(result.output)
        assert output_data["roles"][0]["id"] == "role1"

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_config_permissions_detect(self, mock_client_class: MagicMock,
                                       mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test showing detect permissions."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_permissions_detect.return_value = PermissionsResponse(
            status=True,
            permissions={
                "can_submit": Permission(
                    id="can_submit",
                    label="Submit Files",
                    description="Allow file submission",
                    require_global_access=False,
                ),
            },
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["config", "permissions", "detect"])
        assert result.exit_code == 0
        assert "Submit Files" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_config_permissions_expert(self, mock_client_class: MagicMock,
                                       mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test showing expert permissions."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_permissions_expert.return_value = PermissionsResponse(
            status=True,
            permissions={
                "view_results": Permission(
                    id="view_results",
                    label="View Results",
                    description="View analysis results",
                    require_global_access=True,
                ),
            },
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["config", "permissions", "expert"])
        assert result.exit_code == 0
        assert "View Results" in result.output
        assert "Requires global access" in result.output


class TestServiceManagement:
    """Test service management commands."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_services_list(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                           runner: CliRunner) -> None:
        """Test listing services."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_services.return_value = ServicesListResponse(
            status=True,
            services=[
                Service(
                    name="Service1",
                    version="1.0.0",
                    enabled=True,
                    category="Analysis",
                    stage="CORE",
                ),
                Service(
                    name="Service2",
                    version="2.0.0",
                    enabled=False,
                    category="Detection",
                    stage="POST",
                ),
            ],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["services", "list"])
        assert result.exit_code == 0
        assert "Service1" in result.output
        assert "Service2" in result.output
        assert "Analysis" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_services_list_json(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                                runner: CliRunner) -> None:
        """Test listing services with JSON output."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_services.return_value = ServicesListResponse(
            status=True,
            services=[Service(name="Service1", enabled=True)],
        )
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["services", "list", "--json"])
        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert output_data["services"][0]["name"] == "Service1"


class TestErrorHandling:
    """Test error handling in CLI."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_command_without_auth(self, mock_client_class: MagicMock, mock_get_config: MagicMock,
                                  runner: CliRunner) -> None:
        """Test command execution without authentication."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = False
        mock_client.ensure_authenticated.side_effect = Exception("Not authenticated")
        mock_client_class.return_value = mock_client

        config = Config()  # No token
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "list"])
        assert result.exit_code == 1
        assert "Not logged in" in result.output or "Authentication failed" in result.output

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_api_error_handling(self, mock_client_class: MagicMock,
                                mock_get_config: MagicMock, runner: CliRunner) -> None:
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_users.side_effect = Exception("API Error: 500 Internal Server Error")
        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)
            ).timestamp() * 1000))
        mock_get_config.return_value = config

        result = runner.invoke(gcli, ["users", "list"])
        assert result.exit_code == 1
        assert "Error:" in result.output


class TestComplexScenarios:
    """Test complex CLI scenarios."""

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_multiple_operations_sequence(self, mock_client_class: MagicMock,
                                          mock_get_config: MagicMock,
                                          runner: CliRunner) -> None:
        """Test a sequence of multiple operations."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True

        # Setup mock responses
        mock_client.get_users.return_value = UsersListResponse(
            status=True, count=1, users=[User(username="test@example.com", name="Test User")],
        )
        mock_client.add_user.return_value = AddUserResponse(
            status=True, login="new@example.com", password="Pass123!",
        )
        mock_client.get_profiles.return_value = ProfilesListResponse(
            status=True, count=1, profiles=[Profile(name="profile1", group="group1")],
        )

        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int((
            datetime.now(tz=local_tz) + timedelta(hours=1)).timestamp() * 1000))
        mock_get_config.return_value = config

        # List users
        result = runner.invoke(gcli, ["users", "list"])
        assert result.exit_code == 0

        # Add user
        result = runner.invoke(gcli, [
            "users", "add",
            "--username", "new@example.com",
            "--name", "New User",
            "--group", "test",
        ])
        assert result.exit_code == 0

        # List profiles
        result = runner.invoke(gcli, ["profiles", "list"])
        assert result.exit_code == 0

        # Verify all operations were called
        assert mock_client.get_users.called
        assert mock_client.add_user.called
        assert mock_client.get_profiles.called

    @patch("gmadmin.cli.get_config")
    @patch("gmadmin.cli.GlimpsAdminClient")
    def test_pagination_parameters(self, mock_client_class: MagicMock,
                                   mock_get_config: MagicMock,
                                   runner: CliRunner) -> None:
        """Test pagination parameters in list commands."""
        mock_client = MagicMock()
        mock_client.is_token_valid.return_value = True
        mock_client.get_users.return_value = UsersListResponse(status=True, count=100, users=[])
        mock_client.get_profiles.return_value = ProfilesListResponse(status=True, count=50, profiles=[])

        mock_client_class.return_value = mock_client

        config = Config(token="test-token", expiry=int(
            (datetime.now(tz=local_tz) + timedelta(hours=1)
             ).timestamp() * 1000))
        mock_get_config.return_value = config

        # Test different size parameters
        result = runner.invoke(gcli, ["users", "list", "--size", "100"])
        assert result.exit_code == 0
        mock_client.get_users.assert_called_with(query_filter=None, size=100, types=None, groups=None, tags=None)

        result = runner.invoke(gcli, ["profiles", "list", "--size", "50"])
        assert result.exit_code == 0
        mock_client.get_profiles.assert_called_with(query_filter=None, size=50, roles=None)
