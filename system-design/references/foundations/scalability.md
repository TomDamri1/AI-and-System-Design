# Scalability Foundations

The trade-off vocabulary every design conversation uses.

## Performance vs scalability
- **Performance problem**: slow for a *single* user.
- **Scalability problem**: fast for one user, slow under *load*.
A service is scalable if adding resources increases performance proportionally
(more units of work, or larger units of work as data grows).

## Latency vs throughput
- **Latency** — time to perform one action.
- **Throughput** — actions per unit time.
Aim for **maximal throughput with acceptable latency**. They trade off:
batching/queueing raise throughput but add latency.

## Vertical vs horizontal scaling
- **Vertical (scale up)** — bigger machine. Simple, but expensive, hits a
  ceiling, and the box is a single point of failure.
- **Horizontal (scale out)** — more commodity machines behind a load balancer.
  Cheaper, higher availability, easier to hire for — but introduces complexity
  and **requires stateless servers** (no local sessions/files; push state to a
  shared DB or cache like Redis/Memcached).

Default to horizontal for the web/app tier once you outgrow one box; keep state
out of the app servers.

## The meta-rule
**Everything is a trade-off.** Each component below buys something (throughput,
availability, latency) at a cost (complexity, consistency, money). Good design
is choosing which costs are acceptable for *these* constraints.

## Related
- [[consistency-availability]], [[load-balancing]]

Source: system-design-primer — Performance vs scalability, Latency vs throughput.
