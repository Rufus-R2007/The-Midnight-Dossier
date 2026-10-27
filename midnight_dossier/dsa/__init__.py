"""
Custom Data Structures and Algorithms package for The Midnight Dossier.
Implements pure Python ADTs and algorithms for Course Outcomes CO1 - CO5.
"""

from .stack import Stack, UndoRedoManager, StackUnderflowError
from .queue import Queue, CircularQueue, QueueUnderflowError, QueueOverflowError
from .linked_list import DoublyLinkedList, DoublyLinkedListNode
from .hash_table import HashTable, HashTableEntry
from .sorting import bubble_sort, selection_sort, insertion_sort, merge_sort
from .searching import linear_search, binary_search, interpolation_search
from .trie import Trie, TrieNode
from .bst import BinarySearchTree, BSTNode
from .heap import MaxHeap, PriorityQueue, HeapEmptyError
from .graph import Graph, GraphNode, GraphEdge
from .benchmark import run_sorting_benchmark, run_searching_benchmark

__all__ = [
    "Stack",
    "UndoRedoManager",
    "StackUnderflowError",
    "Queue",
    "CircularQueue",
    "QueueUnderflowError",
    "QueueOverflowError",
    "DoublyLinkedList",
    "DoublyLinkedListNode",
    "HashTable",
    "HashTableEntry",
    "bubble_sort",
    "selection_sort",
    "insertion_sort",
    "merge_sort",
    "linear_search",
    "binary_search",
    "interpolation_search",
    "Trie",
    "TrieNode",
    "BinarySearchTree",
    "BSTNode",
    "MaxHeap",
    "PriorityQueue",
    "HeapEmptyError",
    "Graph",
    "GraphNode",
    "GraphEdge",
    "run_sorting_benchmark",
    "run_searching_benchmark",
]
