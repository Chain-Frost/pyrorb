# Uniform direct-depth DESIGN STM (#250)

## Contract and source basis

Base `ef5c985a607545aee9f58d2a0f4f5712c410e46d`; companion [ryan-tools #118](https://github.com/Chain-Frost/ryan-tools/pull/118) at `ebc227839cde8b7cb6f0dabfca8882f17ca9cc5b`. Its `build_stm` uses one burst, one pluviograph, areally uniform flag 0 and a terminating -99. This differs from PyRORB's existing flag-1 pattern + ordered subarea depths.

RORB Version 6 User Manual (January 2010), §3.2 p.28 and Table 5-2 pp.56–58, items 7.1–8.6 and 9.1 (R1 in [SOURCES](../SOURCES.md)), establish that flag 0 applies the same rainfall depth and temporal distribution throughout the catchment. Pluviograph ordinates are depths in millimetres within intervals after the declared burst start. The direct case skips the subarea-depth/association records; the file can finish when no hydrograph inputs are required. The two timing integers are burst start and finish measured in increments, not time-zero samples. The first #118 depth covers (0, dt], the last covers ((n-1)dt, n dt]. RORBwin 6.52 release notes §1.8 (R3) document a 2,000-increment limit and default 200. These are documentation findings, not executable acceptance. The original manuals are not redistributed.

## API and boundaries

```python
from decimal import Decimal

from runoff_routing.rorb_codec import (
    original_bytes,
    parse_direct_design_stm,
    serialize_direct_design_stm,
)
from runoff_routing.rorb_model import DirectDepthStorm

storm = DirectDepthStorm(
    "SYNTHETIC DIRECT",
    Decimal("0.5"),
    200,
    (Decimal("5.25"), Decimal(0), Decimal("2.5"), Decimal(0)),
)
payload = serialize_direct_design_stm(storm)
parsed = parse_direct_design_stm(payload)
assert parsed.model == storm
assert original_bytes(parsed) == payload
```

The example has four half-hour bins (including two dry bins), 7.75 mm at every point, rainfall ends at hour 2, calculation horizon 100 hours. No zero insertion, trimming, normalisation, subarea mapping, float conversion, or loss transformation occurs in this codec. The title is a single nonempty line of up to 68 characters; one literal `Pluviograph 1` label, start 0, one burst, one gauge, flag 0 and 1–2,000 calculation increments are deliberately bounded to #118. Uncharacterised layouts, extra records and bad counts are rejected. Original bytes and source-token spans retain the input representation; canonical UTF-8 LF output has one depth per line. `write_new` can be used for explicit exclusive-create output.

The existing `StormModel`, weighted `parse_design_stm`, `serialize_design_stm`, generic `parse_bytes/read_file`, ordinary CLI/MCP inspection and project import/routing contracts remain unchanged. The direct type is intentionally **not** a RunModel or JSON-interchange storm. The explicit bytes API is the supported entry point; ordinary CLI inspection and run paths still reject flag 0. Do not pass a direct hyetograph through relative weights, a percent model, or an invented subarea depth. No new MCP tool or CLI workflow is necessary for this downstream library writer.

## Verification and remaining gates

The independently authored literal fixture and controls live in [test_rorb_direct_stm.py](../../tests/test_rorb_direct_stm.py). An extracted Linux Python 3.13.5 harness using the candidate model and codec functions and transcribed existing source helpers passed 24 focused cases; this is not execution from a complete checkout or an installed wheel. Full authenticated checkout was unavailable (GitHub DNS failed), and Ruff/Pyright were unavailable in the local environment. Existing hosted quality, exact-head review, full source regressions and installed-wheel checks remain required. In the local installed-wheel environment run the new focused tests from outside checkout and prove the import is from the exact wheel; do not alter quality workflow or tolerance policies.

The downstream writer switch must wait for a released PyRORB wheel containing this API. Keep the existing #118 branch and all CSV STEPPED interpretation, zero-time/terminal-zero decisions, naming, output root checks, preflight and no-overwrite policy in ryan-tools. Preserve the prior contributor history. When consuming the release, convert the existing validated numeric series to Decimal using its existing emitted decimal tokens (compare exact depths, timestep, timing and horizon before/after); keep the downstream text/error/output contract. Test single-file and batch workflows with synthetic and an approved actual TUFLOW export. Native RORBwin 6.52 acceptance needs a representative installed-model run, exact version, rainfall interval timing, depths, totals and hydrograph peak/time/recession comparison. It has not been run here. No merge, publication, original project files or native execution in this increment. #249 is independent; #242's weighted/combined storm contract is untouched.
