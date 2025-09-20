###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.Tensor import Tensor

class ParametersGenerator:
    """
    Wraps a model UUID and allows iteration over its parameters.
    Uses ModuleProxy and generic_call to get parameter list.
    """

    def __init__(self, uuid: str):
        self.uuid = uuid
        self.proxy = ModuleProxy()
        self.proxy.uuid = uuid  # Set the UUID so .parameters() works

    def __iter__(self):
        return iter(self.proxy.parameters())
