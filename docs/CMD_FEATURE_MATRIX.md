# CMD 6.44 capability and acceptance matrix — single maintained inventory

**Status, 15 November 2026:** Phase-A feature inventory for [CMD gate #5](https://github.com/Chain-Frost/python-runoff-routing/issues/5), [roadmap #1](https://github.com/Chain-Frost/python-runoff-routing/issues/1), [draft PR #84](https://github.com/Chain-Frost/python-runoff-routing/pull/84). It is **not** CMD full replacement or engineering accuracy acceptance. The [public regression-v1 register](../tests/fixtures/regression-v1/register.json) is the **only** case register; there is no second runner, population, or set of goldens.

## Reference, evidence and denominators

The pinned original reference is RORB_CMD **6.44**, executable SHA-256 **10999ca29f9516c6a7abd26df37cafd433a1cd4ae70d7ac61aa7213845c5ab6f** (identity only; binary not distributed). RORBwin 6.52 is a different deferred profile. Do not assume a feature exists in CMD merely because it is described for RORBwin.

| Evidence | Population | Status and limits |
| --- | --- | --- |
| Original authenticated native CMD 6.44 source/report population | **50 cases / 19,550 original full-horizon printed Q rows**, 44 archive plus six supplemental | Original independent native printed records. All 50 retain case IDs, source provenance, original native clock and one terminal physical Hyd001 map; this is not 50 computed current Python outputs |
| **Fresh installed public python-cmd computation** | **36 admitted and printed-pass / 16,836 complete original rows**; **14 source_unsupported**; all 50 visited | [Exact previous source receipt](https://github.com/Chain-Frost/python-runoff-routing/blob/373ed8d70715b284cc6cf7c36cef377f841f9a1f/docs/work/evidence/issue75/public_cmd_fresh_50_replay_20261115.json), [Windows run 43637009435](https://github.com/Chain-Frost/python-runoff-routing/actions/runs/43637009435), integration implementation **e7b4978fe81d94ca9cb646b07d9d0579f32a2942**. Original S1 sources → typed project → actual isolated installed-wheel python-cmd → original native printed comparison. Zero printed failures among 36 admitted. **Bounded printed-token/software regression only**; newer #79 head is not requalified by this run |
| Historical separately reviewed private v6 candidate | **50 / 19,550** printed pass; peak 50; time 48 and two zero-flow incompletes; inclusive reported volume 50 | Candidate source **fea9c80c521127325b779ea0ea87ddf77795b290**; public bundled snapshot is historical execution, not a fresh public engine or wheel. Overlapping private replay/scalar cohorts cannot be counted as independent native populations |
| Native archive gaps | **21 = 11 CMD + 10 RORBwin** | Eleven CMD: three expected negative, one incomplete raw output, seven captured/unreviewed. GUI ten deferred, not silently removed from all-case inventory |
| Authored independent mathematical controls | **10** | Non-native oracles, not extra CMD cases; named below |
| Authored analytical gaps | **4** | Unresolved negative/refinement/isolation cases; named below |
| **All public records** | **85 = 50 + 21 + 10 + 4** | Denominator persists and all-selection remains non-success until gaps are resolved |

**Evidence grades:** D = directly authenticated original CMD input/report; P = fresh public installed-wheel comparison to D; H = historical candidate or overlapping private observation; A = independently authored analytical oracle; G = incomplete/unreviewed reference, unsupported source or missing acceptance; ? = applicability not established in pinned CMD. A native original printed reference is evidence of what CMD did, **not** proof that the selected public native adapter handles the same source.

**Four phases per engine** use **R / X / O / Q**: R = recognised and representable through the maintained source/typed path; X = executed by the selected engine; O = required output supported; Q = numerically qualified under its engine-specific acceptance policy. **Y** means implemented/observed in a bounded path, **N** explicitly rejected/unimplemented, **?** not established, **U** qualification outstanding, **P36** *only* the fresh 36-case original printed-precision comparison. These are not four interchangeable statuses. For example Y/Y/Y/U means the feature executes but scientific acceptance is still open.

The selected engines are default **python** (independent improved engineering and batch method, #6), explicit **python-cmd** (pinned CMD-compatible backend, draft [#79](https://github.com/Chain-Frost/python-runoff-routing/pull/79), not merged into main) and explicit user-configured **rorb-cmd** (native adapter merged #77). No private runtime dependencies, fourth research backend, fallback, or default change. The native adapter has its own narrower conditional local 2 × 201-row receipt; original 50 native CMD runs cannot substitute for that adapter qualification.

## Exact 14 source_unsupported cases from fresh installed-wheel run

These failures occur **before calculation**; they are not 14 numerical mismatches. Original source bytes, semantic ordering and full native reports stay immutable.

| Cause | Exact retained IDs | Work item |
| --- | --- | --- |
| Eight original DESIGN storms have **102.10%** percentage totals, rejected by S1 strict 100% source validator | failure-baseline-before; failure-baseline-after; fig67-ilcl-confirmed; fig67-ilcl-low; fig67-ilcl-probe; fig67-zero; wheel-ilcl-confirmed; wheel-zero | [#93](https://github.com/Chain-Frost/python-runoff-routing/issues/93): independently establish native *effective* percentage interpretation; preserve original lexemes; **never silently normalise** |
| Three supplementary DESIGN storm **pattern-marker dialects** | H1-three-source-asymmetric; H2-four-source-nested-odd-rain; H3-single-source-equality-chain | [#94](https://github.com/Chain-Frost/python-runoff-routing/issues/94): characterise source syntax, not fabricate markers |
| One N4 **unstored running-hydrograph/source-control** stack restriction | N4-six-source-serial-nested | [#95](https://github.com/Chain-Frost/python-runoff-routing/issues/95): verify preserved source/control order, not invent reordering |
| Two **PyRomb graphical-header** variants outside characterised RORB_GE 002 parser | pyromb-pr2-full; pyromb-novel-storm | [#96](https://github.com/Chain-Frost/python-runoff-routing/issues/96): qualify source version/header/control vector, not strip by heuristic |
| **Total** | **8 + 3 + 1 + 2 = 14** | Keep 36 current computed matches and all 14 exclusions as distinct case states; only fresh source/wheel computation may promote them |

## One matrix: required/observed CMD capabilities

**Alias C36** = the 36 case IDs tagged cmd-reviewed or timestep in the public register, 16,836 complete ordinates; **F8** = the eight listed above; **H3** = H1/H2/H3 listed above; **P2** = the two PyRomb cases. **A10** = the ten independent authored controls listed in the gap ledger below. Aliases are pointers to the single case register, **not** additional cases. "Confirmed" means an actual pinned CMD native record supports that bounded source/operation, not every possible parameterisation.

**Single accountable owner per row:** **C** S1 parser/domain #3, **A** CMD-compatible numerical source #75, **B** regression comparator/physical mapping #58, **D** default improved engineering #6, **E** pinned native evidence #2. Dependencies may name another workstream without giving it duplicate implementation ownership. CMD policy = original full-horizon printed intervals and distinct frozen CMD reporting-scalar conventions; SRC = source/dialect semantic identity; OUT = clock/site/printed reporting; ERR = negative/classified errors; ENG = independently justified physical, accuracy, stability and batch policy for default python.

| ID / actual pinned CMD requirement and semantics | Observations, cases and grade | python-cmd R/X/O/Q | python R/X/O/Q | rorb-cmd R/X/O/Q | **One owner**; dependencies and verification |
| --- | --- | --- | --- | --- | --- |
| 01 Confirmed original .par, RORB_GE 002 .catg, DESIGN .stm supplied-source parsing, stable control order | C36 D/P | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **C** #3, A #75 and B #58; SRC + original CMD |
| 02 Original 102.10%-total DESIGN patterns; native effective forcing must be established | F8 D, admission G | N/N/N/U | N/N/N/U | ?/?/?/U | **C** #93, E #2 then A #75; SRC, CMD and ENG |
| 03 Supplementary temporal marker dialects | H3 D, admission G | N/N/N/U | N/N/N/U | ?/?/?/U | **C** #94, A #75; SRC, CMD and ENG |
| 04 PyRomb graphical source/header dialect | P2 D, admission G | N/N/N/U | N/N/N/U | ?/?/?/U | **C** #96, A #75; SRC then CMD |
| 05 N4 nested source re-addition / running control-stack semantics | N4 D, admission G | N/N/N/U | N/N/N/U | ?/?/?/U | **C** #95, E #2, A #75; SRC, control order, CMD |
| 06 Bounded one supplied DESIGN event, one ISA/pluviograph/burst and lumped kc | C36 D/P; H3 D | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **A** #75; C #3, D #6; CMD vs independent ENG |
| 07 IL/CL initial loss crossing/equality, continuing loss and dry/zero-loss | C36 D/P; F8 and H3 D; pub-loss-equality and pub-loss-crossing A | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **A** #75, #93/#94, D #6; CMD plus ENG |
| 08 **IL/runoff-coefficient flag 2:** S1 ParameterSet and .par codec already recognise/round-trip, bounded numerical adapter rejects | fig67-ilroc G; earlier supplemental evidence H | Y/N/N/U | Y/?/?/U | Y/N/N/U | **A** [#90](https://github.com/Chain-Frost/python-runoff-routing/issues/90), E #2, B #58; CMD, not a parser defect |
| 09 Original rainfall/loss → source conversion, source distance/coefficients and original source membership/order | C36 D/P; H1/H2/H3/N4 D; historical separate native operands H | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **A** #75, #94/#95; CMD original order |
| 10 Natural nonlinear m>0 reach routing/translation, control codes 1/3/4/5/7, confluences | C36 D/P; H1/H2/H3/N4 D | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **A** #75, #95/#92 and D #6; CMD and ENG separately |
| 11 Linear m=1, m=0 legacy constant-storage distinction, extreme exponent/rounding | fig67-kc5-m1, failure-m-above-one, failure-m-below-one G; pub-linear-pulse and pub-linear-recession A | Y/?/?/U (typed m=0 N) | Y/?/?/U | ?/?/?/U | **A** [#92](https://github.com/Chain-Frost/python-runoff-routing/issues/92), E #2, D #6; CMD + independent ENG |
| 12 Zero/negative/omitted reaches, invalid control, nonconvergence and fallback vs rejected source | failure-zero-reach, failure-negative-reach, failure-negative-reach-repeat, failure-invalid-code G | ?/N/N/U | ?/?/?/U | ?/?/?/U | **A** #92; C #3 and E #2; ERR, valid CMD only if observed |
| 13 One terminal code-7 original physical print and source-to-Hyd001 mapping | 50 original D, C36 P | Y/Y/Y/P36 | Y/Y/Y/U | Y/Y/Y/U | **B** #58; A #75 and E #2; OUT, no label-only claim |
| 14 Multiple physical output sites / code-11 rainfall-excess print | fig67-code11 raw native output G; no other qualified multi-site cohort | ?/N/N/U | ?/?/?/U | ?/?/?/U | **A** [#91](https://github.com/Chain-Frost/python-runoff-routing/issues/91), E #2, C #3, B #58; OUT then CMD |
| 15 Original one-based increment/time tokens vs separately derived Python elapsed hours, all full original rows | 50 D / 19,550 original rows, C36 P | Y/Y/Y/P36 (elapsed, not original raw tokens) | Y/Y/Y/U (elapsed) | Y/Y/Y/U (native raw tokens when present) | **B** #58; A #75 and E #2; OUT and preserved clock |
| 16 Peak magnitude, peak time/zero-flow undefined, exact stored-Q ties, sub-print time | 50 D/H peaks, 48 nonzero times H, fig67-zero/wheel-zero G, one linear plateau A, one N4 sub-print operand H | Y/Y/Y/U | Y/Y/Y/U | Y/Y/Y/U | **B** #58, E #2, D #6; CMD scalar policy, ENG separately |
| 17 Native **inclusive-sample** reported volume and independent physical-horizon statistic | 50 D/H inclusive volumes; 48 historical endpoint differences H | Y/Y/Y/U | Y/Y/Y/U | Y/Y/Y/U | **B** #58, D #6; OUT, never equate native volume with mass balance |
| 18 Source pre-addition and nonzero initial-state/storage observations | H3 missing S[1], six private Q/S suffixes/38 reaches/1,951 intervals H, pub-initial-state A | ?/?/?/U | ?/?/?/U | ?/?/?/U | **E** #2, A #75 and D #6; no fabricated observed storage |
| 19 Physical full-horizon flux/conservation, full recession, stability and timestep refinement | A10; pub-nonlinear-refinement gap; private diagnostics H | Y/Y/Y/U | Y/Y/Y/U | ?/?/?/U | **D** #6; B #58; independent ENG, not CMD reported volume |
| 20 Exact selected API/CLI/JSON project engine, no implicit fallback, persisted source/profile/result/error provenance | merged #74/#77; draft #79; synthetic controls | Y/Y/Y/U (draft) | Y/Y/Y/U (main) | Y/Y/Y/U (configured native) | **A** #75; #7, B #58; source + wheel, ERR |
| 21 Isolated installed public wheel/source identity, original reference comparator and fail-closed probe | C36 printed pass P; #79 PowerShell failure-masking review open | Y/Y/Y/P36 (earlier exact source) | Y/Y/Y/U | Y/Y/Y/U (adapter scope) | **B** #58; A #75 must repair workflow; source/wheel and deliberately failing baseline |
| 22 Invalid catchment/truncated storm/invalid code and accurate non-success classifications | failure-truncated-storm, invalid-catchment, failure-invalid-code G; pub-invalid-negative-k and pub-unsupported-code authored gaps | ?/?/?/U | ?/?/?/U | ?/?/?/U | **B** #58, E #2, C #3 and A #75; ERR is not numeric pass |
| 23 Repeated events, carry/reset, deterministic in-memory batch isolation | pub-event-isolation gap; A10; no independent native batch cohort | ?/?/?/U | ?/?/?/U | ?/?/?/U | **D** #6; B #58; ENG, batch per-event accounting |

**Reporting qualifications:** All 48 nonzero historical candidate series have unique exact stored maxima, while fig67-zero and wheel-zero have 301 zero samples and undefined native peak-time acceptance. A single reviewed manufactured linear nonzero plateau selected the earliest native exact peak, **not** a universal tie policy. One N4 raw formatter operand distinguishes sub-print timing in that case, not all event formats. A nonzero inclusive-minus-trapezoid endpoint term in 48 old candidate outputs is a mathematical identity, **not** a conservation defect. The conditional 2^-12 m³ budget was only approved for one separate manufactured linear control, not nonlinear network conservation. Missing original S[1]/source prefixes and physical budgets remain open.

## CMD applicability still unresolved — no silent exclusions or RORBwin-derived features

Rows here are **conditional** pending a finite E/#2 assessment of the actual CMD **6.44** build/source contract. If an item is confirmed CMD-supported, it becomes a required CMD row with a small scoped child implementation issue, an original qualified reference, parser/output requirements, source/wheel checks and a single owner. If it is proved GUI-only or not present in CMD, document that evidence. If unresolved, **leave it visible** and do not narrow full-replacement claims. Do not start an undirected native campaign.

| ID / suspected CMD function and semantics | Pinned CMD evidence and cases | python-cmd R/X/O/Q | python R/X/O/Q | rorb-cmd R/X/O/Q | One owner; dependencies; exit policy |
| --- | --- | --- | --- | --- | --- |
| 24 Plain .cat and combined .dat source dialect/round trip | no selected eligible CMD 6.44 case; ? | ?/N/N/U | ?/?/?/U | ?/?/?/U | **C** #3 with E #2; SRC; CMD only if confirmed |
| 25 Multiple ISA/pluviographs/bursts, spatial rainfall, distributed kc, carry/reset | no qualified original multi-source-dialect cohort; ? | ?/N/N/U | ?/?/?/U | ?/N/N/U | **E** #2 with A #75/C #3/D #6; profile evidence then CMD/ENG |
| 26 Generated rainfall/ARR/preburst and external input assets | upstream #8 vs actual CMD program input boundary unresolved | ?/N/N/U | ?/N/N/U | ?/N/N/U | **E** #2 with #8; no inferred CMD generator |
| 27 DCIA/ICIA/nonzero impervious and other GUI-only impervious choices | no CMD direct qualification; flag-2 is a separate observed source gap | ?/N/N/U | ?/?/?/U | ?/N/N/U | **E** #2 with A #75/C #3; explicit mode decision |
| 28 Special/table/reservoir/basin storages, nonzero initial storage, subdivisions | pub-initial-state A only; CMD applicability ? | ?/N/N/U | ?/?/?/U | ?/N/N/U | **E** #2 with A #75/D #6; real source + state controls |
| 29 Diversion/split/rejoin, external inflows/outflows, nonlocal translations | C36 natural confluence does **not** prove generic diversion; ? | ?/N/N/U | ?/?/?/U | ?/?/?/U | **E** #2 with A #75/C #3; original controls/flows |
| 30 Baseflow, transmission losses, limiting flow and other control variants | no characterised selected CMD source/output; ? | ?/N/N/U | ?/?/?/U | ?/?/?/U | **E** #2 with A #75; confirm build and ERR |
| 31 FIT/calibration and non-DESIGN operational modes | all 50 are DESIGN; GUI FIT record is RORBwin, not CMD | ?/N/N/U | ?/?/?/U | ?/?/?/U | **E** #2 with C #3/A #75; version-specific decision |
| 32 RORBwin 6.52-only archive requests | ten deferred GUI records; **not** CMD evidence | —/—/—/— | —/—/—/— | —/—/—/— | **E** #2; deferred outside CMD gate; do not expand RORBwin |

## All 21 native archive gaps and 14 authored items

**Eleven CMD gaps:** 3 expected negative: failure-invalid-code, failure-truncated-storm, invalid-catchment; 1 incomplete raw report: fig67-code11; 7 captured/unreviewed: failure-m-above-one, failure-m-below-one, failure-negative-reach-repeat, failure-negative-reach, failure-zero-reach, fig67-ilroc, fig67-kc5-m1. An input file is not a qualified native golden, and expected rejection is not a computed hydrograph.

**Ten GUI-deferred:** gui652-ilcl-baseline; gui652-werribee-fit-kc018-m1; mr-design-areal-reopened; mr-ensemble-24h-5pct; mr-ensemble-three-durations-two-aeps; policy-after-cancel; policy-constant; policy-fresh-constant; policy-vary-first; policy-vary-reload.

**Ten independent authored oracles:** pub-zero-runoff, pub-equilibrium, pub-linear-recession, pub-linear-pulse, pub-junction, pub-loss-equality, pub-loss-crossing, pub-initial-state, pub-branch-order, pub-full-recession. **Four authored analytic gaps:** pub-invalid-negative-k, pub-unsupported-code, pub-nonlinear-refinement, pub-event-isolation. Neither authored group is native CMD acceptance.

## Ordered dependency and exact CMD gate

1. **C/parser:** #3 plus [#93](https://github.com/Chain-Frost/python-runoff-routing/issues/93), [#94](https://github.com/Chain-Frost/python-runoff-routing/issues/94), [#95](https://github.com/Chain-Frost/python-runoff-routing/issues/95), [#96](https://github.com/Chain-Frost/python-runoff-routing/issues/96) qualify all 14 exact original source dialects and guard against inventing corrections.
2. **A/compatible computation:** #75, [#90](https://github.com/Chain-Frost/python-runoff-routing/issues/90), [#92](https://github.com/Chain-Frost/python-runoff-routing/issues/92), [#91](https://github.com/Chain-Frost/python-runoff-routing/issues/91). Retain native-effective preparation/routing/output, classify missing CMD modes, repair #79's masked-failing CMD probe and demonstrate a deliberately failing baseline actually fails CI.
3. **B/regression:** #58 and completed #81. Preserve all 85 cases with one register, exact original reference/source hashes, sites, clocks, scalar budget, per-engine status, actual new source and isolated wheel execution. No snapshot relabelling or native process in cached suites.
4. **D/default:** #6. Independently validate improved python under ENG, physical full-horizon balance, timestep refinement, deterministic batches and deliberate departures from CMD. No comparison-only engineering acceptance.
5. **E/pinned native evidence:** #2. Finite qualification of 11 CMD gaps and conditional rows 24–31. No RORBwin expansion and no speculative experimental sweep.
6. **Owner/final #5:** independent exact-revision review of the one matrix and per-feature evidence. Each confirmed CMD requirement must pass R, X, O and **its own Q** for **both Python engines**, plus an explicit functioning rorb-cmd adapter, unless the owner **explicitly** accepts a documented per-engine narrower claim. All 50 + 11 CMD + 10 GUI-deferred + 10 analytic + 4 analytic gaps must be accounted for without pretending every category is a computed pass. The parent **remains open**.

[Phase-A delivery, source/evidence identity and issue ownership record](work/2026-11-15-cmd-phase-a-completion.md). The earlier PR #84 independent code-2 recognition P2 was corrected at 4de97a4 and follow-up review found no major issue **at that earlier head**. This extension requires a new independent review; it is not automatically reviewed by the older receipt.
