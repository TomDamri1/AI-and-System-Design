# Design Antipatterns

Common smells when reviewing a design, and what to ask instead.

- **No constraints** — design presented with no QPS / data size / read:write.
  → "What scale and read:write ratio are we designing for?"
- **Premature scaling** — sharding/microservices/multi-region before there's
  load to justify the complexity. → "What's the actual bottleneck today?"
- **Stateful app servers** — sessions/files on the box → can't scale out or
  auto-heal. → "Where does session/state live? Push it to a shared cache/DB."
- **Single point of failure** — one LB, one DB master, one region, no failover.
  → "What happens when this one node dies?"
- **Serial dependency chain** — many services in sequence, each <100% available,
  multiplying downtime. → "Can critical deps be parallel/redundant?"
- **Synchronous fan-out** — doing expensive/N-way work inline in the request.
  → "Can this be a queue + workers?"
- **Cache with no invalidation plan** — added a cache, no TTL or invalidation
  story. → "How does this go stale, and how stale is too stale?"
- **Hot shard / hot key** — sharding by a skewed key (power users, celebrities).
  → "Is load even across shards? Consistent hashing? Hot-key handling?"
- **Wrong consistency posture** — eventual consistency on money/inventory, or
  strong consistency forced on a feed that doesn't need it. → "Does this read
  truly need the latest write?"
- **NoSQL for relational data** — picking NoSQL then re-implementing joins in
  app code badly. → "Do the access patterns actually justify leaving SQL?"
- **Resume-driven architecture** — tech chosen for novelty, not constraints.
  → "What does this buy us that the simpler option doesn't?"

Anchor every critique in **a trade-off**: name the cost the design is paying and
whether it's worth it here.

## Related
- [[rubric]], [[dns-cdn]], [[load-balancing]], [[databases]], [[caching]], [[async]], [[communication]]

Source: synthesized from system-design-primer disadvantages sections.
