import os
import ast
from typing import Dict, List, Set, Tuple


def _py_files(root: str) -> List[str]:
    paths: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".py"):
                paths.append(os.path.join(dirpath, fn))
    return paths


def _module_name_from_path(path: str, root: str) -> str:
    rel = os.path.relpath(path, root)
    no_ext = os.path.splitext(rel)[0]
    parts = []
    for p in no_ext.split(os.sep):
        if p == "__init__":
            continue
        parts.append(p)
    return ".".join(parts)


def build_import_graph_mermaid(root: str) -> str:
    files = _py_files(root)
    nodes: Set[str] = set()
    edges: Set[Tuple[str, str]] = set()
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src)
        except Exception:
            continue
        mod = _module_name_from_path(f, root)
        nodes.add(mod)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.add((mod, alias.name))
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level and base:
                    edges.add((mod, "." * node.level + base))
                elif base:
                    edges.add((mod, base))
    lines = ["graph TD"]
    for n in sorted(nodes):
        lines.append(f'    "{n}"')
    for a, b in sorted(edges):
        lines.append(f'    "{a}" --> "{b}"')
    return "\n".join(lines)


def build_call_graph_mermaid(root: str) -> str:
    files = _py_files(root)
    edges: Set[Tuple[str, str]] = set()
    nodes: Set[str] = set()
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src)
        except Exception:
            continue
        mod = _module_name_from_path(f, root)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                caller = f"{mod}.{node.name}"
                nodes.add(caller)
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        if isinstance(inner.func, ast.Name):
                            callee = inner.func.id
                        elif isinstance(inner.func, ast.Attribute):
                            parts = []
                            cur = inner.func
                            while isinstance(cur, ast.Attribute):
                                parts.append(cur.attr)
                                cur = cur.value
                            if isinstance(cur, ast.Name):
                                parts.append(cur.id)
                                parts.reverse()
                                callee = ".".join(parts)
                            else:
                                callee = "call"
                        else:
                            callee = "call"
                        edges.add((caller, callee))
    lines = ["graph TD"]
    for n in sorted(nodes):
        lines.append(f'    "{n}"')
    for a, b in sorted(edges):
        lines.append(f'    "{a}" --> "{b}"')
    return "\n".join(lines)


def build_function_flow_mermaid(path: str, function_name: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except Exception:
        return ""
    mod = os.path.splitext(os.path.basename(path))[0]
    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            target = node
            break
    if target is None:
        return ""
    nodes: List[str] = []
    edges: List[Tuple[str, str]] = []
    counter = 0
    def nid() -> str:
        nonlocal counter
        counter += 1
        return f"N{counter}"
    start = nid()
    nodes.append(f'{start}["start {mod}.{function_name}"]')
    prev = start
    for stmt in target.body:
        if isinstance(stmt, ast.If):
            cond = nid()
            nodes.append(f'{cond}{{if}}')
            edges.append((prev, cond))
            tnode = nid()
            fnode = nid()
            nodes.append(f'{tnode}["then"]')
            nodes.append(f'{fnode}["else"]')
            edges.append((cond, tnode))
            edges.append((cond, fnode))
            prev = nid()
            nodes.append(f'{prev}["merge"]')
            edges.append((tnode, prev))
            edges.append((fnode, prev))
        elif isinstance(stmt, (ast.For, ast.While)):
            loop = nid()
            nodes.append(f'{loop}(["loop"])')
            edges.append((prev, loop))
            body = nid()
            nodes.append(f'{body}["body"]')
            edges.append((loop, body))
            prev = loop
        elif isinstance(stmt, ast.Try):
            tri = nid()
            nodes.append(f'{tri}{{try}}')
            edges.append((prev, tri))
            for h in stmt.handlers:
                hnode = nid()
                nodes.append(f'{hnode}["except"]')
                edges.append((tri, hnode))
            fnode = nid()
            nodes.append(f'{fnode}["finally"]')
            edges.append((tri, fnode))
            prev = fnode
        else:
            step = nid()
            nodes.append(f'{step}["stmt"]')
            edges.append((prev, step))
            prev = step
    end = nid()
    nodes.append(f'{end}["end"]')
    edges.append((prev, end))
    lines = ["flowchart TD"]
    for n in nodes:
        lines.append(f"    {n}")
    for a, b in edges:
        lines.append(f"    {a} --> {b}")
    return "\n".join(lines)
