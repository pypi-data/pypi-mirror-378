# dl_module.py
import math
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, Iterable, Union, List, Callable
from pathlib import Path
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import _LRScheduler
import torch.nn.functional as F


# --------------------------
# Utility: device & metrics
# --------------------------
def get_device(device: Optional[str] = None) -> str:
    """Get the best available device with fallback options."""
    if device:
        if device.startswith('cuda') and not torch.cuda.is_available():
            warnings.warn("CUDA requested but not available. Falling back to CPU.")
            return "cpu"
        return device

    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def accuracy_from_logits(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Calculate accuracy from logits and targets."""
    preds = logits.argmax(dim=1)
    return (preds == targets).float().mean().item()


def top_k_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5) -> float:
    """Calculate top-k accuracy."""
    _, pred = logits.topk(k, 1, True, True)
    pred = pred.t()
    correct = pred.eq(targets.view(1, -1).expand_as(pred))
    return correct[:k].sum().float() / targets.size(0)


class MetricTracker:
    """Track and compute various metrics."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.metrics = {}
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.metrics:
                self.metrics[key] = []
            if isinstance(value, torch.Tensor):
                value = value.item()
            self.metrics[key].append(value)
    
    def get_average(self, key: str) -> float:
        if key not in self.metrics or not self.metrics[key]:
            return 0.0
        return sum(self.metrics[key]) / len(self.metrics[key])
    
    def get_all_averages(self) -> Dict[str, float]:
        return {key: self.get_average(key) for key in self.metrics}


# --------------------------
# Base Architecture Class
# --------------------------
class BaseArchitecture(nn.Module, ABC):
    """Base class for all architectures with common functionality."""
    
    def __init__(self):
        super().__init__()
        self._input_shape = None
        self._output_shape = None
    
    @abstractmethod
    def forward(self, x):
        pass
    
    def get_num_parameters(self) -> int:
        """Get total number of parameters."""
        return sum(p.numel() for p in self.parameters())
    
    def get_num_trainable_parameters(self) -> int:
        """Get number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def freeze_layers(self, layer_names: List[str]):
        """Freeze specific layers by name."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = False
    
    def unfreeze_layers(self, layer_names: List[str]):
        """Unfreeze specific layers by name."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = True


# --------------------------
# Enhanced Architectures
# --------------------------
class MLPClassifier(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, ...], 
        num_classes: int, 
        hidden_sizes=(256, 128), 
        dropout=0.1,
        activation='relu',
        batch_norm=False,
        bias=True
    ):
        super().__init__()
        self._input_shape = input_shape
        
        # Calculate input features
        in_features = 1
        for d in input_shape:
            in_features *= d
        
        # Activation function
        activations = {
            'relu': nn.ReLU,
            'gelu': nn.GELU,
            'leaky_relu': nn.LeakyReLU,
            'elu': nn.ELU,
            'swish': nn.SiLU,
            'tanh': nn.Tanh
        }
        if activation not in activations:
            raise ValueError(f"Unsupported activation: {activation}")
        act_fn = activations[activation]
        
        layers = [nn.Flatten()]
        prev = in_features
        
        for i, h in enumerate(hidden_sizes):
            layers.append(nn.Linear(prev, h, bias=bias))
            if batch_norm:
                layers.append(nn.BatchNorm1d(h))
            layers.append(act_fn())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev = h
        
        layers.append(nn.Linear(prev, num_classes, bias=bias))
        self.net = nn.Sequential(*layers)
        self._output_shape = (num_classes,)

    def forward(self, x):
        return self.net(x)


class SimpleCNN(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int, int], 
        num_classes: int, 
        base=32,
        num_conv_layers=3,
        kernel_size=3,
        pool_size=2,
        dropout=0.1,
        activation='relu',
        batch_norm=True,
        global_pool='avg'
    ):
        super().__init__()
        self._input_shape = input_shape
        c, h, w = input_shape
        
        # Activation function
        activations = {'relu': nn.ReLU, 'gelu': nn.GELU, 'leaky_relu': nn.LeakyReLU}
        act_fn = activations.get(activation, nn.ReLU)
        
        # Build feature extractor
        layers = []
        in_channels = c
        current_h, current_w = h, w
        
        for i in range(num_conv_layers):
            out_channels = base * (2 ** i)
            layers.extend([
                nn.Conv2d(in_channels, out_channels, kernel_size, padding=kernel_size // 2),
            ])
            if batch_norm:
                layers.append(nn.BatchNorm2d(out_channels))
            layers.extend([
                act_fn(),
                nn.MaxPool2d(pool_size)
            ])
            if dropout > 0 and i < num_conv_layers - 1:
                layers.append(nn.Dropout2d(dropout))
            
            in_channels = out_channels
            current_h //= pool_size
            current_w //= pool_size
        
        self.features = nn.Sequential(*layers)
        
        # Global pooling or flatten
        if global_pool == 'avg':
            self.pool = nn.AdaptiveAvgPool2d(1)
            classifier_input = out_channels
        elif global_pool == 'max':
            self.pool = nn.AdaptiveMaxPool2d(1)
            classifier_input = out_channels
        else:
            self.pool = nn.Identity()
            classifier_input = out_channels * current_h * current_w
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(classifier_input, 256),
            act_fn(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(256, num_classes)
        )
        self._output_shape = (num_classes,)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        return self.classifier(x)


class EnhancedLSTM(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int], 
        num_classes: int, 
        hidden=128, 
        num_layers=1, 
        bidirectional=False, 
        dropout=0.0,
        cell_type='LSTM',
        pooling='last',
        attention=False
    ):
        super().__init__()
        self._input_shape = input_shape
        t, f = input_shape
        
        # RNN cell type
        rnn_cells = {'LSTM': nn.LSTM, 'GRU': nn.GRU, 'RNN': nn.RNN}
        if cell_type not in rnn_cells:
            raise ValueError(f"Unsupported cell type: {cell_type}")
        
        rnn_kwargs = {
            'input_size': f,
            'hidden_size': hidden,
            'num_layers': num_layers,
            'batch_first': True,
            'bidirectional': bidirectional,
            'dropout': dropout if num_layers > 1 else 0.0
        }
        
        self.rnn = rnn_cells[cell_type](**rnn_kwargs)
        self.pooling = pooling
        self.attention = attention
        self.cell_type = cell_type
        
        mult = 2 if bidirectional else 1
        rnn_output_size = hidden * mult
        
        if attention:
            self.attention_layer = nn.MultiheadAttention(
                embed_dim=rnn_output_size, 
                num_heads=8, 
                batch_first=True
            )
        
        self.fc = nn.Linear(rnn_output_size, num_classes)
        self._output_shape = (num_classes,)

    def forward(self, x):
        # x: (B, T, F)
        if self.cell_type == 'LSTM':
            out, (h_n, c_n) = self.rnn(x)
        else:
            out, h_n = self.rnn(x)
        
        if self.attention:
            out, _ = self.attention_layer(out, out, out)
        
        if self.pooling == 'last':
            # Fixed: Handle bidirectional properly
            if self.rnn.bidirectional:
                # h_n shape: (num_layers * num_directions, batch, hidden_size)
                # We want the last layer's forward and backward hidden states
                forward_hidden = h_n[-2] if self.rnn.num_layers > 1 else h_n[0]
                backward_hidden = h_n[-1] if self.rnn.num_layers > 1 else h_n[1]
                pooled = torch.cat([forward_hidden, backward_hidden], dim=1)
            else:
                pooled = h_n[-1]  # Last layer
        elif self.pooling == 'mean':
            pooled = out.mean(dim=1)
        elif self.pooling == 'max':
            pooled = out.max(dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling: {self.pooling}")
        
        return self.fc(pooled)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x: (B, T, D)
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class TransformerEncoderClassifier(BaseArchitecture):
    def __init__(
        self, 
        vocab_size: int, 
        num_classes: int, 
        d_model=512, 
        nhead=8, 
        num_layers=6, 
        dim_feedforward=2048, 
        dropout=0.1,
        max_seq_len=512,
        pooling='cls',
        use_pos_encoding=True
    ):
        super().__init__()
        
        self.d_model = d_model
        self.pooling = pooling
        self.use_pos_encoding = use_pos_encoding
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        if use_pos_encoding:
            self.pos_encoder = PositionalEncoding(d_model, max_seq_len, dropout)
        
        # CLS token for classification
        if pooling == 'cls':
            self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=dim_feedforward, 
            dropout=dropout,
            batch_first=True,
            activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Layer norm
        self.norm = nn.LayerNorm(d_model)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_classes)
        )
        
        self._output_shape = (num_classes,)

    def forward(self, input_ids, attention_mask=None):
        batch_size, seq_len = input_ids.shape
        
        # Embedding
        x = self.embedding(input_ids) * math.sqrt(self.d_model)
        
        # Add CLS token if using cls pooling
        if self.pooling == 'cls':
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat([cls_tokens, x], dim=1)
            if attention_mask is not None:
                cls_mask = torch.ones(batch_size, 1, device=attention_mask.device)
                attention_mask = torch.cat([cls_mask, attention_mask], dim=1)
        
        # Positional encoding
        if self.use_pos_encoding:
            x = self.pos_encoder(x)
        
        # Create padding mask for transformer
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)
        
        # Transformer encoding
        x = self.transformer(x, src_key_padding_mask=key_padding_mask)
        x = self.norm(x)
        
        # Pooling
        if self.pooling == 'cls':
            pooled = x[:, 0]  # use CLS token output
        elif self.pooling == 'mean':
            if attention_mask is not None:
                mask = attention_mask.unsqueeze(-1).float()
                pooled = (x * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            else:
                pooled = x.mean(dim=1)
        elif self.pooling == 'max':
            pooled = x.max(dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling: {self.pooling}")
        
        return self.classifier(pooled)


class ConvAutoencoder(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int, int], 
        latent_dim=64, 
        base=32,
        num_layers=3,
        activation='relu',
        use_skip_connections=False
    ):
        super().__init__()
        self._input_shape = input_shape
        c, h, w = input_shape
        self.use_skip_connections = use_skip_connections
        
        # Activation function
        activations = {'relu': nn.ReLU, 'gelu': nn.GELU, 'leaky_relu': nn.LeakyReLU}
        act_fn = activations.get(activation, nn.ReLU)
        
        # Encoder
        encoder_layers = []
        in_channels = c
        self.encoder_channels = []
        
        for i in range(num_layers):
            out_channels = base * (2 ** i)
            encoder_layers.extend([
                nn.Conv2d(in_channels, out_channels, 3, stride=2, padding=1),
                nn.BatchNorm2d(out_channels),
                act_fn()
            ])
            self.encoder_channels.append(out_channels)
            in_channels = out_channels
            h, w = h // 2, w // 2
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Latent space
        self.to_latent = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_channels * h * w, latent_dim)
        )
        
        self.from_latent = nn.Sequential(
            nn.Linear(latent_dim, in_channels * h * w),
            nn.Unflatten(1, (in_channels, h, w))
        )
        
        # Decoder
        decoder_layers = []
        for i in reversed(range(num_layers)):
            out_channels = base * (2 ** (i-1)) if i > 0 else c
            if i == 0:  # Final layer
                decoder_layers.extend([
                    nn.ConvTranspose2d(in_channels, out_channels, 4, stride=2, padding=1),
                    nn.Sigmoid()
                ])
            else:
                decoder_layers.extend([
                    nn.ConvTranspose2d(in_channels, out_channels, 4, stride=2, padding=1),
                    nn.BatchNorm2d(out_channels),
                    act_fn()
                ])
            in_channels = out_channels
        
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, x):
        if self.use_skip_connections:
            skip_connections = []
            for layer in self.encoder:
                x = layer(x)
                if isinstance(layer, nn.Conv2d):
                    skip_connections.append(x)
        else:
            x = self.encoder(x)
            skip_connections = None
        
        z = self.to_latent(x)
        return z, skip_connections

    def decode(self, z, skip_connections=None):
        x = self.from_latent(z)
        if self.use_skip_connections and skip_connections:
            # Example: U-Net style skip connection addition
            for i, layer in enumerate(self.decoder):
                x = layer(x)
                if isinstance(layer, nn.ConvTranspose2d) and i < len(skip_connections):
                    skip = skip_connections[-(i // 3 + 1)]
                    if x.shape == skip.shape:
                        x = x + skip
        else:
            x = self.decoder(x)
        
        return x

    def forward(self, x):
        z, skip_connections = self.encode(x)
        return self.decode(z, skip_connections)

# ---------- Attention U-Net (2D) ----------
class _ConvBNAct(nn.Module):
    def __init__(self, in_c, out_c, k=3, s=1, p=1, act=nn.ReLU):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_c, out_c, k, s, p, bias=False),
            nn.BatchNorm2d(out_c),
            act(inplace=True) if act in (nn.ReLU, nn.LeakyReLU) else act()
        )
    def forward(self, x): return self.block(x)

class _DoubleConv(nn.Module):
    def __init__(self, in_c, out_c, mid_c=None):
        super().__init__()
        mid_c = mid_c or out_c
        self.conv = nn.Sequential(
            _ConvBNAct(in_c, mid_c, 3, 1, 1),
            _ConvBNAct(mid_c, out_c, 3, 1, 1),
        )
    def forward(self, x): return self.conv(x)

class _AttnGate(nn.Module):
    """Additive attention gate from Attention U-Net."""
    def __init__(self, x_ch, g_ch, inter_ch):
        super().__init__()
        self.theta_x = nn.Conv2d(x_ch, inter_ch, 2, 2, bias=False)  # downsample x
        self.phi_g   = nn.Conv2d(g_ch, inter_ch, 1, 1, bias=True)
        self.psi     = nn.Conv2d(inter_ch, 1, 1, 1, bias=True)
        self.act     = nn.ReLU(inplace=True)
        self.sig     = nn.Sigmoid()
        self.ups     = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)

    def forward(self, x, g):
        # x: skip, g: decoder feature (coarser)
        theta = self.theta_x(x)
        phi   = self.phi_g(g)
        # match spatial sizes
        if phi.shape[-2:] != theta.shape[-2:]:
            phi = F.interpolate(phi, size=theta.shape[-2:], mode='bilinear', align_corners=False)
        f = self.act(theta + phi)
        psi = self.sig(self.psi(f))
        psi_up = self.ups(psi)
        if psi_up.shape[-2:] != x.shape[-2:]:
            psi_up = F.interpolate(psi_up, size=x.shape[-2:], mode='bilinear', align_corners=False)
        return x * psi_up

class AttentionUNet(BaseArchitecture):
    """
    Attention U-Net for 2D semantic segmentation.
    input_shape: (C, H, W)
    """
    def __init__(self, input_shape: Tuple[int,int,int], num_classes: int, base=64):
        super().__init__()
        c, _, _ = input_shape
        self._input_shape = input_shape

        self.enc1 = _DoubleConv(c, base)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = _DoubleConv(base, base*2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = _DoubleConv(base*2, base*4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = _DoubleConv(base*4, base*8)
        self.pool4 = nn.MaxPool2d(2)

        self.bottleneck = _DoubleConv(base*8, base*16)

        self.gate4 = _AttnGate(x_ch=base*8, g_ch=base*16, inter_ch=base*8)
        self.up4 = nn.ConvTranspose2d(base*16, base*8, 2, 2)
        self.dec4 = _DoubleConv(base*16, base*8)

        self.gate3 = _AttnGate(x_ch=base*4, g_ch=base*8, inter_ch=base*4)
        self.up3 = nn.ConvTranspose2d(base*8, base*4, 2, 2)
        self.dec3 = _DoubleConv(base*8, base*4)

        self.gate2 = _AttnGate(x_ch=base*2, g_ch=base*4, inter_ch=base*2)
        self.up2 = nn.ConvTranspose2d(base*4, base*2, 2, 2)
        self.dec2 = _DoubleConv(base*4, base*2)

        self.gate1 = _AttnGate(x_ch=base, g_ch=base*2, inter_ch=base)
        self.up1 = nn.ConvTranspose2d(base*2, base, 2, 2)
        self.dec1 = _DoubleConv(base*2, base)

        self.out_conv = nn.Conv2d(base, num_classes, 1)
        self._output_shape = (num_classes,)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))

        b  = self.bottleneck(self.pool4(e4))

        g4 = self.gate4(e4, b)
        d4 = self.dec4(torch.cat([self.up4(b), g4], dim=1))

        g3 = self.gate3(e3, d4)
        d3 = self.dec3(torch.cat([self.up3(d4), g3], dim=1))

        g2 = self.gate2(e2, d3)
        d2 = self.dec2(torch.cat([self.up2(d3), g2], dim=1))

        g1 = self.gate1(e1, d2)
        d1 = self.dec1(torch.cat([self.up1(d2), g1], dim=1))

        return self.out_conv(d1)

# ---------- TransUNet (compact) ----------
class PatchEmbed(nn.Module):
    def __init__(self, in_ch=3, embed_dim=256, patch=16):
        super().__init__()
        self.proj = nn.Conv2d(in_ch, embed_dim, kernel_size=patch, stride=patch)
    def forward(self, x):  # (B,C,H,W) -> (B, N, D)
        x = self.proj(x)  # (B,D,H/ps,W/ps)
        B, D, H, W = x.shape
        x = x.flatten(2).transpose(1, 2)  # (B, N=H*W, D)
        return x, (H, W)

class TransUNet(BaseArchitecture):
    """
    Minimal TransUNet: CNN encoder -> ViT bottleneck -> U-Net decoder.
    input_shape: (C, H, W)
    """
    def __init__(self, input_shape: Tuple[int,int,int], num_classes: int, base=64,
                 d_model=256, nhead=8, num_layers=4, patch_size=16, ff=1024, dropout=0.1):
        super().__init__()
        c, _, _ = input_shape
        self._input_shape = input_shape

        # Shallow CNN encoder (to provide strong low/mid-level skips)
        self.enc1 = _DoubleConv(c, base)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = _DoubleConv(base, base*2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = _DoubleConv(base*2, base*4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = _DoubleConv(base*4, base*8)
        self.pool4 = nn.MaxPool2d(2)

        # Patch embedding from deepest feature (base*8 channels)
        self.to_patch = nn.Conv2d(base*8, d_model, kernel_size=1)
        self.pe = PatchEmbed(in_ch=d_model, embed_dim=d_model, patch=patch_size)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=ff, dropout=dropout, batch_first=True, activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.norm = nn.LayerNorm(d_model)

        # Project tokens back to 2D map
        self.from_token = nn.Conv2d(d_model, base*8, kernel_size=1)

        # U-Net style decoder
        self.up4 = nn.ConvTranspose2d(base*8, base*8, 2, 2); self.dec4 = _DoubleConv(base*16, base*8)
        self.up3 = nn.ConvTranspose2d(base*8, base*4, 2, 2); self.dec3 = _DoubleConv(base*8,  base*4)
        self.up2 = nn.ConvTranspose2d(base*4, base*2, 2, 2); self.dec2 = _DoubleConv(base*4,  base*2)
        self.up1 = nn.ConvTranspose2d(base*2, base,   2, 2); self.dec1 = _DoubleConv(base*2,  base)

        self.out_conv = nn.Conv2d(base, num_classes, 1)
        self._output_shape = (num_classes,)

    def forward(self, x):
        e1 = self.enc1(x)           # (B, b,   H,   W)
        e2 = self.enc2(self.pool1(e1))  # (B,2b, H/2, W/2)
        e3 = self.enc3(self.pool2(e2))  # (B,4b, H/4, W/4)
        e4 = self.enc4(self.pool3(e3))  # (B,8b, H/8, W/8)
        d  = self.pool4(e4)             # (B,8b, H/16,W/16)

        d = self.to_patch(d)            # (B, D, h, w)
        tokens, (h, w) = self.pe(d)     # (B, N, D)
        tokens = self.transformer(tokens)
        tokens = self.norm(tokens)
        tokens = tokens.transpose(1, 2).reshape(tokens.size(0), -1, h, w)  # (B, D, h, w)
        d = self.from_token(tokens)     # (B, 8b, h, w)

        d4 = self.dec4(torch.cat([self.up4(d), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out_conv(d1)
# ---------- 3D-ResNet (ResNet-18 style) ----------
class BasicBlock3D(nn.Module):
    expansion = 1
    def __init__(self, in_planes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv3d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm3d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv3d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm3d(planes)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return self.relu(out)

def _make_layer3d(block, in_planes, planes, blocks, stride=1):
    downsample = None
    if stride != 1 or in_planes != planes * block.expansion:
        downsample = nn.Sequential(
            nn.Conv3d(in_planes, planes * block.expansion, kernel_size=1, stride=stride, bias=False),
            nn.BatchNorm3d(planes * block.expansion),
        )
    layers = [block(in_planes, planes, stride, downsample)]
    for _ in range(1, blocks):
        layers.append(block(planes * block.expansion, planes))
    return nn.Sequential(*layers)

class ResNet3D(BaseArchitecture):
    """
    ResNet-18 3D for classification on (C, D, H, W) inputs (e.g., video clips or 3D volumes).
    """
    def __init__(self, input_shape: Tuple[int,int,int,int], num_classes: int, base=64):
        super().__init__()
        c, _, _, _ = input_shape
        self._input_shape = input_shape
        self.in_planes = base
        self.conv1 = nn.Conv3d(c, base, kernel_size=7, stride=(1,2,2), padding=(3,3,3), bias=False)
        self.bn1 = nn.BatchNorm3d(base)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool3d(kernel_size=3, stride=2, padding=1)
        self.layer1 = _make_layer3d(BasicBlock3D, base,  base,  blocks=2, stride=1)
        self.layer2 = _make_layer3d(BasicBlock3D, base,  base*2,blocks=2, stride=2)
        self.layer3 = _make_layer3d(BasicBlock3D, base*2,base*4,blocks=2, stride=2)
        self.layer4 = _make_layer3d(BasicBlock3D, base*4,base*8,blocks=2, stride=2)
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.fc = nn.Linear(base*8, num_classes)
        self._output_shape = (num_classes,)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x); x = self.layer2(x); x = self.layer3(x); x = self.layer4(x)
        x = self.pool(x).flatten(1)
        return self.fc(x)
# ---------- Inception-ResNet (small) ----------
class InceptionResA(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.branch1 = _ConvBNAct(in_ch, out_ch//4, 1, 1, 0)
        self.branch3 = nn.Sequential(
            _ConvBNAct(in_ch, out_ch//4, 1, 1, 0),
            _ConvBNAct(out_ch//4, out_ch//4, 3, 1, 1),
        )
        self.branch5 = nn.Sequential(
            _ConvBNAct(in_ch, out_ch//4, 1, 1, 0),
            _ConvBNAct(out_ch//4, out_ch//4, 3, 1, 1),
            _ConvBNAct(out_ch//4, out_ch//4, 3, 1, 1),
        )
        self.conv_linear = nn.Conv2d(3*(out_ch//4), in_ch, 1)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        out = torch.cat([self.branch1(x), self.branch3(x), self.branch5(x)], dim=1)
        out = self.conv_linear(out)
        out = x + out
        return self.relu(out)

class ReductionA(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.branch3 = nn.Sequential(
            _ConvBNAct(in_ch, out_ch//2, 3, 2, 1),
        )
        self.branch5 = nn.Sequential(
            _ConvBNAct(in_ch, out_ch//4, 1, 1, 0),
            _ConvBNAct(out_ch//4, out_ch//4, 3, 1, 1),
            _ConvBNAct(out_ch//4, out_ch//2, 3, 2, 1),
        )
        self.pool = nn.MaxPool2d(3, 2, 1)

    def forward(self, x):
        return torch.cat([self.branch3(x), self.branch5(x), self.pool(x)], dim=1)

class InceptionResNet(BaseArchitecture):
    """
    Compact Inception-ResNet classifier.
    """
    def __init__(self, input_shape: Tuple[int,int,int], num_classes: int, base=64, blocks=5):
        super().__init__()
        c, _, _ = input_shape
        self._input_shape = input_shape
        self.stem = nn.Sequential(
            _ConvBNAct(c, base, 3, 2, 1),
            _ConvBNAct(base, base, 3, 1, 1),
            _ConvBNAct(base, base*2, 3, 1, 1),
        )
        in_ch = base*2
        self.incep = nn.Sequential(*[InceptionResA(in_ch, out_ch=in_ch) for _ in range(blocks)])
        self.reduc = ReductionA(in_ch, out_ch=in_ch)
        self.incep2 = nn.Sequential(*[InceptionResA(in_ch*2, out_ch=in_ch*2) for _ in range(blocks)])
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(in_ch*2, num_classes)
        self._output_shape = (num_classes,)

    def forward(self, x):
        x = self.stem(x)
        x = self.incep(x)
        x = self.reduc(x)
        x = self.incep2(x)
        x = self.pool(x).flatten(1)
        return self.fc(x)

# ---------- EfficientNet-style (MBConv + SE) ----------
class SqueezeExcite(nn.Module):
    def __init__(self, c, r=4):
        super().__init__()
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c, c//r, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(c//r, c, 1),
            nn.Sigmoid()
        )
    def forward(self, x): 
        w = self.se(x); return x * w

class MBConv(nn.Module):
    def __init__(self, in_c, out_c, k=3, s=1, expand=4, se=True, drop=0.0):
        super().__init__()
        mid = in_c*expand
        self.use_res = (s==1 and in_c==out_c)
        layers = []
        if expand != 1:
            layers += [nn.Conv2d(in_c, mid, 1, 1, 0, bias=False), nn.BatchNorm2d(mid), nn.SiLU()]
        layers += [nn.Conv2d(mid, mid, k, s, k//2, groups=mid, bias=False), nn.BatchNorm2d(mid), nn.SiLU()]
        if se: layers += [SqueezeExcite(mid)]
        layers += [nn.Conv2d(mid, out_c, 1, 1, 0, bias=False), nn.BatchNorm2d(out_c)]
        self.block = nn.Sequential(*layers)
        self.dropout = nn.Dropout2d(drop) if drop>0 else nn.Identity()

    def forward(self, x):
        out = self.block(x)
        out = self.dropout(out)
        return x + out if self.use_res else out

class EfficientNetSmall(BaseArchitecture):
    """
    Compact EfficientNet-like classifier.
    """
    def __init__(self, input_shape: Tuple[int,int,int], num_classes: int, width=32):
        super().__init__()
        c, _, _ = input_shape
        self._input_shape = input_shape
        self.stem = nn.Sequential(
            nn.Conv2d(c, width, 3, 2, 1, bias=False),
            nn.BatchNorm2d(width), nn.SiLU()
        )
        self.stage1 = nn.Sequential(MBConv(width,   width,   k=3, s=1, expand=1),
                                    MBConv(width,   width,   k=3, s=1, expand=1))
        self.stage2 = nn.Sequential(MBConv(width,   width*2, k=3, s=2),
                                    MBConv(width*2, width*2, k=3, s=1))
        self.stage3 = nn.Sequential(MBConv(width*2, width*4, k=5, s=2),
                                    MBConv(width*4, width*4, k=5, s=1))
        self.stage4 = nn.Sequential(MBConv(width*4, width*6, k=3, s=2),
                                    MBConv(width*6, width*6, k=3, s=1))
        self.head = nn.Sequential(
            nn.Conv2d(width*6, width*8, 1, 1, 0, bias=False),
            nn.BatchNorm2d(width*8), nn.SiLU(),
            nn.AdaptiveAvgPool2d(1)
        )
        self.fc = nn.Linear(width*8, num_classes)
        self._output_shape = (num_classes,)

    def forward(self, x):
        x = self.stem(x)
        x = self.stage1(x); x = self.stage2(x); x = self.stage3(x); x = self.stage4(x)
        x = self.head(x).flatten(1)
        return self.fc(x)




# --------------------------
# Enhanced Model Registry
# --------------------------
MODEL_REGISTRY = {
    "MLP": MLPClassifier,
    "CNN": SimpleCNN,
    "LSTM": EnhancedLSTM,
    "TransformerEncoderClassifier": TransformerEncoderClassifier,
    "ConvAutoencoder": ConvAutoencoder,
}

MODEL_REGISTRY.update({
    "AttentionUNet": AttentionUNet,
    "TransUNet": TransUNet,
    "ResNet3D": ResNet3D,
    "InceptionResNet": InceptionResNet,
    "EfficientNet": EfficientNetSmall,
})

# --------------------------
# Loss Functions
# --------------------------
class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance."""
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class LabelSmoothingLoss(nn.Module):
    """Label smoothing loss."""
    def __init__(self, num_classes, smoothing=0.1):
        super().__init__()
        self.num_classes = num_classes
        self.smoothing = smoothing
        self.confidence = 1.0 - smoothing

    def forward(self, inputs, targets):
        log_probs = F.log_softmax(inputs, dim=1)
        targets_one_hot = torch.zeros_like(log_probs).scatter_(1, targets.unsqueeze(1), 1)
        targets_smooth = targets_one_hot * self.confidence + (1 - targets_one_hot) * self.smoothing / (self.num_classes - 1)
        return -(targets_smooth * log_probs).sum(dim=1).mean()


LOSS_REGISTRY = {
    'cross_entropy': nn.CrossEntropyLoss,
    'mse': nn.MSELoss,
    'mae': nn.L1Loss,
    'bce': nn.BCELoss,
    'bce_logits': nn.BCEWithLogitsLoss,
    'focal': FocalLoss,
    'label_smoothing': LabelSmoothingLoss,
    'huber': nn.HuberLoss,
}


# --------------------------
# Enhanced Model Wrapper
# --------------------------
class DLModel:
    """Enhanced unified interface for deep learning models."""
    
    def __init__(
        self,
        model_type: str,
        input_shape: Optional[Tuple[int, ...]] = None,
        num_classes: Optional[int] = None,
        task: str = "classification",
        vocab_size: Optional[int] = None,
        lr: float = 1e-3,
        device: Optional[str] = None,
        optimizer: str = 'adam',
        optimizer_kwargs: Optional[Dict[str, Any]] = None,
        loss_fn: str = 'auto',
        loss_kwargs: Optional[Dict[str, Any]] = None,
        scheduler: Optional[str] = None,
        scheduler_kwargs: Optional[Dict[str, Any]] = None,
        gradient_clip: Optional[float] = None,
        **arch_kwargs
    ):
        """
        Initialize the DLModel with the specified parameters.

        Args:
            model_type (str): The type of model to use.
            input_shape (Optional[Tuple[int, ...]]): The shape of the input data.
            num_classes (Optional[int]): The number of output classes.
            task (str): The task type (e.g., "classification", "regression").
            vocab_size (Optional[int]): The vocabulary size (for NLP tasks).
            lr (float): Learning rate.
            device (Optional[str]): Device to run the model on (e.g., "cuda", "cpu").
            optimizer (str): Optimizer type.
            optimizer_kwargs (Optional[Dict[str, Any]]): Additional arguments for the optimizer.
            loss_fn (str): Loss function type.
            loss_kwargs (Optional[Dict[str, Any]]): Additional arguments for the loss function.
            scheduler (Optional[str]): Learning rate scheduler type.
            scheduler_kwargs (Optional[Dict[str, Any]]): Additional arguments for the scheduler.
            gradient_clip (Optional[float]): Gradient clipping value.
            **arch_kwargs: Additional architecture-specific arguments.
        """
        self.model_type = model_type
        self.task = task
        self.device = get_device(device)
        self.gradient_clip = gradient_clip
        
        # Initialize history and metrics
        self.history = {"loss": [], "val_loss": [], "metric": [], "val_metric": []}
        self.metric_tracker = MetricTracker()
        
        # Build model
        self.model = self._build_model(
            model_type, input_shape, num_classes, vocab_size, task, **arch_kwargs
        )
        self.model.to(self.device)
        
        # Setup loss function
        self.criterion = self._setup_loss_function(loss_fn, task, num_classes, loss_kwargs)
        
        # Setup optimizer
        self.optimizer = self._setup_optimizer(optimizer, lr, optimizer_kwargs)
        
        # Setup scheduler
        self.scheduler = self._setup_scheduler(scheduler, scheduler_kwargs)
        
        # Model info
        print(f"Model: {model_type} | Task: {task}")
        print(f"Total parameters: {self.model.get_num_parameters():,}")
        print(f"Trainable parameters: {self.model.get_num_trainable_parameters():,}")
        print(f"Device: {self.device}")

    def _build_model(self, model_type, input_shape, num_classes, vocab_size, task, **arch_kwargs):
        """Build the model based on type and task."""
        if model_type not in MODEL_REGISTRY:
            raise ValueError(f"Unsupported model: {model_type}. Available: {list(MODEL_REGISTRY.keys())}")
        
        model_class = MODEL_REGISTRY[model_type]
        # In DLModel._build_model(...)
        if task == "segmentation":
            if input_shape is None or num_classes is None:
                raise ValueError("Segmentation requires input_shape and num_classes.")
            # Expect models to output (B, num_classes, H, W)
            return model_class(input_shape=input_shape, num_classes=num_classes, **arch_kwargs)

        if model_type == "TransformerEncoderClassifier":
            if vocab_size is None or num_classes is None:
                raise ValueError("TransformerEncoderClassifier needs vocab_size and num_classes.")
            return model_class(vocab_size=vocab_size, num_classes=num_classes, **arch_kwargs)
        elif model_type == "ConvAutoencoder":
            if input_shape is None:
                raise ValueError("ConvAutoencoder needs input_shape=(C,H,W).")
            return model_class(input_shape=input_shape, **arch_kwargs)
        else:
            if input_shape is None:
                raise ValueError(f"{model_type} needs input_shape.")
            
            if task == "classification":
                if num_classes is None:
                    raise ValueError("Classification requires num_classes.")
                return model_class(input_shape=input_shape, num_classes=num_classes, **arch_kwargs)
            elif task == "regression":
                output_dim = arch_kwargs.pop('output_dim', 1)
                return model_class(input_shape=input_shape, num_classes=output_dim, **arch_kwargs)
            elif task == "autoencoder":
                if model_type != "ConvAutoencoder":
                    raise ValueError("For autoencoder task, use model_type='ConvAutoencoder'.")
                return model_class(input_shape=input_shape, **arch_kwargs)
            else:
                raise ValueError("task must be 'classification', 'regression', or 'autoencoder'.")

    def _setup_loss_function(self, loss_fn, task, num_classes=None, loss_kwargs=None):
        """Setup loss function based on task and parameters."""
        loss_kwargs = loss_kwargs or {}
        
        if loss_fn == 'auto':
            if task == "classification":
                loss_fn = 'cross_entropy'
            elif task == "regression":
                loss_fn = 'mse'
            elif task == "autoencoder":
                loss_fn = 'mse'
            elif task == "segmentation":
                loss_fn = 'cross_entropy'
        
        if loss_fn not in LOSS_REGISTRY:
            raise ValueError(f"Unsupported loss function: {loss_fn}")
        
        loss_class = LOSS_REGISTRY[loss_fn]
        if loss_fn == 'label_smoothing' and num_classes:
            loss_kwargs.setdefault('num_classes', num_classes)
        
        return loss_class(**loss_kwargs)

    def _setup_optimizer(self, optimizer_name, lr, optimizer_kwargs):
        """Setup optimizer."""
        optimizer_kwargs = optimizer_kwargs or {}
        optimizers = {
            'adam': optim.Adam,
            'adamw': optim.AdamW,
            'sgd': optim.SGD,
            'rmsprop': optim.RMSprop,
            'adagrad': optim.Adagrad,
        }
        if optimizer_name not in optimizers:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")
        return optimizers[optimizer_name](self.model.parameters(), lr=lr, **optimizer_kwargs)

    def _setup_scheduler(self, scheduler_name, scheduler_kwargs):
        """Setup learning rate scheduler."""
        if scheduler_name is None:
            return None
        scheduler_kwargs = scheduler_kwargs or {}
        schedulers = {
            'step': optim.lr_scheduler.StepLR,
            'multistep': optim.lr_scheduler.MultiStepLR,
            'exponential': optim.lr_scheduler.ExponentialLR,
            'cosine': optim.lr_scheduler.CosineAnnealingLR,
            'plateau': optim.lr_scheduler.ReduceLROnPlateau,
            'cosine_warm': optim.lr_scheduler.CosineAnnealingWarmRestarts,
        }
        if scheduler_name not in schedulers:
            raise ValueError(f"Unsupported scheduler: {scheduler_name}")
        return schedulers[scheduler_name](self.optimizer, **scheduler_kwargs)

    def _compute_metrics(self, outputs, targets, task):
        """Compute metrics based on task type."""
        with torch.no_grad():
            if task == "classification":
                acc = accuracy_from_logits(outputs, targets)
                metrics = {'accuracy': acc}
                if outputs.size(1) >= 5:
                    metrics['top5_accuracy'] = top_k_accuracy(outputs, targets, k=5)
                return metrics
            elif task == "regression":
                # Fix: Ensure dimensions match
                if outputs.dim() > 1:
                    outputs = outputs.squeeze(-1)  # Remove last dimension if it's 1
                targets = targets.float()
                
                mse = F.mse_loss(outputs, targets)
                rmse = torch.sqrt(mse)
                mae = F.l1_loss(outputs, targets)
                return {'mse': mse.item(), 'rmse': rmse.item(), 'mae': mae.item()}
            # In DLModel._compute_metrics(...)
            elif task == "segmentation":
                # outputs: (B,C,H,W), targets: (B,H,W) with class indices
                probs = torch.softmax(outputs, dim=1)
                preds = probs.argmax(dim=1)  # (B,H,W)
                correct = (preds == targets).float().mean().item()
                # Dice macro (ignoring background=0 optional)
                num_classes = outputs.size(1)
                dice_scores = []
                for cls in range(num_classes):
                    pred_c = (preds == cls).float()
                    targ_c = (targets == cls).float()
                    inter = (pred_c * targ_c).sum()
                    denom = pred_c.sum() + targ_c.sum()
                    dice = (2*inter + 1e-6) / (denom + 1e-6)
                    dice_scores.append(dice.item())
                return {'pixel_acc': correct, 'dice_macro': sum(dice_scores)/len(dice_scores)}
            else:
                return {}

    def _forward_batch(self, batch, training=True):
        """Process a single batch and return loss, outputs, and targets."""
        if self.task == "segmentation":
            x, y = batch[0].to(self.device), batch[1].to(self.device).long()
            outputs = self.model(x)  
            loss = self.criterion(outputs, y)  # cross-entropy over pixels
            return loss, outputs, y
        if self.model_type == "TransformerEncoderClassifier":
            if isinstance(batch, (list, tuple)):
                if len(batch) == 3:
                    input_ids, attention_mask, targets = batch
                elif len(batch) == 2:
                    input_ids, targets = batch
                    attention_mask = None
                else:
                    raise ValueError("Transformer batch must be (input_ids, attention_mask, targets) or (input_ids, targets).")
            else:
                raise ValueError("Transformer expects tuple batch.")
            input_ids = input_ids.to(self.device)
            targets = targets.to(self.device)
            if attention_mask is not None:
                attention_mask = attention_mask.to(self.device)
                outputs = self.model(input_ids, attention_mask=attention_mask)
            else:
                outputs = self.model(input_ids)
            loss = self.criterion(outputs, targets)
            return loss, outputs, targets
        
        # For standard supervised learning or autoencoder
        if isinstance(batch, (list, tuple)):
            if self.task == "autoencoder":
                x = batch[0].to(self.device)
                outputs = self.model(x)
                loss = self.criterion(outputs, x)
                return loss, None, None
            else:
                x, y = batch[0].to(self.device), batch[1].to(self.device)
                outputs = self.model(x)
                
                # Fix: Handle regression dimension mismatch
                if self.task == "regression":
                    if outputs.dim() > 1:
                        outputs = outputs.squeeze(-1)  # Remove last dimension if it's 1
                    y = y.float()
                
                loss = self.criterion(outputs, y)
                return loss, outputs, y
        else:
            raise ValueError("Unsupported batch format.")

    def _train_one_epoch(self, loader):
        """Train for one epoch."""
        self.model.train()
        self.metric_tracker.reset()
        for batch_idx, batch in enumerate(loader):
            self.optimizer.zero_grad()
            loss, outputs, targets = self._forward_batch(batch, training=True)
            loss.backward()
            if self.gradient_clip:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
            self.optimizer.step()
            self.metric_tracker.update(loss=loss.item())
            if outputs is not None and targets is not None:
                metrics = self._compute_metrics(outputs, targets, self.task)
                self.metric_tracker.update(**metrics)
        return self.metric_tracker.get_all_averages()

    def _eval_one_epoch(self, loader):
        """Evaluate for one epoch."""
        self.model.eval()
        self.metric_tracker.reset()
        with torch.no_grad():
            for batch in loader:
                loss, outputs, targets = self._forward_batch(batch, training=False)
                self.metric_tracker.update(loss=loss.item())
                if outputs is not None and targets is not None:
                    metrics = self._compute_metrics(outputs, targets, self.task)
                    self.metric_tracker.update(**metrics)
        return self.metric_tracker.get_all_averages()

    def fit(self, train_loader, val_loader=None, epochs=10, print_every=1, early_stopping: Optional[int] = None):
        """Train the model for a number of epochs.
        Args:
            train_loader (DataLoader): DataLoader for the training dataset.
            val_loader (Optional[DataLoader]): DataLoader for the validation dataset.
            epochs (int): Number of training epochs.
            print_every (int): Print training progress every N epochs.
            early_stopping (Optional[int]): Early stopping patience.
        """
        best_val_loss = float('inf')
        epochs_no_improve = 0
        for epoch in range(1, epochs + 1):
            train_metrics = self._train_one_epoch(train_loader)
            if val_loader is not None:
                val_metrics = self._eval_one_epoch(val_loader)
            else:
                val_metrics = {}
            self.history["loss"].append(train_metrics.get("loss", 0))
            self.history["metric"].append(train_metrics)
            self.history["val_loss"].append(val_metrics.get("loss", 0))
            self.history["val_metric"].append(val_metrics)
            if epoch % print_every == 0:
                print(f"Epoch {epoch:03d} | Train Loss: {train_metrics.get('loss', 0):.4f} | Val Loss: {val_metrics.get('loss', 0):.4f}")
            if val_loader is not None and early_stopping is not None:
                if val_metrics.get('loss', float('inf')) < best_val_loss:
                    best_val_loss = val_metrics.get('loss')
                    epochs_no_improve = 0
                    best_state = self.model.state_dict()
                else:
                    epochs_no_improve += 1
                    if epochs_no_improve >= early_stopping:
                        print(f"Early stopping at epoch {epoch}, restoring best model.")
                        self.model.load_state_dict(best_state)
                        break
            if self.scheduler is not None:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics.get('loss', 0))
                else:
                    self.scheduler.step()
        return self

    def evaluate(self, loader):
        """
        Evaluate the model on the given DataLoader.
        Args:
            loader (DataLoader): DataLoader for the evaluation dataset.
        """
        metrics = self._eval_one_epoch(loader)
        if self.task == "classification":
            print(f"Evaluation - Loss: {metrics.get('loss', 0):.4f}, Accuracy: {metrics.get('accuracy', 0):.4f}")
        elif self.task == "regression":
            print(f"Evaluation - Loss: {metrics.get('loss', 0):.4f}, Metrics: {metrics}")
        else:
            print(f"Evaluation - Reconstruction Loss: {metrics.get('loss', 0):.4f}")
        return metrics

    @torch.no_grad()
    def predict(self, X: torch.Tensor):
        """
        Make predictions using the trained model.
        Args:
            X (torch.Tensor): Input tensor for prediction.
        """
        self.model.eval()
        X = X.to(self.device)
        outputs = self.model(X)
        if self.task == "classification":
            return torch.softmax(outputs, dim=1).cpu()
        return outputs.cpu()

    def save_model(self, path: Union[str, Path]):
        """
        Save the model checkpoint.
        Args:
            path (Union[str, Path]): Path to save the model checkpoint.
        """
        torch.save({
            "state_dict": self.model.state_dict(),
            "model_type": self.model_type,
            "task": self.task
        }, path)
        print(f"Model saved to {path}")

    def load_model(self, path: Union[str, Path]):
        """
        Load the model checkpoint.
        Args:
            path (Union[str, Path]): Path to the model checkpoint.
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.to(self.device)
        print(f"Model loaded from {path}")
        return self