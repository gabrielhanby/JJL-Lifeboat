# cli/ui/ui.py
import os

SEP_LEFT  = "| "
SEP_MID   = " | "
SEP_RIGHT = " |"

def clear_screen():
    os.system("cls")

def fit_cell(text, width):
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

def _draw_single(table):
    # Optional pre-rendered rows and post-separators for wrapped blocks
    rows = getattr(table, "_render_rows", None)
    post = getattr(table, "_row_separators_post", None)

    print("-" * table.total_width)
    # header
    parts = [SEP_LEFT]
    for i, (col, w) in enumerate(zip(table.columns, table.widths)):
        cell = fit_cell(col, w)
        parts.append(cell if i == 0 else SEP_MID + cell)
    parts.append(SEP_RIGHT)
    print("".join(parts))
    print("-" * table.total_width)

    # body
    if rows is None:
        rows = table.rows
    if rows:
        last_idx = len(rows) - 1
        for idx, r in enumerate(rows):
            parts = [SEP_LEFT]
            for i, (val, w) in enumerate(zip(r, table.widths)):
                cell = fit_cell(val, w)
                parts.append(cell if i == 0 else SEP_MID + cell)
            parts.append(SEP_RIGHT)
            print("".join(parts))

            # Draw a single shared border after the last wrapped line of a row block.
            # Skip after the very last rendered row; the final table bottom border comes next.
            if post and idx < len(post) and post[idx] and idx != last_idx:
                print("-" * table.total_width)

        print("-" * table.total_width)

def draw_table(_name_unused, table):
    _draw_single(table)

def draw_many(tables):
    for t in tables:
        _draw_single(t)
