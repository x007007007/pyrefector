def use():
    try:
        import pkg.opt
        v = pkg.opt.value
    except ImportError:
        v = 0
    except ValueError:
        v = -1
    else:
        v += 1
    finally:
        pass
    return v
