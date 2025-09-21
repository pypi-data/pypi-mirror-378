from .assoview import *

import warnings
import datetime

# 1) Suppress the deprecation warning in output
warnings.filterwarnings(
    "ignore",
    message="datetime.datetime.utcnow.*",
    category=DeprecationWarning,
)

# 2) Monkey patch datetime.utcnow to be timezone-aware
datetime.utcnow = lambda: datetime.datetime.now(datetime.timezone.utc)


