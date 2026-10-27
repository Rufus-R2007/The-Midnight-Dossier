# THE MIDNIGHT DOSSIER
### *Every clue leaves a thread.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame-CE](https://img.shields.io/badge/Pygame--CE-2.5%2B-green.svg)](https://pyga.me/)
[![Course](https://img.shields.io/badge/DSA-Micro--Project-crimson.svg)](#course-outcomes-co-mapping)
[![Tests](https://img.shields.io/badge/Tests-46%20Passing-brightgreen.svg)](#running-automated-tests)

---

## 1. Project Overview

**The Midnight Dossier** is an atmospheric, interactive detective investigation game built in Python with Pygame, designed as a comprehensive showcase of Data Structures and Algorithms (DSA) for university-level evaluation.

Rather than presenting DSA concepts as abstract visualizers, every data structure and algorithm operates directly beneath genuine forensic investigation mechanics. The player takes the role of a consulting detective investigating **The Blackwood Heist**—the sudden theft of a priceless 14th-century artifact, the **Asterion Compass**, during a nine-minute security camera blackout at the Blackwood Museum.

### Signature Mechanics
* **Procedural Investigation Board:** Physical case-file evidence cards pinned to a dark corkboard, linked with blood-red catenary threads. Cards can be inspected and freely dragged to rearrange the board.
* **Real Graph Relationship Tracing:** Querying connections between any two entities runs a deterministic **Breadth-First Search (BFS)** across the case network, illuminating the exact relationship path with forensic citations.
* **Bidirectional Doubly Linked Timeline:** The chronological sequence of events is navigated via a custom **Doubly Linked List**, with real-time comparison between sequential pointer traversal and $O(\log n)$ binary search.
* **The Detective's Toolkit:** A dedicated in-game viva defense center with five interactive tabs demonstrating every Course Outcome (CO1 – CO5) on live case data with asymptotic complexity analyses.
* **Formal Indictment Engine:** Accuse a prime suspect and attach corroborating physical and digital records to receive an in-depth forensic verdict from the District Attorney.

---

## 2. Narrative Case Synopsis: The Blackwood Heist

* **The Incident:** At 21:47 on a rainy evening, circuit breaker #4 was manually tripped at the Blackwood Museum, disabling cameras across Gallery B and the Service Corridor for nine minutes. At 21:56, power was restored and the **Asterion Compass (EV-01)** was discovered missing from its alarmed glass vitrine.
* **The Four Suspects:**
  1. **Oliver Reed (Restoration Contractor):** Hired to repair gallery display cases. Claims he packed up and drove home in his work van at 21:30.
  2. **Evelyn Shaw (Museum Archivist):** Possesses master vault keys. Server logs show her account active during the blackout, but she claims she was on a tea break in the staff lounge.
  3. **Marcus Vale (Night Security Guard):** On duty in the Control Booth. Countersigned the contractor's work permit and attempted to reset the tripped breaker.
  4. **Dr. Lena Hart (Museum Curator):** Opposed sending the Compass to an overseas exhibition in Athens. Attended a symposium banquet downtown.
* **The Culprit:** Oliver Reed (`SUS-01`). His guilt is established through an unassailable evidentiary chain:
  * Work Order `MR-04` (`EV-02`) placed him near the circuit panel right before the blackout.
  * Electronic badge scan `KC-09` (`EV-04`) placed him in the Service Corridor at 21:49.
  * Serrated snips matching his restoration kit severed the vitrine alarm wire (`EV-07`).
  * A padded instrument case `IC-02` (`EV-05`) was used to conceal the artifact.
  * Barrier camera `VR-07` (`EV-06`) recorded his van exiting at 22:12, completely disproving his 21:30 alibi.
* *Note: Evelyn Shaw, Marcus Vale, and Dr. Lena Hart are supported by independent verifiable alibis and automated logs (see `docs/ALGORITHM_NOTES.md`).*

---

## 3. Course Outcomes (CO) Mapping

Every major Course Outcome is implemented as a custom, pure-Python ADT with zero third-party algorithm libraries:

| Course Outcome | Investigative Feature | Custom Data Structure / Algorithm | Source File | Asymptotic Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **CO1: Stacks & Queues** | Board Action Undo/Redo | `Stack[T]` (LIFO ADT) & `UndoRedoManager` | `midnight_dossier/dsa/stack.py` | Push: $O(1)$, Pop: $O(1)$, Peek: $O(1)$ |
| **CO1: Stacks & Queues** | Routine Lead Triage | `Queue[T]` (FIFO ADT) & `CircularQueue[T]` | `midnight_dossier/dsa/queue.py` | Enqueue: $O(1)$, Dequeue: $O(1)$ |
| **CO1: Stacks & Queues** | Urgent Lead Scheduling | `PriorityQueue[T]` (Max-Heap based) | `midnight_dossier/dsa/heap.py` | Peek: $O(1)$, Extract: $O(\log n)$ |
| **CO2: Storage & Retrieval** | Chronological Case Timeline | `DoublyLinkedList[T]` (Bidirectional ADT) | `midnight_dossier/dsa/linked_list.py` | Step: $O(1)$, Insert: $O(1)$, Search: $O(n)$ |
| **CO2: Storage & Retrieval** | Event Timestamp Search | Sequential Search vs. Binary Search | `midnight_dossier/timeline.py` | Seq: $O(n)$, Binary: $O(\log n)$ |
| **CO3: Search, Sort & Hash** | Evidence ID Indexing | `HashTable[K, V]` (Separate Chaining) | `midnight_dossier/dsa/hash_table.py` | Average: $O(1)$, Worst: $O(n)$ |
| **CO3: Search, Sort & Hash** | Sorting Benchmark | Bubble, Selection, Insertion, Merge Sort | `midnight_dossier/dsa/sorting.py` | Merge: $O(n \log n)$, Quadratic: $O(n^2)$ |
| **CO3: Search, Sort & Hash** | Value Searching | Linear, Binary, Interpolation Search | `midnight_dossier/dsa/searching.py` | Interp: $O(\log \log n)$ uniform |
| **CO4: Trees & Heaps** | Suspect Autocomplete | `Trie` (Prefix Tree ADT) | `midnight_dossier/dsa/trie.py` | Prefix Query: $O(L)$ string length |
| **CO4: Trees & Heaps** | Evidence Records & Traversal | `BinarySearchTree[K, V]` (3-case deletion) | `midnight_dossier/dsa/bst.py` | Average: $O(\log n)$, Inorder: $O(n)$ |
| **CO4: Trees & Heaps** | Transparent Priority Ranking | `MaxHeap[T]` (Array-based Binary Heap) | `midnight_dossier/dsa/heap.py` | Sift-Up/Down: $O(\log n)$, Heapify: $O(n)$ |
| **CO5: Graphs & Networks** | Shortest Relationship Chain | `Graph` (Adjacency List) & Breadth-First Search | `midnight_dossier/dsa/graph.py` | BFS Shortest Path: $O(V + E)$ |
| **CO5: Graphs & Networks** | Deep Exploration & Cycles | Depth-First Search (DFS) & Cycle Detection | `midnight_dossier/dsa/graph.py` | DFS Traversal: $O(V + E)$ |

*For complete academic viva documentation and demonstration steps, refer to [CO_MAPPING.md](docs/CO_MAPPING.md).*

---

## 4. UI & Art Direction

* **Noir Color Palette:**
  * Backgrounds: Midnight navy (`#0e1219`) and charcoal (`#141924`).
  * Corkboard: Procedurally textured slate-cork with dark grain speckling and inner vignetting.
  * Cards: Aged manila parchment (`#f5efe1`) with brass push-pins and drop shadows.
  * Strings: Muted blood-red threads (`#8c282d`) that pulse into glowing crimson-amber (`#ff4d5a`) when an investigative path is traced.
  * Badges: Desaturated teal for verified evidence, muted amber for unconfirmed claims, and gold for suspects.
* **Procedural Vector Silhouettes:** Suspect avatars (Archivist glasses, Guard officer cap, Curator coiffed hair, Contractor flat cap) are procedurally drawn with Pygame geometric primitives, avoiding external image dependencies.
* **Responsive Layout:** Designed for a reference resolution of $1366 \times 768$, with full support for dynamic window resizing (`pygame.RESIZABLE`).

---

## 5. Project Architecture

```
The-Midnight-Dossier/
├── main.py                     # Application entry point (desktop & smoke test modes)
├── requirements.txt            # Python package dependencies (pygame-ce)
├── README.md                   # Project overview, installation, and viva guide
├── docs/
│   ├── CO_MAPPING.md           # Formal Course Outcome mapping matrix and viva guide
│   └── ALGORITHM_NOTES.md      # Algorithm derivations, pseudocode, and case solution
├── midnight_dossier/
│   ├── __init__.py
│   ├── app.py                  # Window controller, header, navigation, and 60 FPS loop
│   ├── title_screen.py         # Cinematic title screen, animated threads, briefing & controls modals
│   ├── ui_components.py        # Synchronized interactive UI button components with hover states
│   ├── theme.py                # Color palette, font caching, procedural corkboard & silhouettes
│   ├── case_data.py            # 24 authored entities, 35+ relationships, timeline, and solution
│   ├── evidence_board.py       # Corkboard, draggable cards, catenary strings, and inspector
│   ├── investigation.py        # Query engine, theory manager, and progress metrics
│   ├── timeline.py             # Doubly linked list timeline & search comparison view
│   ├── toolkit.py              # Detective's Toolkit (CO1 to CO5 live demonstrations)
│   ├── accusation.py           # Formal indictment submission & forensic verdict modal
│   └── dsa/                    # Pure Python Custom Data Structures & Algorithms
│       ├── __init__.py
│       ├── stack.py            # Stack ADT & UndoRedoManager (CO1)
│       ├── queue.py            # FIFO Queue & CircularQueue ADT (CO1)
│       ├── linked_list.py      # DoublyLinkedList ADT (CO2)
│       ├── hash_table.py       # Separate-Chaining HashTable ADT (CO3)
│       ├── sorting.py          # Bubble, Selection, Insertion, Merge Sort (CO3)
│       ├── searching.py        # Linear, Binary, Interpolation Search (CO3)
│       ├── trie.py             # Trie Prefix Tree ADT (CO4)
│       ├── bst.py              # BinarySearchTree ADT with 3-case deletion (CO4)
│       ├── heap.py             # MaxHeap & PriorityQueue ADTs (CO1 / CO4)
│       ├── graph.py            # Adjacency-List Graph, BFS, and DFS (CO5)
│       └── benchmark.py        # Performance measurement harness
└── tests/
    ├── __init__.py
    ├── test_stack_queue.py     # Unit tests for Stack, Queue, CircularQueue, PriorityQueue
    ├── test_linked_list.py     # Unit tests for DoublyLinkedList operations and boundaries
    ├── test_hash_table.py      # Unit tests for HashTable collisions, updates, and buckets
    ├── test_sort_search.py     # Unit tests for all 4 sorting and 3 searching algorithms
    ├── test_trees_heap.py      # Unit tests for Trie autocomplete, BST traversals/deletions, MaxHeap
    ├── test_graph.py           # Unit tests for Graph adjacency, BFS shortest path, DFS cycles
    ├── test_case_logic.py      # Unit tests for case consistency, timeline order, and accusation scoring
    └── test_ui_components.py   # Unit tests for UI buttons, filters, views, and app lifecycle
```

---

## 6. Installation & Execution

### Prerequisites
* Python 3.10 or higher (Python 3.14 fully supported).
* Git (optional).

### Setup Instructions
1. Clone or open the repository directory:
   ```bash
   cd The-Midnight-Dossier
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the game:
   ```bash
   python main.py
   ```

4. Run Headless Smoke Test (Validates all screens and algorithms without opening a window):
   ```bash
   python main.py --smoke-test
   ```

---

## 7. Controls & Navigation

* **Mouse:**
  * **Title Screen:** Click `INVESTIGATE CASE` to start/continue, `HOW TO PLAY (GUIDE)` for detective field manual, `CASE BRIEFING` for incident report, `DETECTIVE'S TOOLKIT (DSA)` to inspect structures, or `CONTROLS & SHORTCUTS` for keyboard reference.
  * **Click Evidence Card:** Select and inspect full dossier in sidebar.
  * **Click & Drag Card:** Reposition cards on the corkboard (records undo action).
  * **Filter Tabs:** Toggle between `All`, `Suspects`, `Evidence`, and `Locations`.
  * **Direct Lead Neighbors:** Click on any related entity pill in the dossier sidebar to jump immediately to that card.
  * **Top Navigation Bar:** Jump between `Main Menu` (0), `Evidence Board` (1), `Case Timeline` (2), `Detective's Toolkit` (3), `Final Accusation` (4), and `How to Play` (H).
* **Keyboard Shortcuts:**
  * `0` or `Escape`: Navigate to **Main Menu / Title Screen**.
  * `1`: Navigate to **Investigation Board**.
  * `2`: Navigate to **Case Timeline**.
  * `3`: Navigate to **Detective's Toolkit**.
  * `4`: Navigate to **Final Accusation**.
  * `H` or `F1`: Open / Close **How to Play Guide** overlay anytime.
  * `Ctrl + Z`: Undo last card reposition or theory modification.
  * `Ctrl + Y`: Redo last undone action.
  * `Type in Search Field`: Live suspect/clue autocomplete powered by Trie.

---

## 8. Running Automated Tests

The automated test suite covers all custom data structures, edge cases (underflow, empty inputs, collisions, duplicate values, cycles), UI components, button callbacks, Trie autocomplete, and application game logic:

```bash
python -m unittest discover tests
```

Expected output:
```
Ran 56 tests in 0.045s
OK
```

---

## 9. Viva & Evaluation Guide (2-Minute Demonstration)

When demonstrating the project during a viva or project evaluation:

1. **Investigation Board (CO5 & CO4):**
   * Select **Oliver Reed** as source and **Antiquities Gallery** as target.
   * Click **Trace Connection Path (BFS)**. Point out that the path illuminates on the board and displays the shortest 2-edge connection with supporting evidence.
   * Type `"ol"` in the query search bar to demonstrate instant **Trie autocomplete**.
2. **Case Timeline (CO2):**
   * Click the **Case Timeline** navigation tab.
   * Click **< Previous** and **Next >** to show bidirectional step-by-step navigation via `prev` and `next` pointers.
   * Select preset **21:47 (Blackout)** in the search comparison panel to demonstrate sequential traversal ($O(n)$) vs. binary search ($O(\log n)$) on the indexed snapshot.
3. **Detective's Toolkit (CO1, CO3, CO4, CO5):**
   * Open the **Detective's Toolkit** tab.
   * **Tab 1 (CO1):** Demonstrate Push, Undo, and Redo on the live stack visualizer, followed by FIFO lead triage and Max-Heap priority extraction.
   * **Tab 3 (CO3):** Click evidence ID buttons (`EV-01`, `EV-04`, `EV-99`) to show separate chaining hash buckets and load factor, then click **Re-run Benchmark** to display real microsecond execution times for Bubble, Selection, Insertion, and Merge sorts.
   * **Tab 4 (CO4):** Probe BST keys to show search traversal hops and sorted inorder traversal.
4. **Final Accusation:**
   * Open **Final Accusation**. Select **Oliver Reed**.
   * Check off corroborating evidence: `EV-02` (Maintenance Request), `EV-04` (Keycard Scan), `EV-05` (Padded Case), and `EV-06` (Van Departure).
   * Click **Submit Formal Indictment** to reveal the comprehensive victory debrief and crime reconstruction.

---

## 10. Limitations & Future Improvements

* **Current Implementation:** Features one complete, meticulously authored mystery case (The Blackwood Heist) with 24 entities, 35+ relationships, and five full CO implementations.
* **Potential Future Extensions:**
  * Procedural generation of randomized secondary suspects and red herring alibis.
  * Multiple chapters with differing museum exhibits and security configurations.
  * Procedurally synthesized 8-bit ambient detective soundtrack using Pygame audio buffers.

---

## 11. Academic Declaration

This project was built to satisfy the university requirements for the Data Structures and Algorithms Micro-Project. All core data structures and algorithms in `midnight_dossier/dsa/` were implemented from first principles in readable, modular Python code.