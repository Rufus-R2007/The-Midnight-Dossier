"""
CO1: Stack ADT and Undo/Redo Manager.
Pure Python implementation of Stack without external libraries.
"""

from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar("T")


class StackUnderflowError(IndexError):
    """Raised when an operation cannot be performed on an empty stack."""
    pass


class Stack(Generic[T]):
    """
    Custom LIFO (Last-In-First-Out) Stack ADT.
    Implemented using an internal dynamic array with O(1) amortized push and pop.
    """

    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        """Push an element onto the top of the stack. O(1) amortized."""
        self._items.append(item)

    def pop(self) -> T:
        """
        Remove and return the top element of the stack. O(1).
        Raises StackUnderflowError if the stack is empty.
        """
        if self.is_empty():
            raise StackUnderflowError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        """
        Return the top element of the stack without removing it. O(1).
        Raises StackUnderflowError if the stack is empty.
        """
        if self.is_empty():
            raise StackUnderflowError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return True if the stack contains no elements, False otherwise. O(1)."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of elements in the stack. O(1)."""
        return len(self._items)

    def clear(self) -> None:
        """Remove all elements from the stack. O(1)."""
        self._items.clear()

    def to_list(self) -> List[T]:
        """Return a copy of the elements from bottom to top."""
        return list(self._items)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"


class UndoRedoManager(Generic[T]):
    """
    Manages undo and redo history for detective board actions using two LIFO Stacks.
    - undo_stack: stores executed actions.
    - redo_stack: stores undone actions that can be re-executed.
    """

    def __init__(self, max_history: int = 50) -> None:
        self.undo_stack: Stack[T] = Stack()
        self.redo_stack: Stack[T] = Stack()
        self.max_history = max_history

    def record_action(self, action: T) -> None:
        """
        Record a new action. Clears redo stack as new actions invalidate future history.
        """
        self.undo_stack.push(action)
        self.redo_stack.clear()

        # Enforce history limit to conserve memory if needed
        if self.undo_stack.size() > self.max_history:
            self.undo_stack._items.pop(0)

    def can_undo(self) -> bool:
        """Return True if there is at least one action to undo."""
        return not self.undo_stack.is_empty()

    def can_redo(self) -> bool:
        """Return True if there is at least one action to redo."""
        return not self.redo_stack.is_empty()

    def undo(self) -> Optional[T]:
        """
        Undo the latest action, moving it to redo stack.
        Returns the undone action, or None if undo_stack is empty.
        """
        if self.can_undo():
            action = self.undo_stack.pop()
            self.redo_stack.push(action)
            return action
        return None

    def redo(self) -> Optional[T]:
        """
        Redo the previously undone action, moving it back to undo stack.
        Returns the redone action, or None if redo_stack is empty.
        """
        if self.can_redo():
            action = self.redo_stack.pop()
            self.undo_stack.push(action)
            return action
        return None

    def clear(self) -> None:
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
