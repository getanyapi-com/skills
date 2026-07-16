# AnyAPI skills agent instructions

This repository publishes customer-facing agent skills for the AnyAPI ecosystem. The authoritative
wiring, contract invariants, impact classifier, repository gates, and rollout order live in the
main repository's [ECOSYSTEM.md](https://github.com/getanyapi-com/anyapi/blob/main/ECOSYSTEM.md).

Before changing discovery, catalog, search, pricing, schemas, MCP/OpenAPI/payment integration,
CLI/SDK guidance, or customer-facing integration docs:

1. Read `ECOSYSTEM.md` from the main repository.
2. Classify the change and create the impact ledger it requires.
3. Mark every ecosystem surface updated or unaffected with a concrete reason.
4. Follow the documented release order; do not infer it from this repository alone.

`getanyapi-com/anyapi/src/lib/agentSkill.ts` owns the live machine skill and the body of
`skills/anyapi/SKILL.md`. Update that source first, deploy it, then sync this derivative. The CLI's
onboarding/discover/run skills are separate task-specific derivatives and must also be reviewed when
their documented commands or contracts change. Do not copy wire shapes into this file.

Run `bash scripts/check.sh` before handing off changes.
