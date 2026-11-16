# #143 — Windows-native CMD 6.44 acceptance

**Subsequent software integration:** The exact tested canonical-reader
candidate below was later merged through [#142 PR #165](https://github.com/Chain-Frost/python-runoff-routing/pull/165)
into main commit `f74620ec87222c8739c4b8887829f95dd0182898`.
The native execution events, hashes, reader partial statuses and
numerical/physical limitations have not changed. Statements below
about the then-unmerged candidate are historical.

16 November 2026 (Perth). **Bounded native execution/portability: pass (5/5).**
Canonical report reading: demonstrated with retained **partial** statuses.
Numerical equivalence: baseline **incomplete**, edited events **not assessed**.
Issue #143 is not declared fully complete; numerical gate #5 stays open.

## Exact implementation and software evidence

Tested production candidate: **`fe0006687d0a698be9a7cc278170be6dac6a60a2`**,
[#142 PR #165](https://github.com/Chain-Frost/python-runoff-routing/pull/165),
integrating merged #138 (`d33e139`), #139 (`215bcc3`), #140 (`42c7137`)
and #141 (`766b56a`). This is the actual reader implementation branch,
not a test overlay. Neither #172 nor #174 was used. The candidate remains
unmerged; its separate private 420-event reader gate remains open.
[Exact-head review](https://github.com/Chain-Frost/python-runoff-routing/pull/165#issuecomment-6899614021)
completed without major findings.

Installed dependencies, confirmed through distribution provenance:

- PyRomb **0.3.1**, `8653babdb544d400775d754b409c1571e773f7bb`.
- `ryan-rorb-readers` **0.0.0.dev0**, ryan-tools
  `598e5edea093df426cda64c3a528fd1c5784c612`, `packaging/rorb-readers`.

Local Windows 10 build 19045, CPython **3.13.15**. The locally built wheel
SHA-256 is `abc219d909532cc431c10be8d92c6aabe7ddaddaef233d66fce7bebfa3180c06`.
It was installed in a fresh external virtual environment and used with `-I`
from outside the candidate checkout. Runoff and canonical-reader imports resolve
inside that environment. Installed package bytes match both the wheel and
source checkout; the standard implementation identity is
`package-code-v1-sha256:635f5e162440c55befe041851620619ecde1902dc718e150731230c9f32ec86e`.
The complete five effective models also agree between source and installation.
Local installed-wheel exporter/reader tests: **22 passed, zero skips**.
Actual-checkout `preflight --full-index`: **50 verified / 254 files**, exit 0.

Separately audited [successful Windows quality run 43749720170](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43749720170)
tested PR merge `59d44e2cb76fd102c697ef103af4858556469d4c` for this head:
Ruff/strict Pyright passed, **1,215 source tests passed / three skips**,
**177 installed-wheel tests passed**. Its complete 50-case source/wheel
Q/scalar/status/input/site/clock reports agree individually: 50 printed passes,
48 scalar passes and two preserved incompletes. The package-code identity
matches the local candidate and installation. Its wheel hash
`9b6b23492d1090c2db0d6cb2ea3c2f970aa40f4b6b5b7c749cbd7e8ae375ddbb`
is a **different build artifact** from the local wheel. This is audited CI
software evidence, not another personally executed native or 50-case run.

## Original inputs and emitted package

Selected only existing registered **review-design-baseline**, 201 ordinates:

| Original | SHA-256 |
| --- | --- |
| PAR | `239d0d5f1e507552065930601dc2dd76a7b507c6f21aa6e2b6da7fe4e46b9338` |
| CATG | `5ca232d0ac52719458b39582f28b2634012325329345816f3b4daf74140bba07` |
| STM | `4860e1531cd1bcbfb7439d4271436e6c3af40053635a7a4b8753c51cf20a1c33` |

Register hashes/sizes were authenticated before staging and rechecked afterward.
The shared effective-event resolver supplied exactly five events. Baseline:
kc=10, m=0.8, IL=24 mm, CL=5 mm/h. Parameter edits: **kc=11, IL=25 mm**,
otherwise unchanged. Storm edit: **all five depths 95.77 → 105.347 mm**;
original pattern, source order, 0.5 h timestep and 200-increment horizon retained.

The **installed canonical exporter ran once**. Manifest SHA-256:
`b1b0644753c04b500bc48cb18e47f06be6c8bc9f125253f3e5ddce0d67a88d71`.
Every emitted triplet reparsed to its intended model; unchanged CATG and
unchanged STM were byte-exact copies. PyRomb is installed/pinned; these five
events require no changed-CATG writer invocation.

The finished package was moved to a new directory with spaces. The disposable
original-source/project directory was renamed and both old directory paths
were absent throughout execution. The original registered fixtures remain
preserved in the repository; no ACL or repository-wide denial was applied.
All actual PAR dependency tokens are relative `catchment.catg` / `storm.stm`
and resolve inside each relocated event directory, with hashes matching the
manifest. Originals and preserved disposable project/source bytes remain exact.

## Direct native execution and observed outputs

Executable: installed **RORB CMD**, 9,778,880 bytes, SHA-256
`10999ca29f9516c6a7abd26df37cafd433a1cd4ae70d7ac61aa7213845c5ab6f`.
Each fresh report actually states **Program version 6.44 (last updated
12th March 2019)**. The report's `RORBWin Output File` heading does not change
this executable identity. FileVersion/ProductVersion resources are empty.

PowerShell launched the binary directly with sole argument **`model.par`**,
cwd **`<relocated package>/events/001` … `005`** in table order, without Python,
PAR regeneration, settings changes or an engine adapter. Each process had a
**180-second timeout**. All exited **0**, no timeout; observed process times
were 0.033–0.046 s. All 15 input pre/post hashes match. Full absolute cwd,
executable path, argv, timestamps and signed exit values remain in local receipts.

| Event | Verbosity | Native result | Observed output information | Rainfall tables | Q rows |
| --- | --- | --- | --- | --- | --- |
| baseline-v3 | 3 | pass | Flows & all input data | 24 + 24 rows | 201 |
| parameter-v1 | 1 | pass | Flows only | absent | 201 |
| parameter-v2 | 2 | pass | Flows & rainfall only | 24 + 24 rows | 201 |
| parameter-v3 | 3 | pass | Flows & all input data | 24 + 24 rows | 201 |
| storm-depth-v3 | 3 | pass | Flows & all input data | 24 + 24 rows | 201 |

Actual report filename for **each** direct invocation:
**`model.parcatchment_storm.out`**, plus `model.log`; no `batch.out`.
The exporter does not promise this filename; record it as observed behaviour.
All stdout/stderr streams were empty (SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
Every four-byte log hashes to
`92213166b606712b238db29140eaaac87be277b693b020226bd5bc78478838d5`.

| Event | Original output bytes | Output SHA-256 |
| --- | --- | --- |
| baseline-v3 | 12,453 | `8243f6892e7a6656cd1e8fa7215a166864d8dc282c1ea886ff58f731845bc58b` |
| parameter-v1 | 6,462 | `427143d21dc3b2fa1eae00d0cff03fd3bc4159507d45f80489814f5f3f0f6598` |
| parameter-v2 | 8,764 | `28a51b7fa4daadd3aa89aff9ee78be09f2b899171c960a594efc39f38d35ddf3` |
| parameter-v3 | 12,453 | `a5cf04ef5f7bc5b7caa39a05f9f9232e920aba60d6a2d812b6b0e79f69f4a6c7` |
| storm-depth-v3 | 12,453 | `eecdedad2da47ba969f89d7a4d849c050e4a06764af5602a6595829a4b231d7c` |

## Reader and numerical verdicts

**Reader fidelity pass for the characterised fields:** installed canonical
ryan-tools read all five original reports, retaining exact bytes/hash,
numeric/time tokens and Decimal values. Runoff's imported adapter agrees for
all **1,005** ordinates, increments and times. Native echoed kc/m/IL/CL agree
with emitted inputs. Original one-based increments **1…201** and clocks
**0.50…100.50 h** were retained without shifting. Parameter-only verbosity
1/2/3 reports have identical full native Q and clock token sequences.

**Reader completeness incomplete:** all five canonical statuses are `partial`,
with `encoding_fallback` and `uninterpreted_sections` warnings; verbosity 1/2
also retain `completion_unverified`. No error diagnostic or reported error
message row was observed. Process success and full supported tables do not
erase those warnings or establish complete grammar coverage.

**Comparator not_run; numerical equivalence incomplete/not_assessed.** The
registered baseline explicitly retains unverified physical HydNNN identity;
the new report's unnamed calculated hydrograph does not authenticate that
mapping. Therefore no physically bound comparison was made. Edited effective
inputs have no exact original reference. No Python hydrograph, historical
candidate snapshot, new tolerance or second comparator was substituted.
RORBwin batch acceptance, structural CATG edits and broad scientific acceptance
are outside these five events, not inferred passes or native failures.

## Evidence custody and next action

Original emitted inputs, native outputs/logs, stdout/stderr, before/after
inventories, complete per-event invocation receipts, canonical token/Decimal
reports, source/wheel/dependency provenance, CI audit and validation scripts
are retained **locally only** under ignored
`.local/issue143-native-acceptance-20261116/` in the original development checkout.
The **85-file** custody inventory SHA-256 is
`942ef0adcd2bce2eb8e6eaf8f3ef549433b6500417eaa2521c7cbc0d3bbb07fd`.
The verified 401,353-byte archive `issue143-native-evidence.zip` hashes to
`25b621b7d5949b0189e7fa0e0bd6a528b8d3498be5226ced5e0e3b8de442025e`.
Archived file bytes were individually rehashed. No executable or unreviewed
native report was added to public Git. No merge, release or gate closure occurred.

**Next action:** review this bounded receipt; retain #142's distinct private
population gate, resolve native physical-site binding before numerical
acceptance, and reconcile final merged source/wheel identity when #142 lands.
No further native campaign is implied. This supersedes the earlier local
preflight's `not_run` status only for the five events and exact revision above.
