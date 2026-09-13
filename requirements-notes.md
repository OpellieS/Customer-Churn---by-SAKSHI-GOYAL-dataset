# Reproducibility notes

The notebook uses Kaggle-style paths and standard scientific Python packages. No locked environment is claimed. The exact successful local CPU versions are recorded in [outputs/run_manifest.json](outputs/run_manifest.json): Python 3.13.5, NumPy 2.4.2, pandas 3.0.0, scikit-learn 1.8.0, matplotlib 3.10.8, seaborn 0.13.2, SHAP 0.52.0, XGBoost 3.4.1 and LightGBM 4.7.0.

Local verification additionally needs SciPy, nbformat, nbclient, jupyter-client and ipykernel. Install missing packages in an isolated environment; these notes are a record, not a fully resolved dependency lock. On Kaggle, check package availability first; the notebook does not install or upgrade dependencies.

From the repository root, after downloading the source CSV separately:

```bash
python scripts/verify_project.py --execute --input-dir /path/to/downloaded/dataset
python scripts/check_compatibility.py
python scripts/verify_project.py
```

The input directory must contain `BankChurners.csv` (nested folders are accepted). Full execution creates a fresh temporary kernel and Kaggle directory mirror; it updates notebook outputs, `outputs/`, `validation_report.json` and `audit/publication/` evidence. It retains the notebook's absolute Kaggle paths. No source CSV is copied into tracked project outputs.

The last command verifies recorded artifacts without retraining. It checks the notebook hash against the recorded clean execution and independently recomputes test metrics, validation threshold decisions and bootstrap intervals. It does not itself prove a new execution occurred.

After a new execution, regenerate the distribution archive with:

```bash
python - <<'PYTHON'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
with ZipFile('results.zip', 'w', ZIP_DEFLATED) as archive:
    for path in sorted(Path('outputs').rglob('*')):
        if path.is_file():
            archive.write(path, path.as_posix())
    archive.write('validation_report.json')
PYTHON
```

Original audit runtime files are intentionally historical snapshots and are not overwritten by replay. Synthetic schema/SHAP compatibility tests are software checks, not additional customer-analysis results.
