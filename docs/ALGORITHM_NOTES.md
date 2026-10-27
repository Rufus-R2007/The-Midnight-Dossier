# Technical Algorithm Notes & Case Forensic Analysis
## Project: THE MIDNIGHT DOSSIER (Case 001 — The Blackwood Heist)

---

## 1. Core Data Structures & Algorithm Design

### 1.1 Stack ADT & Undo/Redo Engine (CO1)
* **File:** `midnight_dossier/dsa/stack.py`
* **Mathematical Model:** $S = \langle e_1, e_2, \dots, e_k \rangle$ where operations occur strictly at the top element $e_k$.
* **Implementation:** Dynamic contiguous array supporting amortized $O(1)$ push and $O(1)$ pop/peek.
* **Dual-Stack Mechanism:**
  ```python
  def record_action(self, action):
      self.undo_stack.push(action)
      self.redo_stack.clear() # Branch invalidation
  ```
  Executing an undo transfers the top state to `redo_stack`, while executing a new action flushes `redo_stack` to prevent non-linear history corruption.

### 1.2 Queue ADT & Circular Queue (CO1)
* **File:** `midnight_dossier/dsa/queue.py`
* **Mathematical Model:** FIFO order where insertions occur at `rear` and removals occur at `front`.
* **Circular Queue Pointer Arithmetic:**
  $$\text{rear} \leftarrow (\text{rear} + 1) \pmod{\text{capacity}}$$
  $$\text{front} \leftarrow (\text{front} + 1) \pmod{\text{capacity}}$$
  Eliminates $O(n)$ array element shifting overhead, achieving strict $O(1)$ bounded performance.

### 1.3 Doubly Linked List (CO2)
* **File:** `midnight_dossier/dsa/linked_list.py`
* **Node Structure:**
  ```
  Node {
      data: TimelineEvent,
      prev: Optional[Node],
      next: Optional[Node]
  }
  ```
* **Invariant:** For any inner node $x$, $x.\text{next}.\text{prev} = x$ and $x.\text{prev}.\text{next} = x$.
* **Rationale:** In a chronological detective investigation, navigating step-by-step backward and forward through event time is an $O(1)$ pointer dereference. Inserting new evidence nodes between historical moments does not require moving existing memory blocks.

### 1.4 Separate-Chaining Hash Table (CO3)
* **File:** `midnight_dossier/dsa/hash_table.py`
* **Hash Function:** Polynomial rolling hash with prime radix $p=31$:
  $$\text{hash}(s) = \left( \sum_{i=0}^{L-1} s[i] \cdot 31^{L-1-i} \right) \pmod{M}$$
  where $M = 17$ (initial prime capacity).
* **Collision Resolution:** Separate chaining. Each bucket $B[h]$ stores a linked chain of `HashTableEntry(key, value)`.
* **Load Factor:** $\alpha = \frac{N}{M}$. If $\alpha > 0.75$, dynamic resizing doubles capacity to $2M + 1$ (next odd/prime candidate) to maintain $O(1)$ average lookup.

### 1.5 Sorting Algorithms (CO3)
* **File:** `midnight_dossier/dsa/sorting.py`

| Algorithm | Comparisons | Swaps / Moves | Best Case | Average Case | Worst Case | Space |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bubble Sort** | Adjacent pairs with early exit flag | Adjacent swaps | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ |
| **Selection Sort** | Unsorted suffix scan for minimum | Max 1 swap per outer pass | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ |
| **Insertion Sort** | Reverse scan in sorted prefix | Rightward shifts | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ |
| **Merge Sort** | Divide-and-conquer sub-array merge | Buffer moves | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ |

### 1.6 Searching Algorithms (CO3)
* **File:** `midnight_dossier/dsa/searching.py`
* **Linear Search:** Unconstrained iteration ($O(n)$).
* **Binary Search:** Repeated interval halving ($O(\log n)$) on sorted data.
* **Interpolation Search:** Linear extrapolation probe formula:
  $$\text{pos} = \text{low} + \left\lfloor \frac{\text{target} - A[\text{low}]}{A[\text{high}] - A[\text{low}]} \times (\text{high} - \text{low}) \right\rfloor$$
  Handles uniform distributions in $O(\log \log n)$. Guards against zero denominators and clamps probe within valid bounds $[\text{low}, \text{high}]$.

### 1.7 Prefix Tree (Trie) (CO4)
* **File:** `midnight_dossier/dsa/trie.py`
* **Structure:** Multiway tree where each node possesses character transition pointers `children: dict[char, TrieNode]` and `is_end_of_word: bool`.
* **Time Complexity:** Search and prefix matching depend strictly on string length $L$, achieving $O(L)$ time independent of total stored dictionary size $N$.

### 1.8 Binary Search Tree (BST) (CO4)
* **File:** `midnight_dossier/dsa/bst.py`
* **Invariant:** $\forall y \in \text{Left}(x), \text{key}(y) < \text{key}(x)$ and $\forall z \in \text{Right}(x), \text{key}(z) > \text{key}(x)$.
* **Three-Case Deletion:**
  1. *Leaf node:* Set parent reference to `None`.
  2. *Single child:* Bypass node by linking parent directly to its child.
  3. *Two children:* Locate inorder successor (minimum element in right subtree), copy successor data to current node, and recursively delete successor from right subtree.
* **Traversals:**
  * Inorder (Left, Root, Right) $\rightarrow$ strictly sorted key sequence.
  * Preorder (Root, Left, Right) $\rightarrow$ tree serialization order.
  * Postorder (Left, Right, Root) $\rightarrow$ bottom-up deletion order.

### 1.9 Max-Heap & Priority Queue (CO4)
* **File:** `midnight_dossier/dsa/heap.py`
* **Complete Binary Tree in Array:**
  $$\text{Parent}(i) = \left\lfloor \frac{i-1}{2} \right\rfloor, \quad \text{Left}(i) = 2i + 1, \quad \text{Right}(i) = 2i + 2$$
* **Invariant:** $A[\text{Parent}(i)] \ge A[i]$ for all valid indices.
* **Sift-Up:** Restores invariant after insertion at leaf in $O(\log n)$.
* **Sift-Down:** Restores invariant after replacing root with last element during extraction in $O(\log n)$.

### 1.10 Adjacency-List Graph & Network Traversals (CO5)
* **File:** `midnight_dossier/dsa/graph.py`
* **Representation:** `Dict[str, List[GraphEdge]]` representing suspects, evidence, places, and events.
* **Deterministic Neighbor Ordering:** Edges are traversed in lexicographical order of destination node ID to ensure fully reproducible viva demonstrations.
* **Breadth-First Search (BFS):**
  * Maintains FIFO exploration queue.
  * Computes single-source shortest path in unweighted networks ($O(V + E)$).
  * Records back-pointers to reconstruct exact evidence chain.
* **Depth-First Search (DFS):**
  * Explores branches deeply using recursive stack.
  * Detects back-edges indicating investigative feedback cycles ($O(V + E)$).

---

## 2. The Blackwood Heist — Complete Forensic Solution & Case Matrix

### 2.1 The Mystery Synopsis
At 21:47, during an evening restoration shift at the Blackwood Museum, circuit breaker #4 was manually tripped, blinding the security cameras covering Gallery B and the Service Corridor for 9 minutes. At 21:56, when power was restored, the priceless 14th-century **Asterion Compass (EV-01)** was discovered missing from its display vitrine.

### 2.2 Culprit Identification & Forensic Corroboration
* **Culprit:** **Oliver Reed** (Restoration Contractor, `SUS-01`).
* **Motive & Opportunity:** Hired to restore showcase woodwork. Possessed unrestricted evening contractor credentials and specialized tools.
* **Corroborating Evidence Chain:**
  1. **EV-02 (Maintenance Request MR-04):** Oliver initiated an emergency recalibration of Gallery B cameras at 21:42, giving him legitimate access to the sub-electrical switchboard right before the blackout.
  2. **EV-03 (CCTV Outage Glitch Log):** Confirms manual breaker trip at 21:47 rather than remote network intrusion.
  3. **EV-04 (Keycard KC-09 Service Scan):** Oliver's badge unlocked the restricted Service Corridor door at 21:49, directly linking him to the crime scene during the blackout.
  4. **EV-07 (Pedestal Wire Cut Forensic Analysis):** Display alarm wires were severed with serrated micro-snips exclusive to antique metal restoration toolkits.
  5. **EV-05 (Missing Instrument Case IC-02):** Padded velvet tool case brought in by Oliver was reported missing from his workshop locker, with internal dimensions matching the Asterion Compass.
  6. **EV-06 (Van Departure Log VR-07):** Perimeter gate camera recorded Oliver's van departing at 22:12, completely contradicting his alibi of having left at 21:30.

### 2.3 Exoneration of Red Herrings
* **Evelyn Shaw (`SUS-02`, Archivist):** Her database account appeared in server access logs at 21:50 (`EV-08`), but server audit records prove this was an automated system cronjob (`catalog_sync.sh`). Multiple night staff verified her continuous presence in the Staff Tea Room from 21:30 to 22:10 (`EV-09`).
* **Marcus Vale (`SUS-03`, Guard):** Marcus signed the maintenance permit for Oliver (`EV-11`), but dispatch tapes and console telemetry (`EV-10`) show he remained in the Control Booth attempting manual breaker resets and radioing headquarters according to standard protocol.
* **Dr. Lena Hart (`SUS-04`, Curator):** Authored an impassioned memo opposing loaning the Compass overseas (`EV-13`), suggesting motive. However, automated highway toll records and restaurant credit receipts (`EV-12`) definitively prove she was 18 miles away downtown at an archaeological symposium.
