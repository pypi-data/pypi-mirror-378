#!/usr/bin/env python3
"""Pre-release checks to ensure everything is ready for a release."""

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def run_command(cmd: str) -> tuple[int, str, str]:
    """Execute command and return exit code with output streams.

    Args:
        cmd: Shell command to execute.

    Returns:
        Tuple containing exit code, stdout, and stderr.
    """
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_git_status() -> bool:
    """Verify git working directory is clean.

    Returns:
        True if working directory has no uncommitted changes.
    """
    code, stdout, _ = run_command("git status --porcelain")
    if code != 0:
        logger.error("Failed to check git status")
        return False

    if stdout.strip():
        logger.error("Working directory has uncommitted changes:")
        logger.error("%s", stdout)
        return False

    logger.info("Git working directory is clean")
    return True


def check_tests() -> bool:
    """Execute tests and verify they pass.

    Returns:
        True if all tests pass.
    """
    logger.info("Running tests...")
    code, stdout, stderr = run_command("uv run pytest -q")

    if code != 0:
        logger.error("Tests failed:")
        logger.error("%s", stderr)
        return False

    logger.info("All tests pass")
    return True


def check_coverage() -> bool:
    """Verify test coverage meets requirements.

    Returns:
        True if coverage meets minimum threshold.
    """
    logger.info("Checking test coverage...")
    code, stdout, stderr = run_command(
        "uv run pytest --cov=coloursamples --cov-fail-under=80 -q"
    )

    if code != 0:
        logger.error("Coverage check failed:")
        logger.error("%s", stderr)
        return False

    logger.info("Test coverage meets requirements")
    return True


def check_code_quality() -> bool:
    """Execute code quality checks with ruff.

    Returns:
        True if all quality checks pass.
    """
    logger.info("Checking code quality...")

    code, stdout, stderr = run_command("uv run ruff check .")
    if code != 0:
        logger.error("Linting failed:")
        logger.error("%s", stdout)
        logger.error("%s", stderr)
        return False

    code, stdout, stderr = run_command("uv run ruff format --check .")
    if code != 0:
        logger.error("Code formatting check failed:")
        logger.error("%s", stdout)
        return False

    logger.info("Code quality checks pass")
    return True


def check_build() -> bool:
    """Verify package builds successfully.

    Returns:
        True if package build succeeds.
    """
    logger.info("Testing package build...")
    code, stdout, stderr = run_command("uv run hatch build --clean")

    if code != 0:
        logger.error("Package build failed:")
        logger.error("%s", stderr)
        return False

    logger.info("Package builds successfully")
    return True


def validate_changelog_content(changelog_content: str) -> bool:
    """Validate changelog has meaningful unreleased content.

    Args:
        changelog_content: Full content of CHANGELOG.md file.

    Returns:
        True if changelog validation passes.
    """
    lines = changelog_content.split("\n")
    unreleased_index = None

    for i, line in enumerate(lines):
        if "[Unreleased]" in line:
            unreleased_index = i
            break

    if unreleased_index is None:
        logger.warning("No [Unreleased] section found in CHANGELOG.md")
        logger.info("Consider adding release notes before creating a release")
        return True

    content_found = False
    for i in range(unreleased_index + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith("## [") and not line.startswith("## [Unreleased]"):
            break
        if (
            line
            and not line.startswith("#")
            and line not in ["", "### Added", "### Changed", "### Fixed"]
        ):
            content_found = True
            break

    if not content_found:
        logger.warning("[Unreleased] section in CHANGELOG.md appears empty")
        logger.info("Consider adding release notes before creating a release")
    else:
        logger.info("CHANGELOG.md has unreleased changes documented")

    return True


def check_changelog() -> bool:
    """Verify CHANGELOG.md exists and has content.

    Returns:
        True if changelog validation passes.
    """
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        logger.error("CHANGELOG.md not found")
        return False

    changelog_content = changelog_path.read_text()
    return validate_changelog_content(changelog_content)


def execute_check(name: str, check_func) -> bool:
    """Execute a single check and log results.

    Args:
        name: Name of the check being executed.
        check_func: Function to execute for the check.

    Returns:
        True if check passes, False otherwise.
    """
    logger.info("--- %s ---", name)
    return check_func()


def setup_logging() -> None:
    """Configure logging for the pre-release check script."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main() -> None:
    """Execute all pre-release checks and report results."""
    setup_logging()
    logger.info("Running pre-release checks...")

    checks = [
        ("Git Status", check_git_status),
        ("Tests", check_tests),
        ("Coverage", check_coverage),
        ("Code Quality", check_code_quality),
        ("Package Build", check_build),
        ("Changelog", check_changelog),
    ]

    failed_checks = []

    for name, check_func in checks:
        if not execute_check(name, check_func):
            failed_checks.append(name)

    logger.info("=" * 50)
    if failed_checks:
        logger.error("Pre-release checks FAILED")
        logger.error("Failed checks: %s", ", ".join(failed_checks))
        logger.info("Please fix the issues above before creating a release.")
        sys.exit(1)
    else:
        logger.info("All pre-release checks PASSED")
        logger.info("")
        logger.info("Ready for release!")
        logger.info("")
        logger.info("To create a release:")
        logger.info("  python scripts/release.py <version> -m 'Release message'")


if __name__ == "__main__":
    main()
