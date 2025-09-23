#!/usr/bin/env python3
"""
GLIMPS Admin CLI Tool.

A command-line interface for the GLIMPS Admin API using Click.
"""

import json
import sys
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import ParamSpec, TypeVar

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .client import GlimpsAdminClient
from .config import Config, get_config, save_config
from .responses import local_tz


console = Console()
pass_config = click.make_pass_decorator(Config, ensure=True)


user_config = get_config()


P = ParamSpec("P")
R = TypeVar("R")


def remap_params(**mappings: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Decorator to remap parameter names with full type preservation."""
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for old_name, new_name in mappings.items():
                if old_name in kwargs:
                    kwargs[new_name] = kwargs.pop(old_name)
            return f(*args, **kwargs)  # type: ignore
        return wrapper
    return decorator


def ensure_auth(config: Config) -> None:
    """Ensure the client is authenticated."""
    if config.client is None:
        click.echo("Not logged in. Please run 'gmadmin login' first.", err=True)
        sys.exit(1)

    try:
        config.client.ensure_authenticated()
    except Exception as e:
        click.echo(f"Authentication failed: {e}", err=True)
        click.echo("Please run 'gmadmin login' again.", err=True)
        sys.exit(1)


@click.group()
@click.option(
    "--url",
    envvar="GLIMPS_ADMIN_URL",
    default=user_config.url,
    help="URL for the GLIMPS server",
)
@click.option("--insecure", is_flag=True, help="Disable SSL verification")
@pass_config
def gcli(config: Config, url: str, *, insecure: bool) -> None:
    """GLIMPS Admin CLI - Command line interface for GLIMPS Admin API."""
    # Load saved configuration into the existing config object
    saved_config = get_config()
    config.url = saved_config.url
    config.login = saved_config.login
    config.token = saved_config.token
    config.expiry = saved_config.expiry
    config.insecure = saved_config.insecure or insecure

    # Override with command line options if provided
    if url != "https://gmalware.glimps.re":  # Only override if not default
        config.url = url

    # Initialize client
    config.client = GlimpsAdminClient(url=config.url, insecure=config.insecure)
    if config.token:
        config.client.token = config.token
        config.client.token_expiry = datetime.fromtimestamp(config.expiry / 1000, tz=local_tz)


# Authentication commands


@gcli.command()
@click.option(
    "--login",
    prompt=True,
    prompt_required=user_config.login == "",
    help="Admin login",
    default=user_config.login,
)
@click.option(
    "--password",
    prompt=True,
    prompt_required=user_config.password == "",
    hide_input=True,
    help="Admin password",
)
@click.option("--totp", help="TOTP code for 2FA")
@pass_config
def login(config: Config, login: str, password: str, totp: str) -> None:
    """Login to GLIMPS Admin API."""
    try:
        if password is None or password == "":
            password = user_config.password
        result = config.client.login(login, password, totp)
        config.login = login
        config.token = result.token
        config.expiry = result.validity
        config.password = password
        save_config(config)

        rprint(f"[green]✓[/green] Successfully logged in as {login}")
        if result.validity:
            expiry = datetime.fromtimestamp(result.validity / 1000, tz=local_tz)
            rprint(f"Token expires at: {expiry}")
    except Exception as e:
        rprint(f"[red]✗[/red] Login failed: {e}")
        sys.exit(1)


@gcli.command()
@pass_config
def whoami(config: Config) -> None:
    """Show current admin information."""
    ensure_auth(config)
    rprint(f"Logged in as: {config.login}")
    rprint(f"API URL: {config.url}")


# User Management Commands


@gcli.group()
def users() -> None:
    """User management commands."""


@users.command("list")
@click.option("--filter", "-f", "qfilter", help="Filter by name/username")
@click.option("--size", "-s", default=25, help="Number of results")
@click.option("--type", "-t", "utype", multiple=True, help="Filter by user type (user/admin)")
@click.option("--group", "-g", multiple=True, help="Filter by group")
@click.option("--tag", multiple=True, help="Filter by tag")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def list_users(config: Config, qfilter: str, size: int, utype: list[str],
               group: list[str], tag: list[str], *, output_json: bool) -> None:
    """List users."""
    ensure_auth(config)

    try:
        result = config.client.get_users(
            query_filter=qfilter,
            size=size,
            types=list(utype) if utype else None,
            groups=list(group) if group else None,
            tags=list(tag) if tag else None,
        )

        if output_json:
            # Convert to dictionary for JSON output (backward compatibility)
            data = {
                "status": result.status,
                "count": result.count,
                "users": [user.to_dict() for user in result.users],
            }
            print(json.dumps(data, indent=2))
        else:
            table = Table(title=f"Users (Total: {result.count})")
            table.add_column("Username", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Active", style="yellow")
            table.add_column("Types", style="magenta")
            table.add_column("Groups", style="blue")

            for user in result.users:
                table.add_row(
                    user.username,
                    user.name,
                    "✓" if user.active else "✗",
                    ", ".join(user.types),
                    ", ".join(user.groups),
                )

            console.print(table)
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("get")
@click.argument("username")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def get_user(config: Config, username: str, *, output_json: bool) -> None:
    """Get user details."""
    ensure_auth(config)

    try:
        user = config.client.get_user(username)

        if output_json:
            print(json.dumps(user.to_dict(), indent=2))
        else:
            rprint(f"[bold]User Details: {username}[/bold]")
            rprint(f"Name: {user.name}")
            rprint(f"Active: {'Yes' if user.active else 'No'}")
            rprint(f"Types: {', '.join(user.types)}")
            rprint(f"Groups: {', '.join(user.groups)}")
            rprint(f"Tags: {', '.join(user.tags)}")
            rprint(f"TOTP Enabled: {'Yes' if user.totp_enabled else 'No'}")

            if user.roles:
                rprint(f"Roles: {', '.join(user.roles)}")

            if user.permissions:
                rprint("[bold]Permissions:[/bold]")
                perms_dict = user.to_dict()["permissions"]
                for key, value in perms_dict.items():
                    rprint(f"  {key}: {value}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("add")
@click.option("--username", "-u", required=True, help="Username (email)")
@click.option("--name", "-n", required=True, help="Display name")
@click.option("--group", "-g", required=True, multiple=True, help="User group (at least one)")
@click.option("--type", "-t", "utype", multiple=True, help="User type (user/admin)")
@click.option("--tag", multiple=True, help="User tag")
@click.option("--role", "-r", multiple=True, help="User role")
@click.option("--inactive", is_flag=True, help="Create as inactive")
@pass_config
def add_user(config: Config, username: str, name: str, group: list[str],
             utype: list[str], tag: list[str], role: list[str], *,
             inactive: bool) -> None:
    """Add a new user."""
    ensure_auth(config)

    try:
        result = config.client.add_user(
            username=username,
            name=name,
            groups=list(group),
            active=not inactive,
            types=list(utype) if utype else ["user"],
            tags=list(tag) if tag else None,
            roles=list(role) if role else None,
        )

        rprint(f"[green]✓[/green] User '{username}' created successfully")
        if result.password:
            rprint(f"[yellow]Temporary password:[/yellow] {result.password}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("update")
@click.argument("username")
@click.option("--type", "-t", "utype", multiple=True, help="User type")
@click.option("--group", "-g", multiple=True, help="User group")
@click.option("--tag", multiple=True, help="User tag")
@click.option("--role", "-r", multiple=True, help="User role")
@click.option("--active/--inactive", default=None, help="Set active status")
@click.option("--totp/--no-totp", default=None, help="Enable/disable TOTP")
@pass_config
def update_user(config: Config, username: str, utype: list[str],
                group: list[str], tag: list[str], role: list[str],
                *, active: bool, totp: bool) -> None:
    """Update user details."""
    ensure_auth(config)

    try:
        result = config.client.update_user(
            username=username,
            active=active,
            types=list(utype) if utype else None,
            groups=list(group) if group else None,
            tags=list(tag) if tag else None,
            roles=list(role) if role else None,
            totp_enabled=totp,
        )

        if result.is_success():
            rprint(f"[green]✓[/green] User '{username}' updated successfully")
        else:
            rprint(f"[red]✗[/red] Failed to update user: {result.error}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("delete")
@click.argument("username")
@click.confirmation_option(prompt="Are you sure you want to delete this user?")
@pass_config
def delete_user(config: Config, username: str) -> None:
    """Delete a user."""
    ensure_auth(config)

    try:
        result = config.client.delete_user(username)
        if result.is_success():
            rprint(f"[green]✓[/green] User '{username}' deleted successfully")
        else:
            rprint(f"[red]✗[/red] Failed to delete user: {result.error}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("reset-password")
@click.argument("username")
@pass_config
def reset_password(config: Config, username: str) -> None:
    """Reset user's password."""
    ensure_auth(config)

    try:
        result = config.client.reset_user_password(username)
        if result.is_success():
            rprint(f"[green]✓[/green] Password reset for '{username}'")
            if result.password:
                rprint(f"[yellow]New temporary password:[/yellow] {result.password}")
        else:
            rprint(f"[red]✗[/red] Failed to reset password: {result.error}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Profile Management Commands


@gcli.group()
def profiles() -> None:
    """Profile management commands."""


@profiles.command("list")
@click.option("--filter", "-f", "qfilter", help="Filter by name")
@click.option("--size", "-s", default=25, help="Number of results")
@click.option("--role", "-r", multiple=True, help="Filter by role ID")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def list_profiles(config: Config, qfilter: str, size: int, role: list[str], *, output_json: bool) -> None:
    """List profiles."""
    ensure_auth(config)

    try:
        result = config.client.get_profiles(
            query_filter=qfilter,
            size=size,
            roles=list(role) if role else None,
        )

        if output_json:
            # Convert to dictionary for JSON output (backward compatibility)
            data = {
                "status": result.status,
                "count": result.count,
                "profiles": [profile.to_dict() for profile in result.profiles],
            }
            print(json.dumps(data, indent=2))
        else:
            table = Table(title=f"Profiles (Total: {result.count})")
            table.add_column("Name", style="cyan")
            table.add_column("Group", style="green")
            table.add_column("Daily Quota", style="yellow")
            table.add_column("Priority", style="magenta")
            table.add_column("Services", style="blue")

            for profile in result.profiles:
                table.add_row(
                    profile.name,
                    profile.group,
                    str(profile.daily_quota),
                    str(profile.priority),
                    ", ".join(profile.services),
                )

            console.print(table)
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@profiles.command("get")
@click.argument("name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def get_profile(config: Config, name: str, *, output_json: bool) -> None:
    """Get profile details."""
    ensure_auth(config)

    try:
        profile = config.client.get_profile(name)

        if output_json:
            print(json.dumps(profile.to_dict(), indent=2))
        else:
            rprint(f"[bold]Profile Details: {name}[/bold]")
            rprint(f"Group: {profile.group}")
            rprint(f"Daily Quota: {profile.daily_quota}")
            rprint(f"Priority: {profile.priority}")
            rprint(f"Result TTL: {profile.result_ttl} days")
            rprint(f"Ignore Cache: {'Yes' if profile.ignore_cache else 'No'}")
            rprint(f"Force Dynamic: {'Yes' if profile.force_dynamic else 'No'}")
            rprint(f"Services: {', '.join(profile.services)}")

            if profile.roles:
                rprint(f"Roles: {', '.join(profile.roles)}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@profiles.command("add")
@click.option("--name", "-n", required=True, help="Profile name")
@click.option("--group", "-g", required=True, help="Profile group")
@click.option("--quota", "-q", default=0, help="Daily submission quota (0=unlimited)")
@click.option("--priority", "-p", default=1000, help="Submission priority (500,1000,1500)")
@click.option("--ttl", default=7, help="Result TTL in days")
@click.option("--al-ttl", default=2, help="AL result TTL in days")
@click.option("--service", "-s", multiple=True, help="Allowed service")
@click.option("--role", "-r", multiple=True, help="Profile role")
@click.option("--ignore-cache", is_flag=True, help="Ignore cache")
@click.option("--force-dynamic", is_flag=True, help="Force dynamic analysis")
@pass_config
def add_profile(config: Config, name: str, group: str, quota: int, priority: int, ttl: int, al_ttl: int, \
                service: list[str], role: list[str], *, ignore_cache: bool, force_dynamic: bool) -> None:
    """Add a new profile."""
    ensure_auth(config)

    try:
        result = config.client.add_profile(
            name=name,
            group=group,
            daily_quota=quota,
            priority=priority,
            result_ttl=ttl,
            al_ttl=al_ttl,
            services=list(service) if service else None,
            roles=list(role) if role else None,
            ignore_cache=ignore_cache,
            force_dynamic=force_dynamic,
        )

        if result.is_success():
            rprint(f"[green]✓[/green] Profile '{name}' created successfully")
            if result.token:
                rprint(f"[yellow]Profile token:[/yellow] {result.token}")
        else:
            rprint(f"[red]✗[/red] Failed to create profile: {result.error}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@profiles.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
@pass_config
def delete_profile(config: Config, name: str) -> None:
    """Delete a profile."""
    ensure_auth(config)

    try:
        result = config.client.delete_profile(name)
        if result.is_success():
            rprint(f"[green]✓[/green] Profile '{name}' deleted successfully")
        else:
            rprint(f"[red]✗[/red] Failed to delete profile: {result.error}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Configuration Commands


@gcli.group()
def config_cmd() -> None:
    """Configuration commands."""


@config_cmd.command("roles")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--detect", "detect", is_flag=True, help="Output detect roles")
@pass_config
def show_roles(config: Config, *, output_json: bool, detect: bool) -> None:
    """Show available roles."""
    ensure_auth(config)

    try:
        result = config.client.get_roles_detect() if detect else config.client.get_roles_expert()

        if output_json:
            # Convert to dictionary for JSON output (backward compatibility)
            data = {
                "status": result.status,
                "roles": [role.__dict__ for role in result.roles],
                "technical_roles": [role.__dict__ for role in result.technical_roles],
            }
            print(json.dumps(data, indent=2))
        else:
            rprint("[bold]Roles:[/bold]")
            for role in result.roles:
                rprint(f"  • {role.id}: {role.label}")
                rprint(f"    {role.description}")

            rprint("\n[bold]Technical Roles:[/bold]")
            for role in result.technical_roles:
                rprint(f"  • {role.id}: {role.label}")
                rprint(f"    {role.description}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@config_cmd.command("permissions")
@click.argument("type", type=click.Choice(["detect", "expert"]))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@remap_params(type="ptype")
@pass_config
def show_permissions(config: Config, ptype: str, *, output_json: bool) -> None:
    """Show available permissions."""
    ensure_auth(config)

    try:
        result = config.client.get_permissions_detect() if ptype == "detect" \
            else config.client.get_permissions_expert()

        if output_json:
            # Convert to dictionary for JSON output (backward compatibility)
            data = {
                "status": result.status,
                "permissions": {k: v.__dict__ for k, v in result.permissions.items()},
            }
            print(json.dumps(data, indent=2))
        else:
            rprint(f"[bold]{ptype.title()} Permissions:[/bold]")
            for perm_id, perm in result.permissions.items():
                rprint(f"  • {perm_id}: {perm.label}")
                rprint(f"    {perm.description}")
                if perm.require_global_access:
                    rprint("    [yellow]Requires global access[/yellow]")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Service Management Commands


@gcli.group()
def services() -> None:
    """Service management commands."""


@services.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def list_services(config: Config, *, output_json: bool) -> None:
    """List available services."""
    ensure_auth(config)

    try:
        result = config.client.get_services()

        if output_json:
            # Convert to dictionary for JSON output (backward compatibility)
            data = {
                "status": result.status,
                "services": [service.__dict__ for service in result.services],
            }
            print(json.dumps(data, indent=2))
        else:
            table = Table(title="Services")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Enabled", style="yellow")
            table.add_column("Category", style="magenta")
            table.add_column("Stage", style="blue")

            for service in result.services:
                table.add_row(
                    service.name,
                    service.version,
                    "✓" if service.enabled else "✗",
                    service.category,
                    service.stage,
                )

            console.print(table)
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    gcli()
