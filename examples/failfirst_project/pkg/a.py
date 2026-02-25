def use():
    try:
        import pkg.opt
        return pkg.opt.value
    except ImportError:
        x = 1
        return x
