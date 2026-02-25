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

def module_name_from_path_multi(path: str, roots: List[str]) -> str:
    abspath = os.path.abspath(path)
    best_root = None
    best_len = -1
    for r in roots:
        ar = os.path.abspath(r)
        if abspath.startswith(ar.rstrip(os.sep) + os.sep):
            l = len(ar)
            if l > best_len:
                best_len = l
                best_root = ar
    if best_root is None:
        best_root = os.path.abspath(roots[0])
    return module_name_from_path(path, best_root)

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

def resolve_relative_pkg(current_module: str, level: int, base: Optional[str], is_init: bool) -> Optional[str]:
    if level <= 0:
        return base or None
    parts = current_module.split(".") if current_module else []
    pkg_parts = parts if is_init else (parts[:-1] if parts else [])
    up = level - 1
    if up > len(pkg_parts):
        return None
    parent = pkg_parts[: len(pkg_parts) - up]
    if base:
        parent.append(base)
    if not parent:
        return base or None
    return ".".join(parent)

def _imports_in_module_top(tree: ast.Module, current_module: str, is_init: bool) -> Set[str]:
    deps: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                deps.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module
            level = node.level or 0
            if level > 0:
                resolved = resolve_relative_pkg(current_module, level, base, is_init)
                if resolved:
                    deps.add(resolved)
            else:
                if base:
                    deps.add(base)
    return deps


def build_dependency_graph(root: str, package_paths: Optional[List[str]] = None) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {}
    roots = package_paths or [root]
    for f in _py_files(root):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src)
        except Exception:
            continue
        mod = module_name_from_path_multi(f, roots)
        is_init = os.path.basename(f) == "__init__.py"
        graph[mod] = _imports_in_module_top(tree, mod, is_init)
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
