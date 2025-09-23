#!/usr/bin/env python3
"""
Command-line interface for the HeySol API client.

This CLI provides access to HeySol API functionality including memory management,
space operations, user profile, and search capabilities.
"""

import sys
from pathlib import Path

import click

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .logs import logs
from .memory import memory
from .profile import profile
from .spaces import spaces
from .tools import tools
from .webhooks import webhooks


@click.group()
@click.option("--api-key", help="HeySol API key (overrides environment variable)")
@click.option("--base-url", help="Base URL for API (overrides default)")
@click.option("--source", help="Source identifier (overrides default)")
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option("--skip-mcp", is_flag=True, help="Skip MCP initialization")
@click.pass_context
def cli(ctx: click.Context, api_key, base_url, source, pretty, skip_mcp):
    """HeySol API Client CLI

    Setup:
      1. Get your API key from: https://core.heysol.ai/settings/api
      2. Set environment variable: export HEYSOL_API_KEY="your-key-here"
      3. Or use --api-key option with each command

    Examples:
      # Get user profile
      heysol-client profile get

      # List spaces
      heysol-client spaces list

      # Create a space
      heysol-client spaces create "My Space" --description "Description"

      # Get space details
      heysol-client spaces get <space-id>

      # Ingest data
      heysol-client memory ingest "Hello world" --space-id abc123

      # Search memory
      heysol-client memory search "query" --space-id abc123 --limit 10

      # List logs with status filtering
      heysol-client logs list --space-id abc123 --status success --limit 50

      # Check ingestion processing status
      heysol-client logs status --space-id abc123

      # Delete logs by source
      heysol-client logs delete-by-source "source-name" --confirm

      # Delete specific log entry
      heysol-client logs delete-entry "log-id" --confirm

      # Get specific log
      heysol-client logs get "log-id"

      # Get logs by source with status filter
      heysol-client logs get-by-source "kilo-code" --status success --limit 10

      # List unique sources with status filter
      heysol-client logs sources --status success

      # Update space properties
      heysol-client spaces update "space-id" --name "New Name"

      # Bulk space operations
      heysol-client spaces bulk-ops "intent" --space-id "space-id"

      # Delete space
      heysol-client spaces delete "space-id" --confirm

      # Create webhook
      heysol-client webhooks create "https://example.com/webhook" --secret "secret"

      # List webhooks
      heysol-client webhooks list

      # Update webhook
      heysol-client webhooks update "webhook-id" "https://new-url.com" --events "event1" --secret "new-secret"

      # List MCP tools
      heysol-client tools list
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url
    ctx.obj["source"] = source
    ctx.obj["pretty"] = pretty
    ctx.obj["skip_mcp"] = skip_mcp


# Add command groups
cli.add_command(profile)
cli.add_command(spaces)
cli.add_command(memory)
cli.add_command(logs)
cli.add_command(webhooks)
cli.add_command(tools)


def main():
    cli()


if __name__ == "__main__":
    main()
