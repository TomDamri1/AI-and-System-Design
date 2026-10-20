# Design Workflow

The backbone for **coach mode**. A system design is an open-ended conversation —
you lead it. Walk these 5 steps; don't jump to components before requirements.

## Step 1 — Outline use cases, constraints, assumptions
Gather requirements and scope the problem before designing anything. Ask:
- Who uses it and how?
- How many users? What read:write ratio?
- What are the inputs and outputs?
- How much data? How many requests/sec?
- What must be fast vs what can be eventual?

State assumptions out loud. A design is only "good" relative to its constraints.

## Step 2 — Create a high-level design
Sketch the main components and how they connect. Justify each box. Keep it
coarse: client → DNS/CDN → load balancer → web/app tier → data tier (+ cache,
+ queue). Don't optimize yet.

## Step 3 — Design core components
Dive into the pieces that carry the load. For each: data model / schema, the
key API, and the algorithm. Example (URL shortener): hash generation (MD5 +
Base62), collision handling, SQL-vs-NoSQL choice, lookup path. Pull the relevant
`components/` leaf here.

## Step 4 — Scale the design
Now find and remove bottlenecks **given the constraints from Step 1**. Reach for:
- Load balancer + horizontal scaling (stateless servers)
- Caching (see `caching.md`) — usually the highest-leverage move for read-heavy
- Read replicas / federation / sharding (see `databases.md`)
- Async work via queues (see `async.md`)
- CDN for static/global content

Every addition is a trade-off — name what it costs (complexity, consistency,
$$), not just what it buys.

## Step 5 — Identify the bottleneck
End by naming the single biggest risk or limit: the hottest shard, the
synchronous fan-out, the cache-miss storm, the single point of failure. A good
answer makes this explicit and proposes a mitigation.

## Estimation checkpoint
Steps 1 and 4 usually need rough numbers (QPS, storage/yr, bandwidth, memory for
cache). Use `process/estimation.md` and `scripts/estimate.py`.

## Related
- [[estimation]], [[scalability]], [[rubric]]

Source: system-design-primer — "How to approach a system design interview question".
