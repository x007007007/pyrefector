import sys

def helper():
    return len(sys.version_info)

def fallback():
    from pkg1.mod1.impl import value
    return value
