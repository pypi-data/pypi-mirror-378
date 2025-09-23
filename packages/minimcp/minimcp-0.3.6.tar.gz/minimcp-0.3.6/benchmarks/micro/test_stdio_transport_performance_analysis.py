"""
Benchmark: sequential vs. concurrent stdio transports.

This benchmark validates the core logic behind sequential and concurrent stdio
transports. When message handlers are **synchronous and CPU-bound** (e.g., numerical
computations, string operations), running them concurrently via asyncio tasks doesn't
provide any benefit. This is true even when threads are used. In fact, the additional
scheduling/coordination overhead can make things slower. In CPython this is primarily
because of the Global Interpreter Lock (GIL), which prevents true parallel execution
of CPU-bound Python bytecode across threads.

To capture that reality, the 'sequential' transport processes messages in a simple
loop with minimal overhead, and is intended for cases where all handlers are
synchronous functions.

This benchmark includes:
- Variable load testing (100, 1000, 3000, 10000 messages) to identify crossover points
- Memory profiling to measure memory usage differences between approaches
- Performance scaling analysis across different message volumes

Notes:
- If handlers are I/O-bound or `async`/awaitable, a concurrent transport will
  deliver better throughput. But that's not covered by this benchmark.
- Behavior may differ under alternative Python runtimes.
- Memory measurements use Python's built-in tracemalloc for accuracy.
"""

import gc
import tracemalloc
from collections.abc import AsyncIterator

import anyio
import pytest


async def handler(item: int) -> int:
    # Just a trivial function to simulate synchronous CPU-bound processing.
    # Keeping it async to match the handler signature in the stdio transport.
    computation_result = sum(i * i for i in range(item % 100 + 1))
    return item + computation_result


async def handle_message(item: int):
    return await handler(item)


# async generator (fresh per call) with configurable load
async def make_data(message_count: int) -> AsyncIterator[int]:
    for i in range(message_count):
        yield i


async def concurrent_func(message_count: int):
    async with anyio.create_task_group() as tg:
        async for line in make_data(message_count):
            tg.start_soon(handle_message, line)


async def sequential_func(message_count: int):
    async for line in make_data(message_count):
        await handle_message(line)


def measure_memory_usage(func, *args, **kwargs):
    """Measure peak memory usage of a function using tracemalloc."""
    # Force garbage collection before measuring
    gc.collect()

    # Start tracing memory allocations
    tracemalloc.start()

    try:
        result = func(*args, **kwargs)
        # Get current memory usage
        current, peak = tracemalloc.get_traced_memory()
        return result, peak
    finally:
        tracemalloc.stop()


def create_benchmark_with_memory_profiling(func, message_count: int):
    """Create a benchmark function that measures both time and memory."""
    memory_usage: list[int] = []

    def run():
        def sync_runner():
            return anyio.run(func, message_count)

        result, peak_memory = measure_memory_usage(sync_runner)
        # Store memory info for later analysis (pytest-benchmark doesn't capture this directly)
        memory_usage.append(peak_memory)
        return result

    return run, memory_usage


# === Benchmark Tests ===

# Variable load testing parameters
MESSAGE_LOADS = [100, 1000, 3000, 10000]


@pytest.mark.benchmark
@pytest.mark.parametrize("message_count", MESSAGE_LOADS)
def test_concurrent_func_variable_load(benchmark, message_count):
    """Test concurrent transport with variable message loads."""
    run_func, memory_usage = create_benchmark_with_memory_profiling(concurrent_func, message_count)

    benchmark.pedantic(run_func, rounds=5, iterations=1)

    # Log memory usage information
    avg_memory = sum(memory_usage) / len(memory_usage)
    max_memory = max(memory_usage)
    print(
        f"\nConcurrent ({message_count} messages): "
        f"Peak memory: {max_memory / 1024 / 1024:.2f} MB, "
        f"Avg: {avg_memory / 1024 / 1024:.2f} MB"
    )


@pytest.mark.benchmark
@pytest.mark.parametrize("message_count", MESSAGE_LOADS)
def test_sequential_func_variable_load(benchmark, message_count):
    """Test sequential transport with variable message loads."""
    run_func, memory_usage = create_benchmark_with_memory_profiling(sequential_func, message_count)

    benchmark.pedantic(run_func, rounds=5, iterations=1)

    # Log memory usage information
    avg_memory = sum(memory_usage) / len(memory_usage)
    max_memory = max(memory_usage)
    print(
        f"\nSequential ({message_count} messages): "
        f"Peak memory: {max_memory / 1024 / 1024:.2f} MB, "
        f"Avg: {avg_memory / 1024 / 1024:.2f} MB"
    )


# Additional memory-focused tests for direct comparison
@pytest.mark.benchmark
def test_memory_comparison_large_load(benchmark):
    """Direct memory usage comparison with large load (10k messages)."""

    def run_both():
        # Test sequential first
        def seq_runner():
            return anyio.run(sequential_func, 10000)

        _, seq_memory = measure_memory_usage(seq_runner)

        # Force cleanup between tests
        gc.collect()

        # Test concurrent
        def conc_runner():
            return anyio.run(concurrent_func, 10000)

        _, conc_memory = measure_memory_usage(conc_runner)

        memory_ratio = conc_memory / seq_memory if seq_memory > 0 else 0
        print("\nMemory usage comparison (10k messages):")
        print(f"  Sequential: {seq_memory / 1024 / 1024:.2f} MB")
        print(f"  Concurrent: {conc_memory / 1024 / 1024:.2f} MB")
        print(f"  Ratio (concurrent/sequential): {memory_ratio:.2f}x")

        return seq_memory, conc_memory

    benchmark.pedantic(run_both, rounds=3, iterations=1)
