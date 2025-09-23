__all__ = [
    "ResBlock",
    "AMPBlock",
    "GatedResBlock",
]
import torch
from torch import nn, Tensor
from lt_utils.common import *
import torch.nn.functional as F
from lt_utils.misc_utils import filter_kwargs
from lt_tensor.model_zoo.fusion import FiLMConv1d
from lt_tensor.model_zoo.convs import ConvBase, BidirectionalConv1d


def get_snake(name: Literal["snake", "snakebeta"] = "snake"):
    assert name.lower() in [
        "snake",
        "snakebeta",
    ], f"'{name}' is not a valid snake activation! use 'snake' or 'snakebeta'"
    from lt_tensor.model_zoo.activations import snake

    if name.lower() == "snake":
        return snake.Snake
    return snake.SnakeBeta


class GatedResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: Union[int, List[int]] = 3,
        dilation: Tuple[int, ...] = (1, 3, 5),
        activation: Callable[[None], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        alpha: float = 1.0,
        train_alpha: bool = True,
        use_beta: bool = True,
        beta: float = 0.1,
        train_beta: bool = True,
        mode: Literal[
            "base", "mesh", "dense", "hilo", "gru", "stochastic", "attn"
        ] = "mesh",
        use_activation_on_pw: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
        init_weights: bool = True,
        conditional: bool = False,
        conditional_size: Optional[int] = None,
        conditional_injection_depth: int = 1,
        stochastic_dropout: float = 0.1,
        **kwargs,
    ):
        super().__init__()
        assert mode in [
            "base",
            "mesh",
            "dense",
            "hilo",
            "gru",
            "stochastic",
            "attn",
        ], f"Invalid mode {mode}"
        self.conditional = conditional
        self.stochastic_dropout = stochastic_dropout
        self.alpha = nn.Parameter(
            torch.tensor(float(max(alpha, 0.1)), dtype=torch.float32),
            requires_grad=train_alpha,
        )
        self.beta = nn.Parameter(
            torch.tensor(float(max(beta, 1e-7)), dtype=torch.float32),
            requires_grad=train_beta,
        )
        self.use_beta = use_beta
        self.mode: Literal[
            "base", "mesh", "dense", "hilo", "gru", "stochastic", "attn"
        ] = mode
        self.dilation_blocks = nn.ModuleList()
        gp2_activation = nn.Identity if not use_activation_on_pw else activation
        if isinstance(kernel_size, int):
            ks = [kernel_size for _ in range(len(dilation))]
        else:
            ks = ks
        for d, k in zip(dilation, ks):
            self.dilation_blocks.append(
                nn.ModuleDict(
                    {
                        "conv": nn.Sequential(
                            activation(),
                            BidirectionalConv1d(
                                channels,
                                channels,
                                k,
                                dilation=d,
                                padding=self.get_padding(k, d),
                                norm=norm,
                                groups_fwd=groups,
                                groups_bwd=groups,
                            ),
                        ),
                        "pw": nn.Sequential(
                            gp2_activation(),
                            self.get_1d_conv(
                                channels,
                                norm=norm,
                                groups=groups,
                            ),
                        ),
                    }
                )
            )
        self.conditional_injection_depth = max(conditional_injection_depth, 1)
        self.cond = (
            nn.Identity()
            if not conditional
            else FiLMConv1d(
                cond_channels=conditional_size or channels,
                feat_channels=channels,
                kernel_size=3,
                padding=1,
            )
        )
        if init_weights:
            self.dilation_blocks.apply(
                lambda m: self._normal_init_default(
                    m=m,
                    **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs),
                )
            )

    def _get_gated(self, y: Tensor, x_cond: Optional[Tensor] = None):
        alpha, h = torch.chunk(y, 2, dim=1)
        if self.use_beta:
            h_beta = self.beta + h.tanh()
        else:
            h_beta = h.tanh()
        if x_cond is None:
            return alpha.sigmoid() * h_beta
        return alpha.sigmoid() * (h_beta + x_cond)

    def _dense_forward(self, x, x_cond=None):
        """Instead of a single running state or a final skip sum, collect all intermediate gated outputs and combine them at the end"""
        feats = []
        h = x
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](h)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            feats.append(b["pw"](g) * self.alpha)
            h = h + feats[-1]  # optional local residual
        return x + torch.mean(torch.stack(feats), dim=0)

    def _stochastic_forward(self, x, x_cond=None):
        """At training time randomly drop individual block contributions"""
        for i, b in enumerate(self.dilation_blocks):
            if self.training and torch.rand(1) < self.stochastic_dropout:
                continue
            y = b["conv"](x)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            x = x + b["pw"](g) * self.alpha
        return x

    def _gru_forward(self, x, x_cond=None):
        """Treat the dilation stack as a mini-RNN: each step updates
        a hidden state rather than overwriting or adding blindly."""
        h = torch.zeros_like(x)
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](x)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            r = torch.sigmoid(self.alpha)  # reset gate
            z = torch.sigmoid(self.alpha * 0.5)  # update gate
            h = (1 - z) * h + z * b["pw"](g * r)
            x = h
        return h

    def _hilo_forward(self, x, x_cond=None):
        """High-Pass / Low-Pass Split
        Let each block predict a delta that is subtracted as well as added,
        so the residual learns to separate slow and fast components.
        """
        low = x
        high = 0
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](low)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            h = b["pw"](g) * self.alpha
            high = high + h
            low = low - h
        return torch.cat([low, high], dim=1)  # double channels

    def _mesh_forward(self, x: Tensor, x_cond: Optional[Tensor] = None):
        skip = torch.zeros_like(x)
        for i, b in enumerate(self.dilation_blocks):
            base = b["conv"](x)
            if i < self.conditional_injection_depth:
                x = self._get_gated(base, x_cond)
            else:
                x = self._get_gated(base, None)
            y = b["pw"](x) * self.alpha
            skip = y + skip
        return skip + x

    def _base_forward(self, x: Tensor, x_cond: Optional[Tensor] = None):
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](x)
            if i < self.conditional_injection_depth:
                gated = self._get_gated(y, x_cond)
            else:
                gated = self._get_gated(y, None)
            y = b["pw"](gated) * self.alpha
            x = y + x
        return x

    def _attn_forward(self, x, x_cond=None):
        """Compute attention weights across the block outputs and blend them"""
        outs = []
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](x)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            outs.append(b["pw"](g))
        outs = torch.stack(outs, dim=0)  # [layers, B, C, T]
        weights = F.softmax(self.alpha * torch.ones(len(outs)), dim=0)
        return x + (weights[:, None, None, None] * outs).sum(dim=0)

    def forward(self, x: Tensor, cond: Optional[Tensor] = None):
        if self.conditional and cond is not None:
            x_cond = self.cond(x=x, cond=cond)
        else:
            x_cond = None

        match self.mode:
            case "base":
                return self._base_forward(x, x_cond)
            case "dense":
                return self._dense_forward(x, x_cond)
            case "gru":
                return self._gru_forward(x, x_cond)
            case "hilo":
                return self._hilo_forward(x, x_cond)
            case "attn":
                return self._attn_forward(x, x_cond)
            case "stochastic":
                return self._stochastic_forward(x, x_cond)
            case _:
                return self._mesh_forward(x, x_cond)


class ResBlock(ConvBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: Callable[[None], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        version: Literal["v1", "v2"] = "v1",
        norm: Optional[Literal["weight", "spectral"]] = None,
        init_weights: bool = True,
        **kwargs,
    ):
        super().__init__()
        self.resblock_version = version

        self.convs1 = nn.ModuleList()
        self.convs2 = nn.ModuleList()
        cnn2_padding = self.get_padding(kernel_size, 1)
        for i, d in enumerate(dilation):
            mdk = dict(
                in_channels=channels,
                kernel_size=kernel_size,
                dilation=d,
                padding=self.get_padding(kernel_size, d),
                norm=norm,
                groups=groups,
            )
            if self.resblock_version == "v1":
                self.convs2.append(
                    nn.Sequential(
                        activation(),
                        self.get_1d_conv(
                            channels,
                            kernel_size=kernel_size,
                            dilation=1,
                            padding=cnn2_padding,
                            norm=norm,
                            groups=groups,
                        ),
                    )
                )
            else:
                self.convs2.append(nn.Identity())

            if i == 0:
                self.convs1.append(self.get_1d_conv(**mdk))
            else:
                self.convs1.append(nn.Sequential(activation(), self.get_1d_conv(**mdk)))
        if init_weights:
            _init_fn = lambda m: self._normal_init_default(
                m=m, **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs)
            )
            self.convs1.apply(_init_fn)
            if self.resblock_version == "v1":
                self.convs2.apply(_init_fn)

    def forward(self, x: Tensor):
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = c1(x)
            x = c2(xt) + x
        return x


class AMPBlock(ConvBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'

    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.

    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        activation: Optional[Callable[[Tensor], Tensor]] = None,
        version: Literal["v1", "v2"] = "v1",
        groups: int = 1,
        norm: Optional[Literal["weight", "spectral"]] = None,
        init_weights: bool = True,
        **kwargs,
    ):
        super().__init__()
        from lt_tensor.model_zoo.activations import alias_free

        self.resblock_version = version
        if activation is None:
            from lt_tensor.model_zoo.activations import snake

            activation = lambda: snake.SnakeBeta(channels, alpha_logscale=True)

        ch1_kwargs = dict(in_channels=channels, kernel_size=kernel_size, norm=norm)
        ch2_kwargs = dict(
            in_channels=channels,
            kernel_size=kernel_size,
            padding=self.get_padding(kernel_size, 1),
            norm=norm,
        )

        self.convs = nn.ModuleList()
        for i, d in enumerate(dilation):
            if version == "v1":
                self.convs.append(
                    nn.Sequential(
                        alias_free.Activation1d(activation=activation()),
                        self.get_1d_conv(
                            **ch1_kwargs,
                            dilation=d,
                            padding=self.get_padding(kernel_size, d),
                            groups=groups,
                        ),
                        alias_free.Activation1d(activation=activation()),
                        self.get_1d_conv(**ch2_kwargs, groups=groups),
                    )
                )
            else:
                self.convs.append(
                    nn.Sequential(
                        alias_free.Activation1d(activation=activation()),
                        self.get_1d_conv(
                            **ch1_kwargs,
                            dilation=d,
                            padding=self.get_padding(kernel_size, d),
                            groups=groups,
                        ),
                    ),
                )

        self.num_layers = len(self.convs)
        if init_weights:
            _init_fn = lambda m: self._normal_init_default(
                m=m, **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs)
            )
            self.convs.apply(_init_fn)

    def forward(self, x):
        for layer in self.convs:
            x = layer(x) + x
        return x
