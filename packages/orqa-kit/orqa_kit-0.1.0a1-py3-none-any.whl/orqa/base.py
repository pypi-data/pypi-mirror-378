# base.py
"""
Base: builds and manages experts for a dataset/use-case.

Responsibilities
----------------
- Interpret DatasetConfig (from config.py).
- Build global + per-expert feature pipelines.
- For each expert:
  - Evaluate its slice (row mask).
  - Instantiate family model (regression/classification/clustering/anomaly/generative).
  - Use mode = "classical" or "quantum" to select implementation.
  - Fit on masked rows; produce standardized outputs aligned to all rows.
- Provide outputs for integration:
  - OOF/VAL outputs during training.
  - Predict outputs for new data.
- Provide provenance: which experts ran, params, mode, quantum cfg, metrics.

This file does not implement the actual models — it delegates to the family
modules (regression.py, classification.py, ...). Those must implement the
FamilyModel interface.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from .config import DatasetConfig, ExpertSpec

def _encode_features(df: pd.DataFrame, ref_columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    """
    One-hot encode non-numeric columns and keep numeric as-is.
    If ref_columns is provided, reindex to those columns (adding missing = 0).
    """
    if df is None or df.shape[0] == 0:
        return pd.DataFrame(index=getattr(df, "index", None)), []

    num = df.select_dtypes(include=[np.number])
    cat = df.select_dtypes(exclude=[np.number])
    if cat.shape[1] > 0:
        cat = cat.astype(str)
        cat_oh = pd.get_dummies(cat, drop_first=False)
        feat = pd.concat([num, cat_oh], axis=1)
    else:
        feat = num.copy()

    # Stable column order
    feat = feat.sort_index(axis=1)

    if ref_columns is not None:
        # Ensure all reference columns exist in the same order
        for col in ref_columns:
            if col not in feat.columns:
                feat[col] = 0
        feat = feat[ref_columns]
    return feat, list(feat.columns)

# ---- family factories (imports) ----
# Each family module must implement FamilyModel(params:dict, mode:str, qcfg:dict|None).
from . import regression
from . import classification
from . import clustering
from . import anomaly_detection
from . import generative


# ----------------------------
# Family factory
# ----------------------------

def make_family(family: str, mode: str, params: dict, qcfg: Optional[dict] = None):
    """Dispatch to the right family implementation."""
    if family == "regression":
        return regression.RegressionFamily(params=params, mode=mode, qcfg=qcfg)
    elif family == "classification":
        return classification.ClassificationFamily(params=params, mode=mode, qcfg=qcfg)
    elif family == "clustering":
        return clustering.ClusteringFamily(params=params, mode=mode, qcfg=qcfg)
    elif family == "anomaly":
        return anomaly_detection.AnomalyFamily(params=params, mode=mode, qcfg=qcfg)
    elif family == "generative":
        return generative.GenerativeFamily(params=params, mode=mode, qcfg=qcfg)
    else:
        raise ValueError(f"Unknown family: {family}")


# ----------------------------
# Slice evaluation (stub)
# ----------------------------

def eval_slice(expr: str, X: pd.DataFrame) -> np.ndarray:
    """
    Convert slice DSL string into boolean mask over rows.
    For now we rely on pandas.query for simplicity; in prod replace with safe parser.
    """
    if expr.strip().lower() == "all":
        return np.ones(len(X), dtype=bool)
    try:
        mask = X.eval(expr)
        if mask.dtype != bool:
            raise ValueError("slice expression must evaluate to boolean mask")
        return mask.to_numpy()
    except Exception as e:
        raise ValueError(f"Failed to evaluate slice {expr!r}: {e}")


# ----------------------------
# Expert wrapper
# ----------------------------

class Expert:
    def __init__(self, spec: ExpertSpec):
        self.spec = spec
        self.model = make_family(
            spec.family, spec.mode, spec.params, 
            qcfg=(spec.quantum and spec.quantum.__dict__) or None
        )
        self.fitted = False
        self._feat_columns: list[str] = []
        self.metrics_: Dict[str, Any] = {}

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series]) -> Dict[str, Any]:
        mask = eval_slice(self.spec.slice, X)
        Xs, ys = X.loc[mask], (y.loc[mask] if y is not None else None)
        if Xs.shape[0] == 0:
            self.metrics_ = {"status": "skipped (no rows matched slice)"}
            return self.metrics_

        # NEW: encode features (store columns for predict-time alignment)
        Xs_feat, cols = _encode_features(Xs, ref_columns=None)
        self._feat_columns = cols

        self.metrics_ = self.model.fit(Xs_feat.values, ys.to_numpy() if hasattr(ys, "to_numpy") else ys)
        self.fitted = True
        return self.metrics_

    def predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        mask = eval_slice(self.spec.slice, X)
        N = len(X)
        if not self.fitted:
            raise RuntimeError(f"Expert {self.spec.id} not fitted yet.")

        Xs = X.loc[mask]
        Xs_feat, _ = _encode_features(Xs, ref_columns=self._feat_columns)  # align to train columns

        preds_raw = self.model.predict(Xs_feat.values)
        # align to all rows (unchanged below)
        outputs = {}
        for k, arr in preds_raw.items():
            if arr.ndim == 1:
                out = np.zeros(N, dtype=float)
            else:
                out = np.zeros((N,) + arr.shape[1:], dtype=float)
            out[mask] = arr
            outputs[k] = out
        outputs["mask"] = mask.astype(int)
        return outputs

    def provenance(self) -> Dict[str, Any]:
        return {
            "id": self.spec.id,
            "family": self.spec.family,
            "mode": self.spec.mode,
            "target": self.spec.target,
            "features": self.spec.features,
            "params": self.spec.params,
            "quantum": (self.spec.quantum and self.spec.quantum.__dict__) or None,
            "metrics": self.metrics_,
        }


# ----------------------------
# ExpertBundle
# ----------------------------

class ExpertBundle:
    """
    Orchestrates all experts for a dataset ruleset.
    """

    def __init__(self, dataset_cfg: DatasetConfig):
        self.cfg = dataset_cfg
        self.experts: List[Expert] = [Expert(spec) for spec in dataset_cfg.experts]

    def fit_all(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Dict[str, np.ndarray]:
        """
        Fit all experts on their slices. Returns dict of standardized outputs (OOF/VAL) aligned to rows.
        """
        stacked: Dict[str, np.ndarray] = {}
        for ex in self.experts:
            metrics = ex.fit(X, y)
            print(f"[fit_all] Expert {ex.spec.id}: {metrics}")
            # after fitting, get outputs on train set (OOF or direct preds)
            try:
                outputs = ex.predict(X)
            except Exception as e:
                print(f"[fit_all] Expert {ex.spec.id} predict failed: {e}")
                continue
            for k, arr in outputs.items():
                stacked[f"{ex.spec.id}:{k}"] = arr
        return stacked

    def predict_all(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Run predict for all experts; returns dict of standardized outputs aligned to rows.
        """
        stacked: Dict[str, np.ndarray] = {}
        for ex in self.experts:
            outputs = ex.predict(X)
            for k, arr in outputs.items():
                stacked[f"{ex.spec.id}:{k}"] = arr
        return stacked

    def provenance(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.cfg.dataset_id,
            "loader": self.cfg.loader,
            "experts": [ex.provenance() for ex in self.experts],
        }
