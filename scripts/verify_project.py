"""Replay the notebook in a fresh kernel and independently verify published metrics.

No dataset downloads, package installation, model changes, or test-set tuning.
"""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone

import nbformat
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / "audit/publication"
OUTPUTS = ROOT / "outputs"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def read_csv(path):
    return pd.read_csv(path, float_precision="round_trip")


def notebook_checks():
    notebook = nbformat.read(ROOT / "notebook.ipynb", as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            ast.parse(cell.source)
            assert "/Users/" not in cell.source and "/tmp/" not in cell.source
    return notebook


INSPECTION_CELL = r'''
inspection_dir = Path("publication_inspection")
inspection_dir.mkdir(exist_ok=True)
pd.DataFrame({"actual": y_validation.to_numpy(), "probability": validation_probability}).to_csv(
    inspection_dir / "validation_predictions.csv", index=False)
validation_check = pd.DataFrame(validation_probabilities)
validation_check.to_csv(inspection_dir / "validation_candidate_probabilities.csv", index=False)
inspection = {
    "source_sha256": source_sha256, "analytical_rows": len(data),
    "source_columns": len(raw.columns), "raw_predictors": len(predictor_columns),
    "engineered_predictors": 2, "transformed_columns": len(transformed_names),
    "missing_source_cells": int(raw.isna().sum().sum()),
    "duplicate_customer_keys": int(data.CLIENTNUM.duplicated().sum()),
    "source_infinite_cells": int(quality.infinite_cells.sum()),
    "invalid_range_cells": int(range_audit.invalid_n.sum()),
    "naive_bayes_fields_excluded": len(nb_columns),
    "identifier_intersections": {
        "train_validation": len(id_sets["Train"] & id_sets["Validation"]),
        "train_test": len(id_sets["Train"] & id_sets["Test"]),
        "validation_test": len(id_sets["Validation"] & id_sets["Test"]),
    },
    "final_predictive_model": final_model_name, "explained_model": course_forest_name,
    "forest_parameters": forest_search.best_params_,
    "forest_classes": forest.classes_.tolist(), "positive_class_index": positive_class,
    "shap_reference": shap_reference_method, "shap_additivity_max_error": shap_additivity_error,
    "source_mapping_columns": len(source_names),
    "local_forest_probability": local_probability, "local_forest_base": local_base,
    "local_shap_sum": float(local_values.sum()),
    "largest_calibration_bin": largest_calibration_bin.to_dict(),
    "calibration_summary": calibration_bin_summary,
}
(inspection_dir / "inspection.json").write_text(json.dumps(inspection, indent=2))
'''


def execute_notebook(notebook, input_dir):
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import KernelSpecManager
    from nbclient import NotebookClient

    if not input_dir.is_dir():
        raise ValueError("--input-dir must contain the downloaded Kaggle CSV files.")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="churn-verification-") as temporary:
        workspace = Path(temporary)
        mirror = workspace / "kaggle/input"
        for csv in input_dir.rglob("*.csv"):
            destination = mirror / csv.relative_to(input_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(csv, destination)
        if not mirror.exists():
            raise ValueError("No CSV files found in --input-dir.")

        kernel_root = workspace / "kernels"
        kernel = kernel_root / "churn-verification"
        kernel.mkdir(parents=True)
        write_json(kernel / "kernel.json", {
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Churn verification", "language": "python",
        })
        manager = KernelManager(kernel_name="churn-verification",
                                kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
        replay = copy.deepcopy(notebook)
        for cell in replay.cells:
            if cell.cell_type == "code":
                cell.source = cell.source.replace('Path("/kaggle/input")', 'Path("kaggle/input")')
                cell.source = cell.source.replace('Path("/kaggle/working")', 'Path("kaggle/working")')
                cell.outputs = []
                cell.execution_count = None
        replay.cells.append(nbformat.v4.new_code_cell(INSPECTION_CELL))

        def progress(cell, cell_index, **kwargs):
            if cell.cell_type == "code":
                print(f"Executing cell {cell_index + 1}/{len(replay.cells)}", flush=True)

        NotebookClient(replay, km=manager, timeout=900,
                       resources={"metadata": {"path": str(workspace)}},
                       on_cell_start=progress).execute()
        warning_outputs = []
        for index, (original, executed) in enumerate(zip(notebook.cells, replay.cells), 1):
            if original.cell_type == "code":
                assert executed.execution_count is not None
                assert not any(output.output_type == "error" for output in executed.outputs)
                original.outputs = executed.outputs
                original.execution_count = executed.execution_count
                for output in executed.outputs:
                    if output.output_type == "stream" and output.name == "stderr":
                        warning_outputs.append({"cell": index, "text": output.text})
        nbformat.validate(notebook)
        nbformat.write(notebook, ROOT / "notebook.ipynb")
        fresh_outputs = workspace / "kaggle/working"
        fresh_names = {path.relative_to(fresh_outputs) for path in fresh_outputs.rglob("*") if path.is_file()}
        existing_names = {path.relative_to(OUTPUTS) for path in OUTPUTS.rglob("*") if path.is_file()}
        assert existing_names <= fresh_names, "Existing outputs were not all recreated; investigate stale files."
        shutil.copytree(fresh_outputs, OUTPUTS, dirs_exist_ok=True)
        shutil.copytree(workspace / "publication_inspection", PUBLICATION, dirs_exist_ok=True)

    result = {
        "status": "passed", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_notebook_cells": len(notebook.cells),
        "executed_notebook_code_cells": sum(cell.cell_type == "code" for cell in notebook.cells),
        "extra_inspection_cells": 1, "execution_seconds": round(time.perf_counter()-started, 2),
        "fresh_kernel": True, "warnings": warning_outputs,
        "execution_environment": "Local CPU; same Python environment as this command; temporary Kaggle directory mirror",
        "path_changes_in_replay_only": ["/kaggle/input to kaggle/input", "/kaggle/working to kaggle/working"],
        "published_notebook_paths": "Unchanged Kaggle absolute paths",
        "notebook_sha256": hashlib.sha256((ROOT / "notebook.ipynb").read_bytes()).hexdigest(),
        "limits": "Not run on hosted Kaggle; not a test of every dependency version or fallback branch",
    }
    write_json(PUBLICATION / "execution.json", result)
    return notebook


def average_precision(actual, score):
    order = np.argsort(-score, kind="stable")
    cumulative_positive = np.cumsum(actual[order])
    endpoints = np.r_[np.flatnonzero(np.diff(score[order])), len(actual)-1]
    tp = cumulative_positive[endpoints]
    positive_in_group = np.diff(np.r_[0, tp])
    return float(np.sum(positive_in_group * tp / (endpoints+1)) / actual.sum())


def roc_auc(actual, score):
    positives = int(actual.sum())
    negatives = len(actual)-positives
    return float((rankdata(score)[actual == 1].sum() - positives*(positives+1)/2) / (positives*negatives))


def counts(actual, flag):
    return {"TP": int(np.sum((actual == 1) & flag)), "FP": int(np.sum((actual == 0) & flag)),
            "FN": int(np.sum((actual == 1) & ~flag)), "TN": int(np.sum((actual == 0) & ~flag))}


def check_metrics():
    predictions = read_csv(OUTPUTS / "test_predictions.csv")
    assert set(predictions) == {"actual_churn", "predicted_churn_probability", "frozen_action_flag"}
    assert not predictions.isna().any().any()
    actual = predictions.actual_churn.to_numpy()
    probability = predictions.predicted_churn_probability.to_numpy()
    flag = predictions.frozen_action_flag.to_numpy().astype(bool)
    policy = json.loads((OUTPUTS / "frozen_policy.json").read_text())
    assert set(np.unique(actual)) == {0, 1}
    assert np.isfinite(probability).all() and ((probability >= 0) & (probability <= 1)).all()
    assert np.array_equal(flag, probability >= policy["threshold"])
    c = counts(actual, flag)
    tp, fp, fn, tn = (c[key] for key in ["TP", "FP", "FN", "TN"])
    values = {
        "Average Precision": average_precision(actual, probability), "ROC-AUC": roc_auc(actual, probability),
        "Accuracy": (tp+tn)/len(actual), "Balanced Accuracy": (tp/(tp+fn)+tn/(tn+fp))/2,
        "Precision": tp/(tp+fp) if tp+fp else 0, "Recall": tp/(tp+fn),
        "F1": 2*tp/(2*tp+fp+fn), "Brier Score": float(np.mean((probability-actual)**2)),
        "Illustrative decision loss": policy["FN_cost"]*fn+policy["FP_cost"]*fp,
        "Frozen threshold": policy["threshold"], **c,
    }
    reported = read_csv(OUTPUTS / "final_metrics.csv").set_index("metric")
    comparisons = pd.DataFrame([{"metric": name, "reported": reported.loc[name, "value"],
                                 "independent": value, "absolute_difference": abs(reported.loc[name, "value"]-value)}
                                for name, value in values.items()])
    assert comparisons.absolute_difference.max() < 1e-12
    comparisons.to_csv(PUBLICATION / "independent_metric_checks.csv", index=False)

    validation = read_csv(PUBLICATION / "validation_predictions.csv")
    thresholds = read_csv(OUTPUTS / "validation_threshold_analysis.csv")
    yv, pv = validation.actual.to_numpy(), validation.probability.to_numpy()
    for row in thresholds.itertuples():
        c = counts(yv, pv >= row.threshold)
        assert all(c[name] == getattr(row, name) for name in c)
        assert policy["FN_cost"]*c["FN"] + policy["FP_cost"]*c["FP"] == row.decision_loss
    selected = thresholds.sort_values(["decision_loss", "flagged_customers", "threshold"],
                                      ascending=[True, True, False]).iloc[0]
    assert selected.threshold == policy["threshold"]

    rng = np.random.default_rng(42)
    bootstrap = []
    for _ in range(500):
        ix = rng.integers(0, len(actual), size=len(actual))
        y, p, f = actual[ix], probability[ix], flag[ix]
        if np.unique(y).size < 2:
            continue
        c = counts(y, f)
        bootstrap.append([average_precision(y, p), roc_auc(y, p), c["TP"]/(c["TP"]+c["FN"]),
                          c["TP"]/(c["TP"]+c["FP"]) if c["TP"]+c["FP"] else 0])
    intervals = np.quantile(bootstrap, [0.025, 0.975], axis=0)
    for index, name in enumerate(["Average Precision", "ROC-AUC", "Recall", "Precision"]):
        np.testing.assert_allclose(intervals[:, index], reported.loc[name, ["ci_95_low", "ci_95_high"]].to_numpy(float), atol=1e-12)

    manifest = json.loads((OUTPUTS / "run_manifest.json").read_text())
    inspection = json.loads((PUBLICATION / "inspection.json").read_text())
    assert manifest["primary_model"] == policy["model"] == inspection["final_predictive_model"]
    for name in ["shap_global_importance.csv", "shap_source_importance.csv"]:
        shap_table = read_csv(OUTPUTS / name)
        assert shap_table.explained_model.eq(manifest["course_forest"]).all()
        assert shap_table.explained_class.eq(1).all()
        assert shap_table.output_scale.eq("churn_probability").all()
    assert inspection["shap_additivity_max_error"] < 1e-4
    assert inspection["source_mapping_columns"] == inspection["transformed_columns"]
    assert inspection["forest_classes"][inspection["positive_class_index"]] == 1
    assert all(value == 0 for value in inspection["identifier_intersections"].values())
    assert inspection["naive_bayes_fields_excluded"] == 2

    prior = ROOT / "audit/runtime/kaggle/working"
    comparison_rows = []
    for path in sorted(OUTPUTS.glob("*.csv")):
        new = read_csv(path)
        old_path = prior / path.name
        if old_path.exists():
            old = read_csv(old_path)
            shared = [column for column in old.columns if column in new.columns and not column.endswith("_time")]
            try:
                pd.testing.assert_frame_equal(new[shared], old[shared], check_exact=False, atol=1e-12, rtol=1e-12)
                same = True
            except AssertionError:
                same = False
            comparison_rows.append({"file": path.name, "historical_values_unchanged": same})
    pd.DataFrame(comparison_rows).to_csv(PUBLICATION / "historical_output_comparison.csv", index=False)
    result = {"status": "passed", "maximum_metric_difference": float(comparisons.absolute_difference.max()),
              "thresholds_checked": len(thresholds), "validation_minimum_loss": int(selected.decision_loss),
              "frozen_threshold": policy["threshold"], "bootstrap_replicates": len(bootstrap),
              "confidence_intervals_match": True, "model_roles_consistent": True,
              "source_customer_ids_in_predictions": False,
              "historical_values_unchanged": all(row["historical_values_unchanged"] for row in comparison_rows),
              "final_model": policy["model"], "metrics": values}
    write_json(PUBLICATION / "independent_verification.json", result)
    return result


def check_schema(notebook):
    namespace = {"np": np, "pd": pd}
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        for node in ast.parse(cell.source).body:
            keep = isinstance(node, ast.FunctionDef) and node.name == "validate_source_schema"
            keep |= isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith("REQUIRED_") for t in node.targets)
            if keep:
                exec(compile(ast.Module(body=[node], type_ignores=[]), "<schema-check>", "exec"), namespace)
    frame = pd.DataFrame({field: [1] for field in namespace["REQUIRED_NUMERIC_FIELDS"]})
    for field in namespace["REQUIRED_CATEGORICAL_FIELDS"]:
        frame[field] = "Unknown"
    frame["CLIENTNUM"] = 1
    frame["Attrition_Flag"] = "Existing Customer"
    namespace["validate_source_schema"](frame)
    passed = []
    for kind, test_frame, error_type in [
        ("missing required feature", frame.drop(columns="Total_Trans_Ct"), ValueError),
        ("non-numeric numeric feature", frame.assign(Customer_Age="invalid"), TypeError),
    ]:
        try:
            namespace["validate_source_schema"](test_frame)
        except error_type:
            passed.append(kind)
        else:
            raise AssertionError(f"Schema guard failed: {kind}")
    write_json(PUBLICATION / "schema_checks.json", {"status": "passed", "rejected_before_eda": passed,
               "scope": "Synthetic invalid-input tests; not empirical customer analysis"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run all cells in a new kernel and refresh outputs")
    parser.add_argument("--input-dir", type=Path, help="Directory containing the downloaded Kaggle dataset CSV")
    args = parser.parse_args()
    PUBLICATION.mkdir(parents=True, exist_ok=True)
    notebook = notebook_checks()
    if args.execute:
        if args.input_dir is None:
            parser.error("--execute requires --input-dir")
        notebook = execute_notebook(notebook, args.input_dir.resolve())
    check_schema(notebook)
    result = check_metrics()
    execution = json.loads((PUBLICATION / "execution.json").read_text())
    current_hash = hashlib.sha256((ROOT / "notebook.ipynb").read_bytes()).hexdigest()
    assert current_hash == execution["notebook_sha256"], "Notebook changed since its recorded clean execution."
    assert all(cell.execution_count is not None for cell in notebook.cells if cell.cell_type == "code")
    summary = {"notebook_json_schema_valid": True, "python_cells_syntax_valid": True,
               "notebook_sha256": current_hash, "execution": execution,
               "independent_metric_verification": result,
               "source_manifest": json.loads((OUTPUTS / "run_manifest.json").read_text()),
               "current_verification_mode": "fresh replay and independent checks" if args.execute else "independent checks against recorded replay",
               "scope": "Historical snapshot classification; no demonstrated future horizon, causal lift, survival or ROI"}
    write_json(ROOT / "validation_report.json", summary)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
