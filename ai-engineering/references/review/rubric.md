# LLM System Review Rubric

Score an agent, prompt pipeline or RAG system against these. Each theme is a
short list of **questions to ask out loud**, with a note on what a good answer
sounds like. For each theme, state what's good, what's missing, and the one
change with highest leverage.

## 1. Scope and fit

- **Does this need a model at all?** Good answer names the part that genuinely
  needs language understanding, and admits the rest is code.
- **Would a rule, a lookup, or plain search do it?** "We tried the boring
  version first" is the answer you want; "we started with an agent" is not.
- **Is this a workflow being called an agent?** Fixed steps in a fixed order is
  a pipeline — cheaper, testable, and fine. Only a model choosing the next step
  makes it an agent ([[agent-loop]]).
- **What is the simplest version that would work?** If nobody can describe it,
  the current design was never compared against anything.

## 2. Determinism and blast radius

- **Which parts are probabilistic and which are code?** A good answer draws the
  line precisely; a vague one means nobody knows where variance enters
  ([[non-determinism]]).
- **What can the agent actually DO?** Ask for the tool list, not the prose
  description. Read-only vs write is the whole risk conversation
  ([[tool-calling]]).
- **Are write tools idempotent?** Retries and duplicated tool calls happen. An
  idempotency key or a natural no-op on repeat is the good answer.
- **Is there a step budget, a timeout, and a cost ceiling per run?** Unbounded
  loops are the default failure mode of a bad agent loop.
- **Is there an approval gate on irreversible actions?** Refunds, deletes,
  emails, payments — human in the loop or a hard-coded allowlist.
- **Is there a kill switch?** Can someone disable the feature, or one tool, in
  minutes without a deploy?

## 3. Context discipline

- **What fills the window on a long conversation?** Good answer is a concrete
  budget per section: system prompt, history, retrieved docs, tool results.
- **Does it grow unboundedly?** Turn 40 of a support chat is the test case.
- **What gets dropped or compacted, and by what rule?** Silent truncation of
  the middle is a correctness bug, not a cost optimization ([[llm-basics]]).
- **Is more context being added where less would do better?** Stuffed windows
  raise cost and latency and dilute attention ([[cost-latency]]).

## 4. Grounding and retrieval

- **Where do the facts come from?** Every claim should trace to a retrieved
  document or a tool result, not to model priors.
- **Is retrieval a tool the model calls, or a fixed pre-step on every turn?**
  Both are valid; the good answer knows which it chose and why
  ([[rag-retrieval]]).
- **How would you know retrieval missed?** If the answer is "the user tells
  us", there is no recall measurement at all.
- **Is the index fresh, and what reindexes it?** Stale embeddings produce
  confidently outdated answers.
- **Is a vector index justified over an exact-match tool?** For ids, orders,
  and structured records, a query is better than a similarity search.

## 5. Measurement

- **Is there a golden set, and how big?** 20 real cases beats 500 generated
  ones ([[evals-observability]]).
- **What gates a prompt change reaching production?** "An eval run in CI" is
  the good answer; "we eyeball a few" is the common one.
- **Are there online metrics, not just offline?** Production distribution is
  never the one you imagined.
- **Is quality measured directly, or inferred from uptime?** Wrong answers
  return HTTP 200 — an APM dashboard cannot see them.
- **Are containment and resolve rate defined and distinguished?** Containment
  is gameable by refusing to escalate; resolve rate is the real number.
- **Is cost attributed per conversation and per tenant?** One monthly provider
  bill is unattributable.

## 6. Failure and safety

- **How does it fail silently?** The interesting failures look like successes.
- **What happens on a hallucination — who catches it and when?** Good answer
  names a grader, a citation check, or a human review sample.
- **Where does untrusted text enter?** Retrieved docs, tool outputs, user
  files, web pages. **What stops that text acting as instruction?**
  ([[guardrails]])
- **What is the escalation path, and does it carry context?** Handing a human a
  cold transcript-less ticket is a failed escalation.
- **What does the user see when the agent gives up?** A visible, honest dead
  end beats a confident guess.

## 7. Change management

- **Are prompts versioned and reviewed like code?** In the repo, in diffs, not
  in a dashboard textbox someone edits live ([[prompts]]).
- **Is the model version pinned?** Otherwise a score change cannot be
  attributed to your edit.
- **Can a bad prompt be reverted in minutes?** Name the mechanism.
- **Is per-customer behaviour configuration or a fork?** Forked prompts per
  tenant do not scale past a handful ([[enterprise-multitenancy]]).

## 8. Economics

- **What does one conversation cost?** A number, not a shrug
  ([[cost-latency]]).
- **What is p95 latency, and time-to-first-token separately?** They are
  different experiences with different fixes.
- **Is prompt caching actually being hit?** Ask for the hit rate. A variable
  timestamp or user id near the top of the prompt silently invalidates it.

## The three questions

If time is short, ask only these:

1. **How would this system tell you it was wrong?**
2. **What is the worst thing it can do unsupervised?**
3. **What gates a prompt change reaching production?**

A system that cannot answer all three is not production-ready, however well it
demos. A system that answers all three is usually sound in the rest too.

## Related

- [[agent-loop]], [[non-determinism]], [[tool-calling]], [[llm-basics]],
  [[rag-retrieval]], [[evals-observability]], [[guardrails]], [[prompts]],
  [[cost-latency]], [[enterprise-multitenancy]], [[antipatterns]]

Source: synthesis — distilled from the sibling leaves in this skill rather than
any single external source.
