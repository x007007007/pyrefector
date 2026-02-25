try:
    import pkg2.utils
    from pkg1.mod2.rel_import import baz
    value = 42
except ImportError:
    value = 0

def foo(x):
    from pkg2.utils import helper
    return x * helper()
