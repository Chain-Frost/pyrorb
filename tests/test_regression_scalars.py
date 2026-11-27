"""Scalar custody controls and bounded original-profile reporting diagnostics."""

from __future__ import annotations

import hashlib
import json
import math
import os
import runpy
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
from test_regression_dataset import dataset_fixture

from runoff_routing import regression_dataset as rd
from runoff_routing import regression_metrics, regression_scalar_adapter, rorb_documents, rorb_out
from runoff_routing.cmd_deviation import assess_cmd_deviation
from runoff_routing.engine_execution import run_engine_project
from runoff_routing.engine_types import EngineOutcome, EngineSelection
from runoff_routing.project_json import LegacyRunFiles, Project, SourceFile, load_project, project_to_json, write_project
from runoff_routing.regression_metrics import bind_report_metrics
from runoff_routing.regression_scalar_adapter import stored_cmd_reporting_clock, stored_float
from runoff_routing.rorb_documents import RorbSource
from runoff_routing.rorb_model import RunModel, to_json
from runoff_routing.rorb_out import inspect_output

REVISION = "a" * 40
REPO = Path(__file__).absolute().parents[1]


@pytest.mark.parametrize(
    ("source_hours", "expected_h", "expected_dt"),
    [
        ("0.3", "0x1.3333340000000p-2", "0x1.0e00000000000p+10"),
        ("0.2", "0x1.99999a0000000p-3", "0x1.6800000000000p+9"),
        ("0.5", "0x1.0000000000000p-1", "0x1.c200000000000p+10"),
    ],
)
def test_cmd_scalar_reporting_clock_matches_independently_retained_binary32_convention(
    source_hours: str, expected_h: str, expected_dt: str
) -> None:
    """The reference clock is two binary32 stores, not the raw decimal hours."""
    h, dt = stored_cmd_reporting_clock(Decimal(source_hours))
    assert h.hex() == expected_h
    assert dt.hex() == expected_dt
    if source_hours in {"0.2", "0.3"}:
        assert h != float(Decimal(source_hours))


@pytest.mark.parametrize("source_hours", ["0", "-0.2", "NaN", "Infinity", "1e-9999", "1e9999"])
def test_cmd_scalar_reporting_clock_rejects_unrepresentable_timesteps(source_hours: str) -> None:
    with pytest.raises(ValueError, match=r"CMD source timestep|CMD scalar timestep"):
        stored_cmd_reporting_clock(Decimal(source_hours))


def _write(path: Path, item: object) -> None:
    path.write_text(json.dumps(item), encoding="utf-8")


def _locator(path: Path) -> dict[str, Any]:
    return {
        "path": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _scalar_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    register, csv = dataset_fixture(tmp_path)
    document = json.loads(register.read_text())
    case = document["cases"][0]
    native = tmp_path / "native.out"
    native.write_text(
        "Time increment (hours)= 0.50\nDuration of calculations: 1\n"
        "Peak discharge,m³/s 1.000\nTime to peak,h 0.50\nVolume,m³ 1800.0\n"
        "Hydrograph summary\nSite Description\n01 Synthetic outlet\n"
        "Inc Time Hyd001\n1 0.50 0.000\n2 1.00 1.000\n",
        encoding="utf-8",
    )
    typed = tmp_path / "event.json"
    _write(typed, {"id": "SYN-001", "n": 1, "h": 0.5})
    source = RorbSource.read(native)
    report = inspect_output(source).hydrographs
    assert report is not None
    binding = bind_report_metrics(source, report)[0]
    selectors = {}
    for name, value in (("peak", binding.peak), ("peak_time", binding.peak_time), ("volume", binding.volume)):
        assert value is not None
        selectors[name] = {k: v for k, v in asdict(value).items() if k != "token"}
    case.update(reference=_locator(native), reference_format="native_report", files=[_locator(native)])
    case["scalar_binding"] = {
        "policy_id": "cmd644-report-scalars-v1",
        "native_column": "Hyd001",
        "report": _locator(native),
        "typed_input": _locator(typed),
        "source_binding": _locator(typed),
        "scalar_selectors": selectors,
        "stored_h_hex": (0.5).hex(),
        "stored_dt_hex": (1800.0).hex(),
    }
    policy = tmp_path / "policy.md"
    # Tests use the exact approved document, not a weakened synthetic policy.
    approved = REPO / "tests" / "fixtures" / "regression-v1" / "scalar-policy.md"
    policy.write_bytes(approved.read_bytes())
    document["scalar_policy_file"] = _locator(policy)
    document["qualified_candidates"] = {REVISION: {"module_sha256": {}, "wheel_sha256": "b" * 64}}
    _write(register, document)
    series = tmp_path / "series.json"
    _write(
        series,
        {
            "format": "runoff-regression-candidate-series",
            "schema_version": 1,
            "implementation_revision": REVISION,
            "mode": "source",
            "module_sha256": {},
            "cases": [
                {
                    "case_id": "SYN-001",
                    "event_input_sha256": _locator(typed)["sha256"],
                    "q_hex": [(0.0).hex(), (1.0).hex()],
                    "h_hex": (0.5).hex(),
                    "dt_hex": (1800.0).hex(),
                }
            ],
        },
    )
    return register, csv, series


def _run(register: Path, csv: Path, series: Path, output: Path, *, custody: bool = True) -> int:
    args = [
        "compare",
        str(register),
        "--csv",
        str(csv),
        "--series",
        str(series),
        "--implementation",
        REVISION,
        "--output",
        str(output),
    ]
    if custody:
        args.extend(["--custody-root", str(register.parent)])
    return rd.main(args)


def test_one_case_diagnosis_accepts_full_registered_candidate_series(tmp_path: Path) -> None:
    """One-case diagnosis must accept a full-population cached output without repacking it."""
    register, csv, series = _scalar_fixture(tmp_path)
    document = json.loads(register.read_text(encoding="utf-8"))
    duplicate = json.loads(json.dumps(document["cases"][0]))
    duplicate["case_id"] = "SYN-002"
    document["cases"].append(duplicate)
    _write(register, document)

    rows = csv.read_text(encoding="utf-8").splitlines(keepends=True)[1:]
    with csv.open("a", encoding="utf-8") as stream:
        for row in rows:
            stream.write(row.replace("SYN-001,", "SYN-002,", 1))

    candidate = json.loads(series.read_text(encoding="utf-8"))
    candidate["cases"].append({**candidate["cases"][0], "case_id": "SYN-002"})
    _write(series, candidate)

    report = tmp_path / "diagnose-one.json"
    assert (
        rd.main(
            [
                "diagnose",
                str(register),
                "--case",
                "SYN-001",
                "--csv",
                str(csv),
                "--series",
                str(series),
                "--custody-root",
                str(tmp_path),
                "--implementation",
                REVISION,
                "--output",
                str(report),
            ]
        )
        == 0
    )
    outcome = json.loads(report.read_text(encoding="utf-8"))
    assert outcome["case_count"] == 1
    assert outcome["cases"][0]["case_id"] == "SYN-001"
    assert outcome["cases"][0]["classification"] == "pass"


def test_scalar_native_end_to_end_and_original_field_details(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    output = tmp_path / "result.json"
    assert _run(register, csv, series, output) == 0
    fields = json.loads(output.read_text())["cases"][0]["metrics"]
    assert {field["verdict"] for field in fields.values()} == {"pass"}
    assert fields["native_reported_volume"]["actual_exact"] == "1800"
    assert fields["peak_time"]["reference"]["token"] in (tmp_path / "native.out").read_text(encoding="utf-8")


@pytest.mark.parametrize("mutation", ["clock", "typed", "duplicate", "modules", "nonfinite", "extra"])
def test_changed_candidate_identity_or_representation_rejected(tmp_path: Path, mutation: str) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    document = json.loads(series.read_text())
    row = document["cases"][0]
    if mutation == "clock":
        row["h_hex"] = (1.0).hex()
    elif mutation == "typed":
        row["event_input_sha256"] = "c" * 64
    elif mutation == "duplicate":
        document["cases"].append(dict(row))
    elif mutation == "modules":
        document["module_sha256"] = {"other.py": "d" * 64}
    elif mutation == "nonfinite":
        row["q_hex"][1] = "inf"
    else:
        document["cases"].append({**row, "case_id": "undeclared"})
    _write(series, document)
    assert _run(register, csv, series, tmp_path / "result.json") != 0


@pytest.mark.parametrize("mutation", ["nonfinite_volume", "unsafe", "truncated", "missing", "unsupported", "selector"])
def test_native_field_availability_and_invalidity_propagate(tmp_path: Path, mutation: str) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    document = json.loads(register.read_text())
    case = document["cases"][0]
    native = tmp_path / "native.out"
    expected = "invalid"
    if mutation == "nonfinite_volume":
        native.write_text(native.read_text(encoding="utf-8").replace("1800.0", "NaN"), encoding="utf-8")
    elif mutation == "unsafe":
        case["scalar_binding"]["report"]["path"] = "../outside.out"
    elif mutation == "truncated":
        native.write_text(native.read_text(encoding="utf-8").rsplit("2 1.00", 1)[0], encoding="utf-8")
        expected = "incomplete"
    elif mutation == "missing":
        native.unlink()
        expected = "incomplete"
    elif mutation == "unsupported":
        case["scalar_binding"]["policy_id"] = "unqualified-profile"
        expected = "unsupported"
    else:
        case["scalar_binding"]["scalar_selectors"]["volume"]["unit"] = "ML"
    if native.exists():
        case["reference"] = _locator(native)
        case["files"] = [_locator(native)]
        if mutation != "unsafe":
            case["scalar_binding"]["report"] = _locator(native)
    _write(register, document)
    output = tmp_path / "result.json"
    assert _run(register, csv, series, output) == 1
    assert json.loads(output.read_text())["cases"][0]["classification"] == expected


def test_custody_required_and_two_zero_flow_metrics_remain_independent(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    missing = tmp_path / "missing-custody.json"
    assert _run(register, csv, series, missing, custody=False) == 1
    assert json.loads(missing.read_text())["cases"][0]["classification"] == "incomplete"
    document = json.loads(series.read_text())
    document["cases"][0]["q_hex"] = [(0.0).hex(), (0.0).hex()]
    _write(series, document)
    csv.write_text(csv.read_text().replace("1.000", "0.000"), encoding="utf-8")
    native = tmp_path / "native.out"
    native.write_text(
        native.read_text(encoding="utf-8").replace("1.000", "0.000").replace("1800.0", "0.0"), encoding="utf-8"
    )
    register_document = json.loads(register.read_text())
    case = register_document["cases"][0]
    case["reference"] = case["scalar_binding"]["report"] = _locator(native)
    case["files"] = [_locator(native)]
    _write(register, register_document)
    output = tmp_path / "zero.json"
    assert _run(register, csv, series, output) == 1
    fields = json.loads(output.read_text())["cases"][0]["metrics"]
    assert fields["peak_time"]["verdict"] == "incomplete"
    assert fields["native_reported_volume"]["verdict"] == "pass"


def test_volume_discrepancy_has_exact_field_path_and_original_token(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    native = tmp_path / "native.out"
    native.write_text(native.read_text(encoding="utf-8").replace("1800.0", "1801.0"), encoding="utf-8")
    document = json.loads(register.read_text())
    case = document["cases"][0]
    case["reference"] = case["scalar_binding"]["report"] = _locator(native)
    case["files"] = [_locator(native)]
    _write(register, document)
    output = tmp_path / "mismatch.json"
    assert _run(register, csv, series, output) == 1
    outcome = json.loads(output.read_text())["cases"][0]
    assert outcome["classification"] == "fail"
    assert outcome["metrics"]["peak_magnitude"]["verdict"] == "pass"
    assert outcome["mismatches"][0]["field_path"] == "metrics.native_reported_volume"
    assert outcome["mismatches"][0]["actual_exact"] == "1800"


def test_missing_candidate_rows_remain_incomplete_and_explicit_unsupported_propagates(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    csv.write_text("\n".join(csv.read_text().splitlines()[:-1]) + "\n", encoding="utf-8")
    output = tmp_path / "incomplete.json"
    assert _run(register, csv, series, output) == 1
    assert json.loads(output.read_text())["cases"][0]["classification"] == "incomplete"
    document = json.loads(series.read_text())
    document["cases"][0].update(status="unsupported", reason="explicit unqualified source path")
    _write(series, document)
    unsupported = tmp_path / "unsupported.json"
    assert _run(register, csv, series, unsupported) == 1
    assert json.loads(unsupported.read_text())["cases"][0]["classification"] == "unsupported"


@pytest.mark.parametrize("field", ["path", "sha256", "size_bytes"])
def test_scalar_and_ordinate_reports_require_one_locator(tmp_path: Path, field: str) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    document = json.loads(register.read_text())
    case = document["cases"][0]
    other = tmp_path / "other.out"
    # Both reports are individually authenticatable and numerically equivalent.
    other.write_bytes((tmp_path / "native.out").read_bytes() + b"\nDifferent retained report\n")
    if field == "path":
        case["scalar_binding"]["report"] = _locator(other)
        case["files"].append(_locator(other))
    elif field == "sha256":
        case["scalar_binding"]["report"][field] = _locator(other)[field]
    else:
        case["scalar_binding"]["report"][field] += 1
    _write(register, document)
    output = tmp_path / "mixed-report.json"
    assert _run(register, csv, series, output) == 1
    result = json.loads(output.read_text())["cases"][0]
    assert result["classification"] == "invalid"
    assert "same original report" in result["reason"]


@pytest.mark.parametrize(
    "mismatch", ["source_cli_wheel", "source_metadata_wheel", "wheel_without_artifact", "wheel_wrong_artifact"]
)
def test_source_and_wheel_evidence_cannot_be_mixed(tmp_path: Path, mismatch: str) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    artifact = tmp_path / "candidate.whl"
    artifact.write_bytes(b"authored candidate identity control")
    document = json.loads(series.read_text())
    args = [
        "compare",
        str(register),
        "--csv",
        str(csv),
        "--series",
        str(series),
        "--custody-root",
        str(tmp_path),
        "--implementation",
        REVISION,
    ]
    if mismatch == "source_cli_wheel":
        args.extend(["--wheel", str(artifact)])
    elif mismatch == "source_metadata_wheel":
        document["wheel_sha256"] = _locator(artifact)["sha256"]
    else:
        document.update(mode="wheel", wheel_sha256="f" * 64)
        if mismatch == "wheel_wrong_artifact":
            args.extend(["--wheel", str(artifact)])
    _write(series, document)
    assert rd.main(args) == 2


def test_matching_wheel_provenance_keeps_its_own_identity(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    artifact = tmp_path / "candidate.whl"
    artifact.write_bytes(b"authored matching wheel identity control")
    digest = _locator(artifact)["sha256"]
    document = json.loads(series.read_text())
    document.update(mode="wheel", wheel_sha256=digest)
    _write(series, document)
    dataset = json.loads(register.read_text())
    dataset["qualified_candidates"][REVISION]["wheel_sha256"] = digest
    _write(register, dataset)
    output = tmp_path / "matching-wheel.json"
    assert (
        rd.main(
            [
                "compare",
                str(register),
                "--csv",
                str(csv),
                "--series",
                str(series),
                "--custody-root",
                str(tmp_path),
                "--implementation",
                REVISION,
                "--wheel",
                str(artifact),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    result = json.loads(output.read_text())
    assert result["wheel_sha256"] == digest
    assert result["candidate_series_provenance"]["mode"] == "wheel"


def test_comparison_provenance_uses_loaded_scalar_module_bytes(tmp_path: Path) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    result = tmp_path / "provenance.json"
    assert _run(register, csv, series, result) == 0
    recorded = json.loads(result.read_text(encoding="utf-8"))
    modules = {
        "regression_dataset.py": rd,
        "regression_scalar_adapter.py": regression_scalar_adapter,
        "regression_metrics.py": regression_metrics,
        "rorb_documents.py": rorb_documents,
        "rorb_out.py": rorb_out,
    }
    digests: dict[str, str] = {}
    for name, module in modules.items():
        location = module.__file__
        assert location is not None
        digests[name] = hashlib.sha256(Path(location).read_bytes()).hexdigest()
    assert recorded["comparison_modules_sha256"] == digests
    assert recorded["comparison_module_sha256"] == digests["regression_dataset.py"]


@pytest.mark.parametrize("name", ["regression_scalar_adapter", "regression_metrics"])
def test_modified_scalar_helper_changes_reported_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    register, csv, series = _scalar_fixture(tmp_path)
    module = {"regression_scalar_adapter": regression_scalar_adapter, "regression_metrics": regression_metrics}[name]
    copy = tmp_path / f"{name}.py"
    location = module.__file__
    assert location is not None
    copy.write_bytes(Path(location).read_bytes())
    monkeypatch.setattr(module, "__file__", str(copy))
    initial = tmp_path / "original-provenance.json"
    changed = tmp_path / "changed-provenance.json"
    assert _run(register, csv, series, initial) == 0
    copy.write_bytes(copy.read_bytes() + b"\n# authored altered module bytes\n")
    assert _run(register, csv, series, changed) == 0
    before = json.loads(initial.read_text(encoding="utf-8"))
    after = json.loads(changed.read_text(encoding="utf-8"))
    key = f"{name}.py"
    assert before["comparison_modules_sha256"][key] != after["comparison_modules_sha256"][key]
    assert before["comparison_module_sha256"] == after["comparison_module_sha256"]
    assert before["cases"] == after["cases"]


@pytest.mark.parametrize("token", ["0x1.0p+9999999999", "not-a-hex-float"])
def test_invalid_candidate_hex_converts_to_typed_invalid(tmp_path: Path, token: str) -> None:
    with pytest.raises(ValueError, match=r"canonical float\.hex"):
        stored_float(token)
    register, csv, series = _scalar_fixture(tmp_path)
    document = json.loads(series.read_text(encoding="utf-8"))
    document["cases"][0]["q_hex"][1] = token
    _write(series, document)
    result_path = tmp_path / "invalid-overflow.json"
    assert _run(register, csv, series, result_path) == 1
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["cases"][0]["classification"] == "invalid"
    assert "canonical float.hex" in result["cases"][0]["reason"]
    assert result["counts"] == {"invalid": 1}


@pytest.mark.parametrize(
    ("scalar_state", "expected"),
    [
        ("missing", "incomplete"),
        ("unsupported", "unsupported"),
        ("malformed", "invalid"),
    ],
)
def test_missing_or_invalid_scalar_evidence_cannot_mask_ordinate_failure(
    tmp_path: Path, scalar_state: str, expected: str
) -> None:
    register, csv_path, series = _scalar_fixture(tmp_path)
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    fields = lines[-1].split(",")
    fields[-1] = "2.000"
    lines[-1] = ",".join(fields)
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    document = json.loads(series.read_text(encoding="utf-8"))
    if scalar_state == "missing":
        document["cases"].clear()
    elif scalar_state == "unsupported":
        document["cases"][0].update(status="unsupported", reason="authored unsupported scenario")
    else:
        document["cases"][0]["q_hex"][1] = "0x1.0p+9999999999"
    _write(series, document)
    output = tmp_path / "failed-ordinates.json"
    assert _run(register, csv_path, series, output) == 1
    result = json.loads(output.read_text(encoding="utf-8"))
    case = result["cases"][0]
    assert case["classification"] == "fail"
    assert case["scalar_evidence"]["classification"] == expected
    assert case["mismatches"][0]["site"] == "Hyd001"
    assert result["counts"] == {"fail": 1}


def _stage_combined_original(
    case: dict[str, Any], namespace: dict[str, Any], directory: Path
) -> tuple[LegacyRunFiles, RunModel]:
    """Use the maintained probe's verified byte loader and typed decoder."""
    source_files: dict[str, SourceFile] = {}
    for suffix in (".par", ".catg", ".stm"):
        raw: bytes = namespace["_original_source"](case, suffix)
        name = f"original{suffix}"
        (directory / name).write_bytes(raw)
        source_files[suffix] = SourceFile(name, hashlib.sha256(raw).hexdigest())
    model: RunModel = namespace["_typed_model"](case)
    assert model.storm.pattern_basis == "combined_preburst_percent"
    assert model.storm.preburst_bins == 48
    assert sum(model.storm.percentages, Decimal(0)) == Decimal("102.10")
    assert model.storm.depths_mm == (Decimal("69.02"),) * 5
    return LegacyRunFiles(source_files[".par"], source_files[".catg"], source_files[".stm"]), model


def _execute_combined_original(
    case_id: str,
    sources: LegacyRunFiles,
    model: RunModel,
    directory: Path,
    selection: EngineSelection,
    wheel: Path | None,
) -> tuple[EngineOutcome, Project]:
    project = Project(case_id, "legacy-rorb", sources, engine=selection)
    path = directory / f"{selection.engine}.json"
    write_project(path, project)
    assert load_project(path).run == model
    outcome = run_engine_project(path, wheel_artifact=wheel)
    assert outcome.status == "computed_unvalidated", outcome.diagnostics
    assert outcome.stored_selection == outcome.effective_selection == selection
    assert outcome.native_parity_status == "not_assessed"
    assert outcome.model_sha256 == hashlib.sha256(to_json(model).encode("utf-8")).hexdigest()
    assert outcome.source_file_hashes == tuple(
        (item.path, item.sha256) for item in (sources.parameters, sources.catchment, sources.storm)
    )
    assert outcome.requested_print_ids == ("print_1",)
    assert outcome.control_order[-1] == 7
    assert outcome.control_order.count(7) == 1
    assert len(outcome.hydrographs) == 1
    assert outcome.hydrographs[0].print_id == "print_1"
    assert len(outcome.hydrographs[0].discharge_m3_s) == 301
    assert not outcome.native_raw_time_tokens
    assert outcome.physical_time_hours == tuple(str(index * model.storm.timestep_hours) for index in range(301))
    if wheel is not None:
        assert outcome.verified_wheel_sha256 == hashlib.sha256(wheel.read_bytes()).hexdigest()
    return outcome, project


@pytest.mark.parametrize(
    ("case_id", "excess_mm"),
    [
        ("fig67-ilroc", 24.51),
        ("fig67-kc5-m1", 33.02),
        ("failure-m-above-one", 33.02),
        ("failure-m-below-one", 33.02),
    ],
)
def test_original_combined_preburst_engineering_and_report_local_scalar_diagnostics(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], case_id: str, excess_mm: float
) -> None:
    root = REPO / "tests" / "fixtures" / "regression-v1"
    register = json.loads((root / "register.json").read_bytes())
    case = next(item for item in register["cases"] if item["case_id"] == case_id)
    assert case["coverage"] == "gap"
    assert "scalar_binding" not in case
    namespace = runpy.run_path(str(REPO / "repo-scripts" / "cmd_public_probe.py"))
    sources, model = _stage_combined_original(case, namespace, tmp_path)
    wheel_env = os.environ.get("RUNOFF_ENGINE_WHEEL")
    wheel = Path(wheel_env) if wheel_env else None
    compatible, cmd_project = _execute_combined_original(
        case_id, sources, model, tmp_path, EngineSelection.for_engine("python-cmd"), wheel
    )
    assert namespace["_binding_error"](case, model, compatible, project_to_json(cmd_project)) is None
    compared = rd.compare_fresh_cmd_case(root, case, compatible)
    assert compared["classification"] == "pass"
    assert compared["fresh_reporting"]["classification"] == "incomplete"

    # Report-local binding only: no register edit or independently named physical site.
    selectors = {
        "native_column": "Hyd001",
        "scalar_selectors": {
            "peak": {"line": 391, "character": 26, "ordinal": 1, "unit": "m3/s"},
            "peak_time": {"line": 392, "character": 27, "ordinal": 1, "unit": "h"},
            "volume": {"line": 393, "character": 23, "ordinal": 1, "unit": "m3"},
        },
    }
    site = regression_scalar_adapter.bind_scalars(RorbSource.read(root / case["reference"]["path"]), selectors)
    assert site.physical_name is None
    assert site.volume is not None
    h, dt = stored_cmd_reporting_clock(model.storm.timestep_hours)
    assert (h, dt) == (0.5, 1800.0)
    cmd_series = {
        "q_hex": [value.hex() for value in compatible.hydrographs[0].discharge_m3_s],
        "h_hex": h.hex(),
        "dt_hex": dt.hex(),
    }
    scalars = regression_scalar_adapter.compare_scalars(cmd_series, site)
    assert {field["verdict"] for field in scalars.values()} == {"pass"}

    engineering, _project = _execute_combined_original(
        case_id, sources, model, tmp_path, EngineSelection.for_engine("python"), wheel
    )
    assert engineering.python_diagnostics is not None
    excess = cast("tuple[tuple[float, ...], ...]", engineering.python_diagnostics["rainfall_excess_mm"])
    assert tuple(math.fsum(source) for source in excess) == pytest.approx((excess_mm,) * 5)
    # The same unique terminal control and report column are bound above.
    # This is a computational-outlet diagnostic, not independent physical-node acceptance.
    columns, rows = rd._reference(root, case)  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
    assert columns == ["Inc", "Time", "Hyd001"]
    native_q = tuple(float(row[2]) for row in rows)
    computed_q = engineering.hydrographs[0].discharge_m3_s
    deviation = assess_cmd_deviation(computed_q, native_q, timestep_hours=h)
    receipt = {
        "case_id": case_id,
        "comparison_scope": "source_derived_terminal_code7_not_independent_physical_name",
        "native_reference_sha256": case["reference"]["sha256"],
        "source_sha256": dict(engineering.source_file_hashes),
        "model_sha256": engineering.model_sha256,
        "engineering_project_sha256": engineering.project_sha256,
        "cmd_project_sha256": compatible.project_sha256,
        "implementation_revision": engineering.implementation_revision,
        "verified_wheel_sha256": engineering.verified_wheel_sha256,
        "engineering_profile": engineering.effective_selection.numerical_profile,
        "engineering_q_hex": [value.hex() for value in computed_q],
        "cmd_series": cmd_series,
        "original_raw_peak_time_hours": rows[deviation.cmd_peak_index][1],
        "original_elapsed_peak_time_hours": deviation.cmd_peak_index * h,
        "engineering_elapsed_peak_time_hours": deviation.python_peak_index * h,
        "native_inclusive_reported_volume_token_m3": site.volume.token,
        "report_local_scalar_diagnostics": scalars,
        "deviations": asdict(deviation),
        "peak_difference_absolute_m3_s": abs(deviation.peak_difference_m3_s),
        "volume_difference_absolute_m3": abs(deviation.volume_difference_m3),
        "registered_reporting": "incomplete",
        "native_physical_name": site.physical_name,
        "numerical_acceptance": "unassessed",
    }
    with capsys.disabled():
        print("combined-preburst-diagnostic: " + json.dumps(receipt, sort_keys=True, allow_nan=False))
