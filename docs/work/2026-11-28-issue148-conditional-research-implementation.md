# 28 November 2026 — #148 conditional research implementation

Scope: source-independent work requested after the #243 synthetic evidence and #244
Python-only specification. Base `e80e56dbd1089874b527b98f9d1606532474c733`. This branch is separate from concurrent
#243/#244; #245 remains the only other-PC evidence-custody issue. No original private
data, physical M04 run, native execution, stochastic sampler invocation, new preflight,
adopted method, or production frequency/solver change. No scientific issue is closed.

## Exact read-only conditional ledger

[Research kernel](../../repo-scripts/mc_conditional_research.py) uses Decimal allocation
masses as exact rational numbers and each stratum's full planned count. It preserves
the restricted rainfall-coordinate denominator 0.49, ties, true zero, unknown mass,
strict survival and attained generalized inverse. It does not use rounded per-event
serialized weights, discard failures, renormalize the observed prefix or extrapolate
the 0.51 excluded domain. Unknown mass is a logical interval under a defined
nonnegative latent response, not an assumption of physical admissibility.

The adapter requires externally pinned immutable project, request, ledger and optional
wheel, one v1 Python CMD scenario/duration population with explicit original masses
0.49/0.01/0.50, unique requested project print ID, and the existing full verified
result iterator. It reads to exhaustion (including final integrity checks) and
rechecks pins before returning. Existing verification owns sample/engine/source
binding; this code is not another ledger parser or runner. External pins must be
obtained independently; matching a digest does not establish scientific custody.
The mathematical kernel alone cannot authenticate arbitrary rows.

## Candidate reference intervals

[Confidence kernel](../../repo-scripts/mc_conditional_confidence.py) implements the
#243 weighted Hoeffding/KL split-reference-alpha proposal for an independently frozen
family of K <= 256 CDF grid points across sites. For normalized stratum masses v_h and
positive counts n_h, S = sum(v_h^2/n_h), b = max(v_h/n_h). The Hoeffding radius is
sqrt(S log(4K/alpha)/2); the weighted Bernoulli KL limit is b log(4K/alpha).
Each family receives alpha/2; union over the grid and both directions retains
the requested reference error alpha. No assumption of independence between sites
or censored endpoint observations. Independence applies to the complete latent
weighted draws, which still requires separate admission.

For the weighted KL argument, convexity on each bounded indicator contribution
after scaling by b and concavity in the Bernoulli mean bound the product moment
generating function by that of a scaled Bernoulli with mean F. Invert this bound
in both directions. Decimal directed division and adjacent representable
correctly-rounded Decimal logarithms enclose the exact log, with subsequent rational
arithmetic. The square root is rounded upward by integer square root and the
56-step KL brackets return only certified exterior trial means. Intersect the
two valid reference enclosures; use observed lower and upper CDFs to preserve
pathwise censoring enclosures. Monotone tighten and invert a fixed finite grid
without inventing an upper quantile at an unresolved tail.

This is a candidate, not an adopted reference construction. Exact finite-distribution
checks support its numerical behavior; they are not a full independently reviewed
one-engine scientific qualification. Do not change tolerances, alpha or physical
execution budgets on the basis of this implementation.

## Verification and handoff

Linux CPython 3.13.5: 23 focused deterministic tests passed on the four exact
new source/test blobs in an isolated directory. The tests cover original Decimal
boundary preservation, unequal weights, ties, zero, missing/failed draws, duplicates,
invalid values, final reader failure, finite-distribution convolution, censoring,
rare-tail narrowing, zero/one and finite-grid inversion. No package install or
routing took place in this isolated environment. The four Git blob hashes match the
locally executed bytes. The appended real verified-ledger integration test uses
the repository's two-event authored deterministic fixture and tests prefix bounds,
external pin rejection and read-only behavior. It requires full repository CI and
has not been run locally. GitHub clone/network DNS is unavailable locally; Ruff,
strict Pyright, full CI and independent exact-head review remain required.

Next: complete actual reader integration/quality review, then agree and qualify
the exact one-engine study construction and independent oracles before activation.
Do not repeat the archived two-engine study. #245 remains sufficient for the
other-PC custody/validation/loss/rights scope; no new local evidence request.
`simulation_authorised=false` for physical admission; #148/#9 remain open.
