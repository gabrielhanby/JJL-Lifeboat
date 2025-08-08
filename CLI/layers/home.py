# cli/layers/home.py
from typing import Dict, Any, Tuple, Optional, List
from ..ui.table_manager import TableManager
from ..ui.ui import clear_screen
from ..ui.hud import ensure_and_set_hud
from ..src.input import parse, route_shared
from ..src.ladder import Ladder

SYSTEM_TABLE = "system"
HUD_TABLE    = "lastio"
WIDTH = 71

# Public commands dict for this layer (Help will read this)
COMMANDS: Dict[str, str] = {
    "Help": "Open the Help screen.",
    "Exit": "Ask to terminate the application (if not on the root layer, behaves like Back).",
    "Exit All": "Ask to terminate the application from any layer.",
}

class HomeLayer:
    def __init__(self):
        self.tm = TableManager()
        # Banner table: System / Ladder / Active
        self.tm.build(SYSTEM_TABLE, WIDTH, ["Carpathia", "Ladder", "Home"])
        # HUD table for Last Input / Output (word-wrapped)
        self.tm.build(HUD_TABLE, WIDTH, ["Last Input", "Last Output"])

    # System-wide common commands (left column of banner)
    def _system_commands(self) -> List[str]:
        return ["Help", "Back", "Forth", "Exit", "Exit All"]

    # Active layer’s quick commands (right column of banner)
    def _active_commands(self) -> List[str]:
        # show only the command names in the banner
        return list(COMMANDS.keys())

    def render(self, ladder: Ladder, last_in: str, last_out: str) -> None:
        clear_screen()

        # ----- Banner: System / Ladder / Active (no wrap) -----
        self.tm.set_headers(SYSTEM_TABLE, ["Carpathia", "Ladder", "Home"])

        system_col = self._system_commands()
        ladder_col = ladder.as_vertical()
        active_col = self._active_commands()

        max_rows = max(len(system_col), len(ladder_col), len(active_col))
        banner_rows: List[List[Optional[str]]] = []
        for i in range(max_rows):
            sys_cell = system_col[i] if i < len(system_col) else ""
            lad_cell = ladder_col[i] if i < len(ladder_col) else ""
            act_cell = active_col[i] if i < len(active_col) else ""
            banner_rows.append([sys_cell, lad_cell, act_cell])

        # No wrapping for the banner
        self.tm.set_rows(SYSTEM_TABLE, banner_rows, wrap_text=False)

        # ----- HUD: Last Input / Last Output (wrapped) -----
        ensure_and_set_hud(
            self.tm,
            name=HUD_TABLE,
            total_width=WIDTH,
            left_text=last_in,
            right_text=last_out,
        )

        # Draw both tables
        self.tm.draw_many([SYSTEM_TABLE, HUD_TABLE])

    def handle_input(
        self,
        text: str,
        ladder: Ladder,
        globals_dict: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        token, orig = parse(text)

        # shared navigation + layer calls
        layer_names = globals_dict.get("layer_names", ["Home", "Help"])
        action, msg = route_shared(token, orig, ladder, layer_names, current_layer="Home")
        if action:
            return action, msg

        # (Optional) custom Home-specific commands would go here

        return "redraw", f"Unknown command: {orig or ''}"
