#!/usr/bin/env python3
"""Release automation script for coloursamples."""

import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class ReleaseError(Exception):
    """Custom exception for release-related errors."""


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Execute shell command and return result.

    Args:
        cmd: Shell command to execute.
        check: Whether to raise exception on command failure.

    Returns:
        CompletedProcess instance with command results.

    Raises:
        ReleaseError: If command fails and check is True.
    """
    logger.info("Executing command: %s", cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        logger.error("Command failed: %s", cmd)
        logger.error("stdout: %s", result.stdout)
        logger.error("stderr: %s", result.stderr)
        raise ReleaseError(f"Command failed: {cmd}")

    return result


def get_current_version() -> str:
    """Retrieve current version from git tags.

    Returns:
        Current version string or '0.0.0' if no tags exist.
    """
    result = run_command("git describe --tags --abbrev=0", check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return "0.0.0"


def validate_version(version: str) -> bool:
    """Validate semantic version format.

    Args:
        version: Version string to validate.

    Returns:
        True if version follows semantic versioning format.
    """
    pattern = r"^v?\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def update_version_files(version: str) -> None:
    """Update version in pyproject.toml and _version.py files.

    Args:
        version: New version string (without 'v' prefix).
    """
    version_clean = version.lstrip("v")

    # Parse version tuple
    version_parts = version_clean.split(".")
    if len(version_parts) != 3:
        raise ReleaseError(f"Invalid version format: {version_clean}")

    try:
        version_tuple = tuple(int(part) for part in version_parts)
    except ValueError as e:
        raise ReleaseError(f"Version parts must be integers: {version_clean}") from e

    # Update pyproject.toml
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Find and replace version line in [project] section only
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == 'version = "0.1.5"' or line.strip().startswith(
            'version = "'
        ):
            # Make sure we're in the [project] section by checking previous lines
            project_section = False
            for j in range(max(0, i - 10), i):
                if "[project]" in lines[j]:
                    project_section = True
                elif lines[j].strip().startswith("[") and "[project]" not in lines[j]:
                    project_section = False

            if project_section:
                lines[i] = f'version = "{version_clean}"'
                break

    content = "\n".join(lines)
    pyproject_path.write_text(content)

    # Update _version.py
    version_file_path = Path("src/coloursamples/_version.py")
    version_content = f'''"""Version information for coloursamples package."""

__version__ = "{version_clean}"
__version_tuple__ = {version_tuple}

# For backwards compatibility
version = __version__
version_tuple = __version_tuple__
'''
    version_file_path.write_text(version_content)

    logger.info(
        "Updated version to %s in pyproject.toml and _version.py", version_clean
    )


def validate_release_conditions(version: str) -> None:
    """Validate conditions required for creating a release.

    Args:
        version: Version string to validate and use for release.

    Raises:
        ReleaseError: If release conditions are not met.
    """
    if not validate_version(version):
        raise ReleaseError(f"Invalid version format: {version}")

    current_version = get_current_version()
    logger.info("Current version: %s", current_version)
    logger.info("New version: %s", version)

    result = run_command("git branch --show-current")
    current_branch = result.stdout.strip()

    if current_branch not in ("master", "main"):
        logger.warning(
            "Creating release from branch '%s', not master/main", current_branch
        )
        response = input("Continue? (y/N): ")
        if response.lower() != "y":
            raise ReleaseError("Release cancelled by user")

    result = run_command("git status --porcelain")
    if result.stdout.strip():
        raise ReleaseError("Working directory has uncommitted changes")


def run_quality_checks() -> None:
    """Execute comprehensive quality checks before release.

    Raises:
        ReleaseError: If any quality check fails.
    """
    logger.info("Running tests...")
    run_command("uv run pytest")

    logger.info("Running code quality checks...")
    run_command("uv run ruff check .")
    run_command("uv run ruff format --check .")


def create_and_push_tag(version: str, message: str) -> None:
    """Create and push git tag for the release.

    Args:
        version: Version string for the tag.
        message: Release message for the tag.

    Raises:
        ReleaseError: If tag creation or push fails.
    """
    logger.info("Creating tag %s...", version)
    run_command(f'git tag -a {version} -m "{message}"')
    run_command(f"git push origin {version}")


def build_packages() -> None:
    """Build distribution packages.

    Raises:
        ReleaseError: If package build fails.
    """
    logger.info("Building packages...")
    run_command("uv run hatch build")


def display_completion_message(version: str) -> None:
    """Display release completion message with next steps.

    Args:
        version: Version string that was released.
    """
    logger.info("Release %s created successfully!", version)
    logger.info("Next steps:")
    logger.info(
        "1. Create GitHub release at: https://github.com/jackemcpherson/colourSamples/releases/new?tag=%s",
        version,
    )
    logger.info("2. Upload to PyPI: uv run twine upload dist/*")
    logger.info("3. Update CHANGELOG.md if needed")


def create_release(version: str, message: str) -> None:
    """Create a new release with the specified version.

    Args:
        version: Version number for the release.
        message: Release message for git tag.

    Raises:
        ReleaseError: If any step of the release process fails.
    """
    if not version.startswith("v"):
        version = f"v{version}"

    validate_release_conditions(version)
    update_version_files(version)

    # Commit the version updates if there are changes
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        run_command("git add pyproject.toml src/coloursamples/_version.py")
        run_command(f'git commit -m "Bump version to {version}"')
    else:
        logger.info("No version changes to commit (already at target version)")

    run_quality_checks()
    create_and_push_tag(version, message)
    build_packages()
    display_completion_message(version)


def setup_logging() -> None:
    """Configure logging for the release script."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main() -> None:
    """Main entry point for the release script."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument("version", help="Version number (e.g., 0.1.4 or v0.1.4)")
    parser.add_argument("-m", "--message", default="", help="Release message")

    args = parser.parse_args()

    if not args.message:
        args.message = f"Release {args.version}"

    try:
        create_release(args.version, args.message)
    except ReleaseError as e:
        logger.error("Release failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
