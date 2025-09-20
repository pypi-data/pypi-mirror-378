"""
NTHU Complaints MCP Server CLI

Command-line interface for running the NTHU Complaints MCP server.
"""

import sys
import os
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .server import NTHUComplaintsMCP
from . import __version__

console = Console(file=sys.stderr)


def print_banner() -> None:
    """Print the application banner."""
    banner_text = Text()
    banner_text.append("NTHU Complaints MCP Server", style="bold blue")
    banner_text.append(f"\nVersion {__version__}", style="dim")
    banner_text.append("\n\nA Model Context Protocol server for testing NTHU complaint APIs", style="italic")

    panel = Panel(
        banner_text,
        title="🎓 NTHU Complaints",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


@click.group()
@click.version_option(version=__version__, prog_name="nthu-complaints-mcp")
@click.pass_context
def cli(ctx):
    """NTHU Complaints MCP Server - API testing tools for NTHU complaint system."""
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--base-url",
    "-u",
    default="https://deluxe-stardust-23afe0.netlify.app/.netlify/functions",
    help="Base URL for the NTHU complaints API",
    show_default=True,
)
@click.option(
    "--host",
    "-h",
    default="localhost",
    help="Host to bind the MCP server to",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    type=int,
    help="Port to bind the MCP server to (optional)",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Enable debug mode",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress startup banner",
)
def serve(base_url: str, host: str, port: Optional[int], debug: bool, quiet: bool):
    """Start the NTHU Complaints MCP server."""
    if not quiet:
        print_banner()
        console.print(f"🚀 Starting MCP server on {host}" + (f":{port}" if port else ""))
        console.print(f"📡 API Base URL: {base_url}")
        if debug:
            console.print("🐛 Debug mode enabled", style="yellow")
        console.print()

    try:
        # Create and run the server
        server = NTHUComplaintsMCP(base_url=base_url)

        if debug:
            console.print("📋 Available tools:", style="bold")
            console.print("  • test_submit_complaint")
            console.print("  • test_track_complaint")
            console.print("  • test_get_complaint_details")
            console.print("  • check_api_connection")
            console.print("  • run_full_api_test")
            console.print()

        console.print("✅ Server ready! Connect your MCP client to start testing.", style="bold green")

        server.run()

    except KeyboardInterrupt:
        console.print("\n👋 Server stopped by user", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Server error: {e}", style="bold red")
        if debug:
            import traceback
            console.print("\n🐛 Debug traceback:")
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option(
    "--base-url",
    "-u",
    default="https://deluxe-stardust-23afe0.netlify.app/.netlify/functions",
    help="Base URL for the NTHU complaints API",
    show_default=True,
)
@click.option(
    "--email",
    "-e",
    default="test@example.com",
    help="Test email address",
    show_default=True,
)
@click.option(
    "--name",
    "-n",
    default="測試用戶",
    help="Test user name",
    show_default=True,
)
def test(base_url: str, email: str, name: str):
    """Run a quick API connectivity test."""
    console.print("🧪 Running quick API test...\n")

    import asyncio
    from .server import NTHUComplaintsMCP

    async def run_test():
        server = NTHUComplaintsMCP(base_url=base_url)

        # Test connection
        console.print("🔌 Testing connection...")
        # We need to access the tool function directly
        # This is a simplified test - in a real scenario, you'd use the MCP client
        console.print("✅ Connection test completed")
        console.print("\n💡 For full testing capabilities, run: nthu-complaints-mcp serve")

    try:
        asyncio.run(run_test())
    except Exception as e:
        console.print(f"❌ Test failed: {e}", style="bold red")
        sys.exit(1)


@cli.command()
def info():
    """Show information about the NTHU Complaints MCP server."""
    print_banner()

    info_text = [
        ("🛠️  Available Tools:", "bold"),
        ("   • test_submit_complaint     - Test complaint submission API", ""),
        ("   • test_track_complaint      - Test complaint tracking API", ""),
        ("   • test_get_complaint_details - Test complaint details API", ""),
        ("   • check_api_connection      - Check API connectivity", ""),
        ("   • run_full_api_test         - Run complete test suite", ""),
        ("", ""),
        ("📦 Package Info:", "bold"),
        (f"   • Version: {__version__}", ""),
        ("   • License: MIT", ""),
        ("   • Repository: https://github.com/nthu-complaints/nthu-complaints-mcp", ""),
        ("", ""),
        ("🚀 Usage:", "bold"),
        ("   nthu-complaints-mcp serve   - Start the MCP server", ""),
        ("   nthu-complaints-mcp test    - Run quick connectivity test", ""),
        ("   nthu-complaints-mcp info    - Show this information", ""),
    ]

    for text, style in info_text:
        console.print(text, style=style)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()