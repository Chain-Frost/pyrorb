"""Integrated S7 #146 → #149 → #147 CLI contract on authored public source bytes.

This exercises the real B/C implementations on the staged integration branch.
Incomplete rainfall tails are retained: successful routing is not a
full-domain flood-frequency estimate or RORBwin native parity.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import cast

from runoff_routing.bom_ifd import read_bom_ifd_csv
from runoff_routing.monte_carlo_effective import iter_effective_events, validate_effective_request
from runoff_routing.monte_carlo_execution import main
from runoff_routing.monte_carlo_plan import ifd_from_bom
from runoff_routing.project_batch import run_project_events
from runoff_routing.project_json import EmbeddedRun, Project, write_project
from runoff_routing.rorb_model import RunModel, from_json

EXAMPLES = Path(__file__).parents[1] / "examples"


def _fixture(root: Path) -> tuple[Path, Path, Path, Path]:
    project = root / "project.json"
    model = from_json((EXAMPLES / "synthetic-run.json").read_text(encoding="utf-8"))
    assert isinstance(model, RunModel)
    write_project(project, Project("integrated_mc", "explicit", EmbeddedRun(model)))
    ifd = root / "ifd.csv"
    patterns = root / "patterns.csv"
    ifd.write_bytes((EXAMPLES / "arr-design-synthetic-ifd.csv").read_bytes())
    patterns.write_bytes((EXAMPLES / "arr-design-synthetic-patterns.csv").read_bytes())
    spec: dict[str, object] = {
        "schema_version": 1,
        "policy": {"id": "monte-carlo-statistics", "version": "1", "status": "reviewed"},
        "scenario_id": "synthetic",
        "duration_min": 60,
        "sources": {
            "ifd": hashlib.sha256(ifd.read_bytes()).hexdigest(),
            "temporal_patterns": hashlib.sha256(patterns.read_bytes()).hexdigest(),
        },
        "rng": {
            "algorithm": "hmac-sha256-53-v1",
            "derivation": "canonical-json-domain-separated-v1",
            "root_seed": 42,
        },
        "within_stratum": "uniform_aep_mass_v1",
        "strata": [
            {"id": "h1", "aep_lower": "0.01", "aep_upper": "0.02", "probability_mass": "0.01", "count": 2},
        ],
        "ifd": ifd_from_bom(read_bom_ifd_csv(ifd), 60),
        "tp_bins": [
            {
                "id": "rare",
                "aep_lower": "0.01",
                "aep_upper": "0.02",
                "choices": [
                    {"event_id": "0001", "source_order": 1, "probability": "0.5"},
                    {"event_id": "0002", "source_order": 2, "probability": "0.5"},
                ],
            },
        ],
        "loss": {"mode": "fixed_storm_il", "storm_il_mm": "1"},
        "fixed_parameters": [
            {"name": "kc", "value": "0.5", "unit": "RORB_coefficient"},
            {"name": "m", "value": "1", "unit": "dimensionless"},
            {"name": "continuing", "value": "0.1", "unit": "mm/h"},
        ],
        "arf_policy": "catchment-wide-once-after-sampling-by-event-owner",
        "preburst_policy": "storm-IL-before-one-time-preburst-adjustment-by-event-owner",
        "joint_policy": "conditional-tp-on-aep__independent-storm-il-v1",
    }
    config = root / "spec.json"
    config.write_text(json.dumps(spec) + "\n", encoding="utf-8")
    return project, config, ifd, patterns


def test_real_b_to_e_to_c_cli_and_representative_replay(tmp_path: Path) -> None:
    project, config, ifd, patterns = _fixture(tmp_path)
    prefix = tmp_path / "study"
    request = tmp_path / "effective.jsonl"
    ledger = tmp_path / "computed.jsonl"
    report = tmp_path / "frequency"
    assert main(["plan", str(config), str(prefix)]) == 0
    assert (
        main(
            [
                "prepare",
                str(project),
                str(tmp_path / "study.plan.json"),
                str(tmp_path / "study.samples.jsonl"),
                str(request),
                "--ifd",
                str(ifd),
                "--patterns",
                str(patterns),
                "--arf-region",
                "South-West Western Australia",
                "--dry-tail-min",
                "120",
            ]
        )
        == 0
    )
    header, _ = validate_effective_request(request)
    assert header.event_count == 2
    assert header.strata[0].planned_samples == 2
    assert header.populations[0].rare_unmodelled_mass == Decimal("0.01")
    assert header.populations[0].frequent_unmodelled_mass == Decimal("0.98")
    events = tuple(iter_effective_events(request))
    assert len(events) == 2
    assert all(item.tp_aep_band == "rare" and item.tp_bin_id == "rare" for item in events)
    assert all(item.event.event_id.startswith("mc-") for item in events)

    assert main(["run", str(project), str(request), str(ledger), "--engine", "python-cmd"]) == 0
    assert main(["run", str(project), str(request), str(ledger), "--resume"]) == 0
    for event in events:
        direct = run_project_events(project, (event.event,)).outcomes[0]
        assert direct.status == "computed_unvalidated"
    assert main(["frequency", str(project), str(request), str(ledger), str(report), "--aep", "0.01"]) == 2
    body = json.loads((tmp_path / "frequency.json").read_text(encoding="utf-8"))
    assert body["point_results_complete"] is False
    scopes = cast("list[dict[str, object]]", body["frequency_scopes"])
    assert len(scopes) == 1
    assert scopes[0]["physical_site_id"] == "print_1"
    targets = cast("list[dict[str, object]]", scopes[0]["targets"])
    assert targets[0]["status"] == "incomplete"
    assert targets[0]["peak_m3_s"] is None
    assert (tmp_path / "frequency.csv").is_file()
    first = events[0]
    assert main(["replay", str(project), str(request), str(ledger), first.sample_id, str(tmp_path / "selected")]) == 0
    replayed = json.loads((tmp_path / "selected.json").read_text(encoding="utf-8"))
    outcomes = cast("list[dict[str, object]]", replayed["outcomes"])
    assert outcomes[0]["event_id"] == first.event.event_id
