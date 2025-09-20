###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################


from proxies.mytorch.nn.linear_proxy import LinearProxy
from torch.nn.Module import Module
from torch.Tensor import Tensor

class Linear(Module):
    def __init__(self, in_features, out_features):
        super().__init__(uuid=None)
        self.proxy = LinearProxy()

        # Construct remote Linear and store UUID locally
        new_uuid = self.proxy.create_linear_on_server(in_features, out_features)
        self.set_uuid(new_uuid)

        # Required metadata for serialization
        self._layer_type = "Linear"
        self._layer_params = {
            "in_features": in_features,
            "out_features": out_features
        }

    def forward(self, x: Tensor) -> Tensor:
        return self.proxy.forward(self.uuid, x)

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)
