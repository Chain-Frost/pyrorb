# Native metric protocol extension: bounded reported peak/time and volume

Policy `cmd644-report-scalars-v1`, 14 November 2026. This continues the
[existing #53 draft](https://github.com/Chain-Frost/runoff-routing-investigations/blob/21c0af54a3ffcdda65b160504cd2a7b1c4fcbac7/research/ordinary-cmd-v2-evaluation/NATIVE_METRIC_PROTOCOL_DRAFT.md).
It is frozen for bounded cached validation; independent final acceptance review remains pending.
It does not approve general native metrics or an improved-engine engineering accuracy budget.

## Selected observations and implementation

The selected population is 50 original nominal-m=.8 terminal print sites: H1/H2/H3/N4, the original
36 plus eight newly bound catalogue cases, and two code-2/impervious events. They are overlapping
retained regressions, not independent holdouts. No other exponent or GUI is included in this gate.
The reviewed numerical implementation remains `fea9c80`, published by `5be37dc`; its original numerical
modules are identical to `7d69855`. No routing/reporting module or default is changed by this policy.

Use existing source IDs, input/typed-event hashes, source/control order and complete N+1 horizons.
Reference records bind original report SHA-256, physical Hyd001 terminal-site mapping, scalar line,
one-based character offset, ordinal, original lexeme and unit. The existing public output inspector
validates the table. The explicit native Hydrograph-summary legend must match every table column
in order. Missing scalars remain incomplete individually; ambiguous partial/duplicate mappings and
wrong units are invalid reference material. Never substitute a zero scalar for an absent value.

## Reporting criteria, fixed before candidate evaluation

1. **Peak magnitude:** compare max of actual stored candidate Q[0..N] to the original native
   `Peak discharge,m³/s` token. Use its exact rational inclusive half-last-printed-unit interval,
   clipped at physical zero. No new relative/percentage tolerance or widened budget is permitted.
2. **Peak time:** for a unique nonzero maximum, compare sample-index elapsed hours `i*stored_h`
   with the original `Time to peak,h` token under its own unchanged inclusive print interval.
   Keep every raw row/increment/time token separate; the characterised CMD table label is
   `(i+1)*h`, not the summary's sample-index time. No array/label shift is applied.
3. **Ties and zero flow:** return incomplete for peak time when the candidate's exact stored peak
   has multiple indices, or when the maximum is zero. Retain all candidate tied indices.
   Printed maxima/ties are not independently observed hidden-state ties; no first/last tie-selection
   rule is asserted by this extension. Exact native tie-handling acceptance remains incomplete.
4. **Native reported volume:** only after peak/time validation, compare the separately labelled
   inclusive sample sum `stored_dt_seconds*sum(Q[0..N])` to the original `Volume,m³` token,
   using that token's original inclusive print interval. This reuses the existing native-volume
   convention evidence; it is not a physical-horizon or conservation criterion.
5. **Physical volume:** retain `dt*(Q0/2+sum(Q[1..N-1])+QN/2)` separately as an explicitly derived
   statistic. Do not replace native reported volume with it or count it as physical validation.

Use exact rational values of emitted stored numbers. Compare candidate source and isolated-wheel
outputs under identical field bindings and policies. Pin source/module/wheel and policy/comparator
hashes. No candidate receives native observations or summary scalars as computational inputs.

The auxiliary reporting inventory has 30 CMD reports/104 columns, of which 89 are nonzero and
26 have repeated printed maxima. All 89 nonzero summary times are consistent with the first
printed-maximum sample on the sample-index axis. That is bounded reporting-consistency evidence,
not proof of the exact hidden-state tie algorithm. The six GUI reports are not used for CMD decisions.
The auxiliary volume analysis remains separate from a fresh candidate metric comparison.

## Controls and remaining gates

Before candidate residual evaluation, freeze controls for inclusive interval endpoints and an outside
value; raw-row versus sample-time shift; zero-flow time; exact candidate ties; inclusive volume versus
endpoint-half-weight volume; nonfinite/negative/malformed scalar tokens; wrong/duplicate native site
mapping; duplicate scalar fields; and individual missing scalar observations. No private data or
native execution is required by these synthetic controls.

Conservation is **incomplete**, not passing: source/outlet ownership, initial/terminal state eligibility
and an independently justified physical/numerical budget must be frozen before any balance-residual
evaluation. No conservation budget is selected here and no accepted S/Q state may be recomputed to
force closure. Improved-default engineering accuracy/refinement policies remain a separate engine gate.

These are narrow metric field helpers and custody bindings for #53/#56, not a competing generic
runner, dispatch contract or fourth engine. The maintained-runner integration remains #56 work;
no public shared module is changed by this private validation slice. Reference tokens and full
candidate arrays remain locally custodied; only sanitised counts/statuses/hashes are published.
