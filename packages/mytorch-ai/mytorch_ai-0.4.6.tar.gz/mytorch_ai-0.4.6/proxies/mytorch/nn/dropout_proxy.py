###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.Tensor import Tensor
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class DropoutProxy(ModuleProxy):
    def create_dropout_on_server(self, p=0.5, inplace=False):
        return self.generic_call(
            "torch.nn", "Dropout",
            kwargs={"p": p, "inplace": inplace},
            call_type="constructor"
        )

    def forward(self, uuid: str, tensor: Tensor) -> Tensor:
        result_uuid, shape, dtype = self.generic_call(
            "torch.nn", "forward",
            uuid, tensor.uuid,
            call_type="method"
        )
        return Tensor(result_uuid, shape, dtype)
