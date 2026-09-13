# Customer Churn Analytics — Credit Card Customers

## Project Overview

End-to-end Business Data Analytics analysis of the **Credit Card Customers** dataset by **Sakshi Goyal**. This project classifies churn status in a historical customer snapshot and connects predictive analysis to a prospective retention experiment.

Dataset: [Kaggle — Credit Card Customers](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers/data). Download the source separately; the original CSV is deliberately not redistributed.

## Business Analytics Framework

Business → EDA → Features → Models → Advanced ML → Causal Action

**Predict → Value → Test → Monitor.** Prediction identifies associations; illustrative costs support a teaching decision rule; randomized experiments must establish whether a retention action works.

## Dataset

10,127 customers; target `Attrition_Flag` maps `Attrited Customer` to 1 and `Existing Customer` to 0. There are 1,627 churn cases (16.07%). Customer identifiers and two source Naive Bayes prediction columns are excluded from predictors.

This is a historical snapshot. A verified scoring timestamp, label horizon, feature cutoff, churn event time, treatment assignment and censoring time are unavailable. Even leakage-controlled random splits cannot establish future operational performance.

## Methodology

- Validate schema, ranges, missingness and unique customer keys before training-only EDA.
- Stratified train/validation/test split: 6,076 / 2,025 / 2,026 customers, with disjoint IDs and seed 42.
- Engineer snapshot ratios; fit imputation, scaling and categorical encoding inside cross-validation pipelines. Use training data only for CV and Random Forest hyperparameter search; compare baselines, imbalance handling, Random Forest, XGBoost and LightGBM.
- Select the predictive model and cost threshold using validation data. Freeze both before held-out test evaluation; no test tuning or refitting calibration on test.
- Evaluate discrimination, confusion counts, Brier score, quantile-bin calibration and 500 bootstrap replicates. Calibration here is a diagnostic, not a fitted probability correction.
- Explain the tuned Random Forest with positive-class TreeSHAP; propose a prospective randomized retention experiment and monitoring.

## Key Results

Final predictive model: **LightGBM benchmark**. Independently recomputed on the frozen test predictions:

| Metric | Verified value |
|---|---:|
| Average Precision | 0.971949039 |
| ROC-AUC | 0.993049441 |
| Recall | 96.6258% |
| Precision | 77.5862% |
| F1 | 0.860655738 |
| Balanced Accuracy | 0.956364128 |
| Brier Score | 0.024354961 |
| Frozen validation threshold | 0.271024392128117 |
| TP / FP / FN / TN | 315 / 91 / 11 / 1609 |
| Illustrative loss: 5 × FN + FP | 146 |

The largest absolute calibration-bin gap has 202 customers: mean score 70.16%, observed churn 55.94%. This is a bin average, not a pointwise probability estimate; the scores are not validated for CLV/ROI calculations.

**Model roles:** LightGBM is the final predictive model selected from model comparison, while the tuned Random Forest is retained as the course-aligned tree model for TreeSHAP explanation. Random Forest SHAP findings describe that model's behavior and must not be interpreted as direct explanations of LightGBM predictions.

## Repository Structure

| Path | Contents |
|---|---|
| [notebook.ipynb](notebook.ipynb) | Final Kaggle-compatible notebook, including freshly executed outputs |
| [outputs/](outputs/) | 12 analytical CSV tables, 17 figures and 2 JSON policy/run records |
| [audit/](audit/) | Original Thai audit, metric checks, source/output snapshots and historical runtime evidence |
| [audit/publication/](audit/publication/) | Latest execution, independent checks, schema/SHAP tests, inventory and publication audit |
| [validation_report.json](validation_report.json) | Latest execution and independent verification summary |
| [results.zip](results.zip) | Compact copy of all final outputs and validation report; excludes source data |
| [scripts/](scripts/) | Reusable execution and independent verification scripts |
| [requirements-notes.md](requirements-notes.md) | Tested environment and local replay instructions |

## Audit and Reproducibility

The final notebook passed a fresh local CPU kernel execution: **57 cells, including all 26 code cells**, with no recorded notebook warnings. Local replay changes only the two Kaggle path constants in a temporary execution copy. The published notebook retains `/kaggle/input/` and `/kaggle/working/`. Hosted Kaggle execution itself has not been repeated here.

See the [final Thai audit](audit/publication/final_audit_th.md), [execution record](audit/publication/execution.json), [independent metrics](audit/publication/independent_metric_checks.csv), and [original audit with provenance notes](audit/audit_report_th.md). Independent recomputation verifies all 2,028 threshold candidates and the frozen policy; maximum metric difference is approximately 1.1e-16. Existing analytical values remain unchanged after cleanup.

Seed 42, source SHA-256, dependency versions, model roles and frozen threshold are recorded in [run_manifest.json](outputs/run_manifest.json). Determinism across every platform or dependency version is not promised. Historical evidence is deliberately preserved and distinguished from the latest publication checks in [audit/README.md](audit/README.md).

## Important Limitations

Historical snapshot; no verified future horizon. Association ≠ causation; SHAP ≠ treatment effect. Uplift and survival behavior are not identifiable from these fields. Teaching decision costs are illustrative, not actual campaign profitability. Retention effectiveness requires a prospective experiment. Correlated predictors can share SHAP attribution; the comparison does not establish statistically significant superiority or an optimal model across all possible searches.

## Running on Kaggle

1. Add the Sakshi Goyal Credit Card Customers dataset to the Kaggle notebook.
2. Import `notebook.ipynb` and run top to bottom.
3. Generated artifacts are written to `/kaggle/working/`.

The notebook uses standard scientific Python packages and performs no automatic installation. Check the installed versions against the recorded environment if results differ. For local replay and package verification, follow [requirements-notes.md](requirements-notes.md).
