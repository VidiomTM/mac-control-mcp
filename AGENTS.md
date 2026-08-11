# mac-control-mcp Agent Rules

## Python Stack
- **Package manager:** `uv` only (no pip, pipx, poetry, conda)
- **Lint:** `uvx ruff check`
- **Format:** `uvx ruff format`
- **Type check:** `uvx pyright`
- **Test:** `uv run pytest --cov --cov-branch --cov-fail-under=90`
- **Mutation:** `uv run mutmut run`

## CI/CD
- **SonarQube (local):** Docker container `sonarqube` at `http://127.0.0.1:9001`, scanner `sonar-scanner` (homebrew). Token: repo secret `SONAR_TOKEN`.
- **PR gate:** runs on self-hosted macOS arm64 runner, unit tests only (integration/e2e auto-skipped on non-macOS)
- **Merge gate:** adds full mutation testing, SonarQube (local) scan
- **OpenCodeReview:** sole automated reviewer (`code-review.yml`, `ocr-review.yml`).

## Positioning (important)
This project is a **read-only gap-filler for cua-driver**. It does NOT click,
type, scroll, or send keys — that belongs to cua-driver (backgrounded, no focus
steal). This server fills cua-driver's blind spots: raw AX snapshots for
Catalyst / iOS-on-Mac apps, screen capture + on-device OCR for AX-empty
(Electron/canvas/game) apps, AppleScript/JXA + Apple-app data, and Spotlight
mdfind. Never re-add `ax_click`/`ax_type`/`ax_scroll`/`ax_hotkey`/`ax_system_ui`/
`screen_list_windows`/`screen_wait_for_change`/`check_ssrf` — they were removed
because cua-driver covers them or they were brittle.

## macOS-Specific Testing
- Unit tests (`@pytest.mark.unit`) are pure logic — no system calls, run anywhere
- Integration tests (`@pytest.mark.integration`) require macOS + accessibility permissions
- E2E tests (`@pytest.mark.e2e`) require full macOS stack
- Set `LIVE_TESTS=0` to skip live macOS calls

## Git Workflow
- No direct pushes to `main`/`master`
- Branch: `feature/*`, `fix/*`, `chore/*`
- PR → OCR automated review → squash merge
