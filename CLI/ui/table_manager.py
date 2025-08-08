# cli/ui/table_manager.py
from typing import List, Optional, Dict, Tuple, Sequence
from .ui import compute_widths, draw_many as _ui_draw_many

class Table:
    def __init__(self, name: str, total_width: int, columns: List[str]):
        self.name = name
        self.total_width = total_width
        self.columns = list(columns)
        self.widths = compute_widths(total_width, len(columns))
        # canonical (flat) rows
        self.rows: List[List[str]] = []
        # pre-rendered view for wrapped tables
        self._render_rows: Optional[List[List[str]]] = None
        self._row_separators_post: Optional[List[bool]] = None  # only post, shared border

class TableManager:
    def __init__(self):
        self.tables: Dict[str, Table] = {}

    # build and structure
    def build(self, name: str, width: int, columns: List[str]) -> Table:
        self.tables[name] = Table(name, width, columns)
        return self.tables[name]

    def has(self, name: str) -> bool:
        return name in self.tables

    def get(self, name: str) -> Table:
        if name not in self.tables:
            raise KeyError(f"Table '{name}' not found in this layer")
        return self.tables[name]

    # headers
    def set_headers(self, name: str, columns: List[str], recompute_widths: Optional[bool] = None) -> None:
        t = self.get(name)
        new_cols = list(columns)
        same = len(new_cols) == len(t.columns)
        need_re = (not same) if recompute_widths is None else bool(recompute_widths)
        if not same and not need_re:
            raise ValueError("Column count changed but recompute_widths=False")
        t.columns = new_cols
        if need_re:
            t.widths = compute_widths(t.total_width, len(t.columns))
        self._invalidate_render_cache(t)

    def update_header(self, name: str, col_index: int, value: Optional[str]) -> None:
        t = self.get(name)
        if col_index < 0 or col_index >= len(t.columns):
            raise IndexError(f"Column {col_index} out of range for table '{name}'")
        if value is None:
            return
        t.columns[col_index] = value
        self._invalidate_render_cache(t)

    def update_headers(self, name: str, values: List[Optional[str]]) -> None:
        t = self.get(name)
        if len(values) != len(t.columns):
            raise ValueError("values length must match current column count")
        for i, v in enumerate(values):
            if v is None:
                continue
            t.columns[i] = v
        self._invalidate_render_cache(t)

    def insert_column(self, name: str, index: int, header: str, fill: str = "") -> None:
        t = self.get(name)
        if index < 0 or index > len(t.columns):
            raise IndexError(f"Insert index {index} out of range")
        t.columns.insert(index, header)
        for r in t.rows:
            r.insert(index, fill)
        t.widths = compute_widths(t.total_width, len(t.columns))
        self._invalidate_render_cache(t)

    def remove_column(self, name: str, index: int) -> None:
        t = self.get(name)
        if index < 0 or index >= len(t.columns):
            raise IndexError(f"Column {index} out of range for table '{name}'")
        t.columns.pop(index)
        for r in t.rows:
            if index < len(r):
                r.pop(index)
        t.widths = compute_widths(t.total_width, len(t.columns))
        self._invalidate_render_cache(t)

    # ---- wrapping helpers ----
    @staticmethod
    def _split_long_word(word: str, width: int) -> List[str]:
        return [word[i:i+width] for i in range(0, len(word), max(1, width))]

    @classmethod
    def _wrap_text(cls, text: Optional[str], width: int) -> List[str]:
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
                if not current:
                    current.append(w)
                else:
                    if len(" ".join(current)) + 1 + len(w) <= width:
                        current.append(w)
                    else:
                        flush()
                        current.append(w)
            else:
                flush()
                chunks = cls._split_long_word(w, width)
                for i, ch in enumerate(chunks):
                    if i < len(chunks) - 1:
                        lines.append(ch)
                    else:
                        current.append(ch)
        flush()
        return lines or [""]

    # rows
    def clear_rows(self, name: str) -> None:
        t = self.get(name)
        t.rows.clear()
        self._invalidate_render_cache(t)

    def add_row(self, name: str, values: List[Optional[str]]) -> None:
        t = self.get(name)
        t.rows.append([("" if v is None else v) for v in values])
        self._invalidate_render_cache(t)

    def _expand_rows_with_wrap(
        self,
        t: Table,
        rows: Sequence[Sequence[Optional[str]]]
    ) -> Tuple[List[List[str]], List[bool]]:
        """
        Expand logical rows into multiple rendered rows.
        - No borders between wrapped lines of the same logical row.
        - A single shared border after the last wrapped line of each logical row,
          which serves as the top border for the next row.
        """
        render_rows: List[List[str]] = []
        post: List[bool] = []

        for logical in rows:
            # wrap each cell to column width
            col_lines: List[List[str]] = []
            for val, w in zip(logical, t.widths):
                col_lines.append(self._wrap_text("" if val is None else str(val), max(1, w)))

            sub_h = max(len(c) for c in col_lines) if col_lines else 1

            for i in range(sub_h):
                render_rows.append([ (col_lines[c][i] if i < len(col_lines[c]) else "") for c in range(len(col_lines)) ])
                # mark post True only on the last wrapped line of this logical row
                post.append(i == sub_h - 1)

        # Avoid double bottom border: the final table bottom is printed by UI.
        if post:
            post[-1] = False

        return render_rows, post

    def set_rows(self, name: str, rows: List[List[Optional[str]]], wrap_text: bool = False) -> None:
        t = self.get(name)
        # canonical storage
        t.rows = [[("" if v is None else v) for v in r] for r in rows]

        if not wrap_text:
            self._invalidate_render_cache(t)
            return

        rrows, post = self._expand_rows_with_wrap(t, rows)
        t._render_rows = rrows
        t._row_separators_post = post

    def update_row(self, name: str, row_index: int, values: List[Optional[str]], wrap_text: bool = False) -> None:
        t = self.get(name)
        if row_index < 0 or row_index >= len(t.rows):
            raise IndexError(f"Row {row_index} out of range for table '{name}'")
        for col_index, val in enumerate(values):
            if val is None:
                continue
            t.rows[row_index][col_index] = val

        if wrap_text:
            rrows, post = self._expand_rows_with_wrap(t, t.rows)
            t._render_rows = rrows
            t._row_separators_post = post
        else:
            self._invalidate_render_cache(t)

    # width
    def update_width(self, name: str, total_width: int) -> None:
        t = self.get(name)
        t.total_width = total_width
        t.widths = compute_widths(t.total_width, len(t.columns))
        self._invalidate_render_cache(t)

    # draw multiple tables
    def draw_many(self, names_in_order: List[str]) -> None:
        _ui_draw_many([self.get(n) for n in names_in_order])

    # internal
    def _invalidate_render_cache(self, t: Table) -> None:
        t._render_rows = None
        t._row_separators_post = None
