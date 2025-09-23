# MiniMCP · Benchmarks

Once you’ve set up a MiniMCP development environment as described in [CONTRIBUTING.md](../CONTRIBUTING.md)
, you can run the benchmarks to re-evaluate the project.

The benchmarks serve two purposes:

1. Validate design decisions
1. Compare MiniMCP against FastMCP

## Run Benchmarks

### Run All Benchmark Tests

```bash
uv run pytest -m benchmark
```

### MiniMCP Stdio Sequential vs Concurrent Transport Performance Analysis

```bash
uv run pytest benchmarks/micro/test_stdio_transport_performance_analysis.py -m benchmark -v
```

The benchmarks provide clear evidence that sequential transport is superior for CPU-bound workloads in both performance and memory efficiency.

- **Performance:** Sequential transport is consistently **2-3x faster** across all message loads
- **Memory Usage:** Sequential uses **2000x less memory** at high loads (10k messages)
- **Scaling:** Sequential maintains linear performance scaling with constant memory footprint

Complete details can be found in the [stdio_transport_performance_analysis](./reports/stdio_transport_performance_analysis.md) report.
