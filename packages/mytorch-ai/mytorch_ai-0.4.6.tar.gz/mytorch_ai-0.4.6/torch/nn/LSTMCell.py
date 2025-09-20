###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.nn.Module import Module
from torch.Tensor import Tensor
from proxies.mytorch.nn.module_proxy import ModuleProxy

class LSTMCell(Module):
    def __init__(self, input_size, hidden_size, bias=True):
        super().__init__(uuid=None)
        self.proxy = ModuleProxy()

        # Register remote LSTMCell and set UUID
        new_uuid = self.proxy.generic_call(
            "torch.nn", "LSTMCell",
            input_size, hidden_size, bias,
            call_type="constructor"
        )
        self.set_uuid(new_uuid)

        # For serialization
        self._layer_type = "LSTMCell"
        self._layer_params = {
            "input_size": input_size,
            "hidden_size": hidden_size,
            "bias": bias
        }

    def forward(self, input: Tensor, hx: tuple) -> tuple:
        h, c = hx
        result = self.proxy.generic_call(
            "torch.nn", "forward",
            self.uuid, input.uuid, h.uuid, c.uuid,
            call_type="method"
        )
        h_info, c_info = result
        return Tensor(*h_info), Tensor(*c_info)

    def __call__(self, input: Tensor, hx: tuple) -> tuple:
        return self.forward(input, hx)
