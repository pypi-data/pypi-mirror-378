# ORQA Documentation

**Open Research on Quantum Algorithms**
**Version:** 0.1.0-alpha
**Status:** This is an **alpha** release intended for testing and early feedback. Interfaces and defaults may change based on community input.
**Contact:** [connectwithpavan@gmail.com](mailto:connectwithpavan@gmail.com)

---

## Introduction

**ORQA** is a modular AI and ML framework built around **expert models**. Instead of relying on a single global model, ORQA lets you define **rulesets** that partition data into meaningful slices and assign a specialized **expert** to each slice. Experts can be **classical** or **quantum-inspired**. Their outputs are fused by an **integration model** to produce robust, explainable predictions.

### Key Features

* Unified support for **regression**, **classification**, **clustering**, **anomaly detection**, and **generative** families
* **Dual-mode** learning: classical learners (scikit-learn and compatible) plus quantum-inspired learners (kernel methods, variational circuits)
* **Ruleset-based** expert assignment to target specific data segments
* **Integration layer** for stacking, blending, or weighted fusion of expert outputs
* **CLI** workflows for **train**, **predict**, **trace**, and **validate**

---

## Installation

### From source (local directory)

```bash
python -m pip install -e .
```

### From PyPI (when published)

```bash
python -m pip install orqa-kit
# optional quantum extras when available
python -m pip install "orqa-kit[quantum]"
```

**Python requirement:** 3.9 or newer

---

## Concepts

* **Ruleset:** A declarative filter that selects a slice of your dataset for a given expert, for example `region == "APAC"` or `age > 50`.
* **Expert:** A model instance from a specific **family** (regression, classification, clustering, anomaly, generative) in a chosen **mode** (classical or quantum).
* **Integration model:** A meta-learner that combines exposed outputs from experts into a final prediction.
* **Config-driven orchestration:** Experiments are defined in a JSON config and executed via CLI or Python.

---

## Package Layout

```
orqa/
  anomaly_detection.py   # Anomaly DetectionFamily (classical and quantum-inspired)
  base.py                # Expert, ExpertBundle, shared utilities
  classification.py      # ClassificationFamily
  clustering.py          # ClusteringFamily
  config.py              # Config loading and validation
  generative.py          # GenerativeFamily
  integrate.py           # Integration strategies and meta models
  main.py                # CLI orchestration entry (also exposed via console script)
  cli.py                 # Console script binding: `orqa`
  _version.py            # Version string for the package
  __init__.py            # Public API surface
```

---

## Configuration

Experiments are defined in a single JSON file. Each top-level key is a dataset profile. ORQA uses **loader** strings to specify data sources and targets.

### Loader notation

* `__csv__:<path>::<target>` loads a CSV at `<path>` and uses `<target>` as the label for supervised tasks.

### Example `config.json`

```json
{
  "my_ds": {
    "dataset_id": "my_ds",
    "loader": "__csv__:data/retail_churn_v1.csv::churn",
    "feature_recipes": ["numeric", "categorical"],
    "experts": [
      {
        "id": "exp_all",
        "slice": "all",
        "family": "classification",
        "mode": "classical",
        "target": "churn",
        "features": ["numeric", "categorical"],
        "params": { "model": "hgb", "calibrate": true },
        "expose": ["proba_pos", "mask"]
      }
    ],
    "integration": {
      "strategy": "stacking",
      "meta": { "type": "logistic" },
      "include": ["exp_all:proba_pos", "exp_all:mask"],
      "calibration": { "type": "isotonic" }
    }
  }
}
```

---

## Model Families

### Regression

**Classical:** HistGradientBoostingRegressor, LinearRegression, RandomForestRegressor
**Quantum-inspired:** Quantum Kernel Ridge Regression, Variational Quantum Regressor

**Outputs**

```python
{"pred": N_by_1, "q05": N_by_1, "q95": N_by_1}
```

**Minimal example**

```python
from orqa.regression import RegressionFamily

reg = RegressionFamily(mode="classical", params={"model": "hgb"})
reg.fit(X_train, y_train)
out = reg.predict(X_test)
print(out["pred"][:5])
```

---

### Classification

**Classical:** HistGradientBoostingClassifier, LogisticRegression, Calibrated XGBoost
**Quantum-inspired:** QSVC, Variational Quantum Classifier

**Outputs**

```python
{"proba": N_by_K, "proba_pos": N_by_1}
```

**Minimal example**

```python
from orqa.classification import ClassificationFamily

clf = ClassificationFamily(mode="classical", params={"model": "hgb"})
clf.fit(X_train, y_train)
out = clf.predict(X_test)
print(out["proba_pos"][:5])
```

---

### Clustering

**Classical:** KMeans, GaussianMixture
**Quantum-inspired:** Quantum KMeans via kernel or swap-test-like embeddings

**Outputs**

```python
{"soft": N_by_C, "dist": N_by_C, "labels": N_by_1}
```

**Minimal example**

```python
from orqa.clustering import ClusteringFamily

clu = ClusteringFamily(mode="classical", params={"model": "kmeans", "n_clusters": 3})
clu.fit(X_train)
out = clu.predict(X_test)
print(out["labels"][:10])
```

---

### Anomaly Detection

**Classical:** IsolationForest, OneClassSVM, LocalOutlierFactor
**Quantum-inspired:** Quantum kernel one-class methods, variational energy-based scores

**Outputs**

```python
{"score": N_by_1}
```

**Minimal example**

```python
from orqa.anomaly_detection import AnomalyDetectionFamily

ano = AnomalyDetectionFamily(mode="classical", params={"model": "isoforest"})
ano.fit(X_train)
out = ano.predict(X_test)
print(out["score"][:5])
```

---

### Generative

**Classical:** Gaussian Copula, Variational Autoencoder, TimeGAN
**Quantum-inspired:** Quantum Circuit Born Machine, hybrid VAE with quantum encoder

**Outputs**

```python
{"aug_stats": {"n_samples": int, "feature_summary": dict}}
```

**Minimal example**

```python
from orqa.generative import GenerativeFamily

gen = GenerativeFamily(mode="classical", params={"model": "vae"})
gen.fit(X_train)
out = gen.predict(X_test)
print(out["aug_stats"])
```

---

## Orchestration and CLI

The console script is exposed as `orqa`. You can also call `python -m orqa.main` directly.

### Validate

```bash
orqa --config config.json --dataset my_ds --mode validate
```

### Train

```bash
orqa --config config.json --dataset my_ds --mode train
```

### Predict

```bash
orqa --config config.json --dataset my_ds --mode predict --input data/new.csv --output preds.csv
```

### Trace

```bash
orqa --config config.json --dataset my_ds --mode trace
```

---

## Programmatic Workflow

```python
from orqa.config import load_config
from orqa.main import run

cfg = load_config("config.json")
run(cfg, dataset_id="my_ds", mode="validate")
run(cfg, dataset_id="my_ds", mode="train")
```

---

## Data and Features

* **Feature recipes:** `["numeric", "categorical"]` represents standard preprocessing pipelines.
* **Targets:** For supervised tasks, set `target` in each expert configuration and in the loader string.
* **Slicing:** Set `slice` to `"all"` for global experts or provide an expression that ORQA can evaluate against your dataframe.

---

## Integration Strategies

* **stacking:** Train a meta-model on expert outputs.
* **weighted:** Combine expert outputs using learned or fixed weights.
* **blending:** Merge experts using simple convex combinations.

Expose the necessary expert outputs using the `expose` list and include them under `integration.include`.

---

## Persistence

* Families may provide `save(path)` and `load(path)` methods when persistence is implemented for the selected model.
* For reproducibility, store the full configuration file alongside saved models.

---

## Logging and Reproducibility

* Use a fixed random seed for experiments when possible.
* Keep dataset snapshots and `config.json` under version control.
* Write predictions to CSV with a timestamped name when running batch jobs.

---

## Limitations in Alpha

* Quantum-inspired backends may require optional dependencies and a compatible environment.
* Persistence APIs may be incomplete for some families and models.
* Integration strategies are stable, but the set of exposed expert outputs can expand in future versions.
* Public API surface is subject to change based on feedback from early users.

---

## License

**Polyform Noncommercial 1.0.0**. Non-commercial use is permitted. Commercial use requires a separate license.

---

## Support and Feedback

* Email: [connectwithpavan@gmail.com](mailto:connectwithpavan@gmail.com)
* Please share bugs, feature requests, and suggestions. This alpha is specifically intended to incorporate community recommendations.