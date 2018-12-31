from micropython import opt_level
opt_level(0)
# noinspection PyUnresolvedReferences
from gc import collect, mem_free
verbose = 1
if verbose:
    print('opt_level:', opt_level())
    print(mem_free())
from classes import Application
application = Application(verbose=verbose)
application.run()
collect()
if verbose:
    print(mem_free())
    print(dir())
    from sys import modules
    print(modules)
