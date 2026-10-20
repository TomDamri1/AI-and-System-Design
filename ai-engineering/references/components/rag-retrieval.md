# RAG and Retrieval

How a model gets facts it was not trained on. The 2023 answer was a pipeline
that stuffed chunks into a prompt; the 2026 answer is a **tool the agent calls**
when it decides it needs something. Most stale advice on this topic is stale in
the same direction.

## The reframe, stated up front

- Retrieval is no longer a pre-inference stage that embeds a query, takes
  cosine top-k, and pastes the result above the user message. It is a **tool
  the agent invokes** ([[tool-calling]]), possibly several times, **adapting
  each query to what the previous one returned**.
- **Agentic retrieval has displaced classic RAG as the default architecture —
  not as the underlying technology.** Embeddings did not die. They were
  demoted from *being the system* to *one tool the agent may call*.
- Classic single-pass RAG is now a **component**: a fine default inside a
  narrow, well-understood lookup, a bad shape for an open-ended question.
- One-shot retrieval breaks on **multi-hop** questions (the second hop depends
  on the first answer) and **ambiguous** ones (the right query is not knowable
  before you see results).

## Pre-inference vs just-in-time

- **Pre-load** what is cheap and near-certainly useful: schemas, the style
  guide, the current file, a small policy doc. Cache it ([[cost-latency]]).
- **Fetch just-in-time** for everything else — the agent asks only for what
  the task turned out to need.
- Pure just-in-time is **slow**: every hop is a round trip. Pure pre-inference
  is **stale and blind** to what the query actually needs. Hybrid wins.

## Consider skipping embeddings entirely

- Where an **exact-match tool already exists** — code, filesystems, SQL, a real
  API — `grep`, `find`, and parameterised queries usually beat an embedding
  index and cost far less to maintain (no pipeline, no drift, no reindex).
- Anthropic **removed vector search from Claude Code** in favour of grep plus
  file reads. The identifiers people search for are literal strings.
- Under ~200k tokens of corpus, **just put it in the prompt** with caching.
- Building an index is a **choice to justify**, not a default.

## If you do index: contextual retrieval

- **Chunking is where most RAG dies.** A chunk ripped out of its document
  loses the context that made it meaningful — "revenue grew 3%" with no
  company, no quarter.
- **Contextual retrieval**: before embedding, prepend a short generated
  description (50–100 tokens) situating the chunk in its parent document.
  Highest-leverage fix available, and cheap with prompt caching.
- Measured on Anthropic's benchmark: contextual embeddings cut retrieval
  failures **~35%**; plus contextual BM25 **~49%**; plus reranking **~67%**.
- Note the shape of that ladder: **chunk-size tuning is not on it**.

## Hybrid search and reranking

- **Hybrid search** = semantic/vector (meaning, paraphrase) **plus**
  keyword/BM25 (exact identifiers, error codes, rare terms), fused — commonly
  **reciprocal rank fusion**. This has been the measured baseline for years;
  embeddings-only is a downgrade, not a simplification.
- **Reranking** is a second-stage precision filter: retrieve wide for recall
  (top ~150), rerank, pass a narrow set (top ~20) to the model. Costs a model
  call's worth of latency — measure whether it earns it.

## Storage choice

- **pgvector** while the corpus fits comfortably on one Postgres box and you
  want transactional consistency between documents and their embeddings —
  one system, one backup, no dual-write skew.
- **Dedicated vector store** for billion-scale ANN, independently scaled
  query load, or **filtered-ANN** patterns that degrade badly with HNSW plus
  a `WHERE` clause.
- Frame it as ordinary **index selection**, not an architecture decision.
  Honest caveat: no neutral first-party source benchmarks this comparison —
  vendor numbers only.

## Failure modes

- **Retrieval miss** — the answer exists, the query did not surface it.
- **Stale index** — the document changed, the embedding did not.
- **Chunk lacking context** — retrieved, but unusable in isolation.
- **Model ignores retrieved context** — it answers from parametric memory
  instead; catch this with citation-grounded evals ([[evals-observability]]).
- **Irrelevant context actively hurts.** OpenAI documents a case where adding
  retrieval on top of a fine-tuned model **lowered** accuracy: noise drowned
  the signal. More retrieved context is not better — see context rot in
  [[llm-basics]].

## The indexing pipeline is a normal data pipeline

Ingestion, change capture, re-embedding on document change, a **freshness
SLA**, backfill and reindex on model or chunking change, plus monitoring for
each. Nothing exotic — and it is the part teams forget to staff.

## Stale advice to flag

- "Chunk everything, embed, cosine top-k, stuff the prompt" **as an
  architecture**.
- **Chunk-size tuning** as the primary lever.
- "You need a vector database."
- **Embeddings-only** retrieval.
- **One-shot** retrieval before generation.

## The hard part

**Deciding whether to build an index at all, then proving retrieval is the
thing that failed.** The default answer used to be automatic; now the first
question is whether an exact-match tool already exists, because an index is
permanent operational surface — a pipeline, a freshness SLA, a reindex every
time the embedding model or chunking changes. When quality is bad, the failure
could be retrieval, chunking, ranking, or the model ignoring what it got, and
you cannot tell them apart without **separate retrieval metrics** (recall@k on
a labelled set) from **answer metrics**. Instrument the two independently or
you will tune the wrong stage for a week.

## Related

- [[tool-calling]], [[agent-loop]], [[llm-basics]], [[prompts]],
  [[cost-latency]], [[evals-observability]], [[antipatterns]]

Source: anthropic.com/engineering/contextual-retrieval;
anthropic.com/engineering/effective-context-engineering-for-ai-agents;
anthropic.com/engineering/multi-agent-research-system;
developers.openai.com/api/docs/guides/optimizing-llm-accuracy
