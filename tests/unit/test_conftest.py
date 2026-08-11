"""Tests for conftest skip logic."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_pytest_collection_modifyitems_skips_non_darwin(mocker):
    items = []
    for _ in ("integration", "e2e"):
        item = mocker.MagicMock(spec=pytest.Item)
        item.get_closest_marker.return_value = mocker.MagicMock()
        item.add_marker = mocker.MagicMock()
        items.append(item)

    mocker.patch("sys.platform", "linux")
    from tests.conftest import pytest_collection_modifyitems

    pytest_collection_modifyitems(items)

    for item in items:
        item.add_marker.assert_called_once()
        args, _ = item.add_marker.call_args
        marker = args[0]
        assert marker.kwargs.get("reason") == "macOS only" or marker.args[0] == "macOS only"


@pytest.mark.unit
def test_pytest_collection_modifyitems_skips_live_tests_0(mocker):
    items = []
    for _ in ("integration", "e2e"):
        item = mocker.MagicMock(spec=pytest.Item)
        item.get_closest_marker.return_value = mocker.MagicMock()
        item.add_marker = mocker.MagicMock()
        items.append(item)

    mocker.patch("sys.platform", "darwin")
    mocker.patch.dict("os.environ", {"LIVE_TESTS": "0"})
    from tests.conftest import pytest_collection_modifyitems

    pytest_collection_modifyitems(items)

    for item in items:
        item.add_marker.assert_called_once()


@pytest.mark.unit
def test_mcp_server_fixture(mcp_server):
    assert mcp_server is not None
    assert mcp_server.name == "mac-control"
