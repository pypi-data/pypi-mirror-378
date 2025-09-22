"""
Main CLI entry point for NetIntel-OCR v0.1.17
"""

import os
import sys
import json
import click
from pathlib import Path
from typing import Optional

# Import command groups
from .commands import process_cmd
from .commands import server_cmd
from .commands import db_cmd
from .commands import kg_cmd
from .commands import project_cmd
from .commands import model_cmd
from .commands import config_cmd
from .commands import system_cmd

# Version info
try:
    from ..__version__ import __version__
except ImportError:
    __version__ = "0.1.17.1"


class GlobalConfig:
    """Global configuration context"""
    def __init__(self):
        self.config_file = None
        self.config_data = {}
        self.verbose = False
        self.debug = False

    def load_config(self, config_file: Optional[str] = None):
        """Load configuration from file"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                self.config_data = json.load(f)
            self.config_file = config_file
            return True
        return False


pass_config = click.make_pass_decorator(GlobalConfig, ensure=True)


def show_version(ctx, value):
    """Show enhanced version information."""
    if not value or ctx.resilient_parsing:
        return

    try:
        # Try to use enhanced version display
        from .utils.version_info import VersionInfo
        info = VersionInfo.get_version_details()
        click.echo(VersionInfo.format_as_text(info, detailed=False))
    except ImportError:
        # Fallback to simple version display
        try:
            from ..__version__ import format_version_string
            click.echo(format_version_string())
        except ImportError:
            click.echo(f"NetIntel-OCR v{__version__}")

    ctx.exit()


@click.group(invoke_without_command=True)
@click.option('--config', type=click.Path(exists=True),
              help='Configuration file to use')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--debug', '-d', is_flag=True,
              help='Enable debug output')
@click.option('--version', is_flag=True, expose_value=False, is_eager=True,
              help='Show enhanced version and capability information',
              callback=lambda ctx, param, value: show_version(ctx, value))
@click.pass_context
def cli(ctx, config, verbose, debug):
    """NetIntel-OCR - Network Intelligence from Documents

    Extract and analyze network diagrams, configurations, and documentation
    from PDF files using AI-powered OCR and knowledge graph technology.

    Examples:
        netintel-ocr process file document.pdf
        netintel-ocr server api --port 8000
        netintel-ocr db query "network topology"
        netintel-ocr kg rag-query "compliance issues"
    """
    # Initialize global config
    ctx.obj = GlobalConfig()
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug

    # Load configuration if provided
    if config:
        if ctx.obj.load_config(config):
            if verbose:
                click.echo(f"Loaded configuration from: {config}")
        else:
            click.echo(f"Warning: Could not load config from {config}", err=True)

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register command groups
cli.add_command(process_cmd.process)
cli.add_command(server_cmd.server)
cli.add_command(db_cmd.db)
cli.add_command(kg_cmd.kg)
cli.add_command(project_cmd.project)
cli.add_command(model_cmd.model)
cli.add_command(config_cmd.config)
cli.add_command(system_cmd.system)


# Add shell completion support
@cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
def completion(shell):
    """Generate shell completion script"""
    import subprocess

    env = os.environ.copy()

    if shell == 'bash':
        env['_NETINTEL_OCR_COMPLETE'] = 'bash_source'
    elif shell == 'zsh':
        env['_NETINTEL_OCR_COMPLETE'] = 'zsh_source'
    elif shell == 'fish':
        env['_NETINTEL_OCR_COMPLETE'] = 'fish_source'

    result = subprocess.run(
        [sys.executable, '-m', 'netintel_ocr.cli_v2'],
        env=env,
        capture_output=True,
        text=True
    )

    click.echo(result.stdout)


def main():
    """Main entry point"""
    try:
        cli(prog_name='netintel-ocr')
    except Exception as e:
        if '--debug' in sys.argv or '-d' in sys.argv:
            raise
        else:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='runpy')
    main()