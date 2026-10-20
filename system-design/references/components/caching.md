# Caching

Usually the highest-leverage move for read-heavy systems. Absorbs uneven load
and hot-key spikes in front of a database. Reads ≫ writes (100:1+), so caching
the hot set wins big.

## Where to cache
- **Client** (browser/OS)
- **CDN** (see `dns-cdn.md`)
- **Web server / reverse proxy** (Varnish) — even dynamic responses
- **Database** (default query/buffer cache; tune for your pattern)
- **Application** — in-memory KV (Redis, Memcached) between app and DB; RAM, so
  far faster than disk. Use an eviction policy (LRU) to keep hot data, evict
  cold. Redis adds persistence + data structures (sorted sets, lists).

Avoid file-based caching — it breaks cloning/auto-scaling.

## What to cache
- **Query level** — hash the query → store result. Simple but brittle: hard to
  invalidate; one cell change can require dropping many cached queries.
- **Object level** — cache assembled objects/structures (like app classes).
  Easier to invalidate (drop when underlying data changes); enables async
  rebuild by workers. Prefer this.
Good candidates: user sessions, fully-rendered pages, activity streams, user
graph data.

## Update strategies (the real decision)
- **Cache-aside (lazy loading)** — app checks cache; on miss, loads from DB and
  populates cache. Only requested data cached. Cost: 3 trips on a miss; data can
  go stale (use TTL); cold new nodes add latency. (Memcached's typical use.)
- **Write-through** — app writes to cache, cache writes synchronously to DB.
  Reads are fresh and fast. Cost: slower writes; most written data may never be
  read (mitigate with TTL); cold nodes miss until next write (pair with
  cache-aside).
- **Write-behind (write-back)** — app writes to cache; cache writes to DB
  **asynchronously**. Fast writes. Cost: data loss if cache dies before flush;
  more complex.
- **Refresh-ahead** — proactively refresh hot entries before they expire.
  Reduces latency *if* you predict accesses well; wasted work if you don't.

## The hard part
**Cache invalidation** — keeping cache consistent with the source of truth is
the difficult, bug-prone part. Always pair a strategy with a TTL, and decide up
front how stale is too stale.

## Related
- [[databases]], [[dns-cdn]], [[estimation]]

Source: system-design-primer — Cache.
