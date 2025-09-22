import torch
import torch.nn as nn
from einops import repeat
from bfms.utils.weights import trunc_normal_


__all__ = [
    "SpatialEmbedding"
]

class SpatialEmbedding(nn.Module):
    """
    In order to enable the model to be aware of the spatial information 
    of patch embeddings, we initialize the following d-dimension list 
    that is learnable during training (the Spatial Embedding list):
    
    SE = {se_1, se_2, ..., se_|C|} (pos_embed)
    
    where |C| is the number of channels (electrodes).
    
    For each channel c_i, we can find its corresponding spatial embedding
    se_i in the spatial embedding list SE.
    
    The identified spatial embedding se is then added to x.
    """
    def __init__(self,
                 embed_dim: int = 200,
                 init_std: float = 0.02,
                 max_channels: int = 128):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.spatial_embed = SpatialEmbedding()

        self.pos_embed = nn.Parameter(torch.zeros(max_channels, embed_dim))
        
        trunc_normal_(self.pos_embed, std=init_std)
    
    @torch.jit.ignore # type: ignore
    def no_weight_decay(self):
        return {'time_embed'}
    
    def forward(self,
                x: torch.Tensor,
                input_channels: list[int] | None = None):
        """
        Args:
            x: Input tensor of shape (B, N, P, embed_dim)
            input_channels: Optional channel indices to subset from pos_embed
        Returns:
            Tensor of shape (B, N, P, embed_dim) with added spatial embeddings
        """
        B, N, P, embed_dim = x.size()
        # note that embed_dim should be equal to self.embed_dim
        assert embed_dim == self.embed_dim, (
            "embed_dim should be equal to self.embed_dim, "
            f"but got {embed_dim} and {self.embed_dim}"
        )
        
        # Spatial Embedding
        pos_embed = self.pos_embed if input_channels is None else self.pos_embed[input_channels]
        # pos_embed is of shape (N, embed_dim)
        pos_embed = repeat(pos_embed, 'N E -> B N P E', B=B, P=P)
        # pos_embed is now of shape (B, N, P, embed_dim)
        x += pos_embed
        
        return x