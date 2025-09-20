###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################


from torch.Tensor import Tensor
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class LinearProxy(ModuleProxy):
    def create_linear_on_server(self, in_features, out_features):
        return self.generic_call(
            "torch.nn", "Linear",
            in_features, out_features,
            call_type="constructor"
        )

    def forward(self, uuid: str, tensor: Tensor) -> Tensor:
        result_uuid, shape, dtype = self.generic_call(
            "torch.nn", "forward",
            uuid, tensor.uuid,
            call_type="method"
        )
        return Tensor(result_uuid, shape, dtype)

    #def delete(self, uuid: str):
    #    return self.generic_call("mytorch.internal", "delete", uuid, call_type="method")
