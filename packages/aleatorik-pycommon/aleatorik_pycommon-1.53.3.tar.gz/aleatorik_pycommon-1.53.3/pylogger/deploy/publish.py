#!/usr/bin/env python3
"""
PyCommon Package Publishing Utility

This script handles the publishing of pycommon packages to PyPI or TestPyPI
with automatic versioning based on git tags and semantic versioning rules.
"""

import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd: list, cwd: Optional[Path] = None) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"Error: {e.stderr}")
        return False, e.stderr.strip()

def parse_version(version_str: str) -> tuple[str, bool]:
    """Parse version string and determine if it's a pre-release."""
    # Remove 'v' prefix if present
    if version_str.startswith('v'):
        version_str = version_str[1:]

    # Check if it's a stable version (x.y.z format)
    stable_pattern = r'^(\d+)\.(\d+)\.(\d+)$'
    if re.match(stable_pattern, version_str):
        return version_str, False

    # Pre-release patterns: .rcN, .aN, .bN (where N is a number)
    # Examples: 1.0.0.rc1, 1.0.0.dev1, 1.0.0.dev2
    prerelease_pattern = r'^(\d+)\.(\d+)\.(\d+)\.(rc|dev)(\d+)$'
    if re.match(prerelease_pattern, version_str):
        return version_str, True

    raise ValueError(f"Invalid version format: {version_str}. Expected: X.Y.Z or X.Y.Z.[rc|dev]N")

def update_pyproject_version(pyproject_path: Path, version: str) -> bool:
    """Update version in pyproject.toml file."""
    try:
        content = pyproject_path.read_text(encoding="utf-8")

        # Update version line
        updated_content = re.sub(
            r'^version = ".*"$',
            f'version = "{version}"',
            content,
            flags=re.MULTILINE
        )

        pyproject_path.write_text(updated_content)
        logger.info(f"Updated pyproject.toml version to {version}")
        return True
    except Exception as e:
        logger.error(f"Failed to update pyproject.toml: {e}")
        return False

def build_package() -> bool:
    """Build the package using uv and build."""
    logger.info("Building package...")

    pycommon_repo_path = Path(__file__).parent.parent.parent
    logger.info(f"PyCommon repo path: {pycommon_repo_path}")

    # Install build dependencies
    success, _ = run_command(["uv", "add", "--dev", "build", "twine"], cwd=pycommon_repo_path)
    if not success:
        logger.error("Failed to install build dependencies")
        return False

    # Build package
    success, _ = run_command(["uv", "run", "python", "-m", "build", "--sdist", "--wheel"], cwd=pycommon_repo_path)
    if not success:
        logger.error("Failed to build package")
        return False

    logger.info("Package built successfully")
    return True

def publish_package(target: str, api_token: str) -> bool:
    """Publish package to PyPI or TestPyPI."""
    logger.info(f"Publishing to {target}...")

    pycommon_repo_path = Path(__file__).parent.parent.parent

    if target == "testpypi":
        repo_url = "https://test.pypi.org/legacy/"
    elif target == "pypi":
        repo_url = "https://upload.pypi.org/legacy/"
    else:
        logger.error(f"Unknown target: {target}")
        return False

    # One-liner command: build + upload
    cmd = (
        f"uv run python -m build "
        f"&& uv run twine upload --disable-progress-bar --repository-url {repo_url} dist/* "
        f"-u __token__ -p {api_token}"
    )

    # Run twine upload with environment variables
    try:
        subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            cwd=pycommon_repo_path
        )
        logger.info("Package published successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to publish package: {e.stderr}")
        return False

def main():
    """Main entry point for the publish utility."""
    parser = argparse.ArgumentParser(description="Publish pycommon package")
    parser.add_argument("--version", help="Specific version to publish")
    parser.add_argument("--target", choices=["pypi", "testpypi"],
                       help="Publishing target (auto-detected from version if not specified)")
    parser.add_argument("--api-token", help="API token for publishing to PyPI or TestPyPI")
    args = parser.parse_args()

    print(args)

    # Determine version
    if args.version:
        version = args.version
    else:
        logger.error("Version is required")
        return 1

    # Parse version and determine target
    try:
        clean_version, is_prerelease = parse_version(version)
    except ValueError as e:
        logger.error(str(e))
        return 1

    target = args.target
    if not target:
        target = "testpypi" if is_prerelease else "pypi"

    logger.info(f"Version: {clean_version}")
    logger.info(f"Pre-release: {is_prerelease}")
    logger.info(f"Target: {target}")

    # Check for API token
    api_token = args.api_token
    if not api_token:
        logger.error("API token is required for publishing")
        return 1

    # Update pyproject.toml
    logger.info(f"Current working directory: {Path.cwd()}")
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    logger.info(f"pyproject.toml path: {pyproject_path}")
    if not pyproject_path.exists():
        logger.error(f"pyproject.toml not found at {pyproject_path}")
        return 1

    if not update_pyproject_version(pyproject_path, clean_version):
        return 1

    # Build package
    if not build_package():
        return 1

    # Publish package
    if not publish_package(target, api_token):
        return 1

    logger.info(f"✅ Successfully published pycommon {clean_version} to {target}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())