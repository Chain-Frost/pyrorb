# Issue #143 — Windows-local RORB CMD 6.44 acceptance handoff

**Purpose:** qualify the *actual exported, relocated* RORB CMD inputs, separately
from source parsing, Python/wheel checks and numerical parity. This is a
bounded local execution task under [#143](https://github.com/Chain-Frost/python-runoff-routing/issues/143),
not a new implementation, feature matrix, benchmark, executable redistribution
or GUI research task.

**Preconditions:** a trusted locally installed RORB CMD **6.44** executable on
Windows, the original approved project source triplets, and an export package
produced by a reviewed **integrated** #138–#142 revision. GitHub-hosted
Windows quality CI and the closed synthetic integration PR #172 **do not**
establish the native results described here. No executable or private data
should be committed to the public product repository.

## Ready-to-paste prompt for the Windows-local agent

> Complete the outstanding **native executable acceptance only** for
> Chain-Frost/python-runoff-routing issue #143, under workflow parent #7 and
> numerical gate #5. First read current main AGENTS.md, docs/DEVELOPMENT.md,
> docs/COMPATIBILITY.md, this handoff, the current #143 acceptance receipt,
> NATIVE_CMD_EXPORT.md from the actual #141 integration revision and the
> existing regression/evidence policies. Refresh all relevant source heads.
>
> **Do not use the old test-only PR #172 as product code.** Use the approved
> final #138–#142 integrated source or an explicitly identified reviewed
> integration commit. If the real exporter/reader is not integrated or a
> suitable CMD executable is not installed, mark the affected checks
> **not_run**; do not silently substitute python-cmd, a stub, RORBwin,
> capture_run, a re-rendered PAR or an arbitrary executable.
>
> **Bounded native cases:** using the single existing public CMD register,
> begin with the authenticated review-design-baseline PAR/CATG/STM triplet,
> 201 printed ordinates. Prepare a package containing no more than five
> independent events: original/equivalent settings at requested verbosity 3;
> a representable parameter-only kc/IL edit at verbosity 1, 2 and 3;
> and a representable edited DESIGN storm-depth event at verbosity 3.
> Use the shared effective event resolver and canonical native exporter.
> Original source files must remain unchanged and hash-pinned. Inspect
> effective settings, requested print sites, storm horizon and generated
> package manifest. A sixth optional parameter-only original
> pyromb-pr2-full modern graphical CATG/code-2/FI case is permissible if
> that preserved original is supported and independently source-verified.
> Do not create more cases or launch a broad campaign.
>
> Export **once per selected package**, reparse the *emitted* PAR/CATG/STM
> with the actual integrated source and record full source/emitted hashes.
> Move the finished package to a fresh directory, ideally another volume.
> During native execution make the original project/source directory
> inaccessible (for example use a separate clean Windows machine or
> temporarily rename only an authorised disposable copy, restoring it
> afterwards). Demonstrate that every declared CATG/STM dependency resolves
> **inside** the moved event folder; reject absolute/original paths.
>
> Execute the relocated event's **exact** model.par, from its event directory,
> using the reviewed locally installed RORB CMD 6.44 executable with that
> PAR as the *literal* argument. The native step must not require Python.
> Do not call S0 capture_cmd, NativeCmdRunSpec, the Python engine or a helper
> that regenerates or overwrites the PAR, settings, paths or verbosity.
> Before and after each native invocation hash the actual relocated PAR,
> CATG and STM; require equality. Record the executable's original SHA-256,
> observed native banner/version, actual absolute executable path (keep
> private), complete argv, working directory, exit code (including signed
> nonzero codes), stdout/stderr, event ID, requested settings and actual
> produced files and hashes. Check native output-report availability for
> each requested verbosity **without assuming an output filename exists**.
> Report a genuine batch.out only if that specific executable actually
> creates one. The retained RORBwin 6.52 80-row/eight-reference batch is a
> **separate reader test**, not proof CMD produced batch.out.
>
> After native execution, inspect original output reports through the
> **installed** canonical ryan-tools reader and retain source tokens, clock,
> increments, physical print-site mapping/uncertainty, report diagnostics and
> completion status. For cases with a matched registered original reference
> and authenticated physical site, invoke **only the existing comparator**
> for full Q series, peak magnitude/time, native clock, volume and
> pass/incomplete/unsupported status, with its frozen precision policy.
> Edited events with no exact native matched reference are
> numerical_equivalence=not_assessed; report actual native execution and
> parsing separately. Never generate a Python hydrograph as a new native
> oracle.
>
> **Handoff evidence:** provide the exact tested Git commit, selected
> project/case/event IDs, wheel SHA-256 and optional dependency revisions;
> original PAR/CATG/STM hashes; exported package manifest SHA-256 and
> each actual relocated file hash; native executable SHA-256 and observed
> version; per-event exact cwd/argv/exit/stderr/stdout, requested vs observed
> verbosity/output flags and output inventory; pre/post unchanged-file hashes,
> reader diagnostics, and comparator verdicts where justified. Distinguish
> **pass, fail, unsupported, incomplete and not_run** per contract.
> Preserve native report bytes and logs in approved restricted evidence
> storage (or send a clearly identified archive to the owner); never
> commit the executable, locally identifying paths, unreviewed reports or
> private data to public main. Publish a concise sanitised #143 acceptance
> receipt linking evidence and an exact reviewed source/CI revision.
> Keep #5 scientific gates open.
>
> **Stop immediately** if the selected executable is not independently
> authenticated as the intended CMD 6.44, the written PAR/CATG/STM no
> longer match their manifest hashes, package paths leave the relocated
> folder, preflight rejects the effective model, or a helper would need
> to rewrite inputs for the native executable. Record the blocker; do
> not modify original inputs or weaken acceptance thresholds.

## Example no-Python PowerShell native execution check

The package must be created beforehand by the reviewed #141 exporter. The
following is an illustrative **local operator procedure, not an executed
receipt**. Replace both paths with real local paths. It runs **one already
emitted** event PAR without rewriting or reconstructing it.

~~~powershell
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$exe   = 'C:\path\to\reviewed\RORB_CMD.exe'
$event = 'D:\s5-native-relocated\events\001'
$log   = 'D:\s5-native-receipts\event-001'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Missing native CMD executable' }
if (-not (Test-Path -LiteralPath $event -PathType Container)) { throw 'Missing emitted event' }
if (Test-Path -LiteralPath $log) { throw 'Choose a new no-overwrite receipt directory' }
New-Item -ItemType Directory -Path $log | Out-Null

$exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
$par = Join-Path $event 'model.par'
$before = (Get-FileHash -LiteralPath $par -Algorithm SHA256).Hash.ToLowerInvariant()
$filesBefore = Get-ChildItem -LiteralPath $event -File |
  Select-Object Name,Length,@{Name='sha256';Expression={
    (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  }}
$filesBefore | ConvertTo-Json -Depth 5 |
  Set-Content -LiteralPath (Join-Path $log 'files-before.json') -Encoding utf8

Push-Location -LiteralPath $event
try {
  & $exe 'model.par' 1> (Join-Path $log 'native-stdout.txt') 2> (Join-Path $log 'native-stderr.txt')
  $exitCode = $LASTEXITCODE
} finally {
  Pop-Location
}

$after = (Get-FileHash -LiteralPath $par -Algorithm SHA256).Hash.ToLowerInvariant()
$filesAfter = Get-ChildItem -LiteralPath $event -File |
  Select-Object Name,Length,@{Name='sha256';Expression={
    (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  }}
$filesAfter | ConvertTo-Json -Depth 5 |
  Set-Content -LiteralPath (Join-Path $log 'files-after.json') -Encoding utf8
[pscustomobject]@{
  executed_at_utc = [DateTime]::UtcNow.ToString('o')
  executable_sha256 = $exeHash
  cwd = $event
  argv = @($exe, 'model.par')
  native_exit_code = $exitCode
  par_before_sha256 = $before
  par_after_sha256 = $after
  par_unchanged = ($before -eq $after)
  native_version_claim = 'unverified_until_output_banner_inspection'
  numerical_equivalence = 'not_assessed'
} | ConvertTo-Json -Depth 6 |
  Set-Content -LiteralPath (Join-Path $log 'execution-receipt.json') -Encoding utf8
if ($before -ne $after) { throw 'STOP: emitted PAR changed during native execution' }
if ($exitCode -ne 0) { throw "Native CMD returned nonzero status: $exitCode" }
~~~

Before running, independently match all three emitted input files against
their package manifest's recorded SHA-256, and verify that event folders
contain no pre-existing output reports that might be mistaken for new results.
The code records the PAR and file inventory; compare the event CATG/STM
before/after hashes explicitly as well. A zero native exit only establishes
process completion, **not** a correct native report or numerical equivalence.

## Disposition

- The #140 branch [PR #159](https://github.com/Chain-Frost/python-runoff-routing/pull/159)
  at source head 089baec88de8867ede2506ef43b7ebae5ef2dcd1
  implements a fail-closed native guard for unrepresented edited storm or
  catchment inputs, with both negative tests and successful Windows source/wheel
  [quality #43733144711](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43733144711).
  **This guard is not yet in main** while #159 remains unmerged.
- Local direct native execution remains **not_run** in this assistant/GitHub
  environment. When supplied, add *actual* evidence to
  [the #143 acceptance receipt](2026-11-15-issue143-s5-acceptance.md),
  distinguish the resulting native-acceptance verdict from CMD numerical #5,
  and perform post-merge source/wheel qualification separately.
