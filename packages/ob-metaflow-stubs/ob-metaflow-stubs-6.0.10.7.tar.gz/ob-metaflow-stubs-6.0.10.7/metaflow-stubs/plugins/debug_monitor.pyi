######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.2+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T18:41:10.627493                                                            #
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

