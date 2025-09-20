from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import apluggy as pluggy

from plextraktsync.decorators.measure_time import measure_time
from plextraktsync.factory import logging

if TYPE_CHECKING:
    from plextraktsync.sync.Sync import Sync


class SyncPluginManager:
    logger = logging.getLogger(__name__)

    @cached_property
    def pm(self):
        from .SyncPluginInterface import SyncPluginInterface

        pm = pluggy.PluginManager("PlexTraktSync")
        pm.add_hookspecs(SyncPluginInterface)

        return pm

    @cached_property
    def ahook(self):
        return self.pm.ahook

    @cached_property
    def hook(self):
        return self.pm.hook

    @cached_property
    def unregister(self):
        return self.pm.unregister

    @property
    def plugins(self):
        from ..AddCollectionPlugin import AddCollectionPlugin
        from ..ClearCollectedPlugin import ClearCollectedPlugin
        from ..LikedListsPlugin import LikedListsPlugin
        from ..SyncRatingsPlugin import SyncRatingsPlugin
        from ..SyncWatchedPlugin import SyncWatchedPlugin
        from ..TraktListsPlugin import TraktListsPlugin
        from ..WatchListPlugin import WatchListPlugin
        from ..WatchProgressPlugin import WatchProgressPlugin

        yield AddCollectionPlugin
        yield ClearCollectedPlugin
        yield LikedListsPlugin
        yield SyncRatingsPlugin
        yield SyncWatchedPlugin
        yield TraktListsPlugin
        yield WatchListPlugin
        yield WatchProgressPlugin

    def register_plugins(self, sync: Sync):
        for plugin in self.plugins:
            enabled = plugin.enabled(sync.config)
            self.logger.info(f"Enable sync plugin '{plugin.__name__}': {enabled}")
            if not enabled:
                continue
            with measure_time(f"Created '{plugin.__name__}' plugin", logger=self.logger.debug):
                p = plugin.factory(sync)
            with measure_time(f"Registered '{plugin.__name__}' plugin", logger=self.logger.debug):
                self.pm.register(p)
