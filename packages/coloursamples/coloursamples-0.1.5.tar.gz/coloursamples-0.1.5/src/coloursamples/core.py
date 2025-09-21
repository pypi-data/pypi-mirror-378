"""Core functionality for creating coloured JPEG images."""

import logging
from pathlib import Path

from PIL import Image

from .exceptions import (
    FileSystemError,
    ImageCreationError,
    InvalidColourCodeError,
    InvalidDimensionsError,
)

logger = logging.getLogger(__name__)


def create_image(
    width: int,
    height: int,
    colour_code: str,
    output_dir: str | Path | None = None,
) -> None:
    """Create and save an image with the specified dimensions and colour.

    Args:
        width: The width of the image in pixels.
        height: The height of the image in pixels.
        colour_code: The HTML colour code for the image background.
        output_dir: The directory to save the image. Accepts a string path or
            pathlib.Path. Defaults to current directory.

    Raises:
        InvalidDimensionsError: If width/height are not positive or exceed limits.
        InvalidColourCodeError: If colour_code format is invalid.
        FileSystemError: If directory creation or file saving fails.
        ImageCreationError: If PIL image creation fails.
    """
    _validate_dimensions(width, height)
    _validate_colour_code(colour_code)

    output_path = _resolve_output_path(output_dir)
    filename = _generate_filename(colour_code)

    try:
        image = Image.new("RGB", (width, height), color=colour_code)
    except ValueError as e:
        raise ImageCreationError(f"Failed to create image: {e}") from e

    _ensure_directory_exists(output_path)

    full_path = output_path / f"{filename}.jpg"
    try:
        image.save(full_path)
        logger.info("Image saved to %s", full_path)
    except OSError as e:
        raise FileSystemError(f"Failed to save image to {full_path}: {e}") from e


def _validate_dimensions(width: int, height: int) -> None:
    """Validate that image dimensions are positive integers within limits.

    Raises:
        InvalidDimensionsError: If dimensions are invalid.
    """
    if width <= 0 or height <= 0:
        raise InvalidDimensionsError("Width and height must be positive integers")

    if width > 10000 or height > 10000:
        raise InvalidDimensionsError("Width and height must be 10000 pixels or less")


def _validate_colour_code(colour_code: str) -> None:
    """Validate that colour code is in proper HTML hex format.

    Raises:
        InvalidColourCodeError: If colour code format is invalid.
    """
    if not isinstance(colour_code, str):
        raise InvalidColourCodeError("Colour code must be a string. Example: #FF5733")

    if not colour_code.startswith("#"):
        raise InvalidColourCodeError(
            "Colour code must start with '#'. Example: #FF5733"
        )

    if len(colour_code) != 7:
        raise InvalidColourCodeError(
            f"Colour code must be exactly 7 characters (got {len(colour_code)}). "
            f"Example: #FF5733"
        )

    hex_part = colour_code[1:]
    try:
        int(hex_part, 16)
    except ValueError as e:
        raise InvalidColourCodeError(
            f"Invalid hex colour code: {colour_code}. "
            f"Must contain only hex digits (0-9, A-F). Example: #FF5733"
        ) from e


def _resolve_output_path(output_dir: str | Path | None) -> Path:
    """Convert output directory to Path object with default fallback."""
    if output_dir is None:
        return Path(".")
    return Path(output_dir)


def _generate_filename(colour_code: str) -> str:
    """Generate filename from colour code by removing hash prefix."""
    return colour_code.lstrip("#")


def _ensure_directory_exists(path: Path) -> None:
    """Create directory if it doesn't exist.

    Raises:
        FileSystemError: If directory creation fails.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise FileSystemError(f"Failed to create directory {path}: {e}") from e
