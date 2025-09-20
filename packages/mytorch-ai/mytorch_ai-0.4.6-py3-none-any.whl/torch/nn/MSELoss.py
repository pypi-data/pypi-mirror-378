###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.nn.Module import Module
from torch.Tensor import Tensor

class MSELoss(Module):
    def __init__(self, reduction="mean"):
        super().__init__(uuid=None)
        self.reduction = reduction
        self.proxy = ModuleProxy()

        # Construct remote MSELoss and store UUID
        new_uuid = self.proxy.generic_call(
            "torch.nn", "MSELoss",
            call_type="constructor",
            kwargs={"reduction": self.reduction}
        )
        self.set_uuid(new_uuid)

        # Required for serialization in Sequential
        self._layer_type = "MSELoss"
        self._layer_params = {"reduction": self.reduction}

    def forward(self, input: Tensor, target: Tensor):
        result = self.proxy.generic_call(
            "torch.nn", "forward",
            self.uuid, input.uuid, target.uuid,
            call_type="method"
        )
        uuid, shape, dtype = result
        return Tensor(uuid, shape, dtype)

    def __call__(self, input: Tensor, target: Tensor):
        return self.forward(input, target)
