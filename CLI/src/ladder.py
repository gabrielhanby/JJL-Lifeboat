# cli/src/ladder.py
from typing import List

class Ladder:
    def __init__(self):
        self.stack: List[str] = []
        self.idx: int = -1

    @property
    def active(self):
        return self.stack[self.idx] if 0 <= self.idx < len(self.stack) else None

    def call(self, layer_name: str):
        if self.active == layer_name:
            return False, "same"
        if layer_name in self.stack:
            self.idx = self.stack.index(layer_name)
            return True, "focus"
        self.stack.append(layer_name)
        self.idx = len(self.stack) - 1
        return True, "push"

    def insert_above_current(self, layer_name: str) -> bool:
        """
        Insert 'layer_name' directly above the current active layer and focus it.
        If the layer already exists anywhere in the ladder, CUT it first to avoid duplicates.
        """
        # if nothing active yet, just append and focus
        if self.idx < 0:
            self.stack = [layer_name]
            self.idx = 0
            return True

        # if already active, do nothing (caller will show Smart... message)
        if self.active == layer_name:
            return False

        # CUT: remove any existing occurrence and fix caret if needed
        if layer_name in self.stack:
            old_pos = self.stack.index(layer_name)
            self.stack.pop(old_pos)
            if old_pos <= self.idx:
                # caret shifts left because we removed an item at/before it
                self.idx -= 1

        # INSERT directly above current, then focus it
        insert_at = self.idx + 1
        self.stack.insert(insert_at, layer_name)
        self.idx = insert_at
        return True

    def back(self) -> bool:
        if self.idx > 0:
            self.idx -= 1
            return True
        return False

    def forth(self) -> bool:
        if self.idx < len(self.stack) - 1:
            self.idx += 1
            return True
        return False

    def ladder_str(self) -> str:
        return " > ".join(self.stack)

    def as_vertical(self, prefix_active: str = "> ", prefix_inactive: str = "  ") -> List[str]:
        if not self.stack:
            return [f"{prefix_active}Home"]
        return [
            f"{prefix_active if i == self.idx else prefix_inactive}{name}"
            for i, name in enumerate(self.stack)
        ]
