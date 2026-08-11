"""Unit tests for server tool handlers with mocked macOS dependencies."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_ax_snapshot_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("ax_snapshot").fn
    mocker.patch(
        "mac_control_mcp.ax.snapshot.snapshot_app",
        return_value={
            "role": "AXWindow",
            "title": "Test",
            "children": [
                {"role": "AXButton", "title": "OK"},
                {"role": "AXUnknown", "children": []},
            ],
        },
    )
    import json

    result = json.loads(fn())
    assert result["role"] == "AXWindow"
    assert result["title"] == "Test"
    assert "children" in result


@pytest.mark.unit
def test_screen_capture_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("screen_capture").fn
    mock_cap = mocker.patch(
        "mac_control_mcp.vision.capture.capture_screen",
        return_value={
            "data": "abc",
            "format": "png",
            "width": 100,
            "height": 200,
            "size_bytes": 123,
        },
    )
    result = fn(display=1, region=[0, 0, 100, 100])
    mock_cap.assert_called_once_with(
        display=1, region=(0, 0, 100, 100), window_id=None, scale=1.0, format="png"
    )
    assert result == {
        "data": "abc",
        "format": "png",
        "width": 100,
        "height": 200,
        "size_bytes": 123,
    }


@pytest.mark.unit
def test_screen_ocr_with_b64(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("screen_ocr").fn
    mocker.patch(
        "mac_control_mcp.vision.ocr.ocr_image_b64",
        return_value={"text": "hello", "observations": [], "count": 0},
    )
    import json

    result = json.loads(fn(image_b64="AAAA"))
    assert result["text"] == "hello"


@pytest.mark.unit
def test_screen_ocr_with_region(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("screen_ocr").fn
    mocker.patch(
        "mac_control_mcp.vision.ocr.ocr_screen_region",
        return_value={"text": "world", "observations": [], "count": 0},
    )
    import json

    result = json.loads(fn(region=[0, 0, 50, 50]))
    assert result["text"] == "world"


@pytest.mark.unit
def test_osa_search_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("osa_search").fn
    mocker.patch("mac_control_mcp.osa.kb.search", return_value=[{"id": "test"}])
    import json

    result = json.loads(fn(query="test", app="Mail", top_k=3))
    assert result == [{"id": "test"}]


@pytest.mark.unit
def test_osa_run_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("osa_run").fn
    mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "ok"})
    import json

    result = json.loads(fn(kb_id="test", args=["a"]))
    assert result == {"output": "ok"}


@pytest.mark.unit
def test_osa_exec_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("osa_exec").fn
    mocker.patch("mac_control_mcp.osa.runner.run_osa", return_value={"output": "done"})
    import json

    result = json.loads(fn(script='return "hi"', lang="applescript", timeout_s=10.0))
    assert result == {"output": "done"}


@pytest.mark.unit
def test_osa_exec_with_args(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("osa_exec").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.runner.run_osa", return_value={"output": "done"}
    )
    import json

    result = json.loads(fn(script='return "hi"', lang="jxa"))
    assert result == {"output": "done"}
    mock_runner.assert_called_once_with('return "hi"', lang="jxa", timeout_s=15.0)


@pytest.mark.unit
def test_mail_search_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("mail_search").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "done"})
    import json

    result = json.loads(fn(query="hello"))
    mock_runner.assert_called_once_with("mail_search_subject", args=["hello"])
    assert result == {"output": "done"}


@pytest.mark.unit
def test_mail_search_with_dates_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("mail_search").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "done"})
    import json

    result = json.loads(fn(query="hello", since="2026-01-01", until="2026-06-01"))
    mock_runner.assert_called_once_with(
        "mail_search_subject", args=["hello", "2026-01-01", "2026-06-01"]
    )
    assert result == {"output": "done"}


@pytest.mark.unit
def test_mail_recent_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("mail_recent").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "done"})
    import json

    result = json.loads(fn(limit=10))
    mock_runner.assert_called_once_with("mail_recent_messages", args=["10"])
    assert result == {"output": "done"}


@pytest.mark.unit
def test_mail_send_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("mail_send").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "sent"})
    import json

    result = json.loads(fn(to="a@b.com", subject="hi", body="there"))
    mock_runner.assert_called_once_with("mail_compose_send", args=["a@b.com", "hi", "there"])
    assert result == {"output": "sent"}


@pytest.mark.unit
def test_calendar_events_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("calendar_events").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "events"}
    )
    import json

    result = json.loads(fn(start="2026-01-01", end="2026-01-31"))
    mock_runner.assert_called_once_with(
        "calendar_list_events_range", args=["2026-01-01", "2026-01-31", "50"]
    )
    assert result == {"output": "events"}


@pytest.mark.unit
def test_calendar_create_event_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("calendar_create_event").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "created"}
    )
    import json

    result = json.loads(fn(title="Meet", start="2026-05-20 14:00", end="2026-05-20 15:00"))
    mock_runner.assert_called_once_with(
        "calendar_create_event", args=["Meet", "2026-05-20 14:00", "2026-05-20 15:00", ""]
    )
    assert result == {"output": "created"}


@pytest.mark.unit
def test_reminders_list_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("reminders_list").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "list"})
    import json

    result = json.loads(fn(list_name="Work", completed=True, limit=10))
    mock_runner.assert_called_once_with("reminders_list", args=["Work", "true", "10"])
    assert result == {"output": "list"}


@pytest.mark.unit
def test_reminders_add_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("reminders_add").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "added"})
    import json

    result = json.loads(fn(name="Test", list_name="Work", due_date="2026-06-01", notes="note"))
    mock_runner.assert_called_once_with(
        "reminders_add", args=["Test", "Work", "2026-06-01", "note"]
    )
    assert result == {"output": "added"}


@pytest.mark.unit
def test_notes_search_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("notes_search").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "notes"})
    import json

    result = json.loads(fn(query="test"))
    mock_runner.assert_called_once_with("notes_search", args=["test", "", "20"])
    assert result == {"output": "notes"}


@pytest.mark.unit
def test_notes_get_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("notes_get").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "content"}
    )
    import json

    result = json.loads(fn(note_id="123"))
    mock_runner.assert_called_once_with("notes_get", args=["123"])
    assert result == {"output": "content"}


@pytest.mark.unit
def test_notes_create_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("notes_create").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "created"}
    )
    import json

    result = json.loads(fn(title="Title", body="Body"))
    mock_runner.assert_called_once_with("notes_create", args=["Title", "Body", ""])
    assert result == {"output": "created"}


@pytest.mark.unit
def test_messages_recent_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("messages_recent").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "msgs"})
    import json

    result = json.loads(fn(handle="John"))
    mock_runner.assert_called_once_with("messages_recent", args=["John", "20"])
    assert result == {"output": "msgs"}


@pytest.mark.unit
def test_messages_send_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("messages_send").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "sent"})
    import json

    result = json.loads(fn(handle="123", text="hello"))
    mock_runner.assert_called_once_with("messages_send", args=["123", "hello"])
    assert result == {"output": "sent"}


@pytest.mark.unit
def test_contacts_search_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("contacts_search").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "contacts"}
    )
    import json

    result = json.loads(fn(query="John"))
    mock_runner.assert_called_once_with("contacts_search", args=["John", "20"])
    assert result == {"output": "contacts"}


@pytest.mark.unit
def test_spotlight_query_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("spotlight_query").fn
    mocker.patch(
        "mac_control_mcp.apple.spotlight.spotlight_query", return_value={"paths": [], "count": 0}
    )
    import json

    result = json.loads(fn(predicate="kind:pdf"))
    assert result["count"] == 0


@pytest.mark.unit
def test_finder_tags_get_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("finder_tags_get").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "tags"})
    import json

    result = json.loads(fn(path="/tmp"))
    mock_runner.assert_called_once_with("finder_list_tags", args=["/tmp"])
    assert result == {"output": "tags"}


@pytest.mark.unit
def test_finder_tags_set_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("finder_tags_set").fn
    mock_runner = mocker.patch("mac_control_mcp.osa.kb.run_by_id", return_value={"output": "set"})
    import json

    result = json.loads(fn(path="/tmp", tags=["red", "blue"]))
    mock_runner.assert_called_once_with("finder_set_tags", args=["/tmp", "red,blue"])
    assert result == {"output": "set"}


@pytest.mark.unit
def test_quicklook_mocked(mcp_server, mocker):
    fn = mcp_server._tool_manager.get_tool("quicklook").fn
    mock_runner = mocker.patch(
        "mac_control_mcp.osa.kb.run_by_id", return_value={"output": "opened"}
    )
    import json

    result = json.loads(fn(path="/tmp/test.pdf"))
    mock_runner.assert_called_once_with("quicklook_file", args=["/tmp/test.pdf"])
    assert result == {"output": "opened"}
