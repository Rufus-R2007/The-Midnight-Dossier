"""
CO2: Doubly Linked List ADT.
Pure Python implementation for chronological investigation timeline navigation.
Enables bidirectional step-by-step traversal through case events.
"""

from typing import Generic, TypeVar, Optional, List, Callable, Iterator, Any

T = TypeVar("T")


class DoublyLinkedListNode(Generic[T]):
    """Node in a Doubly Linked List containing data and bidirectional pointers."""

    def __init__(self, data: T) -> None:
        self.data: T = data
        self.prev: Optional["DoublyLinkedListNode[T]"] = None
        self.next: Optional["DoublyLinkedListNode[T]"] = None

    def __repr__(self) -> str:
        return f"Node({self.data!r})"


class DoublyLinkedList(Generic[T]):
    """
    Custom Doubly Linked List ADT with head and tail pointers.
    Maintains O(1) insertion at head and tail, and supports bidirectional traversal.
    """

    def __init__(self) -> None:
        self.head: Optional[DoublyLinkedListNode[T]] = None
        self.tail: Optional[DoublyLinkedListNode[T]] = None
        self._size: int = 0

    def is_empty(self) -> bool:
        """Return True if list is empty, False otherwise. O(1)."""
        return self._size == 0

    def size(self) -> int:
        """Return number of elements. O(1)."""
        return self._size

    def append(self, item: T) -> DoublyLinkedListNode[T]:
        """Append an element to the tail of the list. O(1)."""
        new_node = DoublyLinkedListNode(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._size += 1
        return new_node

    def prepend(self, item: T) -> DoublyLinkedListNode[T]:
        """Prepend an element to the head of the list. O(1)."""
        new_node = DoublyLinkedListNode(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            assert self.head is not None
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
        return new_node

    def insert_after(self, target_node: DoublyLinkedListNode[T], item: T) -> DoublyLinkedListNode[T]:
        """Insert a new node immediately after target_node. O(1)."""
        if target_node is None:
            raise ValueError("Target node cannot be None.")

        new_node = DoublyLinkedListNode(item)
        new_node.prev = target_node
        new_node.next = target_node.next

        if target_node.next is not None:
            target_node.next.prev = new_node
        else:
            self.tail = new_node

        target_node.next = new_node
        self._size += 1
        return new_node

    def delete_node(self, node: DoublyLinkedListNode[T]) -> T:
        """
        Delete a specific node from the list in O(1) time once located.
        Updates head, tail, and adjacent pointers safely.
        """
        if node is None:
            raise ValueError("Node cannot be None.")

        # Update previous neighbor
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        # Update next neighbor
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        # Nullify deleted node's pointers
        node.prev = None
        node.next = None
        self._size -= 1
        return node.data

    def delete(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """
        Find and delete the first node satisfying predicate.
        Returns the data deleted, or None if not found. O(n).
        """
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return self.delete_node(curr)
            curr = curr.next
        return None

    def find(self, predicate: Callable[[T], bool]) -> Optional[DoublyLinkedListNode[T]]:
        """
        Search linearly for the first node matching predicate. O(n).
        """
        curr = self.head
        while curr is not None:
            if predicate(curr.data):
                return curr
            curr = curr.next
        return None

    def forward_iter(self) -> Iterator[T]:
        """Traverse forward from head to tail."""
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def backward_iter(self) -> Iterator[T]:
        """Traverse backward from tail to head."""
        curr = self.tail
        while curr is not None:
            yield curr.data
            curr = curr.prev

    def to_list(self) -> List[T]:
        """Convert list elements to Python list (forward order). O(n)."""
        return list(self.forward_iter())

    def clear(self) -> None:
        """Clear all nodes."""
        curr = self.head
        while curr is not None:
            nxt = curr.next
            curr.prev = None
            curr.next = None
            curr = nxt
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self) -> int:
        return self.size()

    def __iter__(self) -> Iterator[T]:
        return self.forward_iter()

    def __repr__(self) -> str:
        return f"DoublyLinkedList({self.to_list()!r})"
