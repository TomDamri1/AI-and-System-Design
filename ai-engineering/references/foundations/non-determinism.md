# Non-Determinism

The constraint the rest of this skill is organised around. A probabilistic
component inside a deterministic system doesn't invalidate the classic toolkit
— it invalidates the assumption that failures announce themselves.

## The frame

- An agent is an ordinary distributed system with **one non-deterministic
  component in the middle**. Retries, idempotency, queues, backpressure,
  caching, timeouts, observability and canaries all still apply, unchanged.
- What genuinely changes is **failure detection**. Everything below follows.

## Failure that looks like success

- Classic components fail **loudly** — exception, 500, timeout, constraint
  violation. Signal and failure arrive together, so monitoring, alerting and
  retry policy can all key off the signal.
- A model fails **quietly**: a fluent, well-formed, confidently worded *wrong*
  answer, returned as HTTP 200 at normal latency and normal cost.
- So the dashboard reads **100% success** while the product is wrong. Error
  rate, p99 and uptime are blind to the only failure mode that matters, and
  the loud failures (429s, malformed JSON) are the cheap ones. This is the
  single most important difference; design around it first.
- Correctness must be measured **out of band** — sampled grading, groundedness
  checks, invariant checks on the way out, user feedback. A product-level
  property, not an infra-level one.

## Testing

- Same input, different output, so exact-string assertions are flake
  generators. Assert **properties and invariants**: schema conformance, did it
  call the right tool with arguments from the right fields, is every claim
  grounded in something retrieved, are refusals intact.
- A property suite is a **distribution** test: run n times, require a pass
  *rate*, watch the rate move. One green run proves nothing. Machinery in
  [[evals-observability]].

## Retries mean something different

- Retrying a deterministic call reproduces the failure — that is why retry
  policy is safe and boring. Retrying a model call may simply succeed, because
  you resampled.
- Useful, but it **hides the defect**: a prompt failing 30% of the time looks
  fine at n=3, and you pay ~1.3x for it forever. Log retry rate per call site
  and treat a rising one as a quality regression.

## Idempotency for tool side effects

- Standard distributed-systems practice applied to tool calls: the
  highest-value transfer from classic backend work, and absent from vendor
  tool-use guides. Reason it out — the model **retries invalid or failed tool
  calls** (typically 2–3 times) and can issue **parallel calls** in one turn
  that hit the same tool concurrently.
- So any tool with a side effect — refund, cancel, email, ticket, charge —
  needs an **idempotency key derived from the logical operation**, not a fresh
  UUID per attempt. A new UUID each try is a duplicate generator. Derive it
  from **stable IDs** (`refund:order_8812:v1`): a natural-language argument is
  the worst possible key, since model-authored prose is exactly what varies
  between attempts.
- **Separate read tools from write tools** — reads are freely retryable and
  parallel-safe, writes are neither, and distinct names make that legible to
  the model and to your gating logic. For destructive actions use a **dry-run
  / confirm split**: one tool returns what *would* happen plus a token, a
  second executes the token. Have writes return current state, not "ok".

## Bounding the blast radius

- **Least privilege per tool** ([[tool-calling]]), and **budgets** on steps,
  wall-clock, spend and per-tool calls — enforced in the harness, not
  requested in the prompt ([[agent-loop]]).
- **Human approval gates** on anything irreversible or externally visible, and
  a **kill switch** that disables a tool without a deploy.
- Tool *results* are untrusted input too, not just tool arguments: documents
  and API responses can carry injected instructions ([[guardrails]]).

## What determinism you can still buy

- **Schema-constrained output** — constrained decoding restricts generation to
  tokens the schema permits, so conformance is structural rather than checked
  afterwards.
- **If code can compute it, don't ask the model.** Arithmetic, dates, sorting,
  joins, policy lookups are deterministic, testable and near-free; use the
  model to decide *what* to compute, then compute it.
- **Deterministic shell, probabilistic core** — routing, validation and
  post-checks in code; judgement in the model.
- **Pin what you can** (model version, prompt version, tool schema) so a
  behaviour change is a deploy you made, not weather ([[prompts]]).

## The hard part

**Push determinism outward** — keep the probabilistic part as small and as
well-fenced as possible. Teams get this backwards by treating the model as the
system rather than one component in it: an agent that "decides" whether to
issue a refund is far harder to reason about than one that classifies intent,
hands a typed decision to code, and lets code apply the policy. The temptation
grows with capability — because the frontier model *can* do the arithmetic and
*can* be told to refund at most twice, fencing it feels wasteful. Capability is
not a guarantee: a tool that is 99% correct is one wrong refund per hundred,
with a 200 on every one of them.

## Related

- [[llm-basics]], [[tool-calling]], [[agent-loop]], [[evals-observability]],
  [[guardrails]], [[cost-latency]], [[antipatterns]]

Source: largely synthesis — standard distributed-systems practice (idempotency
keys, least privilege, blast-radius bounding) applied to LLM tool calls, which
no vendor doc covers directly. Vendor-verified: platform.claude.com/docs —
handle-tool-calls (model retries invalid tool calls 2–3 times; tool results are
untrusted input), structured-outputs (constrained decoding).
