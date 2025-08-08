# cli/ui/hud.py
from typing import List, Tuple, Optional
from .table_manager import TableManager

DEFAULT_HUD_NAME = "lastio"
DEFAULT_HEADERS: Tuple[str, str] = ("Last Input", "Last Output")

def _split_long_word(word: str, width: int) -> List[str]:
    """Break a single overlong word into width-sized chunks."""
    return [word[i:i+width] for i in range(0, len(word), max(1, width))]

def _wrap_text(text: Optional[str], width: int) -> List[str]:
    """
    Word-wrap into lines <= width. Does not break words across lines
    unless a single word exceeds width, in which case it hard-wraps that word.
    """
    if not text:
        return [""]
    words = str(text).split()
    lines: List[str] = []
    current: List[str] = []

    def flush():
        if current:
            lines.append(" ".join(current))
            current.clear()

    for w in words:
        if len(w) <= width:
            # Try to place in current line
            if not current:
                current.append(w)
            else:
                # +1 for space
                if len(" ".join(current)) + 1 + len(w) <= width:
                    current.append(w)
                else:
                    flush()
                    current.append(w)
        else:
            # Overlong word: first flush current, then hard-wrap the word
            flush()
            chunks = _split_long_word(w, width)
            # Put all full chunks as their own lines
            for i, ch in enumerate(chunks):
                # If a chunk exactly fills width, keep as a dedicated line
                if len(ch) == width:
                    lines.append(ch)
                else:
                    # Start a new line with the remainder chunk
                    current.append(ch) if i == len(chunks) - 1 else lines.append(ch)
            # If the last chunk was shorter and appended to current, it may get more words
            # in subsequent iterations.

    flush()
    return lines or [""]

def build_hud_table(
    tm: TableManager,
    name: str = DEFAULT_HUD_NAME,
    total_width: int = 71,
    headers: Tuple[str, str] = DEFAULT_HEADERS,
) -> None:
    """
    Ensure the HUD table exists with given width and headers.
    If it already exists, just updates headers (no row changes).
    """
    if not tm.has(name):
        tm.build(name, total_width, list(headers))
    else:
        tm.set_headers(name, list(headers), recompute_widths=None)

def set_hud_content(
    tm: TableManager,
    name: str = DEFAULT_HUD_NAME,
    left_text: Optional[str] = "",
    right_text: Optional[str] = "",
) -> int:
    """
    Word-wrap left/right text to the HUD's column widths and set rows.
    Returns the number of rows written.
    """
    t = tm.get(name)
    if len(t.columns) != 2:
        raise ValueError(f"HUD '{name}' must have exactly 2 columns (has {len(t.columns)})")

    left_w, right_w = t.widths[0], t.widths[1]
    left_lines = _wrap_text(left_text, max(1, left_w))
    right_lines = _wrap_text(right_text, max(1, right_w))

    max_rows = max(len(left_lines), len(right_lines))
    rows: List[List[str]] = []
    for i in range(max_rows):
        l = left_lines[i] if i < len(left_lines) else ""
        r = right_lines[i] if i < len(right_lines) else ""
        rows.append([l, r])

    tm.set_rows(name, rows) # type: ignore[arg-type]
    return max_rows

def ensure_and_set_hud(
    tm: TableManager,
    name: str = DEFAULT_HUD_NAME,
    total_width: int = 71,
    headers: Tuple[str, str] = DEFAULT_HEADERS,
    left_text: Optional[str] = "",
    right_text: Optional[str] = "",
) -> int:
    """
    Convenience: ensure HUD exists, then set its content.
    Returns the number of rows written.
    """
    build_hud_table(tm, name=name, total_width=total_width, headers=headers)
    return set_hud_content(tm, name=name, left_text=left_text, right_text=right_text)
