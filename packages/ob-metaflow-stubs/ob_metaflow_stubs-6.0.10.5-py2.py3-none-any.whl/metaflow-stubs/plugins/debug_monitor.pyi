######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.1+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T08:41:35.173474                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.monitor


class DebugMonitor(metaflow.monitor.NullMonitor, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugMonitorSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

