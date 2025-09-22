import torch
import torch.nn as nn
from einops import repeat
from bfms.utils.weights import trunc_normal_


__all__ = [
    "TemporalEmbedding"
]

class TemporalEmbedding(nn.Module):
    """
    In order to enable the model to be aware of the temporal information 
    of patch embeddings, we initialize the following d-dimension list 
    that is learnable during training (the Temporal Embedding list):
    
    TE = {te_1, te_2, ..., te_tmax} (time_embed)
    
    Here, tmax is the maximum number of time patches (max_patches).
    
    Note: floor(t/w) <= tmax, where t is the length of the EEG signal and 
    w is the length of each time patch (patch_size).
    
    The identified temporal embedding te is then added to x.
    """
    def __init__(self,
                 embed_dim: int = 200,
                 init_std: float = 0.02,
                 max_patches: int = 16):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.time_embed = nn.Parameter(torch.zeros(max_patches, embed_dim), requires_grad=True)
        trunc_normal_(self.time_embed, std=init_std)
    
    @torch.jit.ignore # type: ignore
    def no_weight_decay(self):
        return {'time_embed'}
    
    def forward(self,
                x: torch.Tensor):
        """
        Args:
            x: Input tensor of shape (B, N, P, embed_dim)
        Returns:
            Tensor of shape (B, N, P, embed_dim) with added temporal embeddings
        """
        B, N, P, embed_dim = x.size()
        # note that embed_dim should be equal to self.embed_dim
        assert embed_dim == self.embed_dim, (
            "embed_dim should be equal to self.embed_dim, "
            f"but got {embed_dim} and {self.embed_dim}"
        )
        
        # Temporal Embedding
        time_embed = self.time_embed[:P]
        # time_embed is of shape (P, embed_dim)
        time_embed = repeat(time_embed, 'P E -> B N P E', B=B, N=N)
        # time_embed is now of shape (B, N, P, embed_dim)
        x += time_embed
        
        return x