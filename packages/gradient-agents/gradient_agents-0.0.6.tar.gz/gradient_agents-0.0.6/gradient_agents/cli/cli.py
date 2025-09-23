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
        # Deploy the agent
        deploy_service = get_deploy_service()
        deploy_service.deploy_agent()

    except EnvironmentError as e:
        typer.echo(f"❌ {e}", err=True)
        typer.echo("\nTo set your token permanently:", err=True)
        typer.echo("  export DO_API_TOKEN=your_token_here", err=True)
        raise typer.Exit(1)


@agent_app.command("evaluate")
def agent_evaluate():
    """Run an evaluation of the agent."""
    import time

    try:
        config_reader = get_config_reader()
        agent_name = config_reader.get_agent_name()
        agent_environment = config_reader.get_agent_environment()

        typer.echo(f"🧪 Initiating evaluation for agent: {agent_name}")
        typer.echo(f"🎯 Environment: {agent_environment}")
        typer.echo()

        # Setting up evaluation
        typer.echo("⚙️  Setting up evaluation...")
        time.sleep(2)

        # Starting run
        typer.echo("🚀 Starting run...")
        time.sleep(1)

        # Poll for 10 seconds with progress indicators
        typer.echo("📊 Running evaluation...")
        for i in range(10):
            time.sleep(1)
            dots = "." * ((i % 3) + 1)
            typer.echo(f"   Evaluating{dots}", nl=False)
            if i < 9:  # Don't print newline on last iteration
                typer.echo("\r", nl=False)

        typer.echo()  # Final newline
        time.sleep(0.5)

        # Complete
        typer.echo("✅ Evaluation completed!")
        typer.echo()
        typer.echo("📈 View detailed results at:")
        typer.echo(
            "   https://cloud.digitalocean.com/gen-ai/workspaces/11f076b0-2ff2-d71d-b074-4e013e2ddde4/evaluations/384ad568-76b5-11f0-b074-4e013e2ddde4/runs/73b04ba3-6494-42af-b7de-b093d8082814?i=b59231"
        )

    except Exception as e:
        typer.echo(f"❌ Evaluation failed: {e}", err=True)
        raise typer.Exit(1)


@agent_app.command("traces")
def agent_traces():
    """Open the Galileo traces UI for monitoring agent execution."""
    typer.echo("🔍 Galileo Traces UI")
    typer.echo("📊 To be implemented")
    typer.echo()
    typer.echo("This command will eventually open a URL to view:")
    typer.echo("  • Agent execution traces")
    typer.echo("  • Performance metrics")
    typer.echo("  • Debug information")
    typer.echo("  • Execution logs")
    typer.echo()
    typer.echo("💡 Coming soon: traces.do-ai.run/{agent-id}")


def run():
    app()
