"""Tests for coloursamples core functionality."""

from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from coloursamples.cli import app
from coloursamples.core import create_image
from coloursamples.exceptions import InvalidColourCodeError, InvalidDimensionsError

BASIC_IMAGE_TEST_DATA = [
    (100, 100, "#FF5733", "FF5733.jpg"),
    (200, 150, "#3498db", "3498db.jpg"),
    (50, 75, "#2ECC71", "2ECC71.jpg"),
    (300, 200, "#E74C3C", "E74C3C.jpg"),
    (1, 1, "#000000", "000000.jpg"),
    (800, 600, "#FFFFFF", "FFFFFF.jpg"),
]

INVALID_DIMENSIONS_TEST_DATA = [
    (0, 100, "positive integers"),
    (-1, 100, "positive integers"),
    (100, 0, "positive integers"),
    (100, -1, "positive integers"),
    (-5, -10, "positive integers"),
]

INVALID_COLOUR_CODE_TEST_DATA = [
    ("FF5733", "must start with '#'"),
    ("#", "exactly 7 characters"),
    ("#FF", "exactly 7 characters"),
    ("#FFAABBCC", "exactly 7 characters"),
    ("", "must start with '#'"),
]

COLOUR_CODE_CASE_TEST_DATA = [
    "#ff5733",
    "#FF5733",
    "#Ff5733",
    "#123ABC",
    "#000000",
    "#FFFFFF",
]

LARGE_DIMENSIONS_TEST_DATA = [
    (5000, 5000),
    (1, 10000),
    (10000, 1),
]

CLI_COLOUR_FORMAT_TEST_DATA = [
    ("FF5733", "FF5733.jpg"),
    ("#FF5733", "FF5733.jpg"),
    ("ff5733", "FF5733.jpg"),
]


@pytest.mark.parametrize(
    "width,height,colour_code,expected_filename", BASIC_IMAGE_TEST_DATA
)
def test_successful_image_creation(
    tmp_path: Path, width: int, height: int, colour_code: str, expected_filename: str
) -> None:
    """Test successful image creation with various valid parameters."""
    output_dir = tmp_path / "output_files"
    create_image(width, height, colour_code, output_dir)
    img_path = output_dir / expected_filename
    assert img_path.exists()
    img = Image.open(img_path)
    assert img.size == (width, height)
    expected_rgb_from_hex = (
        int(colour_code[1:3], 16),
        int(colour_code[3:5], 16),
        int(colour_code[5:7], 16),
    )
    actual_rgb = img.getpixel((0, 0))
    for actual, expected in zip(actual_rgb, expected_rgb_from_hex):
        assert abs(actual - expected) <= 2, (
            f"Color mismatch: {actual_rgb} vs {expected_rgb_from_hex}"
        )


@pytest.mark.parametrize("width,height,expected_message", INVALID_DIMENSIONS_TEST_DATA)
def test_invalid_dimensions(width: int, height: int, expected_message: str) -> None:
    """Test that InvalidDimensionsError is raised for invalid dimensions."""
    with pytest.raises(InvalidDimensionsError) as excinfo:
        create_image(width, height, "#FF5733")
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize("colour_code,expected_message", INVALID_COLOUR_CODE_TEST_DATA)
def test_invalid_colour_code(colour_code: str, expected_message: str) -> None:
    """Test that InvalidColourCodeError is raised for invalid colour code formats."""
    with pytest.raises(InvalidColourCodeError) as excinfo:
        create_image(100, 100, colour_code)
    assert expected_message in str(excinfo.value)


def test_invalid_colour_code_non_string() -> None:
    """Test that InvalidColourCodeError is raised for non-string colour codes."""
    with pytest.raises(InvalidColourCodeError):
        create_image(100, 100, 123)

    with pytest.raises(InvalidColourCodeError):
        create_image(100, 100, None)


@pytest.mark.parametrize("colour_code", COLOUR_CODE_CASE_TEST_DATA)
def test_colour_code_case_handling(tmp_path: Path, colour_code: str) -> None:
    """Test that colour codes work with different case formats."""
    output_dir = tmp_path / "case_test"
    create_image(50, 50, colour_code, output_dir)
    expected_filename = colour_code.lstrip("#") + ".jpg"
    img_path = output_dir / expected_filename
    assert img_path.exists()


@pytest.mark.parametrize("width,height", LARGE_DIMENSIONS_TEST_DATA)
def test_large_dimensions(tmp_path: Path, width: int, height: int) -> None:
    """Test that large dimensions work correctly."""
    output_dir = tmp_path / "large_test"
    create_image(width, height, "#FF0000", output_dir)
    img_path = output_dir / "FF0000.jpg"
    assert img_path.exists()
    img = Image.open(img_path)
    assert img.size == (width, height)


def test_output_directory_creation(tmp_path: Path) -> None:
    """Test that output directory is created when it doesn't exist."""
    width, height, colour_code = 100, 100, "#FF5733"
    output_dir = tmp_path / "output_files"
    create_image(width, height, colour_code, output_dir)
    assert output_dir.exists()


def test_string_output_dir(tmp_path: Path) -> None:
    """Ensure create_image works when output_dir is provided as a string."""
    width, height, colour_code = 50, 50, "#00FF00"
    output_dir = tmp_path / "string_output"
    create_image(width, height, colour_code, str(output_dir))
    assert (output_dir / "00FF00.jpg").exists()


def test_default_output_directory() -> None:
    """Test that default output directory is created when none specified."""
    import os

    # Clean up any existing test file
    if os.path.exists("123456.jpg"):
        os.remove("123456.jpg")

    create_image(50, 50, "#123456")
    assert os.path.exists("123456.jpg")

    # Clean up the test file
    os.remove("123456.jpg")


class TestCLI:
    """Test cases for the CLI interface."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_create_command_basic(self) -> None:
        """Test basic create command functionality."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(app, ["create", "100", "100", "#FF5733"])
            assert result.exit_code == 0
            assert "Image created successfully" in result.stdout
            assert Path("FF5733.jpg").exists()

    def test_create_command_with_output_dir(self) -> None:
        """Test create command with custom output directory."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                app,
                ["create", "200", "150", "#3498db", "--output-dir", "custom_output"],
            )
            assert result.exit_code == 0
            assert Path("custom_output/3498db.jpg").exists()

    def test_create_command_verbose(self) -> None:
        """Test create command with verbose logging."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                app, ["create", "50", "50", "#000000", "--verbose"]
            )
            assert result.exit_code == 0
            assert Path("000000.jpg").exists()

    def test_create_command_invalid_dimensions(self) -> None:
        """Test create command with invalid dimensions."""
        result = self.runner.invoke(app, ["create", "0", "100", "#FF5733"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout

    def test_create_command_invalid_colour(self) -> None:
        """Test create command with invalid colour code."""
        result = self.runner.invoke(app, ["create", "100", "100", "invalid"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @pytest.mark.parametrize("colour_input,expected_file", CLI_COLOUR_FORMAT_TEST_DATA)
    def test_colour_format_normalization(
        self, colour_input: str, expected_file: str
    ) -> None:
        """Test that colour codes are properly normalized."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(app, ["create", "100", "100", colour_input])
            assert result.exit_code == 0
            assert Path(expected_file).exists()

    def test_interactive_mode(self) -> None:
        """Test interactive mode functionality."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                app, ["create", "--interactive"], input="800\n600\n#FF5733\n"
            )
            assert result.exit_code == 0
            assert Path("FF5733.jpg").exists()

    def test_info_command(self) -> None:
        """Test info command displays version and repository info."""
        result = self.runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Colour Samples" in result.stdout
        assert "github.com" in result.stdout

    def test_help_command(self) -> None:
        """Test help command functionality."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Generate JPEG images" in result.stdout
        assert "create" in result.stdout
        assert "info" in result.stdout

    def test_partial_arguments_warning(self) -> None:
        """Test that partial arguments trigger interactive mode or show error."""
        result = self.runner.invoke(app, ["create", "100", "100"])
        assert result.exit_code in [0, 1]

    def test_dimension_validation_in_cli(self) -> None:
        """Test CLI dimension validation."""
        result = self.runner.invoke(app, ["create", "11000", "100", "#FF5733"])
        assert result.exit_code == 1
        assert "Width must be between 1 and 10000" in result.stdout

    def test_colour_validation_in_cli(self) -> None:
        """Test CLI colour code validation."""
        result = self.runner.invoke(app, ["create", "100", "100", "#GG5733"])
        assert result.exit_code == 1
        assert "Invalid hex colour code" in result.stdout

    def test_short_colour_code_validation(self) -> None:
        """Test validation of short colour codes."""
        result = self.runner.invoke(app, ["create", "100", "100", "#FF5"])
        assert result.exit_code == 1
        assert "Colour code must be 6 hex characters" in result.stdout
