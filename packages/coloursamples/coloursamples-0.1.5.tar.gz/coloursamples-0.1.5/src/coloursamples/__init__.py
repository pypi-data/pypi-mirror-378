"""Colour Samples - Python utility for generating JPEG images."""

from .core import create_image
from .exceptions import (
    ColourSamplesError,
    FileSystemError,
    ImageCreationError,
    InvalidColourCodeError,
    InvalidDimensionsError,
)

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    "create_image",
    "__version__",
    "ColourSamplesError",
    "InvalidDimensionsError",
    "InvalidColourCodeError",
    "FileSystemError",
    "ImageCreationError",
]
