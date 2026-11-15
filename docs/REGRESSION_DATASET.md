# Self-contained public regression dataset

The existing [register](../tests/fixtures/regression-v1/register.json) and `runoff_routing.regression_dataset` CLI now serve **50 CMD cases** (44 archived and all six supplemental), **21 native gaps**, ten unchanged independent analytical controls and four authored gaps. Stable IDs, source/order/physical-site mappings, full horizons, units, original one-based increment/time tokens, scalar selectors and executable hashes are retained. No private checkout or RORB installation is needed. Tracks [#81](https://github.com/Chain-Frost/python-runoff-routing/issues/81).

## Current CMD evidence status (15 November 2026)

Merged #135 has an independently audited exact-head fresh 50-case source/isolated-wheel probe: **50/50 printed-Q passes across 19,550 ordinates, 48 scalar passes, and two incomplete undefined zero-flow peak times** (`fig67-zero`, `wheel-zero`). H2, N4 and `pyromb-novel-storm` stored h/dt now pass under the original source-hex contract; the older **45-pass/five-incomplete** results elsewhere in this document belong to their separately cited historical revisions. Current main `0675d75` has green [quality CI 43717183197](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43717183197); no new native launch is implied. [Evidence PR #133](https://github.com/Chain-Frost/python-runoff-routing/pull/133) preserves eight authenticated captures plus exact upstream PR16 producer bytes separately, **without promoting four studied original profiles** into the 50-case accepted scope. The corresponding [dated current disposition](work/2026-11-15-independent-native-closeout.md) records the four admission limits and the remaining four explicit unsupported/gap states.

## Evidence and limits

Native references are original CMD 6.44 printed observations. The ten authored cases remain mathematical oracles. All 21 native gaps preserve individual reasons and CMD/RORBwin identities under `native-gaps`; their experimental files are excluded. `all` contains 85 records and intentionally returns non-success.

The bundled Python output is an **immutable prior source-execution snapshot** at `fea9c80c521127325b779ea0ea87ddf77795b290`, independently authenticated before transfer. Its CSV and binary64 hexadecimal series are separate from native truth. The cached CSV records the original execution state `computed_unvalidated`: only the SHA-authenticated `--snapshot` path permits that legacy status to undergo an offline diagnostic comparison. An arbitrary external candidate CSV with this status is still rejected by the general fail-closed computation-state gate. `--snapshot` authenticates both payloads, rejects mixed external identities, and reports `cached_candidate_snapshot` / `candidate_execution: not_run`. This compares original observations with prior execution; it does **not** execute or accept today's production solver. The bounded public `python-cmd` backend is integrated through merged [#79](https://github.com/Chain-Frost/python-runoff-routing/pull/79), but full numerical equivalence and physical accuracy are not accepted. Its fresh actual source/wheel diagnostic is separate from `--snapshot`, as described below. The existing runner still supports externally qualified `--csv` / `--series` comparisons; do not copy native references into predictions. No standalone historical candidate source or wheel is distributed.

Frozen `cmd644-report-scalars-v1` is unchanged: **19,550 ordinate rows pass**, peak magnitude 50 pass, peak time 48 pass / two incomplete (`fig67-zero`, `wheel-zero`), reported volume 50 pass. Scalar aggregate returns **1**. Reported volume is the native **inclusive sample sum**, distinct from physical volume/conservation. Exact ties, sub-print clocks, physical acceptance and production-engine qualification remain open. No tolerances, defaults or goldens changed.

## Windows / Python 3.13 or 3.14 commands

Use fresh output names: existing destinations are rejected. Install only from the public checkout:

```powershell
py -3.13 -m pip install -e ".[dev]"
New-Item -ItemType Directory -Force .local | Out-Null
$Register = 'tests/fixtures/regression-v1/register.json'
py -3.13 -m runoff_routing.regression_dataset preflight $Register --set cmd-eligible --full-index --output .local/preflight.json
py -3.13 -m runoff_routing.regression_dataset diagnose $Register --case H1-three-source-asymmetric --snapshot --output .local/one.json
py -3.13 -m runoff_routing.regression_dataset compare $Register --set timestep --snapshot --output .local/timestep.json
py -3.13 -m runoff_routing.regression_dataset compare $Register --set cmd-eligible --snapshot --output .local/scalars.json
py -3.13 -m runoff_routing.regression_dataset preflight $Register --set native-all --output .local/native-coverage.json
py -3.13 -m runoff_routing.regression_dataset preflight $Register --set authored --engine python --output .local/analytic.json
py -3.13 -m pytest tests/test_regression_dataset.py tests/test_regression_scalars.py tests/test_regression_public_native.py -q
py -3.13 repo-scripts/check_local.py
```

Preflight / one / timestep / authored exit 0; the complete scalar comparison and `native-all` exit 1 by design. **The bundled `candidate-snapshot.csv.gz` is not an ordinary `--csv` ordinate-only pass fixture:** its original `computed_unvalidated` execution status is deliberately rejected by the general candidate-state guard (50 `invalid` classifications, exit 1), even when the historical `--implementation` SHA is supplied. Use `--snapshot` for the authenticated cached comparison of all 19,550 native ordinates and scalar fields; this returns 48 pass / two incomplete overall (exit 1) because zero-flow peak times remain unresolved. An **ordinate-only pass (exit 0)** requires a separately executed and qualified engine CSV whose case records have valid `computed/pass` states; no such fresh production-engine execution is bundled. The external candidate format remains the existing S5 CSV schema; `.gz` is supported losslessly. Existing `--series`, `--wheel` and `--custody-root` remain supported. Bundled cases use relative in-repository bindings and need no custody option. `--wheel` attests the **numerical candidate**, distinct from the comparator wheel.

Selections: `cmd-eligible` (50), `cmd-selected` (44 archive), `supplemental` (six), `cmd-migrated-eight`, `timestep`, `authored` (ten), `smoke` (original three authored), `native-all` (71), `native-gaps` (21), and `all` (85).

### Fresh actual `python-cmd` diagnosis — distinct from the historical snapshot

From a clean source checkout using Python 3.13 or 3.14 on either Linux or Windows, run the **existing** bounded original-input CMD probe; it calls the existing S1 source decoders and the public `python-cmd` engine, without launching RORB or importing private investigation data:

```sh
python3.13 repo-scripts/cmd_public_probe.py
```

It reads the same authenticated published register, visits **all 50 eligible original CMD cases**, and reports **36 fully computed original full-horizon printed Q passes / 16,836 ordinates** plus **14 explicit `source_unsupported`**, rather than treating unadmitted inputs as pass or fail. Its `retained_36_case_printed_baseline` is a bounded Q regression. The separate `retained_36_case_fresh_scalar_baseline` also fails the probe on a fresh peak/time/reported-volume failure or missing result in those 36 retained cases, even if their Q series still pass. Neither gate qualifies the full original 50 cases. The output independently checks generated **model elapsed** time `0,h,…,n*h` against typed source time/horizon and does not substitute original one-based CMD `Inc/Time` labels as generated output. Original archive physical `Hyd001` labels remain `unverified`; the one terminal code-7 source association is not an independently observed native physical-site label.

The same **frozen `cmd644-report-scalars-v1`** comparator now evaluates actual newly computed Q, source-derived verified stored h/dt and authenticated original native report selectors, with *separate* fresh peak magnitude, uniquely defined peak time and **inclusive native reported volume** fields. At [public PR #100 exact code `e93c12b`](https://github.com/Chain-Frost/python-runoff-routing/pull/100) [Python 3.13 source+installed wheel CI #43651931036](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43651931036), all **36/36** admitted cases pass each fresh metric and the 50 per-case JSON records are identical between source and installed wheel; the other **14 are `not_run` for scalar**, so `fresh_reporting_full_population` remains explicitly **`incomplete`**. This evidence is **not** the earlier `fea9c80` historical cached 50/48/50 snapshot. No printed-native ties/hidden states, physical trapezoidal volume, conservation, full CMD capability or improved default-engine numerical accuracy are claimed.

For an independently installed public wheel, build and install it outside the checkout as in the next section. With an isolated interpreter and the copied public checkout/fixture scaffold, execute that **same** `repo-scripts/cmd_public_probe.py` using the installed wheel. Check `runoff_routing.__file__` resolves **within the verified installed root outside the checkout** (either a venv's `site-packages` or a fresh `pip --target` directory), record the exact source head/CI merge tree and wheel SHA-256, and compare **all 50 full per-case/field results**, including statuses, source/site/time identities, raw provenance, scalar classifications and first discrepancies. Do not demand a second site-packages replay merely because the approved CI used `--target`. No second runner, catalogue, export or reference regeneration is needed.

### Installed comparator wheel and complete tests

Use a fresh external directory. Copy test scaffolding; isolated mode and import verification ensure the installed package executes, even where scaffold tests inspect source-file existence. This virtual-environment procedure is one **optional implementation** of the installed-wheel check; the approved quality workflow's fresh external `pip --target` directory is equally valid when verified as described above. Clear any source PYTHONPATH in the shell before these commands.

```powershell
$Checkout = (Get-Location).Path
$Verify = Join-Path $env:TEMP ('runoff81-' + [guid]::NewGuid())
New-Item -ItemType Directory $Verify | Out-Null
py -3.13 -m build --wheel --outdir "$Verify/dist"
py -3.13 -m venv "$Verify/env"
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
& $Python -I -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index --output preflight.json
& $Python -I -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set cmd-eligible --snapshot --output scalars.json
& $Python -I repo-scripts/cmd_public_probe.py
Pop-Location
```

Data are checkout fixtures, not runtime package files. Wheel-only users pass the public checkout register explicitly. Source/wheel per-case results must agree, including both incomplete times. See the [work record](work/2026-11-15-public-cmd-data.md) for executed commands, hashes, counts and limitations.

### Portable offline VM target installation

This is an alternative **installation/isolation procedure**, not another regression runner, a new comparator, or an extra operating-system acceptance gate. It works on Linux/Python 3.13 or 3.14 (Windows can use equivalent PowerShell commands) with an **already available, source-matched public wheel** and the exact source checkout, including `tests/fixtures/regression-v1`. No GitHub, private checkout, native executable or package index is needed at execution time. If the VM lacks the checkout/wheel, obtain authenticated copies first; an empty VM cannot perform a project regression. Building a new wheel from an available source checkout is also valid if the pinned build backend is installed.

From the root of that public checkout, using a fresh wheel in `dist/` (replace the filename to match the actual artifact):

~~~sh
set -eu

REPO="$(pwd)"
VERIFY="$(mktemp -d)"
WHEEL="$REPO/dist/python_runoff_routing-0.0.0.dev0-py3-none-any.whl"
test -f "$WHEEL" || { echo "Provide the exact source-matched wheel" >&2; exit 1; }
python3.13 -m pip install --no-deps --no-index --target "$VERIFY/installed" "$WHEEL"
sha256sum "$WHEEL"
export RUNOFF_PROBE="$REPO/repo-scripts/cmd_public_probe.py"

# -I ignores user-site/PYTHONPATH and cwd injection; the chosen source or
# installed package root is added deliberately and its module origin checked.
export RUNOFF_IMPORT_ROOT="$REPO/src"
(cd "$VERIFY" && python3.13 -I -c '
import os, pathlib, runpy, sys
root = pathlib.Path(os.environ["RUNOFF_IMPORT_ROOT"]).resolve()
sys.path.insert(0, str(root))
import runoff_routing
origin = pathlib.Path(runoff_routing.__file__).resolve()
assert origin.is_relative_to(root), origin
print(f"Source import: {origin}", file=sys.stderr)
runpy.run_path(os.environ["RUNOFF_PROBE"], run_name="__main__")
') > "$VERIFY/source.json"

export RUNOFF_IMPORT_ROOT="$VERIFY/installed"
(cd "$VERIFY" && python3.13 -I -c '
import os, pathlib, runpy, sys
root = pathlib.Path(os.environ["RUNOFF_IMPORT_ROOT"]).resolve()
sys.path.insert(0, str(root))
import runoff_routing
origin = pathlib.Path(runoff_routing.__file__).resolve()
assert origin.is_relative_to(root), origin
print(f"Installed wheel import: {origin}", file=sys.stderr)
runpy.run_path(os.environ["RUNOFF_PROBE"], run_name="__main__")
') > "$VERIFY/wheel.json"

python3.13 -I -c '
import json, pathlib, sys
source, wheel = (json.loads(pathlib.Path(name).read_text(encoding="utf-8")) for name in sys.argv[1:])
assert source == wheel, "Fresh source and installed-wheel per-case/field outcomes differ"
assert source["cases_checked"] == 50
assert len({case["case_id"] for case in source["results"]}) == 50
assert source["retained_36_case_printed_baseline"] == "pass"
assert source["retained_36_case_fresh_scalar_baseline"] == "pass"
assert sum(source["status_counts"].values()) == 50
print("Complete fresh source/installed-wheel 50-case identities and fields agree")
' "$VERIFY/source.json" "$VERIFY/wheel.json"

# Run the existing authenticated full-index check with the installed wheel.
export RUNOFF_REGISTER="$REPO/tests/fixtures/regression-v1/register.json"
(cd "$VERIFY" && python3.13 -I -c '
import os, runpy, sys
sys.path.insert(0, os.environ["RUNOFF_IMPORT_ROOT"])
sys.argv = ["regression_dataset", "preflight", os.environ["RUNOFF_REGISTER"], "--set", "cmd-eligible", "--full-index"]
runpy.run_module("runoff_routing.regression_dataset", run_name="__main__")
')
~~~

Both probe JSON files contain the **actual freshly computed** per-case Q/scalar/source/site/clock statuses. Compare every original required case and failure classification for the selected feature; the retained 36-case gate and a successful installer alone are **not** full CMD acceptance. Expect genuine incomplete scalar outcomes such as the two zero-flow undefined peak times and the H2 stored-time gap until independently resolved; do not silently drop them, shift the original CMD one-based clock, invent a physical HydNNN mapping or convert a printed discharge comparison into a physical-volume conservation pass. Full-index preflight must verify the actual byte-preserved checkout. Keep `--snapshot` as a separate historical replay, never input to this fresh acceptance comparison.

For final evidence, record the source SHA or authenticated archive identity, exact wheel SHA-256, package-code fingerprint, operating system and Python version, imported paths, full-index count, both complete 50-case reports, retained/new admission and per-field failures, and the feature's reference/policy identity. A green reviewed [approved quality workflow](https://github.com/Chain-Frost/python-runoff-routing/blob/main/.github/workflows/quality.yml) with external `--target` import and two identical full reports already supplies equivalent pure-Python software evidence for that exact revision; the verifier must still independently inspect it. This VM method does **not** run Windows-only native RORB and cannot qualify a new native reference without the reviewed evidence.

## Authentication and curation

The [15 November independent closeout](work/2026-11-15-independent-native-closeout.md) adds authenticated
original input/report/source bindings for eight existing gap records and the exact pinned upstream PR16
export. These records remain gaps pending review: **50 CMD-eligible / 21 native gaps / 85 total**.
The current expanded index contains **254 files**. The original 227-file transfer and historical
snapshot retain their original identities; this evidence-only curation does not grant new qualification.

Source: private PR #65 at `78d257745e94cdca74d1fdcdc8a615d472a8bf9c`; original register SHA-256 `a9b74dafe5466491a3ed102a3649df72b992e38c915699934f47096a0228e6f7`. All **1,026** indexed originals authenticated before and after transfer, along with the independent custody receipt and all six supplemental original input/report/typed-event/source bindings. Only model, storm, effective controls, report, typed event and source binding are copied. Unrelated historical manifests/log dumps, empty streams, traces, executables, manuals and research implementations are excluded. Required original capture manifests remain only where they are the authenticated source binding. Historical permission text inside those immutable bindings is superseded prospectively by the 2026-11-15 owner approval.

[provenance.json](../tests/fixtures/regression-v1/native-cmd/provenance.json) records original hash/size/name, published locator/hash/size, evidence class and every transform. Shared objects require identical original SHA-256 and file kind; each case retains explicit references. Different originals yielding the same sanitised payload retain separate original identities.

`basename-pad-path-v1` replaces every drive-qualified path from a drive letter, colon and slash/backslash through end of line with its final basename, right-padded with ASCII spaces to original byte length. This removes machine paths from parameter locators, storm comments and report headers. Line endings, line numbers, character positions, timestamps, scalar selectors, numerical tokens and horizons remain unchanged. These are **derivatives**, never claimed byte-identical originals. Every replacement offset/length/text and original/published hash is retained. Typed events and source bindings retain original bytes. Candidate CSV uses gzip with mtime zero; decompressed hash equals the prior accepted export. Candidate series retain original bytes.

Owner approval on 2026-11-15 is prospective. Historical AUTHORIZATION.json and private originals remain unchanged. Approval excludes unrelated research, executables, manuals and OS traces. No native run, merge, release, new hosted automation or numerical-stage closure is part of this transfer.


### Linux / Python 3.13 cached CMD verification (3.14 also supported)

The native cached regression is **cross-platform** and needs no RORB executable or private custody directory. Under the current development policy, a successful Linux/Python 3.13 or 3.14 pure-Python run is equivalent to Windows for this cached suite; do not require an additional Windows run. This does not certify a fresh numerical engine or native RORB execution. From a clean Linux checkout with the public package installed in a Python 3.13 environment (or substitute Python 3.14):

~~~sh
python3.13 -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index --output /tmp/cmd-preflight.json
python3.13 -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set cmd-eligible --snapshot --output /tmp/cmd-snapshot.json
~~~

Use fresh output names. The snapshot is a retained historical candidate run, not newly computed hydrology. Full-index preflight should pass 50 cases and verify **254** published native files. The cached scalar comparison intentionally exits **1** (48 case passes plus two incomplete zero-flow peak times), while preserving original 19,550 ordinate matches, 50 peak magnitudes and 50 reported inclusive volumes. An unrelated nonzero exit is not acceptable. See [cross-platform index correction](work/2026-11-15-cmd81-native-index-portability.md).
