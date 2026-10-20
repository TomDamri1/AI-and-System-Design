---
name: system-design
description: >
  Guidance for designing scalable backend systems and reviewing system
  designs. Use when the user is architecting a service, sizing capacity,
  choosing between databases / caches / queues / load balancers, weighing
  consistency vs availability, reasoning about CAP / sharding / replication,
  doing back-of-the-envelope estimates, or reviewing/critiquing an existing
  design, RFC, or architecture. Trigger on phrases like "design a system",
  "how should we scale", "which database", "is this design sound", "review
  this architecture", "estimate the load".
---

# System Design

This skill helps developers **design good systems** and **review designs**.
It is a router: read only the leaf file(s) relevant to the task — do not load
everything. The knowledge is condensed from the System Design Primer
(donnemartin/system-design-primer).

**Core principle: everything is a trade-off.** Never present a component as
"the right answer." State what it buys, what it costs, and when it stops being
worth it.

## Three modes — detect which one the request is

1. **Coach** — user is designing something new ("design X", "how would you
   build Y"). Drive the workflow in `references/process/design-workflow.md`,
   pulling component leaves as the design takes shape.
2. **Lookup** — user asks a focused question ("when do I shard?", "cache-aside
   vs write-through?"). Jump straight to the matching leaf below; skip the
   workflow.
3. **Review** — user has an existing design / PR / RFC and wants critique. Use
   `references/review/rubric.md` + `references/review/antipatterns.md`, then
   pull component leaves for the parts under scrutiny.

## Routing table — read the leaf, then answer

### Process (coach mode backbone)
- `references/process/design-workflow.md` — the 5-step method: requirements →
  high-level design → core components → scale → bottlenecks. Start here for any
  "design X" request.
- `references/process/estimation.md` — back-of-the-envelope: powers of two,
  latency numbers, throughput rules, worked QPS/storage math. Use when sizing
  capacity. A helper script lives at `scripts/estimate.py`.

### Foundations (trade-off vocabulary)
- `references/foundations/scalability.md` — performance vs scalability, latency
  vs throughput, vertical vs horizontal scaling.
- `references/foundations/consistency-availability.md` — CAP theorem, CP vs AP,
  consistency patterns (weak/eventual/strong), availability patterns (failover,
  replication), availability-in-numbers math.

### Components (the building blocks)
- `references/components/dns-cdn.md` — DNS routing, push vs pull CDNs.
- `references/components/load-balancing.md` — load balancers (L4/L7, active-
  passive/active-active), reverse proxy, horizontal scaling, statelessness.
- `references/components/databases.md` — RDBMS scaling (replication, federation,
  sharding, denormalization, SQL tuning), NoSQL types (KV/doc/wide-column/
  graph), and SQL-vs-NoSQL decision.
- `references/components/caching.md` — cache layers and update strategies
  (cache-aside, write-through, write-behind, refresh-ahead).
- `references/components/async.md` — message queues, task queues, back pressure.
- `references/components/communication.md` — HTTP, TCP vs UDP, RPC vs REST.

### Review
- `references/review/rubric.md` — checklist to score a design against.
- `references/review/antipatterns.md` — common smells and what to ask instead.

### Examples
- `references/examples/examples.md` — worked reference designs (URL shortener,
  Twitter feed, web crawler, scaling on AWS) and the patterns each one teaches.

## How to answer
- Cite the leaf you used so the user can go deeper.
- Lead with the decision and the trade-off, not a feature dump.
- For coach/review, end by naming the **bottleneck or biggest risk** — that's
  the thing that makes a design good or bad.
