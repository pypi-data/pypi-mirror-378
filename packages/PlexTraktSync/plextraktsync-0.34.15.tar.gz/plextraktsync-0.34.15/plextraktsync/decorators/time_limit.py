from __future__ import annotations

from decorator import decorator

from plextraktsync.config import TRAKT_POST_DELAY
from plextraktsync.util.Timer import Timer

timer = Timer(TRAKT_POST_DELAY)


@decorator
def time_limit(fn, *args, **kwargs):
    """
    Throttles calls not to be called more often than TRAKT_POST_DELAY
    """

    timer.wait_if_needed()

    return fn(*args, **kwargs)
