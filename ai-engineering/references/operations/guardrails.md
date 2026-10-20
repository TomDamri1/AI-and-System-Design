# Guardrails, Hallucination and Escalation

This is the leaf about the answers you do not want shipped and the actions you
do not want taken. Hallucination is the quality failure, prompt injection the
security one, and escalation the release valve for both. All three share a
root cause: a language model will always produce *something*, and it has no
built-in signal for "I should not have."

## Hallucination is not an error path

- The model returns text that is fluent, confident, well-formed, on-topic —
  and wrong. A fabricated refund window, a plausible-looking order id, a
  citation to a document that does not exist.
- It comes back with a **success status**. No exception, no 500, no retry.
  This is exactly why ordinary monitoring never sees it: there is no
  infrastructure signal for "untrue" ([[evals-observability]]).
- Treat it as a **quality failure measured on its own axis**, not as a bug
  class you will eventually fix. Reduction and detection, not elimination.

## Reducing it

- **Explicitly permit "I don't know."** A model given no licensed way to fail
  will invent. Say in the prompt that an unsupported answer must be declined.
- **Ground answers in retrieved source material** ([[rag-retrieval]]) and
  require **a verbatim quote or a citation per claim**, then have the model
  retract anything it cannot support. Extraction is a far easier task than
  recall.
- **Restrict the model to the provided context** for factual questions. Cut
  off appeals to parametric memory for anything the business cares about.
- **Chain-of-thought verification** — make the model state its evidence before
  its conclusion, and re-check the conclusion against the evidence.
- **Best-of-N / self-consistency sampling** for high-stakes answers: sample
  several times and keep what agrees.
- Every one of these costs latency or tokens. Spend them where the blast
  radius justifies it ([[cost-latency]]).

## Detection

- **Grounding / entailment checks** — does the retrieved source actually entail
  the claim? Cheap NLI models or a judge do this well.
- **Self-consistency across samples** — divergence between samples is a decent
  smoke signal ([[non-determinism]]).
- **Deterministic validators** — does that order id exist, does the total match
  the database, is the cited doc real. Free, exact, and badly underused.
- **A cheap secondary classifier** on the output, in parallel with returning it.
- **Token-level probabilities are a poor confidence proxy.** A model is very
  often confidently wrong; high logprobs mean fluent, not correct.

## Structured output as a guardrail

Constraining generation to a schema removes an entire class of failures —
malformed JSON, invented enum values, missing fields — before any semantic
check runs. It is the cheapest guardrail available and it is a decoding
constraint, not a request ([[prompts]], [[tool-calling]]).

## Prompt injection

- **Direct** — the user types the attack. **Indirect** — it arrives inside a
  retrieved document, a web page, an email, or a tool result, and the user
  never sees it.
- **Root cause: instructions and data share one channel.** Anything untrusted
  that reaches the context window can attempt to issue instructions, because
  the model has no privileged way to tell your prompt from a stranger's.
- Defenses, **none sufficient alone**: keep untrusted content in dedicated
  tool-result/data slots and encode it so it cannot break out of its
  container; screen inbound user text and outbound tool results with a cheap
  classifier; apply **least privilege** to tools so a successful injection
  cannot do much; require **human approval for irreversible actions**;
  red-team your own agent.
- Consensus as of now is that prompt injection is **not solved**. Design so a
  successful injection is *survivable* rather than assuming prevention.

## The risk taxonomy

The industry list for LLM apps consistently ranks **prompt injection first**
and **sensitive information disclosure second**. The sharpest riser is
**excessive agency** — an agent granted more permissions, tools or autonomy
than its task requires. Excessive agency is what turns a text bug into a
business incident: the hallucination is annoying, the hallucination with a
refund API key is an outage.

## PII and data minimization

**Redact before logging and before sending to a third-party model.** Be
deliberate about what enters traces and eval datasets — those are long-lived,
widely-read copies of customer data, and they outlive the conversation that
produced them ([[enterprise-multitenancy]]).

## Escalation to a human

A first-class feature, not a fallback.

- **When:** low grounding or confidence, repeated failed attempts, an explicit
  request, detected distress, or any action above a risk threshold.
- **How:** transfer the conversation **with its context** — a summary, what was
  tried, what the customer wants, the relevant records — so the human does not
  restart from zero. Tool-approval patterns that pause a run and return
  **resumable state** are the mechanism ([[agent-loop]]).
- **A silent bad answer is far worse than an escalation.** Score escalation as
  a success when it was the right call ([[evals-observability]]).

## The hard part

Guardrails cost latency and money on **every** request while catching a small
fraction of them, so there is permanent organizational pressure to remove the
ones that have not fired lately — which is the same as removing the ones that
are working. And layering them serially can cost more latency than the model
call itself: an input classifier, a grounding check and an output classifier
chained in front of a 900ms generation triple the user's wait. You have to
decide **per guardrail** which must run blocking, which can run in parallel
with generation, and which are post-hoc sampling of production traffic
([[cost-latency]]).

## Related

- [[prompts]], [[rag-retrieval]], [[evals-observability]], [[agent-loop]],
  [[tool-calling]], [[cost-latency]], [[non-determinism]],
  [[enterprise-multitenancy]], [[antipatterns]]

Source: platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks;
platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations;
developers.openai.com/api/docs/guides/agents/guardrails-approvals;
genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ — the OWASP list is
revised periodically, so check the current edition rather than trusting a
remembered ranking.
