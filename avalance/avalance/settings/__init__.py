from .base import *

is_in_production = os.getenv('IS_IN_PRODUCTION') == 'True'
print(is_in_production)
if is_in_production is False:
    from .dev import *
else:
    from .prod import *
