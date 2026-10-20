# Cost and Latency Engineering

In an agent, **tokens are the unit of both cost and latency**. Every lever that
shortens the prompt or the output moves both numbers at once, so this is one
engineering problem, not two. Treat cost per conversation the way you treat a
latency SLO: a budget set up front, not a bill discovered later.

## Where the tokens actually go

- **The conversation grows every turn.** Each iteration re-sends the whole
  history, so token spend on a run is quadratic-ish in turns, not linear.
- **Tool definitions are re-sent on every call** — a large tool catalogue is a
  fixed tax paid once per model call, not once per session.
- **Tool results are usually the largest payload.** One unfiltered API response
  or file read can dwarf the prompt that requested it.
- Order of magnitude: an **agent loop costs several times a single chat call**,
  and **multi-agent an order of magnitude more** ([[agent-loop]]).

## Prompt caching

Usually the highest-leverage lever available, and the one most often broken by
accident.

- It works on a **prefix match**: the cacheable portion must be a byte-identical
  **stable prefix**. The hierarchy is **tools → system → messages**, and a
  change anywhere invalidates everything after it.
- Practical consequence: **stable content first, volatile content last.** A
  per-request timestamp in the system prompt, or a tool list rendered from an
  unordered map, silently destroys the cache with no error.
- **Cache writes cost more than plain input; cache reads far less** (roughly
  1.25x write, 0.1x read on Claude). So caching pays on repeated prefixes and
  *loses* on one-shot calls.
- There is a **minimum cacheable prefix length** (model-dependent, hundreds to a
  few thousand tokens — below it, caching is silently skipped) and a **TTL**
  (short by default, longer available at a higher write price).

## Context trimming vs caching

- **Compaction** — dropping or summarizing old turns — shortens the prompt but
  **rewrites the prefix**, forcing a cache rewrite of everything downstream.
- These two levers therefore fight: aggressive continuous trimming can cost
  *more* than it saves.
- **Trim in large, infrequent chunks.** Mature APIs expose a "clear at least N
  tokens" style control precisely so you amortize one cache rewrite over many
  subsequent cheap turns.

## Model routing and effort

- **Small fast model** for classification, extraction, routing and guardrail
  checks ([[guardrails]]). **Large model only where judgement is needed.**
- But **effort / thinking-budget controls within one model are often the better
  first lever**: switching models changes behaviour and **invalidates your
  evals** ([[evals-observability]]). Turn the dial before swapping the engine.

## Streaming, and output tokens

- **Streaming reduces perceived latency only.** **Time-to-first-token** is what
  the user feels; **total generation time** is what you pay for
  ([[llm-basics]]).
- **Output is the dominant latency term** and usually the more expensive one per
  token. Cutting it is the most reliable win.
- Ask for a shorter **structure**, not shorter **wording**: "three bullets" or a
  JSON object with four fields works; "be concise" mostly does not
  ([[prompts]]).

## Move work out of the context window

Let the agent **call code that filters, aggregates or paginates** and return
only the answer, instead of piping raw tool output through the model. On
data-heavy steps this is a **one-to-two order of magnitude** reduction. It is
the same argument as pushing computation into the database rather than looping
in the application ([[tool-calling]]).

## Batching

For anything **not user-facing** — evals, backfills, bulk classification — use
the batch API: typically **around half price**, asynchronous, at the cost of
**unpredictable completion time**. Free money on offline workloads.

## Cost per conversation as a design constraint

- **Budget it up front**, alongside the latency target.
- **Attribute it per tenant and per feature** ([[evals-observability]],
  [[enterprise-multitenancy]]) and **alert on drift** — a prompt change or a
  chattier tool can double spend without failing anything.
- An agent that is accurate but unprofitable does not ship.

## The hard part

**These levers fight each other.** Caching wants a long stable prefix; trimming
wants a short one. Guardrails and self-consistency buy safety with latency and
tokens. More retrieved context costs money **and** can reduce accuracy
([[rag-retrieval]]). Smaller models are cheaper and less reliable. There is no
global optimum — **pick the constraint that binds** (usually latency for
interactive, cost for batch) and optimize explicitly against it, accepting
regressions on the others.


## Related

- [[agent-loop]], [[llm-basics]], [[tool-calling]], [[rag-retrieval]],
  [[prompts]], [[evals-observability]], [[guardrails]],
  [[enterprise-multitenancy]], [[antipatterns]]

Source: platform.claude.com/docs/en/build-with-claude/prompt-caching (prefix
matching, tools→system→messages invalidation, write/read ratios, minimum prefix,
TTL); platform.claude.com/docs/en/build-with-claude/context-editing;
platform.claude.com/docs/en/build-with-claude/batch-processing;
anthropic.com/engineering/code-execution-with-mcp. Ratios are stable, prices
are not — check current docs before quoting numbers.
