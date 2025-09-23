"""Direct FastAPI launch service implementation."""

from __future__ import annotations
import importlib
import sys
from pathlib import Path
import typer
import yaml

from .launch_service import LaunchService


class DirectLaunchService(LaunchService):
    """Direct FastAPI implementation of launch service."""

    def __init__(self):
        self.config_dir = Path.cwd() / ".gradient"
        self.config_file = self.config_dir / "agent.yml"

    def launch_locally(self) -> None:
        """Launch the agent locally using FastAPI server."""
        config = self._load_config()
        entrypoint_file = config.get("entrypoint_file")
        agent_name = config.get("agent_name", "gradient-agent")

        if not entrypoint_file:
            typer.echo(
                "Error: No entrypoint file specified in configuration.", err=True
            )
            raise typer.Exit(1)

        self._validate_entrypoint_file(entrypoint_file)
        self._import_entrypoint_module(entrypoint_file)
        self._start_server(agent_name)

    def _load_config(self) -> dict:
        """Load agent configuration from YAML file."""
        if not self.config_file.exists():
            typer.echo("Error: No agent configuration found.", err=True)
            typer.echo(
                "Please run 'gradient agent init' first to set up your agent.", err=True
            )
            raise typer.Exit(1)

        try:
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            typer.echo(f"Error reading agent configuration: {e}", err=True)
            raise typer.Exit(1)

    def _validate_entrypoint_file(self, entrypoint_file: str) -> None:
        """Validate that the entrypoint file exists."""
        entrypoint_path = Path.cwd() / entrypoint_file
        if not entrypoint_path.exists():
            typer.echo(
                f"Error: Entrypoint file '{entrypoint_file}' does not exist.",
                err=True,
            )
            raise typer.Exit(1)

    def _import_entrypoint_module(self, entrypoint_file: str) -> None:
        """Import the entrypoint module to register the @entrypoint function."""
        try:
            current_dir = str(Path.cwd())
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            module_name = (
                entrypoint_file.replace(".py", "").replace("/", ".").replace("\\", ".")
            )
            typer.echo(f"Importing module: {module_name}")
            importlib.import_module(module_name)

        except ImportError as e:
            error_msg = str(e)
            typer.echo(
                f"Error: Error importing entrypoint module '{entrypoint_file}': {error_msg}",
                err=True,
            )
            self._show_import_help()
            raise typer.Exit(1)

    def _start_server(self, agent_name: str) -> None:
        """Start the FastAPI server."""
        typer.echo(f"Starting {agent_name} server...")
        typer.echo("Server will be accessible at http://localhost:8080")
        typer.echo("Press Ctrl+C to stop the server")

        try:
            from gradient_agents import run_server

            run_server(host="0.0.0.0", port=8080)
        except ImportError:
            typer.echo(
                "Error: gradient_agents package not found.",
                err=True,
            )
            typer.echo(
                "Please install it with: pip install gradient-agents",
                err=True,
            )
            raise typer.Exit(1)

    def _show_import_help(self) -> None:
        """Show help for import errors."""
        typer.echo(
            "Please install the gradient-agents package and ensure imports are correct:",
            err=True,
        )
        typer.echo("  pip install gradient-agents", err=True)
        typer.echo("  from gradient_agents import entrypoint", err=True)
