"""
Unit tests for Interactive UI Components, Views, and Application State Transitions.
"""

import unittest
import os

# Use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

from midnight_dossier.ui_components import UIButton
from midnight_dossier.case_data import CaseData
from midnight_dossier.investigation import InvestigationState
from midnight_dossier.evidence_board import EvidenceBoardView
from midnight_dossier.timeline import CaseTimelineView
from midnight_dossier.toolkit import ToolkitView
from midnight_dossier.accusation import AccusationView
from midnight_dossier.app import MidnightDossierApp


class TestUIComponentsAndFlow(unittest.TestCase):
    def setUp(self):
        self.case_data = CaseData()
        self.state = InvestigationState(self.case_data)

    def test_ui_button_click_and_hover(self):
        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        btn = UIButton(pygame.Rect(10, 20, 100, 30), "Test", callback=on_click)
        self.assertTrue(btn.check_hover((20, 25)))
        self.assertFalse(btn.check_hover((200, 200)))

        # Simulate click
        evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (20, 25), "button": 1})
        self.assertTrue(btn.handle_event(evt))
        self.assertTrue(clicked)

        # Click outside
        clicked = False
        evt_out = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (200, 200), "button": 1})
        self.assertFalse(btn.handle_event(evt_out))
        self.assertFalse(clicked)

    def test_investigation_state_reset(self):
        self.state.mark_examined("EV-04")
        self.state.toggle_theory_evidence("EV-04")
        self.assertEqual(len(self.state.theory_evidence_ids), 1)

        self.state.reset()
        self.assertEqual(len(self.state.theory_evidence_ids), 0)
        self.assertTrue(self.state.undo_redo.undo_stack.is_empty())
        self.assertIn("EV-01", self.state.examined_entity_ids)
        self.assertIn("SUS-01", self.state.examined_entity_ids)

    def test_evidence_board_filters_and_layout(self):
        board = EvidenceBoardView(self.state)

        # Initial ALL filter
        card_sus = board.cards["SUS-01"]
        card_clue = board.cards["EV-01"]
        card_loc = board.cards["LOC-01"]

        self.assertTrue(board._is_card_visible(card_sus))
        self.assertTrue(board._is_card_visible(card_clue))
        self.assertTrue(board._is_card_visible(card_loc))

        # Filter: SUSPECTS
        board.set_filter("SUSPECTS")
        self.assertTrue(board._is_card_visible(card_sus))
        self.assertFalse(board._is_card_visible(card_clue))
        self.assertFalse(board._is_card_visible(card_loc))

        # Filter: EVIDENCE
        board.set_filter("EVIDENCE")
        self.assertFalse(board._is_card_visible(card_sus))
        self.assertTrue(board._is_card_visible(card_clue))

        # Move card and test reset layout
        card_sus.x += 100
        card_sus.y += 50
        self.assertNotEqual((card_sus.x, card_sus.y), card_sus.initial_pos)

        board.reset_layout()
        self.assertEqual((card_sus.x, card_sus.y), card_sus.initial_pos)

    def test_timeline_bidirectional_navigation(self):
        located_id = None

        def on_locate(eid):
            nonlocal located_id
            located_id = eid

        timeline = CaseTimelineView(self.state, on_locate_on_board=on_locate)
        first_event = timeline.current_node.data
        self.assertEqual(first_event["id"], "EVT-01")

        # Step next
        timeline._go_next()
        self.assertEqual(timeline.current_node.data["id"], "EVT-02")
        self.assertEqual(timeline.current_index, 1)

        # Step prev
        timeline._go_prev()
        self.assertEqual(timeline.current_node.data["id"], "EVT-01")
        self.assertEqual(timeline.current_index, 0)

        # Locate on board callback
        timeline._go_next()
        ev_id = timeline.current_node.data["evidence_id"]
        timeline.on_locate_on_board(ev_id)
        self.assertEqual(located_id, ev_id)

    def test_toolkit_tab_switching_and_live_actions(self):
        toolkit = ToolkitView(self.state)
        self.assertEqual(toolkit.active_tab, 0)

        # Switch to CO3
        toolkit._select_tab(2)
        self.assertEqual(toolkit.active_tab, 2)
        self.assertIn("CO3", toolkit.feedback_banner)

        # Test live hash probe
        toolkit._co3_probe_key("EV-04")
        self.assertIsNotNone(toolkit.co3_search_res)
        self.assertTrue(toolkit.co3_search_res["found"])
        self.assertEqual(toolkit.co3_search_res["key"], "EV-04")

        # Switch to CO5 and trace path
        toolkit._select_tab(4)
        toolkit._co5_trace("SUS-01", "LOC-04")
        self.assertTrue(toolkit.co5_bfs_res["found"])
        self.assertGreater(toolkit.co5_bfs_res["edge_count"], 0)

    def test_accusation_and_case_restart(self):
        restarted = False

        def on_restart():
            nonlocal restarted
            restarted = True

        acc = AccusationView(self.state, on_restart_case=on_restart)
        self.state.theory_evidence_ids = ["EV-02", "EV-04", "EV-05", "EV-06"]

        # Import theory
        acc._import_theory()
        self.assertIn("EV-02", acc.selected_evidence_ids)
        self.assertIn("EV-04", acc.selected_evidence_ids)

        # Submit accusation for Oliver Reed (SUS-01)
        acc.selected_suspect_id = "SUS-01"
        acc._submit_accusation()
        self.assertIsNotNone(acc.verdict_result)
        self.assertTrue(acc.verdict_result["is_solved"])
        self.assertEqual(acc.verdict_result["verdict"], "GUILTY")

        # Restart case
        acc._handle_case_restart()
        self.assertTrue(restarted)
        self.assertIsNone(acc.verdict_result)

    def test_app_lifecycle(self):
        app = MidnightDossierApp(width=1280, height=720)
        self.assertEqual(app.active_screen_idx, 0)  # Starts at Title Screen

        # Switch to board
        app.switch_screen(1)
        self.assertEqual(app.active_screen_idx, 1)

        # Locate entity switches to board and selects clue
        app.locate_entity_on_board("EV-06")
        self.assertEqual(app.active_screen_idx, 1)
        self.assertEqual(app.evidence_board.selected_card_id, "EV-06")
        self.assertTrue(app.investigation_state.is_examined("EV-06"))

        # Restart app
        app.restart_investigation()
        self.assertEqual(app.active_screen_idx, 1)
        self.assertEqual(app.evidence_board.selected_card_id, "SUS-01")

    def test_relationship_query_input_and_trie_search(self):
        board = EvidenceBoardView(self.state)
        sidebar_rect = pygame.Rect(1000, 54, 366, 714)

        # 1. Render sidebar so search_box_rect is populated
        dummy_surf = pygame.Surface((1366, 768))
        board._render_sidebar(dummy_surf, sidebar_rect)
        self.assertIsNotNone(board.search_box_rect)

        # 2. Click inside search box to activate focus
        sb_center = board.search_box_rect.center
        evt_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": sb_center, "button": 1})
        board.handle_event(evt_click, pygame.Rect(0, 54, 1000, 714), sidebar_rect)
        self.assertTrue(board.search_active)

        # 3. Type into search field
        board.handle_event(pygame.event.Event(pygame.TEXTINPUT, {"text": "ol"}), pygame.Rect(0, 54, 1000, 714), sidebar_rect)
        self.assertEqual(board.search_text, "ol")
        self.assertGreater(len(board.autocomplete_results), 0)
        top_name, top_meta = board.autocomplete_results[0]
        self.assertEqual(top_meta["id"], "SUS-01")

        # 4. Press Return to select top suggestion
        evt_return = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "unicode": "\r", "mod": 0})
        board.handle_event(evt_return, pygame.Rect(0, 54, 1000, 714), sidebar_rect)
        self.assertFalse(board.search_active)
        self.assertEqual(board.selected_card_id, "SUS-01")
        self.assertTrue(self.state.is_examined("SUS-01"))

        # 5. Query BFS path
        board.query_from_id = "SUS-01"
        board.query_to_id = "LOC-01"
        board.query_use_bfs = True
        board._run_trace_query()
        self.assertIsNotNone(self.state.last_query_result)
        self.assertTrue(self.state.last_query_result["found"])
        self.assertEqual(self.state.last_query_result["path"][0], "SUS-01")
        self.assertEqual(self.state.last_query_result["path"][-1], "LOC-01")

        # 6. Swap endpoints
        board._swap_endpoints()
        self.assertEqual(board.query_from_id, "LOC-01")
        self.assertEqual(board.query_to_id, "SUS-01")

        # 7. Clear query
        board._clear_trace_query()
        self.assertEqual(len(self.state.active_path), 0)
        self.assertIsNone(self.state.last_query_result)

    def test_case_file_dossier_controls_and_theory_toggle(self):
        board = EvidenceBoardView(self.state)
        sidebar_rect = pygame.Rect(1000, 54, 366, 714)
        dummy_surf = pygame.Surface((1366, 768))

        # Select evidence card EV-04
        board.selected_card_id = "EV-04"
        board._render_sidebar(dummy_surf, sidebar_rect)

        # Verify neighbor buttons exist
        self.assertGreater(len(board.neighbor_buttons), 0)
        first_btn, neighbor_id = board.neighbor_buttons[0]

        # Click the neighbor button to inspect connected lead
        evt_neighbor = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": first_btn.rect.center, "button": 1})
        board.handle_event(evt_neighbor, pygame.Rect(0, 54, 1000, 714), sidebar_rect)
        self.assertEqual(board.selected_card_id, neighbor_id)
        self.assertTrue(self.state.is_examined(neighbor_id))

        # Select EV-02 and test Add to Theory button
        board.selected_card_id = "EV-02"
        board._render_sidebar(dummy_surf, sidebar_rect)
        self.assertFalse(self.state.is_in_theory("EV-02"))

        board._toggle_current_theory()
        self.assertTrue(self.state.is_in_theory("EV-02"))
        self.assertEqual(len(self.state.theory_evidence_ids), 1)

        # Toggle again to remove
        board._toggle_current_theory()
        self.assertFalse(self.state.is_in_theory("EV-02"))
        self.assertEqual(len(self.state.theory_evidence_ids), 0)

        # Undo restores theory
        board._perform_undo()
        self.assertTrue(self.state.is_in_theory("EV-02"))

    def test_how_to_play_guide_modal(self):
        closed = False

        def on_close():
            nonlocal closed
            closed = True

        from midnight_dossier.how_to_play import HowToPlayView
        guide = HowToPlayView(on_close=on_close)
        self.assertEqual(len(guide.steps), 6)
        self.assertGreater(len(guide.controls), 5)

        # Test close button
        guide.handle_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}),
            pygame.Rect(0, 0, 1280, 720)
        )
        self.assertTrue(closed)

        # Test app toggle
        app = MidnightDossierApp(width=1280, height=720)
        self.assertFalse(app.show_how_to_play)
        app.toggle_how_to_play(True)
        self.assertTrue(app.show_how_to_play)
        app.toggle_how_to_play(False)
        self.assertFalse(app.show_how_to_play)


if __name__ == "__main__":
    unittest.main()
