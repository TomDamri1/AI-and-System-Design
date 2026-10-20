# Evals and Observability

This is the leaf that turns a demo into a product. An LLM feature you cannot
measure is a feature you cannot change safely: no test to gate the prompt
edit, no trace to explain the bad answer, no metric to say whether it works.
Evals are the offline half, observability the online half, and you need both.

## You cannot unit-test an LLM

- A unit test asserts an exact expected output. An LLM has no single correct
  string, and the same input may yield different text on the next call
  ([[non-determinism]]). `assertEqual` has nothing to hold onto.
- What replaces it is a **golden set**: curated examples, each with either a
  **reference output** or a **checkable property** ("returns valid JSON",
  "cites a real doc id", "refuses"). Start small — 5 to 20 hand-written cases
  per component beats a large auto-generated set nobody trusts.
- Running a version of the system against that set is an **experiment**: it
  records outputs, grader scores and traces per example, so you compare
  *scores across versions* rather than asserting on any one answer.
- **An eval suite is to a prompt what a test suite is to code**, and it is the
  gate that makes a prompt change shippable ([[prompts]]).

## Offline vs online

- **Offline** runs the curated dataset with known answers *before* you ship.
  It catches regressions and answers "is v2 better than v1".
- **Online** scores live production traffic, where there is no reference
  output — so graders are reference-free (schema checks, judge on tone or
  groundedness, user feedback signals).
- You need both. Offline catches regressions; **online catches the input
  distribution you failed to imagine**. Feed the surprising production cases
  back into the golden set — that loop is how the suite stays honest.

## Grader types, cheapest first

- **Deterministic code checks** — schema conformance, did it call the right
  tool with the right arguments, does the number match the database, is the
  cited id real. Fast, free, no variance. **Prefer these wherever the property
  is checkable**; most teams reach for a judge far too early.
- **String and similarity metrics** — exact match, regex, embedding distance.
  Cheap, brittle on paraphrase, fine for classification-shaped tasks.
- **LLM-as-judge** — for subjective qualities (helpfulness, tone, coherence,
  groundedness) that no code check expresses.
- **Human review** — the expensive ground truth. Its real job is not to grade
  everything but to **calibrate the cheaper graders**.

## LLM-as-judge, honestly

Useful and scalable, and biased in known directions:

- Prefers **longer answers**, prefers **its own model family's outputs**, and
  is sensitive to **option ordering** in comparisons.
- Mitigations: write an explicit **rubric**; **few-shot calibrate** the judge
  against human-labelled examples; use **binary or low-cardinality scales**
  (pass/fail, 3 levels) rather than 1-10, which is noise dressed as precision;
  use **pairwise comparison** where the question is "which is better", and
  swap the order to cancel position bias.
- **Validate the judge against human labels before trusting it.** An unvalidated
  judge is a second unmeasured model in your quality pipeline.

## Regression testing on prompt change

The core operational loop, and the reason the suite exists:

1. Change the prompt, the model, the retrieval config, or a tool schema.
2. Re-run the golden set as a new experiment.
3. **Diff the scores** against the previous version, per example — an
   aggregate that holds steady can hide ten fixes and ten new breaks.
4. Gate the deploy on it, in CI. No eval run, no merge.

Pin the model version, or you cannot attribute a score change to your edit.

## Tracing

- **One trace per conversation or run**, with a **span per model call and per
  tool call**, nested to mirror the actual control flow ([[agent-loop]]).
- Each span captures **inputs, outputs, latency, token counts, model/version,
  and errors**. Span kinds worth naming consistently: `llm`, `agent`,
  `workflow`, `tool`, `task`, `embedding`, `retrieval`.
- Without per-span traces you cannot answer **"which step made this wrong"** —
  bad retrieval, bad tool arguments, bad tool result, or bad final synthesis
  all look identical from the outside.
- Traces are also your eval dataset source: promote a real failed trace into
  the golden set in one click, and it can never regress silently again.

## Cost and token attribution

- Roll tokens and spend up **per conversation, per tenant, per feature**, not
  just per API key. A single monthly provider bill is unattributable.
- **Cost per conversation is a product metric, not a finance metric** — it
  decides whether the feature can be offered on the cheap tier
  ([[cost-latency]], [[enterprise-multitenancy]]).

## Product metrics, defined precisely

No authoritative first-party source defines these, and they get conflated
constantly. **Agree the definitions explicitly, in writing, as a team.**

- **Containment** — the share of conversations closed **without a human ever
  touching them**. Note it says nothing about whether the user was helped, and
  it is **gameable by simply refusing to escalate**.
- **Resolve rate** — the subset of those where the user's problem was
  *actually solved*. This is the number that matters; it needs a signal
  (user confirmation, no repeat contact within N days, judge or human review).
- **Escalation rate** — handed to a human. Not the inverse of resolve rate;
  a fast correct escalation is a success, not a failure.
- **Latency**, with **time-to-first-token tracked separately** from total
  completion — they are different user experiences and different fixes.
- **Cost per conversation**, as above.
- **A satisfaction signal** — thumbs, CSAT, or a proxy. Sparse and biased
  toward the angry, so read it as a trend, never as a level.

## The hard part

**The failure you must catch returns HTTP 200.** A hallucinated refund policy,
a fabricated citation, a confidently wrong account balance — all of it is a
successful response by every measure standard APM collects. Your uptime
dashboard shows 100% success and p99 latency well inside SLO while the agent
tells customers things that are not true, which makes that dashboard not
merely unhelpful but **actively misleading**: it manufactures confidence
precisely when quality is failing. There is no infrastructure signal for
"wrong". Quality has to be measured directly, on its own axis, with graders
and traces and human review — or it is not being measured at all
([[non-determinism]]).

## Related

- [[prompts]], [[non-determinism]], [[agent-loop]], [[cost-latency]],
  [[guardrails]], [[rag-retrieval]], [[rubric]], [[antipatterns]]

Source: docs.langchain.com/langsmith/evaluation-concepts;
platform.claude.com/docs/en/test-and-evaluate/develop-tests;
docs.datadoghq.com/llm_observability/terms/;
docs.datadoghq.com/llm_observability/monitoring/metrics/
