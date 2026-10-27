"""
CO1 / CO4: Max-Heap and Priority Queue.
Pure Python implementation of Max-Heap without heapq or external libraries.
Used to rank urgent investigation leads by importance score.
"""

from typing import Generic, TypeVar, Optional, List, Callable, Any

T = TypeVar("T")


class HeapEmptyError(IndexError):
    """Raised when an operation cannot be performed on an empty heap."""
    pass


class MaxHeap(Generic[T]):
    """
    Custom Max-Heap implementation based on a 0-indexed array.
    Parent index: (i - 1) // 2
    Left child index: 2 * i + 1
    Right child index: 2 * i + 2
    """

    def __init__(self, key: Optional[Callable[[T], Any]] = None) -> None:
        self._heap: List[T] = []
        self._key: Callable[[T], Any] = key if key is not None else (lambda x: x)

    def _val(self, item: T) -> Any:
        return self._key(item)

    def _sift_up(self, idx: int) -> None:
        """Move element at idx up until heap property is restored. O(log n)."""
        parent = (idx - 1) // 2
        while idx > 0 and self._val(self._heap[idx]) > self._val(self._heap[parent]):
            self._heap[idx], self._heap[parent] = self._heap[parent], self._heap[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int) -> None:
        """Move element at idx down until heap property is restored. O(log n)."""
        size = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest = idx

            if left < size and self._val(self._heap[left]) > self._val(self._heap[largest]):
                largest = left

            if right < size and self._val(self._heap[right]) > self._val(self._heap[largest]):
                largest = right

            if largest != idx:
                self._heap[idx], self._heap[largest] = self._heap[largest], self._heap[idx]
                idx = largest
            else:
                break

    def insert(self, item: T) -> None:
        """Insert a new item into the max-heap. O(log n)."""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def extract_max(self) -> T:
        """
        Remove and return the element with the maximum priority. O(log n).
        Raises HeapEmptyError if heap is empty.
        """
        if self.is_empty():
            raise HeapEmptyError("Cannot extract from an empty heap.")
        if len(self._heap) == 1:
            return self._heap.pop()

        root = self._heap[0]
        # Move last element to root and sift down
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return root

    def peek_max(self) -> T:
        """
        Return the element with the maximum priority without removing it. O(1).
        Raises HeapEmptyError if heap is empty.
        """
        if self.is_empty():
            raise HeapEmptyError("Cannot peek at an empty heap.")
        return self._heap[0]

    def is_empty(self) -> bool:
        """O(1) check if heap has no elements."""
        return len(self._heap) == 0

    def size(self) -> int:
        """O(1) element count."""
        return len(self._heap)

    def to_list(self) -> List[T]:
        """Return the underlying array representation."""
        return list(self._heap)

    def sorted_descending(self) -> List[T]:
        """
        Return all elements sorted in descending order without destroying the original heap.
        Demonstrates Heap Sort principles. O(n log n).
        """
        copy_heap = MaxHeap(key=self._key)
        copy_heap._heap = list(self._heap)
        res = []
        while not copy_heap.is_empty():
            res.append(copy_heap.extract_max())
        return res

    def clear(self) -> None:
        self._heap.clear()

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"MaxHeap({self._heap!r})"


class PriorityQueue(Generic[T]):
    """
    Max-Priority Queue ADT powered by custom MaxHeap.
    Used for scheduling critical detective leads.
    """

    def __init__(self, key: Optional[Callable[[T], Any]] = None) -> None:
        self._heap: MaxHeap[T] = MaxHeap(key=key)

    def enqueue(self, item: T) -> None:
        """Enqueue with priority. O(log n)."""
        self._heap.insert(item)

    def dequeue(self) -> T:
        """Dequeue highest priority item. O(log n)."""
        return self._heap.extract_max()

    def peek(self) -> T:
        """Peek highest priority item. O(1)."""
        return self._heap.peek_max()

    def is_empty(self) -> bool:
        return self._heap.is_empty()

    def size(self) -> int:
        return self._heap.size()

    def to_list(self) -> List[T]:
        return self._heap.to_list()
