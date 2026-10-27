"""
CO1: Queue ADT and Circular Queue.
Pure Python implementations of FIFO Queue without external libraries.
"""

from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar("T")


class QueueUnderflowError(IndexError):
    """Raised when an operation cannot be performed on an empty queue."""
    pass


class QueueOverflowError(OverflowError):
    """Raised when an operation cannot be performed because a bounded queue is full."""
    pass


class Queue(Generic[T]):
    """
    Custom FIFO (First-In-First-Out) Queue ADT.
    Used for routine investigative leads waiting for detective inspection.
    """

    def __init__(self) -> None:
        self._items: List[T] = []

    def enqueue(self, item: T) -> None:
        """Add an element to the rear of the queue. O(1)."""
        self._items.append(item)

    def dequeue(self) -> T:
        """
        Remove and return the front element of the queue.
        Raises QueueUnderflowError if the queue is empty.
        """
        if self.is_empty():
            raise QueueUnderflowError("Cannot dequeue from an empty queue.")
        return self._items.pop(0)

    def peek(self) -> T:
        """
        Return the front element without removing it.
        Raises QueueUnderflowError if the queue is empty.
        """
        if self.is_empty():
            raise QueueUnderflowError("Cannot peek at an empty queue.")
        return self._items[0]

    def is_empty(self) -> bool:
        """Return True if the queue is empty, False otherwise. O(1)."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of elements in the queue. O(1)."""
        return len(self._items)

    def clear(self) -> None:
        """Clear all elements from the queue."""
        self._items.clear()

    def to_list(self) -> List[T]:
        """Return a copy of items from front to rear."""
        return list(self._items)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Queue({self._items!r})"


class CircularQueue(Generic[T]):
    """
    Custom Circular Queue with fixed capacity.
    Demonstrates front/rear pointer arithmetic with modulo wrapping.
    Used for bounded real-time security events.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self.capacity = capacity
        self._buffer: List[Optional[T]] = [None] * capacity
        self._front = 0
        self._rear = 0
        self._count = 0

    def enqueue(self, item: T) -> None:
        """Add an item to the rear with modulo wrapping. Raises QueueOverflowError if full."""
        if self.is_full():
            raise QueueOverflowError(f"CircularQueue capacity ({self.capacity}) exceeded.")
        self._buffer[self._rear] = item
        self._rear = (self._rear + 1) % self.capacity
        self._count += 1

    def dequeue(self) -> T:
        """Remove and return front item with modulo wrapping."""
        if self.is_empty():
            raise QueueUnderflowError("Cannot dequeue from an empty circular queue.")
        item = self._buffer[self._front]
        self._buffer[self._front] = None
        self._front = (self._front + 1) % self.capacity
        self._count -= 1
        return item  # type: ignore

    def peek(self) -> T:
        """Return front item without removing."""
        if self.is_empty():
            raise QueueUnderflowError("Cannot peek at an empty circular queue.")
        return self._buffer[self._front]  # type: ignore

    def is_empty(self) -> bool:
        return self._count == 0

    def is_full(self) -> bool:
        return self._count == self.capacity

    def size(self) -> int:
        return self._count

    @property
    def front_index(self) -> int:
        return self._front

    @property
    def rear_index(self) -> int:
        return self._rear

    def to_list(self) -> List[T]:
        """Return elements in FIFO order from front to rear."""
        items: List[T] = []
        idx = self._front
        for _ in range(self._count):
            items.append(self._buffer[idx])  # type: ignore
            idx = (idx + 1) % self.capacity
        return items

    def raw_buffer(self) -> List[Optional[T]]:
        return list(self._buffer)
