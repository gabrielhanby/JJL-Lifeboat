# CLI/src/main.py
import os
import sys
from typing import Dict, Protocol, runtime_checkable, Tuple, Any, Optional

from .ladder import Ladder
from ..layers.home import HomeLayer
from ..layers.help import HelpLayer
from ..ui.ui import clear_screen

@runtime_checkable
class Layer(Protocol):
    # allow optional extras so any layer with extra params still conforms
    def render(self, ladder: "Ladder", last_in: str, last_out: str, *args: Any, **kwargs: Any) -> None: ...
    def handle_input(
        self,
        text: str,
        ladder: "Ladder",
        globals_dict: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]: ...

def ensure_active_layer_name(ladder: Ladder, layers: Dict[str, "Layer"]) -> str:
    """
    Guarantee there is an active layer name; bootstrap to Home (or first layer) if needed.
    """
    name = ladder.active
    if isinstance(name, str):
        return name
    default = "Home" if "Home" in layers else next(iter(layers.keys()))
    ladder.call(default)
    return ladder.active or default

def seed_ladder_home_help(ladder: Ladder) -> None:
    """
    Build initial ladder: ["Home", "Help"] with active set to "Home".
    Uses existing Ladder APIs without touching internals.
    """
    ladder.call("Home")                  # stack=["Home"], active="Home"
    ladder.insert_above_current("Help")  # stack=["Home","Help"], active becomes "Help"
    ladder.back()                        # active back to "Home" (stack preserved)

def main() -> None:
    last_input: str = ""
    last_output: str = ""

    ladder = Ladder()
    layers: Dict[str, Layer] = {
        "Home": HomeLayer(),
        "Help": HelpLayer(),
    }
    layer_names = list(layers.keys())

    # Seed ladder as: 0. Home, 1. Help (active = Home)
    seed_ladder_home_help(ladder)

    # Initial render
    active_name = ensure_active_layer_name(ladder, layers)
    layers[active_name].render(ladder, last_input, last_output)

    # Main loop
    while True:
        try:
            text = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        last_input = text

        active_name = ensure_active_layer_name(ladder, layers)
        active_layer = layers[active_name]

        action, message = active_layer.handle_input(
            text,
            ladder,
            globals_dict={"layer_names": layer_names, "layers": layers}
        )
        last_output = message or ""

        if action == "quit":
            break

        if action == "quit_prompt":
            ans = input(f"{last_output} ").strip().lower()
            if ans.startswith("y"):
                break
            # user declined; redraw current
            active_name = ensure_active_layer_name(ladder, layers)
            layers[active_name].render(ladder, last_input, last_output)
            continue

        if action.startswith("switch:"):
            target = action.split(":", 1)[1]
            target_name = target if target in layers else active_name
            layers[target_name].render(ladder, last_input, last_output)
            continue

        if action in ("home", "redraw", "noop"):
            active_name = ensure_active_layer_name(ladder, layers)
            layers[active_name].render(ladder, last_input, last_output)
            continue

if __name__ == "__main__":
    # Allow `python -m CLI.src.main` and direct script execution
    if __package__ is None:
        this_file = __file__
        root_dir = os.path.abspath(os.path.join(os.path.dirname(this_file), "..", ".."))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
    main()
