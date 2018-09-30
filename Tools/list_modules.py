import sys

modules = [module for module in sys.modules]
modules.sort()
for module in modules:
    if module == 'list_modules':
        print('* {}'.format(module))
    else:
        print(module)

from sys import modules
if __name__ in modules:
    del modules[__name__]
