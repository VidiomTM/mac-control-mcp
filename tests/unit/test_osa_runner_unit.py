"""Unit tests for osa/runner.py with mocked subprocess."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_run_osa_applescript(mocker):
    mock_run = mocker.patch("mac_control_mcp.osa.runner.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "hello"
    from mac_control_mcp.osa.runner import run_osa

    result = run_osa('return "hello"', lang="applescript")
    assert result["output"] == "hello"
    assert result["lang"] == "applescript"


@pytest.mark.unit
def test_run_osa_jxa(mocker):
    mock_run = mocker.patch("mac_control_mcp.osa.runner.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "42"
    from mac_control_mcp.osa.runner import run_osa

    result = run_osa("42", lang="jxa")
    assert result["output"] == "42"
    cmd = mock_run.call_args[0][0]
    assert "-l" in cmd
    assert "JavaScript" in cmd


@pytest.mark.unit
def test_run_osa_returns_stdout_stripped(mocker):
    mock_run = mocker.patch("mac_control_mcp.osa.runner.subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "  hello world\n"
    from mac_control_mcp.osa.runner import run_osa

    result = run_osa('return "hello"')
    assert result["output"] == "hello world"


@pytest.mark.unit
def test_run_osa_raises_on_nonzero(mocker):
    mock_run = mocker.patch("mac_control_mcp.osa.runner.subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "error"
    from mac_control_mcp.osa.runner import run_osa

    with pytest.raises(RuntimeError, match="OSA error"):
        run_osa("bad script")


@pytest.mark.unit
def test_run_osa_timeout(mocker):
    mock_run = mocker.patch("mac_control_mcp.osa.runner.subprocess.run")
    import subprocess

    mock_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=1)
    from mac_control_mcp.osa.runner import run_osa

    with pytest.raises(RuntimeError, match="timed out"):
        run_osa("slow script", timeout_s=1)


@pytest.mark.unit
def test_run_osa_forbidden_script(mocker):
    from mac_control_mcp.osa.runner import run_osa

    with pytest.raises(ValueError, match="Forbidden"):
        run_osa('do shell script "rm -rf /"')
