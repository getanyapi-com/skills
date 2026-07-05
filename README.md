# AnyAPI agent skills

Official [Agent Skills](https://agentskills.io) for [AnyAPI](https://getanyapi.com) -
hundreds of scraping and data APIs through one gateway: **one key, USD pay-per-request,
normalized schemas, automatic fallback.**

The skills teach your agent the AnyAPI workflow (discover -> inspect -> run, cost
discipline, error handling); the bundled [MCP server](https://getanyapi.com/docs/mcp-server)
gives it live, authenticated tools. They work together, and the skill degrades
gracefully to plain REST when MCP isn't connected.

## Install

Fastest path with the official AnyAPI CLI:

```bash
npx -y anyapi-cli@latest init
```

`anyapi init` installs these agent skills, offers MCP registration, and runs signup if no
key is available. CLI repo: [getanyapi-com/cli](https://github.com/getanyapi-com/cli).

Any agent that supports Agent Skills (Claude Code, Codex, Cursor, Copilot, and others):

```bash
npx skills add getanyapi-com/skills
```

Claude Code, as a plugin (skill + MCP server in one step):

```bash
claude plugin marketplace add getanyapi-com/skills
claude plugin install anyapi@anyapi
```

Manual: copy `skills/anyapi/` into your agent's skills directory
(`.agents/skills/`, `~/.agents/skills/`, or `.claude/skills/`).

## Setup

For local agent use, run:

```bash
npx -y anyapi-cli@latest init
```

For application code, create or claim a dedicated key and expose it only as an environment
variable:

```bash
export ANYAPI_API_KEY=...
```

## Skills

| Skill | What it does |
|---|---|
| [`anyapi`](skills/anyapi/SKILL.md) | Discover, inspect, and run any API in the catalog; pricing and error semantics |
| [`anyapi-build`](skills/anyapi-build/SKILL.md) | Integrate AnyAPI into an app backend, mirror schemas, handle 402s, and smoke-test the call |

## Docs

- [getanyapi.com/docs](https://getanyapi.com/docs) - quickstart, MCP server, API reference
- [api.getanyapi.com/openapi.json](https://api.getanyapi.com/openapi.json) - machine-readable spec
