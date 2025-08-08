# cli/layers/help.py
from typing import Dict, Any, Tuple, Optional, List
from ..ui.table_manager import TableManager
from ..ui.ui import clear_screen
from ..src.input import parse, route_shared
from ..src.ladder import Ladder

HELP_TABLE = "help"
WIDTH = 71

# Public commands dict for this layer (so Help can show itself if needed)
COMMANDS: Dict[str, str] = {
    "Back": "Return to the previous layer in the ladder.",
    "Forth": "Move forward to the next layer in the ladder.",
    "Exit": "Ask to terminate the application (if not on Home, acts like Back).",
    "Exit All": "Ask to terminate the application from any layer.",
}

# System-wide commands with use cases
SYSTEM_COMMANDS: Dict[str, str] = {
    "Help": "Display this help screen with system and layer-specific commands.",
    "Back": "Move to the layer directly below the current one in the ladder.",
    "Forth": "Move to the layer directly above the current one in the ladder.",
    "Exit": "Ask to terminate the application (acts like Back unless on Home).",
    "Exit All": "Prompt to terminate the application from any layer.",
}

class HelpLayer:
    def __init__(self):
        self.tm = TableManager()
        self.tm.build(HELP_TABLE, WIDTH, ["Commands", "Explanation"])
        self._layers_ref: Optional[Dict[str, Any]] = None  # cached from handle_input

    def _prev_layer_commands(self, ladder: Ladder) -> Dict[str, str]:
        """Return COMMANDS dict for the layer one index down, if available."""
        # active index is ladder.idx; previous layer exists if idx > 0
        if ladder.idx is None or ladder.idx <= 0:
            return {}
        prev_name = ladder.stack[ladder.idx - 1]
        layer_obj = None
        if isinstance(self._layers_ref, dict):
            layer_obj = self._layers_ref.get(prev_name)
        if layer_obj and hasattr(layer_obj, "COMMANDS"):
            cmds = getattr(layer_obj, "COMMANDS")
            if isinstance(cmds, dict):
                # ensure str,str
                return {str(k): str(v) for k, v in cmds.items()}
        return {}

    def render(self, ladder: Ladder, last_in: str, last_out: str) -> None:
        clear_screen()

        # Build help rows: system first
        rows: List[List[Optional[str]]] = []
        for cmd, expl in SYSTEM_COMMANDS.items():
            rows.append([cmd, expl])

        # Then previous layer commands (if any)
        prev_cmds = self._prev_layer_commands(ladder)
        if prev_cmds:
            rows.append(["", ""])  # spacer
            # Section header row (wrapped)
            rows.append(
                ["Previous Layer",
                 "Commands available on the layer that would be active after a Back action."]
            )
            for cmd, expl in prev_cmds.items():
                rows.append([cmd, expl])

        # Use wrap_text=True so long explanations wrap with row separators
        self.tm.set_headers(HELP_TABLE, ["Commands", "Explanation"])
        self.tm.set_rows(HELP_TABLE, rows, wrap_text=True)

        # Draw the help table
        self.tm.draw_many([HELP_TABLE])

    def handle_input(
        self,
        text: str,
        ladder: Ladder,
        globals_dict: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        # Cache layers dict (so render() can read the previous layer’s COMMANDS)
        layers = globals_dict.get("layers")
        if isinstance(layers, dict):
            self._layers_ref = layers

        token, orig = parse(text)

        # shared navigation + layer calls
        layer_names = globals_dict.get("layer_names", ["Home", "Help"])
        action, msg = route_shared(token, orig, ladder, layer_names, current_layer="Help")
        if action:
            return action, msg

        return "redraw", f"Unknown command: {orig or ''}"
