"""Public curated CMD data reuse the maintained runner and immutable snapshot contract."""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from runoff_routing import regression_dataset as rd

DATA = Path(__file__).absolute().parent / "fixtures" / "regression-v1"
REGISTER = DATA / "register.json"


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
    assert result["counts"] == {"pass": 48, "incomplete": 2}
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
