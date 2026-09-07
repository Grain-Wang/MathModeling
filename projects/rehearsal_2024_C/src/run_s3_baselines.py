"""Run the eight approved S3 baseline experiments in their dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from s3_common import DEFAULT_CONFIG, PROJECT_ROOT


TZ = ZoneInfo("Asia/Shanghai")
RUNNERS = [
    ("EXP-S3-DATA-001", "build_features.py"),
    ("EXP-Q1-BASE-001", "run_q1.py"),
    ("EXP-Q2-BASE-001", "run_q2.py"),
    ("EXP-Q3-DESC-001", "run_q3.py"),
    ("EXP-Q3-BASE-001", "run_q3.py"),
    ("EXP-Q4-NULL-001", "run_q4.py"),
    ("EXP-Q4-BASE-001", "run_q4.py"),
    ("EXP-Q5-BASE-001", "run_q5.py"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--only",
        nargs="*",
        choices=[experiment_id for experiment_id, _ in RUNNERS],
        help="Run only selected experiment IDs; dependency order is retained.",
    )
    parser.add_argument(
        "--verify-data-rebuild",
        action="store_true",
        help="Run the feature builder twice so the second run can prove byte stability.",
    )
    return parser.parse_args()


def command_for(experiment_id: str, runner: str, config_path: Path) -> list[str]:
    command = [sys.executable, str(PROJECT_ROOT / "src" / runner)]
    method_arguments = {
        "EXP-Q1-BASE-001": ["--model", "logistic", "--stage", "baseline"],
        "EXP-Q2-BASE-001": ["--model", "steinmetz", "--stage", "baseline"],
        "EXP-Q3-DESC-001": ["--model", "descriptive", "--stage", "baseline"],
        "EXP-Q3-BASE-001": ["--model", "additive", "--stage", "baseline"],
        "EXP-Q4-NULL-001": ["--model", "median", "--stage", "baseline"],
        "EXP-Q4-BASE-001": ["--model", "ridge", "--stage", "baseline"],
        "EXP-Q5-BASE-001": ["--mode", "oof-observed-pareto", "--stage", "baseline"],
    }
    command.extend(method_arguments.get(experiment_id, []))
    command.extend(["--config", str(config_path)])
    return command


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    selected = set(args.only or [experiment_id for experiment_id, _ in RUNNERS])
    selected_runners = [item for item in RUNNERS if item[0] in selected]
    if not selected_runners:
        raise ValueError("No S3 experiments selected")

    started = datetime.now(TZ)
    print(f"S3_BASELINE_START {started.isoformat()} python={sys.executable}", flush=True)
    for experiment_id, runner in selected_runners:
        repeats = 2 if experiment_id == "EXP-S3-DATA-001" and args.verify_data_rebuild else 1
        for repeat in range(1, repeats + 1):
            command = command_for(experiment_id, runner, config_path)
            print(
                f"RUN experiment={experiment_id} repeat={repeat}/{repeats} command={subprocess.list2cmdline(command)}",
                flush=True,
            )
            subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    ended = datetime.now(TZ)
    print(f"S3_BASELINE_END {ended.isoformat()} runtime_seconds={(ended - started).total_seconds():.3f}", flush=True)


if __name__ == "__main__":
    main()
