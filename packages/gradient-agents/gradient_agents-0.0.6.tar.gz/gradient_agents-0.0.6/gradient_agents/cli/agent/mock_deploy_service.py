"""Mock deployment service implementation."""

from __future__ import annotations
import time
import uuid
import typer

from .deploy_service import DeployService
from ..config.config_reader import ConfigReader


class MockDeployService(DeployService):
    """Mock implementation of deployment service for testing."""

    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader

    def deploy_agent(self) -> None:
        """Deploy the agent to the configured environment (mocked)."""
        try:
            agent_name = self.config_reader.get_agent_name()
            agent_environment = self.config_reader.get_agent_environment()

            typer.echo(f"🚀 Initiating deployment for agent: {agent_name}")
            typer.echo(f"🎯 Target environment: {agent_environment}")

            # Mock deployment process with progress
            typer.echo("📦 Preparing deployment package...")
            time.sleep(1)

            typer.echo("⬆️  Uploading agent code...")
            time.sleep(2)

            typer.echo("⚙️  Configuring environment...")
            time.sleep(1)

            # Show continuous deploying messages
            typer.echo("🔄 Deploying...")
            for i in range(8):  # Show deploying for about 8 seconds
                time.sleep(1)
                typer.echo("   Deploying...")

            typer.echo("✅ Verifying deployment...")
            time.sleep(1)

            # Generate a UUID for the agent deployment
            agent_uuid = str(uuid.uuid4())

            typer.echo("🎉 Agent deployment completed successfully!")
            typer.echo(
                f"🏃 Agent '{agent_name}' is now running in '{agent_environment}' environment"
            )
            typer.echo()
            typer.echo("📡 Agent endpoint:")
            typer.echo(f"   https://agents.do-ai.run/{agent_uuid}/{agent_environment}")

        except Exception as e:
            typer.echo(f"❌ Deployment failed: {e}", err=True)
            raise typer.Exit(1)
