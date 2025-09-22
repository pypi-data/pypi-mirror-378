from lt_utils.common import *
from lt_tensor.common import *
import torch.nn.functional as F


TC: TypeAlias = Callable[[Any], Tensor]


class Conv1DGatedFusion(Model):
    def __init__(self, channels: int):
        super().__init__()
        # use sigmoid to get gating in [0,1]
        self.gate = nn.Conv1d(channels * 2, channels, 3, padding=1, bias=False)

    def forward(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        # a,b: (B, C, T)
        g = torch.sigmoid(self.gate(torch.cat([a, b], dim=1)))
        return g * a + (1.0 - g) * b


class FiLMConv1d(Model):
    def __init__(
        self,
        cond_channels: int,
        feat_channels: int,
        kernel_size: Union[int, Tuple[int, ...]] = 1,
        padding: Union[int, Tuple[int, ...]] = 0,
        bias: bool = True,
        interp_match: bool = False,
    ):
        super().__init__()
        self.interp_match = interp_match
        self.modulator = nn.Conv1d(
            cond_channels,
            2 * feat_channels,
            kernel_size=kernel_size,
            padding=padding,
            bias=bias,
        )

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        # x: [B, C, T]
        gamma, beta = torch.chunk(self.modulator(cond), 2, dim=-2)
        if self.interp_match:
            if gamma.size(-1) != x.size(-1):
                gamma = F.interpolate(
                    gamma,
                    size=x.size(-1),
                    mode="linear",
                )
                beta = F.interpolate(
                    beta,
                    size=x.size(-1),
                    mode="linear",
                )
        return x * gamma + beta


class FiLMConv2d(Model):
    def __init__(
        self,
        cond_channels: int,
        feat_channels: int,
        kernel_size: Union[int, Tuple[int, ...]] = 1,
        padding: Union[int, Tuple[int, ...]] = 0,
        bias: bool = True,
        interp_match: bool = False,
    ):
        super().__init__()
        self.interp_match = interp_match
        self.cond_dim = cond_channels
        self.feature_dim = feat_channels
        self.modulator = nn.Conv2d(
            cond_channels,
            2 * feat_channels,
            kernel_size=kernel_size,
            padding=padding,
            bias=bias,
        )

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        gamma, beta = torch.chunk(self.modulator(cond), 2, dim=-3)
        if self.interp_match:
            if gamma.shape[-2:] != x.shape[-2:]:
                gamma = F.interpolate(
                    gamma,
                    size=x.shape[-2:],
                    mode="bilinear",
                )
                beta = F.interpolate(
                    beta,
                    size=x.shape[-2:],
                    mode="bilinear",
                )
        return x * gamma + beta


class FiLMAlphaFusion(Model):
    def __init__(
        self,
        cond_dim: int,
        feature_dim: int,
        alpha: float = 1.0,
        base: float = 1.0,
        train_alpha: bool = True,
        train_base: bool = False,
        bias: bool = True,
    ):
        """...

        Args:
            cond_dim (int): Dimension of the conditional
            feature_dim (int): Feature/input size, that will be modulated into.
            alpha (float, optional): 'Strength' that the modulation (condition) will be applied towards the feature, it must be a non-zero value (includes negative values). Defaults to 1.0.
            base (float, optional): Base value that will be summed with module, to avoid a fading effect. Defaults to 1.0.
            train_alpha (bool, optional): While True this makes the parameter alpha trainable. Defaults to True.
            train_base (bool, optional): If True this makes the base value trainable. Defaults to False.
            bias (bool, optional): Bias of the modulator. Defaults to True.
        """
        super().__init__()
        assert (
            alpha != 0.0
        ), "Alpha cannot be zero, use either a positive or negative value to define this"
        self.train_alpha = train_alpha
        self.train_base = train_base
        self.alpha = nn.Parameter(
            torch.tensor(alpha, dtype=torch.float32), requires_grad=train_alpha
        )
        self.base = nn.Parameter(
            torch.tensor(base, dtype=torch.float32), requires_grad=train_base
        )
        self.modulator = nn.Linear(cond_dim, 2 * feature_dim, bias=bias)
        self.bias = bias

        if self.bias:
            nn.init.zeros_(self.modulator.bias)

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        beta, gamma = self.modulator(cond).chunk(2, dim=-1)
        module = (beta + gamma) * self.alpha
        return x * (self.base + module)


class SnakeFusion(Model):
    def __init__(
        self,
        cond_dim: int,
        feature_dim: int,
        alpha: float = 1.0,
        train_alpha: bool = False,
    ):
        super().__init__()
        self.modulator = nn.Linear(cond_dim, int(4 * feature_dim))
        self.update = nn.Linear(feature_dim, feature_dim)
        self.proj = nn.Linear(feature_dim, feature_dim)
        self.alpha = nn.Parameter(
            torch.tensor(alpha, dtype=torch.float32), requires_grad=train_alpha
        )

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        beta, gamma, lt, ch = self.modulator(cond).chunk(4, dim=-1)
        xc = x * beta
        xc = self.update(xc) * (lt.sin() * ch.cos()) + gamma
        return x + (self.proj(xc) * self.alpha)


class GatedFusion(Model):
    def __init__(self, in_dim: int):
        super().__init__()
        self.gate = nn.Linear(in_dim * 2, in_dim)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        gate = self.gate(torch.cat([a, b], dim=-1)).sigmoid()
        return gate * a + (1 - gate) * b


class AdaFusion(Model):
    def __init__(
        self,
        cond_size: int,
        num_features: int,
        alpha: float = 1.0,
        train_alpha: bool = True,
    ):
        super().__init__()
        self.fc = nn.Linear(cond_size, num_features * 2)
        self.norm = nn.InstanceNorm1d(num_features, affine=False)
        self.alpha = nn.Parameter(
            torch.tensor(alpha, dtype=torch.float32), requires_grad=train_alpha
        )

    def forward(
        self,
        inp: Tensor,
        cond: Tensor,
        alpha: Optional[Tensor] = None,
    ):
        h = self.fc(cond)
        h = h.view(h.size(0), h.size(-1), 1)
        gamma, beta = torch.chunk(h, chunks=2, dim=1)
        t = (1.0 + gamma) * self.norm(inp) + beta
        if alpha is not None:
            return t + (1 / alpha) * (torch.sin(alpha * t) ** 2)
        return t + (1 / self.alpha) * (torch.sin(self.alpha * t) ** 2)


class AdaIN(Model):
    def __init__(
        self,
        inp_dim: int,
        cond_dim: int,
        alpha: float = 1.0,
        eps: float = 1e-5,
        train_alpha: bool = False,
    ):
        """
        inp_dim: size of the input
        cond_dim: size of the conditioning
        """
        super().__init__()
        self.proj_expd = nn.Linear(cond_dim, inp_dim * 2)
        self.proj_out = nn.Linear(inp_dim, inp_dim)
        self.eps = eps
        self.alpha = nn.Parameter(
            torch.tensor(alpha, dtype=torch.float32), requires_grad=train_alpha
        )

    def forward(self, x: Tensor, cond: Tensor):
        # x_norm = [B, C, T]
        x_norm = (x - x.mean(dim=-1, keepdim=True)) / (
            x.std(dim=-1, keepdim=True) + self.eps
        )

        # Conditioning
        gamma_beta = self.proj_expd(cond)  # [B, 2*C]
        gamma, beta = gamma_beta.chunk(2, dim=-1)
        xt = self.proj_out((gamma * x_norm + beta))
        return x + (xt * self.alpha)


class InterFusion(Model):
    def __init__(
        self,
        d_model: int,
        cond_channels: int = 1,
        features_channels: int = 1,
        alpha: float = 1.0,
        mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
            "area",
        ] = "nearest",
        split_dim: int = -1,
        inner_activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()
        assert d_model % 4 == 0
        if cond_channels != features_channels:
            self.proj_fn = nn.Conv1d(cond_channels, features_channels, kernel_size=1)
        else:
            self.proj_fn = nn.Identity()

        self.d_model = d_model
        self.quarter_size = d_model // 4
        self.alpha = alpha if alpha else 1.0
        self.split_dim = split_dim

        self.fc_list = nn.ModuleList(
            [
                nn.Sequential(
                    inner_activation,
                    nn.Linear(self.quarter_size, self.d_model),
                )
                for _ in range(4)
            ]
        )

        self.d_model = d_model
        self.mode = mode
        self.inter = lambda x: F.interpolate(x, size=self.d_model, mode=self.mode)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        xt = torch.zeros_like(a, device=a.device)
        resized = self.inter(b).split(self.quarter_size, dim=self.split_dim)
        for i, fc in enumerate(self.fc_list):
            xt = xt + fc(resized[i])
        return a + self.proj_fn(xt * self.alpha).view_as(a)
