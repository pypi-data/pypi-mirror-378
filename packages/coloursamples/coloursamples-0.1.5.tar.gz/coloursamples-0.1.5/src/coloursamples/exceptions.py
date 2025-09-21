"""Custom exceptions for coloursamples application."""


class ColourSamplesError(Exception):
    """Base exception for all coloursamples errors.

    This is the base exception class that all other custom exceptions inherit from.
    It provides a clean way to catch any coloursamples-specific error.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Human-readable error message to display to the user.
        """
        self.message = message
        super().__init__(message)


class InvalidDimensionsError(ColourSamplesError):
    """Raised when image dimensions are invalid.

    This exception is raised when width or height values are not positive
    integers or exceed reasonable limits.
    """


class InvalidColourCodeError(ColourSamplesError):
    """Raised when a colour code format is invalid.

    This exception is raised when the provided colour code doesn't match
    the expected HTML hex format (#RRGGBB).
    """


class FileSystemError(ColourSamplesError):
    """Raised when file system operations fail.

    This exception is raised when there are issues with file or directory
    operations, such as permission errors or disk space issues.
    """


class ImageCreationError(ColourSamplesError):
    """Raised when image creation or saving fails.

    This exception is raised when the PIL image creation or saving
    process encounters an error.
    """
