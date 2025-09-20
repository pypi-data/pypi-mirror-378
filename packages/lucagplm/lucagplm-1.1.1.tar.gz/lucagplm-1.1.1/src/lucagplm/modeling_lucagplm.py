import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel
from transformers.modeling_outputs import BaseModelOutput
from typing import Dict, Optional, List, Union, Tuple
from .configuration_lucagplm import LucaGPLMConfig

def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))

def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary_pos_emb(x, cos, sin):
    cos = cos[:, : x.shape[-2], :]
    sin = sin[:, : x.shape[-2], :]
    return (x * cos) + (rotate_half(x) * sin)

class RotaryEmbedding(torch.nn.Module):
    def __init__(self, dim: int, *_, **__):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

        self._seq_len_cached = None
        self._cos_cached = None
        self._sin_cached = None

    def _update_cos_sin_tables(self, x, seq_dimension=1):
        seq_len = x.shape[seq_dimension]

        if (seq_len != self._seq_len_cached or 
            self._cos_cached is None or 
            self._sin_cached is None or
            self._cos_cached.device != x.device):
            self._seq_len_cached = seq_len
            t = torch.arange(x.shape[seq_dimension], device=x.device).type_as(self.inv_freq)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1).to(x.device)

            self._cos_cached = emb.cos()[None, :, :]
            self._sin_cached = emb.sin()[None, :, :]

        return self._cos_cached, self._sin_cached

    def forward(self, q: torch.Tensor, k: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        self._cos_cached, self._sin_cached = self._update_cos_sin_tables(k, seq_dimension=-2)

        return (
            apply_rotary_pos_emb(q, self._cos_cached, self._sin_cached),
            apply_rotary_pos_emb(k, self._cos_cached, self._sin_cached),
        )

try:
    from apex.normalization import FusedLayerNorm as _FusedLayerNorm
    class LucaGPLM1bLayerNorm(_FusedLayerNorm):
        @torch.jit.unused
        def forward(self, x):
            if not x.is_cuda:
                return super().forward(x)
            else:
                with torch.cuda.device(x.device):
                    return super().forward(x)
except ImportError:
    from torch.nn import LayerNorm as LucaGPLM1bLayerNorm

class LucaGPLM1LayerNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-12, affine=True):
        super().__init__()
        self.hidden_size = (hidden_size,) if isinstance(hidden_size, int) else tuple(hidden_size)
        self.eps = eps
        self.affine = bool(affine)
        if self.affine:
            self.weight = nn.Parameter(torch.ones(hidden_size))
            self.bias = nn.Parameter(torch.zeros(hidden_size))
        else:
            self.weight, self.bias = None, None

    def forward(self, x):
        dims = tuple(-(i + 1) for i in range(len(self.hidden_size)))
        means = x.mean(dims, keepdim=True)
        x_zeromean = x - means
        variances = x_zeromean.pow(2).mean(dims, keepdim=True)
        x = x_zeromean / torch.sqrt(variances + self.eps)
        if self.affine:
            x = (self.weight * x) + self.bias
        return x

class LucaGPLMMultiheadAttention(nn.Module):
    def __init__(
        self,
        embed_dim,
        num_heads,
        kdim=None,
        vdim=None,
        dropout=0.0,
        bias=True,
        add_bias_kv: bool = False,
        add_zero_attn: bool = False,
        self_attention: bool = False,
        encoder_decoder_attention: bool = False,
        use_rotary_embeddings: bool = False,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.kdim = kdim if kdim is not None else embed_dim
        self.vdim = vdim if vdim is not None else embed_dim
        self.qkv_same_dim = self.kdim == embed_dim and self.vdim == embed_dim

        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        assert (
            self.head_dim * num_heads == self.embed_dim
        ), "embed_dim must be divisible by num_heads"
        self.scaling = self.head_dim**-0.5

        self.self_attention = self_attention
        self.encoder_decoder_attention = encoder_decoder_attention

        assert not self.self_attention or self.qkv_same_dim, (
            "Self-attention requires query, key and " "value to be of the same size"
        )

        self.k_proj = nn.Linear(self.kdim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(self.vdim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        if add_bias_kv:
            self.bias_k = nn.Parameter(torch.Tensor(1, 1, embed_dim))
            self.bias_v = nn.Parameter(torch.Tensor(1, 1, embed_dim))
        else:
            self.bias_k = self.bias_v = None

        self.add_zero_attn = add_zero_attn

        self.reset_parameters()

        self.rot_emb = None
        if use_rotary_embeddings:
            self.rot_emb = RotaryEmbedding(dim=self.head_dim)

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.k_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.v_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.q_proj.weight, gain=nn.init.calculate_gain("relu"))
        nn.init.xavier_uniform_(self.out_proj.weight, gain=nn.init.calculate_gain("relu"))
        
        if self.out_proj.bias is not None:
            nn.init.constant_(self.out_proj.bias, 0.0)
        if self.bias_k is not None:
            nn.init.xavier_normal_(self.bias_k)
        if self.bias_v is not None:
            nn.init.xavier_normal_(self.bias_v)

    def forward(
        self,
        query,
        key: Optional[torch.Tensor] = None,
        value: Optional[torch.Tensor] = None,
        key_padding_mask: Optional[torch.Tensor] = None,
        need_weights: bool = True,
        attn_mask: Optional[torch.Tensor] = None,
        need_head_weights: bool = False,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        if need_head_weights:
            need_weights = True

        tgt_len, bsz, embed_dim = query.size()
        assert embed_dim == self.embed_dim

        if self.self_attention:
            q = self.q_proj(query)
            k = self.k_proj(query)
            v = self.v_proj(query)
        else:
            assert key is not None and value is not None
            q = self.q_proj(query)
            k = self.k_proj(key)
            v = self.v_proj(value)

        q *= self.scaling

        if self.bias_k is not None:
            assert self.bias_v is not None
            k = torch.cat([k, self.bias_k.repeat(1, bsz, 1)])
            v = torch.cat([v, self.bias_v.repeat(1, bsz, 1)])
            if attn_mask is not None:
                attn_mask = torch.cat(
                    [attn_mask, attn_mask.new_zeros(attn_mask.size(0), 1)], dim=1
                )
            if key_padding_mask is not None:
                key_padding_mask = torch.cat(
                    [
                        key_padding_mask,
                        key_padding_mask.new_zeros(key_padding_mask.size(0), 1),
                    ],
                    dim=1,
                )

        q = q.contiguous().view(tgt_len, bsz * self.num_heads, self.head_dim).transpose(0, 1)
        if k is not None:
            k = k.contiguous().view(-1, bsz * self.num_heads, self.head_dim).transpose(0, 1)
        if v is not None:
            v = v.contiguous().view(-1, bsz * self.num_heads, self.head_dim).transpose(0, 1)

        assert k is not None
        src_len = k.size(1)

        if self.rot_emb:
            q, k = self.rot_emb(q, k)

        attn_weights = torch.bmm(q, k.transpose(1, 2))
        assert list(attn_weights.size()) == [bsz * self.num_heads, tgt_len, src_len]

        if attn_mask is not None:
            attn_mask = attn_mask.unsqueeze(0)
            attn_weights += attn_mask

        if key_padding_mask is not None:
            attn_weights = attn_weights.view(bsz, self.num_heads, tgt_len, src_len)
            attn_weights = attn_weights.masked_fill(
                key_padding_mask.unsqueeze(1).unsqueeze(2).to(torch.bool), float("-inf")
            )
            attn_weights = attn_weights.view(bsz * self.num_heads, tgt_len, src_len)

        attn_weights_float = F.softmax(attn_weights, dim=-1)
        attn_weights = attn_weights_float.type_as(attn_weights)
        attn_probs = F.dropout(
            attn_weights_float.type_as(attn_weights),
            p=self.dropout,
            training=self.training,
        )

        assert v is not None
        attn = torch.bmm(attn_probs, v)
        assert list(attn.size()) == [bsz * self.num_heads, tgt_len, self.head_dim]
        attn = attn.transpose(0, 1).contiguous().view(tgt_len, bsz, embed_dim)
        attn = self.out_proj(attn)

        attn_weights_output: Optional[torch.Tensor] = None
        if need_weights:
            attn_weights_output = attn_weights_float.view(
                bsz, self.num_heads, tgt_len, src_len
            ).type_as(attn).transpose(1, 0)
            if not need_head_weights:
                # average attention weights over heads
                attn_weights_output = attn_weights_output.mean(dim=0)

        return attn, attn_weights_output

class LucaGPLMTransformerLayer(nn.Module):
    def __init__(
        self,
        embed_dim,
        ffn_embed_dim,
        attention_heads,
        add_bias_kv=True,
        use_lucagplm1b_layer_norm=False,
        use_rotary_embeddings: bool = False,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.ffn_embed_dim = ffn_embed_dim
        self.attention_heads = attention_heads
        self.use_rotary_embeddings = use_rotary_embeddings
        
        LucaGPLMLayerNorm = LucaGPLM1bLayerNorm if use_lucagplm1b_layer_norm else LucaGPLM1LayerNorm

        self.pre_layer_norm = LucaGPLMLayerNorm(self.embed_dim)

        self.self_attn = LucaGPLMMultiheadAttention(
            self.embed_dim,
            self.attention_heads,
            add_bias_kv=add_bias_kv,
            add_zero_attn=False,
            self_attention=True,
            use_rotary_embeddings=self.use_rotary_embeddings,
        )

        # post layer norm
        self.post_layer_norm = LucaGPLMLayerNorm(self.embed_dim)

        # dimension increase by the fully connected layer
        self.fc1 = nn.Linear(self.embed_dim, self.ffn_embed_dim)

        # dimension reduction by the fully connected layer
        self.fc2 = nn.Linear(self.ffn_embed_dim, self.embed_dim)

    def forward(
        self,
        x,
        self_attn_mask=None,
        self_attn_padding_mask=None,
        need_head_weights=False
    ):
        residual = x
        x = self.pre_layer_norm(x)
        x, attn = self.self_attn(
            query=x,
            key=x,
            value=x,
            key_padding_mask=self_attn_padding_mask,
            need_weights=True,
            need_head_weights=need_head_weights,
            attn_mask=self_attn_mask,
        )
        x = residual + x

        residual = x
        x = self.post_layer_norm(x)
        x = gelu(self.fc1(x))
        x = self.fc2(x)
        x = residual + x

        return x, attn

class LucaGPLMEmbeddings(nn.Module):
    def __init__(self, config: LucaGPLMConfig):
        super().__init__()
        
        # Store config flags for forward pass
        self.no_position_embeddings = getattr(config, 'no_position_embeddings', False)
        self.no_token_type_embeddings = getattr(config, 'no_token_type_embeddings', False)
        self.use_embed_layer_norm = getattr(config, 'use_embed_layer_norm', True)
        self.embed_scale = getattr(config, 'embed_scale', 1.0)
        self.token_dropout = getattr(config, 'token_dropout', False)
        
        # Token ids for special tokens (matching old model)
        self.mask_idx = getattr(config, 'mask_token_id', 4)
        self.padding_idx = getattr(config, 'pad_token_id', 0)

        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        
        # Only create position embeddings if not disabled
        if not self.no_position_embeddings:
            self.embed_pos = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        else:
            self.embed_pos = None
            
        # Only create token type embeddings if not disabled    
        if not self.no_token_type_embeddings:
            self.embed_type = nn.Embedding(config.type_vocab_size, config.hidden_size)
        else:
            self.embed_type = None
            
        # Only create layer norm if enabled
        if self.use_embed_layer_norm:
            self.embed_layer_norm = LucaGPLM1bLayerNorm(config.hidden_size)
        else:
            self.embed_layer_norm = None

    def forward(
        self,
        input_ids: torch.Tensor,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        input_shape = input_ids.size()
        seq_length = input_shape[1]

        # Start with token embeddings and apply embed_scale
        inputs_embeds = self.embed_scale * self.embed_tokens(input_ids)
        
        # Add position embeddings if enabled
        if not self.no_position_embeddings and self.embed_pos is not None:
            if position_ids is None:
                position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
                position_ids = position_ids.unsqueeze(0).expand(input_shape)
            position_embeddings = self.embed_scale * self.embed_pos(position_ids)
            inputs_embeds = inputs_embeds + position_embeddings

        # Add token type embeddings if enabled
        if not self.no_token_type_embeddings and self.embed_type is not None:
            if token_type_ids is None:
                token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=input_ids.device)
            token_type_embeddings = self.embed_scale * self.embed_type(token_type_ids)
            inputs_embeds = inputs_embeds + token_type_embeddings
        
        # Apply layer norm if enabled
        if self.use_embed_layer_norm and self.embed_layer_norm is not None:
            embeddings = self.embed_layer_norm(inputs_embeds)
        else:
            embeddings = inputs_embeds

        # Apply token dropout (matching old model behavior)
        if self.token_dropout and self.training:
            # Zero out masked token embeddings
            embeddings = embeddings.masked_fill((input_ids == self.mask_idx).unsqueeze(-1), 0.0)
            
            # Apply token dropout scaling
            mask_ratio_train = 0.15 * 0.8
            padding_mask = input_ids.eq(self.padding_idx)
            src_lengths = (~padding_mask).sum(-1)
            mask_ratio_observed = (input_ids == self.mask_idx).sum(-1).to(embeddings.dtype) / src_lengths
            embeddings = embeddings * (1 - mask_ratio_train) / (1 - mask_ratio_observed)[:, None, None]

        # Apply padding mask to embeddings
        padding_mask = input_ids.eq(self.padding_idx)
        if padding_mask.any():
            embeddings = embeddings * (1 - padding_mask.unsqueeze(-1).type_as(embeddings))

        return embeddings

class LucaGPLMEncoder(nn.Module):
    def __init__(self, config: LucaGPLMConfig):
        super().__init__()

        self.layers = nn.ModuleList([
            LucaGPLMTransformerLayer(
                config.hidden_size,
                4 * config.hidden_size,  # ffn_embed_dim = 4 * embed_dim
                config.num_attention_heads,
                add_bias_kv=False,
                use_lucagplm1b_layer_norm=True,
                use_rotary_embeddings=True,
            )
            for _ in range(config.num_hidden_layers)
        ])
        
        self.use_last_layer_norm = getattr(config, 'use_last_layer_norm', True)
        if self.use_last_layer_norm:
            self.last_layer_norm = LucaGPLM1bLayerNorm(config.hidden_size)
        else:
            self.last_layer_norm = None

        self.padding_idx = config.pad_token_id
        self.gradient_checkpointing = False

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
        need_head_weights: bool = False,
        repr_layers: Optional[List[int]] = None,
        use_last_layer_norm: bool = True,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutput]:
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        
        if repr_layers is None:
            repr_layers = [-1]
        
        # 转换为原始模型的索引系统
        layer_size = len(self.layers)
        repr_layers = [(i + layer_size + 1) % (layer_size + 1) for i in repr_layers]
        repr_layers = set(repr_layers)
        hidden_representations = {}

        # Process attention mask - 原始模型期望的是padding mask
        if attention_mask is None:
            padding_mask = hidden_states.new_zeros(hidden_states.shape[:2]).eq(self.padding_idx)
        else:
            # 原始模型中 padding_mask 是 True 表示 padding位置
            padding_mask = attention_mask.eq(0)

        # 0: embedding layer
        if 0 in repr_layers:
            hidden_representations[0] = hidden_states

        # 转换为 (seq_len, batch_size, hidden_size) 格式，与原始模型一致
        hidden_states = hidden_states.transpose(0, 1)
        
        if not padding_mask.any():
            padding_mask = None

        # 是否需要返回head weights
        if need_head_weights or output_attentions:
            attn_weights = []

        for layer_idx, layer_module in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states.transpose(0, 1),)

            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(
                    layer_module.__call__,
                    hidden_states,
                    None,  # self_attn_mask
                    padding_mask,
                    need_head_weights or output_attentions,
                )
            else:
                layer_outputs = layer_module(
                    hidden_states,
                    self_attn_mask=None,
                    self_attn_padding_mask=padding_mask,
                    need_head_weights=need_head_weights or output_attentions,
                )

            hidden_states, attn = layer_outputs

            if (layer_idx + 1) in repr_layers:
                hidden_representations[layer_idx + 1] = hidden_states.transpose(0, 1)

            if need_head_weights or output_attentions:
                # (H, B, L, L) => (B, H, L, L)
                attn_weights.append(attn.transpose(1, 0))

        # 应用最后的layer norm
        if self.last_layer_norm is not None and use_last_layer_norm:
            hidden_states = self.last_layer_norm(hidden_states)

        # 转换回 (batch_size, seq_len, hidden_size) 格式
        hidden_states = hidden_states.transpose(0, 1)

        # last hidden representation should have layer norm applied
        if (layer_idx + 1) in repr_layers:
            hidden_representations[layer_idx + 1] = hidden_states

        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)

        if need_head_weights or output_attentions:
            # 将attention weights转换为正确格式
            if attn_weights:
                # B x Layers x H x L x L
                all_attentions = torch.stack(attn_weights, 1)
                if padding_mask is not None:
                    attention_mask_expanded = 1 - padding_mask.type_as(all_attentions)
                    attention_mask_expanded = attention_mask_expanded.unsqueeze(1) * attention_mask_expanded.unsqueeze(2)
                    all_attentions = all_attentions * attention_mask_expanded[:, None, None, :, :]
            
            if not output_attentions:
                all_attentions = None

        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states, all_attentions] if v is not None)

        return BaseModelOutput(
            last_hidden_state=hidden_states,
            hidden_states=all_hidden_states,
            attentions=all_attentions,
        )

class LucaGPLMPreTrainedModel(PreTrainedModel):
    config_class = LucaGPLMConfig
    base_model_prefix = "lucagplm"
    supports_gradient_checkpointing = True
    _no_split_modules = ["LucaGPLMTransformerLayer"]

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, (LucaGPLM1LayerNorm, LucaGPLM1bLayerNorm)):
            if hasattr(module, 'weight') and module.weight is not None:
                module.weight.data.fill_(1.0)
            if hasattr(module, 'bias') and module.bias is not None:
                module.bias.data.zero_()

class LucaGPLMModel(LucaGPLMPreTrainedModel):
    """
    The LucaGPLM model for extracting sequence representations and optionally predicting contacts.
    Based on the original LucaGPLM implementation but restructured to use modern transformers architecture.
    """
    
    def __init__(self, config: LucaGPLMConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = LucaGPLMEmbeddings(self.config)
        self.encoder = LucaGPLMEncoder(self.config)
        self.post_init()

    def get_input_embeddings(self):
        return self.embeddings.embed_tokens

    def set_input_embeddings(self, value):
        self.embeddings.embed_tokens = value

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_contacts: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        need_head_weights: Optional[bool] = None,
        repr_layers: Optional[List[int]] = None,
        use_last_layer_norm: Optional[bool] = True,
    ) -> Union[Tuple[torch.Tensor], BaseModelOutput]:
        
        output_attentions = output_attentions if output_attentions is not None else getattr(self.config, 'output_attentions', False)
        output_hidden_states = output_hidden_states if output_hidden_states is not None else getattr(self.config, 'output_hidden_states', False)
        return_contacts = return_contacts if return_contacts is not None else False
        return_dict = return_dict if return_dict is not None else getattr(self.config, 'use_return_dict', True)
        need_head_weights = need_head_weights if need_head_weights is not None else return_contacts  # Need attention weights for contacts
        use_last_layer_norm = use_last_layer_norm if use_last_layer_norm is not None else True

        # Force output_attentions=True when return_contacts=True since we need attention weights
        if return_contacts:
            output_attentions = True
            need_head_weights = True

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")

        batch_size, seq_length = input_shape
        device = input_ids.device if input_ids is not None else inputs_embeds.device

        # Create attention mask if not provided
        if attention_mask is None:
            attention_mask = torch.ones(input_shape, device=device)

        # Get embeddings
        if inputs_embeds is None:
            embedding_output = self.embeddings(
                input_ids=input_ids,
                position_ids=position_ids,
                token_type_ids=token_type_ids,
            )
        else:
            embedding_output = inputs_embeds

        # Pass through encoder
        encoder_outputs = self.encoder(
            embedding_output,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            need_head_weights=need_head_weights,
            repr_layers=repr_layers,
            use_last_layer_norm=use_last_layer_norm,
        )
        
        sequence_output = encoder_outputs[0]
        
        # Handle contact prediction
        contacts = None
        if return_contacts and encoder_outputs.attentions is not None:
            # Simple contact prediction using attention weights
            # This is a simplified implementation - you can enhance this later
            attentions = encoder_outputs.attentions
            # Average over layers and heads, then symmetrize
            averaged_attention = attentions.mean(dim=(1, 2))  # Average over layers and heads
            contacts = (averaged_attention + averaged_attention.transpose(-1, -2)) / 2
            
            # Remove special tokens (BOS/EOS) if present
            if attention_mask is not None:
                # Find actual sequence positions (non-padding)
                seq_lens = attention_mask.sum(dim=1)
                # For now, keep the full contact map - you can trim special tokens later if needed

        if not return_dict:
            outputs = (sequence_output, ) + encoder_outputs[1:]
            if contacts is not None:
                outputs = outputs + (contacts,)
            return outputs

        # Create output object with contacts
        output = BaseModelOutput(
            last_hidden_state=sequence_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
        
        # Add contacts as an attribute if computed
        if contacts is not None:
            output.contacts = contacts
            
        return output

class LucaGPLMForPretraining(LucaGPLMPreTrainedModel):
    """
    LucaGPLM model with pretraining heads for various tasks.
    Based on the original LucaVirus model's pretraining tasks.
    """
    def __init__(self, config: LucaGPLMConfig):
        super().__init__(config)
        self.config = config
        
        # Initialize base model
        self.lucagplm = LucaGPLMModel(config)
        
        # Initialize pretraining tasks
        self.pretrain_tasks = {}
        
        # Initialize language model head for token-level tasks
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Initialize pretraining task heads based on LucaVirus model
        self._init_pretrain_tasks()
        
        # Initialize weights
        self.post_init()
    
    def _init_pretrain_tasks(self):
        """
        Initialize pretraining task heads based on LucaVirus model
        """
        # Token level tasks
        self.pretrain_tasks = {}
        self.pretrain_tasks["token_level"] = {}
        
        # Gene mask prediction (masked language modeling)
        gene_mask_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        gene_mask_classifier = nn.Linear(self.config.hidden_size, self.config.vocab_size, bias=False)
        self.pretrain_tasks["token_level"]["gene_mask"] = {
            "classifier_dropout": gene_mask_classifier_dropout,
            "classifier": gene_mask_classifier
        }
        # Register as direct attributes
        self.gene_mask_classifier_dropout = gene_mask_classifier_dropout
        self.gene_mask_classifier = gene_mask_classifier
        
        # Protein mask prediction (masked language modeling)
        prot_mask_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_mask_classifier = nn.Linear(self.config.hidden_size, self.config.vocab_size, bias=False)
        self.pretrain_tasks["token_level"]["prot_mask"] = {
            "classifier_dropout": prot_mask_classifier_dropout,
            "classifier": prot_mask_classifier
        }
        # Register as direct attributes
        self.prot_mask_classifier_dropout = prot_mask_classifier_dropout
        self.prot_mask_classifier = prot_mask_classifier
        
        # Span level tasks
        self.pretrain_tasks["span_level"] = {}
        
        # Gene type prediction
        gene_type_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        gene_type_hidden_layer = nn.Linear(self.config.hidden_size, 128, bias=True)
        gene_type_hidden_act = nn.GELU()
        gene_type_classifier = nn.Linear(128, 10, bias=True)  # Assuming 10 gene types
        self.pretrain_tasks["span_level"]["gene_type"] = {
            "classifier_dropout": gene_type_classifier_dropout,
            "hidden_layer": gene_type_hidden_layer,
            "hidden_act": gene_type_hidden_act,
            "classifier": gene_type_classifier
        }
        # Register as direct attributes
        self.gene_type_classifier_dropout = gene_type_classifier_dropout
        self.gene_type_hidden_layer = gene_type_hidden_layer
        self.gene_type_hidden_act = gene_type_hidden_act
        self.gene_type_classifier = gene_type_classifier
        
        # Protein homology prediction
        prot_homo_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_homo_hidden_layer = nn.Linear(self.config.hidden_size, 4096, bias=True)
        prot_homo_hidden_act = nn.GELU()
        prot_homo_classifier = nn.Linear(4096, 5, bias=True)  # Assuming 5 homology classes
        self.pretrain_tasks["span_level"]["prot_homo"] = {
            "classifier_dropout": prot_homo_classifier_dropout,
            "hidden_layer": prot_homo_hidden_layer,
            "hidden_act": prot_homo_hidden_act,
            "classifier": prot_homo_classifier
        }
        # Register as direct attributes
        self.prot_homo_classifier_dropout = prot_homo_classifier_dropout
        self.prot_homo_hidden_layer = prot_homo_hidden_layer
        self.prot_homo_hidden_act = prot_homo_hidden_act
        self.prot_homo_classifier = prot_homo_classifier
        
        # Protein site prediction
        prot_site_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_site_hidden_layer = nn.Linear(self.config.hidden_size, 1024, bias=True)
        prot_site_hidden_act = nn.GELU()
        prot_site_classifier = nn.Linear(1024, 20, bias=True)  # Assuming 20 site types
        self.pretrain_tasks["span_level"]["prot_site"] = {
            "classifier_dropout": prot_site_classifier_dropout,
            "hidden_layer": prot_site_hidden_layer,
            "hidden_act": prot_site_hidden_act,
            "classifier": prot_site_classifier
        }
        # Register as direct attributes
        self.prot_site_classifier_dropout = prot_site_classifier_dropout
        self.prot_site_hidden_layer = prot_site_hidden_layer
        self.prot_site_hidden_act = prot_site_hidden_act
        self.prot_site_classifier = prot_site_classifier
        
        # Protein domain prediction
        prot_domain_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_domain_hidden_layer = nn.Linear(self.config.hidden_size, 10240, bias=True)
        prot_domain_hidden_act = nn.GELU()
        prot_domain_classifier = nn.Linear(10240, 100, bias=True)  # Assuming 100 domain types
        self.pretrain_tasks["span_level"]["prot_domain"] = {
            "classifier_dropout": prot_domain_classifier_dropout,
            "hidden_layer": prot_domain_hidden_layer,
            "hidden_act": prot_domain_hidden_act,
            "classifier": prot_domain_classifier
        }
        # Register as direct attributes
        self.prot_domain_classifier_dropout = prot_domain_classifier_dropout
        self.prot_domain_hidden_layer = prot_domain_hidden_layer
        self.prot_domain_hidden_act = prot_domain_hidden_act
        self.prot_domain_classifier = prot_domain_classifier
        
        # Sequence level tasks
        self.pretrain_tasks["seq_level"] = {}
        
        # Gene taxonomy prediction
        gene_taxonomy_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        gene_taxonomy_hidden_layer = nn.Linear(self.config.hidden_size, 2048, bias=True)
        gene_taxonomy_hidden_act = nn.GELU()
        gene_taxonomy_classifier = nn.Linear(2048, 50, bias=True)  # Assuming 50 taxonomy classes
        self.pretrain_tasks["seq_level"]["gene_taxonomy"] = {
            "classifier_dropout": gene_taxonomy_classifier_dropout,
            "hidden_layer": gene_taxonomy_hidden_layer,
            "hidden_act": gene_taxonomy_hidden_act,
            "classifier": gene_taxonomy_classifier
        }
        # Register as direct attributes
        self.gene_taxonomy_classifier_dropout = gene_taxonomy_classifier_dropout
        self.gene_taxonomy_hidden_layer = gene_taxonomy_hidden_layer
        self.gene_taxonomy_hidden_act = gene_taxonomy_hidden_act
        self.gene_taxonomy_classifier = gene_taxonomy_classifier
        
        # Protein taxonomy prediction
        prot_taxonomy_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_taxonomy_hidden_layer = nn.Linear(self.config.hidden_size, 2048, bias=True)
        prot_taxonomy_hidden_act = nn.GELU()
        prot_taxonomy_classifier = nn.Linear(2048, 50, bias=True)  # Assuming 50 taxonomy classes
        self.pretrain_tasks["seq_level"]["prot_taxonomy"] = {
            "classifier_dropout": prot_taxonomy_classifier_dropout,
            "hidden_layer": prot_taxonomy_hidden_layer,
            "hidden_act": prot_taxonomy_hidden_act,
            "classifier": prot_taxonomy_classifier
        }
        # Register as direct attributes
        self.prot_taxonomy_classifier_dropout = prot_taxonomy_classifier_dropout
        self.prot_taxonomy_hidden_layer = prot_taxonomy_hidden_layer
        self.prot_taxonomy_hidden_act = prot_taxonomy_hidden_act
        self.prot_taxonomy_classifier = prot_taxonomy_classifier
        
        # Protein keyword prediction (multi-label)
        prot_keyword_classifier_dropout = nn.Dropout(self.config.classifier_dropout_prob)
        prot_keyword_hidden_layer = nn.Linear(self.config.hidden_size, 2048, bias=True)
        prot_keyword_hidden_act = nn.GELU()
        prot_keyword_classifier = nn.Linear(2048, 100, bias=True)  # Assuming 100 keywords
        prot_keyword_output = nn.Sigmoid()
        self.pretrain_tasks["seq_level"]["prot_keyword"] = {
            "classifier_dropout": prot_keyword_classifier_dropout,
            "hidden_layer": prot_keyword_hidden_layer,
            "hidden_act": prot_keyword_hidden_act,
            "classifier": prot_keyword_classifier,
            "output": prot_keyword_output
        }
        # Register as direct attributes
        self.prot_keyword_classifier_dropout = prot_keyword_classifier_dropout
        self.prot_keyword_hidden_layer = prot_keyword_hidden_layer
        self.prot_keyword_hidden_act = prot_keyword_hidden_act
        self.prot_keyword_classifier = prot_keyword_classifier
        self.prot_keyword_output = prot_keyword_output
    
    @classmethod
    def from_pretrained_old(
        cls,
        old_model_path: str,
        config: Optional[LucaGPLMConfig] = None,
        **kwargs
    ) -> "LucaGPLMForPretraining":
        """
        Load a new LucaGPLMForPretraining from old LucaGPLM pretrained weights.
        
        Args:
            old_model_path: Path to the old model directory containing:
                - config.json: old model configuration
                - pytorch.pth or pytorch.pt: old model weights
                - log file with training args (optional)
            config: Optional new model configuration. If not provided, will be converted from old config.
            **kwargs: Additional arguments
            
        Returns:
            LucaGPLMForPretraining: New model with loaded old weights
        """
        import os
        import json
        from collections import OrderedDict
        
        # Load old config
        old_config_path = os.path.join(old_model_path, "config.json")
        if not os.path.exists(old_config_path):
            raise FileNotFoundError(f"Old model config not found at {old_config_path}")
            
        with open(old_config_path, 'r') as f:
            old_config_dict = json.load(f)
        
        # Convert old config to new config if not provided
        if config is None:
            # Map old config parameters to new config parameters
            new_config_dict = {
                "vocab_size": old_config_dict.get("vocab_size", 39),
                "max_position_embeddings": old_config_dict.get("max_position_embeddings", 1024),
                "num_hidden_layers": old_config_dict.get("num_hidden_layers", 12),
                "hidden_size": old_config_dict.get("hidden_size", 2560),
                "num_attention_heads": old_config_dict.get("num_attention_heads", 20),
                "intermediate_size": old_config_dict.get("intermediate_size", 10240),
                "hidden_act": old_config_dict.get("hidden_act", "gelu"),
                "attention_probs_dropout_prob": old_config_dict.get("attention_probs_dropout_prob", 0.1),
                "hidden_dropout_prob": old_config_dict.get("hidden_dropout_prob", 0.1),
                "classifier_dropout_prob": old_config_dict.get("classifier_dropout_prob", 0.1),
                "embed_scale": old_config_dict.get("embed_scale", 1.0),
                "ignore_index": old_config_dict.get("ignore_index", -100),
                "layer_norm_eps": 1e-12,
                "initializer_range": 0.02,
                "pooling_type": "avg"
            }
            
            # Debug: Print actual old config values for key architectural choices
            print(f"Old config architectural choices:")
            print(f"  no_position_embeddings: {old_config_dict.get('no_position_embeddings')}")
            print(f"  use_embed_layer_norm: {old_config_dict.get('use_embed_layer_norm')}")
            print(f"  hidden_size: {old_config_dict.get('hidden_size')}")
            print(f"  vocab_size: {old_config_dict.get('vocab_size')}")
            print(f"  embed_scale: {old_config_dict.get('embed_scale')}")
            print(f"  num_hidden_layers: {old_config_dict.get('num_hidden_layers')}")
            print(f"  num_attention_heads: {old_config_dict.get('num_attention_heads')}")
            print(f"  token_dropout: {old_config_dict.get('token_dropout')}")
            config = LucaGPLMConfig(**new_config_dict)
        
        # Create new model with converted config
        model = cls(config)
        
        # Load old model weights
        old_weights_path_pth = os.path.join(old_model_path, "pytorch.pth")
        old_weights_path_pt = os.path.join(old_model_path, "pytorch.pt")
        
        old_state_dict = None
        if os.path.exists(old_weights_path_pth):
            old_state_dict = torch.load(old_weights_path_pth, map_location="cpu", weights_only=False)
        elif os.path.exists(old_weights_path_pt):
            old_state_dict = torch.load(old_weights_path_pt, map_location="cpu", weights_only=False)
        else:
            raise FileNotFoundError(f"Old model weights not found at {old_weights_path_pth} or {old_weights_path_pt}")
        
        # Handle wrapped models (remove 'module.' prefix if present)
        if isinstance(old_state_dict, dict):
            new_old_state_dict = OrderedDict()
            for k, v in old_state_dict.items():
                name = k[7:] if k.startswith("module.") else k
                new_old_state_dict[name] = v
            old_state_dict = new_old_state_dict
        else:
            # If it's a model object, get state dict
            old_state_dict = old_state_dict.state_dict()
        
        # Create mapping from old parameter names to new parameter names
        new_state_dict = OrderedDict()
        model_state_dict_keys = set(model.state_dict().keys())
        
        for old_key, old_value in old_state_dict.items():
            new_key = None
            
            # Map embeddings - 直接使用原始参数名
            if old_key == "embed_tokens.weight":
                new_key = "lucagplm.embeddings.embed_tokens.weight"
            elif old_key == "embed_pos.weight":
                new_key = "lucagplm.embeddings.position_embeddings.weight"
            elif old_key == "embed_type.weight":
                new_key = "lucagplm.embeddings.token_type_embeddings.weight"
            elif old_key == "lm_head.weight":
                new_key = "lm_head.weight"
            elif old_key == "last_layer_norm.weight":
                new_key = "lucagplm.embeddings.last_layer_norm.weight"
            elif old_key == "last_layer_norm.bias":
                new_key = "lucagplm.embeddings.last_layer_norm.bias"
            # Map pretraining task heads - 直接映射到新模型的直接属性
            elif old_key == "contact_head.weight":
                new_key = "lm_head.weight"  # Map contact head to LM head
            elif old_key.startswith("pretrain_tasks."):
                # Map pretraining task parameters to direct attributes
                parts = old_key.split(".")
                if len(parts) >= 4:
                    task_type = parts[1]  # token_level, span_level, seq_level
                    task_name = parts[2]  # gene_mask, prot_mask, etc.
                    component = parts[3]  # classifier, hidden_layer, etc.
                    
                    # Map to direct attributes based on task name and component
                    if task_type == "token_level":
                        if task_name == "gene_mask":
                            if component == "classifier":
                                new_key = "gene_mask_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "gene_mask_classifier"
                        elif task_name == "prot_mask":
                            if component == "classifier":
                                new_key = "prot_mask_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_mask_classifier"
                    elif task_type == "span_level":
                        if task_name == "gene_type":
                            if component == "classifier":
                                new_key = "gene_type_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "gene_type_classifier"
                            elif component == "hidden_layer":
                                new_key = "gene_type_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "gene_type_hidden_layer"
                        elif task_name == "prot_homo":
                            if component == "classifier":
                                new_key = "prot_homo_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_homo_classifier"
                            elif component == "hidden_layer":
                                new_key = "prot_homo_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_homo_hidden_layer"
                        elif task_name == "prot_site":
                            if component == "classifier":
                                new_key = "prot_site_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_site_classifier"
                            elif component == "hidden_layer":
                                new_key = "prot_site_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_site_hidden_layer"
                        elif task_name == "prot_domain":
                            if component == "classifier":
                                new_key = "prot_domain_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_domain_classifier"
                            elif component == "hidden_layer":
                                new_key = "prot_domain_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_domain_hidden_layer"
                    elif task_type == "seq_level":
                        if task_name == "gene_taxonomy":
                            if component == "classifier":
                                new_key = "gene_taxonomy_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "gene_taxonomy_classifier"
                            elif component == "hidden_layer":
                                new_key = "gene_taxonomy_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "gene_taxonomy_hidden_layer"
                        elif task_name == "prot_taxonomy":
                            if component == "classifier":
                                new_key = "prot_taxonomy_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_taxonomy_classifier"
                            elif component == "hidden_layer":
                                new_key = "prot_taxonomy_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_taxonomy_hidden_layer"
                        elif task_name == "prot_keyword":
                            if component == "classifier":
                                new_key = "prot_keyword_classifier.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_keyword_classifier"
                            elif component == "hidden_layer":
                                new_key = "prot_keyword_hidden_layer.weight" if len(parts) == 5 and parts[4] == "weight" else "prot_keyword_hidden_layer"
            # Map transformer layers
            elif old_key.startswith("layers."):
                parts = old_key.split(".")
                layer_idx = int(parts[1])
                
                # Check if layer index is within range
                if layer_idx >= config.num_hidden_layers:
                    continue
                
                # Map layer parameters
                if parts[2] == "self_attn":
                    if parts[3] == "k_proj":
                        new_key = f"lucagplm.encoder.layers.{layer_idx}.attention.k_proj.{parts[4]}"
                    elif parts[3] == "v_proj":
                        new_key = f"lucagplm.encoder.layers.{layer_idx}.attention.v_proj.{parts[4]}"
                    elif parts[3] == "q_proj":
                        new_key = f"lucagplm.encoder.layers.{layer_idx}.attention.q_proj.{parts[4]}"
                    elif parts[3] == "out_proj":
                        new_key = f"lucagplm.encoder.layers.{layer_idx}.attention.out_proj.{parts[4]}"
                elif parts[2] == "self_attn_layer_norm":
                    new_key = f"lucagplm.encoder.layers.{layer_idx}.pre_layer_norm.{parts[3]}"
                elif parts[2] == "final_layer_norm":
                    new_key = f"lucagplm.encoder.layers.{layer_idx}.post_layer_norm.{parts[3]}"
                elif parts[2] == "fc1":
                    new_key = f"lucagplm.encoder.layers.{layer_idx}.fc1.{parts[3]}"
                elif parts[2] == "fc2":
                    new_key = f"lucagplm.encoder.layers.{layer_idx}.fc2.{parts[3]}"
                elif parts[2] == "final_layer_norm":
                    new_key = f"lucagplm.encoder.layers.{layer_idx}.post_layer_norm.{parts[3]}"
            
            # If we found a mapping and the key exists in the new model, add it
            if new_key is not None and new_key in model_state_dict_keys:
                # Check if shapes match
                if old_value.shape == model.state_dict()[new_key].shape:
                    new_state_dict[new_key] = old_value
                else:
                    print(f"Warning: Shape mismatch for {new_key}. Old: {old_value.shape}, New: {model.state_dict()[new_key].shape}")
        
        # Load the mapped state dict
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
        
        if missing_keys:
            print(f"Warning: Missing keys when loading old model: {missing_keys}")
        if unexpected_keys:
            print(f"Warning: Unexpected keys when loading old model: {unexpected_keys}")
            
        print(f"Successfully loaded old model from {old_model_path}")
        print(f"Loaded {len(new_state_dict)} parameters from old model")
        
        return model

    def get_input_embeddings(self):
        return self.lucagplm.get_input_embeddings()
    
    def set_input_embeddings(self, value):
        self.lucagplm.set_input_embeddings(value)
    
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        labels: Optional[Dict[str, torch.Tensor]] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs
    ):
        return_dict = return_dict if return_dict is not None else getattr(self.config, 'use_return_dict', True)
        
        # Get base model outputs
        outputs = self.lucagplm(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=True,  # We need hidden states for various tasks
            return_dict=return_dict,
        )
        
        sequence_output = outputs.last_hidden_state
        pooled_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else None
        
        # If no pooler_output is available, create one from sequence_output
        if pooled_output is None:
            # Use the first token's representation as pooled_output (like BERT's [CLS] token)
            pooled_output = sequence_output[:, 0, :]
        
        hidden_states = outputs.hidden_states
        
        # Initialize task outputs
        task_losses = {}
        task_logits = {
            "token_level": {},
            "span_level": {},
            "seq_level": {}
        }
        
        # Process token-level tasks
        if "token_level" in self.pretrain_tasks:
            for task_name, task_head in self.pretrain_tasks["token_level"].items():
                # Use LM head for token-level tasks
                task_logits["token_level"][task_name] = self.lm_head(sequence_output)
                
                # Calculate loss if labels are provided
                if labels is not None and f"token_level_{task_name}" in labels:
                    task_labels = labels[f"token_level_{task_name}"]
                    loss_fct = nn.CrossEntropyLoss(ignore_index=self.config.ignore_index)
                    task_losses[f"token_level_{task_name}"] = loss_fct(
                        task_logits["token_level"][task_name].view(-1, self.config.vocab_size),
                        task_labels.view(-1)
                    )
        
        # Process span-level tasks
        if "span_level" in self.pretrain_tasks:
            for task_name, task_head in self.pretrain_tasks["span_level"].items():
                # Apply dropout using direct attribute
                if task_name == "gene_type":
                    hidden = self.gene_type_classifier_dropout(sequence_output)
                    # Apply hidden layer if present
                    hidden = self.gene_type_hidden_layer(hidden)
                    hidden = self.gene_type_hidden_act(hidden)
                    # Apply classifier
                    task_logits["span_level"][task_name] = self.gene_type_classifier(hidden)
                elif task_name == "prot_homo":
                    hidden = self.prot_homo_classifier_dropout(sequence_output)
                    # Apply hidden layer if present
                    hidden = self.prot_homo_hidden_layer(hidden)
                    hidden = self.prot_homo_hidden_act(hidden)
                    # Apply classifier
                    task_logits["span_level"][task_name] = self.prot_homo_classifier(hidden)
                elif task_name == "prot_site":
                    hidden = self.prot_site_classifier_dropout(sequence_output)
                    # Apply hidden layer if present
                    hidden = self.prot_site_hidden_layer(hidden)
                    hidden = self.prot_site_hidden_act(hidden)
                    # Apply classifier
                    task_logits["span_level"][task_name] = self.prot_site_classifier(hidden)
                elif task_name == "prot_domain":
                    hidden = self.prot_domain_classifier_dropout(sequence_output)
                    # Apply hidden layer if present
                    hidden = self.prot_domain_hidden_layer(hidden)
                    hidden = self.prot_domain_hidden_act(hidden)
                    # Apply classifier
                    task_logits["span_level"][task_name] = self.prot_domain_classifier(hidden)
                
                # Calculate loss if labels are provided
                if labels is not None and f"span_level_{task_name}" in labels:
                    task_labels = labels[f"span_level_{task_name}"]
                    loss_fct = nn.CrossEntropyLoss(ignore_index=self.config.ignore_index)
                    task_losses[f"span_level_{task_name}"] = loss_fct(
                        task_logits["span_level"][task_name].view(-1, task_logits["span_level"][task_name].size(-1)),
                        task_labels.view(-1)
                    )
        
        # Process sequence-level tasks
        if "seq_level" in self.pretrain_tasks and pooled_output is not None:
            for task_name, task_head in self.pretrain_tasks["seq_level"].items():
                # Apply dropout and hidden layers using direct attributes
                if task_name == "gene_taxonomy":
                    hidden = self.gene_taxonomy_classifier_dropout(pooled_output)
                    # Apply hidden layer if present
                    hidden = self.gene_taxonomy_hidden_layer(hidden)
                    hidden = self.gene_taxonomy_hidden_act(hidden)
                    # Apply classifier
                    logits = self.gene_taxonomy_classifier(hidden)
                elif task_name == "prot_taxonomy":
                    hidden = self.prot_taxonomy_classifier_dropout(pooled_output)
                    # Apply hidden layer if present
                    hidden = self.prot_taxonomy_hidden_layer(hidden)
                    hidden = self.prot_taxonomy_hidden_act(hidden)
                    # Apply classifier
                    logits = self.prot_taxonomy_classifier(hidden)
                elif task_name == "prot_keyword":
                    hidden = self.prot_keyword_classifier_dropout(pooled_output)
                    # Apply hidden layer if present
                    hidden = self.prot_keyword_hidden_layer(hidden)
                    hidden = self.prot_keyword_hidden_act(hidden)
                    # Apply classifier
                    logits = self.prot_keyword_classifier(hidden)
                    # Apply output activation if present (e.g., sigmoid for multi-label)
                    logits = self.prot_keyword_output(logits)
                
                task_logits["seq_level"][task_name] = logits
                
                # Calculate loss if labels are provided
                if labels is not None and f"seq_level_{task_name}" in labels:
                    task_labels = labels[f"seq_level_{task_name}"]
                    
                    # Use different loss functions based on task type
                    if task_name == "prot_keyword":  # Multi-label classification
                        loss_fct = nn.BCEWithLogitsLoss()
                        task_losses[f"seq_level_{task_name}"] = loss_fct(logits, task_labels.float())
                    else:  # Multi-class classification
                        loss_fct = nn.CrossEntropyLoss()
                        task_losses[f"seq_level_{task_name}"] = loss_fct(logits, task_labels)
        
        # Calculate total loss
        total_loss = None
        if task_losses:
            total_loss = sum(task_losses.values())
        
        if not return_dict:
            outputs = (sequence_output, pooled_output) + outputs[2:]
            if task_logits:
                outputs = outputs + (task_logits,)
            if total_loss is not None:
                outputs = (total_loss,) + outputs
            return outputs
        
        return {
            "loss": total_loss,
            "logits": task_logits,
            "last_hidden_state": sequence_output,
            "pooler_output": pooled_output,
            "hidden_states": outputs.hidden_states,
            "attentions": outputs.attentions,
        }

class LucaGPLMFeedForward(nn.Module):
    """
    FeedForward network for downstream tasks
    """
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.1, activation='gelu'):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU() if activation == 'relu' else nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.layers(x)

__all__ = [
    "LucaGPLMModel",
    "LucaGPLMPreTrainedModel",
    "LucaGPLMForPretraining",
    "LucaGPLMFeedForward",
]
