# clustering.py
"""
Clustering family (dual-mode: classical | quantum)

Standardized outputs for stacking/integration:
- predict(X) -> {
    "soft":   np.ndarray (N, C),   # soft cluster membership (rows sum to 1)
    "dist":   np.ndarray (N, C),   # distance-to-centroid (or proxy); smaller is closer
    "labels": np.ndarray (N, 1)    # hard labels in [0..C-1]
  }

Classical (mode="classical")
----------------------------
  model="kmeans" (default): KMeans with soft assignments derived from distances
  model="gmm"             : GaussianMixture; soft = responsibilities from predict_proba

Quantum (mode="quantum")  [portable, framework-free hybrids]
-------------------------
  model="qkmeans_kernel"  : "quantum-kernel-like" embedding via RBF kernel matrix factorization,
                            then KMeans in the embedded space (Nyström-style).
  model="qfeature_kmeans" : sin/cos feature map (depth repeats) after PCA to n_qubits,
                            then KMeans.

Notes
-----
- These quantum variants approximate common QML ideas without external deps.
  You can later swap in true q-means or swap-test distances behind the same interface.

Metrics
-------
- score(X) -> {"silhouette": float or NaN when invalid}
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, List
import numpy as np

from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.decomposition import PCA


# ---------- utilities ----------

def _to_numpy(X) -> np.ndarray:
    if hasattr(X, "to_numpy"):
        return X.to_numpy()
    return np.asarray(X)

def _soft_from_dist(D: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """
    Convert distances (N,C) into soft assignments via softmax over negative distance.
    """
    # avoid overflow; scale by temperature (tau); smaller tau -> harder assignments
    S = -D / max(temperature, 1e-12)
    S -= S.max(axis=1, keepdims=True)
    E = np.exp(S)
    P = E / (E.sum(axis=1, keepdims=True) + 1e-12)
    return P

def _euclidean_dist(X: np.ndarray, centers: np.ndarray) -> np.ndarray:
    # (x - c)^2 = x^2 + c^2 - 2 x·c
    x2 = (X ** 2).sum(axis=1, keepdims=True)         # (N,1)
    c2 = (centers ** 2).sum(axis=1, keepdims=True).T # (1,C)
    D2 = x2 + c2 - 2.0 * X @ centers.T               # (N,C)
    D2 = np.maximum(D2, 0.0)
    return np.sqrt(D2 + 1e-12)

def _labels_from_soft(P: np.ndarray) -> np.ndarray:
    return P.argmax(axis=1).reshape(-1, 1)


# ---------- Classical implementations ----------

class _KMeansClus:
    def __init__(self, params: Dict[str, Any]):
        self.C = int(params.get("n_clusters", 8))
        n_init = params.get("n_init", "auto")
        self.temperature = float(params.get("temperature", 1.0))
        self.km = KMeans(n_clusters=self.C, n_init=n_init, random_state=params.get("seed", 42))

    def fit(self, X):
        self.km.fit(X)
        return self

    def predict(self, X) -> Dict[str, np.ndarray]:
        centers = self.km.cluster_centers_
        D = _euclidean_dist(X, centers)                  # (N,C)
        soft = _soft_from_dist(D, temperature=self.temperature)
        labels = _labels_from_soft(soft)
        return {"soft": soft, "dist": D, "labels": labels}


class _GMMClus:
    def __init__(self, params: Dict[str, Any]):
        self.C = int(params.get("n_clusters", 8))
        self.cov_type = params.get("covariance_type", "full")
        self.gmm = GaussianMixture(
            n_components=self.C,
            covariance_type=self.cov_type,
            random_state=params.get("seed", 42),
            reg_covar=params.get("reg_covar", 1e-6),
            max_iter=params.get("max_iter", 200)
        )

    def fit(self, X):
        self.gmm.fit(X)
        return self

    def predict(self, X) -> Dict[str, np.ndarray]:
        soft = self.gmm.predict_proba(X)                 # (N,C)
        labels = _labels_from_soft(soft)
        # proxy distance: Mahalanobis-like negative log-responsibility mapped to distance
        # compute Euclidean to means as a simple, interpretable 'dist'
        centers = self.gmm.means_
        D = _euclidean_dist(X, centers)
        return {"soft": soft, "dist": D, "labels": labels}


# ---------- Quantum-inspired implementations ----------

class _QKMeansKernel:
    """
    "Quantum-kernel-like" KMeans:
      - Build an RBF kernel (as proxy for a quantum feature map inner product)
      - Map to a low-rank feature space via Nyström (top components)
      - Run KMeans in that space.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.C = int(params.get("n_clusters", 8))
        self.gamma = float(params.get("gamma", 0.5))
        self.rank = int(params.get("rank", None) or self.C)  # embedding rank
        self.seed = qcfg.get("seed", 42)
        n_init = params.get("n_init", "auto")
        self.km = KMeans(n_clusters=self.C, n_init=n_init, random_state=self.seed)
        self.X_ref_: Optional[np.ndarray] = None
        self.U_: Optional[np.ndarray] = None
        self.S_: Optional[np.ndarray] = None

    def _embed(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        if fit or self.X_ref_ is None:
            self.X_ref_ = X
            K = rbf_kernel(X, X, gamma=self.gamma)                 # (N,N)
            # eigendecomposition (symmetric PSD)
            S, U = np.linalg.eigh(K)                               # ascending
            S = np.maximum(S, 0.0)
            idx = np.argsort(S)[::-1][: self.rank]
            self.S_ = np.sqrt(S[idx])                              # (r,)
            self.U_ = U[:, idx]                                    # (N,r)
            Phi = self.U_ * self.S_
            return Phi
        else:
            K = rbf_kernel(X, self.X_ref_, gamma=self.gamma)       # (M,Nref)
            Phi = K @ (self.U_ / (self.S_ + 1e-12))                # (M,r)
            return Phi

    def fit(self, X):
        Phi = self._embed(X, fit=True)
        self.km.fit(Phi)
        return self

    def predict(self, X) -> Dict[str, np.ndarray]:
        Phi = self._embed(X, fit=False)
        centers = self.km.cluster_centers_                          # in embedded space
        # distances in embedded space
        D_emb = _euclidean_dist(Phi, centers)
        soft = _soft_from_dist(D_emb, temperature=1.0)
        labels = _labels_from_soft(soft)
        # also compute original-space proxy distance to data-driven "preimages":
        D = D_emb  # report embedded distance as dist
        return {"soft": soft, "dist": D, "labels": labels}


class _QFeatureKMeans:
    """
    Sin/Cos feature map after PCA to n_qubits (depth repeats), then KMeans.
    """
    def __init__(self, params: Dict[str, Any], qcfg: Dict[str, Any]):
        self.C = int(params.get("n_clusters", 8))
        self.n_qubits = int(qcfg.get("n_qubits", 4))
        self.depth = int(qcfg.get("max_depth", 2))
        self.alpha = float(params.get("alpha", 1.0))
        self.seed = qcfg.get("seed", 42)
        self.pca: Optional[PCA] = None
        n_init = params.get("n_init", "auto")
        self.km = KMeans(n_clusters=self.C, n_init=n_init, random_state=self.seed)

    def _map(self, X: np.ndarray, fit=False) -> np.ndarray:
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
        self.km.fit(Phi)
        return self

    def predict(self, X) -> Dict[str, np.ndarray]:
        Phi = self._map(X, fit=False)
        centers = self.km.cluster_centers_
        D = _euclidean_dist(Phi, centers)
        soft = _soft_from_dist(D, temperature=1.0)
        labels = _labels_from_soft(soft)
        return {"soft": soft, "dist": D, "labels": labels}


# ---------- Public Family ----------

class ClusteringFamily:
    """
    FamilyModel for clustering with dual-mode operation.

    Args:
      params: dict of hyperparameters (see above)
      mode: "classical" | "quantum"
      qcfg: quantum spec dict or None

    Methods:
      fit(X)        -> metrics dict (silhouette where valid)
      predict(X)    -> {"soft","dist","labels"}
      score(X, y)   -> unsupervised quality (silhouette) ignoring y
      save/load     -> stubs for persistence
    """

    def __init__(self, params: Dict[str, Any], mode: str = "classical", qcfg: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.mode = mode
        self.qcfg = qcfg or {}
        self.model = None
        self.fitted = False
        self.C = int(self.params.get("n_clusters", 8))

        if self.mode == "classical":
            name = self.params.get("model", "kmeans").lower()
            if name == "kmeans":
                self.model = _KMeansClus(self.params)
            elif name == "gmm":
                self.model = _GMMClus(self.params)
            else:
                self.model = _KMeansClus(self.params)
        else:
            name = self.params.get("model", "qkmeans_kernel").lower()
            if name == "qkmeans_kernel":
                self.model = _QKMeansKernel(self.params, self.qcfg)
            elif name == "qfeature_kmeans":
                self.model = _QFeatureKMeans(self.params, self.qcfg)
            else:
                self.model = _QKMeansKernel(self.params, self.qcfg)

    # -------- core API --------

    def fit(self, X, y=None, cv=None) -> Dict[str, Any]:
        Xn = _to_numpy(X)
        self.model.fit(Xn)
        self.fitted = True
        # attempt silhouette; if degenerate (1 cluster or 1 sample), return NaN
        try:
            preds = self.model.predict(Xn)
            labels = preds["labels"].ravel()
            if len(np.unique(labels)) > 1 and Xn.shape[0] > self.C:
                sil = float(silhouette_score(Xn, labels))
            else:
                sil = float("nan")
        except Exception:
            sil = float("nan")
        return {"silhouette": sil}

    def predict(self, X) -> Dict[str, np.ndarray]:
        if not self.fitted:
            raise RuntimeError("ClusteringFamily not fitted yet.")
        Xn = _to_numpy(X)
        out = self.model.predict(Xn)
        # ensure standard shapes
        out["soft"] = np.asarray(out["soft"], dtype=float)
        out["dist"] = np.asarray(out["dist"], dtype=float)
        out["labels"] = np.asarray(out["labels"], dtype=int).reshape(-1, 1)
        return out

    def score(self, X, y=None) -> Dict[str, Any]:
        Xn = _to_numpy(X)
        try:
            preds = self.predict(Xn)
            labels = preds["labels"].ravel()
            if len(np.unique(labels)) > 1 and Xn.shape[0] > self.C:
                sil = float(silhouette_score(Xn, labels))
            else:
                sil = float("nan")
        except Exception:
            sil = float("nan")
        return {"silhouette": sil}

    # -------- persistence stubs --------

    def save(self, path: str):
        # Hook up joblib or your preferred persistence.
        pass

    @classmethod
    def load(cls, path: str) -> "ClusteringFamily":
        raise NotImplementedError("Implement load() with your chosen persistence layer.")