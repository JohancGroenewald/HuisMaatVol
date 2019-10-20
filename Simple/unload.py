# noinspection PyUnresolvedReferences
import sys
import gc

for module in sys.modules:
    del sys.modules[module]

gc.collect()

print('mem_free ...', gc.mem_free())

print(dir())
