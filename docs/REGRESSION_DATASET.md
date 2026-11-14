# Self-contained public regression dataset

The existing [register](../tests/fixtures/regression-v1/register.json) and `runoff_routing.regression_dataset` CLI now serve **50 CMD cases** (44 archived and all six supplemental), **21 native gaps**, ten unchanged independent analytical controls and four authored gaps. Stable IDs, source/order/physical-site mappings, full horizons, units, original one-based increment/time tokens, scalar selectors and executable hashes are retained. No private checkout or RORB installation is needed. Tracks [#81](https://github.com/Chain-Frost/python-runoff-routing/issues/81).

## Evidence and limits

Native references are original CMD 6.44 printed observations. The ten authored cases remain mathematical oracles. All 21 native gaps preserve individual reasons and CMD/RORBwin identities under `native-gaps`; their experimental files are excluded. `all` contains 85 records and intentionally returns non-success.

The bundled Python output is an **immutable prior source-execution snapshot** at `fea9c80c521127325b779ea0ea87ddf77795b290`, independently authenticated before transfer. Its CSV and binary64 hexadecimal series are separate from native truth. `--snapshot` authenticates both payloads, rejects mixed external identities, and reports `cached_candidate_snapshot` / `candidate_execution: not_run`. This compares original observations with prior execution; it does **not** execute or accept today's production solver. The qualified public backend remains pending [#75](https://github.com/Chain-Frost/python-runoff-routing/issues/75). Future actual engine execution must feed this same runner using `--csv` / `--series` and a newly qualified profile. Never copy native references into predictions. No candidate source code or wheel is distributed.

Frozen `cmd644-report-scalars-v1` is unchanged: **19,550 ordinate rows pass**, peak magnitude 50 pass, peak time 48 pass / two incomplete (`fig67-zero`, `wheel-zero`), reported volume 50 pass. Scalar aggregate returns **1**. Reported volume is the native **inclusive sample sum**, distinct from physical volume/conservation. Exact ties, sub-print clocks, physical acceptance and production-engine qualification remain open. No tolerances, defaults or goldens changed.

## Windows / Python 3.14 commands

Use fresh output names: existing destinations are rejected. Install only from the public checkout:

```powershell
py -3.14 -m pip install -e ".[dev]"
New-Item -ItemType Directory -Force .local | Out-Null
$Register = 'tests/fixtures/regression-v1/register.json'
py -3.14 -m runoff_routing.regression_dataset preflight $Register --set cmd-eligible --full-index --output .local/preflight.json
py -3.14 -m runoff_routing.regression_dataset diagnose $Register --case H1-three-source-asymmetric --snapshot --output .local/one.json
py -3.14 -m runoff_routing.regression_dataset compare $Register --set timestep --snapshot --output .local/timestep.json
py -3.14 -m runoff_routing.regression_dataset compare $Register --set cmd-eligible --snapshot --output .local/scalars.json
py -3.14 -m runoff_routing.regression_dataset preflight $Register --set native-all --output .local/native-coverage.json
py -3.14 -m runoff_routing.regression_dataset preflight $Register --set authored --engine python --output .local/analytic.json
py -3.14 -m pytest tests/test_regression_dataset.py tests/test_regression_scalars.py tests/test_regression_public_native.py -q
py -3.14 repo-scripts/check_local.py
```

Preflight / one / timestep / authored exit 0; full scalar and native-all exit 1 by design. For ordinate-only verification (exit 0), pass `tests/fixtures/regression-v1/native-cmd/candidate-snapshot.csv.gz` as `--csv`, with `--implementation fea9c80c521127325b779ea0ea87ddf77795b290`, without `--series` / `--snapshot`. External CSV uses the existing S5 schema; `.gz` is lossless. Existing `--series`, `--wheel` and `--custody-root` remain supported. Bundled cases use relative in-repository bindings and need no custody option. `--wheel` attests the **numerical candidate**, distinct from the comparator wheel.

Selections: `cmd-eligible` (50), `cmd-selected` (44 archive), `supplemental` (six), `cmd-migrated-eight`, `timestep`, `authored` (ten), `smoke` (original three authored), `native-all` (71), `native-gaps` (21), and `all` (85).

### Installed comparator wheel and complete tests

Use a fresh external directory. Copy test scaffolding; isolated mode and import verification ensure the installed package executes, even where scaffold tests inspect source-file existence. Clear any source PYTHONPATH in the shell before these commands.

```powershell
$Checkout = (Get-Location).Path
$Verify = Join-Path $env:TEMP ('runoff81-' + [guid]::NewGuid())
New-Item -ItemType Directory $Verify | Out-Null
py -3.14 -m build --wheel --outdir "$Verify/dist"
py -3.14 -m venv "$Verify/env"
$Python = Join-Path $Verify 'env/Scripts/python.exe'
$Wheel = (Get-ChildItem "$Verify/dist/*.whl").FullName
& $Python -m pip install $Wheel pytest
Get-FileHash $Wheel -Algorithm SHA256
New-Item -ItemType Directory "$Verify/checkout" | Out-Null
foreach ($Name in @('tests','examples','repo-scripts','src','.github','pyproject.toml','ruff.toml')) {
    Copy-Item -LiteralPath (Join-Path $Checkout $Name) -Destination "$Verify/checkout" -Recurse
}
Push-Location "$Verify/checkout"
& $Python -I -c "import runoff_routing; print(runoff_routing.__file__); assert 'site-packages' in runoff_routing.__file__"
& $Python -I -m pytest -m 'not native and not benchmark'
& $Python -I -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --output preflight.json
& $Python -I -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set cmd-eligible --snapshot --output scalars.json
Pop-Location
```

Data are checkout fixtures, not runtime package files. Wheel-only users pass the public checkout register explicitly. Source/wheel per-case results must agree, including both incomplete times. See the [work record](work/2026-11-15-public-cmd-data.md) for executed commands, hashes, counts and limitations.

## Authentication and curation

Source: private PR #65 at `78d257745e94cdca74d1fdcdc8a615d472a8bf9c`; original register SHA-256 `a9b74dafe5466491a3ed102a3649df72b992e38c915699934f47096a0228e6f7`. All **1,026** indexed originals authenticated before and after transfer, along with the independent custody receipt and all six supplemental original input/report/typed-event/source bindings. Only model, storm, effective controls, report, typed event and source binding are copied. Historical log dumps, empty streams, traces, executables, manuals and research implementations are excluded.

[provenance.json](../tests/fixtures/regression-v1/native-cmd/provenance.json) records original hash/size/name, published locator/hash/size, evidence class and every transform. Shared objects require identical original SHA-256 and file kind; each case retains explicit references. Different originals yielding the same sanitised payload retain separate original identities.

`basename-pad-path-v1` replaces every drive-qualified path from a drive letter, colon and slash/backslash through end of line with its final basename, right-padded with ASCII spaces to original byte length. This removes machine paths from parameter locators, storm comments and report headers. Line endings, line numbers, character positions, timestamps, scalar selectors, numerical tokens and horizons remain unchanged. These are **derivatives**, never claimed byte-identical originals. Every replacement offset/length/text and original/published hash is retained. Typed events and source bindings retain original bytes. Candidate CSV uses gzip with mtime zero; decompressed hash equals the prior accepted export. Candidate series retain original bytes.

Owner approval on 2026-11-15 is prospective. Historical AUTHORIZATION.json and private originals remain unchanged. Approval excludes unrelated research, executables, manuals and OS traces. No native run, merge, release, new hosted automation or numerical-stage closure is part of this transfer.
