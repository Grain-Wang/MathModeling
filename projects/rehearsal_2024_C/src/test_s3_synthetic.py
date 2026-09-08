"""Fast synthetic assertions for S3 boundary cases; no project data are loaded."""

from __future__ import annotations

import numpy as np
import pandas as pd

from run_q5 import add_region_columns, pareto_intersection_empty, region_jaccard, representative_points
from s3_common import assert_pareto, pareto_mask


def test_pareto_dominance_and_ties() -> None:
    loss = np.array([1.0, 2.0, 1.0, 0.5, 1.5])
    energy = np.array([1.0, 1.0, 1.0, 0.5, 2.0])
    mask = pareto_mask(loss, energy)
    assert mask.tolist() == [True, False, True, True, True]
    assert_pareto(loss, energy, mask)


def test_duplicate_quartile_edges_are_recorded() -> None:
    frame = pd.DataFrame(
        {
            "material": ["m"] * 8,
            "waveform": ["w"] * 8,
            "temperature_C": [25] * 8,
            "frequency_Hz": [1.0, 1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            "b_m_T": [0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )
    result, metadata = add_region_columns(frame)
    assert metadata["frequency_duplicate_edges_dropped"] > 0
    assert metadata["b_m_duplicate_edges_dropped"] > 0
    assert result["q5_region_id"].notna().all()


def test_representative_points_zero_ranges() -> None:
    pareto = pd.DataFrame(
        {
            "row_id": ["a", "b"],
            "y_pred_oof": [1.0, 1.0],
            "energy_proxy_Hz_T": [2.0, 2.0],
            "full_oof_log_gap": [0.0, 0.1],
            "oof_absolute_log_residual": [0.2, 0.1],
        }
    )
    representatives, flags = representative_points(pareto)
    assert representatives["provisional_oof_knee_row_id"] == "a"
    assert flags == {"pareto_loss_zero_range": True, "pareto_energy_zero_range": True}


def test_oof_full_empty_intersection_branch() -> None:
    assert pareto_intersection_empty(np.array([True, False]), np.array([False, True]))
    assert not pareto_intersection_empty(np.array([True, False]), np.array([True, False]))


def test_region_jaccard_both_empty_branch() -> None:
    assert region_jaccard(set(), set(), 0.5) == (None, "both_region_sets_empty", False)
    assert region_jaccard({"a", "b"}, {"b", "c"}, 0.3) == (1 / 3, "defined", True)


def main() -> None:
    test_pareto_dominance_and_ties()
    test_duplicate_quartile_edges_are_recorded()
    test_representative_points_zero_ranges()
    test_oof_full_empty_intersection_branch()
    test_region_jaccard_both_empty_branch()
    print("PASS: S3 synthetic boundary assertions")


if __name__ == "__main__":
    main()
