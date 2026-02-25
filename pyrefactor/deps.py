import os
import ast
from typing import Dict, Set, List, Optional


def _py_files(root: str) -> List[str]:
    paths: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".py"):
                paths.append(os.path.join(dirpath, fn))
    return paths


def module_name_from_path(path: str, root: str) -> str:
    rel = os.path.relpath(path, root)
    no_ext = os.path.splitext(rel)[0]
    parts = []
    for p in no_ext.split(os.sep):
        if p == "__init__":
            continue
        parts.append(p)
    return ".".join(parts)


def resolve_relative(current_module: str, level: int, base: Optional[str]) -> Optional[str]:
    if level <= 0:
        return base or None
    parts = current_module.split(".") if current_module else []
    if level > len(parts):
        return None
    parent = parts[: len(parts) - level]
    if base:
        parent.append(base)
    if not parent:
        return None
    return ".".join(parent)


def _imports_in_module_top(tree: ast.Module, current_module: str) -> Set[str]:
    deps: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                deps.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module
            level = node.level or 0
            if level > 0:
                resolved = resolve_relative(current_module, level, base)
                if resolved:
                    deps.add(resolved)
            else:
                if base:
                    deps.add(base)
    return deps


def build_dependency_graph(root: str) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {}
    for f in _py_files(root):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src)
        except Exception:
            continue
        mod = module_name_from_path(f, root)
        graph[mod] = _imports_in_module_top(tree, mod)
    return graph


def _reachable(graph: Dict[str, Set[str]], src: str, dst: str) -> bool:
    seen: Set[str] = set()
    stack: List[str] = [src]
    while stack:
        cur = stack.pop()
        if cur == dst:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in graph.get(cur, ()):
            stack.append(nxt)
    return False


def would_create_cycle(graph: Dict[str, Set[str]], src: str, dst: str) -> bool:
    return _reachable(graph, dst, src)
