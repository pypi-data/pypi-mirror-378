import torch
import torch.nn as nn
from einops import rearrange


__all__ = ['CrissCrossAttention']

class CrissCrossAttention(nn.Module):
    def __init__(self,
                 d_model: int,
                 num_heads: int,
                 dropout_rate: float,
                 bias: bool = True,
                 batch_first: bool = False):
        super().__init__()
        
        self.self_attn_s = nn.MultiheadAttention(
            embed_dim=d_model//2,
            num_heads=num_heads//2,
            dropout=dropout_rate,
            bias=bias,
            batch_first=batch_first
        )
        
        self.self_attn_t = nn.MultiheadAttention(
            embed_dim=d_model//2,
            num_heads=num_heads//2,
            dropout=dropout_rate,
            bias=bias,
            batch_first=batch_first
        )
        
        self.dropout = nn.Dropout(dropout_rate)
    
    def forward(self,
                x: torch.Tensor,
                attn_mask: torch.Tensor | None,
                key_padding_mask: torch.Tensor | None) -> torch.Tensor:
        bz, ch_num, patch_num, patch_size = x.shape
        s = patch_size // 2
        
        # Spatial Attention
        xs = rearrange(x[:, :, :, :s], 'b c p s -> (b p) c s')
        xs = self.self_attn_s(
            xs, xs, xs,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask,
            need_weights=False
        )[0]
        xs = rearrange(xs, '(b p) c s -> b c p s', b=bz, p=patch_num)
        
        # Temporal Attention
        xt = rearrange(x[:, :, :, -s:], 'b c p s -> (b c) p s')
        xt = self.self_attn_t(
            xt, xt, xt,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask,
            need_weights=False
        )[0]
        xt = rearrange(xt, '(b c) p s -> b c p s', b=bz, c=ch_num)
        
        x = torch.concat((xs, xt), dim=3)
        x = self.dropout(x)
        
        return x