"""
CO3: Custom Sorting Algorithms.
Pure Python implementations of Bubble Sort, Selection Sort, Insertion Sort, and Merge Sort.
Each tracks comparisons and element movements/swaps for performance analysis.
"""

from typing import TypeVar, List, Callable, Optional, Dict, Any, Tuple
import time

T = TypeVar("T")


def _get_key_func(key: Optional[Callable[[T], Any]]) -> Callable[[T], Any]:
    return key if key is not None else (lambda x: x)


def bubble_sort(
    arr: List[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False
) -> Tuple[List[T], Dict[str, Any]]:
    """
    Bubble Sort: Repeatedly steps through the list, compares adjacent elements,
    and swaps them if they are in the wrong order. Early exit optimization if no swaps occur.
    Time Complexity: Best O(n), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    a = list(arr)
    n = len(a)
    kf = _get_key_func(key)
    comparisons = 0
    swaps = 0

    start_time = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            left_val = kf(a[j])
            right_val = kf(a[j + 1])
            condition = (left_val < right_val) if reverse else (left_val > right_val)
            if condition:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Bubble Sort",
        "comparisons": comparisons,
        "swaps": swaps,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(n^2)",
        "space_complexity": "O(1)",
    }
    return a, stats


def selection_sort(
    arr: List[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False
) -> Tuple[List[T], Dict[str, Any]]:
    """
    Selection Sort: Repeatedly finds the minimum (or maximum) element from the
    unsorted part and puts it at the beginning.
    Time Complexity: Best O(n^2), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    a = list(arr)
    n = len(a)
    kf = _get_key_func(key)
    comparisons = 0
    swaps = 0

    start_time = time.perf_counter()

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            cur_val = kf(a[j])
            tgt_val = kf(a[target_idx])
            condition = (cur_val > tgt_val) if reverse else (cur_val < tgt_val)
            if condition:
                target_idx = j

        if target_idx != i:
            a[i], a[target_idx] = a[target_idx], a[i]
            swaps += 1

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Selection Sort",
        "comparisons": comparisons,
        "swaps": swaps,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(n^2)",
        "space_complexity": "O(1)",
    }
    return a, stats


def insertion_sort(
    arr: List[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False
) -> Tuple[List[T], Dict[str, Any]]:
    """
    Insertion Sort: Builds the sorted array one item at a time by inserting elements
    into their correct position.
    Time Complexity: Best O(n), Average O(n^2), Worst O(n^2). Space: O(1) auxiliary.
    """
    a = list(arr)
    n = len(a)
    kf = _get_key_func(key)
    comparisons = 0
    shifts = 0

    start_time = time.perf_counter()

    for i in range(1, n):
        item = a[i]
        item_val = kf(item)
        j = i - 1

        while j >= 0:
            comparisons += 1
            left_val = kf(a[j])
            condition = (left_val < item_val) if reverse else (left_val > item_val)
            if condition:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = item

    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Insertion Sort",
        "comparisons": comparisons,
        "swaps": shifts,  # shifts of elements
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(n^2)",
        "space_complexity": "O(1)",
    }
    return a, stats


def merge_sort(
    arr: List[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False
) -> Tuple[List[T], Dict[str, Any]]:
    """
    Merge Sort: Divide-and-conquer algorithm that divides array in halves,
    sorts them recursively, and merges sorted halves.
    Time Complexity: Best O(n log n), Average O(n log n), Worst O(n log n). Space: O(n).
    """
    a = list(arr)
    kf = _get_key_func(key)
    comparisons = 0
    moves = 0

    start_time = time.perf_counter()

    def _merge(left: List[T], right: List[T]) -> List[T]:
        nonlocal comparisons, moves
        merged: List[T] = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            l_val = kf(left[i])
            r_val = kf(right[j])
            condition = (l_val >= r_val) if reverse else (l_val <= r_val)
            if condition:
                merged.append(left[i])
                moves += 1
                i += 1
            else:
                merged.append(right[j])
                moves += 1
                j += 1

        while i < len(left):
            merged.append(left[i])
            moves += 1
            i += 1
        while j < len(right):
            merged.append(right[j])
            moves += 1
            j += 1
        return merged

    def _sort(lst: List[T]) -> List[T]:
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left_sorted = _sort(lst[:mid])
        right_sorted = _sort(lst[mid:])
        return _merge(left_sorted, right_sorted)

    sorted_result = _sort(a)
    elapsed_us = (time.perf_counter() - start_time) * 1_000_000

    stats = {
        "algorithm": "Merge Sort",
        "comparisons": comparisons,
        "swaps": moves,
        "time_us": round(elapsed_us, 2),
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
    }
    return sorted_result, stats
