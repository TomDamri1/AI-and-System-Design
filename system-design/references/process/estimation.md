# Back-of-the-Envelope Estimation

Rough sizing for capacity, storage, bandwidth, and memory. Goal: order-of-
magnitude correct, fast. See `scripts/estimate.py` for a calculator.

## Powers of two
| Power | Approx | Bytes |
|---|---|---|
| 10 | 1 thousand | 1 KB |
| 20 | 1 million | 1 MB |
| 30 | 1 billion | 1 GB |
| 40 | 1 trillion | 1 TB |
| 50 | 1 quadrillion | 1 PB |

## Latency numbers every programmer should know
```
L1 cache reference                   0.5 ns
Branch mispredict                    5   ns
L2 cache reference                   7   ns      14x L1
Mutex lock/unlock                    25  ns
Main memory reference                100 ns      20x L2, 200x L1
Compress 1 KB (Zippy)                10  µs
Send 1 KB over 1 Gbps                10  µs
Read 4 KB random from SSD            150 µs      ~1 GB/s SSD
Read 1 MB sequential from memory     250 µs
Round trip within same datacenter    500 µs
Read 1 MB sequential from SSD        1   ms      4x memory
HDD seek                             10  ms      20x datacenter RT
Read 1 MB sequential from 1 Gbps     10  ms      10x SSD
Read 1 MB sequential from HDD        30  ms      30x SSD
Packet CA→Netherlands→CA             150 ms
```

## Handy throughput rules
- Read sequentially: HDD ~30 MB/s, 1 Gbps net ~100 MB/s, SSD ~1 GB/s, RAM ~4 GB/s
- ~6–7 world-wide round trips/sec; ~2,000 round trips/sec within a datacenter
- Reads typically outnumber writes 100:1 to 1000:1 — design for read scaling

## Method
1. **QPS**: `daily_actions / 86,400`. Peak ≈ 2–10× average. Split read vs write.
2. **Storage/yr**: `writes_per_day × bytes_per_record × 365` (× replication
   factor). Add a retention horizon (e.g. 5 yr) for total disk.
3. **Bandwidth**: `QPS × payload_bytes`.
4. **Cache memory**: cache the hot set — often ~20% of items drive ~80% of
   reads. `hot_items × bytes_per_item`.

### Worked example — tweet-like service
- 100 M writes/day → ~1,150 writes/sec avg, ~10 K/sec peak
- 100:1 read:write → ~115 K reads/sec avg
- 300 bytes/tweet → ~30 GB/day → ~11 TB/yr (before replication)
- Conclusion: write path is fine on one tier; **read path needs cache + CDN +
  fan-out strategy** — that's where the design effort goes.

## Related
- [[design-workflow]] (steps 1 & 4), [[caching]]

Source: system-design-primer — Appendix (powers of two, latency numbers).
