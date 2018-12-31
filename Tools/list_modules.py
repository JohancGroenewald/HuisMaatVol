import sys

print('--[OBJECTS]--------------------------------------------------')
objects = dir()
objects.sort()
for datum in objects:
    print(datum)

print('--[MODULES]--------------------------------------------------')
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
