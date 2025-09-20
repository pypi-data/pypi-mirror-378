###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.optim.optimizer_proxy import OptimizerProxy
from torch.nn.ParametersGenerator import ParametersGenerator

class SGD:
    def __init__(self, generator: ParametersGenerator, lr: float, momentum: float = 0):
        self.proxy = OptimizerProxy()
        param_uuids = [p.uuid for p in generator]
        self.uuid = self.proxy.generic_call(
            "torch.optim", "SGD",
            param_uuids,
            call_type="constructor",
            kwargs={"lr": lr, "momentum": momentum}
        )

    def zero_grad(self):
        self.proxy.zero_grad()

    def step(self):
        self.proxy.step()



