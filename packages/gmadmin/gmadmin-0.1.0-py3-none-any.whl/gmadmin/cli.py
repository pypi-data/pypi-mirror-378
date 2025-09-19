#!/usr/bin/env python3
"""
GLIMPS Admin CLI Tool.

A command-line interface for the GLIMPS Admin API using Click.
"""

import json
import os
import sys
from datetime import datetime
from typing import List

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .client import GlimpsAdminClient
from .config import Config, get_config, save_config
from .responses import local_tz


console = Console()
pass_config = click.make_pass_decorator(Config, ensure=True)


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
    default=os.getenv("GLIMPS_ADMIN_URL", "https://gmalware.glimps.re"),
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
    prompt_required=os.getenv("GLIMPS_ADMIN_LOGIN") is None,
    help="Admin login",
    default=os.getenv("GLIMPS_ADMIN_LOGIN"),
)
@click.option(
    "--password",
    prompt=True,
    prompt_required=os.getenv("GLIMPS_ADMIN_PASSWORD") is None,
    hide_input=True,
    help="Admin password",
)
@click.option("--totp", help="TOTP code for 2FA")
@pass_config
def login(config: Config, login: str, password: str, totp: str) -> None:
    """Login to GLIMPS Admin API."""
    try:
        if password is None:
            password = os.getenv("GLIMPS_ADMIN_PASSWORD")
        result = config.client.login(login, password, totp)
        config.login = login
        config.token = result["token"]
        config.expiry = result["validity"]
        config.password = password
        save_config(config)

        rprint(f"[green]✓[/green] Successfully logged in as {login}")
        if "validity" in result:
            expiry = datetime.fromtimestamp(result["validity"] / 1000, tz=local_tz)
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
@click.option("--filter", "-f", help="Filter by name/username")
@click.option("--size", "-s", default=25, help="Number of results")
@click.option("--type", "-t", multiple=True, help="Filter by user type (user/admin)")
@click.option("--group", "-g", multiple=True, help="Filter by group")
@click.option("--tag", multiple=True, help="Filter by tag")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def list_users(config: Config, qfilter: str, size: int, utype: List[str],
               group: List[str], tag: List[str], *, output_json: bool) -> None:
    """List users."""
    ensure_auth(config)

    try:
        result = config.client.get_users(
            filter=qfilter,
            size=size,
            types=list(utype) if utype else None,
            groups=list(group) if group else None,
            tags=list(tag) if tag else None,
        )

        if output_json:
            print(json.dumps(result, indent=2))
        else:
            table = Table(title=f"Users (Total: {result['count']})")
            table.add_column("Username", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Active", style="yellow")
            table.add_column("Types", style="magenta")
            table.add_column("Groups", style="blue")

            for user in result.get("users", []):
                table.add_row(
                    user.get("username", ""),
                    user.get("name", ""),
                    "✓" if user.get("active") else "✗",
                    ", ".join(user.get("types", [])),
                    ", ".join(user.get("groups", [])),
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
            print(json.dumps(user, indent=2))
        else:
            rprint(f"[bold]User Details: {username}[/bold]")
            rprint(f"Name: {user.get('name', 'N/A')}")
            rprint(f"Active: {'Yes' if user.get('active') else 'No'}")
            rprint(f"Types: {', '.join(user.get('types', []))}")
            rprint(f"Groups: {', '.join(user.get('groups', []))}")
            rprint(f"Tags: {', '.join(user.get('tags', []))}")
            rprint(f"TOTP Enabled: {'Yes' if user.get('totp_enabled') else 'No'}")

            if user.get("roles"):
                rprint(f"Roles: {', '.join(user['roles'])}")

            if user.get("permissions"):
                rprint("[bold]Permissions:[/bold]")
                for key, value in user["permissions"].items():
                    rprint(f"  {key}: {value}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("add")
@click.option("--username", "-u", required=True, help="Username (email)")
@click.option("--name", "-n", required=True, help="Display name")
@click.option("--group", "-g", required=True, multiple=True, help="User group (at least one)")
@click.option("--type", "-t", multiple=True, help="User type (user/admin)")
@click.option("--tag", multiple=True, help="User tag")
@click.option("--role", "-r", multiple=True, help="User role")
@click.option("--inactive", is_flag=True, help="Create as inactive")
@pass_config
def add_user(config: Config, username: str, name: str, group: List[str],
             utype: List[str], tag: List[str], role: List[str], *,
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
        if "password" in result:
            rprint(f"[yellow]Temporary password:[/yellow] {result['password']}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@users.command("update")
@click.argument("username")
@click.option("--type", "-t", multiple=True, help="User type")
@click.option("--group", "-g", multiple=True, help="User group")
@click.option("--tag", multiple=True, help="User tag")
@click.option("--role", "-r", multiple=True, help="User role")
@click.option("--active/--inactive", default=None, help="Set active status")
@click.option("--totp/--no-totp", default=None, help="Enable/disable TOTP")
@pass_config
def update_user(config: Config, username: str, utype: List[str],
                group: List[str], tag: List[str], role: List[str],
                *, active: bool, totp: bool) -> None:
    """Update user details."""
    ensure_auth(config)

    try:
        config.client.update_user(
            username=username,
            active=active,
            types=list(utype) if utype else None,
            groups=list(group) if group else None,
            tags=list(tag) if tag else None,
            roles=list(role) if role else None,
            totp_enabled=totp,
        )

        rprint(f"[green]✓[/green] User '{username}' updated successfully")
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
        config.client.delete_user(username)
        rprint(f"[green]✓[/green] User '{username}' deleted successfully")
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
        rprint(f"[green]✓[/green] Password reset for '{username}'")
        if "password" in result:
            rprint(f"[yellow]New temporary password:[/yellow] {result['password']}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


# Profile Management Commands


@gcli.group()
def profiles() -> None:
    """Profile management commands."""


@profiles.command("list")
@click.option("--filter", "-f", help="Filter by name")
@click.option("--size", "-s", default=25, help="Number of results")
@click.option("--role", "-r", multiple=True, help="Filter by role ID")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def list_profiles(config: Config, qfilter: str, size: int, role: List[str], *, output_json: bool) -> None:
    """List profiles."""
    ensure_auth(config)

    try:
        result = config.client.get_profiles(
            filter=qfilter,
            size=size,
            roles=list(role) if role else None,
        )

        if output_json:
            print(json.dumps(result, indent=2))
        else:
            table = Table(title=f"Profiles (Total: {result['count']})")
            table.add_column("Name", style="cyan")
            table.add_column("Group", style="green")
            table.add_column("Daily Quota", style="yellow")
            table.add_column("Priority", style="magenta")
            table.add_column("Services", style="blue")

            for profile in result.get("profiles", []):
                table.add_row(
                    profile.get("name", ""),
                    profile.get("group", ""),
                    str(profile.get("daily_quota", 0)),
                    str(profile.get("priority", 0)),
                    ", ".join(profile.get("services", [])),
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
            print(json.dumps(profile, indent=2))
        else:
            rprint(f"[bold]Profile Details: {name}[/bold]")
            rprint(f"Group: {profile.get('group', 'N/A')}")
            rprint(f"Daily Quota: {profile.get('daily_quota', 0)}")
            rprint(f"Priority: {profile.get('priority', 0)}")
            rprint(f"Result TTL: {profile.get('result_ttl', 365)} days")
            rprint(f"Ignore Cache: {'Yes' if profile.get('ignore_cache') else 'No'}")
            rprint(f"Force Dynamic: {'Yes' if profile.get('force_dynamic') else 'No'}")
            rprint(f"Services: {', '.join(profile.get('services', []))}")

            if profile.get("roles"):
                rprint(f"Roles: {', '.join(profile['roles'])}")
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
                service: List[str], role: List[str], *, ignore_cache: bool, force_dynamic: bool) -> None:
    """Add a new profile."""
    ensure_auth(config)

    try:
        config.client.add_profile(
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

        rprint(f"[green]✓[/green] Profile '{name}' created successfully")
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
        config.client.delete_profile(name)
        rprint(f"[green]✓[/green] Profile '{name}' deleted successfully")
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
            print(json.dumps(result, indent=2))
        else:
            rprint("[bold]Roles:[/bold]")
            for role in result.get("roles", []):
                rprint(f"  • {role['id']}: {role['label']}")
                rprint(f"    {role['description']}")

            rprint("\n[bold]Technical Roles:[/bold]")
            for role in result.get("technical_roles", []):
                rprint(f"  • {role['id']}: {role['label']}")
                rprint(f"    {role['description']}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@config_cmd.command("permissions")
@click.argument("type", type=click.Choice(["detect", "expert"]))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@pass_config
def show_permissions(config: Config, ptype: str, *, output_json: bool) -> None:
    """Show available permissions."""
    ensure_auth(config)

    try:
        result = config.client.get_permissions_detect() if ptype == "detect" \
            else config.client.get_permissions_expert()

        if output_json:
            print(json.dumps(result, indent=2))
        else:
            rprint(f"[bold]{ptype.title()} Permissions:[/bold]")
            for perm_id, perm in result.get("permissions", {}).items():
                rprint(f"  • {perm_id}: {perm.get('label', '')}")
                rprint(f"    {perm.get('description', '')}")
                if perm.get("require_global_access"):
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
            print(json.dumps(result, indent=2))
        else:
            table = Table(title="Services")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Enabled", style="yellow")
            table.add_column("Category", style="magenta")
            table.add_column("Stage", style="blue")

            for service in result.get("services", []):
                table.add_row(
                    service.get("name", ""),
                    service.get("version", ""),
                    "✓" if service.get("enabled") else "✗",
                    service.get("category", ""),
                    service.get("stage", ""),
                )

            console.print(table)
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@services.command("enable")
@click.argument("service_name")
@pass_config
def enable_service(config: Config, service_name: str) -> None:
    """Enable a service."""
    ensure_auth(config)

    try:
        config.client.update_service(service_name, enabled=True)
        rprint(f"[green]✓[/green] Service '{service_name}' enabled")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


@services.command("disable")
@click.argument("service_name")
@pass_config
def disable_service(config: Config, service_name: str) -> None:
    """Disable a service."""
    ensure_auth(config)

    try:
        config.client.update_service(service_name, enabled=False)
        rprint(f"[green]✓[/green] Service '{service_name}' disabled")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    gcli()
