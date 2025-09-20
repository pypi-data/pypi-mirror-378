"""Command line interface for MLOX.

This rewrite exposes a higher level interface for managing projects,
servers and services in preparation for a server/client architecture.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, List

import typer

from mlox.session import MloxSession
from mlox.config import (
    get_stacks_path,
    load_config,
    load_all_service_configs,
    load_all_server_configs,
    load_service_config_by_id,
)
from mlox.utils import dataclass_to_dict, save_to_json


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


app = typer.Typer(help="MLOX command line interface", no_args_is_help=True)

project_app = typer.Typer(help="Manage MLOX projects")
server_app = typer.Typer(help="Manage servers in the project infrastructure")
service_app = typer.Typer(help="Manage services running on servers")

# New nested groups for configs under server and service
server_configs_app = typer.Typer(help="Server configuration templates")
service_configs_app = typer.Typer(help="Service configuration templates")

app.add_typer(project_app, name="project")
app.add_typer(server_app, name="server")
app.add_typer(service_app, name="service")

# Attach configs namespace under existing groups
server_app.add_typer(server_configs_app, name="configs")
service_app.add_typer(service_configs_app, name="configs")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_session(project: str, password: str) -> MloxSession:
    """Load an existing :class:`MloxSession` from credentials."""
    try:
        session = MloxSession(project, password)
    except Exception as exc:  # pragma: no cover - defensive
        # If the exception looks like an exit (has exit_code or is SystemExit), re-raise
        if hasattr(exc, "exit_code") or isinstance(exc, SystemExit):
            raise
        typer.echo(f"[ERROR] Failed to load session: {exc}", err=True)
        raise typer.Exit(code=1)

    # Check secret manager health outside the try/except so Typer Exit codes
    # raised here are not accidentally caught by the broader exception handler.
    if session.secrets and not session.secrets.is_working():
        typer.echo(
            "[ERROR] Could not initialize session (secrets not working)",
            err=True,
        )
        raise typer.Exit(code=2)

    return session


def parse_kv(pairs: List[str]) -> Dict[str, str]:
    """Convert a list of ``KEY=VALUE`` strings into a dictionary."""

    data: Dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        data[key] = value
    return data


def _load_config_from_path(path: str):
    """Load a configuration file relative to the stacks directory."""

    stacks = get_stacks_path()
    service_dir, candidate = os.path.split(path)
    return load_config(stacks, service_dir, candidate)


# ---------------------------------------------------------------------------
# Project commands
# ---------------------------------------------------------------------------


@project_app.command("new")
def project_new(
    name: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
):
    ms = MloxSession(project_name=name, password=password)
    if not ms:
        typer.echo("[ERROR] Failed to initialise project", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Created project '{name}'.")


# ---------------------------------------------------------------------------
# Server commands
# ---------------------------------------------------------------------------


@server_app.command("list")
def server_list(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
):
    """List all servers registered in the project infrastructure."""

    session = get_session(project, password)
    if not session.infra.bundles:
        typer.echo("No servers found.")
        raise typer.Exit()

    for bundle in session.infra.bundles:
        typer.echo(
            f"{bundle.server.ip} ({bundle.server.state}) - {len(bundle.services)} services"
        )


@server_app.command("add")
def server_add(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    server_template: str = typer.Option(
        ..., help="Server template path relative to the stacks directory"
    ),
    ip: str = typer.Option(..., help="IP or hostname of the server"),
    port: int = typer.Option(22, help="SSH port of the server"),
    root_user: str = typer.Option("root", help="Initial root user"),
    root_pw: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Root password"
    ),
    param: List[str] = typer.Option(
        [], "--param", help="Additional template parameter in the form KEY=VALUE"
    ),
):
    """Register a new server in the current project."""

    session = get_session(project, password)
    config = _load_config_from_path("ubuntu/mlox-server." + server_template + ".yaml")
    # treat an empty dict as a valid config; only None means not found
    if config is None:
        typer.echo("[ERROR] Server template not found", err=True)
        raise typer.Exit(code=1)

    params = {
        "${MLOX_IP}": ip,
        "${MLOX_PORT}": str(port),
        "${MLOX_ROOT}": root_user,
        "${MLOX_ROOT_PW}": root_pw,
    }
    params.update(parse_kv(param))

    bundle = session.infra.add_server(config=config, params=params)
    if not bundle:
        typer.echo("[ERROR] Failed to add server", err=True)
        raise typer.Exit(code=1)

    session.save_infrastructure()
    typer.echo(f"Added server {ip}")


@server_app.command("setup")
def server_setup(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    ip: str = typer.Argument(..., help="Server IP or hostname"),
):
    """Run the setup routine on a server."""

    session = get_session(project, password)
    bundle = session.infra.get_bundle_by_ip(ip)
    if not bundle:
        typer.echo("[ERROR] Server not found", err=True)
        raise typer.Exit(code=1)
    bundle.server.setup()
    session.save_infrastructure()
    typer.echo(f"Server {ip} set up")


@server_app.command("teardown")
def server_teardown(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    ip: str = typer.Argument(..., help="Server IP or hostname"),
):
    """Tear down a server and remove it from the infrastructure."""

    session = get_session(project, password)
    bundle = session.infra.get_bundle_by_ip(ip)
    if not bundle:
        typer.echo("[ERROR] Server not found", err=True)
        raise typer.Exit(code=1)
    bundle.server.teardown()
    session.infra.remove_bundle(bundle)
    session.save_infrastructure()
    typer.echo(f"Server {ip} removed")


@server_app.command("save-key")
def server_save_key(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    ip: str = typer.Argument(..., help="Server IP or hostname"),
    output: str = typer.Option(
        ...,
        help="Path to store the encrypted key file",
    ),
):
    """Save a server key file for local access."""

    session = get_session(project, password)
    bundle = session.infra.get_bundle_by_ip(ip)
    if not bundle:
        typer.echo("[ERROR] Server not found", err=True)
        raise typer.Exit(code=1)
    server_dict = dataclass_to_dict(bundle.server)
    save_to_json(server_dict, output, password, True)
    typer.echo(f"Saved key for {ip} to {output}")


# ---------------------------------------------------------------------------
# Service commands
# ---------------------------------------------------------------------------


@service_app.command("list")
def service_list(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
):
    """List services across all servers in the project."""

    session = get_session(project, password)
    found = False
    for bundle in session.infra.bundles:
        for svc in bundle.services:
            typer.echo(f"{svc.name} ({svc.service_config_id}) on {bundle.server.ip}")
            found = True
    if not found:
        typer.echo("No services found.")


@service_app.command("add")
def service_add(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    server_ip: str = typer.Option(..., help="IP of the target server"),
    template_id: str = typer.Option(..., help="Service template ID"),
    param: List[str] = typer.Option(
        [], "--param", help="Additional template parameter in the form KEY=VALUE"
    ),
):
    """Add a new service to an existing server."""

    session = get_session(project, password)
    config = load_service_config_by_id(template_id)
    if not config:
        typer.echo("[ERROR] Service template not found", err=True)
        raise typer.Exit(code=1)

    params = parse_kv(param)
    bundle = session.infra.add_service(server_ip, config, params)
    if not bundle:
        typer.echo("[ERROR] Failed to add service", err=True)
        raise typer.Exit(code=1)

    session.save_infrastructure()
    svc = bundle.services[-1]
    typer.echo(f"Added service {svc.name} to {server_ip}")


@service_app.command("setup")
def service_setup(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    name: str = typer.Argument(..., help="Service name"),
):
    """Run the setup routine for a service."""

    session = get_session(project, password)
    svc = session.infra.get_service(name)
    if not svc:
        typer.echo("[ERROR] Service not found", err=True)
        raise typer.Exit(code=1)
    session.infra.setup_service(svc)
    session.save_infrastructure()
    typer.echo(f"Service {name} set up")


@service_app.command("teardown")
def service_teardown(
    project: str = typer.Argument(..., help="Project name"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the session"
    ),
    name: str = typer.Argument(..., help="Service name"),
):
    """Remove a service from the infrastructure."""

    session = get_session(project, password)
    svc = session.infra.get_service(name)
    if not svc:
        typer.echo("[ERROR] Service not found", err=True)
        raise typer.Exit(code=1)
    session.infra.teardown_service(svc)
    session.save_infrastructure()
    typer.echo(f"Service {name} removed")


# ---------------------------------------------------------------------------
# Configs commands (nested under server and service)
# ---------------------------------------------------------------------------


@server_configs_app.command("list")
def server_configs_list():
    """List available server configuration templates."""

    configs = load_all_server_configs()
    if not configs:
        typer.echo("No server configs found.")
        return
    for cfg in configs:
        typer.echo(f"{cfg.id} - {cfg.path}")


@service_configs_app.command("list")
def service_configs_list():
    """List available service configuration templates."""

    configs = load_all_service_configs()
    if not configs:
        typer.echo("No service configs found.")
        return
    for cfg in configs:
        typer.echo(f"{cfg.id} - {cfg.path}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app()
