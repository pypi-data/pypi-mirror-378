from typing import Set, Tuple

import libcst as cst


class SymbolCollector(cst.CSTVisitor):
    def __init__(self) -> None:
        self.symbols: Set[str] = set()
        self._nesting: int = 0

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        if self._nesting == 0:  # Only top-level functions
            self.symbols.add(node.name.value)

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        if self._nesting == 0:  # Only top-level classes
            self.symbols.add(node.name.value)
        self._nesting += 1

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._nesting -= 1


def extract_symbols(source: str) -> Set[str]:
    """
    Parses Python source and returns top-level class/function names.
    """
    try:
        tree = cst.parse_module(source)
    except Exception:
        return set()
    collector = SymbolCollector()
    tree.visit(collector)
    return collector.symbols


def diff_symbol_sets(before: str, after: str) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compares before/after source code and returns:
    (added, removed, unchanged)
    """
    old_syms = extract_symbols(before)
    new_syms = extract_symbols(after)

    added = new_syms - old_syms
    removed = old_syms - new_syms
    unchanged = old_syms & new_syms

    return added, removed, unchanged
