# LLM Basics

The vocabulary every other leaf assumes. An architect doesn't need the maths,
they need the four budgets a model imposes — context, cost, latency,
determinism — and where each one bends.

## Tokens and the context window

- **Token** — the unit models read and emit, roughly a word fragment. Billing,
  limits and speed are all denominated in tokens, not words or characters.
- **Context window** — everything the model can reference for one request,
  *including the response it is about to generate*. Working memory, not
  knowledge: nothing persists between requests unless you resend it.
- Treat it as a **memory budget** spent every turn. It is consumed by:
  - the **system prompt**;
  - **tool definitions** — name, description and JSON schema for every tool, on
    every request, called or not. Twenty tools can outweigh the conversation;
    the most commonly missed line item.
  - **tool results** — usually the largest, fastest-growing item in an agent;
  - **conversation history**, resent in full each turn;
  - **thinking tokens**, billed as output when generated and, on models that
    retain them, re-billed as input later;
  - images and documents, tokenised too.
- Caching changes what you *pay* for a prefix, not whether it occupies space.
- Overflow is not graceful: input past the limit is a hard request error, and
  generation that hits the ceiling stops mid-answer. Count, don't guess.

## Context rot

- Accuracy and recall **degrade as the window fills**, well before the limit.
  More context is not better context. Vendors call this *context rot*.
- So curating what enters matters more than how much room remains: retrieve
  five relevant chunks not fifty, prune stale tool results, compact long
  histories. "Just use the million-token model" is not an architecture.

## Cost model

- Priced per **input token** and per **output token**, separately. Output
  typically costs around **5x input** on frontier models, a ratio stable across
  vendors even as absolute prices fall. Thinking bills at the output rate.
- Verbosity is the expensive failure mode: a large prompt is cheaper than it
  looks beside a rambling answer. Structural wins are caching the stable prefix
  and routing bulk work to a small model ([[cost-latency]]).

## Latency model

- **Time to first token (TTFT)** — prompt in, first token out; driven by input
  size and queueing. **Total generation time** — TTFT plus one increment per
  output token, so output length dominates. A long answer is slow however small
  the prompt.
- Cap the **shape** of the output, not its wording: ask for "two sentences" or
  "one paragraph", never "under 50 words" — models count tokens, so word limits
  are poorly obeyed. `max_tokens` truncates mid-sentence: safety rail, not style
  knob.
- **Streaming improves perceived latency only.** Total time is unchanged. Real
  fixes are fewer output tokens, a smaller model, or parallel calls.
- Sampling draws each token from a probability distribution and **temperature**
  scales how peaked it is. Low temperature is focused, not deterministic — even
  temperature 0 varies run to run ([[non-determinism]]).

## Model routing

- Start **efficiency-first** (small fast model, upgrade where evals show a gap)
  or **capability-first** (strongest model, push work down once flow is
  stable). Choose by whether the risk is "can it do this" or "can we afford it".
- Models expose an **effort / thinking-budget knob** trading intelligence
  against latency and cost *within one model*. Tuning it usually beats switching
  models: prompts, evals and tool behaviour stay fixed while cost moves.
- Mixed fleets are normal — a cheap executor escalating to a frontier advisor,
  or an orchestrator delegating bulk work to small workers.

## The hard part

**Fine-tuning is almost never the right first answer.** Split the failure:
missing *knowledge* (in-context memory) or missing *behaviour* (learned memory)?
Wrong facts, stale data or no access to proprietary content is a context problem
— better prompt, then retrieval ([[rag-retrieval]]). Right facts but wrong
format, tone or inconsistent procedure is a behaviour problem, where fine-tuning
is a candidate. Order: prompting, retrieval, fine-tuning. Skipping ahead buys a
slow, costly, hard-to-update artefact that still doesn't know today's data. Nor
are the layers additive by default: in OpenAI's documented Icelandic case,
adding retrieval on top of a fine-tuned model *dropped* the score from 87 to 83
BLEU, because irrelevant context drowned a signal the model had already learned.
Measure each layer with [[evals-observability]] before adding the next.

## Related

- [[non-determinism]], [[prompts]], [[tool-calling]], [[rag-retrieval]],
  [[cost-latency]], [[evals-observability]], [[antipatterns]]

Source: platform.claude.com/docs — context-windows, choosing-a-model,
reduce-latency; developers.openai.com/api/docs/guides/optimizing-llm-accuracy
