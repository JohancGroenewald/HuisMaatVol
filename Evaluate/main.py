# verbose = 0
run_app = True
if run_app:
    import app
    # if verbose:
    #     print('dir(main):', dir())
    del app
from sys import modules
for module in modules:
    # if verbose:
    #     print('#(main) ', module)
    del modules[module]
# noinspection PyUnboundLocalVariable
del module
del modules
del run_app
import gc
gc.collect()
# if verbose:
#     # noinspection PyUnresolvedReferences
#     print('mem_free(main): ', gc.mem_free())
#     print('dir(main):', dir())
# del verbose
