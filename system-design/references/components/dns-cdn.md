# DNS & CDN

## DNS
Translates a domain (www.example.com) to an IP. Hierarchical; results cached at
many levels with a TTL (stale until TTL expires). Records: **A** (name→IP),
**CNAME** (name→name), **NS** (name servers), **MX** (mail). Managed services
(Route 53, Cloudflare) can route by **weighted round robin**, **latency**, or
**geolocation** — useful for A/B tests, draining servers, multi-region.
- Cost: extra lookup latency (mitigated by caching); management complexity;
  DNS is a DDoS target.

## CDN
Globally distributed proxy servers serving content from near the user. Usually
static assets (HTML/CSS/JS, images, video); some (CloudFront) do dynamic too.
Wins: users get content from a nearby PoP, and your origin sheds load.

### Push vs pull
- **Push CDN** — you upload content to the CDN on change. Good for **low-traffic
  or rarely-changing** content. Minimizes traffic, maximizes your storage
  responsibility.
- **Pull CDN** — CDN fetches from your origin on first request, caches per TTL.
  Good for **heavy traffic**; first request is slower; can serve stale within
  TTL; minimal storage on your side.

Cost: $$ at high traffic; stale content within TTL; must rewrite static URLs to
point at the CDN.

## Related
- [[caching]] (CDNs are a cache layer), [[load-balancing]]

Source: system-design-primer — DNS, Content delivery network.
