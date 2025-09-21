"""Command-line interface for coloursamples using typer."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from . import __version__
from .core import create_image
from .exceptions import (
    ColourSamplesError,
    InvalidColourCodeError,
    InvalidDimensionsError,
)

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="coloursamples",
    help="Generate JPEG images with specified dimensions and colours.",
    no_args_is_help=True,
)
console = Console()


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbose: Enable debug level logging if True, info level otherwise.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("Logging configured with level: %s", logging.getLevelName(level))


def _validate_colour_format(colour: str) -> str:
    """Validate and normalize colour code format.

    Args:
        colour: Raw colour code input from user.

    Returns:
        Normalized colour code in uppercase with # prefix.

    Raises:
        InvalidColourCodeError: If colour format is invalid.
    """
    if not colour.startswith("#"):
        colour = f"#{colour}"

    if len(colour) != 7:
        raise InvalidColourCodeError(
            f"Colour code must be 6 hex characters (got {len(colour) - 1}). "
            f"Example: #FF5733 or FF5733"
        )

    try:
        int(colour[1:], 16)
    except ValueError as e:
        raise InvalidColourCodeError(
            f"Invalid hex colour code: {colour}. "
            f"Must contain only hex digits (0-9, A-F). Example: #FF5733"
        ) from e

    return colour.upper()


def _interactive_mode() -> tuple[int, int, str]:
    """Run interactive mode to collect user input.

    Returns:
        Tuple of (width, height, colour) from user input.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Interactive Image Creator[/bold cyan]\n"
            "Enter image dimensions and colour",
            border_style="cyan",
        )
    )

    width = IntPrompt.ask(
        "[bold]Image width[/bold] (pixels)", default=800, show_default=True
    )
    height = IntPrompt.ask(
        "[bold]Image height[/bold] (pixels)", default=600, show_default=True
    )

    colour = Prompt.ask(
        "[bold]Colour code[/bold] (hex format)", default="#3498db", show_default=True
    )

    return width, height, colour


def _validate_input_parameters(width: int, height: int) -> None:
    """Validate that input parameters are within acceptable ranges.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.

    Raises:
        InvalidDimensionsError: If width or height are outside valid range.
    """
    if width <= 0 or width > 10000:
        raise InvalidDimensionsError("Width must be between 1 and 10000 pixels")
    if height <= 0 or height > 10000:
        raise InvalidDimensionsError("Height must be between 1 and 10000 pixels")


def _handle_input_collection(
    interactive: bool, width: int | None, height: int | None, colour: str | None
) -> tuple[int, int, str]:
    """Handle input collection from arguments or interactive mode.

    Args:
        interactive: Whether to force interactive mode.
        width: Width from command line arguments or None.
        height: Height from command line arguments or None.
        colour: Colour from command line arguments or None.

    Returns:
        Tuple of (width, height, colour) from arguments or interactive input.

    Raises:
        InvalidDimensionsError: If arguments are missing and not in interactive mode.
    """
    if interactive:
        return _interactive_mode()

    if width is None or height is None or colour is None:
        missing_args = []
        if width is None:
            missing_args.append("width")
        if height is None:
            missing_args.append("height")
        if colour is None:
            missing_args.append("colour")

        raise InvalidDimensionsError(
            f"Missing required arguments: {', '.join(missing_args)}. "
            f"Use --interactive or provide all three arguments."
        )

    return width, height, colour


def _create_and_save_image(
    width: int, height: int, colour: str, output_dir: Path | None
) -> None:
    """Create and save the image with status indicator.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        colour: Normalized colour code with # prefix.
        output_dir: Directory to save image or None for default.
    """
    with console.status(f"[bold green]Creating {width}x{height} image..."):
        create_image(width, height, colour, output_dir)


def _display_success_message(
    width: int, height: int, colour: str, output_dir: Path | None
) -> None:
    """Display formatted success message with image details.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        colour: Normalized colour code with # prefix.
        output_dir: Directory where image was saved or None for default.
    """
    output_path = output_dir or Path(".")
    filename = colour.lstrip("#") + ".jpg"
    full_path = output_path / filename

    console.print(
        Panel.fit(
            f"[bold green]✓ Image created successfully![/bold green]\n\n"
            f"[bold]Dimensions:[/bold] {width}x{height} pixels\n"
            f"[bold]Colour:[/bold] {colour}\n"
            f"[bold]Saved to:[/bold] {full_path}",
            border_style="green",
            title="Success",
        )
    )


@app.command()
def create(
    width: Annotated[
        int | None, typer.Argument(help="Width of the image in pixels (1-10000)")
    ] = None,
    height: Annotated[
        int | None, typer.Argument(help="Height of the image in pixels (1-10000)")
    ] = None,
    colour: Annotated[
        str | None, typer.Argument(help="Hex colour code (e.g., #FF5733 or FF5733)")
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to save the image (default: current directory)",
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive", "-i", help="Run in interactive mode with prompts"
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging")
    ] = False,
) -> None:
    """Create a JPEG image with specified dimensions and colour.

    Args:
        width: Width of the image in pixels (1-10000) or None for interactive.
        height: Height of the image in pixels (1-10000) or None for interactive.
        colour: Hex colour code (e.g., #FF5733) or None for interactive.
        output_dir: Directory to save the image or None for default.
        interactive: Force interactive mode with prompts.
        verbose: Enable verbose logging output.

    Raises:
        typer.Exit: If any validation fails or image creation errors occur.

    Examples:
        coloursamples create 800 600 "#FF5733"
        coloursamples create 400 300 "3498db" --output-dir ./images
        coloursamples create --interactive
    """
    _setup_logging(verbose)

    try:
        width, height, colour = _handle_input_collection(
            interactive, width, height, colour
        )
        _validate_input_parameters(width, height)

        normalised_colour = _validate_colour_format(colour)
        _create_and_save_image(width, height, normalised_colour, output_dir)
        _display_success_message(width, height, normalised_colour, output_dir)

    except ColourSamplesError as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}", style="red")
        raise typer.Exit(1) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]", style="yellow")
        raise typer.Exit(1) from None
    except Exception as e:
        logger.exception("Unexpected error during image creation: %s", e)
        console.print(
            f"[bold red]Unexpected error:[/bold red] {e}\n"
            f"[dim]Please report this issue if it persists.[/dim]",
            style="red",
        )
        raise typer.Exit(1) from None


@app.command()
def info() -> None:
    """Display information about the coloursamples tool."""
    console.print(
        Panel.fit(
            f"[bold cyan]Colour Samples[/bold cyan] v{__version__}\n\n"
            "A Python utility for generating JPEG images with specified "
            "dimensions and colours.\n\n"
            "[bold]Repository:[/bold] https://github.com/jackemcpherson/colourSamples\n"
            "[bold]Documentation:[/bold] See README.md for detailed usage",
            border_style="cyan",
            title="Info",
        )
    )


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
