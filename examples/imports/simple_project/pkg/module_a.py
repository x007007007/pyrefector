import os
def foo(x):
    return len(os.listdir(".")) + x
