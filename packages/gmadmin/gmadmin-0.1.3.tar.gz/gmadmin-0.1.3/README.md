# GLIMPS Malware Admin Client Library and CLI

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/gmadmin.svg)](https://badge.fury.io/py/gmadmin)

A comprehensive Python client library and command-line interface for interacting with the GLIMPS Malware Admin API v1.1.0. This tool enables administrators to manage users, profiles, services, and configurations in the GLIMPS malware analysis platform.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [CLI Usage Guide](#cli-usage-guide)
- [Python Library Usage](#python-library-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Testing](#testing)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

### Core Capabilities
- **Complete Admin API Coverage**: Full implementation of GLIMPS Admin API v1.1.0
- **User Management**: Create, update, delete, and manage user accounts
- **Profile Management**: Configure submission profiles with quotas and permissions
- **Role-Based Access Control**: Manage user roles and permissions
- **Multi-Factor Authentication**: Support for TOTP-based 2FA
- **Configuration Management**: View and manage system configurations

### Technical Features
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Secure Authentication**: JWT-based authentication with automatic token management
- **Rich CLI Output**: Formatted tables and colored output for better readability
- **Comprehensive Testing**: 80%+ code coverage with unit and integration tests
- **Type Hints**: Full type annotation support for better IDE integration
- **Configuration Persistence**: Save credentials and settings locally

## Requirements

- Python 3.10 or higher
- pip package manager
- Active GLIMPS Malware Admin account with API access

### System Dependencies
- Operating System: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Network: Internet connection for API access
- Storage: ~10MB for installation

## Installation

### From PyPI (Recommended)

```bash
pip install gmadmin
```

### From Source (Latest Development)

```bash
# Clone the repository
git clone https://github.com/GLIMPS/gmadmin.git
cd gmadmin

# Install in production mode
pip install .

# Or install in development mode (editable)
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Quick Start

### CLI Quick Start

```bash
# Login to the API
gmadmin login
# Enter your admin login and password when prompted

# Check authentication status
gmadmin whoami

# List users
gmadmin users list

# Get user details
gmadmin users get user@example.com

# List profiles
gmadmin profiles list

# Show available services
gmadmin services list
```

### Python Library Quick Start

```python
from gmadmin import GlimpsAdminClient

# Initialize client
client = GlimpsAdminClient(url="https://gmalware.glimps.re")

# Login
client.login("admin", "password")

# List users
users = client.get_users(size=50)
print(f"Total users: {users['count']}")

# Get specific user
user = client.get_user("user@example.com")
print(f"User: {user['name']}, Active: {user['active']}")

# Add new user
new_user = client.add_user(
    username="newuser@example.com",
    name="New User",
    groups=["analysts"],
    types=["user"]
)
print(f"Created user with temporary password: {new_user.get('password')}")
```

## Configuration

### Environment Variables

```bash
# API Configuration
export GLIMPS_ADMIN_URL="https://gmalware.glimps.re"
export GLIMPS_ADMIN_LOGIN="admin"
export GLIMPS_ADMIN_PASSWORD="your-password"
```

### Configuration File

Configuration is stored in a platform-specific location:
- **Linux/Unix**: `~/.config/gmadmin/config.json`
- **macOS**: `~/Library/Application Support/gmadmin/config.json`
- **Windows**: `%APPDATA%\gmadmin\config.json`

Example configuration:
```json
{
  "url": "https://gmalware.glimps.re",
  "login": "admin",
  "token": "eyJhbGci...",
  "verify_ssl": true
}
```

## CLI Usage Guide

### Authentication

```bash
# Login with prompts
gmadmin login

# Login with environment variables
export GLIMPS_ADMIN_LOGIN="admin"
export GLIMPS_ADMIN_PASSWORD="password"
gmadmin login

# Login with TOTP (2FA)
gmadmin login --totp 123456

# Logout
gmadmin logout

# Check current user
gmadmin whoami
```

### User Management

```bash
# List all users
gmadmin users list

# Filter users
gmadmin users list --filter john --type admin --group analysts

# Get user details
gmadmin users get john.doe@example.com

# Add a new user
gmadmin users add \
  --username jane.doe@example.com \
  --name "Jane Doe" \
  --group analysts \
  --type user \
  --role analyst

# Update user
gmadmin users update jane.doe@example.com \
  --active \
  --type admin \
  --group managers

# Reset user password
gmadmin users reset-password jane.doe@example.com

# Delete user
gmadmin users delete jane.doe@example.com
```

### Profile Management

```bash
# List profiles
gmadmin profiles list

# Get profile details
gmadmin profiles get analyst_profile

# Add new profile
gmadmin profiles add \
  --name new_profile \
  --group analysts \
  --quota 100 \
  --priority 5 \
  --service GlimpsCorrelate \
  --role detect_submitter

# Delete profile
gmadmin profiles delete old_profile
```

### Service Management

```bash
# List all services
gmadmin services list
```

### Configuration Commands

```bash
# Show available roles
gmadmin config roles

# Show permissions (detect or expert)
gmadmin config permissions detect
gmadmin config permissions expert
```

### Output Formats

```bash
# Default formatted output
gmadmin users list

# JSON output for scripting
gmadmin users list --json

# Pipe to other tools
gmadmin users list --json | jq '.users[] | .username'
```

## Python Library Usage

### Authentication

```python
from gmadmin import GlimpsAdminClient

# Initialize client
client = GlimpsAdminClient(
    url="https://gmalware.glimps.re",
    verify_ssl=True
)

# Login
result = client.login("admin", "password")
print(f"Token expires at: {client.token_expiry}")

# Login with TOTP
result = client.login("admin", "password", totp_code="123456")

# Check if token is valid
if client.is_token_valid():
    print("Token is still valid")

# Logout
client.logout()
```

### User Management

```python
# List users with filters
users = client.get_users(
    filter="john",
    types=["admin", "user"],
    groups=["analysts"],
    size=100
)

for user in users["users"]:
    print(f"{user['username']}: {user['name']}")

# Get specific user
user = client.get_user("john.doe@example.com")

# Add new user
new_user = client.add_user(
    username="jane.doe@example.com",
    name="Jane Doe",
    groups=["analysts", "reviewers"],
    types=["user"],
    active=True,
    roles=["analyst", "reviewer"]
)

# Update user
client.update_user(
    username="jane.doe@example.com",
    active=False,
    types=["admin"],
    totp_enabled=True
)

# Reset password
result = client.reset_user_password("jane.doe@example.com")
print(f"New password: {result['password']}")

# Delete user
client.delete_user("jane.doe@example.com")
```

### Profile Management

```python
# List profiles
profiles = client.get_profiles(size=50)

# Get specific profile
profile = client.get_profile("analyst_profile")

# Create profile
client.add_profile(
    name="high_priority",
    group="vip",
    daily_quota=1000,
    priority=10,
    result_ttl=730,  # 2 years
    services=["GlimpsCorrelate", "Extract"],
    force_dynamic=True,
    roles=["detect_submitter", "analyst"]
)

# Update profile
client.update_profile(
    name="high_priority",
    daily_quota=2000,
    priority=15
)

# Delete profile
client.delete_profile("old_profile")
```

### Service Management

```python
# List services
services = client.get_services()
for service in services["services"]:
    print(f"{service['name']}: {'Enabled' if service['enabled'] else 'Disabled'}")

# Get service details
service = client.get_service("GlimpsCorrelate")

# Enable/disable service
client.update_service("GlimpsCorrelate", enabled=True)
client.update_service("Extract", enabled=False)
```

### Configuration Access

```python
# Get available roles
roles = client.get_roles_expert()
print("Expert Roles:", roles["roles"])
print("Technical Roles:", roles["technical_roles"])

# Get permissions
detect_perms = client.get_permissions_detect()
expert_perms = client.get_permissions_expert()
```

### Error Handling

```python
from gmadmin.client import APIError

try:
    user = client.get_user("nonexistent@example.com")
except APIError as e:
    print(f"API Error: {e}")
    if e.status_code == 404:
        print("User not found")
    elif e.status_code == 403:
        print("Permission denied")
```

## API Reference

### Client Class

```python
class GlimpsAdminClient:
    def __init__(self, url: str = "https://gmalware.glimps.re", verify_ssl: bool = True)
    
    # Authentication
    def login(self, login: str, password: str, totp_code: Optional[str] = None) -> Dict
    def login_totp(self, totp_code: str) -> Dict
    def logout() -> Dict
    def is_token_valid() -> bool
    def ensure_authenticated() -> None
    
    # User Management
    def get_users(filter: Optional[str], size: int, from_index: int, ...) -> Dict
    def add_user(username: str, name: str, groups: List[str], ...) -> Dict
    def get_user(username: str) -> Dict
    def update_user(username: str, ...) -> Dict
    def delete_user(username: str) -> Dict
    def reset_user_password(username: str) -> Dict
    
    # Profile Management
    def get_profiles(filter: Optional[str], size: int, ...) -> Dict
    def add_profile(name: str, group: str, ...) -> Dict
    def get_profile(name: str) -> Dict
    def update_profile(name: str, ...) -> Dict
    def delete_profile(name: str) -> Dict
    
    # Service Management
    def get_services() -> Dict
    def get_service(service_name: str) -> Dict
    def update_service(service_name: str, enabled: bool) -> Dict
    
    # Configuration
    def get_roles_expert() -> Dict
    def get_permissions_detect() -> Dict
    def get_permissions_expert() -> Dict
```

## Testing

### Running Tests

```bash
# Run all unit tests
pytest

# Run with coverage
pytest --cov=gmadmin

# Run specific test file
pytest tests/test_client.py

# Run integration tests (requires credentials)
export GLIMPS_TEST_API_URL="https://gmalware.glimps.re"
export GLIMPS_TEST_LOGIN="test-admin"
export GLIMPS_TEST_PASSWORD="test-password"
pytest -m integration

# Run with tox (test multiple Python versions)
tox
```

### Test Coverage

Current test coverage targets:
- Minimum: 80%
- Target: 90%+
- Current: Check with `pytest --cov=gmadmin`

## Development

### Project Structure

```
gmadmin/
├── src/gmadmin/          # Source code
│   ├── __init__.py      # Package initialization
│   ├── client.py        # API client implementation
│   ├── cli.py           # CLI implementation
│   └── config.py        # Configuration management
├── tests/               # Test suite
│   ├── test_client.py   # Client tests
│   ├── test_cli.py      # CLI tests
│   └── utils.py         # Test utilities
├── docs/                # Documentation
│   └── openapi.yml      # API specification
├── examples/            # Example scripts
├── requirements.txt     # Production dependencies
└── pyproject.toml       # Project configuration
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/GLIMPS/gmadmin.git
cd gmadmin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run linting
ruff check src tests

# Format code
ruff format src tests

# Run tests
pytest
```

### Code Style

This project follows:
- PEP 8 style guide
- Type hints for all public methods
- Docstrings for all modules, classes, and functions
- Maximum line length: 119 characters

## Troubleshooting

### Common Issues

#### Authentication Failures

**Problem**: "API Error 401: Unauthorized"

**Solutions**:
1. Verify credentials are correct
2. Check if token has expired: `gmadmin whoami`
3. Re-authenticate: `gmadmin login`
4. Verify API URL is correct

#### SSL Certificate Errors

**Problem**: SSL certificate verification failed

**Solutions**:
1. Update certificates: `pip install --upgrade certifi`
2. For testing only: `gmadmin --insecure login`
3. Set custom CA bundle: `export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt`

#### TOTP Authentication Issues

**Problem**: "TOTP code required for authentication"

**Solutions**:
1. Ensure your authenticator app is synchronized
2. Use the `--totp` flag with login: `gmadmin login --totp 123456`
3. Check system time is correct (TOTP is time-based)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/glimps-re/py-gmadmin/issues)
- **Email**: contact@glimps.re

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

## Authors

- GLIMPS Dev Core Team - contact@glimps.re

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Tested with [pytest](https://pytest.org/)