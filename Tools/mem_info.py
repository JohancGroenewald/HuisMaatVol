import micropython
micropython.mem_info()

from sys import modules
if __name__ in modules:
    del modules[__name__]
