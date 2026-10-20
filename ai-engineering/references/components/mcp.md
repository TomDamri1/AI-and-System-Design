# MCP — the Model Context Protocol

An open protocol for connecting AI applications to the systems that hold their
context. It standardises the plumbing around [[tool-calling]] rather than
replacing it, and its real costs are context budget and security, not wiring.

## The problem it solves

- Without a standard, every agent needs bespoke glue for every system: an
  **N×M integration problem**, M systems rewritten for each of N agents.
- MCP makes it **N+M**. A server exposes a system *once*; any compliant client
  can consume it. Servers are reusable across agents, teams and vendors.
- One line of analogy: a **common port and driver interface** instead of a
  custom cable for every device pair.
- It is a spec with multiple independent implementers and SDKs, not one
  vendor's feature.

## Architecture

- A **host** — the AI application — contains one or more **clients**. Each
  client holds a dedicated connection to one **MCP server** fronting some
  system (filesystem, database, issue tracker, error monitor).
- Servers are usually **small and single-purpose**. Hosts compose several.
- The wire format is **JSON-RPC 2.0**: requests, responses, notifications.
  Primitives are discovered by `*/list` and invoked by `*/call` or `*/get`, so
  listings are dynamic and can change mid-session.
- Two layers: a **data layer** (JSON-RPC, capabilities, primitives) inside a
  **transport layer** (channels, framing, authorization).

**As of spec revision `2026-07-28` the core is stateless.** The
`initialize`/`initialized` handshake and the `Mcp-Session-Id` header are gone;
every request carries its own protocol version, client identity and client
capabilities in `_meta`. A session id is server affinity, so removing it is what
lets a remote server run behind a **plain round-robin load balancer** with no
shared state. `server/discover` (mandatory on servers, optional for clients to
call) returns identity, capabilities and supported versions, and is cacheable via
`ttlMs` / `cacheScope`. Tool, prompt and resource lists are cacheable the same way.
Change notifications are **opt-in and best effort**: the client opens
`subscriptions/listen` naming the types it wants, and still polls for freshness.

## What a server exposes: the primitives

People conflate these three; the distinction is the whole design.

- **Tools** — executable actions with a name, description and JSON input
  schema. These surface to the model and become ordinary tool calls: see
  [[tool-calling]] for the round trip and schema design, which apply unchanged.
- **Resources** — data sources (file contents, records, API responses) the
  **host** reads and decides to place in context.
- **Prompts** — reusable templates and workflows, typically surfaced for the
  **user** to select.

**Tools are chosen by the model; resources are chosen by the application.**
Get this backwards and you build either an agent that cannot reach its data
(everything buried in resources nothing selects) or one that thrashes calling
tools to fetch context the host could have supplied directly.

Clients expose one primitive back: **elicitation** (`elicitation/create`), letting
a server ask the user for input or confirmation mid-call. It is delivered through
**Multi Round-Trip Requests**: the tool returns `resultType: "input_required"` and
the client retries with `inputResponses`, so no server-initiated stream is needed.

**Deprecated as of `2026-07-28`**, with at least a twelve-month support window:
**sampling** (the server borrowing the client's model), **logging**, and **roots**.
New implementations integrate with the LLM provider directly and log to `stderr`
or OpenTelemetry. Naming sampling as current dates you to 2025.

## Transports

- **stdio** — the server runs as a local subprocess on the user's machine.
  Trivial to launch, no network, inherits the user's trust and privileges.
- **Streamable HTTP**: HTTP POST for client-to-server messages, optional SSE for
  streaming. Remote servers, typically many clients per server. This is what
  enterprise deployments use, and it needs real authorization. Requests also carry
  `Mcp-Method` and `Mcp-Name` headers so gateways and WAFs can route and meter
  without parsing JSON bodies.
- The legacy **HTTP+SSE** transport is formally deprecated with a one-year
  transition. There are two live transports, not three.

## Authorization for remote servers

Optional overall, but HTTP transports SHOULD conform. **stdio servers SHOULD NOT**
follow it and take credentials from the environment instead.

- The MCP server is an **OAuth 2.1 resource server**; the authorization server is a
  separate concern and may be a third party.
- **Discovery runs backwards from a 401.** The server MUST implement Protected
  Resource Metadata (RFC 9728) and answer unauthenticated calls with a
  `WWW-Authenticate: Bearer resource_metadata="…", scope="…"` challenge. The client
  reads that, finds the authorization server, then runs a normal PKCE flow.
- **RFC 8707 resource indicators are MUST**: the `resource` parameter names the
  canonical URI of the target server in both the authorization and token request,
  sent whether or not the AS supports it.
- **RFC 9207 issuer validation**: record the expected issuer before redirecting,
  compare the returned `iss` by exact string match before redeeming the code.
- **Client ID Metadata Documents** are the preferred registration path (an HTTPS
  URL as `client_id`). **Dynamic Client Registration is deprecated.**
- Runtime permission gaps return `403` with `error="insufficient_scope"`; the
  client re-authorizes with the **union** of old and challenged scopes or silently
  loses permissions it had.
- ⭐ **Tokens are audience-bound.** Servers MUST validate that a token was issued
  for them, and MUST NOT accept or transit any other token; clients MUST NOT send
  tokens from another server's authorization server. **Token passthrough is the
  confused deputy, forbidden at spec level.**
- **Credentials belong to the server, not the prompt.** Never pass secrets as
  tool arguments where they land in context and transcripts. Tenant isolation
  and per-user scoping in [[enterprise-multitenancy]].

## Security

An MCP server is a **third-party dependency that can write directly into your
model's context**. Treat it with dependency-level suspicion.

- **Tool descriptions are prompt surface**, therefore a poisoning vector: a
  malicious description can carry instructions the model reads every request.
- **Tool results are untrusted input**, same as any fetched page.
- A compromised or malicious server can attempt to **redirect the agent** —
  exfiltrate context, chain into another server's write tools.
- Many connected servers grant broad **ambient authority**: the
  excessive-agency risk, where the union of capabilities exceeds any intent.
- Defences: install only servers you trust or have reviewed; **pin versions**;
  least privilege per server; **human approval for consequential tools**; and
  treat every server boundary as untrusted. Depth in [[guardrails]].

## Cost and context reality

- Every connected server's tool definitions are **resent on every single
  call**, called or not. A handful of servers can outweigh the conversation and
  degrade selection (context rot in [[llm-basics]]).
- Piping raw results through the model is expensive twice over: a document
  retrieved and then written elsewhere crosses context twice.
- A documented mitigation is **letting the agent write code that calls the
  servers**, loading definitions on demand and filtering results before they
  reach context — reported as **~150k tokens down to ~2k** on a data-heavy
  task. See [[cost-latency]].

## When not to use it

For **one** integration you own end to end, a plain function is simpler,
faster and easier to debug. MCP earns its keep with **many** integrations,
**reuse** across agents or teams, or **third-party and customer-supplied**
connectors. Do not add a protocol to solve a single function call.

The ecosystem is young and moving: primitives get added, deprecated and
renamed between spec revisions. **Verify against the current spec** rather
than a remembered detail.

## The hard part

**MCP makes it trivially easy to expand what an agent can reach, which is
exactly what makes it dangerous.** Each server you add widens two things at
once: the context budget consumed on every request, and the blast radius of a
single successful injection. Neither cost is visible at the moment you add it —
the connection succeeds, the tools appear, nothing breaks — and both show up
later as degraded tool selection, a bill you cannot explain, or an agent that
did something no one asked for. Curate connected servers like production
dependencies: reviewed, pinned, scoped, and removed when unused. Not like
browser extensions. Then measure it — tool-selection accuracy and tokens per
task per server belong in [[evals-observability]].

## Related

- [[tool-calling]], [[agent-loop]], [[guardrails]], [[cost-latency]],
  [[llm-basics]], [[enterprise-multitenancy]], [[evals-observability]],
  [[antipatterns]]

Related: **WebMCP** puts the same tool descriptor inside a web page instead of a
connected server. Different registry, different threat model. See [[webmcp]].

Source: modelcontextprotocol.io, learn/architecture and specification
`2026-07-28` (statelessness, discovery, primitives, transports, authorization);
blog.modelcontextprotocol.io/posts/2026-07-28 (what changed);
anthropic.com/engineering/code-execution-with-mcp.
**Verified 2026-08-29 against spec revision `2026-07-28`.** The ecosystem renames
and deprecates between revisions: re-check the revision before quoting a detail.
