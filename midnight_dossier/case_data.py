"""
Authored Case Data: The Blackwood Heist.
Case 001 - The Theft of the Asterion Compass.

Contains:
- Suspects (4)
- Artifact (1)
- Locations (6)
- Clues / Evidence (14)
- Events / Timeline (10)
- Investigative Relationships (35+)
- Solution & Corroborating Logic
"""

from typing import Dict, List, Any, Optional
from .dsa.graph import Graph
from .dsa.hash_table import HashTable
from .dsa.linked_list import DoublyLinkedList
from .dsa.trie import Trie
from .dsa.bst import BinarySearchTree
from .dsa.heap import MaxHeap, PriorityQueue
from .dsa.queue import Queue


# ==============================================================================
# 1. ENTITY DEFINITIONS
# ==============================================================================

SUSPECTS = [
    {
        "id": "SUS-01",
        "name": "Oliver Reed",
        "role": "Restoration Contractor",
        "description": "Freelance metalsmith and antique restorer hired to refurbish gallery showcases. Had after-hours access credentials.",
        "alibi": "Claims he left the museum at 21:30 after packing tools, heading straight home in his work van.",
        "avatar_type": "contractor",
        "is_culprit": True,
    },
    {
        "id": "SUS-02",
        "name": "Evelyn Shaw",
        "role": "Museum Archivist",
        "description": "Senior curator of records with master keycard privileges and access to the basement vault.",
        "alibi": "Claims she was taking an evening tea break in the staff lounge from 21:30 until 22:10.",
        "avatar_type": "archivist",
        "is_culprit": False,
    },
    {
        "id": "SUS-03",
        "name": "Marcus Vale",
        "role": "Night Security Guard",
        "description": "Veteran watchman on duty in the main security booth. In charge of the camera feeds and gate controls.",
        "alibi": "States he was at the security console trying to reboot the circuit breaker when the camera monitors went black.",
        "avatar_type": "guard",
        "is_culprit": False,
    },
    {
        "id": "SUS-04",
        "name": "Dr. Lena Hart",
        "role": "Museum Curator",
        "description": "Director of antiquities who opposed sending the Asterion Compass to an overseas exhibition.",
        "alibi": "Attended an archaeological symposium dinner downtown starting at 21:00.",
        "avatar_type": "curator",
        "is_culprit": False,
    },
]

LOCATIONS = [
    {
        "id": "LOC-01",
        "name": "Antiquities Gallery",
        "category": "Crime Scene",
        "description": "Central exhibition hall where the Asterion Compass was displayed inside an alarmed glass vitrine.",
    },
    {
        "id": "LOC-02",
        "name": "Security Control Booth",
        "category": "Facility",
        "description": "Monitors all 32 CCTV feeds, keycard logs, and alarm triggers. Located by the main entrance.",
    },
    {
        "id": "LOC-03",
        "name": "Service Corridor",
        "category": "Access Way",
        "description": "Unmonitored back hallway linking the conservation workshop, loading bay, and gallery back door.",
    },
    {
        "id": "LOC-04",
        "name": "Loading Bay Dock",
        "category": "Exit Point",
        "description": "Heavy industrial roller door used for delivery vans and equipment transport.",
    },
    {
        "id": "LOC-05",
        "name": "Archive Basement Vault",
        "category": "Storage",
        "description": "Climate-controlled repository storing historical deeds, accession catalogs, and spare keys.",
    },
    {
        "id": "LOC-06",
        "name": "Staff Tea Room",
        "category": "Rest Area",
        "description": "Break area on the mezzanine level overlooking the courtyard with a digital clock and coffee machine.",
    },
]

EVIDENCE_ITEMS = [
    {
        "id": "EV-01",
        "name": "Asterion Compass (Stolen)",
        "category": "Artifact",
        "source": "Display Pedestal Vitrine",
        "timestamp": "21:56 (Discovered Missing)",
        "reliability": "VERIFIED",
        "priority": 95,
        "description": "14th-century brass navigational masterpiece with celestial engravings. Value estimated at 2.4 million.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-02",
        "name": "Maintenance Request MR-04",
        "category": "Official Record",
        "source": "Facilities Work Order Database",
        "timestamp": "21:42",
        "reliability": "VERIFIED",
        "priority": 90,
        "description": "Work order submitted by Oliver Reed requesting an urgent camera recalibration in Gallery B right before the blackout.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-03",
        "name": "CCTV Control Switch Glitch Log",
        "category": "Digital Log",
        "source": "Security Server Event Logger",
        "timestamp": "21:47 - 21:56",
        "reliability": "VERIFIED",
        "priority": 85,
        "description": "Nine-minute blackout across Gallery B and Corridor C caused by a manual breaker trip, not a remote cyberattack.",
        "importance": "HIGH",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-04",
        "name": "Keycard KC-09 Service Scan",
        "category": "Security Log",
        "source": "Electronic Door Controller #4",
        "timestamp": "21:49",
        "reliability": "VERIFIED",
        "priority": 92,
        "description": "Contractor Badge #09 (issued to Oliver Reed) opened the restricted Service Corridor door during the blackout.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-05",
        "name": "Missing Instrument Case IC-02",
        "category": "Inventory Audit",
        "source": "Workshop Tool Registry",
        "timestamp": "22:05",
        "reliability": "VERIFIED",
        "priority": 88,
        "description": "A velvet-lined padded instrument case brought in by the contractor was missing from the workshop locker.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-06",
        "name": "Van Departure Log VR-07",
        "category": "Gate Record",
        "source": "Automated Barrier Camera",
        "timestamp": "22:12",
        "reliability": "VERIFIED",
        "priority": 86,
        "description": "Oliver Reed's restoration van exited the loading bay barrier at 22:12, despite his claim of leaving at 21:30.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-07",
        "name": "Pedestal Wire Cut Forensic Analysis",
        "category": "Forensic Physical",
        "source": "Crime Scene Investigation",
        "timestamp": "23:15",
        "reliability": "VERIFIED",
        "priority": 89,
        "description": "The vitrine alarm wire was severed with serrated micro-snips specific to high-tensile antique restoration toolsets.",
        "importance": "CRITICAL",
        "corroborates_culprit": True,
    },
    {
        "id": "EV-08",
        "name": "Archive Catalog Sync Script",
        "category": "Server Digital Log",
        "source": "Museum Data Server #2",
        "timestamp": "21:50",
        "reliability": "VERIFIED",
        "priority": 60,
        "description": "Server cronjob executed an automated catalog backup under Evelyn Shaw's username. No physical terminal inputs.",
        "importance": "EXCULPATORY",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-09",
        "name": "Staff Tea Room Witness Testimony",
        "category": "Witness Statement",
        "source": "Janitorial Staff Interview",
        "timestamp": "21:35 - 22:05",
        "reliability": "TESTIMONY",
        "priority": 55,
        "description": "Two night custodians confirm Evelyn Shaw was in the tea room drinking chamomile tea continuously during the blackout.",
        "importance": "EXCULPATORY",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-10",
        "name": "Breaker Reset Security Radio Audio",
        "category": "Audio Record",
        "source": "Security Dispatch Tape #8",
        "timestamp": "21:52",
        "reliability": "TESTIMONY",
        "priority": 65,
        "description": "Marcus Vale's radio transmission reporting the camera breaker trip while requesting instructions from central control.",
        "importance": "EXCULPATORY",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-11",
        "name": "Guard Maintenance Permit Signature",
        "category": "Document Record",
        "source": "Security Logbook",
        "timestamp": "21:40",
        "reliability": "VERIFIED",
        "priority": 70,
        "description": "Marcus Vale countersigned Oliver Reed's routine maintenance permit as required by museum standing procedure.",
        "importance": "CIRCUMSTANTIAL",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-12",
        "name": "Symposium Dinner Bill & Highway Toll",
        "category": "Financial Record",
        "source": "Bank Statement & Highway Transponder",
        "timestamp": "21:15 - 22:30",
        "reliability": "VERIFIED",
        "priority": 50,
        "description": "Dr. Lena Hart's vehicle toll at 21:05 and restaurant credit receipt at 21:48 confirm she was 18 miles away downtown.",
        "importance": "EXCULPATORY",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-13",
        "name": "Curator Overseas Loan Dispute Memo",
        "category": "Correspondence Memo",
        "source": "Curator Office Desk",
        "timestamp": "09:30 (Morning of Incident)",
        "reliability": "UNCONFIRMED",
        "priority": 45,
        "description": "Memo revealing Dr. Hart strongly opposed moving the Compass to Athens, creating a potential motive for concealment.",
        "importance": "RED_HERRING",
        "corroborates_culprit": False,
    },
    {
        "id": "EV-14",
        "name": "Master Key Override Protocol",
        "category": "Policy Manual",
        "source": "Security Vault Procedures",
        "timestamp": "Standard Operating Document",
        "reliability": "VERIFIED",
        "priority": 40,
        "description": "Physical master keys remain sealed in the security safe; neither keys nor locks showed signs of picking.",
        "importance": "CIRCUMSTANTIAL",
        "corroborates_culprit": False,
    },
]

TIMELINE_EVENTS = [
    {
        "id": "EVT-01",
        "timestamp": "21:15",
        "time_minutes": 1275,  # 21 * 60 + 15
        "title": "Dr. Lena Hart arrives downtown",
        "location": "Downtown Bistro",
        "description": "Curator attends archaeological symposium banquet 18 miles from the museum.",
        "evidence_id": "EV-12",
        "related_person": "Dr. Lena Hart",
    },
    {
        "id": "EVT-02",
        "timestamp": "21:30",
        "time_minutes": 1290,
        "title": "Evelyn Shaw begins evening break",
        "location": "Staff Tea Room",
        "description": "Archivist enters staff lounge on mezzanine level; confirmed by night cleaning staff.",
        "evidence_id": "EV-09",
        "related_person": "Evelyn Shaw",
    },
    {
        "id": "EVT-03",
        "timestamp": "21:35",
        "time_minutes": 1295,
        "title": "Oliver Reed signs in at service desk",
        "location": "Service Corridor",
        "description": "Contractor checks in with tool trolley and padded instrument case IC-02.",
        "evidence_id": "EV-05",
        "related_person": "Oliver Reed",
    },
    {
        "id": "EVT-04",
        "timestamp": "21:40",
        "time_minutes": 1300,
        "title": "Marcus Vale signs maintenance permit",
        "location": "Security Control Booth",
        "description": "Guard signs contractor permit MR-04 for camera recalibration in Gallery B.",
        "evidence_id": "EV-11",
        "related_person": "Marcus Vale",
    },
    {
        "id": "EVT-05",
        "timestamp": "21:47",
        "time_minutes": 1307,
        "title": "CCTV blackout begins",
        "location": "Antiquities Gallery",
        "description": "Circuit breaker #4 trips; video feed to monitors in Security Booth drops out.",
        "evidence_id": "EV-03",
        "related_person": "Oliver Reed",
    },
    {
        "id": "EVT-06",
        "timestamp": "21:49",
        "time_minutes": 1309,
        "title": "Service corridor door opened",
        "location": "Service Corridor",
        "description": "Contractor keycard KC-09 scans into Antiquities Gallery rear access during blackout.",
        "evidence_id": "EV-04",
        "related_person": "Oliver Reed",
    },
    {
        "id": "EVT-07",
        "timestamp": "21:50",
        "time_minutes": 1310,
        "title": "Automated catalog sync script runs",
        "location": "Archive Basement Vault",
        "description": "Scheduled database sync runs under Evelyn's account without human terminal input.",
        "evidence_id": "EV-08",
        "related_person": "Evelyn Shaw",
    },
    {
        "id": "EVT-08",
        "timestamp": "21:52",
        "time_minutes": 1312,
        "title": "Marcus attempts breaker reset",
        "location": "Security Control Booth",
        "description": "Guard attempts manual reboot and radios dispatch regarding power irregularity.",
        "evidence_id": "EV-10",
        "related_person": "Marcus Vale",
    },
    {
        "id": "EVT-09",
        "timestamp": "21:56",
        "time_minutes": 1316,
        "title": "CCTV restored; compass missing",
        "location": "Antiquities Gallery",
        "description": "Monitors restore video feed. Pedestal glass is ajar; Asterion Compass is missing.",
        "evidence_id": "EV-01",
        "related_person": "Oliver Reed",
    },
    {
        "id": "EVT-10",
        "timestamp": "22:12",
        "time_minutes": 1332,
        "title": "Contractor van departs loading bay",
        "location": "Loading Bay Dock",
        "description": "Oliver Reed's van departs museum perimeter, 42 minutes later than claimed alibi.",
        "evidence_id": "EV-06",
        "related_person": "Oliver Reed",
    },
]

RELATIONSHIPS = [
    # Oliver Reed relationships (culprit chain)
    ("SUS-01", "EV-02", "SUBMITTED", "Oliver initiated maintenance request MR-04 right before outage.", "EV-02", "VERIFIED"),
    ("EV-02", "EV-03", "TRIGGERS", "Work order permitted access to circuit panel where breaker tripped.", "EV-03", "VERIFIED"),
    ("SUS-01", "EV-04", "BADGE_HOLDER", "Badge KC-09 issued to Oliver Reed scanned during blackout.", "EV-04", "VERIFIED"),
    ("EV-04", "LOC-03", "UNLOCKED", "Badge KC-09 granted entry through the Service Corridor door.", "EV-04", "VERIFIED"),
    ("LOC-03", "LOC-01", "CONNECTS_TO", "Service corridor provides direct unmonitored rear door to Antiquities Gallery.", "EV-04", "VERIFIED"),
    ("SUS-01", "EV-05", "OWNED_EQUIPMENT", "Padded instrument case IC-02 brought on-site by Oliver is missing.", "EV-05", "VERIFIED"),
    ("EV-05", "EV-01", "CONCEALED", "Dimensions of padded case IC-02 precisely fit the Asterion Compass.", "EV-05", "INFERRED"),
    ("SUS-01", "EV-06", "OPERATED_VEHICLE", "Oliver Reed's restoration van logged leaving at 22:12.", "EV-06", "VERIFIED"),
    ("EV-06", "LOC-04", "DEPARTED_FROM", "Vehicle departed through the Loading Bay Dock perimeter barrier.", "EV-06", "VERIFIED"),
    ("SUS-01", "EV-07", "MATCHING_TOOL", "Serrated micro-snips used on pedestal alarm match Oliver's restoration kit.", "EV-07", "VERIFIED"),
    ("EV-07", "EV-01", "SEVERED_ALARM", "Alarm wire was severed directly underneath the Compass display pedestal.", "EV-07", "VERIFIED"),
    ("SUS-01", "EV-06", "CONTRADICTS_ALIBI", "Van departure at 22:12 directly disproves claim of leaving at 21:30.", "EV-06", "CONTRADICTORY"),

    # Evelyn Shaw relationships (red herring chain)
    ("SUS-02", "EV-08", "LOGGED_CREDENTIAL", "Archive account used for automated server catalog sync.", "EV-08", "VERIFIED"),
    ("EV-08", "LOC-05", "ACCESSED_SYSTEM", "Sync script updated database records for Archive Basement Vault.", "EV-08", "VERIFIED"),
    ("EV-08", "SUS-02", "EXPLAINS_PRESENCE", "System log confirms routine cronjob ran without manual user presence.", "EV-08", "VERIFIED"),
    ("SUS-02", "EV-09", "CORROBORATES_ALIBI", "Staff witness statements place Evelyn in Tea Room continuously.", "EV-09", "TESTIMONY"),
    ("EV-09", "LOC-06", "LOCATED_AT", "Evelyn remained inside Staff Tea Room during theft window.", "EV-09", "TESTIMONY"),

    # Marcus Vale relationships (red herring chain)
    ("SUS-03", "EV-11", "COUNTERSIGNED", "Marcus signed the routine maintenance request submitted by Oliver.", "EV-11", "VERIFIED"),
    ("EV-11", "EV-02", "AUTHORIZED", "Signed permit authorized Oliver's presence near electrical switchboard.", "EV-11", "VERIFIED"),
    ("SUS-03", "EV-10", "TRANSMITTED_RADIO", "Audio logs confirm Marcus reported outage and attempted breaker reset.", "EV-10", "TESTIMONY"),
    ("EV-10", "LOC-02", "RECORDED_AT", "Marcus stayed at Security Control Booth console attempting recovery.", "EV-10", "VERIFIED"),
    ("SUS-03", "EV-14", "FOLLOWED_PROTOCOL", "Standard operating protocol followed for key safe and logbook entries.", "EV-14", "VERIFIED"),

    # Dr. Lena Hart relationships (red herring chain)
    ("SUS-04", "EV-13", "AUTHORED_MEMO", "Memo shows Lena opposed loaning Compass to overseas institution.", "EV-13", "UNCONFIRMED"),
    ("EV-13", "EV-01", "SUBJECT_OF_MEMO", "Memo concerned the preservation and loan of Asterion Compass.", "EV-13", "UNCONFIRMED"),
    ("SUS-04", "EV-12", "CORROBORATES_ALIBI", "Toll pass and dinner bill prove curator was 18 miles away downtown.", "EV-12", "VERIFIED"),

    # Physical layout and artifact links
    ("LOC-01", "EV-01", "DISPLAY_SITE", "Antiquities Gallery housed the Asterion Compass vitrine.", "EV-01", "VERIFIED"),
    ("LOC-02", "LOC-01", "MONITORED_BY", "Security Booth monitored Gallery B prior to camera outage.", "EV-03", "VERIFIED"),
    ("LOC-04", "LOC-03", "ADJACENT_TO", "Loading bay connects directly to service corridor for freight delivery.", "EV-06", "VERIFIED"),
]


# ==============================================================================
# 2. CASE DATA ENGINE & BUILDER
# ==============================================================================

class CaseData:
    """
    Central repository for all authored case entities, graph networks,
    hash indexes, timeline doubly linked list, trie autocomplete, and BST records.
    """

    def __init__(self) -> None:
        self.suspects: List[dict] = list(SUSPECTS)
        self.locations: List[dict] = list(LOCATIONS)
        self.evidence: List[dict] = list(EVIDENCE_ITEMS)
        self.timeline_events: List[dict] = list(TIMELINE_EVENTS)
        self.relationships: List[tuple] = list(RELATIONSHIPS)

        # Build pure DSA structures
        self.graph = Graph()
        self.evidence_hash_table = HashTable[str, dict](capacity=17)
        self.timeline_dll = DoublyLinkedList[dict]()
        self.autocomplete_trie = Trie()
        self.evidence_bst = BinarySearchTree[str, dict]()
        self.urgent_leads_heap = MaxHeap[dict](key=lambda x: x["priority"])
        self.routine_leads_queue = Queue[dict]()

        self._populate_dsa_structures()

    def reset(self) -> None:
        """Reset all DSA structures to clean authored state."""
        self.graph = Graph()
        self.evidence_hash_table = HashTable[str, dict](capacity=17)
        self.timeline_dll = DoublyLinkedList[dict]()
        self.autocomplete_trie = Trie()
        self.evidence_bst = BinarySearchTree[str, dict]()
        self.urgent_leads_heap = MaxHeap[dict](key=lambda x: x["priority"])
        self.routine_leads_queue = Queue[dict]()
        self._populate_dsa_structures()

    def _populate_dsa_structures(self) -> None:
        """Populate custom DSA structures from authored case data."""
        # 1. Graph nodes
        for s in self.suspects:
            self.graph.add_node(s["id"], s["name"], "suspect", metadata=s)
            self.autocomplete_trie.insert(s["name"], metadata={"id": s["id"], "type": "suspect"})

        for loc in self.locations:
            self.graph.add_node(loc["id"], loc["name"], "location", metadata=loc)
            self.autocomplete_trie.insert(loc["name"], metadata={"id": loc["id"], "type": "location"})

        for ev in self.evidence:
            self.graph.add_node(ev["id"], ev["name"], "clue", metadata=ev)
            self.autocomplete_trie.insert(ev["name"], metadata={"id": ev["id"], "type": "clue"})

            # Hash table indexing by ID (e.g. EV-01)
            self.evidence_hash_table.insert(ev["id"], ev)

            # BST indexing by ID
            self.evidence_bst.insert(ev["id"], ev)

            # Initial Leads Queues
            if ev["priority"] >= 80:
                self.urgent_leads_heap.insert(ev)
            else:
                self.routine_leads_queue.enqueue(ev)

        # 2. Graph edges
        for u, v, rel_type, explanation, ev_id, reliability in self.relationships:
            self.graph.add_edge(u, v, rel_type, explanation, ev_id, reliability, bidirectional=True)

        # 3. Timeline Doubly Linked List
        for event in self.timeline_events:
            self.timeline_dll.append(event)

    def get_entity_by_id(self, entity_id: str) -> Optional[dict]:
        """Look up entity from suspects, evidence, or locations."""
        if entity_id.startswith("EV-"):
            return self.evidence_hash_table.search(entity_id)
        for s in self.suspects:
            if s["id"] == entity_id:
                return s
        for loc in self.locations:
            if loc["id"] == entity_id:
                return loc
        return None

    def get_all_entities(self) -> List[dict]:
        """Return unified list of all case entities."""
        items: List[dict] = []
        for s in self.suspects:
            items.append({"id": s["id"], "name": s["name"], "type": "suspect", "raw": s})
        for ev in self.evidence:
            items.append({"id": ev["id"], "name": ev["name"], "type": "clue", "raw": ev})
        for loc in self.locations:
            items.append({"id": loc["id"], "name": loc["name"], "type": "location", "raw": loc})
        return items

    def evaluate_accusation(self, accused_suspect_id: str, selected_evidence_ids: List[str]) -> dict:
        """
        Evaluate detective accusation against case facts.
        Culprit: Oliver Reed (SUS-01).
        Key Corroborating Clues:
          - EV-02: Maintenance Request MR-04 (Blackout trigger)
          - EV-04: Keycard KC-09 Service Scan (Corridor presence)
          - EV-05: Missing Instrument Case IC-02 (Concealment)
          - EV-06: Van Departure Log VR-07 (Alibi contradiction)
          - EV-07: Pedestal Wire Cut (Tool match)
        """
        suspect = next((s for s in self.suspects if s["id"] == accused_suspect_id), None)
        if not suspect:
            return {
                "verdict": "ERROR",
                "title": "Invalid Suspect",
                "message": "No valid suspect was selected for formal accusation.",
                "is_solved": False,
            }

        # Identify submitted corroborating clues
        key_clues = {"EV-02", "EV-04", "EV-05", "EV-06", "EV-07"}
        matching_clues = set(selected_evidence_ids).intersection(key_clues)
        clue_count = len(matching_clues)

        if suspect["is_culprit"]:
            if clue_count >= 3:
                return {
                    "verdict": "GUILTY",
                    "title": "CASE SOLVED — WARRANT ISSUED",
                    "suspect_name": suspect["name"],
                    "is_solved": True,
                    "clue_count": clue_count,
                    "message": (
                        f"Oliver Reed was arrested at his workshop with the Asterion Compass safely recovered! "
                        f"Your investigation established an unassailable evidentiary chain: "
                        f"1) Maintenance Request MR-04 permitted him access to trip the gallery circuit breaker. "
                        f"2) Keycard scan KC-09 placed his badge in the restricted service corridor at 21:49 during the blackout. "
                        f"3) Serrated cuts on the vitrine alarm wire matched his specialist restoration tools. "
                        f"4) Padded case IC-02 was used to transport the compass undetected. "
                        f"5) Loading bay gate log VR-07 shattered his 21:30 alibi by proving his van exited at 22:12. "
                        f"The District Attorney commended your thorough forensic corroboration."
                    ),
                    "score": 100 if clue_count >= 4 else 85,
                }
            else:
                return {
                    "verdict": "INSUFFICIENT_EVIDENCE",
                    "title": "CASE DISMISSED — INSUFFICIENT PROBABLE CAUSE",
                    "suspect_name": suspect["name"],
                    "is_solved": False,
                    "clue_count": clue_count,
                    "message": (
                        f"You correctly suspected {suspect['name']}, but presented only {clue_count} corroborating piece(s) of evidence. "
                        f"The magistrate dismissed the warrant, citing insufficient physical proof and uncorroborated timeline gaps. "
                        f"A successful prosecution requires linking access records (KC-09), maintenance orders (MR-04), "
                        f"tool markings, and the loading bay departure log (VR-07)."
                    ),
                    "score": 40,
                }
        else:
            # Wrong suspect exoneration details
            exoneration_details = {
                "SUS-02": (
                    "Evelyn Shaw is innocent. While her database credentials appeared during the outage (EV-08), "
                    "system logs confirm this was an automated scheduled catalog sync script. Two night custodians "
                    "and tea room cameras confirmed she was on break continuously from 21:30 to 22:10 (EV-09)."
                ),
                "SUS-03": (
                    "Marcus Vale is innocent. While he countersigned the maintenance permit (EV-11), security dispatch tapes "
                    "and control booth logs (EV-10) confirm he remained at the console trying to reset breaker #4 and "
                    "contacting central authorities according to standard museum protocols."
                ),
                "SUS-04": (
                    "Dr. Lena Hart is innocent. Although she authored a contentious memo opposing the overseas exhibition (EV-13), "
                    "highway transponder records and downtown restaurant payment receipts (EV-12) definitively place her 18 miles "
                    "away during the 21:47–21:56 theft window."
                ),
            }
            return {
                "verdict": "WRONGFUL_ACCUSATION",
                "title": "FALSE ARREST — INNOCENT PARTY ACCUSED",
                "suspect_name": suspect["name"],
                "is_solved": False,
                "clue_count": clue_count,
                "message": exoneration_details.get(
                    suspect["id"],
                    f"{suspect['name']} was exonerated by verifiable alibis and digital logs."
                ),
                "score": 15,
            }
