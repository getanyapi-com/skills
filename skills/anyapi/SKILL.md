---
name: anyapi
description: Accesses hundreds of scraping and data APIs (social media, search results, web data) through AnyAPI's unified gateway with one API key and USD pay-per-request pricing. Use when the user needs third-party data - Instagram, TikTok, YouTube, Reddit, Facebook profiles/posts/comments, Google search results, web scraping - or mentions AnyAPI.
license: Apache-2.0
metadata:
  author: AnyAPI
  version: "0.2.0"
---

# AnyAPI - agent onboarding

AnyAPI is a unified marketplace for scraping and data APIs: **any API, one wallet, USD, no subscriptions.** You reach hundreds of APIs through one interface and one key, pay per request in real dollars, and AnyAPI normalizes schemas and fails over automatically on error. The provider is always reported as **AnyAPI**.

## 1. Get credentials

Every direct API call uses an `aa_live_...` key in an `Authorization: Bearer` header. Prefer the `ANYAPI_API_KEY` environment variable for applications and automation. The CLI also reads `~/.anyapi/config.json`.

### Self-signup (zero-human fast path)

If `ANYAPI_API_KEY` is not already set, mint a starter key immediately. First ask the human which email address they want this AnyAPI account tied to, then pass it as `sponsorEmail`:

    curl -s -X POST https://api.getanyapi.com/agent/signup \
      -H "Content-Type: application/json" \
      -d '{ "sponsorEmail": "<their email>", "label": "my-agent" }'

The response returns `secret` (your `aa_live_...` key, shown once), `capUsd` (your starting spend cap), `claimToken`, and `expiresAt`. Put `secret` in `ANYAPI_API_KEY` and start calling immediately. Keep the `claimToken`; never print the `secret`.

This starter key is **capped at a small USD amount and expires in 7 days** until a human claims it. Until then, exceeding the cap returns HTTP 402 `key_cap_exceeded`. To lift the cap, make the key permanent, and add the one-time **$1** account credit, tell the human to sign in at https://getanyapi.com/dashboard with that email, open **API keys -> Claim agent key**, and paste the `claimToken`. Claiming upgrades the same key already in `ANYAPI_API_KEY` and moves it onto their funded wallet. If you passed `sponsorEmail`, that address also gets an approve/block email.

### Dashboard key

A human who is already signed in at https://getanyapi.com can create an uncapped, non-expiring key directly at https://getanyapi.com/dashboard/keys and hand it to you via `ANYAPI_API_KEY`. New accounts get the same one-time USD credit.

## 2. Choose your path

### Path A - CLI

Use the official CLI when you want installable agent skills, local credentials, catalog discovery, and output files without writing HTTP glue.

    npx -y anyapi-cli@latest init

`anyapi init` installs the AnyAPI agent skills into detected agents, offers MCP registration, and runs `anyapi signup` if no key is available. `anyapi signup` mints the key for you and saves it to `~/.anyapi/config.json`.

Command cheat sheet:

    anyapi signup [--email <sponsorEmail>] [--label]
    anyapi login --api-key aa_live_...
    anyapi search <query>
    anyapi list [--category]
    anyapi describe <sku>
    anyapi run <sku> --input '<json>' [--fields a,b] [--max-items N] [--summary] [-o path] [--json]
    anyapi balance
    anyapi claim
    anyapi init [--all] [--yes]

By default, `anyapi run` writes the result to `.anyapi/<sku>-<timestamp>.json` and prints the path plus `costUsd`. Authentication lookup order is `--api-key` flag, `ANYAPI_API_KEY` env, `~/.anyapi/config.json`, then self-signup.

Repo: https://github.com/getanyapi-com/cli

### Path B - MCP

Use MCP for clients that cannot run a shell: hosted chat agents, no-code and workflow tools, and any runtime where the model cannot invoke a command line. For those, MCP is the way to expose AnyAPI as native tools. If your agent has a shell (Claude Code, Cursor, Codex, and similar), prefer the CLI in Path A: it keeps these tool schemas out of your context window and writes results to files instead of into the conversation.

Connect any MCP client to the streamable HTTP endpoint:

    https://api.getanyapi.com/mcp

Authenticate with `Authorization: Bearer aa_live_...`. Tools exposed:

- `list_apis` - discover APIs. Optional `query` and `category` filters. Token-light because schemas are omitted.
- `get_api` - full definition of one API, including normalized input/output JSON Schema. Args: `sku_id`.
- `run_api` - execute an API. Args: `sku_id`, `input` (object matching the input schema). Returns `output`, `provider` ("AnyAPI"), `costUsd`, and `items`. Supports the context-budget controls in section 4.
- `get_balance` - remaining wallet balance in USD for your key.

### Path C - Integrate into your app

Use the REST run endpoint from your app when AnyAPI should become part of the product flow rather than an agent-only tool.

Build workflow:

1. Inspect the project and decide where the API call belongs. For browser apps, keep the AnyAPI key on your server and expose only your own backend route to the browser.
2. Mint a **dedicated key for this app** using self-signup or the dashboard. Store it only in the `ANYAPI_API_KEY` environment variable. Never hardcode it and never commit it.
3. Fetch `GET https://api.getanyapi.com/v1/apis/{sku}` and mirror the input schema in your form, job, or typed wrapper.
4. Write the call site against `POST https://api.getanyapi.com/v1/run/{sku}`.
5. Handle HTTP 402 `key_cap_exceeded` by asking the human to claim or fund the key.
6. Smoke-test one cheap call and verify the response shape, `provider: "AnyAPI"`, and `costUsd`.

Concrete TypeScript fetch example:

    type RunResponse<TOutput> = {
      output: TOutput;
      provider: "AnyAPI";
      costUsd: number;
      items?: number;
    };

    export async function runAnyApi<TOutput>(
      sku: string,
      input: Record<string, unknown>,
    ): Promise<RunResponse<TOutput>> {
      const apiKey = process.env.ANYAPI_API_KEY;
      if (!apiKey) throw new Error("Missing ANYAPI_API_KEY");

      const res = await fetch(
        "https://api.getanyapi.com/v1/run/" + encodeURIComponent(sku),
        {
          method: "POST",
          headers: {
            Authorization: "Bearer " + apiKey,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(input),
        },
      );

      if (res.status === 402) {
        throw new Error("AnyAPI key cap exceeded. Claim or fund the key.");
      }
      if (!res.ok) {
        throw new Error("AnyAPI run failed: " + res.status + " " + (await res.text()));
      }
      return (await res.json()) as RunResponse<TOutput>;
    }

For typed clients, generate from https://api.getanyapi.com/openapi.json.

### Path D - REST

Use REST when you want direct HTTP calls from scripts, backends, jobs, or custom agent tooling.

Base URL `https://api.getanyapi.com/v1`, Bearer auth on every request.

    curl -X POST https://api.getanyapi.com/v1/run/{sku} \
      -H "Authorization: Bearer aa_live_..." \
      -H "Content-Type: application/json" \
      -d '{ ...input matching the API schema... }'

Other endpoints: `GET /apis` (list), `GET /apis/{sku}` (describe), `GET /balance`. The public catalog (no auth) is at https://api.getanyapi.com/catalog; a typed OpenAPI document is at https://api.getanyapi.com/openapi.json.

## 3. The call loop

1. `list_apis` (or read the catalog) to find a SKU.
2. `get_api` to read its input/output schema.
3. `run_api` with input that matches the schema. On a schema mismatch you get the fields and an example back so you can self-correct without another round-trip, with no charge. `costUsd` and `items` tell you what you paid and received.

## 4. Context-budget controls (keep results from flooding your context)

`run_api` returns the full normalized result by default. To return less, pass any of these (MCP: as fields on the tool input; REST: as query params on `/run/{sku}`; CLI: flags on `anyapi run`):

- `fields` - comma-separated keys (dotted paths allowed) to keep on each result item. The biggest token saver: a page becomes a small object.
- `max_items` - cap the number of result rows returned. A `_truncated` note reports how many were withheld so you can page via the API's own `limit`.
- `summary` - return only a structural outline (top-level keys and array lengths), not the bulk data.

These trim what is returned to you; they do **not** change what you are charged (`costUsd` reflects the full result the API produced).

## 5. Pricing

Every price is in **USD**. Each API advertises a per-request ceiling, a fixed base cost, and a marginal per-unit cost (per result row, or per submitted input for input-priced APIs). `get_api` returns these as `priceUsd`, `baseUsd`, `perItemUsd`, and `perItemUnit`. You are never billed in "credits".

Docs: https://getanyapi.com/docs
