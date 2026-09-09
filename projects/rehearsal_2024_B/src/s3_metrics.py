"""Metric helpers for the frozen rehearsal_2024_B S3 contracts."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, r2_score


def nearest_rank(values: np.ndarray, quantile: float) -> float | None:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return None
    ordered = np.sort(finite)
    return float(ordered[max(0, math.ceil(quantile * ordered.size) - 1)])


def regression_metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    y, yhat = np.asarray(truth, float), np.asarray(prediction, float)
    if y.shape != yhat.shape or y.ndim != 1:
        raise ValueError("regression arrays must be one-dimensional and aligned")
    if not np.isfinite(y).all() or not np.isfinite(yhat).all():
        raise ValueError("regression truth and predictions must be finite")
    residual = yhat - y
    return {
        "n": int(y.size), "mae": float(np.mean(np.abs(residual))),
        "rmse": float(np.sqrt(np.mean(np.square(residual)))),
        "r2": float(r2_score(y, yhat)) if y.size > 1 else None,
        "median_error": float(np.median(residual)),
    }


def relative_error_metrics(
    truth: np.ndarray, prediction: np.ndarray, include_cdf: bool = False,
) -> dict[str, Any]:
    y, yhat = np.asarray(truth, float), np.asarray(prediction, float)
    if y.shape != yhat.shape or y.ndim != 1:
        raise ValueError("relative-error arrays must be aligned")
    if not np.isfinite(y).all() or not np.isfinite(yhat).all():
        raise ValueError("relative-error inputs must be finite")
    zero = y == 0
    signed = (yhat[~zero] - y[~zero]) / y[~zero]
    absolute = np.abs(signed)
    signed90, absolute90 = nearest_rank(signed, .90), nearest_rank(absolute, .90)
    result: dict[str, Any] = {
        **regression_metrics(y, yhat),
        "positive_denominator_count": int((~zero).sum()),
        "zero_truth_count": int(zero.sum()),
        "zero_truth_absolute_errors": [
            float(value) for value in np.abs(yhat[zero] - y[zero])
        ],
        "signed_error_90": signed90,
        "accuracy_90": None if signed90 is None else float(1.0 - signed90),
        "absolute_relative_error_90": absolute90,
        "median_signed_bias": float(np.median(signed)) if signed.size else None,
    }
    if include_cdf:
        ordered, ordered_abs = np.sort(signed), np.sort(absolute)
        result["signed_cdf"] = {
            "error_fraction": [float(value) for value in ordered],
            "empirical_probability": [
                float((index + 1) / ordered.size) for index in range(ordered.size)
            ],
        }
        result["absolute_relative_error_cdf"] = {
            "error_fraction": [float(value) for value in ordered_abs],
            "empirical_probability": [
                float((index + 1) / ordered_abs.size)
                for index in range(ordered_abs.size)
            ],
        }
    return result


def classification_metrics(
    truth: np.ndarray, prediction: np.ndarray,
    probability: np.ndarray, labels: list[str],
) -> dict[str, Any]:
    y, yhat = np.asarray(truth, str), np.asarray(prediction, str)
    proba = np.asarray(probability, float)
    if y.shape != yhat.shape or proba.shape != (y.size, len(labels)):
        raise ValueError("classification arrays are not aligned to fixed labels")
    if not np.isfinite(proba).all():
        raise ValueError("classification probabilities must be finite")
    if not np.allclose(proba.sum(axis=1), 1.0, atol=1e-10, rtol=0):
        raise ValueError("classification probabilities do not sum to one")
    if set(yhat) - set(labels) or set(y) - set(labels):
        raise ValueError("truth/prediction outside fixed label space")
    nss_true = np.asarray([item.split("|")[0] for item in y])
    nss_pred = np.asarray([item.split("|")[0] for item in yhat])
    mcs_true = np.asarray([item.split("|")[1] for item in y])
    mcs_pred = np.asarray([item.split("|")[1] for item in yhat])
    observed = [label for label in labels if np.any(y == label)]
    balanced = np.mean([
        np.mean(yhat[y == label] == label) for label in observed
    ])
    true_index = np.asarray([labels.index(item) for item in y], dtype=int)
    fixed_log_loss = -np.mean(np.log(
        np.clip(proba[np.arange(y.size), true_index], 1e-15, 1.0)
    ))
    return {
        "n": int(y.size),
        "macro_f1_fixed_17": float(
            f1_score(y, yhat, labels=labels, average="macro", zero_division=0)
        ),
        "joint_accuracy": float(accuracy_score(y, yhat)),
        "balanced_accuracy": float(balanced),
        "nss_accuracy": float(accuracy_score(nss_true, nss_pred)),
        "mcs_accuracy": float(accuracy_score(mcs_true, mcs_pred)),
        "multiclass_log_loss": float(fixed_log_loss),
        "predicted_class_support": {
            label: int(np.sum(yhat == label)) for label in labels
        },
        "true_class_support": {
            label: int(np.sum(y == label)) for label in labels
        },
    }


def fixed_confusion(
    truth: np.ndarray, prediction: np.ndarray, labels: list[str],
) -> dict[str, Any]:
    matrix = confusion_matrix(
        np.asarray(truth, str), np.asarray(prediction, str), labels=labels
    )
    return {"labels": labels, "matrix": matrix.astype(int).tolist()}


def percentile_interval(values: list[float], level: float = .95) -> dict[str, Any]:
    array = np.asarray(values, float)
    alpha = (1.0 - level) / 2.0
    return {
        "replicates": int(array.size), "level": level,
        "lower": float(np.quantile(array, alpha)),
        "median": float(np.quantile(array, .5)),
        "upper": float(np.quantile(array, 1.0 - alpha)),
    }
