###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.nn.Module import Module
from torch.Tensor import Tensor

class CrossEntropyLoss(Module):
    def __init__(self, weight: Tensor = None, ignore_index=-100, reduction='mean', label_smoothing=0.0):
        super().__init__(uuid=None)
        self.proxy = ModuleProxy()

        # Save all parameters
        self._layer_type = "CrossEntropyLoss"
        self._layer_params = {
            "ignore_index": ignore_index,
            "reduction": reduction,
            "label_smoothing": label_smoothing
        }

        # Construct kwargs, handling tensor UUID for weight
        kwargs = self._layer_params.copy()
        if weight is not None:
            kwargs["weight"] = weight.uuid  # must be a Tensor with .uuid

        # Create remote loss module using generic_call
        new_uuid = self.proxy.generic_call(
            "torch.nn", "CrossEntropyLoss",
            call_type="constructor",
            kwargs=kwargs
        )
        self.set_uuid(new_uuid)

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        uuid, shape, dtype = self.proxy.generic_call(
            "torch.nn", "forward",
            self.uuid, input.uuid, target.uuid,
            call_type="method"
        )
        return Tensor(uuid, shape, dtype)

    def __call__(self, input: Tensor, target: Tensor) -> Tensor:
        return self.forward(input, target)
