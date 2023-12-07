import click
from app.cli.start import Environment, pass_environment
from app.config import settings
from app.lib import terminal


@click.command('run', short_help='Run the application.')
# Define the debug argument as a flag (-d, --debug).
@click.option(
    '-d',
    '--debug',
    is_flag=True,
    help='Enable debug mode.',
    default=settings.debug,
)
# Define the model argument (-m, --model) and its type (click.Choice).
@click.option(
    '-m',
    '--model',
    type=click.Choice(
        ['gpt-4-vision-preview', 'agent-1'],
        case_sensitive=False),
    help='The model to use.',
    default=settings.openai_model,
)
# Define the voice argument as a flag (-v, --voice).
@click.option(
    '-v',
    '--voice',
    is_flag=True,
    help='Use voice prompts for control instead of text-based prompts.',
    default=settings.voice_mode,
)
# Define the accurate argument as a flag (-a, --accurate).
@click.option(
    '-a',
    '--accurate',
    is_flag=True,
    help='Activate reflective mouse click mode.',
    default=settings.accurate_mode,
)
@pass_environment
def cli(ctx: Environment, debug: bool, model: str, voice: bool, accurate: bool):
    """ Run the application."""
    from app.main import main
    ctx.settings.debug = debug
    ctx.settings.openai_model = model
    ctx.settings.voice_mode = voice
    ctx.settings.accurate_mode = accurate

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{terminal.ANSI_BRIGHT_MAGENTA}Exiting SOC...")
