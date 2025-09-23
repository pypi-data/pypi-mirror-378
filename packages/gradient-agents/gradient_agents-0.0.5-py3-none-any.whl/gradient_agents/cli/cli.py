from __future__ import annotations
from typing import Optional
import typer

from .agent import (
    AgentConfigService,
    LaunchService,
    DeployService,
    ConfigReader,
    YamlAgentConfigService,
    DirectLaunchService,
    YamlConfigReader,
    MockDeployService,
    get_do_api_token,
    EnvironmentError,
)

_agent_config_service = YamlAgentConfigService()
_launch_service = DirectLaunchService()
_config_reader = YamlConfigReader()
_deploy_service = MockDeployService(_config_reader)

app = typer.Typer(no_args_is_help=True, add_completion=False, help="gradient CLI")

agent_app = typer.Typer(
    no_args_is_help=True,
    help="Agent configuration and management",
)
app.add_typer(agent_app, name="agent")


def get_agent_config_service() -> AgentConfigService:
    return _agent_config_service


def get_launch_service() -> LaunchService:
    return _launch_service


def get_deploy_service() -> DeployService:
    return _deploy_service


def get_config_reader() -> ConfigReader:
    return _config_reader


@agent_app.command("init")
def agent_init(
    agent_name: Optional[str] = typer.Option(
        None, "--agent-name", help="Name of the agent"
    ),
    agent_environment: Optional[str] = typer.Option(
        None, "--agent-environment", help="Agent environment name"
    ),
    entrypoint_file: Optional[str] = typer.Option(
        None,
        "--entrypoint-file",
        help="Python file containing @entrypoint decorated function",
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Interactive prompt mode"
    ),
):
    agent_config_service = get_agent_config_service()
    agent_config_service.configure(
        agent_name=agent_name,
        agent_environment=agent_environment,
        entrypoint_file=entrypoint_file,
        interactive=interactive,
    )


@agent_app.command("run")
def agent_run():
    launch_service = get_launch_service()
    launch_service.launch_locally()


@agent_app.command("deploy")
def agent_deploy(
    api_token: Optional[str] = typer.Option(
        None,
        "--api-token",
        help="DigitalOcean API token (overrides DO_API_TOKEN env var)",
        envvar="DO_API_TOKEN",
        hide_input=True,
    )
):
    """Deploy the agent to DigitalOcean."""
    try:
        # Get the token from environment or command line argument
        token = get_do_api_token(token_override=api_token, required=True)
        typer.echo(f"Using API token: {token[:8]}...")

        # Deploy the agent
        deploy_service = get_deploy_service()
        deploy_service.deploy_agent()

    except EnvironmentError as e:
        typer.echo(f"❌ {e}", err=True)
        typer.echo("\nTo set your token permanently:", err=True)
        typer.echo("  export DO_API_TOKEN=your_token_here", err=True)
        raise typer.Exit(1)


@agent_app.command("traces")
def agent_traces(
    action: str = typer.Argument(help="Action to perform: list, create, get, delete"),
    trace_id: Optional[str] = typer.Argument(
        None, help="Trace ID (required for get/delete actions)"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="Name for new trace (create action)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Description for new trace (create action)"
    ),
    limit: int = typer.Option(
        10, "--limit", help="Number of traces to list (list action)"
    ),
    api_token: Optional[str] = typer.Option(
        None,
        "--api-token",
        help="DigitalOcean API token (overrides DO_API_TOKEN env var)",
        envvar="DO_API_TOKEN",
        hide_input=True,
    ),
):
    """Manage Galileo traces via DigitalOcean API."""
    import asyncio
    from .agent.api import ApiServiceFactory, TraceRequest

    async def run_traces_command():
        try:
            # Get the token from environment or command line argument
            token = get_do_api_token(token_override=api_token, required=True)

            # Create the traces service
            traces_service = ApiServiceFactory.create_digitalocean_traces_service(token)

            try:
                if action == "list":
                    typer.echo(f"Fetching {limit} traces...")
                    traces = await traces_service.list_traces(limit=limit)

                    if not traces:
                        typer.echo("No traces found.")
                        return

                    typer.echo(f"\nFound {len(traces)} traces:")
                    for trace in traces:
                        typer.echo(
                            f"  {trace.id} - {trace.name} ({trace.status.value})"
                        )
                        if trace.description:
                            typer.echo(f"    {trace.description}")

                elif action == "create":
                    if not name:
                        name = typer.prompt("Enter trace name")

                    trace_request = TraceRequest(
                        name=name,
                        description=description or "",
                        metadata={"created_via": "gradient_cli"},
                        tags=["gradient", "cli"],
                    )

                    typer.echo(f"Creating trace '{name}'...")
                    new_trace = await traces_service.create_trace(trace_request)
                    typer.echo(f"✅ Created trace: {new_trace.id}")
                    typer.echo(f"   Name: {new_trace.name}")
                    typer.echo(f"   Status: {new_trace.status.value}")

                elif action == "get":
                    if not trace_id:
                        trace_id = typer.prompt("Enter trace ID")

                    typer.echo(f"Fetching trace {trace_id}...")
                    trace = await traces_service.get_trace(trace_id)

                    if trace:
                        typer.echo(f"✅ Trace found:")
                        typer.echo(f"   ID: {trace.id}")
                        typer.echo(f"   Name: {trace.name}")
                        typer.echo(f"   Status: {trace.status.value}")
                        typer.echo(f"   Description: {trace.description}")
                        if trace.tags:
                            typer.echo(f"   Tags: {', '.join(trace.tags)}")
                    else:
                        typer.echo(f"❌ Trace {trace_id} not found")

                elif action == "delete":
                    if not trace_id:
                        trace_id = typer.prompt("Enter trace ID")

                    # Confirm deletion
                    if typer.confirm(
                        f"Are you sure you want to delete trace {trace_id}?"
                    ):
                        typer.echo(f"Deleting trace {trace_id}...")
                        success = await traces_service.delete_trace(trace_id)

                        if success:
                            typer.echo(f"✅ Trace {trace_id} deleted successfully")
                        else:
                            typer.echo(f"❌ Failed to delete trace {trace_id}")
                    else:
                        typer.echo("Deletion cancelled.")

                else:
                    typer.echo(f"❌ Unknown action: {action}")
                    typer.echo("Available actions: list, create, get, delete")
                    raise typer.Exit(1)

            finally:
                # Always clean up HTTP resources
                await traces_service.http_client.close()

        except EnvironmentError as e:
            typer.echo(f"❌ {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"❌ Error: {e}", err=True)
            raise typer.Exit(1)

    # Run the async function
    try:
        asyncio.run(run_traces_command())
    except KeyboardInterrupt:
        typer.echo("\n❌ Operation cancelled by user", err=True)
        raise typer.Exit(1)


def run():
    app()
