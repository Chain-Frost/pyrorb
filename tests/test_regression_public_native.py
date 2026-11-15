"""Public curated CMD data reuse the maintained runner and immutable snapshot contract."""

from __future__ import annotations

import gzip
import hashlib
import json
import runpy
import shutil
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from runoff_routing import regression_dataset as rd
from runoff_routing.rorb_codec import parse_catg

DATA = Path(__file__).absolute().parent / "fixtures" / "regression-v1"
REGISTER = DATA / "register.json"


def test_recovered_pinned_pr16_export_matches_historical_crlf_source() -> None:
    """Preserve both original identities while proving the complete serialization relationship."""
    provenance = json.loads((DATA / "native-cmd" / "provenance.json").read_bytes())
    export = provenance["independent_2026_11_15_closeout"]["upstream_pr16_export"]
    assert export["exporter_revision"] == "a323d5709f7ce14c6adf46f01e0224b60668340c"
    raw = (DATA / export["output"]["path"]).read_bytes()
    assert len(raw) == 2818
    assert hashlib.sha256(raw).hexdigest() == "67ae955b515a0594298fa1b0e48005d4d12db520e0a7dc582f37e6e06d6ad815"
    register = json.loads(REGISTER.read_bytes())
    historical = next(case for case in register["cases"] if case["case_id"] == "pyromb-pr2-full")
    source = next(item for item in historical["inputs"] if item["path"].endswith(".catg"))
    original = (DATA / source["path"]).read_bytes()
    assert len(original) == 2913
    assert hashlib.sha256(original).hexdigest() == "2ad4663ddeaacdfd4bba4b199a29d3eed7bcb6d9f096ff62f6d9d107330bd247"
    assert b"\r" not in raw
    assert raw.replace(b"\n", b"\r\n") == original
    model = parse_catg(raw).model
    assert model == parse_catg(original).model
    assert model.reach_mode == "explicit_reach_types"
    assert tuple(step.code for step in model.controls) == (1, 3, 1, 4, 2, 3, 1, 2, 4, 5, 2, 7)
    assert tuple(area.impervious_fraction for area in model.subareas) == tuple(
        map(Decimal, ("0", "0.5", "0.2", "0", "0", "0"))
    )


def test_authenticated_feature_evidence_still_fails_closed_as_gap(tmp_path: Path) -> None:
    """A complete retained native table does not silently promote feature qualification."""
    result = _run(tmp_path, group="native-gaps")
    assert result["counts"] == {"incomplete": 21}
    register = json.loads(REGISTER.read_bytes())
    cases = [case for case in register["cases"] if "evidence_review" in case]
    assert len(cases) == 8
    for case in cases:
        assert case["coverage"] == "gap"
        assert "cmd-eligible" not in case["sets"]
        assert case["clock"]["row_count"] == 301
        assert len(case["files"]) == 5
        assert case["evidence_review"]["status"] == "authenticated_original_pending_admission"


def _run(tmp_path: Path, *, group: str = "cmd-eligible", snapshot: bool = False) -> dict[str, Any]:
    output = tmp_path / f"{group}-{snapshot}.json"
    args = ["compare" if snapshot else "preflight", str(REGISTER), "--set", group, "--output", str(output)]
    if snapshot:
        args.append("--snapshot")
    assert rd.main(args) in {0, 1}
    return json.loads(output.read_bytes())


def test_curated_population_and_full_snapshot(tmp_path: Path) -> None:
    """Missing clocks remain incomplete even while all native ordinates and volumes pass."""
    assert _run(tmp_path)["counts"] == {"verified": 50}
    result = _run(tmp_path, snapshot=True)
    assert result["counts"] == {"pass": 48, "incomplete": 2}, result["cases"][0]["reason"]
    assert result["policy_id"] == "cmd644-printed-interval-v1"
    assert {case["policy_id"] for case in result["cases"]} == {"cmd644-printed-interval-v1"}
    assert result["scalar_policy_sha256"] == "a0be5aa27e61813b120a30aaa8527961365c88af81ea77e881585bf68703bd50"
    assert result["run_kind"] == "cached_candidate_snapshot"
    assert result["candidate_execution"].startswith("not_run")
    assert sum(case["reference_rows"] for case in result["cases"]) == 19_550
    for field in ("peak_magnitude", "native_reported_volume"):
        assert Counter(case["metrics"][field]["verdict"] for case in result["cases"]) == {"pass": 50}
    assert {case["case_id"] for case in result["cases"] if case["classification"] == "incomplete"} == {
        "fig67-zero",
        "wheel-zero",
    }
    assert _run(tmp_path, group="native-all")["counts"] == {"verified": 50, "incomplete": 21}
    assert _run(tmp_path, group="authored")["counts"] == {"verified": 10}


def test_unvalidated_candidate_status_requires_authenticated_snapshot(tmp_path: Path) -> None:
    """Legacy computed_unvalidated outputs cannot pass as arbitrary external candidates."""
    register = json.loads(REGISTER.read_bytes())
    snapshot = DATA / register["candidate_snapshot"]["csv"]["path"]
    out = tmp_path / "untrusted-legacy-candidate.json"
    assert (
        rd.main(
            [
                "diagnose",
                str(REGISTER),
                "--case",
                "H1-three-source-asymmetric",
                "--csv",
                str(snapshot),
                "--implementation",
                register["candidate_snapshot"]["implementation_revision"],
                "--output",
                str(out),
            ]
        )
        == 1
    )
    result = json.loads(out.read_bytes())
    assert result["cases"][0]["classification"] == "invalid"
    assert "computed_unvalidated" in result["cases"][0]["reason"]


def test_public_payload_inventory_and_lossless_candidate() -> None:
    provenance = json.loads((DATA / "native-cmd" / "provenance.json").read_bytes())
    assert provenance["authentication_before"] == provenance["authentication_after"]
    assert provenance["authentication_before"]["files"] == 1026
    for record in provenance["files"]:
        published = record["published"]
        raw = (DATA / published["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == published["sha256"]
        assert len(raw) == published["size_bytes"]
        if record["transform"] == "gzip-mtime-zero":
            original = gzip.decompress(raw)
            assert hashlib.sha256(original).hexdigest() == record["original_sha256"]
            assert len(original) == record["original_size_bytes"]
        elif record["transform"] == "identity":
            assert published["sha256"] == record["original_sha256"]
        else:
            assert record["transform"] == "basename-pad-path-v1"
            assert len(raw) == record["original_size_bytes"]
            for change in record["replacements"]:
                start = change["offset"]
                assert raw[start : start + change["length"]] == change["replacement_ascii"].encode("ascii")


@pytest.mark.parametrize("key", ["csv", "series"])
def test_snapshot_changed_bytes_are_rejected(tmp_path: Path, key: str) -> None:
    shutil.copytree(DATA, tmp_path / "data")
    register = json.loads(REGISTER.read_bytes())
    target = tmp_path / "data" / register["candidate_snapshot"][key]["path"]
    target.write_bytes(target.read_bytes() + b" ")
    assert rd.main(["compare", str(tmp_path / "data" / "register.json"), "--snapshot"]) == 2


def test_snapshot_cannot_mix_identities() -> None:
    assert rd.main(["compare", str(REGISTER), "--snapshot", "--implementation", "a" * 40]) == 2


def test_native_full_index_uses_checkout_stable_attributes(tmp_path: Path) -> None:
    """Original native file-index checks must pass after Linux or Windows checkout."""
    attributes = DATA / ".gitattributes"
    index = json.loads((DATA / "native-cmd" / "index.json").read_bytes())
    fingerprint = index["files"][".gitattributes"]
    original = attributes.read_bytes()
    assert original == b"scalar-policy.md -text\n"
    assert fingerprint["size_bytes"] == len(original)
    assert fingerprint["sha256"] == hashlib.sha256(original).hexdigest()

    output = tmp_path / "verified-native-index.json"
    assert rd.main(["preflight", str(REGISTER), "--set", "cmd-eligible", "--full-index", "--output", str(output)]) == 0
    result = json.loads(output.read_bytes())
    assert result["index_files_verified"] == len(index["files"])
    assert result["counts"] == {"verified": 50}


@pytest.mark.parametrize(
    ("group", "expected"),
    [("cmd-selected", 44), ("supplemental", 6), ("cmd-migrated-eight", 8)],
)
def test_curated_named_preflight_subsets_are_complete(tmp_path: Path, group: str, expected: int) -> None:
    """Eligible source subgroups are self-contained without an external custody root."""
    output = tmp_path / f"{group}.json"
    assert rd.main(["preflight", str(REGISTER), "--set", group, "--output", str(output)]) == 0
    result = json.loads(output.read_bytes())
    assert len(result["cases"]) == expected
    assert result["counts"] == {"verified": expected}


def test_curated_one_case_and_timestep_snapshot_diagnosis(tmp_path: Path) -> None:
    """Use only the existing authenticated cached snapshot and original clocks."""
    case_path = tmp_path / "one.json"
    assert (
        rd.main(
            [
                "diagnose",
                str(REGISTER),
                "--case",
                "H1-three-source-asymmetric",
                "--snapshot",
                "--output",
                str(case_path),
            ]
        )
        == 0
    )
    one = json.loads(case_path.read_bytes())
    assert [item["case_id"] for item in one["cases"]] == ["H1-three-source-asymmetric"]
    assert one["cases"][0]["classification"] == "pass"
    assert one["run_kind"] == "cached_candidate_snapshot"
    assert one["candidate_execution"].startswith("not_run")

    subset_path = tmp_path / "timestep.json"
    assert (
        rd.main(
            [
                "compare",
                str(REGISTER),
                "--set",
                "timestep",
                "--snapshot",
                "--output",
                str(subset_path),
            ]
        )
        == 0
    )
    timestep = json.loads(subset_path.read_bytes())
    assert timestep["counts"] == {"pass": 25}
    assert len(timestep["cases"]) == 25
    assert sum(item["reference_rows"] for item in timestep["cases"]) > 0
    assert timestep["run_kind"] == "cached_candidate_snapshot"

@pytest.mark.parametrize(
    "case_id",
    [
        "fig67-ilroc",
        "fig67-kc5-m1",
        "failure-m-above-one",
        "failure-m-below-one",
    ],
)
def test_original_feature_profile_q_study_retains_unadmitted_scalar_status(case_id: str) -> None:
    """Run the *existing* native-input/public-CMD comparator without promoting an original gap."""
    register = json.loads(REGISTER.read_bytes())
    matches = [case for case in register["cases"] if case["case_id"] == case_id]
    assert len(matches) == 1
    case = matches[0]

    assert case["coverage"] == "gap"
    assert case["sets"] == ["all", "native-all", "native-gaps"]
    assert "scalar_binding" not in case
    assert case["engine_profile"]["native_profile"] == "CMD_6.44"
    assert case["engine_profile"]["observed_version"] == "6.44"
    assert case["clock"]["row_count"] == 301
    assert Decimal(case["clock"]["timestep_hours"]) == Decimal("0.5")
    assert case["sites"][0]["native_column_id"] == "Hyd001"
    assert len(case["files"]) == 5
    assert {Path(item["path"]).suffix for item in case["inputs"]} == {".catg", ".stm", ".par"}

    # Load the maintained source-and-wheel probe, not a second parser, runner or Q comparator.
    namespace = runpy.run_path(str(DATA.parents[2] / "repo-scripts" / "cmd_public_probe.py"))
    observed = namespace["_one"](case)
    assert observed["status"] == "printed_pass", observed
    assert observed["rows"] == 301
    assert observed["mismatch_count"] == 0
    assert observed["first_mismatch"] is None
    assert observed["model_print_id"] == case["sites"][0]["model_print_id"]
    assert observed["original_native_column_id"] == "Hyd001"
    assert observed["site_identity_evidence"] == case["observations"]["physical_site_identity"]
    assert observed["computed_time_rows"] == 301
    assert Decimal(str(observed["computed_time_start_hours"])) == 0
    assert Decimal(str(observed["computed_time_end_hours"])) == 150
    assert observed["original_input_sha256"] == {
        Path(source["path"]).suffix: source["sha256"] for source in case["inputs"]
    }
    # A Q pass is not a report peak/clock/volume pass without independent scalar binding.
    assert observed["fresh_reporting"] == {
        "classification": "incomplete",
        "reason": "Original native scalar binding is unavailable",
    }


@pytest.mark.parametrize(
    "case_id",
    [
        "fig67-ilroc",
        "fig67-kc5-m1",
        "failure-m-above-one",
        "failure-m-below-one",
        "failure-zero-reach",
        "failure-negative-reach",
        "failure-negative-reach-repeat",
        "fig67-code11",
    ],
)
def test_eight_original_capture_dispositions_remain_explicit_gaps(case_id: str) -> None:
    """Source preservation does not change membership in the 50-case numerical population."""
    register = json.loads(REGISTER.read_bytes())
    case = next(item for item in register["cases"] if item["case_id"] == case_id)
    assert case["coverage"] == "gap"
    assert case["sets"] == ["all", "native-all", "native-gaps"]
    assert case["expectations"]["python-cmd"]["status"] == "not_assessed"
    assert "cmd-eligible" not in case["sets"]
