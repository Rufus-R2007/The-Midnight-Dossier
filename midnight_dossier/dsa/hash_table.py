"""
CO3: Custom Hash Table using Separate Chaining.
Pure Python implementation of Hash Table for evidence ID indexing (e.g. EV-01).
Demonstrates hash function, collision handling, bucket chaining, and load factor.
"""

from typing import Generic, TypeVar, Optional, List, Tuple, Any

K = TypeVar("K")
V = TypeVar("V")


class HashTableEntry(Generic[K, V]):
    """Stores key-value pair in a collision chain."""

    def __init__(self, key: K, value: V) -> None:
        self.key: K = key
        self.value: V = value

    def __repr__(self) -> str:
        return f"Entry({self.key!r}: {self.value!r})"


class HashTable(Generic[K, V]):
    """
    Custom Hash Table using Separate Chaining for collision resolution.
    Uses polynomial rolling hash for string keys and modulo arithmetic.
    """

    def __init__(self, capacity: int = 17) -> None:
        self.capacity: int = capacity
        self.buckets: List[List[HashTableEntry[K, V]]] = [[] for _ in range(self.capacity)]
        self._count: int = 0
        self._total_collisions_encountered: int = 0

    def _hash_function(self, key: K) -> int:
        """
        Compute hash code using polynomial rolling hash (base 31) and modulo capacity.
        Deterministic and custom-built for educational clarity.
        """
        key_str = str(key)
        hash_val = 0
        p = 31
        for ch in key_str:
            hash_val = (hash_val * p + ord(ch)) % self.capacity
        return hash_val

    def insert(self, key: K, value: V) -> None:
        """
        Insert or update a key-value pair.
        Average Case: O(1)
        Worst Case (all collide): O(n)
        """
        bucket_idx = self._hash_function(key)
        bucket = self.buckets[bucket_idx]

        # Check if key already exists (update)
        for entry in bucket:
            if entry.key == key:
                entry.value = value
                return

        # Key is new; if bucket already has entries, collision occurred
        if len(bucket) > 0:
            self._total_collisions_encountered += 1

        bucket.append(HashTableEntry(key, value))
        self._count += 1

        # Check if rehash needed when load factor exceeds 0.75
        if self.load_factor() > 0.75:
            self._rehash(self.capacity * 2 + 1)

    def search(self, key: K) -> Optional[V]:
        """
        Look up value by key. Returns None if key not found.
        Average Case: O(1)
        Worst Case: O(n)
        """
        bucket_idx = self._hash_function(key)
        bucket = self.buckets[bucket_idx]
        for entry in bucket:
            if entry.key == key:
                return entry.value
        return None

    def delete(self, key: K) -> bool:
        """
        Remove key-value pair. Returns True if deleted, False if not found.
        """
        bucket_idx = self._hash_function(key)
        bucket = self.buckets[bucket_idx]
        for i, entry in enumerate(bucket):
            if entry.key == key:
                bucket.pop(i)
                self._count -= 1
                return True
        return False

    def contains(self, key: K) -> bool:
        """Return True if key exists in table."""
        return self.search(key) is not None

    def get_bucket_index(self, key: K) -> int:
        """Return the target bucket index for a given key."""
        return self._hash_function(key)

    def inspect_bucket(self, bucket_idx: int) -> List[Tuple[K, V]]:
        """Return contents of a specific bucket for educational inspection."""
        if 0 <= bucket_idx < self.capacity:
            return [(e.key, e.value) for e in self.buckets[bucket_idx]]
        return []

    def load_factor(self) -> float:
        """Ratio of stored items to bucket capacity (n / m)."""
        return self._count / self.capacity if self.capacity > 0 else 0.0

    def collision_stats(self) -> dict:
        """Provide detailed statistics for the Detective's Toolkit."""
        non_empty = [b for b in self.buckets if len(b) > 0]
        collided_buckets = [b for b in self.buckets if len(b) > 1]
        max_chain = max((len(b) for b in self.buckets), default=0)
        return {
            "capacity": self.capacity,
            "total_items": self._count,
            "load_factor": round(self.load_factor(), 3),
            "occupied_buckets": len(non_empty),
            "collided_buckets": len(collided_buckets),
            "max_chain_length": max_chain,
            "total_collisions": self._total_collisions_encountered,
        }

    def _rehash(self, new_capacity: int) -> None:
        """Rehash all entries into a larger bucket array."""
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self._count = 0
        for bucket in old_buckets:
            for entry in bucket:
                self.insert(entry.key, entry.value)

    def keys(self) -> List[K]:
        res = []
        for b in self.buckets:
            for e in b:
                res.append(e.key)
        return res

    def values(self) -> List[V]:
        res = []
        for b in self.buckets:
            for e in b:
                res.append(e.value)
        return res

    def items(self) -> List[Tuple[K, V]]:
        res = []
        for b in self.buckets:
            for e in b:
                res.append((e.key, e.value))
        return res

    def size(self) -> int:
        return self._count

    def clear(self) -> None:
        self.buckets = [[] for _ in range(self.capacity)]
        self._count = 0
        self._total_collisions_encountered = 0

    def __len__(self) -> int:
        return self.size()

    def __getitem__(self, key: K) -> V:
        val = self.search(key)
        if val is None:
            raise KeyError(f"Key {key!r} not found in HashTable.")
        return val

    def __setitem__(self, key: K, value: V) -> None:
        self.insert(key, value)
