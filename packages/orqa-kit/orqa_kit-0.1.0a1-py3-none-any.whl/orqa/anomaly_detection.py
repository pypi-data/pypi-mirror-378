# anomaly_detection.py
"""
Anomaly family (dual-mode: classical | quantum)

Standardized outputs for stacking/integration:
- predict(X) -> {"score": np.ndarray shape (N,1)}    # higher = more anomalous

Classical (mode="classical")
----------------------------
  model="isoforest"   : IsolationForest (default)
  model="oneclasssvm" : One-Class SVM (RBF by default)
  model="lof"         : Local Outlier Factor (novelty=True for predict on new data)

Quantum (mode="quantum")  [portable, framework-free hybrids]
-------------------------
  model="qocsvm"      : "Quantum-kernel-like" One-Class SVM:
                        PCA to n_qubits → RBF kernel OCSVM (simulates Q-kernel behavior)
  model="vqc_energy"  : Variational-like energy score:
                        PCA to n_qubits → sin/cos feature map (depth repeats)
                        → distance-to-center energy (Deep-SVDD style)

Notes
-----
- These quantum variants mimic common QML ideas without heavy deps; you can swap
  in true Q-kernel or VQC backends later behind the same interface.
- All models emit an *anomaly score* where larger means "more anomalous".
- If labels are provided at fit(time) (0=normal, 1=anomaly), we report AUROC/AP.

Metrics
-------
- fit(X, y) -> {"AUROC": ..., "AP": ...} when y is given; else {}.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score, average_precision_score


# ---------- utilities ----------

def _to_numpy(X) -> np.ndarray:
    if hasattr(X, "to_numpy"):
        return X.to_numpy()
    return np.asarray(X)

def _ensure_labels(y) -> np.ndarray:
    y = np.asarray(y)
    if y.ndim > 1:
        y = y.ravel()
    return y.astype(int)

def _metrics_from_scores(y_true: np.ndarray, scores: np.ndarray) -> Dict[str, float]:
    m: Dict[str, float] = {}
    try:
        m["AUROC"] = float(roc_auc_score(y_true, scores))
    except Exception:
        pass
    try:
        m["AP"] = float(average_precision_score(y_true, scores))
    except Exception:
        pass
    return m


# ---------- Classical implementations ----------

class _ISOForest:
    def __init__(self, params: Dict[str, Any]):
        self.model = IsolationForest(
            contamination=params.get("contamination", "auto"),
            n_estimators=params.get("n_estimators", 200),
            max_samples=params.get("max_samples", "auto"),
            random_state=params.get("seed", 42),
            n_jobs=params.get("n_jobs", None),
            bootstrap=params.get("bootstrap", False),
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def score_samples(self, X) -> np.ndarray:
        # sklearn: higher score_samples => more normal. We want higher = more anomalous.
        return -self.model.decision_function(X)  # invert so higher = more anomalous


class _OneClassSVM:
    def __init__(self, params: Dict[str, Any]):
        self.model = OneClassSVM(
            kernel=params.get("kernel", "rbf"),
            gamma=params.get("gamma", "scale"),
            nu=params.get("nu", 0.5),
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def score_samples(self, X) -> np.ndarray:
        # decision_function: positive for inliers, negative for outliers
        return -self.model.decision_function(X)  # higher = more anomalous


class _LOF:
    def __init__(self, params: Dict[str, Any]):
        # novelty=True allows predicting on unseen data
        self.model = LocalOutlierFactor(
            n_neighbors=params.get("n_neighbors", 20),
            contamination=params.get("contamination", "auto"),
            novelty=True,
            metric=params.get("metric", "minkowski"),
            p=params.get("p", 2)
        )
        self._fitted = False

    def fit(self, X):
        self.model.fit(X)
        self._fitted = True
        return self

    def score_samples(self, X) -> np.ndarray:
        # decision_function: positive for inliers, negative for outliers
        return -self.model.decision_function(X)  # higher = more anomalous


# ---------- Quantum-inspired implementations ----------

class _QOCSVM:
    """
    "Quantum-kernel-like" One-Class SVM:
      PCA to n_qubits → OCSVM(RBF). Mimics using a quantum feature map by working
      in a reduced latent space compatible with a limited qubit budget.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.seed = qcfg.get("seed", 42)
        self.gamma = params.get("gamma", "scale")
        self.nu = float(params.get("nu", 0.5))
        self.pca: Optional[PCA] = None
        self.ocsvm = OneClassSVM(kernel="rbf", gamma=self.gamma, nu=self.nu)

    def _prep(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        if X.shape[1] > self.n_qubits:
            if self.pca is None or fit:
                self.pca = PCA(n_components=self.n_qubits, random_state=self.seed)
                return self.pca.fit_transform(X)
            else:
                return self.pca.transform(X)
        return X

    def fit(self, X):
        Z = self._prep(X, fit=True)
        self.ocsvm.fit(Z)
        return self

    def score_samples(self, X) -> np.ndarray:
        Z = self._prep(X, fit=False)
        return -self.ocsvm.decision_function(Z)  # higher = more anomalous


class _VQCEnergy:
    """
    Variational-like energy score (unsupervised):
      PCA to n_qubits → sin/cos feature map repeated 'depth' times →
      compute center vector c = mean(Phi(X_train)) →
      score(x) = ||Phi(x) - c||_2

    Params:
      alpha (float): feature map frequency scale
      depth (int): repetitions of map
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.depth = int(qcfg.get("max_depth", 2))
        self.alpha = float(params.get("alpha", 1.0))
        self.seed = qcfg.get("seed", 42)
        self.pca: Optional[PCA] = None
        self.center_: Optional[np.ndarray] = None

    def _map(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        Z = X
        if X.shape[1] > self.n_qubits:
            if self.pca is None or fit:
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

    def fit(self, X):
        Phi = self._map(X, fit=True)
        self.center_ = Phi.mean(axis=0, keepdims=True)  # (1,D)
        return self

    def score_samples(self, X) -> np.ndarray:
        Phi = self._map(X, fit=False)
        C = self.center_ if self.center_ is not None else Phi.mean(axis=0, keepdims=True)
        dist = np.linalg.norm(Phi - C, axis=1)  # (N,)
        return dist  # higher = more anomalous


# ---------- Public Family ----------

class AnomalyFamily:
    """
    FamilyModel for anomaly detection with dual-mode operation.

    Args:
      params: dict of hyperparameters
      mode: "classical" | "quantum"
      qcfg: quantum spec dict or None

    Methods:
      fit(X, y=None) -> metrics dict (AUROC/AP if y provided: 1=anomaly, 0=normal)
      predict(X)     -> {"score": (N,1)}
      score(X, y)    -> metrics dict on given split
      save/load      -> stubs for persistence
    """

    def __init__(self, params: Dict[str, Any], mode: str = "classical", qcfg: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.mode = mode
        self.qcfg = qcfg or {}
        self.model = None
        self.fitted = False

        if self.mode == "classical":
            name = self.params.get("model", "isoforest").lower()
            if name in ("isoforest", "iforest", "iso"):
                self.model = _ISOForest(self.params)
            elif name in ("oneclasssvm", "ocsvm", "svm"):
                self.model = _OneClassSVM(self.params)
            elif name in ("lof", "localoutlierfactor"):
                self.model = _LOF(self.params)
            else:
                self.model = _ISOForest(self.params)
        else:  # quantum
            name = self.params.get("model", "qocsvm").lower()
            if name in ("qocsvm", "q-ocsvm"):
                self.model = _QOCSVM(self.params, self.qcfg)
            elif name in ("vqc_energy", "vqce"):
                self.model = _VQCEnergy(self.params, self.qcfg)
            else:
                self.model = _QOCSVM(self.params, self.qcfg)

    # -------- core API --------

    def fit(self, X, y=None, cv=None) -> Dict[str, Any]:
        Xn = _to_numpy(X)
        self.model.fit(Xn)
        self.fitted = True
        if y is not None:
            yn = _ensure_labels(y)
            scores = self.model.score_samples(Xn).reshape(-1)
            return _metrics_from_scores(yn, scores)
        return {}

    def predict(self, X) -> Dict[str, np.ndarray]:
        if not self.fitted:
            raise RuntimeError("AnomalyFamily not fitted yet.")
        Xn = _to_numpy(X)
        s = self.model.score_samples(Xn).reshape(-1, 1)
        return {"score": s}

    def score(self, X, y=None) -> Dict[str, Any]:
        if y is None:
            return {}
        Xn = _to_numpy(X)
        yn = _ensure_labels(y)
        s = self.model.score_samples(Xn).reshape(-1)
        return _metrics_from_scores(yn, s)

    # -------- persistence stubs --------

    def save(self, path: str):
        # Hook up joblib or your preferred persistence.
        pass

    @classmethod
    def load(cls, path: str) -> "AnomalyFamily":
        raise NotImplementedError("Implement load() with your chosen persistence layer.")