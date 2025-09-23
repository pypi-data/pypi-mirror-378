"""Agent management commands."""
import click
from typing import Optional, List

# Import Rich formatting
from engine_cli.formatting import success, error, header, key_value


@click.group()
def cli():
    """Manage AI agents."""
    pass


@cli.command()
@click.argument("name")
@click.option("--model", default="claude-3.5-sonnet", help="AI model to use")
@click.option("--speciality", help="Agent speciality")
@click.option("--stack", multiple=True, help="Technology stack (can be used multiple times)")
def create(name, model, speciality, stack):
    """Create a new AI agent."""
    try:
        from engine_core.core.agents.agent_builder import AgentBuilder

        builder = AgentBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)
        builder = builder.with_model(model)

        if speciality:
            builder = builder.with_speciality(speciality)

        if stack:
            builder = builder.with_stack(list(stack))

        agent = builder.build()

        success(f"Agent '{name}' created successfully!")

        # Display agent details
        agent_info = {
            "ID": name,
            "Name": name,
            "Model": model,
        }

        if speciality:
            agent_info["Speciality"] = speciality

        if stack:
            agent_info["Stack"] = ', '.join(stack)

        key_value(agent_info, "Agent Details")

    except ImportError:
        error("Engine Core not available. Please install engine-core first.")
    except Exception as e:
        error(f"Error creating agent: {e}")


@cli.command()
def list():
    """List all agents."""
    try:
        # TODO: Implement agent listing from database/storage
        click.echo("⚠ Agent listing not yet implemented")
        click.echo("This will list all created agents from the database")

    except Exception as e:
        click.echo(f"✗ Error listing agents: {e}")


@cli.command()
@click.argument("name")
def show(name):
    """Show details of a specific agent."""
    try:
        # TODO: Implement agent details retrieval
        click.echo(f"⚠ Agent details for '{name}' not yet implemented")
        click.echo("This will show detailed information about the specified agent")

    except Exception as e:
        click.echo(f"✗ Error showing agent: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete an agent."""
    try:
        if not force:
            click.echo(f"⚠ This will delete agent '{name}'. Use --force to confirm.")
            return

        # TODO: Implement agent deletion
        click.echo(f"⚠ Agent deletion not yet implemented")

    except Exception as e:
        click.echo(f"✗ Error deleting agent: {e}")
