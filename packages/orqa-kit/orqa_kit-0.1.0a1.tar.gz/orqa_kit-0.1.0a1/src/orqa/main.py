# main.py
"""
Orchestrator & CLI

Modes:
  - train   : load dataset → fit experts → stack → train integrator → persist artifacts
  - predict : load artifacts → run experts → stack → integrator → save predictions
  - trace   : inspect artifacts (experts' provenance, integrator features/weights)

Examples:
  python main.py --dataset retail_churn_v1 --mode train
  python main.py --dataset retail_churn_v1 --mode predict --input data/new_batch.csv
  python main.py --dataset sensor_forecast_v2 --mode trace
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
from dataclasses import asdict
from joblib import dump, load

# Project modules
from .config import DatasetConfig  # :contentReference[oaicite:8]{index=8}
from .base import ExpertBundle, eval_slice                # :contentReference[oaicite:9]{index=9}
from .integrate import IntegrationModel       # :contentReference[oaicite:10]{index=10}


# ---------------------------
# Data loading registry
# ---------------------------

def load_retail_churn() -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Demo loader: expects data/retail_churn_v1.csv with a 'churn' label column.
    Replace with your real pipeline or implement your own loader function.
    """
    path = Path("data/retail_churn_v1.csv")
    if not path.exists():
        raise FileNotFoundError(f"Expected dataset at {path.resolve()}. Provide your own loader or CSV.")
    df = pd.read_csv(path)
    y = df.pop("churn") if "churn" in df.columns else None
    return df, y

def load_sensor_forecast_v2() -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Demo loader: expects data/sensor_forecast_v2.csv with a 'target' column.
    """
    path = Path("data/sensor_forecast_v2.csv")
    if not path.exists():
        raise FileNotFoundError(f"Expected dataset at {path.resolve()}. Provide your own loader or CSV.")
    df = pd.read_csv(path)
    y = df.pop("target") if "target" in df.columns else None
    return df, y

def load_sensor_panel():
    """Alias: config may reference 'load_sensor_panel'; reuse the same CSV."""
    return load_sensor_forecast_v2()

# Map string names in config.loader → function objects
BUILTIN_LOADERS = {
    "load_retail_churn": load_retail_churn,
    "load_sensor_forecast_v2": load_sensor_forecast_v2,
    "load_sensor_panel": load_sensor_panel,
}

def resolve_loader(loader_str: str):
    import pandas as pd, pathlib, importlib
    if loader_str.startswith("__csv__:"):
        _, spec = loader_str.split("__csv__:", 1)
        path_str, _, target = spec.partition("::")
        p = pathlib.Path(path_str)
        if not p.exists():
            raise FileNotFoundError(f"CSV loader: file not found → {p}")
        def _csv_loader():
            df = pd.read_csv(p)
            if target:
                if target not in df.columns:
                    raise KeyError(f"CSV loader: target column '{target}' not found in {p}")
                y = df.pop(target)
            else:
                y = None
            return df, y
        return _csv_loader
    if loader_str in BUILTIN_LOADERS:
        return BUILTIN_LOADERS[loader_str]
    if ":" in loader_str:
        mod, fn = loader_str.split(":", 1)
        try:
            m = importlib.import_module(mod)
            return getattr(m, fn)
        except Exception as e:
            raise ImportError(f"Failed to import loader '{loader_str}': {e}") from e
    raise ValueError(f"Unknown loader '{loader_str}'. Use a CSV spec, a built-in name, or a dotted path.")

# ---------------------------
# Artifact helpers
# ---------------------------

def artifact_dir(root: Optional[str], dataset_id: str) -> Path:
    base = Path(root) if root else Path("artifacts") / dataset_id
    base.mkdir(parents=True, exist_ok=True)
    return base

def save_artifacts(outdir: Path,
                   bundle: ExpertBundle,
                   integrator: IntegrationModel,
                   cfg: DatasetConfig,
                   columns_meta: Dict[str, Any],
                   train_metrics: Dict[str, Any]):
    dump(bundle, outdir / "experts.joblib")
    dump(integrator, outdir / "integrator.joblib")
    (outdir / "config.json").write_text(json.dumps(asdict(cfg), indent=2))
    (outdir / "provenance.json").write_text(json.dumps(bundle.provenance(), indent=2))
    (outdir / "integration_columns.json").write_text(json.dumps(columns_meta, indent=2))
    (outdir / "train_metrics.json").write_text(json.dumps(train_metrics, indent=2))


def load_artifacts(indir: Path) -> Tuple[ExpertBundle, IntegrationModel, Dict[str, Any]]:
    bundle: ExpertBundle = load(indir / "experts.joblib")
    integrator: IntegrationModel = load(indir / "integrator.joblib")
    columns_meta = json.loads((indir / "integration_columns.json").read_text()) if (indir / "integration_columns.json").exists() else {}
    return bundle, integrator, columns_meta


# ---------------------------
# Core routines
# ---------------------------

def run_validate(cfg: DatasetConfig) -> int:
    """
    Validation-only path:
      - Resolve loader (CSV/dotted/built-in)
      - Load a small sample (or full CSV if small)
      - Check target column for supervised experts
      - Evaluate each expert slice → coverage on the sample
      - Light-check integration.include tokens
    Returns 0 on success, >0 if problems found.
    """
    problems = 0

    # Resolve & load a small sample
    try:
        loader_fn = resolve_loader(cfg.loader)
    except Exception as e:
        print(f"[validate] Loader resolution failed for {cfg.loader!r}: {e}", file=sys.stderr)
        return 1

    try:
        X, y = loader_fn()
    except Exception as e:
        print(f"[validate] Loader execution failed: {e}", file=sys.stderr)
        return 1

    # If it's a big frame, subsample for quick validation
    if isinstance(X, pd.DataFrame) and len(X) > 2000:
        X = X.sample(2000, random_state=42).reset_index(drop=True)
        if y is not None and len(y) > 2000:
            y = y.iloc[X.index].reset_index(drop=True)

    print("=== VALIDATE: DATASET ===")
    print(cfg.dataset_id)
    print(f"[validate] rows={len(X)}, cols={list(X.columns)}")
    if y is not None:
        print(f"[validate] target provided (len={len(y)})")
    else:
        print("[validate] target=None (unsupervised config is OK if all experts are unsupervised)")

    # Check expert specs
    print("\n=== VALIDATE: EXPERTS ===")
    for ex in cfg.experts:
        print(f"- {ex.id}: family={ex.family}, mode={ex.mode}, slice={ex.slice!r}")
        # Supervised target present?
        if ex.target:
            if y is None and ex.target not in X.columns:
                print(f"  [error] Supervised expert requires target '{ex.target}', "
                      f"but loader returned y=None and column not found in X.", file=sys.stderr)
                problems += 1
            elif y is None and ex.target in X.columns:
                print(f"  [warn] Target '{ex.target}' found in X columns; "
                      f"loader should pop it and return as y to avoid leakage.")
            elif y is not None:
                # OK (we can't verify name equality if loader popped it without keeping the name)
                pass

        # Slice evaluation coverage
        try:
            mask = eval_slice(ex.slice, X)
            cov = float(mask.mean()) if len(mask) else 0.0
            print(f"  [ok] slice coverage on sample: {cov:.1%} (matched {int(mask.sum())}/{len(mask)})")
            if mask.sum() == 0:
                print(f"  [warn] slice matched 0 rows in sample; check expression/columns.")
        except Exception as e:
            print(f"  [error] slice evaluation failed: {e}", file=sys.stderr)
            problems += 1

        # Expose keys are validated by config schema; nothing more to do here.

    # Integration include tokens are already pattern-validated in config,
    # but we can echo them for clarity.
    print("\n=== VALIDATE: INTEGRATION ===")
    print(f"strategy={cfg.integration.strategy}, meta={cfg.integration.meta}")
    print("include=" + ", ".join(cfg.integration.include) if cfg.integration.include else "include=(empty)")
    if not cfg.integration.include:
        print("  [warn] integration.include is empty; integrator may have no features.")

    # Summary
    print("\n=== VALIDATE: SUMMARY ===")
    if problems == 0:
        print("[validate] OK: configuration and loader look sane.")
    else:
        print(f"[validate] Completed with {problems} problem(s). See messages above.", file=sys.stderr)

    return 0 if problems == 0 else 2

def run_train(cfg: DatasetConfig, outdir: Path):
    # 1) Load dataset
    # run_train(...)
    loader_fn = resolve_loader(cfg.loader)
    if loader_fn is None:
        raise ValueError(
            f"Loader {cfg.loader!r} could not be resolved. Use a CSV spec, a built-in name, or a dotted path."
        )


    X, y = loader_fn()
    if y is None:
        print("[warn] No target column found; training integrator without supervision is not supported.", file=sys.stderr)
        print("       Provide a target column in your loader or adjust workflow.", file=sys.stderr)
        sys.exit(2)

    # 2) Build experts & fit (produces row-aligned stacks)
    bundle = ExpertBundle(cfg)
    stacked = bundle.fit_all(X, y)  # dict: "exp_id:key" -> ndarray  :contentReference[oaicite:11]{index=11}

    # 3) Train integrator
    integ_cfg = asdict(cfg.integration)
    integrator = IntegrationModel(integ_cfg)  # :contentReference[oaicite:12]{index=12}
    integrator.fit(stacked, y.to_numpy() if hasattr(y, "to_numpy") else np.asarray(y))

    # 4) Persist artifacts
    columns_meta = {
        "selected_columns": integrator.columns_,
        "include_patterns": integ_cfg.get("include", []),
        "strategy": integ_cfg.get("strategy", "stacking"),
        "meta": integ_cfg.get("meta", {}),
    }
    train_metrics = {"integration": {"task": getattr(integrator, "task_", None)}}
    save_artifacts(outdir, bundle, integrator, cfg, columns_meta, train_metrics)

    # 5) Report
    print(f"[train] Saved artifacts to: {outdir.resolve()}")
    print(f"[train] Experts: {len(bundle.experts)}; Integration features: {len(integrator.columns_)}")


def run_predict(cfg: DatasetConfig, indir: Path, input_csv: Path, output_csv: Optional[Path]):
    if not (indir / "experts.joblib").exists() or not (indir / "integrator.joblib").exists():
        raise FileNotFoundError(
            f"No artifacts found at {indir}. Train first:\n  python main.py --config {args.config or 'config.json'} "
            f"--dataset {cfg.dataset_id} --mode train"
        )
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")
    X = pd.read_csv(input_csv)

    # Load artifacts
    bundle, integrator, _ = load_artifacts(indir)

    # schema guard (optional but recommended)
    required_cols = set()
    for ex in getattr(bundle, "experts", []):
        cols = getattr(ex, "_feat_columns", None)
        if cols:
            required_cols.update(cols)

    if required_cols:
        overlap = required_cols & set(X.columns)
        coverage = len(overlap) / max(1, len(required_cols))
        if coverage < 0.5:
            missing = sorted(required_cols - set(X.columns))[:12]
            raise ValueError(
                f"Input schema mismatch: only {coverage:.0%} of required columns present. "
                f"Missing (sample): {missing} ..."
            )
        elif coverage < 0.9:
            print(f"[warn] Input schema partial match: {coverage:.0%}; predictions may degrade.", flush=True)


    # Experts → stacked → integrator
    stacked = bundle.predict_all(X)  # :contentReference[oaicite:13]{index=13}
    fused = integrator.predict(stacked)  # {"fused": (N,1 or K), "contrib": ..., "columns": ...}  :contentReference[oaicite:14]{index=14}

    # Package results
    out_df = pd.DataFrame()
    f = fused["fused"]
    if f.ndim == 1 or f.shape[1] == 1:
        out_df["fused"] = f.reshape(-1)
    else:
        for j in range(f.shape[1]):
            out_df[f"fused[{j}]"] = f[:, j]

    # Save or print head
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)
        print(f"[predict] Saved predictions → {output_csv.resolve()}")

    else:
        print(out_df.head())


def run_trace(cfg: DatasetConfig, indir: Path):
    bundle, integrator, columns_meta = load_artifacts(indir)

    print("=== DATASET ===")
    print(cfg.dataset_id)
    print()

    print("=== EXPERTS PROVENANCE ===")
    prov = bundle.provenance()  # per-expert family/mode/metrics  :contentReference[oaicite:15]{index=15}
    print(json.dumps(prov, indent=2))
    print()

    print("=== INTEGRATION CONFIG ===")
    print(json.dumps(asdict(cfg.integration), indent=2))
    print()

    print("=== INTEGRATION FEATURES (selected) ===")
    print(json.dumps(columns_meta, indent=2))
    print()

    print("=== CONTRIBUTIONS ===")
    # Attempt to surface global coefficients/weights if available
    contrib = {"columns": getattr(integrator, "columns_", []), "details": None}
    try:
        # Build a dummy zero-matrix to trigger contribution logic? Not needed; we can use attributes:
        details = {"task": getattr(integrator, "task_", None)}
        # For weighted strategies
        if isinstance(getattr(integrator, "model_", None), tuple) and integrator.model_[0].startswith("weighted"):
            details["weights"] = integrator.model_[1].tolist()
        else:
            # Linear/logistic coef
            if hasattr(integrator.model_, "coef_"):
                details["coef"] = getattr(integrator.model_, "coef_").ravel().tolist()
        contrib["details"] = details
    except Exception as e:
        contrib["details"] = {"error": str(e)}
    print(json.dumps(contrib, indent=2))


# ---------------------------
# CLI
# ---------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Modular Multi-Expert Orchestrator")
    p.add_argument("--config", type=str, help="Path to config.json|yaml (overrides built-ins)")
    p.add_argument("--dataset", required=True, help="Dataset id (must exist in the config)")
    p.add_argument(
        "--mode",
        required=True,
        choices=["train", "predict", "trace", "validate"],  # ← added "validate"
    )
    p.add_argument("--input", type=str, help="CSV path for predict mode")
    p.add_argument("--output", type=str, help="Where to save predictions (CSV)")
    p.add_argument("--artifacts", type=str, help="Artifacts directory (defaults to artifacts/<dataset>)")
    return p.parse_args()

def main():
    args = parse_args()

    if args.config:
        from .config import load_user_config
        cfg_map = load_user_config(args.config)
        if args.dataset not in cfg_map:
            raise KeyError(f"Dataset '{args.dataset}' not found in {args.config}. Available: {list(cfg_map)}")
        cfg = cfg_map[args.dataset]
    else:
        from .config import get_dataset_config
        cfg = get_dataset_config(args.dataset)

    if args.mode == "train":
        outdir = artifact_dir(args.artifacts, cfg.dataset_id)
        run_train(cfg, outdir)

    elif args.mode == "predict":
        if not args.input:
            raise ValueError("--input CSV is required for predict mode")
        indir = artifact_dir(args.artifacts, cfg.dataset_id)
        run_predict(cfg, indir, Path(args.input), Path(args.output) if args.output else None)

    elif args.mode == "trace":
        indir = artifact_dir(args.artifacts, cfg.dataset_id)
        run_trace(cfg, indir)

    elif args.mode == "validate":
        # No artifacts needed, we just introspect the loader + slices
        sys.exit(run_validate(cfg))

if __name__ == "__main__":
    main()
