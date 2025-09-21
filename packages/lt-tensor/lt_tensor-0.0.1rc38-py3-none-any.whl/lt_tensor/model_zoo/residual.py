__all__ = [
    "ResBlock",
    "AMPBlock",
    "GatedResBlock",
]
import torch
import math
from lt_utils.common import *
from lt_utils.misc_utils import flatten_list
from torch import nn, Tensor
from lt_tensor.model_zoo.convs import ConvBase
from torch.nn.utils.parametrizations import weight_norm


def get_snake(name: Literal["snake", "snakebeta"] = "snake"):
    assert name.lower() in [
        "snake",
        "snakebeta",
    ], f"'{name}' is not a valid snake activation! use 'snake' or 'snakebeta'"
    from lt_tensor.model_zoo.activations import snake

    if name.lower() == "snake":
        return snake.Snake
    return snake.SnakeBeta


def _get_alpha_gamma_activation(
    name: Optional[Literal["sigmoid", "tanh", "sin", "cos"]],
) -> Callable[[Tensor], Tensor]:
    if name is None:
        return lambda x: x

    match name:
        case "cos":
            return lambda x: torch.cos(x)
        case "sin":
            return lambda x: torch.sin(x)
        case "tanh":
            return lambda x: torch.tanh(x)
        case _:
            return lambda x: torch.sigmoid(x)


class GatedResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: Tuple[int, ...] = (1, 3, 9),
        activation: Callable[[None], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        residual_scale: float = 0.5,
        gamma_activation: Literal["sigmoid", "tanh", "sin", "cos"] = "sigmoid",
        alpha_activation: Optional[Literal["sigmoid", "tanh", "sin", "cos"]] = None,
        mode: Literal["base", "reset"] = "base",
        use_activation_on_pw: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
    ):
        super().__init__()
        assert gamma_activation in [
            "sigmoid",
            "tanh",
            "sin",
            "cos",
        ], f'Unknown gamma_activation "{gamma_activation}". Use one of: "sigmoid", "tanh", "sin" or "cos".'
        assert alpha_activation is None or alpha_activation in [
            "sigmoid",
            "tanh",
            "sin",
            "cos",
        ], f'Unknown alpha_activation "{alpha_activation}". Use one of: "sigmoid", "tanh", "sin", "cos" or None in case no activation should be used.'
        self.residual_scale = max(residual_scale, 0.1)
        self.alpha_activation = _get_alpha_gamma_activation(alpha_activation)
        self.gamma_activation = _get_alpha_gamma_activation(gamma_activation)
        self.mode: Literal["base", "reset"] = mode
        self.dilation_blocks = nn.ModuleList()
        gp2_activation = nn.Identity if not use_activation_on_pw else activation
        for d in dilation:
            self.dilation_blocks.append(
                nn.ModuleDict(
                    {
                        "conv": nn.Sequential(
                            activation(),
                            self.get_1d_conv(
                                channels,
                                int(channels * 2),
                                kernel_size,
                                dilation=d,
                                padding=self.get_padding(kernel_size, d),
                                norm=norm,
                                groups=min(
                                    math.gcd(channels, int(channels * 2)), groups
                                ),
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
        self.dilation_blocks.apply(self._init_conv_weights_a)

    def _get_gated(self, y: Tensor):
        # Split into two halves (GLU): alpha and gamma
        alpha, gamma = torch.chunk(y, 2, dim=1)
        gated = self.alpha_activation(alpha) * self.gamma_activation(gamma)
        return gated

    def _reset_forward(self, x: Tensor):
        xt = torch.zeros_like(x)
        for b in self.dilation_blocks:
            y = b["conv"](x)
            gated = self._get_gated(y)
            y = b["pw"](gated) * self.residual_scale
            xt = y + xt
        return xt + x

    def _base_forward(self, x: Tensor):
        for b in self.dilation_blocks:
            y = b["conv"](x)
            gated = self._get_gated(y)
            y = b["pw"](gated) * self.residual_scale
            x = y + x
        return x

    def forward(self, x: Tensor):
        if self.mode == "reset":
            return self._reset_forward(x)
        return self._base_forward(x)


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
        *args,
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

        self.convs1.apply(self._init_conv_weights_a)

        if self.resblock_version == "v1":
            self.convs2.apply(self._init_conv_weights_a)

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
        *args,
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

        self.convs: List[Callable[[Tensor], Tensor]] = nn.ModuleList()
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
        self.convs.apply(self._init_conv_weights_a)

    def forward(self, x):
        for layer in self.convs:
            x = layer(x) + x
        return x
