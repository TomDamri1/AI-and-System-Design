# Databases

## RDBMS
A relational store (SQL) with **ACID** transactions:
- **Atomicity** — all or nothing.
- **Consistency** — valid state → valid state.
- **Isolation** — concurrent == serial result.
- **Durability** — committed stays committed.

### Scaling an RDBMS (in rough order of reach)
1. **Master-slave replication** — master takes reads+writes, replicates to
   read-only slaves. Scales reads. Cost: promotion logic on master failure;
   replication lag.
2. **Master-master replication** — both nodes take writes. Survives a node loss.
   Cost: needs LB/app routing for writes; conflict resolution; often loosens
   ACID or adds write latency.
   - Replication risks (both): data loss if master dies pre-replication; read
     replicas bogged down replaying writes; lag grows with #slaves; more hw.
3. **Federation** (functional partitioning) — split DBs by function (users,
   products, forums). Less traffic/lag per DB, more fits in memory. Cost: app
   must route; cross-DB joins are hard; ineffective for huge single tables.
4. **Sharding** — split a table's rows across DBs (e.g. by user initial or
   geo). Less traffic, smaller indexes, parallel writes, fault isolation. Cost:
   app complexity; **uneven "hot" shards** (use consistent hashing to rebalance);
   cross-shard joins hard.
5. **Denormalization** — write redundant copies to avoid expensive joins; trades
   write perf for read perf (good when reads ≫ writes). Materialized views can
   automate it. Cost: duplicated data, harder to keep in sync, worse under heavy
   writes.
6. **SQL tuning** — benchmark + profile (slow query log), then: tighten schema
   (CHAR vs VARCHAR, right types, NOT NULL), add good indices (B-tree),
   avoid expensive joins, partition hot tables, tune the query cache.

## NoSQL
KV / document / wide-column / graph. Data is denormalized; joins done in app
code; most favor **BASE** (Basically Available, Soft state, Eventual
consistency) over ACID — availability over consistency.

- **Key-value** — hash table; O(1) read/write, often memory/SSD. Great for
  simple models, hot/rapidly-changing data, cache layers. Limited ops → logic
  moves to app. (Redis, Memcached, DynamoDB.)
- **Document** — KV where values are documents (JSON/XML); query by document
  fields; flexible schema. Good for occasionally-changing, semi-structured data.
  (MongoDB, CouchDB, DynamoDB, Elasticsearch.)
- **Wide-column** — nested map `ColumnFamily<RowKey, Columns<ColKey,Value,TS>>`.
  High availability + scalability for very large datasets. (Bigtable, HBase,
  Cassandra.)
- **Graph** — nodes + edges; optimized for many-to-many / complex relationships
  (social graphs). Newer, fewer tools. (Neo4j.)

## SQL or NoSQL — decision
**SQL when**: structured/relational data, strict schema, complex joins,
transactions, fast index lookups, mature tooling.
**NoSQL when**: semi-structured/flexible schema, non-relational, no complex
joins, TB–PB scale, very high write/IOPS throughput.
Well-suited to NoSQL: clickstream/logs, leaderboards, shopping carts (temp),
hot lookup tables, metadata.

Rule of thumb: start relational; reach for NoSQL when a specific access pattern
or scale makes the relational model the bottleneck.

## Related
- [[consistency-availability]], [[caching]]

Source: system-design-primer — Database (RDBMS, NoSQL, SQL-or-NoSQL).
