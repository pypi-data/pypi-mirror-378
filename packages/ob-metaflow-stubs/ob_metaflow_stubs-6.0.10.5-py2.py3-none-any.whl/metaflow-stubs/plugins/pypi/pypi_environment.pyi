######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.7.1+obcheckpoint(0.2.6);ob(v1)                                                    #
# Generated on 2025-09-19T08:41:35.201609                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

