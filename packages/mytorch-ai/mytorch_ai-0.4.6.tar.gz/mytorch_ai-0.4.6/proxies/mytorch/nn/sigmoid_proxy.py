###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.Tensor import Tensor
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class SigmoidProxy(ModuleProxy):
    def create_sigmoid_on_server(self):
        return self.generic_call(
            "torch.nn", "Sigmoid",
            call_type="constructor"
        )

    def forward(self, uuid: str, tensor: Tensor) -> Tensor:
        result_uuid, shape, dtype = self.generic_call(
            "torch.nn", "forward",
            uuid, tensor.uuid,
            call_type="method"
        )
        return Tensor(result_uuid, shape, dtype)
