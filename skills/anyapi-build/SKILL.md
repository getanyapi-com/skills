---
name: anyapi-build
description: Add scraping and data APIs to application code with AnyAPI. Use this skill when the user wants to add scraping/data APIs to their app, integrate AnyAPI into a product flow, call AnyAPI from backend code, build a typed client for an AnyAPI SKU, wire social data, search data, web scraping, profile lookups, post search, or marketplace data into an app, use GET /v1/apis/{sku}, use POST /v1/run/{sku}, handle AnyAPI HTTP 402, store ANYAPI_API_KEY, or generate clients from openapi.json.
license: Apache-2.0
metadata:
  author: AnyAPI
  version: "0.1.0"
---

# AnyAPI build integration

Use this when AnyAPI should become part of an app's product flow. The app is the
caller, so keep the AnyAPI key on the server and expose only your own app route to
the browser.

AnyAPI is a unified marketplace for scraping and data APIs: any API, one wallet,
USD, no subscriptions. The visible provider is always AnyAPI.

## Workflow

1. Inspect the project before wiring anything.
   - Find the server boundary: API route, backend service, worker, job, action, or queue.
   - Reuse the project's existing HTTP client, validation library, env loader, and test style.
   - For browser apps, never put an AnyAPI key in client code. Add a server route instead.
2. Pick and inspect the SKU.
   - CLI: `anyapi search "<intent>"`, then `anyapi describe <sku>`.
   - REST: `GET https://api.getanyapi.com/v1/apis?query=<intent>`, then
     `GET https://api.getanyapi.com/v1/apis/{sku}`.
   - Read `inputSchema`, `outputSchema`, `priceUsd`, `baseUsd`, `perItemUsd`, and
     `perItemUnit` before building inputs.
3. Mint a dedicated app key.
   - Use a dashboard key or self-signup:

     ```bash
     curl -s -X POST https://api.getanyapi.com/agent/signup \
       -H "Content-Type: application/json" \
       -d '{ "sponsorEmail": "you@example.com", "label": "my-app" }'
     ```

   - Store the returned `secret` only as `ANYAPI_API_KEY`.
   - Do not hardcode it, print it, commit it, send it to the browser, or rely on
     `~/.anyapi/config.json` from production app code.
4. Mirror the SKU input schema in the app.
   - Use the schema from `GET /v1/apis/{sku}` as the source of truth.
   - Match required fields, enums, defaults, and limits in forms, jobs, typed wrappers,
     and validation.
   - If the project already uses Zod, Ajv, Valibot, TypeBox, Pydantic, or another schema
     tool, adapt the AnyAPI JSON Schema into that local pattern.
5. Call `POST /v1/run/{sku}` from server-side code.
   - Send `Authorization: Bearer $ANYAPI_API_KEY`.
   - Send input as JSON.
   - Add `fields`, `max_items`, or `summary` query params when the app or agent needs a
     smaller response.
6. Handle 402s.
   - `key_cap_exceeded` means a starter key hit its USD cap. Ask the human to claim or
     fund the key, then retry with the same key.
   - Show a clear operational error in app logs or admin UI. Do not loop retries.
7. Smoke-test one cheap call.
   - Verify the app path can read `ANYAPI_API_KEY`.
   - Verify the response has `provider: "AnyAPI"` and `costUsd`.
   - Verify `output` matches the inspected output schema.
   - Keep the output small during tests with a low input limit or context-budget flags.
8. Generate typed clients when useful.
   - Use `https://api.getanyapi.com/openapi.json` for OpenAPI clients and generated types.
   - Keep generated code in the project's normal generated-code location.

## TypeScript server helper

```ts
type AnyApiRunResponse<TOutput> = {
  output: TOutput;
  provider: "AnyAPI";
  costUsd: number;
  items?: number;
};

export async function runAnyApi<TOutput>(
  sku: string,
  input: Record<string, unknown>,
): Promise<AnyApiRunResponse<TOutput>> {
  const apiKey = process.env.ANYAPI_API_KEY;
  if (!apiKey) {
    throw new Error("Missing ANYAPI_API_KEY");
  }

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
    const body = await res.text();
    throw new Error("AnyAPI key needs claiming or funding: " + body);
  }
  if (!res.ok) {
    throw new Error("AnyAPI run failed: " + res.status + " " + (await res.text()));
  }

  return (await res.json()) as AnyApiRunResponse<TOutput>;
}
```

## Hard rules

- Prices and costs are USD only.
- The provider is AnyAPI.
- Application code reads `ANYAPI_API_KEY`; it does not read CLI config.
- Browser code never receives the AnyAPI secret.
- Invalid input should be fixed against `GET /v1/apis/{sku}`, not retried blindly.
