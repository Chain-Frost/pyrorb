"""Issue #140: content classification, PAR-led import, source bindings and relocatable edits."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from runoff_routing.project_json import (
    LegacyRunFiles,
    ProjectError,
    import_rorb_project,
    load_project,
    main,
    save_project_as,
    write_project,
)
from runoff_routing.rorb_codec import serialize_catg, serialize_cmd_par, serialize_design_stm
from runoff_routing.rorb_model import (
    CatchmentModel,
    ControlStep,
    LossValue,
    ParameterSet,
    PrintLocation,
    Reach,
    RoutingValue,
    RunModel,
    StormModel,
    SubArea,
    to_json,
)
from runoff_routing.rorb_par import inspect_par_bytes, read_par_file


def _inputs(
    root: Path,
    *,
    cat_token: str = "catchment.catg",
    storm_token: str = "storm.stm",
    cat_name: str = "catchment.catg",
    storm_name: str = "storm.stm",
) -> tuple[Path, Path, Path, RunModel]:
    root.mkdir(parents=True, exist_ok=True)
    params = ParameterSet(
        cat_token, storm_token, True, 3, 1, 1, 1,
        (RoutingValue(1, Decimal("12"), Decimal("0.8")),),
        (LossValue(1, 1, Decimal("20"), Decimal("2")),),
    )
    catchment = CatchmentModel(
        "Synthetic model", (SubArea("area_1", Decimal("2"), "A"),),
        (Reach("reach_1", Decimal("3"), "Reach 1 Sub-area A"),),
        (ControlStep(1, "area_1", "reach_1", label="Reach 1 Sub-area A"),
         ControlStep(7, print_id="print_1", label="Outlet")),
        (PrintLocation("print_1", "Outlet"),),
    )
    storm = StormModel(
        "Synthetic storm", Decimal("0.5"), 10, 0,
        (Decimal("25"), Decimal("75")), (Decimal("10"),), ("area_1",),
    )
    run = RunModel(params, catchment, storm)
    par_path = root / "settings.par"
    cat_path = root / cat_name
    storm_path = root / storm_name
    cat_path.parent.mkdir(parents=True, exist_ok=True)
    storm_path.parent.mkdir(parents=True, exist_ok=True)
    par_path.write_bytes(serialize_cmd_par(params).replace(b"\n", b"\r\n"))
    cat_path.write_bytes(serialize_catg(catchment))
    storm_path.write_bytes(serialize_design_stm(storm))
    return par_path, cat_path, storm_path, run


def _import(target: Path, par: Path, **kwargs: Path) -> None:
    write_project(
        target,
        import_rorb_project(
            target, identifier="example", rainfall_profile="legacy-rorb", parameters=par, **kwargs
        ),
    )


def test_par_bytes_recognise_cmd_and_inspect_without_following_references(tmp_path: Path) -> None:
    par, _, _, run = _inputs(tmp_path / "inputs")
    parsed = inspect_par_bytes(par.read_bytes())
    assert parsed.kind == "cmd_par"
    assert parsed.status == "parsed"
    assert parsed.parameters is not None
    assert parsed.parameters.catchment_reference == run.parameters.catchment_reference
    assert parsed.source.sha256 == hashlib.sha256(par.read_bytes()).hexdigest()
    assert read_par_file(par).source.path == par.absolute()


def test_genuine_capture_layout_recognised_only_as_deferred_rorbwin() -> None:
    # Structural analogue of retained native GUI 6.52 saved-PAR captures:
    # 755 lines, ordered directory/CATG/STM and ARR header, trailing -999 tables.
    header = [
        r"C:\analysis\project", " 3", "",
        r"C:\analysis\project\catchment.catg", r"C:\analysis\project\storm.stm",
        "", "", "", " 3", "T", " 3", " 3", " 1",
        "  14   0  19   0   1 200   0      0.00",
        "ARR2016  SinglARR16", "    T    F",
        r"C:\PROGRAM FILES\RORBWIN\SampleData\IFD_Aust.map", "",
        r"C:\analysis\project", "   1  11   1   1  11  12  12   5   1   4   2   2   1   1 100",
    ]
    data = ("\n".join([*header, *(" -999.00 " for _ in range(735))]) + "\n").encode()
    parsed = inspect_par_bytes(data)
    assert parsed.kind == "rorbwin_saved_par"
    assert parsed.status == "unsupported"
    assert parsed.parameters is None
    assert parsed.diagnostics[0].code == "rorbwin_saved_par_deferred"
    for other in (b"", b"arbitrary PAR data\n", b"ARR2016\n", data[:70]):
        unknown = inspect_par_bytes(other)
        assert unknown.kind == "unknown_par"


def test_par_only_stages_and_reopens_without_original_source_tree(tmp_path: Path) -> None:
    par, cat, stm, run = _inputs(tmp_path / "original")
    root = tmp_path / "new project"
    root.mkdir()
    target = root / "hydrology.json"
    _import(target, par)
    loaded = load_project(target)
    assert loaded.run == run
    assert tuple(item.role for item in loaded.project.source_bindings) == (
        "parameters", "catchment", "storm"
    )
    assert tuple(item.origin for item in loaded.project.source_bindings) == (
        "explicit", "embedded", "embedded"
    )
    assert json.loads(target.read_text())["schema_version"] == 3
    assert isinstance(loaded.project.model_source, LegacyRunFiles)
    original = (par.read_bytes(), cat.read_bytes(), stm.read_bytes())
    for binding, raw in zip(loaded.project.source_bindings, original, strict=True):
        assert (root / binding.staged.path).read_bytes() == raw
        assert binding.staged.sha256 == hashlib.sha256(raw).hexdigest()
    shutil.rmtree(par.parent)
    assert load_project(target).run == run


def test_missing_reference_exposes_declared_token_and_override(tmp_path: Path) -> None:
    par, cat, stm, run = _inputs(tmp_path / "legacy", cat_token="obsolete.catg")
    target = tmp_path / "project.json"
    with pytest.raises(ProjectError, match=r"catchment.*obsolete.catg.*--catchment"):
        _import(target, par)
    assert not (tmp_path / "sources").exists()
    _import(target, par, catchment=cat)
    loaded = load_project(target)
    assert loaded.run == run
    binding = loaded.project.source_bindings[1]
    assert binding.origin == "override"
    assert binding.declared_reference == "obsolete.catg"
    assert binding.selected_reference == str(cat)
    assert binding.staged.path.startswith("sources/")


def test_spaced_quoted_and_windows_relative_path_tokens(tmp_path: Path) -> None:
    par, _, _, run = _inputs(
        tmp_path / "original", cat_token=r'"nested\my catchment.catg"',
        cat_name="nested/my catchment.catg", storm_token='"storm.stm"',
    )
    target = tmp_path / "project.json"
    _import(target, par)
    assert load_project(target).run == run


@pytest.mark.skipif(os.name == "nt", reason="Foreign-path diagnostic is POSIX-specific")
@pytest.mark.parametrize("token", [
    r"C:\Work\catchment.catg",
    r"\\server\share\catchment.catg",
    r"C:relative.catg",
])
def test_foreign_drive_and_unc_do_not_fall_back_to_basename(tmp_path: Path, token: str) -> None:
    par, _, _, _ = _inputs(tmp_path / "input", cat_token=token)
    target = tmp_path / "project.json"
    with pytest.raises(ProjectError, match="override|--catchment"):
        _import(target, par)
    assert not (tmp_path / "sources").exists()


def test_explicit_reference_base_does_not_use_cwd(tmp_path: Path) -> None:
    par, cat, _, _ = _inputs(tmp_path / "a", cat_token="other/catchment.catg")
    supplied = tmp_path / "new base"
    (supplied / "other").mkdir(parents=True)
    (supplied / "other" / "catchment.catg").write_bytes(cat.read_bytes())
    (_, _, stm, _) = _inputs(supplied, cat_token="other/catchment.catg")
    (supplied / "storm.stm").write_bytes(stm.read_bytes())
    target = tmp_path / "project.json"
    _import(target, par, base_directory=supplied)
    assert load_project(target).project.source_bindings[1].resolved_source == str(
        (supplied / "other/catchment.catg").absolute()
    )


def test_edit_save_relocate_reopen_retains_original_bytes_and_edited_settings(tmp_path: Path) -> None:
    par, _, _, run = _inputs(tmp_path / "origin")
    original_root = tmp_path / "project-a"
    relocated = tmp_path / "project-b"
    original_root.mkdir()
    relocated.mkdir()
    target = original_root / "project.json"
    _import(target, par)
    edited_routing = (replace(run.parameters.routing[0], kc=Decimal("27.125")),)
    edited = replace(run, parameters=replace(run.parameters, routing=edited_routing))
    output = relocated / "edited.json"
    save_project_as(target, output, effective_run=edited)
    shutil.rmtree(original_root)
    shutil.rmtree(par.parent)
    loaded = load_project(output)
    assert loaded.run == edited
    assert loaded.project.effective_run == edited
    assert loaded.project.source_bindings[1].origin == "embedded"
    assert loaded.project.engine.engine == "python-cmd"
    assert isinstance(loaded.project.model_source, LegacyRunFiles)
    pinned = loaded.project.model_source.parameters
    assert (relocated / pinned.path).read_bytes() == serialize_cmd_par(run.parameters).replace(
        b"\n", b"\r\n"
    )


def test_cli_import_inspect_save_and_no_overwrite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    par, cat, _, run = _inputs(tmp_path / "inputs", cat_token="stale.catg")
    target = tmp_path / "first.json"
    assert main(["inspect-par", str(par)]) == 0
    assert json.loads(capsys.readouterr().out)["references"]["catchment"] == "stale.catg"
    assert main([
        "import-rorb", "case-one", "legacy-rorb", str(par), str(target),
        "--catchment", str(cat),
    ]) == 0
    capsys.readouterr()
    edited = replace(
        run, parameters=replace(run.parameters, routing=(RoutingValue(1, Decimal("15"), Decimal("0.8")),))
    )
    edited_file = tmp_path / "effective.json"
    edited_file.write_text(to_json(edited), encoding="utf-8")
    destination = tmp_path / "edited.json"
    assert main(["save-run", str(target), str(edited_file), str(destination)]) == 0
    assert load_project(destination).run == edited
    capsys.readouterr()
    assert main(["save-run", str(target), str(edited_file), str(destination)]) == 2


def test_import_fails_without_partial_sources_for_invalid_cat_and_occupied_target(tmp_path: Path) -> None:
    par, cat, _, _ = _inputs(tmp_path / "original")
    cat.write_bytes(b"OLD PLAIN CAT\n")
    target = tmp_path / "project.json"
    with pytest.raises(ProjectError, match="supported run"):
        _import(target, par)
    assert not (tmp_path / "sources").exists()
    cat.write_bytes(b"OLD PLAIN CAT\n")
    target.write_text("already here", encoding="utf-8")
    with pytest.raises(FileExistsError):
        _import(target, par)
