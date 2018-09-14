"""
HuisMaat Application

Update history
--------------
20190910.1250: Created
"""
from micropython import opt_level, mem_info
print('{} opt_level: {}'.format(__name__, opt_level()))

print('-' * 69)
print('{}\n{}'.format(mem_info(), '-' * 69))
from gc import collect
collect()

from config import CONFIG
from run import RunLoop

run_loop = RunLoop(CONFIG, verbose=1)
# noinspection PyBroadException
try:
    print('-' * 69)
    print('{}\n{}'.format(mem_info(), '-' * 69))
    collect()
    run_loop.run()
except Exception as e:
    import sys

    # noinspection PyUnresolvedReferences
    sys.print_exception(e)
finally:
    run_loop.close()
    import unload
