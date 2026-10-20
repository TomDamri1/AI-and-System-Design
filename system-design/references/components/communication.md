# Communication

## HTTP
Request/response protocol for encoding + transporting data. Self-contained, so
it flows through proxies/LBs/caches. Request = verb + resource.

| Verb | Use | Idempotent | Safe | Cacheable |
|---|---|---|---|---|
| GET | read | yes | yes | yes |
| POST | create / process | no | no | if fresh |
| PUT | create/replace | yes | no | no |
| PATCH | partial update | no | no | if fresh |
| DELETE | delete | yes | no | no |

Runs over TCP or UDP.

## TCP vs UDP
- **TCP** — connection-oriented (handshake). Guarantees in-order, uncorrupted
  delivery via sequence numbers, checksums, ACKs + retransmission; adds flow &
  congestion control. Slower, more overhead. Keeping many connections open costs
  memory — use **connection pooling**. Use when **all data must arrive intact**
  and timing is secondary: web, DB, SMTP, FTP, SSH.
- **UDP** — connectionless datagrams; may arrive out of order or not at all; no
  congestion control; more efficient. Can broadcast (e.g. DHCP). Use when you
  need **lowest latency** and late data is worse than lost data: VoIP, video
  chat, streaming, realtime games.

## RPC vs REST
- **RPC** — call a procedure on a remote server as if local; client stub
  marshals args. Exposes **behaviors**. Common for **internal** service-to-
  service (Protobuf/gRPC, Thrift, Avro) where you hand-craft calls for perf.
  Cost: client tightly coupled to implementation; new API per operation; harder
  to debug/cache.
- **REST** — stateless client/server over resources (URIs); verbs + status
  codes; cacheable. Exposes **data**. Best for **public** APIs; great for
  horizontal scaling. Cost: awkward for non-hierarchical actions; fixed verb set;
  nested resources → multiple round trips; payload bloat over time.

Rule of thumb: **REST for public/edge APIs, RPC (gRPC) for internal hot paths.**

## Related
- [[async]], [[load-balancing]]

Source: system-design-primer — Communication (HTTP, TCP/UDP, RPC, REST).
