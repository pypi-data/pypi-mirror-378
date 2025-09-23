"""
Knowledge Graph commands - wrapper for existing KG CLI
"""

import click
import sys


@click.group()
@click.pass_context
def kg(ctx):
    """Knowledge Graph operations

    All KG commands are passed through to the existing KG CLI implementation.
    """
    # Check if KG features are available
    from ...core.feature_detection import FeatureDetector

    if not FeatureDetector.has_kg():
        click.echo(
            "❌ Knowledge Graph features not installed.\n"
            "Install with: pip install netintel-ocr[kg]\n"
            "\nThis will add:\n"
            "  • PyKEEN - Knowledge graph embeddings\n"
            "  • torch - Deep learning framework\n"
            "  • FalkorDB - Graph database\n"
            "  • Additional dependencies (~1.5GB)\n",
            err=True
        )
        ctx.exit(1)


# Instead of duplicating all KG commands, we pass through to the existing implementation
@kg.command(add_help_option=False, context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def _passthrough(ctx, args):
    """Pass through to existing KG CLI"""

    # Import the existing KG CLI (will fail if not installed)
    try:
        from ...kg.cli_commands import kg_cli
    except ImportError:
        click.echo(
            "❌ KG module not found. Install with: pip install netintel-ocr[kg]",
            err=True
        )
        ctx.exit(1)

    # Convert args to proper format and invoke
    import sys
    sys.argv = ['netintel-ocr-kg'] + list(args)

    try:
        kg_cli()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        click.echo(f"❌ KG command failed: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


# Override the group's invoke to handle all subcommands
original_invoke = kg.invoke

def invoke_wrapper(ctx):
    if hasattr(ctx, 'protected') and ctx.protected:
        return original_invoke(ctx)

    # Get all args after 'kg'
    import sys
    kg_index = sys.argv.index('kg') if 'kg' in sys.argv else -1
    if kg_index >= 0 and kg_index < len(sys.argv) - 1:
        kg_args = sys.argv[kg_index + 1:]

        # Pass to existing KG CLI
        from ...kg.cli_commands import kg_cli
        sys.argv = ['netintel-ocr-kg'] + kg_args

        try:
            kg_cli()
            sys.exit(0)
        except SystemExit as e:
            sys.exit(e.code)
        except Exception as e:
            click.echo(f"❌ KG command failed: {e}", err=True)
            sys.exit(1)
    else:
        # Show help if no subcommand
        click.echo(ctx.get_help())

kg.invoke = invoke_wrapper