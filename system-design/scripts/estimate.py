#!/usr/bin/env python3
"""Back-of-the-envelope estimator for system design.

Quick capacity math: QPS, storage/year, bandwidth, and cache memory for the hot
set. Numbers are order-of-magnitude, matching references/process/estimation.md.

Usage:
    python3 estimate.py --daily-writes 100_000_000 \
        --read-write-ratio 100 --bytes-per-record 300 \
        --peak-factor 10 --replication 3 --retention-years 5 \
        --hot-fraction 0.2
"""
import argparse


def human_count(n: float) -> str:
    for unit, size in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= size:
            return f"{n / size:.2f}{unit}"
    return f"{n:.0f}"


def human_bytes(n: float) -> str:
    for unit, size in (("PB", 2**50), ("TB", 2**40), ("GB", 2**30),
                       ("MB", 2**20), ("KB", 2**10)):
        if abs(n) >= size:
            return f"{n / size:.2f} {unit}"
    return f"{n:.0f} B"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--daily-writes", type=float, required=True,
                   help="write actions per day")
    p.add_argument("--read-write-ratio", type=float, default=100.0,
                   help="reads per write (default 100)")
    p.add_argument("--bytes-per-record", type=float, default=300.0,
                   help="payload size per write")
    p.add_argument("--peak-factor", type=float, default=10.0,
                   help="peak QPS / average QPS (default 10)")
    p.add_argument("--replication", type=float, default=3.0,
                   help="storage replication factor (default 3)")
    p.add_argument("--retention-years", type=float, default=5.0)
    p.add_argument("--hot-fraction", type=float, default=0.2,
                   help="fraction of a day's data kept hot in cache")
    a = p.parse_args()

    SECONDS_PER_DAY = 86_400
    write_qps = a.daily_writes / SECONDS_PER_DAY
    read_qps = write_qps * a.read_write_ratio
    daily_bytes = a.daily_writes * a.bytes_per_record
    yearly_bytes = daily_bytes * 365
    total_bytes = yearly_bytes * a.retention_years * a.replication
    write_bw = write_qps * a.bytes_per_record
    read_bw = read_qps * a.bytes_per_record
    cache_bytes = daily_bytes * a.hot_fraction

    print("=== Back-of-the-envelope estimate ===")
    print(f"Write QPS    avg {human_count(write_qps)}/s   "
          f"peak {human_count(write_qps * a.peak_factor)}/s")
    print(f"Read  QPS    avg {human_count(read_qps)}/s   "
          f"peak {human_count(read_qps * a.peak_factor)}/s")
    print(f"New data     {human_bytes(daily_bytes)}/day   "
          f"{human_bytes(yearly_bytes)}/yr (raw)")
    print(f"Total disk   {human_bytes(total_bytes)}  "
          f"({a.retention_years:g} yr x {a.replication:g}x replication)")
    print(f"Bandwidth    write {human_bytes(write_bw)}/s   "
          f"read {human_bytes(read_bw)}/s")
    print(f"Cache (hot)  {human_bytes(cache_bytes)}  "
          f"({a.hot_fraction:g} of one day's data)")


if __name__ == "__main__":
    main()
