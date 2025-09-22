#!/usr/bin/env python3
"""
UV Lock Sync Utility for PyCommon Package Updates

This script synchronizes uv.lock files across Python services when pycommon is updated.
It can be used both as a standalone script and as part of the CI/CD pipeline.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Python services that use pycommon
PYTHON_SERVICES = [
    "AleatorikUI.Noti",
    "AleatorikUI.DataTransfer",
    "AleatorikUI.SmartReport",
    "AleatorikUI.SmartEditor",
    "AleatorikUI.SchedAgent",
]

def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"Error: {e.stderr}")
        return False, e.stderr

def check_uv_project(service_path: Path) -> bool:
    """Check if a service directory contains a valid uv project."""
    pyproject_file = service_path / "pyproject.toml"
    uv_lock_file = service_path / "uv.lock"
    uv_lock_dev_file = service_path / "uv.lock.dev"

    if not pyproject_file.exists():
        logger.warning(f"No pyproject.toml found in {service_path}")
        return False

    if not uv_lock_file.exists():
        logger.warning(f"No uv.lock found in {service_path}")
        return False

    if not uv_lock_dev_file.exists():
        logger.warning(f"No uv.lock.dev found in {service_path}")
        return False

    return True

def update_pycommon_dependency(service_path: Path, version: str, use_testpypi: bool = True) -> bool:
    """Update pycommon dependency in a service."""
    logger.info(f"Updating pycommon to {version} in {service_path.name}")

    if use_testpypi:
        # Run uv lock with prerelease allowed
        cmd = [
            "uv", "lock",
            "--upgrade-package", f"aleatorik-pycommon=={version}",
            "--prerelease=if-necessary-or-explicit",
            "--index-url", "https://test.pypi.org/simple/",
            "--extra-index-url", "https://pypi.org/simple",
            "--index-strategy", "unsafe-best-match"
        ]
    else:
        cmd = [
            "uv", "lock",
            "--upgrade-package", f"aleatorik-pycommon=={version}",
        ]

    success, output = run_command(cmd, cwd=service_path)
    if not success:
        logger.error(f"Failed to update dependency in {service_path.name}")
        logger.error(output)
        return False

    if use_testpypi:
        # Copy uv.lock -> uv.lock.dev
        uv_lock = service_path / "uv.lock"
        uv_lock_dev = service_path / "uv.lock.dev"
        if uv_lock.exists():
            uv_lock_dev.write_text(uv_lock.read_text(encoding="utf-8"), encoding="utf-8")
            logger.info(f"Updated uv.lock.dev for {service_path.name}")

            # Reset uv.lock back (so prod lock remains stable)
            run_command(["git", "restore", "uv.lock"], cwd=service_path)

    logger.info(f"Successfully updated {service_path.name}")
    return True

def sync_service_dependencies(
    backend_repo_path: Path,
    version: str,
    services: list[str] | None = None,
    use_testpypi: bool = False
) -> list[str]:
    """Sync pycommon dependencies across specified services."""

    if services is None:
        services = PYTHON_SERVICES

    updated_services = []

    for service in services:
        service_path = backend_repo_path / service

        if not service_path.exists():
            logger.warning(f"Service directory not found: {service_path}")
            continue

        if not check_uv_project(service_path):
            logger.warning(f"Skipping {service} - not a valid uv project")
            continue

        if update_pycommon_dependency(service_path, version, use_testpypi):
            updated_services.append(service)

    return updated_services

def main():
    """Main entry point for the UV sync utility."""
    parser = argparse.ArgumentParser(description="Sync uv.lock files after pycommon update")
    parser.add_argument("--version", required=True, help="PyCommon version to sync")
    parser.add_argument("--publish-target", choices=["testpypi", "pypi"], default="testpypi",
                       help="Target PyPI repository (default: testpypi)")
    args = parser.parse_args()

    use_testpypi = args.publish_target == "testpypi"

    logger.info(f"Starting UV sync for pycommon version {args.version}")
    logger.info(f"Using TestPyPI: {use_testpypi}")

    # Navigate back to backend-repo root (3 levels up from pycommon/pylogger/deploy/)
    backend_repo_path = Path(__file__).parent.parent.parent.parent
    logger.info(f"Backend repo path: {backend_repo_path}")

    updated_services = sync_service_dependencies(
        backend_repo_path,
        args.version,
        PYTHON_SERVICES,
        use_testpypi
    )

    if updated_services:
        logger.info(f"Successfully updated {len(updated_services)}/{len(PYTHON_SERVICES)} services.")
    else:
        logger.warning("No services were updated")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())