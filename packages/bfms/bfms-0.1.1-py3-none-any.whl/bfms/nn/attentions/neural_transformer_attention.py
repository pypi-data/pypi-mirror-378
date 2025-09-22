import torch
import torch.nn as nn
import torch.nn.functional as F


__all__ = ["NeuralTransformerAttention"]

class RelativePositionBias(nn.Module):
    def __init__(self, window_size: tuple[int, int], num_heads: int):
        super().__init__()
        
        self.window_size = window_size
        H, W = self.window_size
        
        self.num_relative_distance = (2 * H - 1) * (2 * W - 1) + 3
        
        self.relative_position_bias_table = nn.Parameter(torch.zeros(
            self.num_relative_distance, num_heads
        ))  # (2*W-1) * (2*H-1) + 3, num_heads
        
        # cls to token & token to cls & cls to cls

        # get pair-wise relative position index for each token inside the window
        coords_h = torch.arange(H) # H
        coords_w = torch.arange(W) # W
        
        coords_h, coords_w = torch.meshgrid([coords_h, coords_w]) # Each is H, W
        
        coords_h = coords_h.flatten()  # H*W
        coords_w = coords_w.flatten()  # H*W
        
        relative_coords_h = coords_h[:, None] - coords_h[None, :]  # H*W, H*W
        relative_coords_w = coords_w[:, None] - coords_w[None, :]  # H*W, H*W
        
        relative_coords_h += H - 1  # shift to start from 0
        relative_coords_w += W - 1
        relative_coords_h *= 2 * W - 1
        
        relative_position_index = torch.zeros(
            size=(H*W + 1, ) * 2, dtype=relative_coords_h.dtype
        )
        relative_position_index[1:, 1:] = relative_coords_h + relative_coords_w  # H*W, H*W
        relative_position_index[0, :] = self.num_relative_distance - 3
        relative_position_index[:, 0] = self.num_relative_distance - 2
        relative_position_index[0, 0] = self.num_relative_distance - 1
        # self.relative_position_index = relative_position_index
        self.register_buffer("relative_position_index", relative_position_index)
        
    def forward(self):
        if self.relative_position_bias_table is None or self.relative_position_index is None:
            return None
        
        H, W = self.window_size
        relative_position_bias = self.relative_position_bias_table[
            self.relative_position_index.view(-1) # type: ignore
        ].view(H * W + 1, H * W + 1, -1) # H*W, H*W, nH
        relative_position_bias = relative_position_bias.permute(2, 0, 1).contiguous() # nH, H*W, H*W
        
        return relative_position_bias.unsqueeze(0)


class NeuralTransformerAttention(nn.Module):
    def __init__(self,
                 dim: int,
                 num_heads: int = 8,
                 use_qkv_bias: bool = False,
                 qk_norm = None,
                 qk_scale = None,
                 attn_drop = 0.0,
                 proj_drop = 0.0,
                 window_size: tuple[int, int] | None = None,
                 attn_head_dim: int | None = None):
        super().__init__()
        
        self.num_heads = num_heads
        
        head_dim = attn_head_dim if attn_head_dim is not None else dim // num_heads
        
        all_head_dim = head_dim * self.num_heads
        
        self.scale = qk_scale or head_dim ** -0.5

        self.qkv = nn.Linear(dim, all_head_dim * 3, bias=False)
        
        self.q_bias = nn.Parameter(torch.zeros(all_head_dim)) if use_qkv_bias else None
        self.v_bias = nn.Parameter(torch.zeros(all_head_dim)) if use_qkv_bias else None
        
        self.q_norm = qk_norm(head_dim) if qk_norm is not None else None
        self.k_norm = qk_norm(head_dim) if qk_norm is not None else None

        self.window_size = window_size
        
        self.relative_position_bias = RelativePositionBias(window_size, num_heads) if window_size is not None else None

        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(all_head_dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x, return_attention=False, return_qkv=False):
        B, N, C = x.shape
        
        qkv_bias = None
        if self.q_bias is not None and self.v_bias is not None:
            qkv_bias = torch.cat((
                self.q_bias,
                torch.zeros_like(self.v_bias, requires_grad=False),
                self.v_bias
            ))
    
        # qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
        
        qkv = F.linear(input=x, weight=self.qkv.weight, bias=qkv_bias)
        # qkv is of shape (B, N, 3 * all_head_dim)
        
        qkv.reshape(B, N, 3, self.num_heads, -1)
        # qkv is of shape (B, N, 3, num_heads, head_dim)
        
        qkv = qkv.permute(2, 0, 3, 1, 4)
        # qkv is of shape (3, B, num_heads, N, head_dim)
        
        q, k, v = qkv[0], qkv[1], qkv[2] # (B, nH, N, C)
        
        if self.q_norm is not None:
            q = self.q_norm(q).type_as(v)
        if self.k_norm is not None:
            k = self.k_norm(k).type_as(v)

        q = q * self.scale
        
        # (B, nH, N, C) @ (B, nH, C, N) -> (B, nH, N, N)
        attn = (q @ k.transpose(-2, -1))

        if self.relative_position_bias is not None:
            attn += self.relative_position_bias()
        
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        if return_attention:
            return attn

        x = (attn @ v).transpose(1, 2).reshape(B, N, -1)

        x = self.proj(x)
        x = self.proj_drop(x)

        if return_qkv:
            return x, qkv

        return x