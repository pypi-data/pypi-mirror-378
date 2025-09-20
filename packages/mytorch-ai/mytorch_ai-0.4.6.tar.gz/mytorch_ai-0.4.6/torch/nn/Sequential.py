###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################


from torch.nn.Module import Module
from proxies.mytorch.nn.sequential_proxy import SequentialProxy

class Sequential(Module):
    def __init__(self, *args):
        super().__init__(uuid=None)

        # Save layers
        self.layers = []
        for idx, layer in enumerate(args):
            if not isinstance(layer, Module):
                raise TypeError(f"Sequential only accepts MyTorch Module instances, got: {type(layer)}")
            if not hasattr(layer, "_layer_type") or not hasattr(layer, "_layer_params"):
                raise ValueError(f"Layer {layer} is missing _layer_type or _layer_params")
            self.layers.append(layer)

        # Step 1: Call proxy to create remote Sequential (get UUID FIRST)
        self.proxy = SequentialProxy(self.layers)
        new_uuid = self.proxy.create_sequential_on_server()
        self.set_uuid(new_uuid)

        # Step 2: Register layers using setattr AFTER UUID is set
        for idx, layer in enumerate(self.layers):
            setattr(self, f"layer_{idx}", layer)

        # Step 3: Save metadata
        self._layer_type = "Sequential"
        self._layer_params = {
            "num_layers": len(self.layers)
        }

    def forward(self, input_data):
        return self.proxy.forward(self.uuid, input_data)

    def __call__(self, input_data):
        return self.forward(input_data)
