import os

# separators
SEP_LEFT  = "| "
SEP_MID   = " | "
SEP_RIGHT = " |"

TABLES = {}

def fit_cell(text, width):
    # Treat None as empty at render time
    if text is None:
        text = ""
    s = str(text)
    if width <= 3:
        return ("." * width) if len(s) > width else s.ljust(width)
    if len(s) > width:
        return s[:width - 3] + "..."
    return s.ljust(width)

def compute_widths(total_width, num_cols):
    borders = len(SEP_LEFT) + len(SEP_RIGHT) + (num_cols - 1) * len(SEP_MID)
    avch = total_width - borders
    if avch < num_cols:
        raise ValueError("table_width too small for the number of columns and borders")
    base = avch // num_cols
    rem = avch % num_cols
    return [base + (1 if i < rem else 0) for i in range(num_cols)]

class Table:
    def __init__(self, name, total_width, columns):
        self.name = name
        self.total_width = total_width
        self.columns = list(columns)
        self.widths = compute_widths(total_width, len(columns))
        self.rows = []

    def border(self):
        print("-" * self.total_width)

    def header(self):
        parts = [SEP_LEFT]
        for i, (col, w) in enumerate(zip(self.columns, self.widths)):
            cell = fit_cell(col, w)
            parts.append(cell if i == 0 else SEP_MID + cell)
        parts.append(SEP_RIGHT)
        print("".join(parts))

    def row(self, values):
        parts = [SEP_LEFT]
        for i, (val, w) in enumerate(zip(values, self.widths)):
            cell = fit_cell(val, w)
            parts.append(cell if i == 0 else SEP_MID + cell)
        parts.append(SEP_RIGHT)
        print("".join(parts))

    def draw(self, include_rows=True):
        self.border()
        self.header()
        self.border()
        if include_rows and self.rows:
            for r in self.rows:
                self.row(r)
            self.border()

def draw_table(table: Table, include_rows=True):
    table.draw(include_rows=include_rows)

# ---------- public API: build, rows ----------

def table_build(name, width, columns):
    TABLES[name] = Table(name, width, columns)

def table_add_row(name, values):
    """Add a new row. None becomes blank since there is nothing to keep."""
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    processed = [("" if v is None else v) for v in values]
    TABLES[name].rows.append(processed)

def table_set_rows(name, rows):
    """Replace all rows. None becomes blank since there is nothing to keep."""
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    TABLES[name].rows = [[("" if v is None else v) for v in r] for r in rows]

def table_update_row(name, row_index, values):
    """
    Update a row in place.
    None = keep existing cell
    ""   = set blank
    other value = replace
    """
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    if row_index < 0 or row_index >= len(t.rows):
        raise IndexError(f"Row {row_index} out of range for table '{name}'")
    for col_index, val in enumerate(values):
        if val is None:
            continue
        t.rows[row_index][col_index] = val

def table_clear_rows(name):
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    TABLES[name].rows.clear()

# ---------- public API: headers ----------

def table_set_headers(name, columns, recompute_widths=None):
    """
    Replace all headers.
    recompute_widths:
      - None: recompute only if column count changed
      - True: always recompute
      - False: never recompute (raises if count changed)
    """
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    new_cols = list(columns)
    same_count = len(new_cols) == len(t.columns)
    need_recompute = (not same_count) if recompute_widths is None else bool(recompute_widths)
    if not same_count and not need_recompute:
        raise ValueError("Column count changed but recompute_widths=False")
    t.columns = new_cols
    if need_recompute:
        t.widths = compute_widths(t.total_width, len(t.columns))

def table_update_header(name, col_index, value):
    """
    Update a single header cell.
    None = keep existing
    ""   = blank
    other value = replace
    """
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    if col_index < 0 or col_index >= len(t.columns):
        raise IndexError(f"Column {col_index} out of range for table '{name}'")
    if value is None:
        return
    t.columns[col_index] = value

def table_update_headers(name, values):
    """
    Bulk header update. Length must match current column count.
    Uses same rules: None keep, "" blank, other replace.
    """
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    if len(values) != len(t.columns):
        raise ValueError("values length must match current column count")
    for i, v in enumerate(values):
        if v is None:
            continue
        t.columns[i] = v

def table_insert_column(name, index, header, fill=""):
    """
    Insert a new column at index. Recomputes widths.
    Adds 'fill' into each row at the same position.
    """
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    if index < 0 or index > len(t.columns):
        raise IndexError(f"Insert index {index} out of range")
    t.columns.insert(index, header)
    for r in t.rows:
        r.insert(index, fill)
    t.widths = compute_widths(t.total_width, len(t.columns))

def table_remove_column(name, index):
    """Remove a column at index and recompute widths."""
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    if index < 0 or index >= len(t.columns):
        raise IndexError(f"Column {index} out of range for table '{name}'")
    t.columns.pop(index)
    for r in t.rows:
        if index < len(r):
            r.pop(index)
    t.widths = compute_widths(t.total_width, len(t.columns))

# ---------- public API: width + draw ----------

def table_update_width(name, total_width):
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    t = TABLES[name]
    t.total_width = total_width
    t.widths = compute_widths(t.total_width, len(t.columns))

def table_draw(name, include_rows=True, clear=False):
    if name not in TABLES:
        raise KeyError(f"Table '{name}' not found. Build it first.")
    if clear:
        os.system("cls")
    draw_table(TABLES[name], include_rows=include_rows)

# ---------- example usage ----------

if __name__ == "__main__":
    # build
    table_build("system", 71, ["Carpathia", "Ladder", "Active"])

    # initial rows (None -> blank for new rows)
    table_add_row("system", ["Help", None, None])
    table_add_row("system", ["Back", None, None])
    table_add_row("system", ["Forth", None, None])
    table_add_row("system", ["Exit", None, None])
    table_add_row("system", ["Exit All", None, None])

    table_draw("system", clear=True)

    # update some cells in place
    table_update_row("system", 0, [None, "> Home", "Help"])
    table_update_row("system", 1, [None, "  Help", "Exit"])
    table_update_row("system", 2, [None, "  Search", "Exit All"])

    # rename a header cell and blank another
    table_update_header("system", 0, "System")
    table_update_headers("system", [None, None, ""])

    table_draw("system", clear=True)

    # insert a "Status" column at index 1 with default value
    table_insert_column("system", 1, "Status", fill="")
    table_update_row("system", 0, [None, "OK", None, None])
    table_draw("system", clear=True)

    # remove the last column
    table_remove_column("system", len(TABLES["system"].columns) - 1)
    table_draw("system", clear=True)
