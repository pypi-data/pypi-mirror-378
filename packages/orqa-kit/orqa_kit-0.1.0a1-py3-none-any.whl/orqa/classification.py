# classification.py
"""
Classification family (dual-mode: classical | quantum)

Standardized outputs for stacking/integration:
- predict(X) -> {"proba": np.ndarray shape (N,K),
                 "proba_pos": np.ndarray shape (N,1) if K==2}

Classical (mode="classical")
----------------------------
  model="hgb"    : HistGradientBoostingClassifier (default)
  model="logreg" : LogisticRegression (liblinear/saga chosen by sklearn)
  model="xgb"    : XGBoost XGBClassifier (optional; requires xgboost)

  Calibration (optional): params["calibrate"]=True wraps base model with
  CalibratedClassifierCV(method="isotonic" by default; "sigmoid" optional).

Quantum (mode="quantum")  [portable hybrids; swap for real QML later]
-------------------------
  model="qsvc"   : "Quantum-kernel-like" SVC with RBF kernel (probability=True),
                   optionally preceded by PCA to fit n_qubits.
  model="qkrr"   : Quantum-kernel ridge classifier (one-vs-rest) using KernelRidge
                   on RBF kernels and logistic link on outputs.
  model="vqc"    : Variational-like classifier: nonlinear sin/cos feature map
                   (depth repeats) + LogisticRegression (OVR for multi-class).

Notes
-----
- These quantum variants are *framework-free* approximations that respect the same
  interface (accept n_qubits/encoding/ansatz/etc.) so you can plug a real QML backend
  later without changing base/integration code.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, List
import warnings
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.svm import SVC
from sklearn.kernel_ridge import KernelRidge
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelBinarizer

# Optional XGBoost
try:
    from xgboost import XGBClassifier  # type: ignore
    _HAS_XGB = True
except Exception:
    _HAS_XGB = False


# ---------- utilities ----------

def _to_numpy(X) -> np.ndarray:
    if hasattr(X, "to_numpy"):
        return X.to_numpy()
    return np.asarray(X)

def _ensure_labels(y) -> np.ndarray:
    y = np.asarray(y)
    if y.ndim > 1:
        y = y.ravel()
    return y

def _is_binary(y: np.ndarray) -> bool:
    return np.unique(y).size == 2


# ---------- Classical models ----------

class _HGBClf:
    def __init__(self, params: Dict[str, Any]):
        self.params = {
            "max_depth": params.get("max_depth", None),
            "learning_rate": params.get("lr", 0.05),
            "l2_regularization": params.get("l2", 0.0),
            "class_weight": params.get("class_weight", None),
        }
        self.model = HistGradientBoostingClassifier(**self.params)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)

    def decision_function(self, X):
        # HGB has predict_proba; decision_function not used here
        proba = self.predict_proba(X)
        if proba.shape[1] == 2:
            return proba[:, 1] - proba[:, 0]
        return proba  # fallback


class _LogRegClf:
    def __init__(self, params: Dict[str, Any]):
        self.params = {
            "class_weight": params.get("class_weight", None),
            "max_iter": params.get("max_iter", 500),
        }
        self.model = LogisticRegression(**self.params)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)

    def decision_function(self, X):
        if hasattr(self.model, "decision_function"):
            return self.model.decision_function(X)
        return self.model.predict_proba(X)[:, 1]


class _XGBClf:
    def __init__(self, params: Dict[str, Any]):
        if not _HAS_XGB:
            raise ImportError("xgboost is not installed; set model!='xgb' or install xgboost.")
        xgb_params = {
            "n_estimators": params.get("n_estimators", 300),
            "max_depth": params.get("max_depth", 6),
            "learning_rate": params.get("lr", 0.05),
            "subsample": params.get("subsample", 0.8),
            "colsample_bytree": params.get("colsample_bytree", 0.8),
            "reg_alpha": params.get("reg_alpha", 0.0),
            "reg_lambda": params.get("reg_lambda", 1.0),
            "tree_method": params.get("tree_method", "hist"),
            "eval_metric": params.get("eval_metric", "logloss"),
            "use_label_encoder": False,
        }
        self.model = XGBClassifier(**xgb_params)

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)

    def decision_function(self, X):
        proba = self.predict_proba(X)
        if proba.shape[1] == 2:
            return proba[:, 1] - proba[:, 0]
        return proba


# ---------- Quantum-inspired models ----------

class _QSVC:
    """
    "Quantum-kernel-like" SVC with RBF kernel; optional PCA to n_qubits.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.seed = qcfg.get("seed", 42)
        self.gamma = params.get("gamma", "scale")  # SVC default
        self.C = float(params.get("C", 1.0))
        self.pca: Optional[PCA] = None
        self.svc = SVC(kernel="rbf", gamma=self.gamma, C=self.C, probability=True, random_state=self.seed)

    def _prep(self, X):
        if X.shape[1] > self.n_qubits:
            if self.pca is None:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                return self.pca.fit_transform(X)
            else:
                return self.pca.transform(X)
        return X

    def fit(self, X, y):
        Z = self._prep(X)
        self.svc.fit(Z, y)
        return self

    def predict_proba(self, X) -> np.ndarray:
        Z = self._prep(X)
        return self.svc.predict_proba(Z)

    def decision_function(self, X):
        Z = self._prep(X)
        return self.svc.decision_function(Z)


class _QKRRClf:
    """
    Kernel Ridge "classifier": one-vs-rest KernelRidge with RBF kernel,
    probabilities via calibrated logistic on OVR scores.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.seed = qcfg.get("seed", 42)
        self.gamma = float(params.get("gamma", 0.5))
        self.alpha = float(params.get("alpha", 1e-2))
        self.pca: Optional[PCA] = None
        self.ovr_: List[KernelRidge] = []
        self.lr_: List[LogisticRegression] = []  # Platt link per class

    def _prep(self, X):
        if X.shape[1] > self.n_qubits:
            if self.pca is None:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                return self.pca.fit_transform(X)
            else:
                return self.pca.transform(X)
        return X

    def fit(self, X, y):
        Z = self._prep(X)
        y = _ensure_labels(y)
        classes = np.unique(y)
        self.ovr_.clear(); self.lr_.clear()
        for c in classes:
            kr = KernelRidge(alpha=self.alpha, kernel="rbf", gamma=self.gamma)
            ybin = (y == c).astype(float)
            kr.fit(Z, ybin)
            self.ovr_.append(kr)
            # calibrate to probability
            score = kr.predict(Z).reshape(-1, 1)
            lr = LogisticRegression(max_iter=300)
            lr.fit(score, (y == c).astype(int))
            self.lr_.append(lr)
        self.classes_ = classes
        return self

    def _scores(self, Z) -> np.ndarray:
        return np.column_stack([kr.predict(Z) for kr in self.ovr_])  # (N,K)

    def predict_proba(self, X) -> np.ndarray:
        Z = self._prep(X)
        scores = self._scores(Z)
        # per-class Platt scaling then normalize to 1
        probs = []
        for j, lr in enumerate(self.lr_):
            p = lr.predict_proba(scores[:, [j]])[:, 1]
            probs.append(p)
        P = np.column_stack(probs)
        P = np.clip(P, 1e-8, 1.0)
        P = P / P.sum(axis=1, keepdims=True)
        return P

    def decision_function(self, X):
        Z = self._prep(X)
        return self._scores(Z)


class _VQC:
    """
    Variational-like classifier:
      - Reduce to n_qubits via PCA
      - Nonlinear sin/cos feature map repeated 'depth' times
      - LogisticRegression (OVR) on mapped features
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.depth = int(qcfg.get("max_depth", 2))
        self.alpha = float(params.get("alpha", 1.0))
        self.seed = qcfg.get("seed", 42)
        self.pca: Optional[PCA] = None
        self.lr = LogisticRegression(max_iter=500, multi_class="auto")

    def _map(self, X):
        Z = X
        if X.shape[1] > self.n_qubits:
            if self.pca is None:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                Z = self.pca.fit_transform(X)
            else:
                Z = self.pca.transform(X)
        feats = []
        for d in range(self.depth):
            a = self.alpha * (d + 1)
            feats.append(np.sin(a * Z))
            feats.append(np.cos(a * Z))
        return np.concatenate(feats, axis=1)

    def fit(self, X, y):
        Phi = self._map(X)
        self.lr.fit(Phi, y)
        return self

    def predict_proba(self, X) -> np.ndarray:
        Phi = self._map(X)
        return self.lr.predict_proba(Phi)

    def decision_function(self, X):
        Phi = self._map(X)
        if hasattr(self.lr, "decision_function"):
            return self.lr.decision_function(Phi)
        return self.lr.predict_proba(Phi)[:, 1]


# ---------- Public Family ----------

class ClassificationFamily:
    """
    FamilyModel for classification with dual-mode operation.

    Args:
      params: dict of hyperparameters (see above)
      mode: "classical" | "quantum"
      qcfg: quantum spec dict or None

    Methods:
      fit(X, y)    -> metrics dict
      predict(X)   -> {"proba": (N,K), "proba_pos": (N,1) if K==2}
      score(X, y)  -> metrics dict
      save/load    -> stubs for persistence
    """

    def __init__(self, params: Dict[str, Any], mode: str = "classical", qcfg: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.mode = mode
        self.qcfg = qcfg or {}
        self.base = None
        self.model = None  # possibly calibrated wrapper
        self.fitted = False
        self.classes_: Optional[np.ndarray] = None
        self.binary_: bool = False

        # choose base estimator
        if self.mode == "classical":
            name = self.params.get("model", "hgb").lower()
            if name == "hgb":
                self.base = _HGBClf(self.params)
            elif name in ("logreg", "lr", "logistic"):
                self.base = _LogRegClf(self.params)
            elif name == "xgb":
                self.base = _XGBClf(self.params)
            else:
                self.base = _HGBClf(self.params)
        else:
            name = self.params.get("model", "qsvc").lower()
            if name == "qsvc":
                self.base = _QSVC(self.params, self.qcfg)
            elif name == "qkrr":
                self.base = _QKRRClf(self.params, self.qcfg)
            elif name == "vqc":
                self.base = _VQC(self.params, self.qcfg)
            else:
                self.base = _QSVC(self.params, self.qcfg)

        # calibration
        self.calibrate = bool(self.params.get("calibrate", True))
        self.calib_method = self.params.get("calibration_method", "isotonic")  # or "sigmoid"

    # -------- core API --------

    def fit(self, X, y=None, cv=None) -> Dict[str, Any]:
        if y is None:
            raise ValueError("ClassificationFamily.fit requires y for supervised training.")
        Xn = _to_numpy(X)
        yn = _ensure_labels(y)

        self.base.fit(Xn, yn)
        self.classes_ = np.unique(yn)
        self.binary_ = _is_binary(yn)

        # Wrap with calibrator if requested and supported
        if self.calibrate:
            # We re-wrap only for binary or when base lacks reliable proba calibration.
            # For multi-class isotonic is not directly supported; fall back gracefully.
            try:
                if self.binary_:
                    self.model = CalibratedClassifierCV(
                        base_estimator=self.base.model if hasattr(self.base, "model") else self.base,
                        method=self.calib_method,
                        cv=3
                    )
                    # Need decision function or proba; provide via wrappers
                    Xn_small = Xn
                    yn_small = yn
                    # Create a thin shim exposing predict_proba/decision_function
                    # If base has 'predict_proba', CalibratedClassifierCV can call it; else it uses decision_function.
                    # We'll try to pass through base.model when available.
                    self.model.fit(Xn_small, yn_small)
                else:
                    # multi-class: skip calibration or use base proba directly
                    self.model = self.base
            except Exception:
                warnings.warn("Calibration failed or unsupported; using base model.")
                self.model = self.base
        else:
            self.model = self.base

        self.fitted = True

        # quick train metrics
        proba = self.predict_proba(Xn)
        metrics = _clf_metrics(yn, proba)
        return metrics

    def predict(self, X) -> Dict[str, np.ndarray]:
        return self._predict_dict(X)

    def _predict_dict(self, X) -> Dict[str, np.ndarray]:
        if not self.fitted:
            raise RuntimeError("ClassificationFamily not fitted yet.")
        Xn = _to_numpy(X)
        proba = self.predict_proba(Xn)
        out = {"proba": proba}
        if proba.shape[1] == 2:
            out["proba_pos"] = proba[:, [1]]
        return out

    def predict_proba(self, X) -> np.ndarray:
        # The wrapped calibrator exposes predict_proba; base may also expose it.
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        # Fallback: convert decision_function to proba with sigmoid
        if hasattr(self.model, "decision_function"):
            s = self.model.decision_function(X)
            if s.ndim == 1:
                p1 = 1.0 / (1.0 + np.exp(-s))
                return np.column_stack([1 - p1, p1])
            # multi-class: softmax
            e = np.exp(s - s.max(axis=1, keepdims=True))
            return e / e.sum(axis=1, keepdims=True)
        # Last resort (shouldn't happen): uniform
        K = len(self.classes_) if self.classes_ is not None else 2
        return np.ones((len(X), K)) / float(K)

    def score(self, X, y=None) -> Dict[str, Any]:
        if y is None:
            return {}
        Xn = _to_numpy(X)
        yn = _ensure_labels(y)
        proba = self.predict_proba(Xn)
        return _clf_metrics(yn, proba)

    # -------- persistence stubs --------

    def save(self, path: str):
        # Hook up joblib or your preferred persistence.
        pass

    @classmethod
    def load(cls, path: str) -> "ClassificationFamily":
        raise NotImplementedError("Implement load() with your chosen persistence layer.")


# ---------- metrics ----------

def _clf_metrics(y_true: np.ndarray, proba: np.ndarray) -> Dict[str, float]:
    y_true = _ensure_labels(y_true)
    K = proba.shape[1]
    y_pred = proba.argmax(axis=1)
    acc = float(accuracy_score(y_true, y_pred))
    f1m = float(f1_score(y_true, y_pred, average="macro"))
    metrics = {"ACC": acc, "F1_macro": f1m}
    if K == 2:
        try:
            auc = float(roc_auc_score(y_true, proba[:, 1]))
            metrics["AUC"] = auc
        except Exception:
            pass
    return metrics