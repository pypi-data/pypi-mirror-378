###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from gRPC_impl.mytorch.nn import sequential_pb2_grpc, nn_msg_types_pb2
from utils.logger import Logger
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class SequentialProxy(ModuleProxy):
    def __init__(self, layers):
        super().__init__()  # Sets up channel and module_stub
        self.sequential_stub = sequential_pb2_grpc.SequentialServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.layers = layers  # Flat list of MyTorch Modules
        self.uuid = None

    @wrap_with_error_handler
    def create_sequential_on_server(self):
        # Prepare the list of NNLayer messages
        serialized_layers = []
        layer_descriptions = []

        for i, module in enumerate(self.layers):
            if not hasattr(module, "_layer_type") or not hasattr(module, "_layer_params"):
                raise ValueError(f"Layer {i} missing _layer_type or _layer_params")

            nn_layer_msg = nn_msg_types_pb2.NNLayer()
            nn_layer_msg.type = module._layer_type

            for key, value in module._layer_params.items():
                nn_layer_msg.params.append(f"{key}={value}")

            serialized_layers.append(nn_layer_msg)
            layer_descriptions.append(f"Layer {i}: {module._layer_type}({module._layer_params})")

        # Log layer summary
        self.logger.info("Creating Sequential model with layers:\n" + "\n".join(layer_descriptions))

        # Create and send NNLayers message
        nn_layers_msg = nn_msg_types_pb2.NNLayers()
        nn_layers_msg.layers.extend(serialized_layers)

        response = self.sequential_stub.CreateSequentialModuleOnServer(nn_layers_msg)
        self.uuid = response.uuid
        return self.uuid

    @wrap_with_error_handler
    def forward(self, uuid: str, input_tensor):
        result_uuid, shape, dtype = self.generic_call(
            "torch.nn", "forward",
            uuid, input_tensor.uuid,
            call_type="method"
        )
        from torch.Tensor import Tensor
        return Tensor(result_uuid, shape, dtype)
