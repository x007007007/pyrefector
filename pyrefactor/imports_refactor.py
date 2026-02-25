import os
import difflib
from typing import List, Tuple, Set, Dict, Optional

import libcst as cst
from .deps import would_create_cycle, build_dependency_graph, module_name_from_path, resolve_relative


class ImportLifter(cst.CSTTransformer):
    def __init__(self, module_name: str, dep_graph: Dict[str, Set[str]], include_relative: bool = False, allow_control_blocks: bool = False):
        self.include_relative = include_relative
        self.allow_control_blocks = allow_control_blocks
        self._in_function_or_class = 0
        self._in_control_block = 0
        self._collected: List[cst.CSTNode] = []
        self._module_name = module_name
        self._graph = dep_graph

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self._in_function_or_class += 1
        return True
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        self._in_function_or_class -= 1
        return updated_node

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._in_function_or_class += 1
        return True
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self._in_function_or_class -= 1
        return updated_node

    def visit_If(self, node: cst.If) -> bool:
        self._in_control_block += 1
        return True
    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        self._in_control_block -= 1
        return updated_node

    def visit_For(self, node: cst.For) -> bool:
        self._in_control_block += 1
        return True
    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For:
        self._in_control_block -= 1
        return updated_node

    def visit_While(self, node: cst.While) -> bool:
        self._in_control_block += 1
        return True
    def leave_While(self, original_node: cst.While, updated_node: cst.While) -> cst.While:
        self._in_control_block -= 1
        return updated_node

    def visit_With(self, node: cst.With) -> bool:
        self._in_control_block += 1
        return True
    def leave_With(self, original_node: cst.With, updated_node: cst.With) -> cst.With:
        self._in_control_block -= 1
        return updated_node

    def visit_Try(self, node: cst.Try) -> bool:
        self._in_control_block += 1
        return True
    def leave_Try(self, original_node: cst.Try, updated_node: cst.Try) -> cst.Try:
        self._in_control_block -= 1
        return updated_node

    def _is_safe_to_lift(self) -> bool:
        if self._in_function_or_class <= 0:
            return False
        if not self.allow_control_blocks and self._in_control_block > 0:
            return False
        return True

    def _import_target(self, node: cst.CSTNode) -> Optional[str]:
        if isinstance(node, cst.ImportFrom):
            level = len(node.relative) if node.relative else 0
            if level > 0 and not self.include_relative:
                return None
            base_name = None
            if node.module is not None:
                mod = node.module
                parts: List[str] = []
                while isinstance(mod, cst.Attribute):
                    parts.append(mod.attr.value)
                    mod = mod.value
                if isinstance(mod, cst.Name):
                    parts.append(mod.value)
                else:
                    return None
                parts.reverse()
                base_name = ".".join(parts)
            if level > 0:
                resolved = resolve_relative(self._module_name, level, base_name)
                return resolved
            return base_name
        elif isinstance(node, cst.Import):
            if len(node.names) != 1:
                return None
            alias = node.names[0]
            name = alias.name
            parts: List[str] = []
            while isinstance(name, cst.Attribute):
                parts.append(name.attr.value)
                name = name.value
            if isinstance(name, cst.Name):
                parts.append(name.value)
            else:
                return None
            parts.reverse()
            return ".".join(parts)
        else:
            return None

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        if not self._is_safe_to_lift():
            return updated_node
        kept: List[cst.BaseSmallStatement] = []
        for small in updated_node.body:
            target = self._import_target(small)
            if target is not None and not would_create_cycle(self._graph, self._module_name, target):
                self._collected.append(small)
            else:
                kept.append(small)
        if len(kept) == len(updated_node.body):
            return updated_node
        return updated_node.with_changes(body=tuple(kept))

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if not self._collected:
            return updated_node
        existing_import_codes: Set[str] = set()
        prefix_count = 0
        body = list(updated_node.body)
        if body and isinstance(body[0], cst.SimpleStatementLine):
            exprs = body[0].body
            if len(exprs) == 1 and isinstance(exprs[0], cst.Expr) and isinstance(exprs[0].value, cst.SimpleString):
                prefix_count = 1
        i = prefix_count
        while i < len(body) and isinstance(body[i], cst.SimpleStatementLine):
            line = body[i]
            if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in line.body):
                existing_import_codes.add(cst.Module([line]).code.strip())
                i += 1
            else:
                break
        new_import_lines: List[cst.SimpleStatementLine] = []
        for node in self._collected:
            line = cst.SimpleStatementLine(body=[node])
            code = cst.Module([line]).code.strip()
            if code not in existing_import_codes:
                existing_import_codes.add(code)
                new_import_lines.append(line)
        new_body = []
        new_body.extend(body[:i])
        new_body.extend(new_import_lines)
        new_body.extend(body[i:])
        return updated_node.with_changes(body=tuple(new_body))


def rewrite_file(path: str, module_name: str, dep_graph: Dict[str, Set[str]], include_relative: bool = False, allow_control_blocks: bool = False, dry_run: bool = False) -> Tuple[bool, str]:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        module = cst.parse_module(src)
    except Exception:
        return False, ""
    transformer = ImportLifter(module_name=module_name, dep_graph=dep_graph, include_relative=include_relative, allow_control_blocks=allow_control_blocks)
    new_module = module.visit(transformer)
    new_src = new_module.code
    if new_src == src:
        return False, ""
    if dry_run:
        diff = difflib.unified_diff(src.splitlines(True), new_src.splitlines(True), fromfile=path, tofile=path)
        return True, "".join(diff)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_src)
    return True, ""


def rewrite_directory(root: str, include_relative: bool = False, allow_control_blocks: bool = False, dry_run: bool = False, output_diff: Optional[str] = None, modify_under: Optional[str] = None) -> List[str]:
    changes: List[str] = []
    graph = build_dependency_graph(root)
    diff_chunks: List[str] = []
    base_root = os.path.abspath(root)
    target_prefix = None
    if modify_under:
        target_prefix = os.path.abspath(modify_under)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            mod = module_name_from_path(path, root)
            if target_prefix and not os.path.abspath(path).startswith(target_prefix):
                continue
            changed, diff = rewrite_file(path, mod, graph, include_relative, allow_control_blocks, dry_run)
            if changed:
                if dry_run and diff:
                    diff_chunks.append(diff)
                else:
                    changes.append(path)
    if output_diff and diff_chunks:
        with open(output_diff, "w", encoding="utf-8") as f:
            for d in diff_chunks:
                f.write(d)
        changes.append(output_diff)
    return changes
