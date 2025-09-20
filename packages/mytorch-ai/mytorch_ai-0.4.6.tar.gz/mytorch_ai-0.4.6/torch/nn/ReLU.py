###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.relu_proxy import ReLUProxy
from torch.nn.Module import Module

class ReLU(Module):
    def __init__(self, inplace=False):
        super().__init__(uuid=None)
        self.proxy = ReLUProxy()

        # Call proxy to create remote module and assign UUID to this Module
        new_uuid = self.proxy.create_relu_on_server(inplace=inplace)
        self.set_uuid(new_uuid)

        # Save metadata for Sequential serialization
        self._layer_type = "ReLU"
        self._layer_params = {"inplace": inplace}

    def __call__(self, tensor):
        return self.proxy.forward(self.uuid, tensor)

    def forward(self, x):
        return self.proxy.forward(self.uuid, x)
