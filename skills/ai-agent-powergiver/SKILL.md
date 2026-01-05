---
name: ai-agent-powergiver
description: Permission presets for coding assistants (Copilot/Claude) that auto-approve common dev commands while blocking destructive ones, using JSON templates in /Users/kenyansong/Desktop/CodeEnv/vikAISkills/AI-Agent-PowerGiver.
metadata:
  short-description: Copilot/Claude auto-approve settings with guardrails
---

# AI Agent PowerGiver

Use these templates when you want Copilot or Claude Code to run most development commands without prompting, while keeping guardrails for destructive/network-sensitive actions.

## Files
- Copilot: `/Users/kenyansong/Desktop/CodeEnv/vikAISkills/AI-Agent-PowerGiver/copilot-ai-agent/copilot-settings.json`
- Claude: `/Users/kenyansong/Desktop/CodeEnv/vikAISkills/AI-Agent-PowerGiver/claude-ai-agent/claude-settings.json`
- Example local Claude config already present in repo: `/Users/kenyansong/Desktop/CodeEnv/vikAISkills/.claude/settings.local.json`

## Copilot setup (VS Code)
1. Open the Copilot settings JSON above and merge it into your user or workspace `settings.json`.
2. Key flags: `chat.tools.global.autoApprove` + terminal auto-approve enabled; explicit denylist for destructive commands (`rm`, `chmod`, `curl`, `sudo`, etc.).
3. Restart VS Code / Copilot chat to apply.

## Claude Code setup
1. Copy the Claude JSON above into `~/.claude/settings.local.json` (or workspace `.claude/settings.local.json`). Overwrite or merge as needed.
2. This preset allows broad Bash/tools/WebFetch/WebSearch while you keep explicit control over additional permissions.
3. Restart Claude Code to pick up the new permissions.

## Safety notes
- These presets intentionally approve most dev tooling; destructive commands remain blocked by default.
- Review deny/allow lists before enabling in sensitive environments.
