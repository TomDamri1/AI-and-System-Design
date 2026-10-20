# Load Balancing & Reverse Proxy

## Load balancer
Distributes client requests across servers/databases. Buys: no traffic to
unhealthy servers, no overload, removes a single point of failure. Hardware
(expensive) or software (HAProxy, NGINX). Extras: **SSL termination** (offload
crypto from backends), **session persistence** (sticky sessions via cookies).

Run **multiple** LBs (active-passive or active-active) — a single LB is itself a
single point of failure.

### Routing methods
Random, least-loaded, session/cookie, round robin / weighted round robin, or by
layer:
- **Layer 4** — routes on transport info (source/dest IP + port), forwards
  packets with NAT, doesn't inspect contents. Less CPU, less flexible.
- **Layer 7** — routes on application data (headers, URL, cookies). Can send
  video traffic to video servers, billing to hardened servers. More flexible,
  slightly more cost (minimal on modern hardware).

### Cost
LB can become a bottleneck if under-provisioned; adds complexity; needs
redundancy to avoid being a SPOF.

## Horizontal scaling (enabled by the LB)
Scale out with commodity machines instead of one big box: cheaper, higher
availability. **Requirement: stateless servers** — no local sessions or
profile pics on the app box; store session state in a shared DB or persistent
cache (Redis/Memcached). Downstream caches/DBs must handle more concurrent
connections as you add app servers.

## Reverse proxy (web server)
Single public-facing entry that forwards to internal services. Useful even with
**one** backend. Buys: hide/secure backends, IP blacklisting, connection limits,
SSL termination, compression, caching, serving static content directly.

### Load balancer vs reverse proxy
- LB makes sense with **multiple** servers doing the same job.
- Reverse proxy helps even with **one** server (security, caching, TLS).
- NGINX/HAProxy do both.

## Related
- [[scalability]], [[caching]], [[dns-cdn]]

Source: system-design-primer — Load balancer, Reverse proxy, Horizontal scaling.
