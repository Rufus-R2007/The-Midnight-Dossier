"""
Unit tests for CO3: Sorting and Searching algorithms.
"""

import unittest
from midnight_dossier.dsa.sorting import bubble_sort, selection_sort, insertion_sort, merge_sort
from midnight_dossier.dsa.searching import linear_search, binary_search, interpolation_search


class TestSortingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.algorithms = [
            ("Bubble Sort", bubble_sort),
            ("Selection Sort", selection_sort),
            ("Insertion Sort", insertion_sort),
            ("Merge Sort", merge_sort),
        ]

    def test_empty_and_single_element(self):
        for name, algo in self.algorithms:
            res_empty, stats_empty = algo([])
            self.assertEqual(res_empty, [], f"{name} failed on empty list")

            res_single, stats_single = algo([42])
            self.assertEqual(res_single, [42], f"{name} failed on single element")

    def test_already_sorted_and_reversed(self):
        for name, algo in self.algorithms:
            arr_sorted = [1, 2, 3, 4, 5, 6, 7]
            res_sorted, _ = algo(arr_sorted)
            self.assertEqual(res_sorted, arr_sorted, f"{name} failed on already sorted")

            arr_rev = [7, 6, 5, 4, 3, 2, 1]
            res_rev, _ = algo(arr_rev)
            self.assertEqual(res_rev, [1, 2, 3, 4, 5, 6, 7], f"{name} failed on reverse sorted")

    def test_duplicates_and_negatives(self):
        for name, algo in self.algorithms:
            arr = [5, -2, 9, 5, 0, -2, 8, 1]
            res, _ = algo(arr)
            self.assertEqual(res, sorted(arr), f"{name} failed on duplicates/negatives")

    def test_custom_key_sorting(self):
        evidence_list = [
            {"id": "EV-03", "time": 2150},
            {"id": "EV-01", "time": 2115},
            {"id": "EV-02", "time": 2130},
        ]
        for name, algo in self.algorithms:
            res, _ = algo(evidence_list, key=lambda x: x["time"])
            times = [x["time"] for x in res]
            self.assertEqual(times, [2115, 2130, 2150], f"{name} failed on custom key")


class TestSearchingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.sorted_arr = [10, 25, 33, 47, 50, 68, 72, 89, 95]

    def test_linear_search(self):
        idx, stats = linear_search(self.sorted_arr, 47)
        self.assertEqual(idx, 3)
        self.assertEqual(stats["comparisons"], 4)

        idx_miss, stats_miss = linear_search(self.sorted_arr, 999)
        self.assertIsNone(idx_miss)
        self.assertEqual(stats_miss["comparisons"], len(self.sorted_arr))

    def test_binary_search(self):
        # Middle element
        idx_mid, stats_mid = binary_search(self.sorted_arr, 50)
        self.assertEqual(idx_mid, 4)

        # First and last
        idx_first, _ = binary_search(self.sorted_arr, 10)
        self.assertEqual(idx_first, 0)
        idx_last, _ = binary_search(self.sorted_arr, 95)
        self.assertEqual(idx_last, 8)

        # Misses
        idx_miss, _ = binary_search(self.sorted_arr, 40)
        self.assertIsNone(idx_miss)
        idx_out, _ = binary_search(self.sorted_arr, 5)
        self.assertIsNone(idx_out)

    def test_interpolation_search(self):
        # Uniform array
        uniform = [10, 20, 30, 40, 50, 60, 70, 80]
        idx, stats = interpolation_search(uniform, 50.0)
        self.assertEqual(idx, 4)

        # First and last
        idx_first, _ = interpolation_search(uniform, 10.0)
        self.assertEqual(idx_first, 0)
        idx_last, _ = interpolation_search(uniform, 80.0)
        self.assertEqual(idx_last, 7)

        # Out of bounds and miss
        idx_low, _ = interpolation_search(uniform, 2.0)
        self.assertIsNone(idx_low)
        idx_high, _ = interpolation_search(uniform, 105.0)
        self.assertIsNone(idx_high)
        idx_mid_miss, _ = interpolation_search(uniform, 35.0)
        self.assertIsNone(idx_mid_miss)

        # Equal endpoints safe handling
        equal_arr = [42, 42, 42, 42]
        idx_eq, _ = interpolation_search(equal_arr, 42.0)
        self.assertEqual(idx_eq, 0)
        idx_eq_miss, _ = interpolation_search(equal_arr, 99.0)
        self.assertIsNone(idx_eq_miss)


if __name__ == "__main__":
    unittest.main()
