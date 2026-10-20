# The Agent Loop

What turns a single model call into a system that keeps going until a task is
done. The whole topic reduces to one question — **who owns control flow** — and
then to the unglamorous engineering of stopping, budgeting, and remembering.

## Workflows vs agents

- In a **workflow**, control flow is **predefined in code**. You wrote the
  steps; the model fills in each one. Deterministic shape, auditable, cheap.
- In an **agent**, the **model decides what to do next**, and a loop keeps
  running until a stopping condition fires. Open-ended shape, variable cost.
- Both are "agentic systems". The dividing line is not tool use, autonomy vibes
  or number of calls — it is **whether the next step is chosen by your code or
  by the model**. Lead with this in any interview answer.
- Choose an agent when the step sequence genuinely cannot be enumerated ahead
  of time. If you can draw the flowchart, write the flowchart.

## Start with the simplest thing that works

- Most production value comes from **one well-prompted call** ([[prompts]]),
  then a **workflow**, and only then an agent. Add complexity only when it
  demonstrably improves outcomes.
- A fully autonomous agent is the **most expensive and least predictable**
  option: it trades latency, cost and reproducibility for task performance.
- **Single agent first.** Reach for extra agents after one agent with good
  tools and a good prompt has visibly hit a ceiling.

## Workflow patterns worth naming

- **Prompt chaining** — fixed sequence; each call consumes the previous output.
- **Routing** — classify the input, dispatch to a specialised handler.
- **Parallelization** — fan out independent subtasks (sectioning), or run the
  same task repeatedly and aggregate (voting).
- **Orchestrator with subagents** — a lead model decomposes dynamically and
  delegates to workers, then synthesises.
- **Evaluator-optimizer** — a generator and a critic iterate to a bar.

## The loop itself

Gather context → **take action** (a tool call, [[tool-calling]]) → **observe**
the result → repeat until a stop condition. Each turn appends the action and
its result to the conversation, so the window grows monotonically.

- **ReAct** interleaves reason/act/observe every turn. **Plan-then-execute**
  fixes a plan up front, then runs the steps. These are academic labels for
  variants of the same loop — know them by name because papers and interviewers
  use them, while vendor docs mostly describe the mechanics unlabelled.
- The loop only works if the environment returns **ground truth** each step.
  Vague or missing tool results leave the model guessing at its own progress.

## Termination is a design problem

- Set **max steps/turns**, a **token budget**, and a **wall-clock timeout**.
  Every loop needs all three; any one alone has a runaway mode.
- Detect a **stuck agent**: repeated identical tool calls, oscillation between
  two states, no progress against the goal for N turns.
- Decide what happens **when the budget is exhausted**. Degrade to a human or a
  deterministic fallback path, and surface it. Silent failure or a confident
  half-answer is the worst outcome.

## Conversation state across turns

- The window is finite, so **every turn is a choice** about what to keep
  verbatim, what to **compact** (summarise older turns into a brief), and what
  to drop entirely.
- **Tool results are usually the largest and most droppable payload** — a
  200-row query result matters this turn and rarely three turns later. Truncate
  or replace old results with a one-line digest.
- Keep the original goal and recent turns verbatim; that pair is what most
  loops actually need.

## Memory

- **Short-term memory** is just what is in the window right now.
- **Long-term memory** is written to an external store and retrieved later
  ([[rag-retrieval]]) — often structured notes the agent maintains itself, so
  progress survives compaction and new sessions.

## Multi-agent and handoff

- **Manager/orchestrator**: one agent owns the goal and calls others as tools.
- **Decentralized handoff**: control transfers wholesale to a peer agent.
- Cost, honestly: an agent loop burns **several times** the tokens of a single
  chat call, and multi-agent roughly **an order of magnitude** more. It has to
  earn that ([[cost-latency]]).

## The hard part

**The loop is easy; knowing when to leave it is not.** Writing while-not-done
around a model call takes an afternoon — the remaining work is deciding what
"done" means, proving the agent got there, and containing what happens when it
did not. That means an explicit success signal rather than the model's own
say-so, budgets on all three axes, an unwind path to a human, and traces good
enough to answer "why did it take nineteen steps" after the fact
([[evals-observability]]). Autonomy also multiplies blast radius: each extra
turn is another chance to act on injected content from a tool result, so gate
consequential actions inside the loop, not only at its edge ([[guardrails]]).
Cost and step count are variable per run, so budget on **distributions, not
averages** — the p95 run, not the demo.


## Related

- [[tool-calling]], [[prompts]], [[cost-latency]], [[guardrails]],
  [[evals-observability]], [[rag-retrieval]], [[non-determinism]],
  [[antipatterns]]

Source: anthropic.com/engineering/building-effective-agents;
anthropic.com/engineering/effective-context-engineering-for-ai-agents;
openai.github.io/openai-agents-python/running_agents;
cdn.openai.com — a-practical-guide-to-building-agents.pdf
