# AnyAPI agent skills

Official [Agent Skills](https://agentskills.io) for [AnyAPI](https://getanyapi.com) —
hundreds of scraping and data APIs through one gateway: **one key, USD pay-per-request,
normalized schemas, automatic failover.**

The skill teaches your agent the AnyAPI workflow (discover → inspect → run, cost
discipline, error handling); the bundled [MCP server](https://docs.getanyapi.com/mcp)
gives it live, authenticated tools. They work together, and the skill degrades
gracefully to plain REST when MCP isn't connected.

## Install

Any agent that supports Agent Skills (Claude Code, Codex, Cursor, Copilot, …):

```bash
npx skills add getanyapi/skills
```

Claude Code, as a plugin (skill + MCP server in one step):

```bash
claude plugin marketplace add getanyapi/skills
claude plugin install anyapi@anyapi
```

Manual: copy `skills/anyapi/` into your agent's skills directory
(`.agents/skills/`, `~/.agents/skills/`, or `.claude/skills/`).

## Setup

1. Create an API key at [app.getanyapi.com](https://app.getanyapi.com) and fund your
   USD wallet.
2. Export it: `export ANYAPI_API_KEY=...`

## Skills

| Skill | What it does |
|---|---|
| [`anyapi`](skills/anyapi/SKILL.md) | Discover, inspect, and run any API in the catalog; pricing and error semantics |

## Docs

- [docs.getanyapi.com](https://docs.getanyapi.com) — quickstart, MCP server, API reference
- [api.getanyapi.com/openapi.json](https://api.getanyapi.com/openapi.json) — machine-readable spec
