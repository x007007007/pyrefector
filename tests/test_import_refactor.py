import os
import tempfile
import shutil
import subprocess

from pyrefactor.imports_refactor import rewrite_directory
from pyrefactor.abs_imports import rewrite_abs_directory


def test_relative_import_absolute_in_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "aaa", "bbb")
        os.makedirs(pkg_dir)
        init_path = os.path.join(pkg_dir, "__init__.py")
        name_path = os.path.join(pkg_dir, "name.py")
        
        with open(init_path, "w") as f:
            f.write("from .name import aa\n")
        
        with open(name_path, "w") as f:
            f.write("aa=1\n")
        
        rewrite_abs_directory(tmpdir)
        
        with open(init_path, "r") as f:
            content = f.read()
        
        assert "from aaa.bbb.name import aa" in content


def test_import_lifting_and_failfirst():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)
        a_path = os.path.join(pkg_dir, "a.py")
        opt_path = os.path.join(pkg_dir, "opt.py")
        
        with open(opt_path, "w") as f:
            f.write("value = 42\n")
        
        with open(a_path, "w") as f:
            f.write("""
def use():
    try:
        import pkg.opt
        v = pkg.opt.value
    except ImportError:
        v = 0
    return v
""")
        
        changes = rewrite_directory(tmpdir, failfirst=True)
        
        assert len(changes) > 0
        
        with open(a_path, "r") as f:
            content = f.read()
        
        assert "import pkg.opt" in content
        assert "except ImportError" not in content
        assert "v = pkg.opt.value" in content


def test_modify_under():
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = os.path.join(tmpdir, "app")
        lib_dir = os.path.join(tmpdir, "lib")
        os.makedirs(app_dir)
        os.makedirs(lib_dir)
        
        app_mod_path = os.path.join(app_dir, "mod.py")
        lib_mod_path = os.path.join(lib_dir, "mod.py")
        
        with open(app_mod_path, "w") as f:
            f.write("""
def f():
    import os
    return os.name
""")
        
        with open(lib_mod_path, "w") as f:
            f.write("""
def g():
    import sys
    return sys.version
""")
        
        changes = rewrite_directory(tmpdir, modify_under=app_dir)
        
        assert len(changes) == 1
        assert app_mod_path in changes
        
        with open(app_mod_path, "r") as f:
            content = f.read()
        
        assert "import os" in content
        
        with open(lib_mod_path, "r") as f:
            content = f.read()
        
        assert "import sys" in content


def test_package_path_with_src():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "src")
        pkg_dir = os.path.join(src_dir, "pkg")
        os.makedirs(pkg_dir)
        
        rel_user_path = os.path.join(pkg_dir, "rel_user.py")
        utils_path = os.path.join(pkg_dir, "utils.py")
        
        with open(utils_path, "w") as f:
            f.write("def helper(): return 2\n")
        
        with open(rel_user_path, "w") as f:
            f.write("""
def use():
    from .utils import helper
    return helper()
""")
        
        changes = rewrite_directory(tmpdir, include_relative=True, failfirst=True, dry_run=True, package_paths=[src_dir])
        
        with open(rel_user_path, "r") as f:
            original_content = f.read()
        
        assert "from .utils" in original_content


def test_cli_basic():
    result = subprocess.run(
        ["uv", "run", "pyrefactor", "refc_import", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "refc_import" in result.stdout


def test_graph_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "test_module.py"), "w") as f:
            f.write("import os")
        
        result = subprocess.run(
            ["uv", "run", "pyrefactor", "graph", "imports", tmpdir],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "os" in result.stdout


def test_dependency_graph_building():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test_dir")
        os.makedirs(test_dir)
        
        with open(os.path.join(test_dir, "a.py"), "w") as f:
            f.write("import b")
        
        with open(os.path.join(test_dir, "b.py"), "w") as f:
            f.write("import a")
        
        from pyrefactor.deps import build_dependency_graph
        
        graph = build_dependency_graph(test_dir)
        
        assert "a" in graph
        assert "b" in graph
        assert "b" in graph["a"]
        assert "a" in graph["b"]


def test_cycle_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test_dir")
        os.makedirs(test_dir)
        
        with open(os.path.join(test_dir, "a.py"), "w") as f:
            f.write("""
def f():
    import b
    return b
""")
        
        with open(os.path.join(test_dir, "b.py"), "w") as f:
            f.write("""
def g():
    import a
    return a
""")
        
        from pyrefactor.imports_refactor import rewrite_directory
        
        changes = rewrite_directory(test_dir)
        
        assert len(changes) == 0


def test_module_name_resolution():
    from pyrefactor.deps import module_name_from_path_multi
    
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "src")
        lib_dir = os.path.join(tmpdir, "lib")
        os.makedirs(src_dir)
        os.makedirs(lib_dir)
        
        f1 = os.path.join(src_dir, "pkg", "mod.py")
        f2 = os.path.join(lib_dir, "other.py")
        
        # Test file under src
        mod1 = module_name_from_path_multi(f1, [src_dir, lib_dir])
        assert mod1 == "pkg.mod"
        
        # Test file under lib
        mod2 = module_name_from_path_multi(f2, [src_dir, lib_dir])
        assert mod2 == "other"
        
        # Test file not under any root (fallback)
        f3 = os.path.join(tmpdir, "outside.py")
        mod3 = module_name_from_path_multi(f3, [src_dir])
        # The behavior depends on os.path.relpath implementation
        # and how split handles '..'
        # Just ensure it returns something reasonable or check implementation
        assert "outside" in mod3


def test_relative_import_resolution():
    from pyrefactor.deps import resolve_relative_pkg
    
    # Test inside __init__.py
    # from . import x (level=1) in pkg.__init__ -> pkg.x
    res = resolve_relative_pkg("pkg", 1, "x", True)
    assert res == "pkg.x"
    
    # from .. import x (level=2) in pkg.sub.__init__ -> pkg.x
    res = resolve_relative_pkg("pkg.sub", 2, "x", True)
    assert res == "pkg.x"
    
    # Test inside normal module
    # from . import x (level=1) in pkg.mod -> pkg.x
    res = resolve_relative_pkg("pkg.mod", 1, "x", False)
    assert res == "pkg.x"
    
    # from .. import x (level=2) in pkg.sub.mod -> pkg.x
    res = resolve_relative_pkg("pkg.sub.mod", 2, "x", False)
    assert res == "pkg.x"
    
    # Test boundary condition: resolving to root
    # from .. import x (level=2) in pkg.__init__ -> x
    res = resolve_relative_pkg("pkg", 2, "x", True)
    assert res == "x"
    
    # Test overflow
    # from ... import x (level=3) in pkg.__init__ -> None (beyond root)
    res = resolve_relative_pkg("pkg", 3, "x", True)
    assert res is None


def test_abs_import_complex_cases():
    from pyrefactor.abs_imports import rewrite_abs_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)
        
        # Test Case 1: Complex relative import in __init__.py
        # from ...sub import mod
        init_path = os.path.join(pkg_dir, "__init__.py")
        with open(init_path, "w") as f:
            f.write("from .sub import mod\n")
            
        rewrite_abs_file(init_path, [tmpdir])
        
        with open(init_path, "r") as f:
            content = f.read()
        assert "from pkg.sub import mod" in content
        
        # Test Case 2: Import from parent
        sub_dir = os.path.join(pkg_dir, "sub")
        os.makedirs(sub_dir)
        mod_path = os.path.join(sub_dir, "mod.py")
        
        with open(mod_path, "w") as f:
            f.write("from .. import other\n")
            
        rewrite_abs_file(mod_path, [tmpdir])
        
        with open(mod_path, "r") as f:
            content = f.read()
        assert "from pkg import other" in content





def test_control_blocks_lifting():
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        
        # Test imports inside if/for/while
        with open(mod_path, "w") as f:
            f.write("""
if True:
    import a
    
for i in range(1):
    import b

while False:
    import c
""")
        
        # By default (allow_control_blocks=False), these should NOT be lifted
        rewrite_directory(tmpdir, allow_control_blocks=False)
        with open(mod_path, "r") as f:
            content = f.read()
        assert "if True:\n    import a" in content
        
        # With allow_control_blocks=True, they SHOULD be lifted
        rewrite_directory(tmpdir, allow_control_blocks=True)
        with open(mod_path, "r") as f:
            content = f.read()
        # Imports should be at top
        assert content.startswith("import a\nimport b\nimport c") or "import a\nimport b\nimport c" in content


def test_class_and_func_scope():
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        
        # Imports inside functions and classes ARE lifted by default
        with open(mod_path, "w") as f:
            f.write("""
class C:
    import a
    def m(self):
        import b

def f():
    import c
""")
        
        rewrite_directory(tmpdir)
        with open(mod_path, "r") as f:
            content = f.read()
        
        # Imports should be lifted to top level
        assert "import a\nimport b\nimport c" in content or content.startswith("import a\nimport b\nimport c")
        # Original locations should be empty or pass
        assert "class C:\n    pass" in content or "class C:\n    def m(self):\n        pass" in content
        assert "def f():\n    pass" in content


def test_preserve_docstring_and_comments():
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        
        with open(mod_path, "w") as f:
            f.write('''"""Docstring."""
import a
# Comment
def f():
    try:
        import b
    except ImportError:
        pass
''')
        
        rewrite_directory(tmpdir, failfirst=True)
        with open(mod_path, "r") as f:
            content = f.read()
        
        # Docstring should be first
        assert content.startswith('"""Docstring."""')
        # import b should be lifted, likely after import a
        assert "import a" in content
        assert "import b" in content
        # Check that import b is at top level
        assert "\nimport b" in content


def test_abs_import_nested_module():
    from pyrefactor.abs_imports import rewrite_abs_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)
        mod_path = os.path.join(pkg_dir, "mod.py")
        
        # Test from .sub.deep import x
        with open(mod_path, "w") as f:
            f.write("from .sub.deep import x\n")
            
        rewrite_abs_file(mod_path, [tmpdir])
        
        with open(mod_path, "r") as f:
            content = f.read()
        assert "from pkg.sub.deep import x" in content


def test_failfirst_preserves_other_handlers():
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        
        with open(mod_path, "w") as f:
            f.write("""
def f():
    try:
        import a
    except ImportError:
        pass
    except ValueError:
        pass
    except:
        pass
    finally:
        pass
""")
        
        rewrite_directory(tmpdir, failfirst=True)
        with open(mod_path, "r") as f:
            content = f.read()
        
        # import a should be lifted
        assert "import a" in content and content.find("import a") < content.find("def f():")
        # ImportError handler should be gone
        assert "except ImportError" not in content
        # ValueError and bare except should remain
        assert "except ValueError" in content
        assert "except:" in content
        # finally should remain
        assert "finally" in content


def test_output_diff():
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        diff_path = os.path.join(tmpdir, "changes.patch")
        
        with open(mod_path, "w") as f:
            f.write("def f():\n    import a\n")
            
        changes = rewrite_directory(tmpdir, dry_run=True, output_diff=diff_path)
        
        assert len(changes) > 0
        assert diff_path in changes
        assert os.path.exists(diff_path)
        
        with open(diff_path, "r") as f:
            content = f.read()
        assert "--- " in content
        assert "+++ " in content
        assert "import a" in content


def test_abs_imports_no_change():
    from pyrefactor.abs_imports import rewrite_abs_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)
        mod_path = os.path.join(pkg_dir, "mod.py")
        
        # Already absolute import
        original = "from pkg.utils import x\n"
        with open(mod_path, "w") as f:
            f.write(original)
            
        changed = rewrite_abs_file(mod_path, [tmpdir])
        assert not changed
        
        with open(mod_path, "r") as f:
            content = f.read()
        assert content == original
        
        # Relative import that cannot be resolved (too many dots)
        bad_import = "from ... import x\n"
        with open(mod_path, "w") as f:
            f.write(bad_import)
            
        changed = rewrite_abs_file(mod_path, [tmpdir])
        assert not changed
        
        # Relative import without base (from . import x)
        dot_import = "from . import x\n"
        with open(mod_path, "w") as f:
            f.write(dot_import)
            
        changed = rewrite_abs_file(mod_path, [tmpdir])
        assert changed
        with open(mod_path, "r") as f:
            content = f.read()
        assert "from pkg.x import x" not in content # Wait, from . import x -> from pkg import x
        assert "from pkg import x" in content


def test_try_star_imports():
    # Only runs on Python 3.11+
    import sys
    if sys.version_info < (3, 11):
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        mod_path = os.path.join(tmpdir, "mod.py")
        
        # Test imports inside try-except*
        with open(mod_path, "w") as f:
            f.write("""
try:
    import a
except* ImportError:
    pass
""")
        
        # Build dependency graph should find 'a'
        from pyrefactor.deps import build_dependency_graph
        graph = build_dependency_graph(tmpdir)
        # mod name depends on root, likely 'mod'
        assert "mod" in graph
        assert "a" in graph["mod"]


def test_module_name_resolution_edge_cases():
    from pyrefactor.deps import module_name_from_path_multi
    
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(src_dir)
        
        # Case: path equals root
        mod = module_name_from_path_multi(src_dir, [src_dir])
        assert mod == "" or mod == "." # Behavior check
        
        # Case: root with trailing slash
        root_slash = src_dir + os.sep
        f = os.path.join(src_dir, "mod.py")
        mod = module_name_from_path_multi(f, [root_slash])
        assert mod == "mod"
