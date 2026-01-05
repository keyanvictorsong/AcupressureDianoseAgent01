---
name: browser-automation-tools
description: Playwright-based CLI for quick browsing tasks (Google search, screenshot, page text/html) using browser_tool.py in /Users/kenyansong/Desktop/CodeEnv/vikAISkills/Browser-Automation-Tools.
metadata:
  short-description: Playwright CLI for search/screenshot/text/html
---

# Browser Automation Tools

Use this when you need fast browser automation without writing new scripts. Commands run against `browser_tool.py` at `/Users/kenyansong/Desktop/CodeEnv/vikAISkills/Browser-Automation-Tools/browser_tool.py`.

## Dependencies
- Python 3, `pip install playwright`, then `playwright install chromium`.
- Requires network access; headless Chromium is launched by Playwright.

## Quick commands
- Search: `python3 browser_tool.py search "<query>"`
- Screenshot: `python3 browser_tool.py screenshot "<url>" "<output.png>"`
- Page text: `python3 browser_tool.py get_text "<url>"`
- Page HTML: `python3 browser_tool.py get_html "<url>"`

Outputs are JSON with `timestamp`; screenshot saves to the specified path.

## Notes
- Script also exposes `click_and_extract(url, click_selector, extract_selector)` for programmatic use (not wired to CLI).
- Keep usage respectful of target sites; avoid login-protected flows.
