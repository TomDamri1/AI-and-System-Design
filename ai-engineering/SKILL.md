---
name: ai-engineering
description: >
  Design and review guidance for production LLM systems and AI agents: tool
  calling, agent loops, RAG, MCP, evals, guardrails, cost and latency, voice,
  multi-tenant deployment. Use when the user is designing or reviewing how an
  LLM system should work, or asks why one is wrong, slow or expensive. Not for
  routine coding that merely touches these words.
---

# AI Engineering

This skill helps developers **build LLM systems that survive production** and
**review AI architectures**. It is a router: read only the leaf file(s)
relevant to the task — do not load everything.

**Core principle: an agent is a distributed system with a non-deterministic
component in the middle.** Every classic tool still applies (retries,
idempotency, queues, caching, observability), but the failure detection is
different: an LLM can be wrong, confident, and return HTTP 200. Never present a
technique as "the fix." State what it buys, what it costs, and how you'd know
it stopped working.

## Three modes — detect which one the request is

1. **Build** — user is creating something ("build an agent that…", "how do I
   wire tools"). Start at `references/foundations/llm-basics.md` for the
   budget, then pull component leaves as the design takes shape.
2. **Lookup** — user asks a focused question ("what's a good chunk size?",
   "how do I stop prompt injection?"). Jump straight to the matching leaf.
3. **Review** — user has an existing agent / prompt / pipeline and wants
   critique. Use `references/review/rubric.md` +
   `references/review/antipatterns.md`, then pull leaves for the parts under
   scrutiny.

## Routing table — read the leaf, then answer

### Foundations (the vocabulary everything else assumes)
- `references/foundations/llm-basics.md` — tokens, context window as a memory
  budget, context rot, cost model, TTFT vs total latency, streaming, model
  routing, why fine-tuning is usually the wrong first answer. **Start here.**
- `references/foundations/non-determinism.md` — what actually changes versus
  classic systems: testing, retries, idempotency for tool side effects, and
  failure that looks like success.

### Components (the building blocks)
- `references/components/tool-calling.md` — the round trip (you pass schemas,
  the model *requests*, your code executes), schema design, instructive tool
  errors, parallel vs sequential, side effects.
- `references/components/agent-loop.md` — workflows vs agents (who owns
  control flow), the loop, termination, conversation state, memory, multi-agent
  and handoff.
- `references/components/rag-retrieval.md` — retrieval as a tool the agent
  calls, chunking and contextual enrichment, hybrid search, reranking, failure
  modes, and when to skip embeddings entirely.
- `references/components/prompts.md` — message roles, structured output as a
  contract, prompt versioning and rollback, per-tenant config over forking.
- `references/components/mcp.md` — the Model Context Protocol: what it solves,
  hosts/clients/servers, tools vs resources vs prompts, transports, the
  security surface of a third-party server, and when a plain function is
  better.
- `references/components/webmcp.md`: WebMCP, a web page registering its own
  tools for an in-page agent via `document.modelContext`, why not a manifest,
  malicious manifests vs contaminated outputs, spotlighting, and why a
  client-side tool is not a security boundary. Draft spec, still moving.

### Operations (what makes it survivable)
- `references/operations/evals-observability.md` — why you can't unit-test an
  LLM, golden sets, offline vs online, LLM-as-judge, regression on prompt
  change, tracing spans, cost attribution.
- `references/operations/guardrails.md` — hallucination detection, grounding,
  prompt injection, PII, escalation to a human.
- `references/operations/cost-latency.md` — prompt caching and prefix
  invalidation, context trimming (and its tension with caching), model routing,
  batching, cost per conversation.

### Deployment (getting it into someone else's world)
- `references/deployment/voice-telephony.md` — STT→LLM→TTS vs speech-to-speech,
  the latency budget, turn detection, barge-in, SIP and transports.
- `references/deployment/enterprise-multitenancy.md` — tenant isolation,
  configuration over forking, data residency, credentials into customer
  systems, safe rollout, and the disclosure obligations that now apply.

### Review
- `references/review/rubric.md` — checklist to score an LLM system against.
- `references/review/antipatterns.md` — common smells and what to ask instead.

## How to answer
- Cite the leaf you used so the user can go deeper.
- Lead with the decision and the trade-off, not a feature dump.
- Name the **failure mode** — for LLM systems that means saying how the thing
  breaks *silently*, not just how it errors.
- Prefer boring determinism: if code can do it, don't make the model do it.
