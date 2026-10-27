"""
CO3: Custom Searching Algorithms.
Pure Python implementations of Linear Search, Binary Search, and Interpolation Search.
Each tracks comparisons and inspected indices for performance analysis.
"""

from typing import TypeVar, List, Callable, Optional, Dict, Any, Tuple
import time

T = TypeVar("T")


def _get_key_func(key: Optional[Callable[[T], Any]]) -> Callable[[T], Any]:
    return key if key is not None else (lambda x: x)


def linear_search(
    arr: List[T],
    target: Any,
    key: Optional[Callable[[T], Any]] = None
) -> Tuple[Optional[int], Dict[str, Any]]:
    """
    Linear Search: Checks every element sequentially until target is found or end is reached.
    Applicable to unsorted or sorted collections.
    Time Complexity: Best O(1), Average O(n), Worst O(n). Space: O(1).
    """
    kf = _get_key_func(key)
    comparisons = 0
    checked_indices: List[int] = []

    start_time = time.perf_counter()
    found_idx: Optional[int] = None

    for i, item in enumerate(arr):
        comparisons += 1
        checked_indices.append(i)
        if kf(item) == target:
            found_idx = i
            break

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Linear Search",
        "comparisons": comparisons,
        "checked_indices": checked_indices,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    }
    return found_idx, stats


def binary_search(
    arr: List[T],
    target: Any,
    key: Optional[Callable[[T], Any]] = None
) -> Tuple[Optional[int], Dict[str, Any]]:
    """
    Binary Search: Halves the search space at each step. Requires sorted array.
    Time Complexity: Best O(1), Average O(log n), Worst O(log n). Space: O(1).
    """
    kf = _get_key_func(key)
    comparisons = 0
    checked_indices: List[int] = []

    start_time = time.perf_counter()
    found_idx: Optional[int] = None

    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        checked_indices.append(mid)
        mid_val = kf(arr[mid])

        if mid_val == target:
            found_idx = mid
            break
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Binary Search",
        "comparisons": comparisons,
        "checked_indices": checked_indices,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
    }
    return found_idx, stats


def interpolation_search(
    arr: List[T],
    target: float,
    key: Optional[Callable[[T], float]] = None
) -> Tuple[Optional[int], Dict[str, Any]]:
    """
    Interpolation Search: Probes position using linear interpolation formula:
    pos = low + [ (target - arr[low]) * (high - low) / (arr[high] - arr[low]) ]
    Requires sorted array with numerical keys.
    Robustly handles duplicates, out-of-bounds, and equal endpoint values.
    Time Complexity: Best O(1), Average O(log log n) for uniform distributions, Worst O(n).
    """
    kf = key if key is not None else (lambda x: float(x))
    comparisons = 0
    checked_indices: List[int] = []

    start_time = time.perf_counter()
    found_idx: Optional[int] = None

    if len(arr) > 0:
        low = 0
        high = len(arr) - 1

        while low <= high:
            low_val = float(kf(arr[low]))
            high_val = float(kf(arr[high]))

            # Guard 1: target out of boundary bounds
            if target < low_val or target > high_val:
                break

            # Guard 2: endpoints equal
            if low_val == high_val:
                comparisons += 1
                checked_indices.append(low)
                if low_val == target:
                    found_idx = low
                break

            # Interpolation probe formula
            fraction = (target - low_val) / (high_val - low_val)
            pos = low + int(fraction * (high - low))

            # Guard 3: clamp probe within bounds
            if pos < low:
                pos = low
            elif pos > high:
                pos = high

            comparisons += 1
            checked_indices.append(pos)
            pos_val = float(kf(arr[pos]))

            if pos_val == target:
                found_idx = pos
                break
            elif pos_val < target:
                low = pos + 1
            else:
                high = pos - 1

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Interpolation Search",
        "comparisons": comparisons,
        "checked_indices": checked_indices,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(log log n) avg, O(n) worst",
        "space_complexity": "O(1)",
    }
    return found_idx, stats
