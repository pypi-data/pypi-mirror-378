
###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.optim.optimizer_proxy import OptimizerProxy

class LBFGS:
    def __init__(self, params, lr=1.0, max_iter=20, max_eval=None, tolerance_grad=1e-5,
                 tolerance_change=1e-9, history_size=100, line_search_fn=None):
        self.proxy = OptimizerProxy()
        param_uuids = [p.uuid for p in params]
        self.uuid = self.proxy.generic_call(
            "torch.optim", "LBFGS",
            param_uuids,
            call_type="constructor",
            kwargs={
                "lr": lr,
                "max_iter": max_iter,
                "max_eval": max_eval,
                "tolerance_grad": tolerance_grad,
                "tolerance_change": tolerance_change,
                "history_size": history_size,
                "line_search_fn": line_search_fn
            }
        )

    def step(self, closure):
        # Do not call .step() on the server — LBFGS will break
        # You’ve already done the gradient update
        # If needed, consider a no-op call or logging
        return #self.proxy.generic_call("torch.optim", "step", self.uuid, call_type="method")
        # ? return closure() ? MAYBE THIS?

    def zero_grad(self):
        return self.proxy.generic_call("torch.optim", "zero_grad", self.uuid, call_type="method")
