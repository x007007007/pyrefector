import os
from typing import List, Tuple, Optional
import libcst as cst
from .deps import module_name_from_path_multi, resolve_relative_pkg


def _to_cst_module(name: str) -> cst.CSTNode:
    parts = name.split(".")
    node: cst.CSTNode = cst.Name(parts[0])
    for p in parts[1:]:
        node = cst.Attribute(value=node, attr=cst.Name(p))
    return node


class AbsImportRewriter(cst.CSTTransformer):
    def __init__(self, module_name: str, is_init: bool):
        self.module_name = module_name
        self.is_init = is_init
        self.changed = False

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        level = len(updated_node.relative) if updated_node.relative else 0
        if level <= 0:
            return updated_node
        base = None
        if updated_node.module is not None:
            mod = updated_node.module
            parts: List[str] = []
            while isinstance(mod, cst.Attribute):
                parts.append(mod.attr.value)
                mod = mod.value
            if isinstance(mod, cst.Name):
                parts.append(mod.value)
            else:
                return updated_node
            parts.reverse()
            base = ".".join(parts)
        resolved = resolve_relative_pkg(self.module_name, level, base, self.is_init)
        if not resolved:
            return updated_node
        self.changed = True
        return updated_node.with_changes(module=_to_cst_module(resolved), relative=())


def rewrite_abs_file(path: str, roots: List[str]) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        module = cst.parse_module(src)
    except Exception:
        return False
    modname = module_name_from_path_multi(path, roots)
    is_init = os.path.basename(path) == "__init__.py"
    rewriter = AbsImportRewriter(modname, is_init)
    new_module = module.visit(rewriter)
    if not rewriter.changed:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_module.code)
    return True


def rewrite_abs_directory(root: str, package_paths: Optional[List[str]] = None) -> List[str]:
    changed: List[str] = []
    roots = package_paths or [root]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            if rewrite_abs_file(path, roots):
                changed.append(path)
    return changed
