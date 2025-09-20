# integrate.py
"""
IntegrationModel: learns a fusion model over per-expert outputs.

- Consumes standardized, row-aligned outputs from base.ExpertBundle:
    stacked_dict = {
        "exp_id:key": np.ndarray shape (N, d_key)  # e.g., "exp_a:proba_pos", "exp_b:pred", "exp_c:soft", "exp_a:mask"
    }

- Selects which "exp_id:key" tensors to use via config.integration.include
  (supports wildcards like "exp_*:mask", "exp_a:*").

- Builds a meta design matrix X_meta by concatenating the selected tensors
  (flattening last dimensions). Handles shape mismatches and NaNs robustly.

- Strategies:
    * stacking  : logistic (classification) or linear/ridge (regression)
    * weighted  : constrained non-negative simplex weights (least squares / logloss proxy)
    * blending  : holdout-based convex combination (simple variant)

- Calibration (optional):
    * "isotonic": IsotonicRegression on fused probabilities (classification binary)
    * "platt"   : LogisticRegression on fused scores → calibrated proba (binary)

- Outputs:
    predict() → {
        "fused": np.ndarray (N, 1 or K),
        "contrib": { "coef": np.ndarray (D,), "columns": [col names], "per_row": Optional[np.ndarray] }
    }

Notes:
- For multi-class classification, we currently train one-vs-rest logistic stacking.
- For regression, we use LinearRegression by default; replace with Ridge if needed.
- Masks: include them explicitly in integration.include (e.g., "exp_*:mask"),
  so the meta-learner can separate "zero because not applicable" from a true zero.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional
import fnmatch
import numpy as np

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


# -----------------------------
# Utility: pattern matching and stacking
# -----------------------------

def _match_keys(available: List[str], patterns: List[str]) -> List[str]:
    """Return ordered list of keys matching any of the wildcard patterns."""
    out: List[str] = []
    seen = set()
    for pat in patterns:
        for k in available:
            if fnmatch.fnmatch(k, pat) and k not in seen:
                out.append(k); seen.add(k)
    return out


def _flatten_feature_block(arr: np.ndarray, key: str) -> Tuple[np.ndarray, List[str]]:
    """Flatten (N, d1, d2, ...) to (N, D) with column names key[j]."""
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    elif arr.ndim > 2:
        arr = arr.reshape(arr.shape[0], -1)
    cols = [f"{key}[{j}]" for j in range(arr.shape[1])]
    return arr, cols


def _nan_safe(arr: np.ndarray, fill: float = 0.0) -> np.ndarray:
    if not np.isnan(arr).any():
        return arr
    out = arr.copy()
    out[np.isnan(out)] = fill
    return out


# -----------------------------
# Calibration helpers
# -----------------------------

class _IsotonicCalibrator:
    """Binary isotonic calibration on predicted probabilities."""
    def __init__(self):
        self.iso = IsotonicRegression(out_of_bounds="clip")

    def fit(self, p: np.ndarray, y: np.ndarray):
        p1 = p.ravel()
        y1 = y.ravel()
        self.iso.fit(p1, y1)
        return self

    def predict(self, p: np.ndarray) -> np.ndarray:
        return self.iso.transform(p.ravel()).reshape(-1, 1)


class _PlattCalibrator:
    """Binary Platt scaling via logistic regression on fused score/proba."""
    def __init__(self):
        self.lr = LogisticRegression(max_iter=200)

    def fit(self, s: np.ndarray, y: np.ndarray):
        s1 = s.reshape(-1, 1)  # single feature = fused score/proba
        self.lr.fit(s1, y.ravel())
        return self

    def predict(self, s: np.ndarray) -> np.ndarray:
        s1 = s.reshape(-1, 1)
        return self.lr.predict_proba(s1)[:, 1:].reshape(-1, 1)


# -----------------------------
# IntegrationModel
# -----------------------------

class IntegrationModel:
    """
    Meta-learner over expert outputs.

    cfg = {
        "strategy": "stacking" | "weighted" | "blending",
        "meta": {"type": "logistic" | "linear" | "mlp", "params": {...}},
        "include": ["exp_a:proba_pos","exp_b:pred","exp_*:mask", ...],
        "calibration": {"type": "isotonic" | "platt" | "none"},
        "budget_policy": {...}  # (not implemented here)
    }
    """

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg or {}
        meta = self.cfg.get("meta", {}) or {}
        self.meta_type: str = str(meta.get("type", "logistic"))
        self.strategy: str = str(self.cfg.get("strategy", "stacking"))
        self.include: List[str] = list(self.cfg.get("include", []))
        self.calib_cfg: Optional[Dict[str, Any]] = self.cfg.get("calibration", None)

        # Learned artifacts
        self.columns_: List[str] = []
        self.scaler_: Optional[StandardScaler] = None
        self.model_: Any = None           # meta learner
        self.models_ovr_: Optional[List[Any]] = None  # multi-class OVR
        self.calibrator_: Any = None
        self.task_: str = "classification" if self.meta_type == "logistic" else "regression"
        self.class_count_: Optional[int] = None

    # -------- Core stacking matrix builder --------

    def _build_meta_matrix(self, stacked: Dict[str, np.ndarray]) -> np.ndarray:
        available = list(stacked.keys())
        selected_keys = _match_keys(available, self.include)
        if not selected_keys:
            raise ValueError("Integration.include selected no features. Check config.include patterns.")

        X_blocks: List[np.ndarray] = []
        cols: List[str] = []
        for key in selected_keys:
            arr = stacked[key]
            arr = _nan_safe(arr, fill=0.0)
            block, names = _flatten_feature_block(arr, key)
            X_blocks.append(block)
            cols += names

        X_meta = np.hstack(X_blocks) if X_blocks else np.zeros((len(next(iter(stacked.values()))), 0))
        self.columns_ = cols
        return X_meta

    # -------- Strategy trainers --------

    def _fit_stacking(self, X: np.ndarray, y: np.ndarray):
        # Simple scaling helps linear/logistic meta
        self.scaler_ = StandardScaler(with_mean=True, with_std=True)
        Xs = self.scaler_.fit_transform(X)

        if self.task_ == "classification":
            # Check if multi-class (labels > 2)
            classes = np.unique(y)
            K = len(classes)
            self.class_count_ = K
            if K <= 2:
                self.model_ = LogisticRegression(max_iter=500)
                self.model_.fit(Xs, y)
            else:
                # One-vs-rest logistic
                self.models_ovr_ = []
                for k in classes:
                    yk = (y == k).astype(int)
                    lr = LogisticRegression(max_iter=500)
                    lr.fit(Xs, yk)
                    self.models_ovr_.append(lr)
        else:
            self.model_ = LinearRegression()
            self.model_.fit(Xs, y)

        # Calibration (binary classification only)
        if self.task_ == "classification" and (self.class_count_ is None or self.class_count_ == 2):
            if self.calib_cfg and self.calib_cfg.get("type") in {"isotonic", "platt"}:
                p = self._predict_proba_internal(X)  # pre-calib proba (N,1)
                ctype = self.calib_cfg["type"]
                if ctype == "isotonic":
                    self.calibrator_ = _IsotonicCalibrator().fit(p, y)
                elif ctype == "platt":
                    self.calibrator_ = _PlattCalibrator().fit(p, y)

    def _fit_weighted(self, X: np.ndarray, y: np.ndarray):
        """
        Learn non-negative weights (convex) to combine columns. For classification (binary),
        minimize logloss via simple grid-prox (approx); for regression, least squares with NNLS.
        """
        # Initialize equal weights per column
        n_feat = X.shape[1]
        w = np.ones(n_feat, dtype=float) / max(n_feat, 1)

        if self.task_ == "classification":
            # crude projected gradient on logloss over proba in [0,1]
            # interpret columns as base probabilities; clip to [1e-6,1-1e-6]
            Xp = np.clip(X, 1e-6, 1 - 1e-6)
            lr = 0.5
            for _ in range(300):
                p = np.clip(Xp @ w, 1e-6, 1 - 1e-6)
                # gradient of logloss wrt p times dp/dw = X
                grad = ((p - y) / (p * (1 - p))) @ Xp / len(y)
                w -= lr * grad
                # project to simplex
                w = np.maximum(w, 0)
                s = w.sum()
                if s == 0: w[:] = 1.0 / n_feat
                else: w /= s
            self.model_ = ("weighted_classification", w)
        else:
            # regression NNLS-like: non-negative least squares via projected GD
            lr = 0.1
            for _ in range(500):
                grad = (X @ w - y) @ X / len(y)
                w -= lr * grad
                w = np.maximum(w, 0)
                s = w.sum()
                if s == 0: w[:] = 1.0 / n_feat
                else: w /= s
            self.model_ = ("weighted_regression", w)

    def _fit_blending(self, X: np.ndarray, y: np.ndarray):
        """
        Simple holdout blending (assumes you've provided a holdout split upstream).
        Here we just fallback to stacking with linear/logistic for simplicity.
        """
        self._fit_stacking(X, y)

    # -------- Public API --------

    def fit(self, stacked_dict: Dict[str, np.ndarray], y: Optional[np.ndarray] = None):
        """
        Train the fusion layer.

        For unsupervised workflows (y=None), the integrator cannot learn;
        you may still call predict() to return a configured weighted sum
        (not implemented here) — we recommend providing y for training.
        """
        X = self._build_meta_matrix(stacked_dict)
        if y is None or len(y) == 0:
            # No supervision → store scaler and exit; predict() will just pass through first column
            self.scaler_ = StandardScaler(with_mean=True, with_std=True).fit(X) if X.size else None
            self.model_ = ("identity", None)
            return self

        if self.strategy == "stacking":
            self._fit_stacking(X, y)
        elif self.strategy == "weighted":
            self._fit_weighted(X, y)
        elif self.strategy == "blending":
            self._fit_blending(X, y)
        else:
            raise ValueError(f"Unknown integration strategy: {self.strategy}")
        return self

    # -------- Internal prediction helpers --------

    def _predict_meta_raw(self, X: np.ndarray) -> np.ndarray:
        """Return raw fused scores (regression value or classification score/proba)."""
        if isinstance(self.model_, tuple) and self.model_[0].startswith("weighted"):
            w = self.model_[1]
            s = X @ w
            return s.reshape(-1, 1)

        if self.model_ == ("identity", None):
            # passthrough first column (or zeros)
            if X.size == 0:
                return np.zeros((0, 1))
            return X[:, [0]]

        # scaling
        Xs = self.scaler_.transform(X) if self.scaler_ is not None else X

        if self.task_ == "classification":
            if self.models_ovr_ is not None:
                # multi-class one-vs-rest
                scores = []
                for lr in self.models_ovr_:
                    scores.append(lr.decision_function(Xs).reshape(-1, 1))
                scores = np.hstack(scores)  # shape (N, K)
                # convert to probabilities via softmax
                e = np.exp(scores - scores.max(axis=1, keepdims=True))
                p = e / e.sum(axis=1, keepdims=True)
                return p
            else:
                # binary: return probability of class 1
                p = self.model_.predict_proba(Xs)[:, 1].reshape(-1, 1)
                return p
        else:
            yhat = self.model_.predict(Xs).reshape(-1, 1)
            return yhat

    def _predict_proba_internal(self, X: np.ndarray) -> np.ndarray:
        """Binary proba helper (pre-calibration)."""
        p = self._predict_meta_raw(X)
        # if multi-class, not used for calibration here
        return p

    # -------- Public predict --------

    def predict(self, stacked_dict: Dict[str, np.ndarray]) -> Dict[str, Any]:
        X = self._build_meta_matrix(stacked_dict)
        fused_raw = self._predict_meta_raw(X)

        if self.task_ == "classification" and (self.class_count_ is None or self.class_count_ == 2):
            # optional calibration
            if self.calibrator_ is not None:
                fused = self.calibrator_.predict(fused_raw)
            else:
                fused = fused_raw
        else:
            fused = fused_raw  # regression or multi-class probs

        contrib = self._contributions(X, fused_raw)
        return {
            "fused": fused,
            "contrib": contrib,
            "columns": self.columns_,
        }

    # -------- Contributions / explanations --------

    def _contributions(self, X: np.ndarray, fused_raw: np.ndarray) -> Dict[str, Any]:
        """
        Provide lightweight contribution info:
        - For linear/logistic (binary): coefficients and optional per-row dot-products.
        - For weighted strategies: learned weights.
        - For multi-class: per-class coefficient norms.
        """
        info: Dict[str, Any] = {}

        if isinstance(self.model_, tuple) and self.model_[0].startswith("weighted"):
            w = self.model_[1]
            info["weights"] = w.tolist()
            info["columns"] = self.columns_
            return info

        if self.model_ == ("identity", None):
            info["weights"] = [1.0] + [0.0] * (X.shape[1] - 1)
            info["columns"] = self.columns_
            return info

        Xs = self.scaler_.transform(X) if self.scaler_ is not None else X

        if self.task_ == "classification":
            if self.models_ovr_ is not None:
                # multi-class: report L2 norm per feature across OVR classifiers
                coefs = np.stack([m.coef_.ravel() for m in self.models_ovr_], axis=1)  # (D,K)
                norms = np.linalg.norm(coefs, axis=1)
                info["coef_norm"] = norms.tolist()
                info["columns"] = self.columns_
            else:
                coef = getattr(self.model_, "coef_", None)
                if coef is not None:
                    coef = coef.ravel()
                    info["coef"] = coef.tolist()
                    # optional per-row contribution = Xs * coef (elementwise) summed
                    contrib = Xs * coef
                    info["per_row"] = contrib.tolist() if Xs.shape[0] <= 2000 else None
                    info["columns"] = self.columns_
        else:
            coef = getattr(self.model_, "coef_", None)
            if coef is not None:
                coef = coef.ravel()
                info["coef"] = coef.tolist()
                contrib = Xs * coef
                info["per_row"] = contrib.tolist() if Xs.shape[0] <= 2000 else None
                info["columns"] = self.columns_

        return info
