"""
Configuration management for GLIMPS Admin CLI.

This module handles configuration persistence for the GLIMPS Admin client,
including credentials, API endpoints, and SSL settings. Configuration is
stored in platform-specific locations.
"""

import json
import os
import platform
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .client import GlimpsAdminClient


__all__ = ["CONFIG_FILE", "Config", "get_config_dir", "load_config", "save_config"]
load_dotenv()


def get_config_dir() -> Path:
    """
    Get the appropriate configuration directory based on the operating system.

    Returns the platform-specific configuration directory:
    - Windows: %APPDATA%/gmadmin
    - macOS: ~/Library/Application Support/gmadmin
    - Linux/Unix: ~/.config/gmadmin

    Returns:
        Path: Configuration directory path
    """
    system = platform.system()

    if system == "Windows":
        # Windows: Use %APPDATA%/gmadmin
        config_dir = Path.home() / "AppData" / "Roaming" / "gmadmin"
    elif system == "Darwin":
        # macOS: Use ~/Library/Application Support/gmadmin
        config_dir = Path.home() / "Library" / "Application Support" / "gmadmin"
    else:
        # Linux and others: Use ~/.config/gmadmin
        config_dir = Path.home() / ".config" / "gmadmin"

    return config_dir


# Configuration file location - computed once at module import
CONFIG_FILE = get_config_dir() / "config.json"


class Config:
    """
    Configuration holder for the GLIMPS Admin CLI.

    This class manages the configuration state including authentication
    credentials, API endpoints, and SSL settings. It provides methods
    to load and save configuration to persistent storage.

    Attributes:
        client: GlimpsAdminClient instance
        url: API base URL
        login: Admin login/username
        token: JWT authentication token
        insecure: Whether to verify SSL certificates
        config_path: Path to configuration file
        password: Admin password (optional, for auto-login)
        totp_secret: TOTP secret for 2FA (optional)
    """

    def __init__(
        self,
        client: GlimpsAdminClient | Any = None,
        url: str = "",
        login: str = "",
        token: str = "",
        expiry: int = 0,
        password: str = "",
        totp_secret: str = "",
        *,
        insecure: bool = False,
    ) -> None:
        """
        Initialize configuration object.

        Args:
            client: Optional GlimpsAdminClient instance
            url: API base URL (default: empty string)
            login: Admin login/username (default: empty string)
            token: JWT token (default: empty string)
            expiry: when does the token expire
            insecure: Whether to not verify SSL certificates (default: False)
            password: Admin password (default: empty string)
            totp_secret: TOTP secret for 2FA (default: empty string)
        """
        self.client = client
        self.url = url
        self.login = login
        self.token = token
        self.expiry = expiry
        self.insecure = insecure
        self.config_path = CONFIG_FILE
        self.password = password
        self.totp_secret = totp_secret

    def __eq__(self, value: object) -> bool:
        """
        Check equality with another Config object.

        Args:
            value: Object to compare with

        Returns:
            bool: True if configurations are equal, False otherwise
        """
        if not isinstance(value, Config):
            return False

        return (
            self.url == value.url
            and self.login == value.login
            and self.token == value.token
            and self.insecure == value.insecure
            and self.password == value.password
            and self.totp_secret == self.totp_secret
        )

    def __repr__(self) -> str:
        """
        String representation of the Config object.

        Returns:
            str: String representation
        """
        return (
            f"Config(url='{self.url}', login='{self.login}', "
            f"insecure={self.insecure}, has_token={bool(self.token)})"
        )

    def load_config(self) -> None:
        """
        Load configuration from persistent storage.

        Updates the current instance with values from the saved configuration file.
        """
        cfg = load_config()
        self.login = cfg.login
        self.url = cfg.url
        self.token = cfg.token
        self.expiry = cfg.expiry
        self.insecure = cfg.insecure
        self.password = cfg.password
        self.totp_secret = cfg.totp_secret

    def save_config(self) -> None:
        """
        Save current configuration to persistent storage.

        Writes the current configuration state to the configuration file.
        """
        save_config(self)

    def clear_credentials(self) -> None:
        """
        Clear sensitive credentials from configuration.

        Removes token, password, and TOTP secret while preserving
        other settings like URL and SSL verification.
        """
        self.token = ""
        self.password = ""
        self.totp_secret = ""

    def is_authenticated(self) -> bool:
        """
        Check if configuration has authentication token.

        Returns:
            bool: True if token is present, False otherwise
        """
        return bool(self.token)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            "url": self.url,
            "login": self.login,
            "token": self.token,
            "expiry": self.expiry,
            "insecure": self.insecure,
            "password": self.password,
            "totp_secret": self.totp_secret,
        }

    def __hash__(self) -> int:
        """
        Hash all fields of Config.

        Returns:
            int: hash()
        """
        return hash(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """
        Create Config instance from dictionary.

        Args:
            data: Dictionary with configuration values

        Returns:
            Config: New Config instance
        """
        return cls(
            url=data.get("url", ""),
            login=data.get("login", ""),
            token=data.get("token", ""),
            expiry=data.get("expiry", 0),
            insecure=data.get("insecure", False),
            password=data.get("password", ""),
            totp_secret=data.get("totp_secret", ""),
        )


def load_config() -> Config:
    """
    Load configuration from file.

    Reads the configuration from the platform-specific configuration file.
    If the file doesn't exist, returns a default configuration.

    Returns:
        Config: Loaded configuration or default if file doesn't exist
    """
    config_from_env = get_config_from_env()
    if CONFIG_FILE.exists():
        try:
            with Path.open(CONFIG_FILE, encoding="utf8") as f:
                data = json.load(f)

                # Handle both old and new configuration formats
                return Config(
                    url=data.get("url", "https://gmalware.glimps.re"),
                    login=data.get("login", data.get("username", "")),  # Support old 'username' field
                    token=data.get("token", ""),
                    expiry=data.get("expiry", 0),
                    insecure=data.get("insecure", False),
                    password=data.get("password", ""),
                    totp_secret=data.get("totp_secret", ""),
                )
        except (OSError, json.JSONDecodeError) as e:
            # If there's an error reading the file, return default config
            print(f"Warning: Could not read configuration file: {e}")
            return config_from_env

    # Return default configuration if file doesn't exist
    return config_from_env


def save_config(config: Config) -> None:
    """
    Save configuration to file.

    Writes the configuration to the platform-specific configuration file.
    Creates the configuration directory if it doesn't exist.

    Args:
        config: Configuration object to save

    Raises:
        IOError: If unable to write configuration file
    """
    data = {
        "url": config.url,
        "login": config.login,
        "token": config.token,
        "expiry": config.expiry,
        "insecure": config.insecure,
        "password": config.password,
        "totp_secret": config.totp_secret,
    }

    # Create configuration directory if it doesn't exist
    if not CONFIG_FILE.exists():
        folder = get_config_dir()
        folder.mkdir(parents=True, exist_ok=True)

    try:
        with Path.open(CONFIG_FILE, "w", encoding="utf8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        raise OSError(f"Failed to save config: {e}") from e


def get_config_from_env() -> Config:
    """
    Create configuration from environment variables.

    Reads configuration from environment variables:
    - GLIMPS_ADMIN_URL: API base URL
    - GLIMPS_ADMIN_LOGIN: Admin login
    - GLIMPS_ADMIN_TOKEN: JWT token
    - GLIMPS_ADMIN_EXPIRY: expiry
    - GLIMPS_ADMIN_PASSWORD: Admin password
    - GLIMPS_ADMIN_INSECURE: disable SSL verification (true/false)
    - GLIMPS_ADMIN_TOTP_SECRET: TOTP secret

    Returns:
        Config: Configuration from environment variables
    """
    return Config(
        url=os.getenv("GLIMPS_ADMIN_URL", ""),
        login=os.getenv("GLIMPS_ADMIN_LOGIN", ""),
        token=os.getenv("GLIMPS_ADMIN_TOKEN", ""),
        expiry=int(os.getenv("GLIMPS_ADMIN_EXPIRY", "0")),
        password=os.getenv("GLIMPS_ADMIN_PASSWORD", ""),
        insecure=os.getenv("GLIMPS_ADMIN_INSECURE", "false").lower() == "true",
        totp_secret=os.getenv("GLIMPS_ADMIN_TOTP_SECRET", ""),
    )


def merge_configs(file_config: Config, env_config: Config) -> Config:
    """
    Merge file and environment configurations.

    Environment variables take precedence over file configuration.

    Args:
        file_config: Configuration from file
        env_config: Configuration from environment

    Returns:
        Config: Merged configuration
    """
    return Config(
        url=env_config.url if env_config.url else file_config.url,
        login=env_config.login if env_config.login else file_config.login,
        token=env_config.token if env_config.token else file_config.token,
        expiry=env_config.expiry if env_config.expiry else file_config.expiry,
        password=env_config.password if env_config.password else file_config.password,
        insecure=env_config.insecure if env_config else file_config.insecure,
        totp_secret=env_config.totp_secret if env_config.totp_secret else file_config.totp_secret,
    )


def get_config() -> Config:
    fconfig = load_config()
    econfig = get_config_from_env()
    return merge_configs(file_config=fconfig, env_config=econfig)


def clear_config() -> None:
    """
    Clear all saved configuration.

    Deletes the configuration file if it exists.
    """
    if CONFIG_FILE.exists():
        try:
            CONFIG_FILE.unlink()
        except OSError as e:
            print(f"Warning: Could not delete configuration file: {e}")


# Default configuration instance
DefaultConfig = Config(url="https://gmalware.glimps.re", insecure=False)
