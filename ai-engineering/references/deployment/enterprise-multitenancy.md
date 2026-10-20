# Enterprise Multi-Tenancy

Shipping one agent platform to many enterprise customers, each convinced their
requirements are unique. The organizing principle for everything below is
**configuration, not forking**: every per-customer difference is data in a
versioned tenant config, never a branch of the platform.

## Configuration over forking

- Per-customer **prompts**, retrieval indexes, voices, **tool allow-lists**,
  escalation policies and disclosure text are all config values, versioned and
  reviewable like code, loaded at runtime by tenant id ([[prompts]]).
- A **tenant config schema** is the contract. New customer requirement? It
  either maps onto an existing field, justifies a new field for everyone, or is
  declined. Those are the only three answers.
- A per-customer fork is the fastest route to a codebase nobody can upgrade:
  security patches land in one branch, the model swap lands in another, and
  within two quarters no tenant is running the same system.
- Corollary: config changes need the same rollout discipline as deploys —
  review, staging, rollback. A prompt edit is a production change.

## Tenant isolation

Three shapes, in increasing isolation and increasing cost:

- **Shared model, shared infrastructure**, tenant id on every request and every
  row. Cheapest, best utilisation, thinnest blast-radius margin.
- **Per-tenant tuned models or adapters** over shared serving. Customer-specific
  behaviour without a separate stack; a fine-tune is customer data.
- **Fully dedicated per-tenant stacks** — separate infra, sometimes separate
  region or account. Maximum isolation, maximum operational cost, and the shape
  enterprise procurement usually asks for first.

Isolate more than the primary datastore. **Retrieval indexes, caches, eval
datasets and logs/traces all contain customer content.** A shared vector index
with a tenant filter is one bad query away from cross-tenant leakage; a shared
prompt cache can return another tenant's context.

**Rule: anything derived from customer data — embeddings, fine-tunes, traces,
eval sets, transcripts — carries the same sensitivity as the raw data**, and
the same residency, retention and deletion obligations.

**Noisy neighbour**: one large tenant exhausting shared rate limits or model
quota starves everyone else, and it shows up as latency for customers who did
nothing. Mitigate with per-tenant quotas and concurrency caps, enforced before
the request reaches the provider ([[cost-latency]]).

## Data residency and retention

- **Where data is stored and where it is processed are different questions**,
  and enterprise buyers ask both. Inference is processing.
- Model providers typically retain API inputs and outputs for a limited
  **abuse-monitoring window** by default. **Zero-retention** and **regional
  processing** options generally exist but require prior approval and
  contractual amendments — they are not runtime flags.
- **EU data residency is not a checkbox.** It is deliberate configuration plus
  paperwork, and it constrains which models, versions and regions you can use;
  the newest model is often not available in the region you promised.
- Retention has a deletion counterpart: an enterprise deletion request must
  reach the indexes, caches and traces, not just the primary store.

## VPC and on-prem deployment

Some customers will demand the agent run inside their own environment. The
honest trade-off: it breaks your ability to **ship quickly, observe production
and reproduce bugs** — precisely the tension a deployment engineer lives
inside. You debug a system you cannot see, at a version you did not choose.

Ways to soften it: strict **version pinning** with a supported-version window,
customer-side **telemetry export** (agreed metrics and redacted traces pushed
back to you), reproducible release artifacts, and a self-serve diagnostics
bundle the customer can send when something breaks.

## Credentials into customer systems

- **OAuth authorization-code with per-tenant apps** for actions taken in a
  user's context, so the agent inherits that user's permissions.
- **Service accounts or client-credentials** for backend sync and batch work.
- Prefer **short-lived credentials**, workload identity federation or
  impersonation over long-lived static keys.
- Secrets live in a **KMS-backed vault**, scoped per tenant, rotated and
  audited. Never in a prompt, a config repo or a tool description.
- **Least privilege is a security control for the agent itself**: a
  prompt-injected agent can only do what its credentials allow, so scope is
  containment, not just hygiene ([[guardrails]]).

## Safe rollout

Ordinary release engineering, re-pointed at a new metric.

- **Shadow mode** (traffic teeing): run the agent alongside the human or the
  existing system, compare outputs, take no action.
- **Canary by tenant or by intent**, then staged expansion. Feature-flag every
  new capability per tenant.
- A **kill switch** that falls back to a human queue or a deterministic flow,
  tested, and operable by someone who is not you at 2am.
- **Canary on containment, escalation and wrong-action rate, not error rate.**
  A confidently wrong agent has a perfect error rate ([[evals-observability]]).

## Disclosure obligations

Factual summary, not legal advice.

- Under the **EU AI Act, Article 50 transparency obligations apply from
  2 August 2026**: systems interacting directly with people must ensure those
  people are informed they are interacting with an AI. For a voice agent that
  means disclosure **in the audio itself** ([[voice-telephony]]).
- **Machine-readable marking of synthetic content** is a related provider duty,
  with a grace period into **December 2026** for systems already on the market.
- The heavier **Annex III high-risk obligations were deferred to 2 December
  2027**.
- Penalties reach **€15M or 3% of worldwide turnover**.
- Duties split between **provider** and **deployer** — which is exactly the
  who-owns-what negotiation between a platform vendor and its enterprise
  customer. Settle it in the contract, not after an incident.
- This area is moving and secondary trackers have been observed to lag. Verify
  against the European Commission's own pages before relying on a date.

## The hard part

**Every enterprise customer's requirements feel like a special case, and each
one individually seems worth a small exception.** Discipline is pushing each
into the config schema or declining it — the exception is always cheap today
and always the thing you cannot upgrade in a year.

The second hard part: **isolation, residency and on-prem all reduce your
visibility into production at exactly the moment reliability matters most.**
The customers with the strictest requirements are usually the largest, the
loudest about outages, and the ones whose traces you are not allowed to see.

## Related

- [[prompts]], [[guardrails]], [[evals-observability]], [[cost-latency]],
  [[voice-telephony]], [[rag-retrieval]], [[tool-calling]], [[antipatterns]]

Source: digital-strategy.ec.europa.eu/en/policies/guidelines-transparency-ai-
generated-content (Article 50 applies 2 August 2026; provider vs deployer
duties; machine-readable marking); learn.microsoft.com/azure/architecture/guide/
multitenant/approaches/ai-ml (isolation shapes, noisy neighbour);
developers.openai.com/api/docs/guides/your-data (retention windows,
zero-retention and regional processing by approval); sre.google/workbook/
canarying-releases (canary and staged rollout). Technical reference only, not
legal advice.
