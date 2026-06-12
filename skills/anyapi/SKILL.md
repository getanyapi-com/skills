---
name: anyapi
description: Accesses hundreds of scraping and data APIs (social media, search results, web data) through AnyAPI's unified gateway with one API key and USD pay-per-request pricing. Use when the user needs third-party data — Instagram, TikTok, YouTube, Reddit, Facebook profiles/posts/comments, Google search results, web scraping — or mentions AnyAPI.
license: Apache-2.0
metadata:
  author: AnyAPI
  version: "0.1.0"
---

# AnyAPI

AnyAPI is a unified marketplace for scraping and data APIs: any API, one wallet,
USD, no subscriptions. One key reaches the whole catalog; every API has a
normalized input/output JSON Schema; failed calls are never charged (AnyAPI
fails over across providers automatically under one price reservation).

- Gateway: `https://api.getanyapi.com` (REST) and `https://api.getanyapi.com/mcp` (MCP, Streamable HTTP)
- Dashboard (keys, wallet top-up): `https://app.getanyapi.com`
- Docs: `https://getanyapi.com/docs`

## Authentication

Use the customer's AnyAPI key from the `ANYAPI_API_KEY` environment variable.
Never hardcode keys or print them. If no key is set, tell the user to create one
at https://app.getanyapi.com under **API keys** and fund the wallet. Discovery
over MCP works without a key; running an API always requires one.

## Choosing a surface

- **MCP server connected** (tools `list_apis`, `get_api`, `run_api` from the
  `anyapi` server): prefer it. Same catalog, schema-validated, structured output.
- **No MCP**: use REST with curl. Both surfaces are equivalent; pick one and
  stick with it for the session.

## Workflow: discover → inspect → run

1. **Discover.** Find the SKU for the data you need.
   - MCP: `list_apis` with `{"query": "<keywords>"}` (and/or `category`).
   - REST: `curl -s "https://api.getanyapi.com/v1/apis?query=<keywords>" -H "Authorization: Bearer $ANYAPI_API_KEY"`

   SKUs are `<platform>.<resource>` slugs, e.g. `reddit.search`,
   `instagram.profile`, `tiktok.profile`, `google.search`, `web.scrape`.

2. **Inspect.** Read the input schema before building a payload.
   - MCP: `get_api` with `{"sku_id": "<sku>"}`.
   - REST: `curl -s "https://api.getanyapi.com/v1/apis/<sku>" -H "Authorization: Bearer $ANYAPI_API_KEY"`

   The response includes `priceUsd` (per request), `inputSchema`, and
   `outputSchema`. Build the input strictly from the schema's `required` and
   `properties` — invalid input is rejected without charge.

3. **Run.**
   - MCP: `run_api` with `{"sku_id": "<sku>", "input": {...}}`.
   - REST: `curl -s -X POST "https://api.getanyapi.com/v1/run/<sku>" -H "Authorization: Bearer $ANYAPI_API_KEY" -H "Content-Type: application/json" -d '<input JSON>'`

   Success returns `{output, provider, costUsd}`. `output` matches the SKU's
   output schema; `provider` is always "AnyAPI".

## Cost discipline

Every successful run charges the wallet `costUsd` (typically fractions of a
cent; the exact per-request price is on the SKU as `priceUsd`). Before a bulk
job (more than ~20 calls), compute and state the estimated total cost
(`calls × priceUsd`) and get the user's confirmation. Check the balance with
`GET /v1/balance` (`{usd}`) when a run fails with insufficient funds, and point
the user at the dashboard to top up. Never retry a failed run in a tight loop —
failures are unbilled but retries won't fix invalid input or an empty wallet.

## Results and "not found"

Many output schemas use the envelope `{found: boolean, data: object|null}`.
`{"found": false}` is a **successful, billed** response meaning the entity
doesn't exist upstream (e.g. a deleted profile) — do not treat it as an error
or retry it.

## Errors

Errors are machine-readable prefixes (MCP tool errors) or HTTP statuses (REST).
None of these are charged:

| MCP prefix / REST status | Meaning | What to do |
|---|---|---|
| `unauthorized` / 401 | Missing or invalid key | Check `ANYAPI_API_KEY`; have the user create a key |
| `sku_not_found` / 404 | Unknown SKU | Re-run discovery; don't guess slugs |
| `invalid_input` / 400 | Input failed schema validation | Re-read the input schema and fix the payload |
| `insufficient_credits` / 402 | Wallet too low | Ask the user to top up at app.getanyapi.com |
| `all_providers_failed` / 502 | Every provider errored | Transient; retry once after a pause, then report |
| `no_providers` | SKU has no enabled providers | Report; pick another SKU |

## Hard rules

- Prices are **USD only** — never mention "credits".
- The provider is **AnyAPI** — responses never name an upstream backend, and
  neither should you.
