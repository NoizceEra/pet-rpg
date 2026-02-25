#!/usr/bin/env python3
"""Latency audit utility for unified_scanner log output."""
import argparse
import re
from collections import deque, defaultdict
from datetime import datetime
from pathlib import Path

DETECTION_PATTERNS = [
    (re.compile(r"ARB FOUND!"), "pbot1"),
    (re.compile(r"FastLoop Executing"), "fastloop"),
]
TRADE_PATTERN = re.compile(r"TRADE EXECUTED \((?P<strategy>[a-zA-Z0-9_]+) (?P<action>[A-Z]+)\)")

def parse_timestamp(line):
    try:
        timestamp_str = line.split(" [", 1)[0]
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
    except Exception:
        return None

def audit(log_path, expiry_seconds=60):
    pending = {strategy: deque() for _, strategy in DETECTION_PATTERNS}
    stats = defaultdict(list)
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            ts = parse_timestamp(line)
            if ts is None:
                continue
            for strategy in pending:
                while pending[strategy] and (ts - pending[strategy][0][0]).total_seconds() > expiry_seconds:
                    pending[strategy].popleft()
            matched_detection = False
            for pattern, strategy in DETECTION_PATTERNS:
                if pattern.search(line):
                    pending.setdefault(strategy, deque()).append((ts, line.strip()))
                    matched_detection = True
                    break
            if matched_detection:
                continue
            match = TRADE_PATTERN.search(line)
            if match:
                strategy = match.group("strategy")
                if pending.get(strategy):
                    det_ts, det_line = pending[strategy].popleft()
                    delta = (ts - det_ts).total_seconds() * 1000
                    stats[strategy].append((delta, det_line))
    return stats

def summarize(stats):
    summary_lines = []
    for strategy, samples in stats.items():
        if not samples:
            continue
        latencies = [delta for delta, _ in samples]
        avg = sum(latencies) / len(latencies)
        summary_lines.append(
            {
                "strategy": strategy,
                "samples": len(latencies),
                "avg_ms": round(avg, 2),
                "p95_ms": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 2) if len(latencies) > 1 else round(latencies[0], 2),
                "max_ms": round(max(latencies), 2),
            }
        )
    return summary_lines

def main():
    parser = argparse.ArgumentParser(description="Latency audit for unified_scanner log")
    parser.add_argument("--log", default="unified_scanner.log", help="Path to log file")
    args = parser.parse_args()
    log_path = Path(args.log)
    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")
    stats = audit(log_path)
    summary = summarize(stats)
    if not summary:
        print("No latency samples detected.")
        return
    print("Latency Audit Summary (signal -> trade execution):")
    for record in summary:
        print(
            f"- {record['strategy']}: samples={record['samples']} | avg={record['avg_ms']} ms | "
            f"p95={record['p95_ms']} ms | max={record['max_ms']} ms"
        )

if __name__ == "__main__":
    main()
