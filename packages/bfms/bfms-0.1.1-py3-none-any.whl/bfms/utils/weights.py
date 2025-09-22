import torch
import torch.nn as nn


def trunc_normal_(tensor: torch.Tensor,
                  mean: float = 0.0,
                  std: float = 1.0):
    nn.init.trunc_normal_(tensor, mean=mean, std=std, a=-std, b=std)
    return tensor


def init_weights_(m: nn.Module,
                  init_std: float = 0.02):
    if isinstance(m, nn.Linear):
        trunc_normal_(m.weight, std=init_std)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.LayerNorm):
        nn.init.constant_(m.bias, 0)
        nn.init.constant_(m.weight, 1.0)
    elif isinstance(m, nn.Conv2d):
        trunc_normal_(m.weight, std=init_std)
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)