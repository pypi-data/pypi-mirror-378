
###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.Tensor import Tensor
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class FlattenProxy(ModuleProxy):
    def create_flatten_on_server(self, start_dim=1, end_dim=-1):
        return self.generic_call(
            "torch.nn", "Flatten",
            kwargs={"start_dim": start_dim, "end_dim": end_dim},
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
