from torch.optim import Optimizer


def get_lr(optimizer: Optimizer):
    if optimizer is not None:
        if len(optimizer.param_groups) == 1:
            return optimizer.param_groups[0]["lr"]
        lrs = [param_group["lr"] for param_group in optimizer.param_groups]
        return lrs
    raise ValueError("Optimizer is None")
