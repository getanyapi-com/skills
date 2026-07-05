---
name: anyapi
description: Accesses hundreds of scraping and data APIs (social media, search results, web data) through AnyAPI's unified gateway with one API key and USD pay-per-request pricing. Use when the user needs third-party data - Instagram, TikTok, YouTube, Reddit, Facebook profiles/posts/comments, Google search results, web scraping - or mentions AnyAPI.
license: Apache-2.0
metadata:
  author: AnyAPI
  version: "0.1.0"
---

# AnyAPI

AnyAPI is a unified marketplace for scraping and data APIs: any API, one wallet,
USD, no subscriptions. One key reaches the whole catalog; every API has a
normalized input/output JSON Schema; failed calls are never charged, and AnyAPI
falls back automatically under one price reservation.

- Gateway: `https://api.getanyapi.com` (REST) and `https://api.getanyapi.com/mcp` (MCP, Streamable HTTP)
- Dashboard (keys, wallet top-up): `https://getanyapi.com/dashboard`
- Docs: `https://getanyapi.com/docs`

## Fast install path

Use the official CLI when you want local setup, skills installation, MCP registration,
catalog discovery, and output files without writing HTTP glue:

```
npx -y anyapi-cli@latest init
```

`anyapi init` installs the AnyAPI agent skills into detected agents, offers MCP
registration, and runs `anyapi signup` if no key is available. The CLI resolves auth in
this order: `--api-key`, `ANYAPI_API_KEY`, `~/.anyapi/config.json`, then self-signup in
an interactive terminal.

Useful commands:

```
anyapi signup [--email <email>] [--label <label>]
anyapi login --api-key aa_live_...
anyapi search <query>
anyapi list [--category <cat>]
anyapi describe <sku>
anyapi run <sku> --input '<json>' [--fields a,b] [--max-items N] [--summary] [-o path] [--json]
anyapi balance
anyapi claim
```

By default, `anyapi run` writes JSON to `.anyapi/<sku>-<timestamp>.json` and prints the
path, `costUsd`, and item count. CLI repo: https://github.com/getanyapi-com/cli.

## Authentication

Every run needs an AnyAPI key (an `aa_live_...` secret) in the `ANYAPI_API_KEY`
environment variable, sent as `Authorization: Bearer $ANYAPI_API_KEY`. Discovery over
MCP works without a key; running an API always requires one. Never hardcode or print the
secret.

**If `ANYAPI_API_KEY` is already set, use it.** Otherwise mint one right here - no
dashboard trip, no sign-in:

1. Ask the user which email address they want this AnyAPI account tied to.
2. Mint a key with that email as the sponsor:

   ```
   curl -s -X POST https://api.getanyapi.com/agent/signup \
     -H "Content-Type: application/json" \
     -d '{ "sponsorEmail": "<their email>", "label": "<your tool or repo name>" }'
   ```

   The response returns `secret` (the `aa_live_...` key - shown once), `claimToken`, and
   `expiresAt`. Put `secret` in `ANYAPI_API_KEY` and start working; it's seeded with a
   small USD grant so calls succeed immediately. Keep the `claimToken`; never print the
   `secret`.
3. This starter key is **capped at a small amount and expires in 7 days** until it's
   claimed. Tell the user how to upgrade it - claiming lifts the cap, makes it permanent,
   and adds the one-time **$1** account credit:

   > Sign in at https://getanyapi.com/dashboard with **<their email>**, open
   > **API keys -> Claim agent key**, and paste this token: `<claimToken>`

   Claiming upgrades the *same* key already in `ANYAPI_API_KEY` and moves it onto the
   user's funded wallet - nothing to swap. (If you passed `sponsorEmail`, that address
   also gets an approve/block email.)

## Choosing a surface

- **CLI available**: use `npx -y anyapi-cli@latest init` for setup, then `anyapi search`,
  `anyapi describe`, and `anyapi run` for filesystem-native local work.
- **MCP server connected** (tools `list_apis`, `get_api`, `run_api`, `get_balance`
  from the `anyapi` server): prefer it. Same catalog, schema-validated, structured
  output.
- **No MCP**: use REST with curl. Both surfaces are equivalent; pick one and
  stick with it for the session.

## Workflow: discover -> inspect -> run

1. **Discover.** Find the SKU for the data you need.
   - MCP: `list_apis` with `{"query": "<keywords>"}` (and/or `category`).
   - REST: `curl -s "https://api.getanyapi.com/v1/apis?query=<keywords>" -H "Authorization: Bearer $ANYAPI_API_KEY"`

   SKUs are `<platform>.<resource>` slugs, e.g. `reddit.search`,
   `instagram.profile`, `tiktok.profile`, `google.search`, `web.scrape`.

2. **Inspect.** Read the input schema before building a payload.
   - MCP: `get_api` with `{"sku_id": "<sku>"}`.
   - REST: `curl -s "https://api.getanyapi.com/v1/apis/<sku>" -H "Authorization: Bearer $ANYAPI_API_KEY"`

   The response includes `priceUsd`, `inputSchema`, and `outputSchema`. Most APIs
   bill **per result returned** (`baseUsd + perItemUsd x items`) - set `limit` in
   the input to cap how many results you get and what you pay; simple lookups are
   flat per request. Build the input strictly from the schema's `required` and
   `properties` - invalid input is rejected without charge.

3. **Run.**
   - MCP: `run_api` with `{"sku_id": "<sku>", "input": {...}}`.
   - REST: `curl -s -X POST "https://api.getanyapi.com/v1/run/<sku>" -H "Authorization: Bearer $ANYAPI_API_KEY" -H "Content-Type: application/json" -d '<input JSON>'`

   Success returns `{output, provider, costUsd}`. `output` matches the SKU's
   output schema; `provider` is always "AnyAPI".

## Response budget controls

`run_api` returns the full normalized result by default. When a result would be
large (many rows, or rows with many fields), trim what comes back so it doesn't
flood your context. These are **opt-in** - MCP: pass them as fields on the
`run_api` input; REST: append them as **query params** on `/v1/run/{sku}`:

- `fields` - comma-separated keys to keep on each result item (dotted paths like
  `author.name` descend into nested objects). The biggest saver: a page becomes a
  small object.
- `max_items` - cap the number of result rows returned. A `_truncated` note reports
  how many were withheld, so you can page via the SKU's own `limit`.
- `summary` - return only a structural outline (top-level keys and item counts),
  not the bulk data. Useful to learn a result's shape before fetching it in full.

They change only what is **returned to you**, never what you are **charged** -
`costUsd` reflects the full result the API produced. Example (REST):

```
curl -s -X POST "https://api.getanyapi.com/v1/run/reddit.search?fields=title,score&max_items=10" \
  -H "Authorization: Bearer $ANYAPI_API_KEY" -H "Content-Type: application/json" -d '<input JSON>'
```

## Cost discipline

Every successful run charges the wallet `costUsd` (typically fractions of a
cent; the exact per-request price is on the SKU as `priceUsd`). Before a bulk
job (more than ~20 calls), compute and state the estimated total cost
(`calls x priceUsd`) and get the user's confirmation. Check the balance with
`get_balance` (MCP) or `GET /v1/balance` (REST) when a run fails with insufficient
funds, and point the user at the dashboard to top up. Never retry a failed run in a tight loop -
failures are unbilled but retries won't fix invalid input or an empty wallet.

## Results and "not found"

Many output schemas use the envelope `{found: boolean, data: object|null}`.
`{"found": false}` is a **successful, billed** response meaning the entity
doesn't exist in the source data (e.g. a deleted profile) - do not treat it as an error
or retry it.

## Errors

Errors are machine-readable prefixes (MCP tool errors) or HTTP statuses (REST).
None of these are charged:

| MCP prefix / REST status | Meaning | What to do |
|---|---|---|
| `unauthorized` / 401 | Missing or invalid key | Check `ANYAPI_API_KEY`; mint one via self-signup (see Authentication) |
| `sku_not_found` / 404 | Unknown SKU | Re-run discovery; don't guess slugs |
| `invalid_input` / 400 | Input failed schema validation | Re-read the input schema and fix the payload |
| `key_cap_exceeded` / 402 | Starter key hit its spend cap | Have the user claim the key (see Authentication) to uncap it |
| 402 | Wallet too low | Ask the user to top up at getanyapi.com/dashboard |
| 502 | The API run failed | Transient; retry once after a pause, then report |

## Hard rules

- Prices are **USD only**.
- The provider is **AnyAPI** - responses never name an upstream backend, and
  neither should you.
