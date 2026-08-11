"""Unit tests for mac_control_mcp.security."""

from __future__ import annotations

import pytest

from mac_control_mcp.security import check_osa_script

# OSA: forbidden patterns


@pytest.mark.unit
@pytest.mark.parametrize(
    "script",
    [
        'do shell script "rm -rf /tmp/foo"',
        'do shell script "rm -rf / --no-preserve-root"',
        'do shell script "sudo launchctl unload ..."',
        'do shell script "dd if=/dev/zero of=/dev/disk0"',
    ],
)
def test_osa_blocks_forbidden(script: str) -> None:
    with pytest.raises(ValueError, match="Forbidden OSA pattern"):
        check_osa_script(script)


# OSA: allowed patterns


@pytest.mark.unit
@pytest.mark.parametrize(
    "script",
    [
        'tell application "Notes" to make new note',
        'tell application "Calendar" to get name of every calendar',
        'return "hello"',
        "set x to 1 + 2\nreturn x",
    ],
)
def test_osa_allows_safe(script: str) -> None:
    check_osa_script(script)  # must not raise
