from micropython import opt_level
opt_level(0)
# noinspection PyUnresolvedReferences
from gc import collect, mem_free
verbose = 1
if verbose:
    print('opt_level:', opt_level())
    print(mem_free())
collect()
if verbose:
    print(mem_free())
from classes import Application
application = Application(verbose=verbose)
collect()
if verbose:
    print(mem_free())
application.run(watch_dog=10)
if verbose:
    print(mem_free())

from sys import modules
for name in ['main', 'app', 'classes', 'mqtt']:
    if name in modules:
        del modules[name]

collect()
if verbose:
    print(mem_free())
