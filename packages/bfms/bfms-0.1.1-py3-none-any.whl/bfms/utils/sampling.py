import torch

def sample_vectors(samples: torch.Tensor, num: int) -> torch.Tensor:
    """
    Randomly sample `num` vectors from the dataset `samples`.
    - If samples >= num: sample without replacement.
    - If samples < num: sample with replacement.

    (N, D) -> (num, D)
    """
    num_samples = samples.shape[0]
    device = samples.device
    
    if num_samples >= num:
        # sample unique indices (i.e. without replacement)
        indices = torch.randperm(num_samples, device=device)[:num]
    else:
        # sample with replacement
        indices = torch.randint(0, num_samples, (num,), device=device)
    
    return samples[indices]