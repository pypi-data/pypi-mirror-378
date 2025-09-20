# config.py
"""
Config schema & loaders (dataset/use-case centric, slice-defined experts).

Core ideas
----------
- Experts are *dataset slices* (sub-parts), not problem types.
- Each expert chooses a model *family* (Regression, Classification, Clustering, Anomaly, Generative)
  and a *mode* ("classical" or "quantum").
- Integration config declares how to fuse expert outputs.

What's new (dynamic configs)
----------------------------
- Users can ship a **config.json / .yaml** with any number of datasets.
- `load_user_config(path_or_dict)` parses & validates into `DatasetConfig` objects.
- `loader` can be:
    * CSV spec: {"kind":"csv","path":"data/file.csv","target":"label_col" (optional)}
      -> internally encoded as "__csv__:<abs_path>::<target>"
    * Dotted path: "mypkg.mymodule:my_loader_fn" (returns (X_df, y_series|None))
    * Short name registered by the application (e.g., examples in main.py)

Backwards compatible:
- Keeps example `DATASETS` for dev/tests.
- `get_dataset_config()` still works on the in-repo examples.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional, Union
import re
import json
import pathlib

# -----------------------
# Enumerations / Aliases
# -----------------------

Family = Literal["regression", "classification", "clustering", "anomaly", "generative"]
Mode = Literal["classical", "quantum"]

# Keys experts can emit (standardized across families). Integrator may select any subset.
# NOTE: Keep this in sync with family implementations.
STACKABLE_KEYS_WHITELIST: Dict[str, set[str]] = {
    "regression": {"pred", "q05", "q95", "mask"},
    "classification": {"proba", "proba_pos", "mask"},
    "clustering": {"soft", "dist", "labels", "mask"},
    "anomaly": {"score", "mask"},
    "generative": {"aug_stats", "mask"},
}

# -----------------------
# Slice DSL (light guard)
# -----------------------
# We use a permissive but *safe* DSL for row filtering. It is intentionally simple and
# will be parsed/evaluated safely in base.py. Here we only sanity-check characters.
_SLICE_ALLOWED = re.compile(r"^(all|[a-zA-Z0-9_ \t\-\+\*/<>=!():'\",.\[\]\{\}]+)$")


def _validate_slice_expr(expr: str) -> None:
    if expr.strip().lower() == "all":
        return
    if not _SLICE_ALLOWED.match(expr):
        raise ValueError(
            f"Slice expression contains disallowed characters: {expr!r}. "
            "Use simple comparisons, logical and/or, parentheses. "
            "Membership like `x in {...}` is handled by the safe parser."
        )


# -----------------------
# Dataclasses
# -----------------------

@dataclass
class QuantumSpec:
    backend: str = "aer"             # e.g., "aer", "lightning", "braket", "default.qubit"
    n_qubits: int = 4
    encoding: str = "angle"          # "angle" | "amplitude" | "qkernel" | "pauli"
    shots: int = 2048
    ansatz: str = "hardware_efficient"  # "hardware_efficient" | "qaoa" | "ucc" | "custom"
    max_depth: int = 3
    seed: Optional[int] = 42
    # room for backend-specific kwargs
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExpertSpec:
    """
    A single expert = one slice of the dataset + one family + one mode.
    """
    id: str
    slice: str                         # DSL or 'all'
    family: Family
    mode: Mode                         # "classical" or "quantum"
    target: Optional[str]              # label column or None (unsupervised)
    features: List[str]                # recipe names to apply for this expert
    params: Dict[str, Any] = field(default_factory=dict)  # family/model params
    quantum: Optional[QuantumSpec] = None                 # required if mode == "quantum"

    # OPTIONAL: Which outputs from this expert are intended for stacking.
    # If None, integrator will rely on integration.include at the dataset level.
    expose: Optional[List[str]] = None

    def validate(self) -> None:
        if not self.id or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.id):
            raise ValueError(f"Expert id must be a valid identifier: {self.id!r}")
        _validate_slice_expr(self.slice)
        if self.mode == "quantum" and self.quantum is None:
            raise ValueError(f"Expert {self.id}: mode='quantum' requires a 'quantum' spec.")
        # sanity: known stackable keys
        if self.expose:
            allowed = STACKABLE_KEYS_WHITELIST[self.family] | {"mask"}
            unknown = [k for k in self.expose if k not in allowed and not k.endswith(":*")]
            if unknown:
                raise ValueError(f"Expert {self.id}: unknown expose keys {unknown} for family={self.family}.")


@dataclass
class IntegrationConfig:
    strategy: Literal["stacking", "weighted", "blending"] = "stacking"
    meta: Dict[str, Any] = field(default_factory=lambda: {"type": "logistic"})  # or {"type":"linear"} for regression
    include: List[str] = field(default_factory=list)  # e.g., ["exp_a:proba_pos","exp_b:pred","exp_*:score","exp_*:mask"]
    calibration: Optional[Dict[str, Any]] = field(default_factory=lambda: {"type": "isotonic"})
    # Optional budget/early-exit policy (handled in integrate/base)
    budget_policy: Optional[Dict[str, Any]] = None

    def validate(self, expert_ids: List[str]) -> None:
        # Accept wildcards in include; light check for format "<exp_id or *>:<key>"
        pat = re.compile(r"^(?P<exp>[\w\*\?]+):(?P<key>[\w\*\?]+)$")
        for token in self.include:
            if not pat.match(token):
                raise ValueError(
                    f"Integration.include token {token!r} must look like 'exp_id:key' or use wildcards."
                )


@dataclass
class DatasetConfig:
    dataset_id: str
    loader: str                              # to be resolved at runtime (csv spec | dotted path | short name)
    feature_recipes: List[str]               # global recipe names available
    experts: List[ExpertSpec]
    integration: IntegrationConfig

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("dataset_id required")
        if not self.loader or not isinstance(self.loader, str):
            raise ValueError(f"loader must be a non-empty string (csv spec | dotted path | short name), got {self.loader!r}")
        if not self.experts:
            raise ValueError(f"{self.dataset_id}: must define at least one expert")
        ids = set()
        for ex in self.experts:
            ex.validate()
            if ex.id in ids:
                raise ValueError(f"{self.dataset_id}: duplicate expert id {ex.id!r}")
            ids.add(ex.id)
        self.integration.validate([ex.id for ex in self.experts])


# -----------------------
# Dynamic Config Loading
# -----------------------

JsonLike = Union[str, pathlib.Path, dict]


def _coerce_dataset_config(key: str, raw: dict) -> DatasetConfig:
    """
    Turn a raw dict (from JSON/YAML) into a validated DatasetConfig.
    - Normalizes 'loader':
        * CSV dict {"kind":"csv","path":"...","target":"..."} → "__csv__:<abs_path>::<target>"
        * String keeps as-is (dotted path or short name)
    """
    raw = dict(raw)  # shallow copy

    # 1) Normalize loader
    loader_raw = raw.get("loader")
    if isinstance(loader_raw, dict):
        kind = loader_raw.get("kind")
        if kind != "csv":
            raise ValueError(f"{key}: unsupported loader kind {kind!r}. Use {{'kind':'csv',...}} or a string.")
        p = str(pathlib.Path(loader_raw["path"]).expanduser().resolve())
        tgt = loader_raw.get("target", "")
        raw["loader"] = f"__csv__:{p}::{tgt}"
    elif isinstance(loader_raw, str):
        # accept dotted path or short name; runtime will resolve
        pass
    else:
        raise ValueError(f"{key}: 'loader' must be a csv spec or a string (short name / dotted path).")

    # 2) Experts
    ex_specs: List[ExpertSpec] = []
    for ex in raw.get("experts", []):
        qspec = None
        if ex.get("mode") == "quantum" and ex.get("quantum") is not None:
            qspec = QuantumSpec(**ex["quantum"])
        ex_specs.append(ExpertSpec(
            id=ex["id"],
            slice=ex["slice"],
            family=ex["family"],
            mode=ex["mode"],
            target=ex.get("target"),
            features=ex.get("features", []),
            params=ex.get("params", {}),
            quantum=qspec,
            expose=ex.get("expose"),
        ))

    # 3) Integration
    integ_raw = raw.get("integration") or {}
    integ = IntegrationConfig(
        strategy=integ_raw.get("strategy", "stacking"),
        meta=integ_raw.get("meta", {"type": "logistic"}),
        include=integ_raw.get("include", []),
        calibration=integ_raw.get("calibration", {"type": "isotonic"}),
        budget_policy=integ_raw.get("budget_policy"),
    )

    cfg = DatasetConfig(
        dataset_id=key,
        loader=raw["loader"],
        feature_recipes=raw.get("feature_recipes", []),
        experts=ex_specs,
        integration=integ,
    )
    cfg.validate()
    return cfg


def load_user_config(config: JsonLike) -> Dict[str, DatasetConfig]:
    """
    Load a user-provided config (json/yaml path or already-loaded dict)
    → mapping: {dataset_id: DatasetConfig}
    """
    if isinstance(config, dict):
        blob = config
    else:
        path = pathlib.Path(config)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".yaml", ".yml"):
            try:
                import yaml  # optional dependency
            except Exception as e:
                raise RuntimeError("YAML config requires PyYAML. Install with: pip install pyyaml") from e
            blob = yaml.safe_load(text)
        else:
            blob = json.loads(text)

    if "datasets" not in blob or not isinstance(blob["datasets"], dict):
        raise ValueError("Config must have a top-level 'datasets' object mapping ids → dataset specs.")

    out: Dict[str, DatasetConfig] = {}
    for key, raw in blob["datasets"].items():
        out[key] = _coerce_dataset_config(key, raw)
    return out


# -----------------------
# Example Datasets (for immediate use / dev)
# -----------------------

DATASETS: Dict[str, DatasetConfig] = {
    "retail_churn_v1": DatasetConfig(
        dataset_id="retail_churn_v1",
        loader="load_retail_churn",
        feature_recipes=[
            "num_impute_median", "onehot(min_freq=10)", "standard_scale", "pca(16)"
        ],
        experts=[
            ExpertSpec(
                id="exp_apac_premium",
                slice="region=='APAC' and spend_q>=0.8",
                family="classification",
                mode="classical",
                target="churn",
                features=["numeric", "categorical", "pca(16)"],
                params={"model": "hgb", "calibrate": True},
                expose=["proba_pos", "mask"]
            ),
            ExpertSpec(
                id="exp_longtail",
                slice="sku_freq<=5",
                family="anomaly",
                mode="classical",
                target=None,
                features=["numeric"],
                params={"model": "isoforest", "contamination": 0.05},
                expose=["score", "mask"]
            ),
            ExpertSpec(
                id="exp_quantum_kernel",
                slice="all",
                family="classification",
                mode="quantum",
                target="churn",
                features=["numeric", "pca(8)"],
                params={"model": "qsvc"},
                quantum=QuantumSpec(
                    backend="aer",
                    n_qubits=8,
                    encoding="qkernel",
                    shots=2048,
                    ansatz="hardware_efficient",
                    max_depth=3,
                    seed=42,
                ),
                expose=["proba_pos", "mask"]
            ),
        ],
        integration=IntegrationConfig(
            strategy="stacking",
            meta={"type": "logistic"},
            include=[
                "exp_apac_premium:proba_pos",
                "exp_longtail:score",
                "exp_quantum_kernel:proba_pos",
                "exp_*:mask"
            ],
            calibration={"type": "isotonic"}
        ),
    ),

    "sensor_forecast_v2": DatasetConfig(
        dataset_id="sensor_forecast_v2",
        loader="load_sensor_panel",  # alias resolved by the app (e.g., main.py)
        feature_recipes=[
            "lags([1,2,7,28])", "rolling([7,28])", "calendar", "scale_robust", "pca(6)"
        ],
        experts=[
            ExpertSpec(
                id="exp_day",
                slice="hour>=8 and hour<=20",
                family="regression",
                mode="classical",
                target="y",
                features=["lags", "rolling", "calendar"],
                params={"model": "hgb"},
                expose=["pred", "mask"]
            ),
            ExpertSpec(
                id="exp_night_q",
                slice="hour<8 or hour>20",
                family="regression",
                mode="quantum",
                target="y",
                features=["lags", "rolling", "pca(6)"],
                params={"model": "vqr"},
                quantum=QuantumSpec(
                    backend="lightning",
                    n_qubits=6,
                    encoding="angle",
                    shots=4096,
                    ansatz="hardware_efficient",
                    max_depth=3,
                    seed=7,
                ),
                expose=["pred", "mask"]
            ),
            ExpertSpec(
                id="exp_spikes",
                slice="all",
                family="anomaly",
                mode="classical",
                target=None,
                features=["lags", "rolling"],
                params={"model": "oneclasssvm"},
                expose=["score", "mask"]
            ),
        ],
        integration=IntegrationConfig(
            strategy="stacking",
            meta={"type": "linear"},
            include=["exp_day:pred", "exp_night_q:pred", "exp_spikes:score", "exp_*:mask"],
            calibration=None
        ),
    ),
}


# -----------------------
# Helpers (dev)
# -----------------------

def get_dataset_config(key: str) -> DatasetConfig:
    """Return a *validated* DatasetConfig by key (from in-repo examples)."""
    if key not in DATASETS:
        raise KeyError(f"Unknown dataset key {key!r}. Available: {list(DATASETS)}")
    cfg = DATASETS[key]
    cfg.validate()
    return cfg


def snapshot_config() -> Dict[str, Any]:
    """Return a JSON-serializable snapshot of all example configs (post-validate)."""
    snap: Dict[str, Any] = {}
    for k, v in DATASETS.items():
        v.validate()
        snap[k] = asdict(v)
    return snap


# Validate eagerly at import-time for the built-in examples (fail fast in dev; harmless in prod)
for _key in list(DATASETS.keys()):
    _ = get_dataset_config(_key)
