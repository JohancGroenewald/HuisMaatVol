run_app = True
if run_app:
    import app
    del app
from sys import modules
for module in modules:
    del modules[module]
del modules
del run_app
__import__('gc').collect()
import wifi_restore
