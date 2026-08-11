"""Unit tests for kb.run_by_id with mocked run_osa."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_run_by_id_mocked(mocker):
    mocker.patch("mac_control_mcp.osa.runner.run_osa", return_value={"output": "ok"})
    from mac_control_mcp.osa.kb import run_by_id

    result = run_by_id("reminders_add", args=["test"])
    assert result["output"] == "ok"


@pytest.mark.unit
def test_run_by_id_raises_for_missing(mocker):
    from mac_control_mcp.osa.kb import run_by_id

    with pytest.raises(KeyError, match="nope"):
        run_by_id("nope")


@pytest.mark.unit
def test_get_returns_entry():
    from mac_control_mcp.osa.kb import get

    entry = get("reminders_add")
    assert entry["id"] == "reminders_add"
    assert "script" in entry
