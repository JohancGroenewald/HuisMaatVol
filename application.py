"""
HuisMaat Application

Update history
--------------
20190910.1250: Created
"""
from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

from config import CONFIG
import run

run_loop = run.RunLoop(CONFIG, verbose=1)
# noinspection PyBroadException
try:
    run_loop.run()
except Exception as e:
    import sys

    # noinspection PyUnresolvedReferences
    sys.print_exception(e)
finally:
    run_loop.close()
    import unload
