# Issue #190: independent ARR total-probability reference

**24 November 2026 — research/verification only.** This reference supports the bounded software scope of
[#190](https://github.com/Chain-Frost/pyrorb/issues/190) and parent
[#9](https://github.com/Chain-Frost/pyrorb/issues/9). It does not change the
provisionally delivered `monte-carlo-statistics/1` policy, expand sampled AEP support,
admit native RORBwin 6.52 frequency algorithms or establish flood engineering acceptance.

## Source and calculation contract

- Nathan, R. and Weinmann, E. (2013), *Australian Rainfall and Runoff Discussion Paper:
  Monte Carlo Simulation Techniques*, report D2, §§4.3, 7.4, pp. 21–22 and 37–38.
  [Published PDF](https://www.arr-software.org/pdfs/ARR_DiscussionPaper_MonteCarlo.pdf).
  © Commonwealth of Australia (Geoscience Australia), CC BY 4.0.
- *Australian Rainfall and Runoff*, Book 4, version 4.2, §4.4, Table 4.4.3, p. 69.
  [Published PDF](https://www.arr-software.org/pdfs/ARR_190514_Book4_V4.2.pdf).
  © Commonwealth of Australia (Geoscience Australia), CC BY 4.0.

The standalone [reference module](../../repo-scripts/arr_tpt_reference.py) computes
the strict flood-threshold exceedance probability from explicit rainfall interval
masses `w_i`, simulated counts `N_i` and counts `n_i` with peak **strictly greater**
than the threshold: `P(Q>q; modelled) = sum_i w_i * n_i / N_i`.

The reference does not read native reports, infer interval weights, draw random events,
run routing, interpolate flood quantiles or import the product frequency estimator.
It returns the original per-interval contributions, modelled rainfall mass,
remaining unmodelled mass and conservative `[known, known + unmodelled]` bounds.
Bounds omit sampling uncertainty, law/parameter uncertainty and boundary-assumption
uncertainty. Incomplete probability support is **never renormalised**.

The opt-in `arr2013_illustration` rule reproduces D2's **illustrative pragmatic
outer-bin assumptions**, requiring caller-designated frequent and rare first/last
intervals with **already full-tail** masses totalling 1. For the frequent interval
its conditional exceedance is multiplied by `sqrt(0.1)`; for the rare interval
it is replaced with `sqrt(p_conditional)`. These are **not** established RORBwin
defaults or an accepted PyRORB full-tail policy. The default mode never inserts
outer-bin assumptions or inferred mass.

## Published arithmetic controls

| Published example | Printed-value calculation | Reported result | Interpretation |
| --- | ---: | ---: | --- |
| D2 (2013) §7.4 Table 3, flood >50 m³/s | 0.057161 | 0.0572 | Ten 4dp widths, 200 draws/bin, explicit outer-bin illustration |
| Book 4 v4.2 Table 4.4.3, level >10.4 m | 0.0149121 | 0.014911 | Ten 6dp widths, 20 draws/bin; small reported/printed rounding difference |

The Book 4 example's *printed* interval widths sum to `0.158625`;
the reference therefore retains `0.841375` unmodelled rainfall mass,
not an invented frequent/rare tail or a complete full-domain flood AEP.
Numerical comparison tolerances reflect the published decimal precision
(D2 `0.00005`, Book 4 `0.000002`). The published worked examples are
mathematical controls only; they do **not** authenticate RORBwin's native
sampling distribution, output frequency inversion or treatment of boundary bins.

## Verification and limits

[Focused tests](../../tests/test_arr_tpt_reference.py) cover the two published
tables, unequal weights, strict exceedance/ties and a real zero sample,
the existing 0.49/0.51 modelled/unmodelled mass example, opt-in boundaries,
invalid sample counts/weights, duplicate intervals and Decimal-context invariance.
Run `python -m pytest -q tests/test_arr_tpt_reference.py` on a supported Python 3.11–3.14 interpreter.

**Local isolated preflight:** 19 focused pytest tests passed on Python 3.13.5.
Full repository Ruff, strict Pyright and hosted Windows CI must be checked on
the exact PR head. No native executable was launched or original reference
file modified; no product runtime module or saved method was changed.

The retained [#150 native evidence](2026-11-16-issue150-windows-native-receipt.md)
rejects a simple attained-peak-only explanation for RORBwin's frequency summaries
but does not establish its interval weighting, interpolation, smoothing, tails or
precise sampled effective-event inputs. The native-compatible software policy in #190
remains blocked on admitted F6 evidence from #150; scientific acceptance remains
open under #9, #150, #228 (annual support/tails) and #148 (physical convergence).
This bounded arithmetic reference does not close those issues.
