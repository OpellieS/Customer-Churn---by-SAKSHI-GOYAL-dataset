# Audit evidence and provenance

Start with [publication/final_audit_th.md](publication/final_audit_th.md) for the final publication decision and [publication/execution.json](publication/execution.json) for the final clean execution.

The root-level audit files and `runtime/` preserve the **prior audit**. Their notebook hashes, cell references and MINOR findings describe the pre-publication version. They are not claims that the final notebook still has those findings. The original Thai audit includes a publication note and portable links; temporary environment paths in the embedded-output transcript were redacted without changing analytical numbers.

- `cell_inventory.json`, `notebook_cells.txt`, `embedded_outputs.txt`: historical notebook inspection snapshots.
- `execution_verification.json`, `independent_verification.json`, `independent_metric_checks.csv`, `schema_order_check.json`, `compatibility_checks.json`, `output_file_checks.csv`: prior execution and independent checks.
- `runtime/audit_execution.ipynb`, `runtime/audit_exports/`, `runtime/kaggle/working/`: intentionally retained historical replay and detailed model/SHAP evidence. These duplicate some final outputs to allow before/after verification; they are not disposable execution caches.
- `publication/`: current fresh-kernel execution, independent metric/threshold/interval checks, schema rejection tests, SHAP API-shape tests, candidate validation probabilities, source diff, file inventory and publication checks.

The original Kaggle CSV under a local `runtime/kaggle/input/` directory is ignored and not redistributed. Download it separately for replay. The original notebook source SHA-256 is `323c968b6aa1ad3874c7fb916b069626aa250b3c315af76a8682a0ca831389d4`; the final notebook hash is recorded in the latest execution record. Historical results were numerically compared with the final outputs; runtime timing differences and added SHAP metadata are expected.
