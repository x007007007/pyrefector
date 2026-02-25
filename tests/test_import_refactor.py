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
