import click
from app.cli.start import Environment, pass_environment
from app.lib import terminal


@click.command('run', short_help='Run a mouse cursor detection feature that prints the mouse coordinates to the CLI.')
@pass_environment
def cli(ctx: Environment):
    """ Run a mouse cursor detection feature that prints the mouse coordinates to the CLI."""
    import pyautogui

    try:
        pyautogui.displayMousePosition()
    except KeyboardInterrupt:
        print(f"\n{terminal.ANSI_BRIGHT_MAGENTA}Exiting SOC...")
