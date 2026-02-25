from .impl import foo

def bar():
    from pkg2.utils import helper
    return foo(helper())
