from .rel_import import baz

def use():
    from .rel_import import baz
    return baz()
