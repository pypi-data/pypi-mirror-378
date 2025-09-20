######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.2+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T18:41:10.602431                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from .....exception import MetaflowException as MetaflowException

class UnspecifiedRemoteStorageRootException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, message):
        ...
    ...

class EmptyOllamaManifestCacheException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, message):
        ...
    ...

class EmptyOllamaBlobCacheException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, message):
        ...
    ...

