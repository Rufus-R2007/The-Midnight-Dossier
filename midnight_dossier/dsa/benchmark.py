"""
CO3: Algorithm Performance Benchmarking Suite.
Measures real execution times, comparisons, and element moves for custom sorting and searching algorithms.
Provides data for the performance comparison view in the Detective's Toolkit.
"""

from typing import List, Dict, Any, Tuple, Optional
import random
from .sorting import bubble_sort, selection_sort, insertion_sort, merge_sort
from .searching import linear_search, binary_search, interpolation_search


def run_sorting_benchmark(sizes: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """
    Run sorting benchmarks across different input sizes with pseudo-random integer keys.
    Returns structured results for visualization in the Detective's Toolkit.
    """
    if sizes is None:
        sizes = [15, 30, 60]

    results: List[Dict[str, Any]] = []

    for n in sizes:
        # Deterministic random seed for fair comparison
        rng = random.Random(42 + n)
        dataset = [rng.randint(100, 999) for _ in range(n)]
        expected = sorted(dataset)

        algorithms = [
            ("Bubble Sort", bubble_sort),
            ("Selection Sort", selection_sort),
            ("Insertion Sort", insertion_sort),
            ("Merge Sort", merge_sort),
        ]

        for name, fn in algorithms:
            sorted_arr, stats = fn(dataset)
            correct = (sorted_arr == expected)
            results.append({
                "size": n,
                "algorithm": name,
                "comparisons": stats["comparisons"],
                "swaps": stats["swaps"],
                "time_us": stats["time_us"],
                "correct": correct,
                "time_complexity": stats["time_complexity"],
                "space_complexity": stats["space_complexity"],
            })

    return results


def run_searching_benchmark(size: int = 50) -> List[Dict[str, Any]]:
    """
    Run searching benchmarks on a sorted uniform dataset.
    Compares Linear Search, Binary Search, and Interpolation Search on both hit and miss cases.
    """
    # Create uniformly spaced sorted numbers: 10, 20, 30, ...
    dataset = [i * 10 for i in range(1, size + 1)]
    target_hit = dataset[size // 2]  # Middle element
    target_miss = dataset[-1] + 5    # Non-existent element

    results: List[Dict[str, Any]] = []

    for target, label in [(target_hit, "Hit (Mid)"), (target_miss, "Miss (Out)")]:
        # Linear Search
        idx_lin, stats_lin = linear_search(dataset, target)
        results.append({
            "algorithm": "Linear Search",
            "scenario": label,
            "target": target,
            "found": idx_lin is not None,
            "comparisons": stats_lin["comparisons"],
            "time_us": stats_lin["time_us"],
            "complexity": stats_lin["time_complexity"],
        })

        # Binary Search
        idx_bin, stats_bin = binary_search(dataset, target)
        results.append({
            "algorithm": "Binary Search",
            "scenario": label,
            "target": target,
            "found": idx_bin is not None,
            "comparisons": stats_bin["comparisons"],
            "time_us": stats_bin["time_us"],
            "complexity": stats_bin["time_complexity"],
        })

        # Interpolation Search
        idx_inp, stats_inp = interpolation_search(dataset, float(target))
        results.append({
            "algorithm": "Interpolation Search",
            "scenario": label,
            "target": target,
            "found": idx_inp is not None,
            "comparisons": stats_inp["comparisons"],
            "time_us": stats_inp["time_us"],
            "complexity": stats_inp["time_complexity"],
        })

    return results
