######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.2+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T18:41:10.660933                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

