# WebMCP, a web page exposing its own tools

A browser API that lets a **website register tools an in-page agent can call**,
instead of the agent scraping the DOM, guessing at selectors, or reasoning over
screenshots. It is the page-side sibling of [[mcp]], not a replacement for it.

⚠️ **Status: W3C Draft Community Group Report (Web Machine Learning CG, editors
from Google and Microsoft), dated 2026-08-26. Not a W3C Standard and not on the
standards track.** Chrome ran a flag-gated DevTrial in 146 and an origin trial
from 149; Edge ships behind a flag. The surface is still renaming between drafts:
it was `navigator.modelContext` and is now `document.modelContext`. Feature-detect,
and check the draft before quoting a detail.

## The API

```javascript
await document.modelContext.registerTool({
  name: "add-todo",
  description: "Add a new item to the user's active todo list",
  inputSchema: { type: "object", properties: { text: { type: "string" } },
                 required: ["text"] },
  async execute({ text }) {
    await addTodoItemToCollection(text);
    return { content: [{ type: "text", text: `Added "${text}"` }] };
  }
});
```

- `registerTool(tool, options)`: `options` carries `exposedTo` (origins allowed
  to see the tool) and a `signal` that unregisters on abort.
- `getTools(options)`: visible tools, with `fromOrigins` to query across frames.
- `executeTool(tool, input, options)`: resolves to a stringified result.
- `ontoolchange`: the tool list is live, as in [[mcp]].
- Tool fields: `name`, `description`, optional `title` and `inputSchema`, async
  `execute`, and `annotations`: **`readOnlyHint`** and **`untrustedContentHint`**.
- Gated by a Permissions Policy feature named `tools`, default `['self']`;
  cross-origin frames need `allow="tools"`.

**The descriptor is the same object as any tool call** ([[tool-calling]]), so
schema design and "descriptions are prompt surface" transfer unchanged. What
changes is where the registry lives: in the page, tied to the live session.

## Why not something simpler

- **Plain MCP**: built for server-to-client and stdio/SSE process communication,
  with no native web concepts (origins, frames, permissions policy, live DOM).
- **A static manifest**: cannot express tools that depend on page state or on
  whether the user is signed in. Build-time artifact, runtime condition.
- **Events**: separate the schema from the implementation, so they drift.

**The economic argument**: a backend MCP server for your product means replicating
state and auth outside the app and carrying a second integration forever. A WebMCP
tool **reuses the session the user is already logged into**, in the page that
already holds the state.

**Non-goals, stated**: headless browsing, fully autonomous workflows without human
oversight, replacing MCP.

## Security, the whole topic

The browser guarantees almost nothing. Chrome's guidance is a defense-in-depth
strategy implemented by **agent developers**.

Two attack vectors, both indirect prompt injection ([[guardrails]]):
1. **Malicious manifests**: hidden instructions in tool names, parameters or
   descriptions, designed to hijack the agent. The site author writes a prompt
   into your model on every request.
2. **Contaminated outputs**: an honest site returning third-party data (user
   comments) that carries instructions.

Agent-side defences:
- **Token-limit every inbound tool response** and reject payloads over it.
- **Restrict the origins** the agent may touch to those relevant to the task.
- **Assume a tool mutates state unless `readOnlyHint` says otherwise**; confirm.
- **Spotlighting**: tell the model to treat content as data. Delimiting
  (`<untrusted>…`) when token-cheap matters; **base64** when robustness against
  structural evasion matters. Apply it to `untrustedContentHint` output.
- Classifiers over descriptions and outputs; a **critic** model checking that a
  call matches user intent and minimises PII.

Site-author side: `exposedTo` read tools only to origins you would hand the data
to directly, write tools only to origins you trust to act for the user. Chrome's
budgets, which also cap the context tax: **500 chars per tool description, 150 per
parameter description, 30 per name, 1.5K per tool output.**

## The hard part

**A client-side tool is not a security boundary.** `execute` runs in the page under
the user's own session; anything an agent can call, a console can call. The tool is
a **new front door onto endpoints that still need server-side authorization and
validation**. And trust fails in both directions at once: the agent cannot trust
the page's descriptions, and the page cannot trust an agent that may be driven by
someone else's prompt. Consent is unsettled. The draft adds
`requestUserInteraction()` for asking mid-execution, and nobody has decided who
owns the confirmation.

## Related

- [[mcp]], [[tool-calling]], [[guardrails]], [[agent-loop]], [[antipatterns]]

Source: webmachinelearning.github.io/webmcp (draft spec, 2026-08-26) and its
README explainer; developer.chrome.com/docs/agents/security and
/docs/ai/webmcp/secure-tools. **Verified 2026-08-29.**
