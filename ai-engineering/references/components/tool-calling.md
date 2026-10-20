# Tool Calling

How a model reaches outside its context window: you describe functions, it asks
for one to be run, your code runs it. Everything agentic is built on this loop,
and most of its failure modes are schema and error-message design, not modelling.

## The round trip, stated precisely

1. You send the prompt **plus a list of tool schemas** (name, description,
   JSON parameter schema) in the request.
2. The model replies with a **stop reason indicating tool use** and a structured
   call: a tool name, an id, and JSON arguments. This is a *request*, not an act.
3. **Your code executes it.** Validate, authorise, run, catch.
4. You send the output back as a **tool-result message** keyed to that call id,
   with the model's own tool-request turn preserved in the history.
5. The model continues from there, possibly calling again ([[agent-loop]]).

- **The model never executes anything.** It emits text describing a call. Most
  beginner bugs are here: expecting side effects to happen, dropping the
  assistant turn before the result, or omitting the id that pairs them.
- Provider-hosted tools (web search, code execution) are the exception: the
  vendor runs them, so no result message from you. The contract is otherwise
  identical, so treat client-executed tools as the default mental model.

## Schemas are prompt surface

- The **tool name, its description and every parameter description are read by
  the model** and are the only thing it selects on. A vague description is a
  bug, exactly like a vague system prompt ([[prompts]]).
- Say what the tool does, when to use it, when *not* to, and what it returns.
- Tool definitions are resent on **every request, called or not**, and cost
  input tokens each time, along with a vendor system prompt that tool use
  enables. Twenty tools can outweigh the conversation ([[llm-basics]]).

## Schema design

- Use **strict / constrained decoding** where offered so arguments are
  guaranteed to validate against the schema — it removes a whole class of retry.
- **Enums over free strings.** `status: "open"|"closed"` cannot be misspelled;
  `status: string` will be.
- **Namespace related tools** (`calendar_list`, `calendar_create`) so selection
  is a two-step narrowing rather than a flat scan.
- Keep the count small — **roughly under 20** before mis-selection climbs. Merge
  near-duplicates, drop unused ones, or load tools on demand.
- **Offload work to code.** Never make the model sum, sort, paginate, or
  reformat what a function can do exactly and for free.

## Errors

- Return **instructive errors**: "Rate limit exceeded, retry after 60 seconds"
  or "No user with that email; try search_users first" — never "failed". The
  model can only adapt to what the error says.
- **Mark errors as errors** using the protocol's error flag rather than
  returning apologetic prose that reads as a successful result.
- Validation failures are cheap teaching moments: name the offending field and
  the allowed values, and the retry usually succeeds.

## Untrusted input

**Tool results are untrusted input.** A fetched page, a database row or another
agent's output can contain text aimed at the model. Never treat it as
instruction; delimit it, and gate consequential follow-on actions ([[guardrails]]).

## Parallel, sequential, compositional

- **Independent** calls (three lookups on different ids) can be issued in one
  turn and executed concurrently — the main latency win in an agent.
- **Compositional / chained** calls feed one output into the next input and are
  inherently sequential; the model must see result *n* to form call *n+1*.
- Latency is therefore set by chain depth, not call count ([[cost-latency]]).

## Side effects

Models retry and may fire the same call in parallel. Give write tools
**idempotency keys** and keep a **read/write split** so the risky surface is
small. Depth in [[non-determinism]].

## The hard part

**A tool is an API whose consumer is non-deterministic, and normal API design
intuitions do not transfer.** Terse names, positional conventions, opaque ids
and "the caller will read the docs" all assume a programmer who reads once and
codes forever. This caller re-reads the description on every request, has no
memory of your conventions, and guesses when the schema is ambiguous. So: spell
names out, describe every field, and **return semantically meaningful values
over opaque ids** — a result saying `owner: "tom@example.com"` lets the next
call be formed directly, while `owner_id: "u_8823"` forces a lookup the model
may hallucinate instead. Design for a competent colleague reading the signature
cold, not for a compiler. Then measure selection accuracy: wrong-tool and
wrong-argument rates are first-class eval metrics ([[evals-observability]]).


## Related

- [[mcp]], [[agent-loop]], [[prompts]], [[guardrails]], [[non-determinism]],
  [[llm-basics]], [[cost-latency]], [[evals-observability]], [[antipatterns]]

Source: platform.claude.com/docs — tool-use/overview, handle-tool-calls;
anthropic.com/engineering/writing-tools-for-agents;
developers.openai.com/api/docs/guides/function-calling
