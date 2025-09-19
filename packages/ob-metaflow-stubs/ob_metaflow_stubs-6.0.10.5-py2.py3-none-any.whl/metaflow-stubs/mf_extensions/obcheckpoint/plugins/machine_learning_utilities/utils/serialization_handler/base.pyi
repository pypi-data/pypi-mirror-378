######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.1+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T08:41:35.320376                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing


class SerializationHandler(object, metaclass=type):
    def serialze(self, *args, **kwargs) -> typing.Union[str, bytes]:
        ...
    def deserialize(self, *args, **kwargs) -> typing.Any:
        ...
    ...

