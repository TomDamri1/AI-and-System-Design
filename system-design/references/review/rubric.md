# Design Review Rubric

Score an existing design / RFC / architecture against these. For each, state
**what's good**, **what's missing**, and **the one change with highest leverage**.

## 1. Requirements & constraints
- Are use cases, scale (users, QPS, read:write), and data volume stated?
- Is it clear what must be strongly consistent vs eventually consistent?
- Are non-functional needs (latency target, availability SLA) explicit?
A design with no constraints can't be judged — flag this first.

## 2. High-level soundness
- Do the components match the load shape (read-heavy? write-heavy? spiky?)?
- Is the data tier appropriate (SQL vs NoSQL) for the access patterns?
- Is state kept out of app servers (stateless, horizontally scalable)?

## 3. Scalability
- Where does it break at 10×? 100×? Is there a sharding/partitioning story?
- Is caching used where reads dominate? Right strategy + invalidation plan?
- Is expensive/fan-out work async (queue) rather than inline?

## 4. Availability & failure
- Single points of failure? (one LB, one master, one region)
- Redundancy in **parallel**, not a long serial dependency chain?
- What happens on partition? On a node death? Is data-loss window acceptable?

## 5. Consistency
- Does the chosen CP/AP posture match the business need?
- Replication lag / stale reads understood and acceptable?

## 6. Operability & cost
- Can it be deployed, observed, and rolled back?
- Is the complexity justified by the constraints, or premature?

## Output format
1. **Verdict** — sound / sound-with-gaps / not-yet.
2. **Top risk / bottleneck** — the single thing most likely to fail or limit it.
3. **Prioritized fixes** — highest leverage first.

## Related
- [[antipatterns]], [[design-workflow]]

Source: synthesized from system-design-primer principles.
