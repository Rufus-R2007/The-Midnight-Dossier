"""
THE MIDNIGHT DOSSIER: Every clue leaves a thread.
An interactive detective mystery game powered by Data Structures and Algorithms.

Application Entry Point.
"""

import sys
import os

# Ensure the project directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    # Check for headless smoke test mode
    if "--smoke-test" in sys.argv:
        print("[Smoke Test] Initializing Midnight Dossier in headless validation mode...")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from midnight_dossier.app import MidnightDossierApp
        import pygame

        app = MidnightDossierApp(width=1366, height=768)
        print("[Smoke Test] App instantiated successfully.")

        # Test switching across all screens (0: Title, 1: Board, 2: Timeline, 3: Toolkit, 4: Accusation)
        for screen_idx in range(5):
            app.active_screen_idx = screen_idx
            app._update(0.016)
            app._render()
            print(f"[Smoke Test] Screen #{screen_idx} rendered without error.")

        # Test query execution in headless mode
        res = app.investigation_state.query_relationship("SUS-01", "EV-01", use_bfs=True)
        print(f"[Smoke Test] BFS path trace verified: {res['found']} (Edges: {res['edge_count']})")

        # Test case restart
        app.restart_investigation()
        print("[Smoke Test] Case restart execution verified cleanly.")

        pygame.quit()
        print("[Smoke Test] All checks passed successfully.")
        return

    # Normal desktop launch
    from midnight_dossier.app import MidnightDossierApp
    app = MidnightDossierApp(width=1366, height=768)
    app.run()


if __name__ == "__main__":
    main()
