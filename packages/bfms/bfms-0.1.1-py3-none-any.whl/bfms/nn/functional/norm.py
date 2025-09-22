import torch
import torch.nn.functional as F

def l2norm(t: torch.Tensor) -> torch.Tensor:
    """
    Unit L2 Normalization along the last dimension of the tensor t.
    (*, ..., D)
    """
    return F.normalize(t, p=2, dim=-1)