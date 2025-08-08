# cli/src/input.py

from typing import Dict, Any, Tuple, Optional, List

def normalize(s: str) -> str:
    return (s or "").strip()

def lower(s: str) -> str:
    return normalize(s).lower()

def is_cmd(s: str, *aliases) -> bool:
    ls = lower(s)
    return any(ls == a for a in aliases)

def parse(s: str) -> Tuple[str, str]:
    orig = normalize(s)
    token = orig.lower()
    return token, orig

def route_shared(
    token: str,
    orig: str,
    ladder,
    layer_names: List[str],
    current_layer: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Shared navigation and layer-calling logic.

    Returns (action, message) or (None, None).

    Actions:
      - "quit"         → terminate immediately
      - "quit_prompt"  → ask y/n before terminating
      - "switch:<L>"   → switch to a named layer
      - "redraw"       → refresh current layer
      - "noop"         → do nothing
    """

    # exit all → always prompt to terminate
    if is_cmd(token, "exit all", "exitall"):
        return "quit_prompt", "Terminate application? (y/n)"

    # exit → acts like back unless on Home (then prompt)
    if is_cmd(token, "exit"):
        if current_layer.lower() == "home":
            return "quit_prompt", "Terminate application? (y/n)"
        if ladder.back():
            return "redraw", "Went back"
        return "redraw", "You cannot go that way."

    # back
    if is_cmd(token, "back"):
        if ladder.back():
            return "redraw", "Went back"
        return "redraw", "You cannot go that way."

    # forth
    if is_cmd(token, "forth"):
        if ladder.forth():
            return "redraw", "Went forth"
        return "redraw", "You cannot go that way."

    # layer calls by name (case-insensitive)
    tlower = token
    for lname in layer_names:
        if tlower == lname.lower():
            if current_layer.lower() == lname.lower():
                return "redraw", "Smart... Only you would try that"
            ladder.insert_above_current(lname)
            return f"switch:{lname}", f"Switching to {lname}"

    return None, None
