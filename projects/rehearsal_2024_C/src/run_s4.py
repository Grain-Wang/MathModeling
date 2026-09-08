"""Run all mandatory S4 experiments in G3 priority order, then independently verify outputs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from s3_common import DEFAULT_CONFIG, PROJECT_ROOT
from s4_common import S4_RESULTS_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def execute(script: str, mode: str | None, config_path: Path) -> None:
    command = [sys.executable, str(PROJECT_ROOT / "src" / script)]
    if mode is not None:
        command.extend(["--mode", mode])
    command.extend(["--config", str(config_path)])
    print("RUN", " ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    execute("run_s4_q2.py", "main", config_path)
    q2 = json.loads((S4_RESULTS_ROOT / "q2" / "quadratic_temperature_metrics.json").read_text(encoding="utf-8"))
    if q2["conditional_upgrade_triggered"]:
        raise RuntimeError("EXP-Q2-EXT-001 was triggered; stop bounded queue for an explicit conditional-upgrade implementation review")
    execute("run_s4_q2.py", "sensitivity", config_path)
    execute("run_s4_q4.py", "main", config_path)
    q4 = json.loads((S4_RESULTS_ROOT / "q4" / "hgb_metrics.json").read_text(encoding="utf-8"))
    if q4["random_forest_triggered"]:
        raise RuntimeError("EXP-Q4-CHAL-001 was triggered; stop bounded queue for an explicit challenger implementation review")
    execute("run_s4_q4.py", "ablation", config_path)
    execute("run_s4_q4.py", "stress", config_path)
    execute("run_s4_q5.py", "robustness", config_path)
    execute("run_s4_q5.py", "sensitivity", config_path)
    execute("run_s4_q3.py", "interaction", config_path)
    execute("run_s4_q3.py", "bootstrap", config_path)
    execute("run_s4_q3.py", "sensitivity", config_path)
    execute("run_s4_q1.py", None, config_path)
    execute("verify_s4_outputs.py", None, config_path)


if __name__ == "__main__":
    main()