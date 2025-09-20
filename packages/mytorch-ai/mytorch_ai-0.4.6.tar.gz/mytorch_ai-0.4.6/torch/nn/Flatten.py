###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.flatten_proxy import FlattenProxy
from torch.nn.Module import Module

class Flatten(Module):
    def __init__(self, start_dim=1, end_dim=-1):
        super().__init__(uuid=None)
        self.start_dim = start_dim
        self.end_dim = end_dim
        self.proxy = FlattenProxy()

        # Construct Flatten remotely
        new_uuid = self.proxy.create_flatten_on_server(start_dim=self.start_dim, end_dim=self.end_dim)
        self.set_uuid(new_uuid)

        # For Sequential serialization
        self._layer_type = "Flatten"
        self._layer_params = {
            "start_dim": self.start_dim,
            "end_dim": self.end_dim
        }

    def forward(self, x):
        return self.proxy.forward(self.uuid, x)

    def __call__(self, x):
        return self.forward(x)
