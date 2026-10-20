# Worked Reference Designs

Each maps a classic problem to the steps in `process/design-workflow.md` and the
pattern it best teaches. Use as analogies when coaching.

## URL shortener / Pastebin (Bit.ly)
- **Teaches**: hashing + KV lookup, SQL-vs-NoSQL for simple high-read data.
- **Core**: generate short hash (MD5 → Base62), handle collisions, store
  hash→URL, redirect on lookup. Read-heavy → cache hot URLs.
- **Bottleneck**: read QPS on popular links → cache + CDN.

## Twitter timeline & search (Facebook feed)
- **Teaches**: fan-out on write vs read, async queues, the celebrity hot-key
  problem.
- **Core**: tweet write is cheap; building each follower's timeline is the cost.
  Fan-out-on-write (push to follower timelines via a queue) for most users;
  fan-out-on-read (pull) for celebrities with millions of followers.
- **Bottleneck**: fan-out for high-follower accounts → hybrid strategy.

## Web crawler
- **Teaches**: queues, dedup at scale, politeness/back pressure.
- **Core**: URL frontier queue, workers fetch + parse, dedup seen URLs (bloom
  filter / KV), store content. Rate-limit per domain.
- **Bottleneck**: dedup state size + avoiding re-crawl → KV store + TTL.

## Mint.com (personal finance aggregator)
- **Teaches**: async batch jobs, third-party integration, eventual consistency.
- **Core**: periodically pull bank transactions via queue+workers, categorize,
  aggregate. Users tolerate eventual freshness.
- **Bottleneck**: third-party rate limits → scheduled async pulls.

## Scaling to millions of users on AWS
- **Teaches**: the whole progression in order — vertical → horizontal + LB →
  read replicas → cache → CDN → federation/sharding → async.
- **Core**: this is `design-workflow.md` Step 4 made concrete; add each layer
  only when the prior bottleneck demands it.
- **Bottleneck**: shifts as you scale — always name the *current* one.

## Related
- [[design-workflow]], [[dns-cdn]], [[load-balancing]], [[databases]], [[caching]], [[async]], [[communication]]

Source: system-design-primer — solutions/system_design/* exercises.
