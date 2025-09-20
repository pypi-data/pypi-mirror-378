from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import choose_device, seed_all


class MaskedLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, sparsity: float = 0.8, random_state: Optional[int] = None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        rs = torch.Generator()
        if random_state is not None:
            rs.manual_seed(int(random_state))
        # mask==1 keeps connection; expected density = 1 - sparsity
        density = max(0.0, min(1.0, 1.0 - float(sparsity)))
        mask = (torch.rand((out_features, in_features), generator=rs) < density).float()
        self.register_buffer("mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.linear.weight * self.mask
        return F.linear(x, w, self.linear.bias)


class LSM(nn.Module):
    """Liquid State Machine-inspired expander (feed-forward, sparse layers).

    Expands input features to a higher-dimensional representation using sparse
    masked linear layers and a configurable nonlinearity.

    Parameters
    - input_dim: int — number of input features (D)
    - output_dim: int — number of output features (K)
    - hidden_layers: int — number of hidden MaskedLinear layers
    - hidden_units: int -- width of each hidden layer (alias hidden_width)
    - sparsity: float in [0,1] — expected fraction of zeroed connections
    - nonlinearity: 'sine' | 'tanh' | 'relu'
    - bias: include bias terms
    - random_state: optional seed for mask sampling

    Shapes
    - forward(X): (N, D) -> (N, K)
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_units: Optional[int] = None,
        hidden_width: Optional[int] = 128,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        bias: bool = True,
        random_state: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.output_dim = int(output_dim)
        if hidden_units is not None and hidden_width is not None and int(hidden_units) != int(hidden_width):
            raise ValueError("hidden_units and hidden_width must agree when both provided")
        width_val = hidden_units if hidden_units is not None else hidden_width
        if width_val is None:
            width_val = 128
        width = int(width_val)
        self.hidden_layers = int(hidden_layers)
        self.hidden_units = width
        self.hidden_width = width
        self.sparsity = float(sparsity)
        self.nonlinearity = nonlinearity

        act = {
            "sine": torch.sin,
            "tanh": torch.tanh,
            "relu": F.relu,
        }.get(nonlinearity)
        if act is None:
            raise ValueError("nonlinearity must be one of: sine, tanh, relu")
        self._act = act

        layers = []
        in_dim = self.input_dim
        for i in range(self.hidden_layers):
            layers.append(MaskedLinear(in_dim, self.hidden_width, bias=bias, sparsity=self.sparsity, random_state=None if random_state is None else random_state + i))
            in_dim = self.hidden_width
        self.body = nn.Sequential(*layers)
        self.head = MaskedLinear(in_dim, self.output_dim, bias=bias, sparsity=self.sparsity, random_state=None if random_state is None else random_state + 999)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, input_dim)
        z = x
        for layer in self.body:
            z = self._act(layer(z))
        z = self.head(z)
        return z


class LSMExpander:
    """Pretraining interface for :class:`LSM` with an OLS-in-the-loop objective.

    Objective: learn LSM parameters such that a ridge/OLS readout from the
    expanded features can reconstruct inputs with high R^2 (or low MSE).

    Usage
    - fit(X): trains the internal :class:`LSM` on X; stores `.model` and `.W_`.
    - transform(X): returns expanded features via `.model`.
    - score_reconstruction(X): computes OLS reconstruction R^2 on X.
    """

    def __init__(
        self,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_units: Optional[int] = None,
        hidden_width: Optional[int] = 128,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        epochs: int = 100,
        lr: float = 1e-3,
        ridge: float = 1e-4,
        batch_size: int = 256,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
        early_stopping: bool = False,
        patience: int = 20,
        tol: float = 1e-6,
        val_split: Optional[float] = None,
        verbose: int = 0,
        objective: str = "r2",  # 'r2' or 'mse'
        alpha_ortho: float = 0.0,
        alpha_sparse: float = 0.0,
        alpha_var: float = 0.0,
        target_var: float = 1.0,
        noisy: Optional[float] = None,
        noise_decay: float = 1.0,
    ) -> None:
        self.output_dim = int(output_dim)
        if hidden_units is not None and hidden_width is not None and int(hidden_units) != int(hidden_width):
            raise ValueError("hidden_units and hidden_width must agree when both provided")
        width_val = hidden_units if hidden_units is not None else hidden_width
        if width_val is None:
            width_val = 128
        width = int(width_val)
        self.hidden_layers = int(hidden_layers)
        self.hidden_units = width
        self.hidden_width = width
        self.sparsity = sparsity
        self.nonlinearity = nonlinearity
        self.epochs = epochs
        self.lr = lr
        self.ridge = ridge
        self.batch_size = batch_size
        self.device = device
        self.random_state = random_state
        self.early_stopping = early_stopping
        self.patience = patience
        self.tol = tol
        self.val_split = val_split
        self.verbose = verbose
        self.objective = objective
        self.alpha_ortho = float(alpha_ortho)
        self.alpha_sparse = float(alpha_sparse)
        self.alpha_var = float(alpha_var)
        self.target_var = float(target_var)
        self.noisy = noisy
        self.noise_decay = float(noise_decay)

        self.model: Optional[LSM] = None
        self.W_: Optional[torch.Tensor] = None  # OLS readout (output_dim -> input_dim)

    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _ols_readout(self, Z: torch.Tensor, X: torch.Tensor, ridge: float) -> torch.Tensor:
        # Add bias term
        ones = torch.ones((Z.shape[0], 1), dtype=Z.dtype, device=Z.device)
        Zb = torch.cat([Z, ones], dim=1)
        A = Zb.T @ Zb
        b = Zb.T @ X
        I = torch.eye(A.shape[0], dtype=A.dtype, device=A.device)
        # Try ridge solve with adaptive damping; fall back to lstsq/pinv if necessary
        lam = float(ridge if ridge is not None else 0.0)
        lam = lam if lam > 0 else 1e-8
        W = None
        last_err = None
        for k in range(6):  # up to 1e2 increase
            try:
                W = torch.linalg.solve(A + lam * I, b)
                break
            except Exception as e:
                last_err = e
                lam *= 10.0
        if W is None:
            try:
                # Least squares without explicit ridge
                W = torch.linalg.lstsq(Zb, X, rcond=None).solution
            except Exception:
                # Pseudoinverse as last resort
                Zpinv = torch.linalg.pinv(Zb)
                W = Zpinv @ X
        return W

    def fit(
        self,
        X: np.ndarray,
        epochs: Optional[int] = None,
        *,
        validation_data: Optional[np.ndarray] = None,
        val_split: Optional[float] = None,
        early_stopping: Optional[bool] = None,
        patience: Optional[int] = None,
        tol: Optional[float] = None,
        verbose: Optional[int] = None,
    ) -> "LSMExpander":
        seed_all(self.random_state)
        X = np.asarray(X, dtype=np.float32)
        n_features = X.shape[1]
        device = self._device()
        self.model = LSM(n_features, self.output_dim, hidden_layers=self.hidden_layers, hidden_width=self.hidden_width, sparsity=self.sparsity, nonlinearity=self.nonlinearity, random_state=self.random_state).to(device)
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        # Resolve control params
        es = self.early_stopping if early_stopping is None else bool(early_stopping)
        pat = int(self.patience if patience is None else patience)
        tolerance = float(self.tol if tol is None else tol)
        verb = int(self.verbose if verbose is None else verbose)
        vs = self.val_split if val_split is None else val_split
        E = int(epochs) if epochs is not None else (10000 if es else self.epochs)

        # Train/val split
        if validation_data is not None:
            X_tr = X
            X_va = np.asarray(validation_data, dtype=np.float32)
        elif vs is not None or es:
            frac = 0.1 if vs is None else float(vs)
            frac = min(max(frac, 0.0), 0.9)
            n = X.shape[0]
            n_val = max(1, int(n * frac))
            rs = np.random.RandomState(self.random_state)
            idx = np.arange(n)
            rs.shuffle(idx)
            va_idx = idx[:n_val]
            tr_idx = idx[n_val:]
            X_tr = X[tr_idx]
            X_va = X[va_idx]
        else:
            X_tr = X
            X_va = None

        X_tr_t = torch.from_numpy(X_tr).to(device)
        X_va_t = torch.from_numpy(X_va).to(device) if X_va is not None else None

        # Prepare noise std tensor if requested
        noise_std_t: Optional[torch.Tensor] = None
        if self.noisy is not None and float(self.noise_decay) >= 0.0:
            if np.isscalar(self.noisy):
                std = np.full((1, X_tr.shape[1]), float(self.noisy), dtype=np.float32)
            else:
                arr = np.asarray(self.noisy, dtype=np.float32).reshape(1, -1)
                if arr.shape[1] != X_tr.shape[1]:
                    raise ValueError(f"noisy has {arr.shape[1]} features, expected {X_tr.shape[1]}")
                std = arr
            noise_std_t = torch.from_numpy(std).to(device)

        best_r2 = -float("inf")
        best_state = None
        patience_left = pat

        # Full-batch optimization of LSM with OLS-in-the-loop readout
        for epoch in range(E):
            self.model.train()
            opt.zero_grad()
            # Optional Gaussian noise (decayed over epochs) applied to inputs
            if noise_std_t is not None:
                factor = float(max(self.noise_decay, 0.0) ** epoch)
                X_in = X_tr_t + torch.randn_like(X_tr_t) * (noise_std_t * factor)
            else:
                X_in = X_tr_t
            Z_tr = self.model(X_in)
            W = self._ols_readout(Z_tr, X_tr_t, ridge=self.ridge)
            ones_tr = torch.ones((Z_tr.shape[0], 1), dtype=Z_tr.dtype, device=Z_tr.device)
            Zb_tr = torch.cat([Z_tr, ones_tr], dim=1)
            X_hat_tr = Zb_tr @ W
            # Base loss
            if self.objective == "mse":
                base = F.mse_loss(X_hat_tr, X_tr_t)
            else:  # 'r2'
                ss_res_tr = ((X_tr_t - X_hat_tr) ** 2).sum()
                ss_tot_tr = ((X_tr_t - X_tr_t.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
                base = ss_res_tr / ss_tot_tr
            # Regularizers on Z
            reg = 0.0
            if self.alpha_ortho > 0.0:
                Zc = Z_tr - Z_tr.mean(dim=0, keepdim=True)
                Cz = (Zc.T @ Zc) / max(1, Z_tr.shape[0] - 1)
                offdiag = Cz - torch.diag(torch.diag(Cz))
                reg = reg + self.alpha_ortho * (offdiag.pow(2).sum() / (Z_tr.shape[1] ** 2))
            if self.alpha_sparse > 0.0:
                reg = reg + self.alpha_sparse * Z_tr.abs().mean()
            if self.alpha_var > 0.0:
                var = Z_tr.var(dim=0, unbiased=False)
                reg = reg + self.alpha_var * ((var - self.target_var) ** 2).mean()
            loss = base + reg
            loss.backward()
            opt.step()

            # Validation R^2 using same W
            if X_va_t is not None:
                self.model.eval()
                with torch.no_grad():
                    Z_va = self.model(X_va_t)
                    ones_va = torch.ones((Z_va.shape[0], 1), dtype=Z_va.dtype, device=Z_va.device)
                    Zb_va = torch.cat([Z_va, ones_va], dim=1)
                    X_hat_va = Zb_va @ W
                    ss_res_va = ((X_va_t - X_hat_va) ** 2).sum()
                    ss_tot_va = ((X_va_t - X_va_t.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
                    r2_va = float(1.0 - (ss_res_va / ss_tot_va))
                if verb:
                    print(f"LSMExpander epoch {epoch+1}/{E} - val R^2: {r2_va:.6f}")
                if r2_va > best_r2 + tolerance:
                    best_r2 = r2_va
                    best_state = {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}
                    patience_left = pat
                else:
                    patience_left -= 1
                    if es and patience_left <= 0:
                        if verb:
                            print(f"Early stopping LSM at epoch {epoch+1} (best R^2: {best_r2:.6f})")
                        break

        # Restore best state if available
        if best_state is not None:
            self.model.load_state_dict(best_state)
        self.model.eval()
        with torch.no_grad():
            X_all_t = torch.from_numpy(X).to(device)
            Z_all = self.model(X_all_t)
            self.W_ = self._ols_readout(Z_all, X_all_t, ridge=self.ridge).detach().cpu()
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSMExpander not fitted; call fit() first or set .model externally.")
        X = np.asarray(X, dtype=np.float32)
        device = next(self.model.parameters()).device
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(device)).cpu().numpy()
        return Z

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def score_reconstruction(self, X: np.ndarray) -> float:
        if self.model is None or self.W_ is None:
            raise RuntimeError("LSMExpander not fitted")
        X = np.asarray(X, dtype=np.float32)
        device = next(self.model.parameters()).device
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(device))
            ones = torch.ones((Z.shape[0], 1), dtype=Z.dtype, device=Z.device)
            Zb = torch.cat([Z, ones], dim=1)
            X_hat = Zb @ self.W_.to(device)
            ss_res = ((torch.from_numpy(X).to(device) - X_hat) ** 2).sum()
            ss_tot = ((torch.from_numpy(X).to(device) - torch.from_numpy(X).to(device).mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
            r2 = 1.0 - float(ss_res.cpu() / ss_tot.cpu())
        return r2


# ----------------------------- Conv2d Variant -----------------------------

class MaskedConv2d(nn.Conv2d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 1, bias: bool = True, sparsity: float = 0.8, random_state: Optional[int] = None):
        super().__init__(in_channels, out_channels, kernel_size=kernel_size, padding=0, bias=bias)
        rs = torch.Generator()
        if random_state is not None:
            rs.manual_seed(int(random_state))
        k = self.kernel_size[0] * self.kernel_size[1]
        density = max(0.0, min(1.0, 1.0 - float(sparsity)))
        mask = (torch.rand((out_channels, in_channels, self.kernel_size[0], self.kernel_size[1]), generator=rs) < density).float()
        self.register_buffer("mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.weight * self.mask
        return F.conv2d(x, w, self.bias, stride=self.stride, padding=self.padding, dilation=self.dilation, groups=self.groups)


class LSMConv2d(nn.Module):
    """Conv2d expander using masked convolutions with configurable nonlinearity.

    Expands channels while preserving spatial dimensions.

    Parameters
    - in_channels: int — input channels (C_in)
    - out_channels: int — output channels (C_out)
    - hidden_layers: int — number of masked conv blocks
    - conv_channels: int -- channels per hidden block (alias hidden_channels)
    - kernel_size: int — kernel size for masked convs
    - sparsity: float in [0,1] — expected fraction of zeroed connections
    - nonlinearity: 'sine' | 'tanh' | 'relu'
    - bias: bool
    - random_state: optional seed for masks

    Shapes
    - forward(X): (N, C_in, H, W) -> (N, C_out, H, W)
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        hidden_layers: int = 1,
        conv_channels: Optional[int] = None,
        hidden_channels: Optional[int] = 128,
        kernel_size: int = 1,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        bias: bool = True,
        random_state: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        if conv_channels is not None and hidden_channels is not None and int(conv_channels) != int(hidden_channels):
            raise ValueError("conv_channels and hidden_channels must agree when both provided")
        channels_val = conv_channels if conv_channels is not None else hidden_channels
        if channels_val is None:
            channels_val = 128
        channels = int(channels_val)
        hidden_channels = channels
        self.hidden_layers = int(hidden_layers)
        self.conv_channels = channels
        self.hidden_channels = channels
        self.kernel_size = int(kernel_size)
        kernel_size = int(self.kernel_size)
        act = {
            "sine": torch.sin,
            "tanh": torch.tanh,
            "relu": F.relu,
        }.get(nonlinearity)
        if act is None:
            raise ValueError("nonlinearity must be one of: sine, tanh, relu")
        self._act = act

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            layers.append(MaskedConv2d(c, hidden_channels, kernel_size=kernel_size, bias=bias, sparsity=sparsity, random_state=None if random_state is None else random_state + i))
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.head = MaskedConv2d(c, out_channels, kernel_size=kernel_size, bias=bias, sparsity=sparsity, random_state=None if random_state is None else random_state + 777)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = x
        for layer in self.body:
            z = self._act(layer(z))
        z = self.head(z)
        return z


class LSMConv2dExpander:
    """Pretraining interface for :class:`LSMConv2d` with OLS per-pixel objective.

    Treats the readout as a 1×1 convolution (per-pixel linear map) learned in
    closed form via ridge-OLS over flattened `(N*H*W, C)` samples.
    """

    def __init__(
        self,
        out_channels: int,
        *,
        hidden_layers: int = 1,
        conv_channels: Optional[int] = None,
        hidden_channels: Optional[int] = 128,
        kernel_size: int = 1,
        sparsity: float = 0.8,
        nonlinearity: str = "sine",
        epochs: int = 50,
        lr: float = 1e-3,
        ridge: float = 1e-4,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
        noisy: Optional[float] = None,
        noise_decay: float = 1.0,
        alpha_ortho: float = 0.0,
        alpha_sparse: float = 0.0,
        alpha_var: float = 0.0,
        target_var: float = 1.0,
    ) -> None:
        self.out_channels = int(out_channels)
        if conv_channels is not None and hidden_channels is not None and int(conv_channels) != int(hidden_channels):
            raise ValueError("conv_channels and hidden_channels must agree when both provided")
        channels_val = conv_channels if conv_channels is not None else hidden_channels
        if channels_val is None:
            channels_val = 128
        channels = int(channels_val)
        self.hidden_layers = int(hidden_layers)
        self.conv_channels = channels
        self.hidden_channels = channels
        self.kernel_size = int(kernel_size)
        kernel_size = int(self.kernel_size)
        self.sparsity = sparsity
        self.nonlinearity = nonlinearity
        self.epochs = epochs
        self.lr = lr
        self.ridge = ridge
        self.device = device
        self.random_state = random_state
        self.model: Optional[LSMConv2d] = None
        self.W_: Optional[torch.Tensor] = None  # (C_out+1, C_in)
        self.noisy = noisy
        self.noise_decay = float(noise_decay)
        self.alpha_ortho = float(alpha_ortho)
        self.alpha_sparse = float(alpha_sparse)
        self.alpha_var = float(alpha_var)
        self.target_var = float(target_var)

    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _ols_readout(self, Z: torch.Tensor, X: torch.Tensor, ridge: float) -> torch.Tensor:
        # Z: (N, C_out, H, W) -> (N*H*W, C_out)
        N, C_out, H, W = Z.shape
        Zf = Z.permute(0, 2, 3, 1).reshape(-1, C_out)
        Cin = X.shape[1]
        ones = torch.ones((Zf.shape[0], 1), dtype=Z.dtype, device=Z.device)
        Zb = torch.cat([Zf, ones], dim=1)
        A = Zb.T @ Zb
        Xf = X.permute(0, 2, 3, 1).reshape(-1, Cin)
        b = Zb.T @ Xf
        I = torch.eye(A.shape[0], dtype=A.dtype, device=A.device)
        lam = float(ridge if ridge is not None else 0.0)
        lam = lam if lam > 0 else 1e-8
        W = None
        for k in range(6):
            try:
                W = torch.linalg.solve(A + lam * I, b)
                break
            except Exception:
                lam *= 10.0
        if W is None:
            try:
                W = torch.linalg.lstsq(Zb, Xf, rcond=None).solution
            except Exception:
                Zpinv = torch.linalg.pinv(Zb)
                W = Zpinv @ Xf
        return W

    def fit(self, X: np.ndarray, epochs: Optional[int] = None) -> "LSMConv2dExpander":
        seed_all(self.random_state)
        X = np.asarray(X, dtype=np.float32)
        assert X.ndim == 4, "Expected channels-first (N, C, H, W) input"
        N, Cin, H, W = X.shape
        device = self._device()
        self.model = LSMConv2d(Cin, self.out_channels, hidden_layers=self.hidden_layers, hidden_channels=self.hidden_channels, kernel_size=self.kernel_size, sparsity=self.sparsity, nonlinearity=self.nonlinearity, random_state=self.random_state).to(device)
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        E = int(epochs) if epochs is not None else self.epochs
        X_t = torch.from_numpy(X).to(device)
        # Prepare noise std per-channel if requested
        noise_std_t: Optional[torch.Tensor] = None
        if self.noisy is not None and float(self.noise_decay) >= 0.0:
            if np.isscalar(self.noisy):
                std = np.full((1, Cin, 1, 1), float(self.noisy), dtype=np.float32)
            else:
                arr = np.asarray(self.noisy, dtype=np.float32)
                if arr.ndim == 1 and arr.shape[0] == Cin:
                    std = arr.reshape(1, Cin, 1, 1)
                elif arr.shape == (Cin, 1, 1):
                    std = arr.reshape(1, Cin, 1, 1)
                else:
                    raise ValueError(f"noisy shape {arr.shape} incompatible with channels={Cin}")
            noise_std_t = torch.from_numpy(std).to(device)
        for _ in range(E):
            self.model.train()
            opt.zero_grad()
            # Apply decayed input noise each epoch
            if noise_std_t is not None:
                factor = float(max(self.noise_decay, 0.0) ** _)
                X_in = X_t + torch.randn_like(X_t) * (noise_std_t * factor)
            else:
                X_in = X_t
            Z = self.model(X_in)
            W = self._ols_readout(Z, X_t, ridge=self.ridge)
            # Reconstruct with 1x1 conv via channel-wise linear map
            Zf = Z.permute(0, 2, 3, 1).reshape(-1, Z.shape[1])
            ones = torch.ones((Zf.shape[0], 1), dtype=Z.dtype, device=Z.device)
            Zbf = torch.cat([Zf, ones], dim=1)
            Xf_hat = Zbf @ W
            Xf = X_t.permute(0, 2, 3, 1).reshape(-1, Cin)
            ss_res = ((Xf - Xf_hat) ** 2).sum()
            ss_tot = ((Xf - Xf.mean(dim=0, keepdim=True)) ** 2).sum().clamp_min(1e-8)
            base = ss_res / ss_tot
            # Regularizers on Z features (flattened over spatial/batch)
            reg = 0.0
            if self.alpha_ortho > 0.0:
                Zc = Zf - Zf.mean(dim=0, keepdim=True)
                Cz = (Zc.T @ Zc) / max(1, Zf.shape[0] - 1)
                offdiag = Cz - torch.diag(torch.diag(Cz))
                reg = reg + self.alpha_ortho * (offdiag.pow(2).sum() / (Zf.shape[1] ** 2))
            if self.alpha_sparse > 0.0:
                reg = reg + self.alpha_sparse * Zf.abs().mean()
            if self.alpha_var > 0.0:
                var = Zf.var(dim=0, unbiased=False)
                reg = reg + self.alpha_var * ((var - self.target_var) ** 2).mean()
            loss = base + reg
            loss.backward()
            opt.step()

        # Store final readout
        self.model.eval()
        with torch.no_grad():
            Z = self.model(X_t)
            self.W_ = self._ols_readout(Z, X_t, ridge=self.ridge).detach().cpu()
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LSMConv2dExpander not fitted")
        X = np.asarray(X, dtype=np.float32)
        with torch.no_grad():
            Z = self.model(torch.from_numpy(X).to(self._device())).cpu().numpy()
        return Z

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
