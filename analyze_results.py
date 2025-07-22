import json
import statistics
from collections import defaultdict


def parse_version(version_str):
    # Split version string into numeric components for proper sorting
    # e.g., "1.25.13" -> (1, 25, 13)
    try:
        return tuple(int(x) for x in version_str.split("."))
    except ValueError:
        # Fallback for malformed versions
        return (0, 0, 0)


def make_ascii_bar(value, min_val, max_val, width=20):
    if max_val == min_val:
        normalized = 0
    else:
        normalized = (value - min_val) / (max_val - min_val)
    bar_length = int(normalized * width)
    bar = "█" * bar_length + "░" * (width - bar_length)
    return bar


def main():
    data = []
    with open("log.jsonl", "r") as f:
        for line in f:
            data.append(json.loads(line.strip()))

    # Filter out warmup iterations
    filtered_data = [entry for entry in data if not entry["hyperfine_iteration"].startswith("warmup")]

    # Group by all factors except hyperfine_iteration
    groups = defaultdict(list)
    for entry in filtered_data:
        key = (
            tuple(entry["python_version"]),
            entry["boto3_version"],
            entry["botocore_version"],
            entry["awscrt_version"],
        )
        groups[key].append(entry["sign_time_ms"])

    # Calculate statistics for each group
    results = []
    for key, times in groups.items():
        python_ver, boto3_ver, botocore_ver, awscrt_ver = key

        stats = {
            "python_version": python_ver,
            "boto3_version": boto3_ver,
            "botocore_version": botocore_ver,
            "awscrt_version": awscrt_ver,
            "count": len(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "min_ms": min(times),
            "max_ms": max(times),
        }
        results.append(stats)

    results.sort(key=lambda x: parse_version(x["botocore_version"]))

    min_time = 0  # min(r["mean_ms"] for r in results)
    max_time = max(r["mean_ms"] for r in results)

    print("## Performance Analysis (grouped by library versions)")
    print()
    print(
        "| boto3 | botocore | awscrt | count | mean (ms) | median (ms) | std (ms) | min (ms) | max (ms) | Visual Chart |"
    )
    print(
        "|-------|----------|--------|-------|-----------|-------------|----------|----------|----------|--------------|"
    )

    for result in results:
        awscrt_str = result["awscrt_version"] or "-"
        chart = make_ascii_bar(result["mean_ms"], min_time, max_time)
        print(
            f"| {result['boto3_version']} | {result['botocore_version']} | {awscrt_str} | "
            f"{result['count']} | {result['mean_ms']:.1f} | {result['median_ms']:.1f} | "
            f"{result['std_dev_ms']:.1f} | {result['min_ms']:.1f} | {result['max_ms']:.1f} | `{chart}` |"
        )

    # Performance comparison
    print()
    print("## Performance Impact Analysis")
    print()

    # Group by boto3/botocore versions to compare with/without awscrt
    version_pairs = defaultdict(dict)
    for result in results:
        version_key = (result["boto3_version"], result["botocore_version"])
        if result["awscrt_version"]:
            version_pairs[version_key]["with_awscrt"] = result
        else:
            version_pairs[version_key]["without_awscrt"] = result

    print("| Version | Without CRT (ms) | With CRT (ms) | Speedup |")
    print("|---------|------------------|---------------|---------|")

    for (boto3_ver, botocore_ver), pair in version_pairs.items():
        if "with_awscrt" in pair and "without_awscrt" in pair:
            without = pair["without_awscrt"]["mean_ms"]
            with_crt = pair["with_awscrt"]["mean_ms"]
            speedup = without / with_crt
            version_str = f"{boto3_ver}/{botocore_ver}"
            print(f"| {version_str} | {without:.1f} | {with_crt:.1f} | {speedup:.2f}x |")


if __name__ == "__main__":
    main()
