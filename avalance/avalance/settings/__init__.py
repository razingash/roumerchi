from .base import *

is_in_production = os.getenv('IS_IN_PRODUCTION') == 'True'

if is_in_production:
    from .dev import *
else:
    from .prod import *
