# colourSamples

A Python utility for generating JPEG images with specified dimensions and colors.

## Getting Started

### Installation

Install the package and its dependencies using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package in development mode
uv pip install -e ".[dev]"
```

Alternatively, install dependencies manually:

```bash
pip install Pillow pytest ruff
```

### Usage

#### Command Line Interface

The package provides a modern CLI with rich formatting and helpful options:

```bash
# Direct command with arguments
coloursamples create 800 600 "#FF5733"

# With custom output directory
coloursamples create 400 300 "3498db" --output-dir ./my_images

# Interactive mode with prompts and defaults
coloursamples create --interactive

# Verbose logging for debugging
coloursamples create 200 150 "#8E44AD" --verbose

# Get help
coloursamples --help
coloursamples create --help

# Display tool information
coloursamples info
```

#### Programmatic Usage

```python
from coloursamples import create_image

# Create a 500x300 red image
create_image(500, 300, "#FF0000")

# Create an image in a specific directory
create_image(100, 100, "#00FF00", "my_output_dir")
```

The function will create an image of the specified size and color, and save it as a JPEG file. The filename will be the color code without the leading '#'.

## Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_core.py
```

## Development Setup

### Code Formatting and Linting

This project uses ruff for code formatting and linting:

```bash
# Check code style
ruff check .

# Format code
ruff format .
```

### Project Structure

```
colourSamples/
├── src/
│   └── coloursamples/
│       ├── __init__.py
│       ├── core.py           # Main image creation functionality
│       └── cli.py            # Modern typer-based CLI
├── tests/
│   ├── __init__.py
│   └── test_core.py          # Test suite
├── docs/                     # Documentation
├── logs/                     # Log files
├── pyproject.toml            # Project configuration with console scripts
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please ensure tests pass and code is formatted before submitting:

```bash
pytest
ruff check .
ruff format .
```
