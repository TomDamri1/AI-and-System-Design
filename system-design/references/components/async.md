# Asynchronism

Move expensive work out of the request path. Also lets you precompute (periodic
aggregation). Trade-off: adds delay + complexity, so don't queue cheap or
realtime-critical work.

## Message queues
Receive, hold, deliver messages. Flow: app publishes a job and tells the user
"in progress"; a worker picks it up, processes, signals done. User isn't
blocked. (Classic: post a tweet — show it instantly, fan out to followers in the
background.)
- **Redis** — simple broker, but messages can be lost.
- **RabbitMQ** — popular, AMQP, you manage nodes.
- **Amazon SQS** — hosted; higher latency; at-least-once (can deliver twice →
  make consumers idempotent).

## Task queues
Receive tasks + data, run them, deliver results. Support scheduling and
CPU-heavy background jobs. (Celery — scheduling, Python.)

## Back pressure
If the queue grows past memory, you get cache misses, disk reads, slowdowns.
Back pressure **caps queue size** to hold throughput steady: when full, return
**HTTP 503 / "server busy"** and have clients retry with **exponential backoff**.

## When NOT to go async
Inexpensive calculations and realtime workflows are often better synchronous —
queues add latency and moving parts.

## Related
- [[communication]], [[scalability]]

Source: system-design-primer — Asynchronism.
