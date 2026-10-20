# LLM System Antipatterns

Recurring smells in LLM-backed systems, why each one is tempting, what it costs,
and what to ask or build instead. Use alongside [[rubric]] — the rubric asks the
questions, this leaf names the answers you should worry about.

## Architecture

- **Agent when a workflow would do** — autonomy chosen because agents are
  interesting, not because the problem needs them. Fixed steps in a fixed order
  are a pipeline: cheap, testable, debuggable. An agent loop buys unpredictable
  step counts, unpredictable cost, and a much larger failure surface. Ask what
  the model decides at runtime that code could not decide in advance; if the
  answer is nothing, it's a workflow ([[agent-loop]]).
- **Letting the model do arithmetic or policy** — totals, prorations,
  eligibility, discount rules and refund limits computed inside the prompt.
  Tempting because it "just works" in the demo, and wrong at the tail where
  money lives. The model classifies and drafts; code computes, decides and
  applies. Anything you would put in a unit test belongs in code.
- **Prompt sprawl** — one enormous system prompt that accreted a paragraph per
  incident and now contradicts itself, with nobody willing to delete a line
  because nobody knows what it holds up. Split by responsibility, delete on a
  schedule, and require an eval case to justify each addition — an instruction
  with no test behind it is a rumour ([[prompts]]).
- **Tool soup** — thirty tools with overlapping names and fuzzy boundaries. The
  model picks the wrong one, and every tool definition is tokens on every turn.
  Consolidate near-duplicates, namespace by domain, and cut anything that isn't
  earning its place ([[tool-calling]]).
- **Opaque tool returns** — returning bare IDs, unlabelled arrays, or a raw API
  blob. The model then guesses at meaning or burns another call resolving it.
  Return labelled, self-describing, already-resolved fields, and trim what the
  model doesn't need.
- **Non-idempotent write tools** — `create_refund` with no idempotency key.
  Models retry after timeouts, and parallel tool calls duplicate work; you get
  two refunds, not one ([[non-determinism]]).
- **Unbounded loops** — no step budget, no token ceiling, no wall-clock timeout.
  Fine until one pathological conversation loops two hundred times; usually
  discovered via the bill rather than an alert ([[cost-latency]]).

## Retrieval

- **Vector store by default** — an embedding index stood up where grep, a SQL
  `WHERE`, or an existing API would be exact, cheaper, and maintenance-free.
  Similarity search is for meaning, not for order numbers and IDs. Ask what
  question the index answers that a query cannot ([[rag-retrieval]]).
- **Chunk-size tuning as the main lever** — weeks spent on 512 vs 1024 tokens
  while chunks sit stripped of the document, section and date that made them
  meaningful. Contextual enrichment and hybrid (keyword + vector) search
  dominate chunk-size micro-tuning by a wide margin.
- **Stuffing the context window** — more retrieved context assumed to be
  strictly better. It costs money, adds latency, and past a point *reduces*
  accuracy by diluting attention and burying the relevant passage. Retrieve
  fewer, better passages and measure precision, not just recall.
- **Stale index, silent** — no freshness SLA and no alert on reindex failure, so
  the agent confidently cites last quarter's policy in this quarter's voice.
  Track index age as a monitored metric and fail loudly when it stops moving.

## Operations

- **Demo-driven development** — shipping on a handful of impressive manual
  examples, where the demo *is* the eval. Those examples are the ones you tuned
  against; they measure nothing. Twenty real cases with expected outcomes,
  running in CI, beats any number of live walkthroughs
  ([[evals-observability]]).
- **Uptime as quality** — dashboards green, latency fine, error rate zero, while
  the agent is confidently wrong. Wrong answers return HTTP 200. Measure output
  quality directly; APM cannot see a hallucination.
- **Judge without calibration** — LLM-as-judge scores trusted as ground truth
  though they were never checked against human labels. Label a sample by hand,
  measure agreement, and recheck when you change judge model or prompt.
- **Console prompt editing** — production prompts edited in a provider web
  console: unversioned, unreviewed, and unrevertible when the 2am regression
  lands. Prompts are code; keep them in the repo, in diffs, behind the same
  review and rollback as everything else ([[prompts]]).
- **Unpinned model** — a floating model alias, so the provider ships an update
  and behaviour shifts under a prompt nobody touched. Pin the version, upgrade
  deliberately, and re-run evals as part of the upgrade.
- **Guardrails removed for latency** — an output check quietly dropped under
  p95 pressure, with no record of what risk was accepted or by whom. Make the
  trade-off explicit and reversible instead of silent ([[guardrails]]).
- **Escalation as an afterthought** — no path to a human, or a handoff that
  dumps the customer at the front of the queue with no transcript and no
  summary. Escalation is a first-class feature with its own context payload.
- **Trusting tool output and retrieved text as instructions** — the injection
  vector. Retrieved documents, tool results, web pages and user files are data.
  Keep them structurally separate from instructions, and never let them widen
  what the agent is permitted to do.
- **Cache-hostile prompt layout** — timestamps, session IDs or reordered tool
  definitions near the top of the prompt, silently destroying prefix caching and
  quietly multiplying cost. Stable prefix first, volatile content last; check
  the hit rate rather than assuming it ([[cost-latency]]).

## Organizational

- **Per-customer forks** — a prompt branch per enterprise customer. Works at
  three tenants, collapses at thirty: no change can be made once without being
  made thirty times. Tenant behaviour is configuration and data, not a branch
  ([[enterprise-multitenancy]]).
- **Chat-latency assumptions in voice** — a two-second pause is acceptable in
  text and dead air on a phone call. Voice needs streaming, filler, and a
  latency budget of its own ([[voice-telephony]]).
- **"We'll add evals later"** — the antipattern that guarantees all the others
  persist, because without a measurement harness nothing can be safely changed,
  so nothing is. Evals come before the second prompt change, not after the
  first incident.

## The meta-pattern

Nearly all of these come from treating the model as *the system* rather than as
one non-deterministic component inside a system that still needs ordinary
engineering discipline: bounded inputs, typed interfaces, idempotent writes,
version control, tests, monitoring, and a defined blast radius. The model is
new; the discipline isn't.


## Related

- [[rubric]], [[agent-loop]], [[non-determinism]], [[tool-calling]],
  [[rag-retrieval]], [[prompts]], [[evals-observability]], [[guardrails]],
  [[cost-latency]], [[voice-telephony]], [[enterprise-multitenancy]],
  [[llm-basics]]

Source: synthesis distilled from the sibling leaves in this skill.
