"""Unit tests for spotlight module with mocked subprocess."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_spotlight_returns_paths(mocker):
    mock_run = mocker.patch("mac_control_mcp.apple.spotlight.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "/Applications/Calculator.app\n/Applications/Calendar.app\n"
    from mac_control_mcp.apple.spotlight import spotlight_query

    result = spotlight_query("kind:app", limit=10)
    assert result["count"] == 2
    assert "/Applications/Calculator.app" in result["paths"]


@pytest.mark.unit
def test_spotlight_raises_on_nonzero_exit(mocker):
    mock_run = mocker.patch("mac_control_mcp.apple.spotlight.subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "mdfind: error"
    from mac_control_mcp.apple.spotlight import spotlight_query

    with pytest.raises(RuntimeError, match="mdfind error"):
        spotlight_query("kind:pdf")


@pytest.mark.unit
def test_spotlight_with_directory(mocker):
    mock_run = mocker.patch("mac_control_mcp.apple.spotlight.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "/tmp/test.txt\n"
    from mac_control_mcp.apple.spotlight import spotlight_query

    result = spotlight_query("test", directory="/tmp", limit=5)
    assert result["count"] == 1
    cmd = mock_run.call_args[0][0]
    assert "-onlyin" in cmd
    assert "/tmp" in cmd


@pytest.mark.unit
def test_spotlight_respects_limit(mocker):
    mock_run = mocker.patch("mac_control_mcp.apple.spotlight.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "\n".join(f"/path/{i}" for i in range(20))
    from mac_control_mcp.apple.spotlight import spotlight_query

    result = spotlight_query("kind:pdf", limit=3)
    assert result["count"] == 3
    assert len(result["paths"]) == 3
