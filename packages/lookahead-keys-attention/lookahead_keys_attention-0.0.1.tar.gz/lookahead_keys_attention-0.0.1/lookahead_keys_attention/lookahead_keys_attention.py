from __future__ import annotations

from functools import partial
from collections import namedtuple

import torch
from torch.nn import Module
from torch import nn, cat, sigmoid, einsum
from torch.autograd import Function
import torch.nn.functional as F

from einops.layers.torch import Rearrange

# Import Triton implementation
from .lookahead_keys_attention_triton import castle_attention_triton

# constants

LinearNoBias = partial(nn.Linear, bias=False)

Cache = namedtuple('Cache', ('U', 'qu_cache', 'kc_cache', 'vc_cache'))

# helper functions

def exists(val):
    return val is not None

def default(val, d):
    return val if exists(val) else d

def max_neg_value(t):
    return -torch.finfo(t.dtype).max

# castle implementation

class Castle(Module):
    def __init__(
        self,
        dim,
        heads = 8,
        dim_head = 64,
        use_triton = None
    ):
        super().__init__()
        dim_inner = dim_head * heads

        self.dim = dim
        self.dim_head = dim_head
        self.heads = heads

        # Auto-detect whether to use Triton
        if use_triton is None:
            self.use_triton = torch.cuda.is_available()
        else:
            self.use_triton = use_triton

        self.scale = dim_head ** -0.5

        self.to_all_qkv = LinearNoBias(dim, dim_inner * 6)

        self.split_heads = Rearrange('b n (qkv h d) -> qkv b h n d', qkv = 6, h = heads)
        self.merge_heads = Rearrange('b h n d -> b n (h d)')

        self.combine_heads = LinearNoBias(dim_inner, dim)

    def forward(
        self,
        x,
        cache: Cache | None = None,
        return_next_cache = None
    ):
        batch_size, seq_len, scale, device = *x.shape[:2], self.scale, x.device
        is_inference = seq_len == 1

        return_next_cache = default(return_next_cache, is_inference)

        # projection

        qkvs = self.to_all_qkv(x)

        # c - usual causal parameters
        # u - lookup keys related

        qu, ku, vu, qc, kc, vc = self.split_heads(qkvs)

        # scaled queries

        qu_scaled = qu * scale
        qc_scaled = qc * scale

        # handle single token vs multiple ones differently

        if not is_inference:
            assert not exists(cache), 'must be inferencing single tokens if receiving cache'

            # Use Triton implementation if enabled and tensors are on CUDA
            if self.use_triton and qc.is_cuda:
                # Use Triton path - much more efficient for parallel training
                out = castle_attention_triton(qc_scaled, kc, vc, qu_scaled, ku, vu, 1.0)

                if return_next_cache:
                    # Calculate lookahead keys for cache
                    mask_shape = (seq_len, seq_len)
                    causal_mask = torch.ones(mask_shape, device = device, dtype = torch.bool).triu(1)
                    lookahead_attn = einsum('...id, ...jd -> ...ij', qu_scaled, ku).sigmoid()
                    lookahead_attn = lookahead_attn.masked_fill(~causal_mask, 0.)
                    U = einsum('...ij, ...jd -> ...id', lookahead_attn, vu)
                    next_cache = Cache(U, qu, kc, vc)
            else:
                # Use reference PyTorch implementation
                mask_shape = (seq_len, seq_len)

                causal_mask = torch.ones(mask_shape, device = device, dtype = torch.bool).triu(1)

                term1 = einsum('...id, ...jd -> ...ij', qc_scaled, vu)
                term1 = term1.masked_fill(causal_mask, 0.)

                lookahead_attn = einsum('...id, ...jd -> ...ij', qu_scaled, ku).sigmoid()
                lookahead_attn = lookahead_attn.masked_fill(~causal_mask, 0.)

                Su = einsum('...ij, ...kj -> ...ik', term1, lookahead_attn)

                Sc = einsum('...id, ...jd -> ...ij', qc_scaled, kc)

                scores = Sc - F.silu(Su)
                scores = scores.masked_fill(causal_mask, max_neg_value(scores))

                # attention
                attn = scores.softmax(dim = -1)

                # aggregate
                out = einsum('...ij, ...jd -> ...id', attn, vc)

                if return_next_cache:
                    # need to calculate U if returning next cache in parallel
                    U = einsum('...ij, ...jd -> ...id', lookahead_attn, vu)
                    next_cache = Cache(U, qu, kc, vc)

        else:
            # Inference mode (single token) - always use reference implementation
            if not exists(cache):
                empty_tensor = qu[..., 0:0, :] # (batch, heads, 0, dim_head)
                cache = (empty_tensor,) * 4

            U_prev, qu_cache, kc_cache, vc_cache = cache

            qu_cache_scaled = qu_cache * scale

            lookahead_attn = einsum('...id, ...jd -> ...ij', qu_cache_scaled, ku).sigmoid()
            U_updated_prev = U_prev + (lookahead_attn * vu)

            Ut = cat((U_updated_prev, torch.zeros_like(qu)), dim = -2)

            kc = cat((kc_cache, kc), dim = -2)
            vc = cat((vc_cache, vc), dim = -2)

            Sc = einsum('...id, ...jd -> ...ij', qc_scaled, kc)
            Su = einsum('...id, ...jd -> ...ij', qc_scaled, Ut)

            # combine causal scores with lookahead scores
            scores = Sc - F.silu(Su)

            # attention
            attn = scores.softmax(dim = -1)

            # aggregate
            out = einsum('...ij, ...jd -> ...id', attn, vc)

            qu_next = cat((qu_cache, qu), dim = -2)
            next_cache = Cache(Ut, qu_next, kc, vc)

        # merge and combine heads

        out = self.merge_heads(out)

        out = self.combine_heads(out)

        if not return_next_cache:
            return out

        return out, next_cache
