# Consistency & Availability

## CAP theorem
In a distributed system you can guarantee only **two** of:
- **Consistency** — every read gets the most recent write (or an error).
- **Availability** — every request gets a response (maybe stale).
- **Partition tolerance** — keeps working despite network partitions.

Networks fail, so **partition tolerance is mandatory**. The real choice is
**CP vs AP**:
- **CP** — consistency + partition tolerance. A partitioned node may time out.
  Choose when you need atomic reads/writes (banking, inventory, anything where a
  stale read is wrong).
- **AP** — availability + partition tolerance. Returns the most available
  (possibly stale) data; writes propagate once the partition heals. Choose when
  the system must keep serving and eventual consistency is acceptable (feeds,
  social, metrics).

## Consistency patterns
- **Weak** — after a write, reads may or may not see it (best effort).
  e.g. memcached, VoIP, live video, realtime games.
- **Eventual** — reads see the write eventually (usually ms); async replication.
  e.g. DNS, email. Works well in highly available systems.
- **Strong** — reads see the write immediately; synchronous replication.
  e.g. filesystems, RDBMS transactions.

## Availability patterns
Two complementary tools: **failover** and **replication**.

### Failover
- **Active-passive** — heartbeat between active and standby; standby takes over
  the active's IP on failure. Downtime depends on hot vs cold standby. (a.k.a.
  master-slave failover.)
- **Active-active** — both serve traffic, sharing load. (a.k.a. master-master.)
- Cost: more hardware + complexity; risk of data loss if the active dies before
  replicating.

### Replication
Master-slave and master-master — see `components/databases.md`.

## Availability in numbers (the "nines")
- 99.9% (three 9s) ≈ 8h 46m downtime/year.
- 99.99% (four 9s) ≈ 52m downtime/year.
- **In sequence**: `A_total = A1 × A2` (two 99.9% deps → 99.8% — worse).
- **In parallel**: `A_total = 1 − (1−A1)(1−A2)` (two 99.9% → 99.9999% — better).
Put critical dependencies in parallel/redundant, not in a long serial chain.

## Related
- [[databases]], [[caching]], [[scalability]]

Source: system-design-primer — CAP, consistency/availability patterns.
