"""Send randomized requests to the Heart Disease API and print a summary.

Usage::

    # Default: 100 requests to http://127.0.0.1:8000
    python scripts/load_test.py

    # Custom count + URL + seed
    python scripts/load_test.py --n 500 --url http://127.0.0.1:8000 --seed 42

Useful for:
    * Smoke-testing the FastAPI service end-to-end.
    * Populating /metrics so Prometheus / Grafana panels light up.
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
from typing import Dict, List

import requests


def random_patient(rng: random.Random) -> Dict[str, float]:
    """Generate a clinically plausible (not necessarily realistic) patient."""
    return {
        "age": rng.randint(29, 77),
        "sex": rng.randint(0, 1),
        "cp": rng.randint(0, 3),
        "trestbps": rng.randint(94, 200),
        "chol": rng.randint(126, 564),
        "fbs": rng.randint(0, 1),
        "restecg": rng.randint(0, 2),
        "thalach": rng.randint(71, 202),
        "exang": rng.randint(0, 1),
        "oldpeak": round(rng.uniform(0.0, 6.2), 1),
        "slope": rng.randint(0, 2),
        "ca": rng.randint(0, 3),
        "thal": rng.choice([3.0, 6.0, 7.0]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000",
                        help="API base URL (default: %(default)s)")
    parser.add_argument("--n", type=int, default=100,
                        help="Number of requests (default: %(default)s)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="Per-request timeout in seconds (default: %(default)s)")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    endpoint = f"{args.url.rstrip('/')}/predict"

    counts = {0: 0, 1: 0}
    confidences: List[float] = []
    latencies_ms: List[float] = []
    errors = 0

    print(f"Sending {args.n} requests to {endpoint} ...")
    t0 = time.perf_counter()

    for i in range(1, args.n + 1):
        payload = random_patient(rng)
        try:
            t_start = time.perf_counter()
            resp = requests.post(endpoint, json=payload, timeout=args.timeout)
            latencies_ms.append((time.perf_counter() - t_start) * 1000)
            resp.raise_for_status()
            data = resp.json()
            counts[int(data["prediction"])] += 1
            confidences.append(float(data["confidence"]))
        except Exception as exc:  # noqa: BLE001
            errors += 1
            if errors <= 5:
                print(f"  [{i}] ERROR: {exc}")

        if i % max(1, args.n // 10) == 0:
            print(f"  ... {i}/{args.n} done")

    elapsed = time.perf_counter() - t0
    ok = args.n - errors

    print("\n=== Summary ===")
    print(f"Total requests   : {args.n}")
    print(f"Successful       : {ok}")
    print(f"Errors           : {errors}")
    print(f"Elapsed (s)      : {elapsed:.2f}")
    if ok:
        print(f"Throughput (rps) : {ok / elapsed:.1f}")
        print(f"no_disease (0)   : {counts[0]}  ({100 * counts[0] / ok:.1f}%)")
        print(f"disease    (1)   : {counts[1]}  ({100 * counts[1] / ok:.1f}%)")
        print(f"Confidence mean  : {statistics.mean(confidences):.3f}")
        print(f"Confidence stdev : {statistics.pstdev(confidences):.3f}")
        if latencies_ms:
            sorted_lat = sorted(latencies_ms)
            p50 = sorted_lat[len(sorted_lat) // 2]
            p95 = sorted_lat[int(len(sorted_lat) * 0.95) - 1]
            print(f"Latency p50 (ms) : {p50:.1f}")
            print(f"Latency p95 (ms) : {p95:.1f}")
            print(f"Latency max (ms) : {max(latencies_ms):.1f}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
