###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.dropout_proxy import DropoutProxy
from torch.Tensor import Tensor
from torch.nn.Module import Module

class Dropout(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__(uuid=None)
        self.p = p
        self.inplace = inplace
        self.proxy = DropoutProxy()

        # Ask proxy to create the remote Dropout module and assign UUID
        new_uuid = self.proxy.create_dropout_on_server(p=self.p, inplace=self.inplace)
        self.set_uuid(new_uuid)

        # Required for Sequential serialization
        self._layer_type = "Dropout"
        self._layer_params = {"p": self.p, "inplace": self.inplace}

    def __call__(self, tensor: Tensor):
        return self.proxy.forward(self.uuid, tensor)

    def forward(self, x: Tensor):
        return self.proxy.forward(self.uuid, x)
