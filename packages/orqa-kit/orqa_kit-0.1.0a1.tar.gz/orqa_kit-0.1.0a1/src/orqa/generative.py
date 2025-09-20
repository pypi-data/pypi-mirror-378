# generative.py
"""
Generative family (dual-mode: classical | quantum-inspired)

Goal
----
Provide a portable, dependency-light generative module that you can swap later
for full Torch/QML implementations without changing orchestration.

Standardized behavior
---------------------
- fit(X) trains a generator on tabular (or tabularized) data.
- sample(n) returns n synthetic rows (np.ndarray).
- predict(X) returns optional {"aug_stats": ...} used by the integrator if configured:
    {
      "aug_stats": {
          "recon_err": (N,1)  # if model has a notion of reconstruction
      }
    }

Classical (mode="classical")
----------------------------
model="copula" (default): Gaussian Copula tabular synthesizer.
model="vae"            : Tiny VAE (if torch available) else PCA autoencoder fallback.
model="timegan"        : Compact seq synthesizer (stub—requires torch; fallback error if unavailable).

Quantum (mode="quantum")  [portable approximations; swap for real QML later]
-------------------------
model="qcbm"           : Quantum Circuit Born Machine–like: learn a low-dim mixture in
                         PCA latent (categorical mixture + gaussian leaf), sample & decode.
model="hybrid_vae"     : VAE-like with a sinusoidal "quantum encoder" feature map in latent,
                         linear decoder; portable & differentiable without Q libs.

Metrics
-------
score(X_real) → {"KS_mean": ..., "MMD_rbf": ...}  # quick fidelity proxies
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import numpy as np
from scipy import stats as st
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import rbf_kernel

# Try optional torch for the VAE/time models
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False


# -----------------------
# Utility helpers
# -----------------------

def _to_numpy(X) -> np.ndarray:
    if hasattr(X, "to_numpy"):
        return X.to_numpy()
    return np.asarray(X)

def _standardize(X: np.ndarray):
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True) + 1e-9
    Z = (X - mu) / sd
    return Z, mu, sd

def _destandardize(Z: np.ndarray, mu: np.ndarray, sd: np.ndarray):
    return Z * sd + mu

def _ks_mean(X: np.ndarray, Y: np.ndarray) -> float:
    vals = []
    for j in range(min(X.shape[1], Y.shape[1])):
        try:
            vals.append(st.ks_2samp(X[:, j], Y[:, j]).statistic)
        except Exception:
            pass
    return float(np.mean(vals)) if vals else float("nan")

def _mmd_rbf(X: np.ndarray, Y: np.ndarray, gamma: float = None) -> float:
    """Unbiased MMD^2 with RBF kernel as a rough distributional distance."""
    if gamma is None:
        # median heuristic on pooled pairwise distances
        Z = np.vstack([X[:512], Y[:512]])
        D2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
        med = np.median(D2)
        gamma = 1.0 / (2.0 * max(med, 1e-9))
    Kxx = rbf_kernel(X, X, gamma=gamma)
    Kyy = rbf_kernel(Y, Y, gamma=gamma)
    Kxy = rbf_kernel(X, Y, gamma=gamma)
    n = X.shape[0]; m = Y.shape[0]
    mmd2 = (Kxx.sum() - np.trace(Kxx)) / (n * (n - 1) + 1e-9) \
         + (Kyy.sum() - np.trace(Kyy)) / (m * (m - 1) + 1e-9) \
         - 2.0 * Kxy.mean()
    return float(max(mmd2, 0.0))


# -----------------------
# Classical models
# -----------------------

class _GaussianCopula:
    """Simple Gaussian Copula synthesizer (tabular)."""
    def __init__(self, params: Dict[str, Any]):
        self.params = params or {}
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None
        self.corr_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray):
        Z, mu, sd = _standardize(X)
        C = np.corrcoef(Z.T)
        C = np.nan_to_num(C, nan=0.0)
        self.mu_, self.sd_, self.corr_ = mu, sd, C
        return self

    def sample(self, n: int) -> np.ndarray:
        assert self.mu_ is not None and self.sd_ is not None and self.corr_ is not None
        d = self.corr_.shape[0]
        Z = np.random.multivariate_normal(mean=np.zeros(d), cov=self.corr_, size=n)
        return _destandardize(Z, self.mu_, self.sd_)

    def recon_error(self, X: np.ndarray) -> np.ndarray:
        # Copula has no recon; return zeros
        return np.zeros((X.shape[0], 1), dtype=float)


class _PCAAutoencoder:
    """
    Torch-free fallback approximating an autoencoder using PCA for encode/decode.
    """
    def __init__(self, params: Dict[str, Any]):
        self.k = int(params.get("latent_dim", 16))
        self.pca: Optional[PCA] = None
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray):
        Z, mu, sd = _standardize(X)
        self.mu_, self.sd_ = mu, sd
        self.pca = PCA(n_components=min(self.k, Z.shape[1]), random_state=42).fit(Z)
        return self

    def sample(self, n: int) -> np.ndarray:
        assert self.pca is not None and self.mu_ is not None and self.sd_ is not None
        # Sample latent ~ N(0, diag(explained_variance))
        d = self.pca.components_.shape[0]
        z = np.random.normal(size=(n, d)) * np.sqrt(self.pca.explained_variance_[:d])
        Z = z @ self.pca.components_
        return _destandardize(Z, self.mu_, self.sd_)

    def recon_error(self, X: np.ndarray) -> np.ndarray:
        assert self.pca is not None and self.mu_ is not None and self.sd_ is not None
        Z = (X - self.mu_) / self.sd_
        Zr = self.pca.inverse_transform(self.pca.transform(Z))
        err = ((Z - Zr) ** 2).mean(axis=1, keepdims=True)
        return err


class _TorchVAE(nn.Module):
    def __init__(self, d: int, latent: int = 16, hid: int = 64):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Linear(d, hid), nn.ReLU(),
            nn.Linear(hid, hid), nn.ReLU(),
        )
        self.mu = nn.Linear(hid, latent)
        self.logvar = nn.Linear(hid, latent)
        self.dec = nn.Sequential(
            nn.Linear(latent, hid), nn.ReLU(),
            nn.Linear(hid, hid), nn.ReLU(),
            nn.Linear(hid, d)
        )

    def forward(self, x):
        h = self.enc(x)
        mu, logvar = self.mu(h), self.logvar(h)
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        xr = self.dec(z)
        return xr, mu, logvar

class _VAEWrapper:
    """Tiny VAE wrapper (requires torch)."""
    def __init__(self, params: Dict[str, Any]):
        if not _HAS_TORCH:
            raise ImportError("Torch not available; use model='copula' or PCA fallback.")
        self.latent = int(params.get("latent_dim", 16))
        self.hid = int(params.get("hidden", 64))
        self.epochs = int(params.get("epochs", 10))
        self.lr = float(params.get("lr", 1e-3))
        self.batch = int(params.get("batch_size", 128))
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None
        self.model: Optional[_TorchVAE] = None
        self.d_: Optional[int] = None

    def fit(self, X: np.ndarray):
        Z, mu, sd = _standardize(X)
        self.mu_, self.sd_ = mu, sd
        d = Z.shape[1]
        self.d_ = d
        self.model = _TorchVAE(d=d, latent=self.latent, hid=self.hid)
        opt = optim.Adam(self.model.parameters(), lr=self.lr)

        Xten = torch.tensor(Z, dtype=torch.float32)
        ds = torch.utils.data.TensorDataset(Xten)
        dl = torch.utils.data.DataLoader(ds, batch_size=self.batch, shuffle=True)

        def loss_fn(xr, x, mu, logvar):
            recon = ((xr - x) ** 2).mean()
            kld = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
            return recon + 0.001 * kld

        self.model.train()
        for _ in range(max(1, self.epochs)):
            for (xb,) in dl:
                opt.zero_grad()
                xr, mu, logvar = self.model(xb)
                loss = loss_fn(xr, xb, mu, logvar)
                loss.backward()
                opt.step()
        return self

    def sample(self, n: int) -> np.ndarray:
        assert self.model is not None and self.mu_ is not None and self.sd_ is not None and self.d_ is not None
        self.model.eval()
        with torch.no_grad():
            z = torch.randn(n, self.model.mu.out_features)
            xr = self.model.dec(z).cpu().numpy()
        return _destandardize(xr, self.mu_, self.sd_)

    def recon_error(self, X: np.ndarray) -> np.ndarray:
        assert self.model is not None and self.mu_ is not None and self.sd_ is not None
        Z = (X - self.mu_) / self.sd_
        with torch.no_grad():
            xr, _, _ = self.model(torch.tensor(Z, dtype=torch.float32))
        err = ((xr.numpy() - Z) ** 2).mean(axis=1, keepdims=True)
        return err


# -----------------------
# Quantum-inspired models
# -----------------------

class _QCBMTabular:
    """
    Quantum Circuit Born Machine–like for tabular:
      - Standardize, then PCA to qcfg.n_qubits
      - Fit a small mixture over latent (categorical π, component means/diag std)
      - Sample component -> gaussian -> decode via inverse PCA → destandardize
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.seed = int(qcfg.get("seed", 42))
        self.K = int(params.get("n_components", max(2, self.n_qubits // 2)))
        self.pca: Optional[PCA] = None
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None
        self.mix_pi_: Optional[np.ndarray] = None
        self.comp_mu_: Optional[np.ndarray] = None
        self.comp_sd_: Optional[np.ndarray] = None
        np.random.seed(self.seed)

    def fit(self, X: np.ndarray):
        Z, mu, sd = _standardize(X)
        self.mu_, self.sd_ = mu, sd
        dlat = min(self.n_qubits, Z.shape[1])
        self.pca = PCA(n_components=dlat, random_state=self.seed).fit(Z)
        H = self.pca.transform(Z)  # (N,dlat)
        # Simple EM-like moment fit
        # Init by kmeans++-style sampling
        N, D = H.shape
        idx = np.random.choice(N, size=self.K, replace=False)
        self.comp_mu_ = H[idx]
        self.comp_sd_ = np.tile(H.std(axis=0, keepdims=True), (self.K, 1)) * 0.5 + 1e-3
        # Soft responsibilities by nearest center
        for _ in range(10):
            dist = ((H[:, None, :] - self.comp_mu_[None, :, :]) ** 2).sum(-1)  # (N,K)
            R = np.exp(-dist)
            R = R / (R.sum(axis=1, keepdims=True) + 1e-12)
            Nk = R.sum(axis=0, keepdims=True) + 1e-9
            self.comp_mu_ = (R.T @ H) / Nk.T
            var = (R.T @ ((H - self.comp_mu_[None, :, :]) ** 2)) / Nk.T
            self.comp_sd_ = np.sqrt(var + 1e-6)
        self.mix_pi_ = (R.sum(axis=0) / R.shape[0]).reshape(1, -1)
        return self

    def sample(self, n: int) -> np.ndarray:
        assert self.pca is not None and self.mu_ is not None and self.sd_ is not None
        assert self.mix_pi_ is not None and self.comp_mu_ is not None and self.comp_sd_ is not None
        comps = np.random.choice(self.K, size=n, p=self.mix_pi_.ravel())
        Hs = []
        for c in comps:
            mu = self.comp_mu_[c]
            sd = self.comp_sd_[c]
            Hs.append(np.random.normal(loc=mu, scale=sd))
        Hs = np.vstack(Hs)  # (n,D)
        Zs = self.pca.inverse_transform(Hs)
        return _destandardize(Zs, self.mu_, self.sd_)

    def recon_error(self, X: np.ndarray) -> np.ndarray:
        # Use distance to nearest component in latent as a proxy "energy"
        assert self.pca is not None
        H = self.pca.transform((X - self.mu_) / self.sd_)
        dist = ((H[:, None, :] - self.comp_mu_[None, :, :]) ** 2).sum(-1).min(axis=1, keepdims=True)
        return dist


class _HybridVAEPortable:
    """
    Hybrid VAE with a sinusoidal 'quantum' encoder:
      - Standardize
      - Encoder: PCA to n_qubits → sin/cos feature map (depth repeats)
      - Latent ~ N(0,I) around encoded mean (no learned variance in this portable version)
      - Decoder: linear least squares from latent to standardized features
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.depth = int(qcfg.get("max_depth", 2))
        self.alpha = float(params.get("alpha", 1.0))
        self.seed = int(qcfg.get("seed", 42))
        self.pca: Optional[PCA] = None
        self.W_dec_: Optional[np.ndarray] = None
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None
        np.random.seed(self.seed)

    def _encode(self, Z: np.ndarray, fit=False) -> np.ndarray:
        if self.pca is None or fit:
            self.pca = PCA(n_components=min(self.n_qubits, Z.shape[1]), random_state=self.seed).fit(Z)
        H = self.pca.transform(Z)
        feats = []
        for d in range(self.depth):
            a = self.alpha * (d + 1)
            feats.append(np.sin(a * H))
            feats.append(np.cos(a * H))
        return np.concatenate(feats, axis=1)  # latent features

    def fit(self, X: np.ndarray):
        Z, mu, sd = _standardize(X)
        self.mu_, self.sd_ = mu, sd
        Phi = self._encode(Z, fit=True)  # (N,L)
        # least-squares decoder: Phi * W ≈ Z  → W = (Phi^T Phi)^-1 Phi^T Z
        self.W_dec_ = np.linalg.pinv(Phi) @ Z
        return self

    def sample(self, n: int) -> np.ndarray:
        assert self.W_dec_ is not None and self.mu_ is not None and self.sd_ is not None and self.pca is not None
        # Sample latent around 0 with unit variance
        L = self.W_dec_.shape[0]
        Phi = np.random.normal(size=(n, L))
        Z = Phi @ self.W_dec_
        return _destandardize(Z, self.mu_, self.sd_)

    def recon_error(self, X: np.ndarray) -> np.ndarray:
        assert self.W_dec_ is not None and self.mu_ is not None and self.sd_ is not None and self.pca is not None
        Z = (X - self.mu_) / self.sd_
        Phi = self._encode(Z, fit=False)
        Zr = Phi @ self.W_dec_
        err = ((Z - Zr) ** 2).mean(axis=1, keepdims=True)
        return err


# -----------------------
# Public Family
# -----------------------

class GenerativeFamily:
    """
    FamilyModel for generation/augmentation with dual-mode operation.

    Args:
      params: dict of hyperparameters
      mode: "classical" | "quantum"
      qcfg: quantum spec dict or None

    Methods:
      fit(X)            -> metrics dict (optionally comparing self-sample to X)
      sample(n)         -> np.ndarray (n, d)
      predict(X)        -> {"aug_stats": {"recon_err": (N,1)}} when supported
      score(X_real)     -> {"KS_mean": ..., "MMD_rbf": ...}
      save/load         -> stubs
    """

    def __init__(self, params: Dict[str, Any], mode: str = "classical", qcfg: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.mode = mode
        self.qcfg = qcfg or {}
        self.model = None
        self.fitted = False

        if self.mode == "classical":
            name = self.params.get("model", "copula").lower()
            if name in ("copula", "gaussian_copula"):
                self.model = _GaussianCopula(self.params)
            elif name == "vae":
                if _HAS_TORCH:
                    self.model = _VAEWrapper(self.params)
                else:
                    # portable PCA "autoencoder" fallback
                    self.model = _PCAAutoencoder(self.params)
            elif name == "timegan":
                if not _HAS_TORCH:
                    raise ImportError("TimeGAN requires torch; install torch or choose another model.")
                # For brevity, not implementing full TimeGAN here.
                raise NotImplementedError("Compact TimeGAN not included in portable build.")
            else:
                self.model = _GaussianCopula(self.params)
        else:
            name = self.params.get("model", "qcbm").lower()
            if name in ("qcbm",):
                self.model = _QCBMTabular(self.params, self.qcfg)
            elif name in ("hybrid_vae", "qvae"):
                self.model = _HybridVAEPortable(self.params, self.qcfg)
            else:
                self.model = _QCBMTabular(self.params, self.qcfg)

        # placeholders for scaling stats if needed by predict
        self.mu_: Optional[np.ndarray] = None
        self.sd_: Optional[np.ndarray] = None

    # -------- core API --------

    def fit(self, X, y=None, cv=None) -> Dict[str, Any]:
        Xn = _to_numpy(X)
        self.model.fit(Xn)
        self.fitted = True
        # quick fidelity proxy: compare self-samples to train
        n = min(1024, Xn.shape[0])
        Xf = self.model.sample(n)
        return {
            "KS_mean": _ks_mean(Xn[:n], Xf[:n]),
            "MMD_rbf": _mmd_rbf(Xn[:n], Xf[:n]),
        }

    def sample(self, n: int) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("GenerativeFamily not fitted yet.")
        return self.model.sample(n)

    def predict(self, X) -> Dict[str, np.ndarray]:
        """
        For stacking, we optionally expose reconstruction error as aug_stats.
        If the model doesn't have a notion of recon, we omit aug_stats.
        """
        if not self.fitted:
            raise RuntimeError("GenerativeFamily not fitted yet.")
        Xn = _to_numpy(X)
        out: Dict[str, np.ndarray] = {}
        if hasattr(self.model, "recon_error"):
            out["aug_stats"] = np.asarray(self.model.recon_error(Xn), dtype=float)
        return out

    def score(self, X_real) -> Dict[str, Any]:
        Xr = _to_numpy(X_real)
        Xf = self.sample(min(2048, Xr.shape[0]))
        return {"KS_mean": _ks_mean(Xr[:len(Xf)], Xf), "MMD_rbf": _mmd_rbf(Xr[:len(Xf)], Xf)}

    # -------- persistence stubs --------

    def save(self, path: str):
        # Hook up joblib/torch.save if needed.
        pass

    @classmethod
    def load(cls, path: str) -> "GenerativeFamily":
        raise NotImplementedError("Implement load() with your chosen persistence layer.")
