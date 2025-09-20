# regression.py
"""
Regression family (dual-mode: classical | quantum)

Standardized outputs (for stacking/integration):
- predict(X) -> {"pred": np.ndarray shape (N,1), optional "q05": (N,1), "q95": (N,1)}

Models supported
----------------
Classical (mode="classical"):
  - model="hgb"   : HistGradientBoostingRegressor (default)
  - model="lin"   : LinearRegression baseline
  - optional quantiles via GradientBoostingRegressor(loss="quantile") when params["quantiles"] is provided

Quantum (mode="quantum")  [lightweight, simulator-friendly, no external QML deps]:
  - model="vqr"   : Variational-like regressor (nonlinear feature map + LinearRegression)
  - model="qkrr"  : "Quantum-kernel-like" Kernel Ridge Regression (RBF kernel)

Notes
-----
- This file avoids heavy quantum frameworks to keep the repo portable.
  The "quantum" models here are hybrid approximations that respect the same
  interface (accept n_qubits/encoding/etc.) so you can later swap in a real
  QML backend without touching base/integration code.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, List
import numpy as np

from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.decomposition import PCA


# ---------- utilities ----------

def _to_numpy(X) -> np.ndarray:
    if hasattr(X, "to_numpy"):
        return X.to_numpy()
    return np.asarray(X)


def _ensure_2d(y) -> np.ndarray:
    y = np.asarray(y).ravel()
    return y


# ---------- Classical implementations ----------

class _HGBReg:
    def __init__(self, params: Dict[str, Any]):
        self.params = {"max_depth": params.get("max_depth", None),
                       "learning_rate": params.get("lr", 0.05),
                       "l2_regularization": params.get("l2", 0.0)}
        self.model = HistGradientBoostingRegressor(**self.params)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)


class _LinReg:
    def __init__(self, params: Dict[str, Any]):
        self.model = LinearRegression()

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)


class _QuantileEnsemble:
    """Fit separate quantile regressors via GradientBoostingRegressor."""
    def __init__(self, quantiles: List[float], params: Dict[str, Any]):
        self.quantiles = quantiles
        self.models: Dict[float, GradientBoostingRegressor] = {}
        self.gbr_params = {
            "n_estimators": params.get("q_n_estimators", 200),
            "max_depth": params.get("q_max_depth", 3),
            "min_samples_leaf": params.get("q_min_samples_leaf", 1),
            "learning_rate": params.get("q_lr", 0.05),
            "subsample": params.get("q_subsample", 1.0),
            "random_state": params.get("seed", 42),
        }

    def fit(self, X, y):
        for q in self.quantiles:
            m = GradientBoostingRegressor(
                loss="quantile", alpha=float(q), **self.gbr_params
            )
            m.fit(X, y)
            self.models[q] = m
        return self

    def predict(self, X) -> Dict[float, np.ndarray]:
        return {q: self.models[q].predict(X) for q in self.quantiles}


# ---------- Quantum-inspired implementations ----------

class _VQR:
    """
    Variational-like regressor:
      - Reduce to n_qubits with PCA (if needed)
      - Nonlinear feature map: [sin(a*x), cos(a*x)] repeated depth times
      - Linear regression on mapped features

    Parameters (from qcfg/params):
      n_qubits, max_depth, seed (optional), encoding (angle|amplitude -> angle used here)
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.depth = int(qcfg.get("max_depth", 2))
        self.seed = qcfg.get("seed", 42)
        self.alpha = float(params.get("alpha", 1.0))
        self.pca: Optional[PCA] = None
        self.lin = LinearRegression()

    def _map(self, X: np.ndarray) -> np.ndarray:
        Z = X
        if X.shape[1] > self.n_qubits:
            if self.pca is None:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                Z = self.pca.fit_transform(X)
            else:
                Z = self.pca.transform(X)
        # angle encoding + depth repetitions
        feats = []
        for d in range(self.depth):
            a = self.alpha * (d + 1)
            feats.append(np.sin(a * Z))
            feats.append(np.cos(a * Z))
        Phi = np.concatenate(feats, axis=1)  # shape (N, 2 * n_qubits * depth)
        return Phi

    def fit(self, X, y):
        Phi = self._map(X)
        self.lin.fit(Phi, y)
        return self

    def predict(self, X) -> np.ndarray:
        Phi = self._map(X)
        return self.lin.predict(Phi)


class _QKRR:
    """
    "Quantum-kernel-like" Kernel Ridge Regression using an RBF kernel.
    Accepts n_qubits (for dimensionality capping via PCA) but uses classical kernel underneath.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.seed = qcfg.get("seed", 42)
        self.gamma = float(params.get("gamma", 0.5))   # kernel width
        self.alpha = float(params.get("alpha", 1e-2))  # ridge
        self.pca: Optional[PCA] = None
        self.kr = KernelRidge(alpha=self.alpha, kernel="rbf", gamma=self.gamma)

    def _prep(self, X: np.ndarray) -> np.ndarray:
        if X.shape[1] > self.n_qubits:
            if self.pca is None:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                return self.pca.fit_transform(X)
            else:
                return self.pca.transform(X)
        return X

    def fit(self, X, y):
        Z = self._prep(X)
        self.kr.fit(Z, y)
        return self

    def predict(self, X) -> np.ndarray:
        Z = self._prep(X)
        return self.kr.predict(Z)


# ---------- Public Family ----------

class RegressionFamily:
    """
    FamilyModel for regression with dual-mode operation.

    Args:
      params: dict of hyperparameters (see above)
      mode: "classical" | "quantum"
      qcfg: quantum spec dict or None

    Methods:
      fit(X, y)    -> metrics dict
      predict(X)   -> {"pred": (N,1), optional "q05": (N,1), "q95": (N,1)}
      score(X, y)  -> metrics dict
      save/load    -> (placeholders; wire to joblib/torch if needed)
    """

    def __init__(self, params: Dict[str, Any], mode: str = "classical", qcfg: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.mode = mode
        self.qcfg = qcfg or {}
        self.model = None
        self.quantiles_model: Optional[_QuantileEnsemble] = None
        self.fitted = False

        # choose base model
        if self.mode == "classical":
            model_name = self.params.get("model", "hgb").lower()
            if model_name == "hgb":
                self.model = _HGBReg(self.params)
            elif model_name == "lin":
                self.model = _LinReg(self.params)
            else:
                # fallback to HGB
                self.model = _HGBReg(self.params)
        else:  # quantum
            model_name = self.params.get("model", "vqr").lower()
            if model_name == "vqr":
                self.model = _VQR(self.params, self.qcfg)
            elif model_name == "qkrr":
                self.model = _QKRR(self.params, self.qcfg)
            else:
                self.model = _VQR(self.params, self.qcfg)

        # optional quantiles (classical path only by default)
        qs = self.params.get("quantiles", None)
        if self.mode == "classical" and qs:
            qs = sorted({float(q) for q in qs if 0.0 < float(q) < 1.0})
            if qs:
                self.quantiles_model = _QuantileEnsemble(qs, self.params)

    # -------- core API --------

    def fit(self, X, y=None, cv=None) -> Dict[str, Any]:
        Xn = _to_numpy(X)
        if y is None:
            raise ValueError("RegressionFamily.fit requires y for supervised training.")
        yn = _ensure_2d(y)

        self.model.fit(Xn, yn)

        if self.quantiles_model is not None:
            self.quantiles_model.fit(Xn, yn)

        self.fitted = True
        # training metrics (quick sanity)
        yhat = self.model.predict(Xn)
        metrics = _reg_metrics(yn, yhat)
        return metrics

    def predict(self, X) -> Dict[str, np.ndarray]:
        if not self.fitted:
            raise RuntimeError("RegressionFamily not fitted yet.")
        Xn = _to_numpy(X)
        pred = self.model.predict(Xn).reshape(-1, 1)

        out = {"pred": pred}
        if self.quantiles_model is not None:
            qpreds = self.quantiles_model.predict(Xn)
            for q, arr in qpreds.items():
                key = f"q{int(round(q*100)):02d}"
                out[key] = np.asarray(arr).reshape(-1, 1)
        return out

    def score(self, X, y=None) -> Dict[str, Any]:
        if y is None:
            return {}
        Xn = _to_numpy(X)
        yn = _ensure_2d(y)
        yhat = self.model.predict(Xn)
        return _reg_metrics(yn, yhat)

    # -------- persistence stubs (fill with joblib if desired) --------

    def save(self, path: str):
        # Placeholder: integrate joblib.dump(...) as needed
        pass

    @classmethod
    def load(cls, path: str) -> "RegressionFamily":
        # Placeholder: integrate joblib.load(...) as needed
        raise NotImplementedError("Implement load() with your chosen persistence layer.")


# ---------- metrics ----------

def _reg_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    return {"MAE": mae, "RMSE": rmse, "R2": r2}
