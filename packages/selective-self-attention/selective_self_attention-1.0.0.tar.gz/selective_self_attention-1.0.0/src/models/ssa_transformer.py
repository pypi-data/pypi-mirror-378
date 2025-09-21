"""
SSA-Enhanced Transformer Model
Implements the Selective Self-Attention transformer from the NeurIPS 2024 paper.
"""

from typing import Optional, List, Dict, Any

try:
    import torch
    from torch import nn
    from torch.nn import functional as F
except Exception:  # pragma: no cover
    torch = None
    nn = object
    F = object

from .modules import TransformerBlock, SelectiveSelfAttention, TemperatureModule
from .embeddings import PositionalEncoding


class SSATransformer(nn.Module):
    """
    Transformer model with Selective Self-Attention.
    
    This implementation follows the NeurIPS 2024 paper:
    "Selective Attention: Enhancing Transformer through Principled Context Control"
    
    Key features:
    - Temperature scaling for queries and values
    - Position-aware and token-aware temperature
    - Weight sharing strategy for parameter efficiency
    - Drop-in replacement for standard transformers
    """
    
    def __init__(
        self,
        vocab_size: int = 50257,
        max_seq_len: int = 1024,
        dim: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        mlp_ratio: float = 4.0,
        drop: float = 0.1,
        attn_drop: float = 0.1,
        use_ssa: bool = True,
        ssa_config: Optional[Dict[str, Any]] = None
    ):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.dim = dim
        self.num_layers = num_layers
        self.use_ssa = use_ssa
        
        # Token embeddings
        self.token_emb = nn.Embedding(vocab_size, dim)
        self.pos_emb = PositionalEncoding(dim, max_seq_len)
        self.emb_drop = nn.Dropout(drop)
        
        # SSA configuration
        default_ssa_config = {
            'use_query_temp': True,
            'use_key_temp': False,  # Optional, disabled by default as per paper
            'use_value_temp': True,
            'use_position_aware': True,
            'weight_sharing': True
        }
        if ssa_config:
            default_ssa_config.update(ssa_config)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerBlock(
                dim=dim,
                num_heads=num_heads,
                mlp_ratio=mlp_ratio,
                drop=drop,
                attn_drop=attn_drop,
                use_ssa=use_ssa,
                **default_ssa_config
            )
            for _ in range(num_layers)
        ])
        
        self.ln_f = nn.LayerNorm(dim)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights following the paper's recommendations."""
        if torch is None:
            return
        
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(
        self, 
        input_ids: 'torch.Tensor', 
        attention_mask: Optional['torch.Tensor'] = None,
        return_attention_stats: bool = False
    ) -> Dict[str, 'torch.Tensor']:
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        
        batch_size, seq_len = input_ids.shape
        assert seq_len <= self.max_seq_len, f"Sequence length {seq_len} exceeds maximum {self.max_seq_len}"
        
        # Embeddings
        token_embeddings = self.token_emb(input_ids)  # [B, T, C]
        position_embeddings = self.pos_emb(seq_len)  # [T, C]
        x = self.emb_drop(token_embeddings + position_embeddings)
        
        # Prepare causal mask
        if attention_mask is None:
            # Create causal mask
            mask = torch.triu(torch.ones(seq_len, seq_len, device=input_ids.device), diagonal=1)
            mask = mask.bool()
            mask = mask.unsqueeze(0).unsqueeze(0)  # [1, 1, T, T]
        else:
            mask = attention_mask
        
        # Apply transformer layers
        attention_stats = []
        for i, layer in enumerate(self.layers):
            x = layer(x, mask=mask)
            
            # Collect attention statistics if requested
            if return_attention_stats and self.use_ssa:
                if hasattr(layer.attn, 'get_attention_spikiness'):
                    spikiness = layer.attn.get_attention_spikiness(x)
                    attention_stats.append({
                        'layer': i,
                        'spikiness': spikiness
                    })
        
        # Final layer norm
        x = self.ln_f(x)
        
        result = {'hidden_states': x}
        if return_attention_stats:
            result['attention_stats'] = attention_stats
        
        return result
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics including parameter count and SSA overhead."""
        if torch is None:
            return {'error': 'PyTorch not available'}
        
        total_params = sum(p.numel() for p in self.parameters())
        
        # Count SSA-specific parameters
        ssa_params = 0
        if self.use_ssa:
            for layer in self.layers:
                if hasattr(layer.attn, 'query_temp'):
                    ssa_params += sum(p.numel() for p in layer.attn.query_temp.parameters())
                if hasattr(layer.attn, 'value_temp'):
                    ssa_params += sum(p.numel() for p in layer.attn.value_temp.parameters())
        
        ssa_overhead = (ssa_params / total_params) * 100 if total_params > 0 else 0
        
        return {
            'total_parameters': total_params,
            'ssa_parameters': ssa_params,
            'ssa_overhead_percent': ssa_overhead,
            'num_layers': self.num_layers,
            'hidden_dim': self.dim,
            'num_heads': self.num_heads,
            'use_ssa': self.use_ssa
        }


class SSALanguageModel(nn.Module):
    """
    Language modeling head for SSA Transformer.
    Includes next-token prediction and loss computation.
    """
    
    def __init__(
        self,
        transformer: SSATransformer,
        tie_weights: bool = True
    ):
        if torch is None:
            self._no_torch = True
            return
        super().__init__()
        
        self.transformer = transformer
        self.lm_head = nn.Linear(transformer.dim, transformer.vocab_size, bias=False)
        
        # Tie weights with token embedding
        if tie_weights:
            self.lm_head.weight = transformer.token_emb.weight
    
    def forward(
        self,
        input_ids: 'torch.Tensor',
        labels: Optional['torch.Tensor'] = None,
        attention_mask: Optional['torch.Tensor'] = None,
        return_attention_stats: bool = False
    ) -> Dict[str, 'torch.Tensor']:
        if torch is None:
            raise RuntimeError('PyTorch not available: cannot run forward pass.')
        
        # Forward through transformer
        transformer_outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_attention_stats=return_attention_stats
        )
        
        hidden_states = transformer_outputs['hidden_states']
        
        # Language modeling head
        logits = self.lm_head(hidden_states)
        
        result = {
            'logits': logits,
            'hidden_states': hidden_states
        }
        
        # Compute loss if labels provided
        if labels is not None:
            # Shift labels for next-token prediction
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            # Compute cross-entropy loss
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            )
            result['loss'] = loss
        
        # Add attention stats if available
        if 'attention_stats' in transformer_outputs:
            result['attention_stats'] = transformer_outputs['attention_stats']
        
        return result


def create_ssa_model(config: Dict[str, Any]) -> SSALanguageModel:
    """
    Factory function to create SSA language model from config.
    
    Args:
        config: Configuration dictionary with model parameters
        
    Returns:
        SSALanguageModel instance
    """
    model_config = config.get('model', {})
    
    transformer = SSATransformer(
        vocab_size=model_config.get('vocab_size', 50257),
        max_seq_len=model_config.get('max_seq_len', 1024),
        dim=model_config.get('dim', 768),
        num_layers=model_config.get('num_layers', 12),
        num_heads=model_config.get('num_heads', 12),
        mlp_ratio=model_config.get('mlp_ratio', 4.0),
        drop=model_config.get('dropout', 0.1),
        attn_drop=model_config.get('attn_dropout', 0.1),
        use_ssa=model_config.get('use_ssa', True),
        ssa_config=model_config.get('ssa_config', {})
    )
    
    model = SSALanguageModel(
        transformer=transformer,
        tie_weights=model_config.get('tie_weights', True)
    )
    
    return model