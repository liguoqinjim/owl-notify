"""Smoke tests for owl-notify."""

import subprocess
import sys


def test_import():
    """Test that owl_notify can be imported."""
    import owl_notify

    assert hasattr(owl_notify, "__version__")
    assert owl_notify.__version__ == "0.1.0"
    assert hasattr(owl_notify, "Notify")


def test_cli_help():
    """Test that CLI help works."""
    result = subprocess.run(
        [sys.executable, "-m", "owl_notify.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Send notifications" in result.stdout
    assert "--platform" in result.stdout
    assert "--config" in result.stdout


def test_cli_version():
    """Test that CLI version works."""
    result = subprocess.run(
        [sys.executable, "-m", "owl_notify.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
