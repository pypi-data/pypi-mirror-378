###############################################################################
# Copyright (c) 2025 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.sigmoid_proxy import SigmoidProxy
from torch.nn.Module import Module

class Sigmoid(Module):    
    def __init__(self):
        super().__init__(uuid=None)
        self.proxy = SigmoidProxy()

        # Create remote Sigmoid and set UUID on this Module
        new_uuid = self.proxy.create_sigmoid_on_server()
        self.set_uuid(new_uuid)

        # For use in Sequential serialization
        self._layer_type = "Sigmoid"
        self._layer_params = {}

    def __call__(self, tensor):
        return self.proxy.forward(self.uuid, tensor)

    def forward(self, x):
        return self.proxy.forward(self.uuid, x)
