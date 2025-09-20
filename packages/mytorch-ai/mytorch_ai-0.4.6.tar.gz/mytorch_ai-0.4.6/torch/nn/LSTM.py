###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################


from torch.nn.Module import Module
from torch.Tensor import Tensor
from proxies.mytorch.nn.lstm_proxy import LSTMProxy

class LSTM(Module):
    def __init__(self, input_size, hidden_size, num_layers=1, bias=True, batch_first=False,
                 dropout=0.0, bidirectional=False):
        super().__init__(uuid=None)
        self.proxy = LSTMProxy()

        # Call proxy to create LSTM on server
        new_uuid = self.proxy.create_lstm_on_server(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            bias=bias,
            batch_first=batch_first,
            dropout=dropout,
            bidirectional=bidirectional
        )
        self.set_uuid(new_uuid)

        # Save all parameters for serialization
        self._layer_type = "LSTM"
        self._layer_params = {
            "input_size": input_size,
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "bias": bias,
            "batch_first": batch_first,
            "dropout": dropout,
            "bidirectional": bidirectional
        }

    # LSTM returns (output, (h_n, c_n)).
    def forward(self, input: Tensor, hx=None):
        return self.proxy.forward(self.uuid, input, hx)

    def __call__(self, input: Tensor, hx=None):
        return self.forward(input, hx)

