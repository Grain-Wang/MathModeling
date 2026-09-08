"""Small synthetic checks for S5 waveform feature reuse and class encoding."""

from __future__ import annotations

import numpy as np

from build_features import WAVEFORM_POINTS, waveform_features
from s3_common import CLASS_ENCODING, SHAPE_FEATURES, WAVEFORM_LABELS


def main() -> None:
    x = np.arange(WAVEFORM_POINTS, dtype=np.float64) / WAVEFORM_POINTS
    waves = {
        "正弦波": np.sin(2.0 * np.pi * x),
        "三角波": 2.0 * np.abs(2.0 * (x - np.floor(x + 0.5))) - 1.0,
        "梯形波": np.clip(4.0 * np.sin(2.0 * np.pi * x), -1.0, 1.0),
    }
    for label, waveform in waves.items():
        features, blocks = waveform_features(waveform, plateau_fraction=0.01)
        assert label in CLASS_ENCODING
        assert CLASS_ENCODING[label] in {1, 2, 3}
        assert all(name in features for name in SHAPE_FEATURES)
        assert np.isfinite([features[name] for name in SHAPE_FEATURES]).all()
        assert blocks.shape == (64,) and np.isfinite(blocks).all()
    assert set(CLASS_ENCODING) == set(WAVEFORM_LABELS)
    print("S5_SYNTHETIC_CHECKS_PASS")


if __name__ == "__main__":
    main()
