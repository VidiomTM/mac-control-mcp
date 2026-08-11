# mac-control-mcp

macOS MCP server that **fills the gaps in [cua-driver](https://cua.ai/docs/cua-driver)** — it does NOT re-implement what cua-driver already does.

**Use cua-driver for:** clicking, typing, scrolling, hotkeys, window listing, focus handling, verify-by-resnapshot — the action layer. It works backgrounded, without stealing focus.

**Use this server for:** the places cua-driver can't see:

| Gap in cua-driver | What this server provides |
|---|---|
| Window-mapped AX resolver returns empty (`degraded:true`, `ax_unresolved`) for **Catalyst / iOS-on-Mac / AppleSystemUIService** apps | `ax_snapshot(app=...)` — raw, app-name-mapped AX tree walk (read-only, no input post) |
| No way to turn pixels into text when AX is blank (**Electron, canvas, games**) | `screen_capture` + `screen_ocr` — on-device Vision.framework OCR with word bounding boxes |
| No AppleScript/JXA layer | `osa_search` / `osa_run` / `osa_exec` + pre-vetted knowledge base |
| No Apple-app integrations | `mail_*`, `calendar_*`, `reminders_*`, `notes_*`, `messages_*`, `contacts_search`, `finder_tags_*`, `quicklook` |
| No Spotlight / mdfind file search | `spotlight_query` |

**This server is READ-ONLY for input.** It never clicks, types, or posts keys. Output (AX frames, OCR bounding boxes) is meant to be turned into **cua-driver actions** — e.g. feed an OCR bbox center or an AX frame into a cua-driver `click`.

## Requirements

- macOS 12+ (Monterey or later)
- Python 3.11+
- [cua-driver](https://cua.ai/docs/cua-driver) for the action side

## Install & run

```bash
uvx mac-control-mcp
```

Or from source:
```bash
uvx --from . mac-control-mcp
```

## Claude Desktop config

Register both servers:

```json
{
  "mcpServers": {
    "mac-control": {
      "command": "uvx",
      "args": ["mac-control-mcp"]
    },
    "cua-driver": {
      "command": "cua-driver",
      "args": ["mcp"]
    }
  }
}
```

## Required macOS permissions

Grant these in **System Settings → Privacy & Security**:

| Permission | Required by |
|---|---|
| Accessibility | `ax_snapshot` |
| Automation | AppleScript/JXA for Mail, Calendar, etc. |
| Screen Recording | `screen_capture`, `screen_ocr` |
| Full Disk Access | `spotlight_query` on all locations |
| Contacts | `contacts_search` |

## Tools

### AX (read-only snapshot)
- `ax_snapshot(app?, max_depth, budget_chars)` — pruned element tree with screen coords. Use where cua-driver's window-mapped AX can't bind (Catalyst/iOS-on-Mac/AppleSystemUIService). Coordinates go to cua-driver clicks (px rung).

### Vision (screenshot + OCR — requires Screen Recording)
- `screen_capture(display?, region?, window_id?, scale?, format?)` → base64 image
- `screen_ocr(region?, image_b64?)` — Vision.framework OCR. Use as fallback for Electron/game apps where AX tree is unavailable; bboxes give click targets for cua-driver.

### OSA (AppleScript / JXA)
- `osa_search(query, app?, top_k?)` — fuzzy search knowledge base
- `osa_run(kb_id, args?)` — run verified script by ID
- `osa_exec(script, lang?, timeout_s?)` — raw fallback (blocks destructive patterns)

### Apple apps (paginated, OS-side filtered)
- `mail_search(query, since?, until?, limit?)`
- `mail_recent(limit?)`
- `mail_send(to, subject, body)`
- `calendar_events(start, end, limit?)`
- `calendar_create_event(title, start, end, calendar_name?)`
- `reminders_list(list_name?, completed?, limit?)`
- `reminders_add(name, list_name?, due_date?, notes?)`
- `notes_search(query, folder?, limit?)`
- `notes_get(note_id)`
- `notes_create(title, body, folder?)`
- `messages_recent(handle?, limit?)`
- `messages_send(handle, text)`
- `contacts_search(query, limit?)`
- `spotlight_query(predicate, directory?, limit?)` — raw mdfind predicates (calls mdfind directly, not via KB)
- `finder_tags_get(path)`
- `finder_tags_set(path, tags)`
- `quicklook(path)`

### Removed (use cua-driver instead)
These used to live here but were removed because cua-driver does them better:

- `ax_click` / `ax_type` / `ax_scroll` / `ax_hotkey` → cua-driver `click`/`type_text`/`scroll`/`press_key`/`hotkey` (backgrounded, no focus steal)
- `ax_system_ui` (Spotlight / menu bar / Control Center / Launchpad) → cua-driver drives menu bars natively; Spotlight is a `hotkey(["cmd","space"])` there
- `screen_list_windows` → cua-driver `list_windows`
- `screen_wait_for_change` → cua-driver verify-by-resnapshot loop

## Recommended usage pattern

```
1. ax_snapshot(app="Tapo") or screen_capture + screen_ocr → find target (map AX frame / OCR bbox → screen coords)
2. cua-driver click{x, y}   # background, no focus steal
3. cua-driver get_window_state → verify state change
```

## Security

- `osa_exec` blocks destructive patterns: `rm -rf /`, `sudo`, `dd if=` in shell scripts
- KB scripts (`osa_run`) are pre-vetted; only `osa_exec` allows arbitrary scripts
- All subprocess calls use list-form args — no `shell=True` injection surface

## Adding knowledge base scripts

Add YAML files to `src/mac_control_mcp/osa/knowledge/`. Format:

```yaml
- id: unique_id
  app: AppName
  lang: applescript  # or jxa
  summary: One-line description for fuzzy search
  tags: [tag1, tag2]
  args:
    - {name: arg_name, description: what it does}
  script: |
    on run argv
        -- Access positional args: item 1 of argv, item 2 of argv, ...
        ...
    end run
```

For JXA entries, access args via `argv[0]`, `argv[1]`, etc. Scripts are executed via `osascript -e <script> -- <args>`.
