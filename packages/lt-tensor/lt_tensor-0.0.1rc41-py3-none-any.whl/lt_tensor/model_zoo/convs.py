__all__ = [
    "ConvBase",
    "BidirectionalConv1d",
    "calc_max_groups",
    "get_padding_1d_a",
    "get_padding_1d_b",
    "get_padding_2d",
    "get_conv",
    "remove_norm",
    "is_groups_compatible",
    "is_conv",
]
import math
import torch
from torch import Tensor
from lt_utils.common import *
from lt_utils.misc_utils import filter_kwargs
from torch.nn.utils.parametrize import remove_parametrizations
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from lt_tensor.common import nn, Model

TP_SHAPE_1: TypeAlias = Union[int, Tuple[int]]
TP_SHAPE_2: TypeAlias = Union[TP_SHAPE_1, Tuple[int, int]]
TP_SHAPE_3: TypeAlias = Union[TP_SHAPE_2, Tuple[int, int, int]]

TC: TypeAlias = Callable[[Tensor], Tensor]


def _dummy(module: Model, *args, **kwargs):
    return module


def is_groups_compatible(channels_in: int, channels_out: int, groups: int):
    if channels_in < 2 or channels_out < 2:
        return groups == 1
    return groups % channels_in == 0 and groups % channels_out == 0


def calc_max_groups(channels_in: int, channels_out: int):
    return math.gcd(int(channels_in), int(channels_out))


def is_conv(module: nn.Module):
    return isinstance(
        module,
        (
            nn.Conv1d,
            nn.Conv2d,
            nn.Conv3d,
            nn.ConvTranspose1d,
            nn.ConvTranspose2d,
            nn.ConvTranspose3d,
            nn.LazyConv1d,
            nn.LazyConv2d,
            nn.LazyConv3d,
            nn.LazyConvTranspose1d,
            nn.LazyConvTranspose2d,
            nn.LazyConvTranspose3d,
            nn.modules.conv._ConvNd,
        ),
    )


def get_padding_1d_a(kernel_size: int, dilation: int):
    return (kernel_size - 1) * dilation // 2


def get_padding_1d_b(kernel_size: int, dilation: int):
    return (kernel_size * dilation) - dilation // 2


def get_weight_norm(
    norm_type: Optional[Literal["weight_norm", "spectral_norm"]] = None, **norm_kwargs
) -> Callable[[Union[nn.Module, Model]], Union[nn.Module, Model]]:
    if not norm_type:
        return _dummy
    if norm_type == "weight_norm":
        return lambda x: weight_norm(x, **norm_kwargs)
    return lambda x: spectral_norm(x, **norm_kwargs)


def remove_norm(module, name: str = "weight"):
    try:
        try:
            remove_parametrizations(module, name, leave_parametrized=False)
        except:
            # many times will fail with 'leave_parametrized'
            remove_parametrizations(module, name, leave_parametrized=True)
    except ValueError:
        pass  # not parametrized


def get_conv(
    in_channels: int = 1,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_3 = 1,
    stride: TP_SHAPE_3 = 1,
    padding: TP_SHAPE_3 = 0,
    output_padding: TP_SHAPE_3 = 0,
    dilation: TP_SHAPE_3 = 1,
    groups: TP_SHAPE_3 = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    dim: Literal["1d", "2d", "3d"] = "1d",
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[
    nn.Conv1d,
    nn.LazyConv1d,
    nn.ConvTranspose1d,
    nn.LazyConvTranspose1d,
    nn.Conv2d,
    nn.LazyConv2d,
    nn.ConvTranspose2d,
    nn.LazyConvTranspose2d,
    nn.Conv3d,
    nn.LazyConv3d,
    nn.ConvTranspose3d,
    nn.LazyConvTranspose3d,
    TC,
]:
    dim = dim.lower().strip()
    assert dim in [
        "1d",
        "2d",
        "3d",
    ], f"Invalid conv dim '{dim}'. It must be either '1d', '2d' or '3d'."
    if norm is not None:
        norm = norm.strip().lower()
        if norm and norm not in ["weight_norm", "spectral_norm"]:
            if norm == "weight":
                norm = "weight_norm"
            elif norm == "spectral":
                norm == "spectral_norm"
            elif norm == "none":
                norm = None
            else:
                raise ValueError(
                    f"Invalid norm '{norm}'. "
                    'It must be either "weight_norm" or "spectral_norm" or None.'
                )
    out_ch = out_channels if out_channels is not None else in_channels
    if groups > 1:
        groups = min(groups, math.gcd(in_channels, out_ch))
        if groups % in_channels != 0 or groups % out_ch != 0:
            groups = 1

    kwargs = dict(
        in_channels=max(in_channels, 1),
        out_channels=max(out_ch, 1),
        kernel_size=max(kernel_size, 1),
        padding=padding,
        stride=max(stride, 1),
        dilation=max(dilation, 1),
        bias=bias,
        groups=max(groups, 1),
        padding_mode=padding_mode,
        output_padding=output_padding,
    )

    match dim:
        case "1d":
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose1d
                else:
                    md = nn.ConvTranspose1d
            else:
                if lazy:
                    md = nn.LazyConv1d
                else:
                    md = nn.Conv1d
        case "2d":
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose2d
                else:
                    md = nn.ConvTranspose2d
            else:
                if lazy:
                    md = nn.LazyConv2d
                else:
                    md = nn.Conv2d
        case _:
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose3d
                else:
                    md = nn.ConvTranspose3d

            else:
                if lazy:
                    md = nn.LazyConv3d
                else:
                    md = nn.Conv3d

    kwargs = filter_kwargs(md, False, [], **kwargs)
    if norm:
        norm_fn = get_weight_norm(norm, **norm_kwargs)
        return norm_fn(md(**kwargs))
    return md(**kwargs)


def get_1d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: int = 1,
    stride: int = 1,
    padding: int = 0,
    output_padding: int = 0,
    dilation: int = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv1d, nn.ConvTranspose1d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="1d",
        lazy=lazy,
    )


def get_2d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_2 = 1,
    stride: TP_SHAPE_2 = 1,
    padding: TP_SHAPE_2 = 0,
    output_padding: TP_SHAPE_2 = 0,
    dilation: TP_SHAPE_2 = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv2d, nn.ConvTranspose2d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="2d",
        lazy=lazy,
    )


def get_3d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_3 = 1,
    stride: TP_SHAPE_3 = 1,
    padding: TP_SHAPE_3 = 0,
    output_padding: TP_SHAPE_3 = 0,
    dilation: TP_SHAPE_3 = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv3d, nn.ConvTranspose3d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="3d",
        lazy=lazy,
    )


class ConvBase(Model):

    @staticmethod
    def get_1d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        dilation: int = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
        lazy: bool = False,
    ) -> Union[nn.Conv1d, nn.ConvTranspose1d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="1d",
            lazy=lazy,
        )

    @staticmethod
    def get_2d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_2 = 1,
        stride: TP_SHAPE_2 = 1,
        padding: TP_SHAPE_2 = 0,
        output_padding: TP_SHAPE_2 = 0,
        dilation: TP_SHAPE_2 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ) -> Union[nn.Conv2d, nn.ConvTranspose2d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="2d",
        )

    @staticmethod
    def get_3d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_3 = 1,
        stride: TP_SHAPE_3 = 1,
        padding: TP_SHAPE_3 = 0,
        output_padding: TP_SHAPE_3 = 0,
        dilation: TP_SHAPE_3 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ) -> Union[nn.Conv3d, nn.ConvTranspose3d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="3d",
        )

    @staticmethod
    def get_max_groups(in_channels: int, out_channels: int):
        return calc_max_groups(in_channels, out_channels)

    @staticmethod
    def get_padding(kernel_size: int, dilation: int, mode: Literal["a", "b"] = "a"):
        if mode == "a":
            return get_padding_1d_a(kernel_size, dilation)
        return get_padding_1d_b(kernel_size, dilation)

    def remove_norms(self, name: str = "weight"):
        for module in self.modules():
            try:
                if is_conv(module):
                    remove_norm(module, name)
            except:
                pass

    @staticmethod
    def _normal_init_default(m: nn.Module, mean=0.0, std=0.01, zero_bias: bool = False):
        if is_conv(m):
            nn.init.normal_(m.weight, mean=mean, std=std)
            if zero_bias and m.bias is not None:
                nn.init.zeros_(m.bias)


class BidirectionalConv1d(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        padding: int = 0,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        output_padding: int = 0,
        bias_fwd: bool = True,
        bias_bwd: bool = True,
        transposed: bool = False,
        *,
        return_tuple: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
        apply_init: bool = False,
        init_biasses: bool = False,
        init_mean: float = 0.0,
        init_std: float = 0.1,
    ):
        super().__init__()
        padding = (kernel_size - 1) * dilation // 2
        self.fwd = self.get_1d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_fwd,
            dilation=dilation,
            padding=padding,
            stride=stride,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_fwd,
        )
        self.bwd = self.get_1d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_bwd,
            dilation=dilation,
            padding=padding,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_bwd,
        )
        self.return_tuple = return_tuple
        if apply_init:
            self.fwd.weight.data.normal_(mean=init_mean, std=init_std)
            self.bwd.weight.data.normal_(mean=init_mean, std=init_std)
            if init_biasses:
                if bias_fwd:
                    self.fwd.bias.data.zero_()
                if bias_bwd:
                    self.bwd.bias.data.zero_()

    def __call__(self, *args, **kwds) -> Union[Tuple[Tensor, Tensor], Tensor]:
        return super().__call__(*args, **kwds)

    def forward(self, x: Tensor) -> Union[Tuple[Tensor, Tensor], Tensor]:
        # forward path
        y_fwd = self.fwd(x)
        # backward path: flip time axis, convolve, flip back
        x_rev = self.bwd(x.flip(dims=[-1]))
        y_bwd = x_rev.flip(dims=[-1])
        if self.return_tuple:
            return y_fwd, y_bwd
        return torch.cat((y_fwd, y_bwd), dim=1)
