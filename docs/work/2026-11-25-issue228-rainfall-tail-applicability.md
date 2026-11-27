# #228: rainfall-tail and annual flood-frequency applicability

**25 November 2026; author source follow-up 28 November 2026 — proposed scientific decision; independent scientific review pending.**
Owner: #228 (this scoped contribution; no permanent issue assignment changed). Baseline:
[main b6788a83fbe5](https://github.com/Chain-Frost/pyrorb/commit/b6788a83fbe5eb9ccd68232fe8d92dfb596e0f6b).
[Parent #9](https://github.com/Chain-Frost/pyrorb/issues/9) remains open.
The provisional [project method](../MONTE_CARLO.md) and merged
[#224 arithmetic reference](2026-11-24-issue190-arr-tpt-reference.md) are unchanged.
The initial and pre-write remote checks found no open PR or branch matching #228; issue
#228 was open and unassigned. This is not engineering sign-off, a new estimator,
a native-method admission or an adopted tail policy.

## Decision

**GO:** original-mass restricted-domain description and explicitly conditional research,
subject to valid source/engine/site inputs and correct weighting. **STOP:** general annual
flood-AEP point estimates, unconditional zero-flow mass or full-domain design quantiles
from this input alone. **BOUNDED/INCOMPLETE:** conservative bounds on the full
*design-event surrogate*, not on the real annual flood without a separately justified link.
ARR's published outer-interval approximation is a legitimate candidate for sensitivity
assessment when its assumptions hold; it is not established for the current population.
No missing-tail value is selected here. An adequately supported threshold-specific bound
may eventually suffice without a complete curve, but no such catchment-specific bound
has been demonstrated.

## 1. Population, denominators and event-to-year interpretation

Fix scenario (climate/epoch, catchment, losses, routing parameters), physical output site s
and rainfall duration d. Define X_d as the duration-specific annual maximum rainfall
depth in the rainfall source population. Define p = 1 - F_d(X_d) under a continuous
annual-maximum distribution F_d, so p has uniform probability measure on (0,1);
if a source has atoms, its probability-coordinate/quantile construction must explicitly
preserve them. Smaller p denotes rarer/deeper rainfall. The source may be a point
rainfall distribution; areal transformation and site-specific contributing area are
additional modelling assumptions, not automatically an annual maximum areal-rainfall law.

For a sampled p, the v1 rainfall depth, eligible temporal-pattern identity, loss law and
fixed model inputs produce the routed nonnegative event peak Q_sd. The joint
distribution of these design inputs (including loss/pattern dependence and antecedent
state) defines the **design-event surrogate**. It is not a uniform draw from all storms,
a draw of annual maximum discharge, or a posterior distribution of calibrated parameters.
At a fixed p, a TP/loss ensemble describes response conditional on that p, not a flood
frequency. The rainfall AEP remains an input coordinate, not the output's assigned flood AEP.

Define M_s as maximum of the actual discharge process at s over the defined year.
Annual flood survival is Pr(M_s > q) with denominator all years of the stated scenario.
To identify it from Pr(Q_sd > q), establish that the modelled event population and
conditional response represent the annual flood-generating process. A year's largest
rainfall of duration d may occur under dry conditions while another, smaller storm
generates its maximum flood; annual maximum rainfall durations may also occur in
different storms. Even full p coverage alone cannot resolve these differences.
ARR Book 1 discusses AEP neutrality as an objective, not an established identity [S1].
A sufficient route is a representative calibrated continuous simulation with year maxima,
or a justified joint event-occurrence/response model (including storm definition,
dependence, clustering, baseflow, antecedent conditions, no-event years and competing
mechanisms). For illustration only, independent marked Poisson storms of rate lambda/year
and event-mark survival H(q) give annual survival 1 - exp(-lambda H(q)); H has
denominator events, not years, and neither Poisson occurrence nor independent marks is
assumed in v1. Do not apply that conversion to a rainfall-AMS-weighted result a second time.
A justified design-event approximation with independent flood-frequency validation
is a separate possible engineering route; exact stochastic reproduction is not required
if its accuracy and limitations are demonstrated for the design application.

ARR's terminology includes equality in AEP [S1]; v1's strict exceedance Q > q
matches the TPT equations [S2/S3] and is a project convention. Pr(Q >= q) differs by
Pr(Q = q), especially for zeros/ties. Always declare which is used; do not silently
substitute one for the other. A successful exact zero is a nonexceedance at q >= 0,
with original weight. A printed rounded zero, failed/unsupported/missing result, or
unmodelled tail is not a successful exact zero. Zero routed direct runoff need not mean
zero total river discharge in a year (baseflow/other contributions).

Keep each site's curve and duration distinct. Site IDs bind the physical section,
contributing area and definition of Q; diagnostic outputs or different areas cannot
be treated as interchangeable. Each duration has its own rainfall coordinate, not
independent annual events. ARR's design-duration envelope is the largest eligible
per-duration quantile at a specified probability; it is not the probability
distribution of the joint maximum [S2/S3]. A common conditional envelope is merely
a design selection statistic, and its conditional denominator is duration-specific;
an incomplete required duration prevents a complete envelope. An attained sample
chosen to represent a quantile is not an interpolated hydrograph. A multi-site or
cross-duration annual maximum needs a joint dependence/occurrence model.

## 2. Probability ledger (reuse #224; no new numerical qualification)

For every fixed site/duration/scenario use the adopted planned mass w_i = width in p
of rainfall stratum i, with N_i planned equally weighted conditional draws and event
weight w_i/N_i. Let B be [0.01,0.50], conditional on the adopted source and all input
requirements. For this nominal B (endpoints have no continuous mass):

| Region | p interval | Original mass | Present status |
| --- | --- | ---: | --- |
| Rare | (0,0.01) | 0.01 | Unsupported, not assumed to exceed |
| Interior B | [0.01,0.50] | 0.49 | Modelled input domain, not proof of successful outcomes |
| Frequent | (0.50,1) | 0.50 | Unsupported, not assumed zero |
| Whole design-rainfall coordinate | (0,1) | 1.00 | Not a demonstrated annual flood population |

If actual support is narrower or has gaps, replace these values with the actual
non-overlapping supported widths. Partition 0.49 into successful positive mass W_pos,
successful exact-zero mass W_zero and unavailable planned mass W_miss (failures,
unexecuted or unsupported; retain each cause). Let K(q) be the sum of original
successful weights with Q > q. The lower/upper empirical completions are

    K(q) <= S_surrogate(q) <= min(1, K(q) + W_miss + 0.01 + 0.50).

The bounds describe the planned weighted ledger and unknown outcomes for a fixed
threshold; extending them to population probabilities requires sampling uncertainty
and an accepted joint input law. They are not confidence intervals, and are not
guaranteed bounds on Pr(M_s > q). Do not count a failed event again as an omitted
rainfall tail. Valid zero outcomes remain in the denominator. A conditional
restricted-domain curve uses K(q)/0.49 only if all B outcomes are known; otherwise
its ledger bounds are [K(q)/0.49, (K(q)+W_miss)/0.49]. A successful-only description
K(q)/(W_pos+W_zero) may be explicitly labelled as conditional on computational
success (undefined if denominator zero); selection bias can make it unrepresentative
of B and it cannot replace either curve. An unweighted count/number of runs is not
a probability estimate across unequal strata.

For a target strict survival alpha, the generalized inverse inf{q>=0:S(q)<=alpha}
can be bounded by inverses of lower and upper survival envelopes; the upper endpoint
is unavailable if the upper curve never falls below/equal to alpha on the justified
domain. Without further physical evidence the 0.51 unknown mass alone means no
finite upper inverse is established for alpha < 0.51, even with zero failures; this
includes typical design targets. If bounds are narrow enough at a prespecified
threshold, a separately accepted inequality decision can be sufficient, without a
point quantile. For an illustrative target alpha=0.01, the rare tail alone can
contribute all of alpha. It cannot be dismissed as numerically small. For q>=0,
a proven lower/upper conditional tail probability [l_t,u_t] gives contributions
[w_t*l_t,w_t*u_t]; add to K and account for W_miss separately. Such constraints
must come from source/physical evidence rather than curve aesthetics. No catchment
has been evaluated in this PR.

## 3. Tail options and required evidence

**Frequent tail (mass 0.50):** BoM 2016 very-frequent rainfalls use a declustered
partial-duration series and a different fitted distribution; standard and rare
rainfalls use duration-specific annual maxima [S4]. ARR recommends EY terminology
for very frequent design events [S1]. EY is an expected count; it is not a probability.
Under a Poisson count assumption p = 1 - exp(-EY), but applying this conversion needs
explicit source convention, occurrence assumptions and a continuous joined rainfall
law; it is not a universal relation for clustered storms. BoM publishes corresponding
frequencies and very frequent anchors, not a fully specified joint runoff law.
In particular the 50% IFD is not the two-year event recurrence interval in BoM's
terminology. A defensible extension requires source-consistent AEP/EY mapping,
duration-specific and areal rainfall data, appropriate temporal patterns, seasonal
wetness/loss and preburst dependence, baseflow and independently checked response.
The current ARF range and the v1 joint-law restrictions remain unchanged. Even
modest storms can exceed q on wet/saturated catchments; no observed zero count
in a finite B sample proves that all more frequent rainfall has zero peak.
A strict threshold-specific upper bound of zero requires an upper response envelope
for *all* admissible frequent-tail states (or an independently justified deterministic
no-runoff mechanism); proving no exceedance at one positive q does not establish
an atom at Q=0. A statistical upper limit from observations needs sample selection,
dependence and uncertainty. Without these: leave [0,0.50] contribution unresolved.

**Rare tail (mass 0.01):** BoM publishes rare rainfall depths to 1 in 2000 AEP,
but these are extrapolated estimates with distinct source method/uncertainty [S4].
ARR Book 2 recommends ARF methods into this range subject to limitations; v1 does
not enable its separately guarded extension [S5]. A source-qualified support
extension from p=0.01 to p=0.0005 would recover at most 0.0095 of the coordinate,
still leave 0.0005 rare and 0.50 frequent unresolved; this is potential coverage,
not implemented or approved. Require reconciled IFD joins and duration/region/area
ARF applicability, original TP eligibility and rare-storm/spatial structure,
appropriate loss/preburst/antecedent and routing assumptions including changing
physical mechanisms, and independent flood/physical data with uncertainties.
ARR Book 8 [S6] provides methods linking credible rare rainfall estimates to PMP,
with uncertain assigned AEP and shape checks; this is not a universal law down to
p=0, a guarantee of a hard physical cap, or proof of flood validity. Do not freeze
depth at 1%, use constant ARF without a valid area rule, extrapolate ordinary IFD
arbitrarily, or assume all rarer events exceed q. The current rare contribution is
[0,0.01]; even if a threshold-specific rare lower bound is substantiated, retain
the remaining difference and the separate frequent tail.

**ARR outer-bin candidate:** D2 §4.3 and Book 4 §4.3.3.3 prescribe a pragmatic
geometric approximation when outer bins are sufficiently distant from the
probability region of interest [S2/S3]. With b_f and b_r the conditional exceedance
probabilities at representative outer-bin boundaries, the respective candidates
are sqrt(0.1)*b_f and sqrt(b_r); the actual outer-bin widths must include their
tails, replacing rather than double-counting any interior width. These are
approximations to a conditional probability, not a rainfall/flow distribution
validated at all thresholds, and #224 already verifies their arithmetic as an
explicit illustration. Neither 0.1 nor the approach to certainty establishes a
physical constraint here. In particular an observed boundary count of zero would
make the geometric expression zero, not prove a population zero; b_r=1 would
impute certainty despite unknown rare responses. Sensitivity of the frequent
contribution to its assumed conditional probability is amplified by its 0.50
width. Require an independently justified, threshold-specific margin on excluded
contributions, comparison against alternative admissible response curves and
physical/frequency observations, and sampling and model uncertainty before
using the approximation. Bracketing the desired flood AEP by rainfall inputs is
useful screening, not sufficient for engineering acceptance [S7].

**Partial identification:** if it is independently established that conditional
exceedance h(p,q) is nonincreasing as p increases on the *whole* affected
domain, then h(0.50,q) provides a frequent-tail upper bound and h(0.01,q) a
rare-tail lower bound; use uncertainty envelopes around those boundary values.
Monotone IFD depth does not prove this monotonicity of the marginal response:
TP membership, loss dependence, storage and routing can change with p. ARR
Book 2 §5.9.4 reports counterexamples around TP-bin changes [S5]. Do not
impose monotonicity from isolated samples. A credible threshold-specific
physical bound, regional flood-frequency evidence, or properly validated joint
or continuous model may narrow uncertainty. Prespecify thresholds and a design-
appropriate tolerance, propagate both bounds and uncertainty, and assess against
observed/independent regional flood frequency before acceptance. No tolerance or
tail law is adopted here. Monte Carlo convergence (#148) reduces sampling error,
not structural, climatic, IFD/ARF/loss, routing or missing-support uncertainty.

## 4. Applicability register

Disposition refers to the interpretation, not a blanket model approval.
"Admitted" below is recommended for research only, subject to independent review.

| Interpretation | Source/evidence and assumptions | Domain / contradiction / unresolved requirement | Recommendation |
| --- | --- | --- | --- |
| Original weighted contribution K(q) and mass accounting | S2/S3, #224; fixed site/duration/scenario, valid plan | B only; failures separate; no empirical annual link | Admitted, research only |
| Conditional survival and quantiles given rainfall in B | TPT plus explicit 0.49 denominator; full B outcomes for point distribution | Not annual flood AEP; incomplete outcomes retain conditional bounds | Admitted, research only |
| Full surrogate bounds, no tail assignments | TPT partition, unknown conditional probabilities in [0,1] | Entire p coordinate; no annual interpretation or sampling-confidence claim | Bounded/incomplete |
| Frequent extension from BoM PDS or catchment-specific no-exceedance bound | S1/S4/S5; occurrence conversion, losses, TP, spatial/seasonal response | >50% rainfall coordinate; no approved joint law or proof of zero; ordinary ARF guard | Bounded/incomplete; reject blanket zero |
| Rare extension to BoM limit / Book 8 extreme rainfall | S4/S5/S6; catchment/engine and source-specific physical applicability | <1% p; rare and extreme inputs and flood validation missing | Bounded/incomplete; reject automatic extrapolation |
| Geometric outer-bin approximation | S2/S3, #224; far boundaries and credible conditional trend | Threshold-specific candidate only; no established margins or catchment evidence | Bounded/incomplete, sensitivity only |
| Monotonic response bound | Mathematical conditional assumption; S5 cautions | May fail at TP/loss changes; needs physical and statistical evidence across tails | Bounded/incomplete |
| Full annual flood curve from v1, unweighted pooled duration/site, or success-only renormalisation | S1/S2 conflict with inference; no annual link | No supported annual point estimate; 0.51 unknown rainfall support | Rejected as current interpretation |
| Native RORBwin result rule as hydrological proof | S7/S8, retained negative evidence | F6 algorithm unknown; even authenticated rule would require separate physical evaluation | Rejected as proof; native reproduction remains #150/#190 |

## 5. Source register and contradictions

ARR attribution: Ball, Babister, Nathan, Weeks, Weinmann, Retallick and Testoni (eds.),
Australian Rainfall and Runoff: A Guide to Flood Estimation, © Commonwealth of
Australia (Geoscience Australia) 2019, version 4.2, CC BY 4.0; D2 © Commonwealth
of Australia (Geoscience Australia) 2013, CC BY 4.0. The v4.2 PDF changelog identifies
the climate change update. This is a version-pinned assessment, not an assertion
about the applicability of any later edition (#193). Printed pages below are not PDF indexes.
Direct public sources accessed 25 and 28 November 2026; image checks where noted. The 28 November author review recovered the complete searchable publisher-indexed text for Books 2 and 5, but the PDF page-image endpoints still rejected both files (14,932,303 and 14,287,332 bytes respectively); direct download from this runtime also failed. No local PDF-byte hash or visual verification of those two books is claimed. Primary Project 3 and 6 report page images were accessible and checked as specified below.

| ID | Source / exact locator | Verified observation and limitation |
| --- | --- | --- |
| S1 | [ARR Book 1 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book1_V4.2.pdf), §§2.2–2.4.1, pp. 10–11 (PDF indices 25–26) | Text and page images checked. AEP versus EY terminology, variable wetness, AEP neutrality and joint-probability bias. Not a proof of an annual link or Poisson occurrence. |
| S2 | [ARR Book 4 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book4_V4.2.pdf), §3.2.4 p.24 (index 38), §4.2.2.2 p.44 Eq. (4.4.2) (58), §4.3.3.3 p.64 Eq. (4.4.7) (78), §4.4 Table 4.4.3 p.69 (83) | Text and page images checked. The general theorem needs a complete partition; the specific example uses a restricted mainstream-flow conditioning variable and finite sampled bins. Reuse #224's 0.158625 printed mass and 0.0149121 arithmetic, not a rainfall-tail validation. Both the geometric rule and possible duration-envelope bias are present in this edition. |
| S3 | [Nathan & Weinmann, ARR D2, final 6 May 2013](https://www.arr-software.org/pdfs/ARR_DiscussionPaper_MonteCarlo.pdf), §4.3 Eq. 4 pp.21–22 (29–30), §4.4 p.22, §7.4/Table 3 pp.37–38 (45–46) | Equation, discussion, and worked-text page checked visually; #224 retains Table 3 arithmetic. Historical guidance, uses reciprocal terminology; do not reinterpret old ARI labels as current EY. The source's outer-bin discussion is an approximate method, not native algorithm documentation. |
| S4 | BoM [2016 design rainfall probability terminology](https://www.bom.gov.au/water/designRainfalls/) and [2016 estimation methods](https://www.bom.gov.au/water/designRainfalls/ifd/ifd-estimation.shtml), HTML, unpaginated | Direct text read: distinct AMS and PDS, regionalisation, rare depth extrapolation, 1-in-2000 limit. No equation for annual flood probabilities supplied; no source data for a selected catchment checked. |
| S5 | [ARR Book 2 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book2_V4.2.pdf), §§4.3.1–4.3.3, Table 2.4.1 pp.62–63, Eqs. (2.4.1)–(2.4.4) p.64, Table 2.4.2 pp.65–66; §§5.3.2, 5.5, 5.6, 5.7.3, 5.9.1–5.9.9, 6.3.2; [pinned ARF implementation](../../src/runoff_routing/arr_arf.py) | Direct publisher-indexed text/printed page labels and tables inspected on 28 November; page images unavailable. Derivation and recommended domains differ; conditional TP and spatial source changes matter. See §5.1. Numeric ARF qualification stays with #192/#193. |
| S6 | [ARR Book 8 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book8_V4.2.pdf), §1.3.3/Table 8.1.1 p.4 (18), §3.5.1 p.22 (36), §3.5.2 Eqs. (8.3.1)–(8.3.6), pp.24–25 (38–39) | Text and page images checked; regional rainfall extrapolation limit and uncertainty, rare-to-PMP procedure and applicability checks. No exact tail support or validated site-specific rainfall/runoff curve. |
| S7 | [HARC RORB MC summary discussion](https://harc.com.au/forums/topic/monte-carlo-simulation-summary-results/), HTML, thread concerning v6.32 and subsequent warning discussion; [v6.32 announcement and correction](https://harc.com.au/forums/topic/rorbwin-version-6-32/) | Direct publisher statements checked: input bracketing and reported boundary issues; correction to loss-table equivalence claim. No precise current native F6 warning algorithm or hydrological validity. |
| S8 | [ARR Book 5 v4.2](https://www.arr-software.org/pdfs/ARR_190514_Book5_V4.2.pdf), Fig. 5.3.5 p.28, §3.6.1 pp.67–70, Fig. 5.3.26 p.69, Table 5.3.13 p.70, §§3.6.3/3.7.1 pp.70–71, §§3.7.4–3.7.5 pp.76–79; [Ladson correction](https://tonyladson.wordpress.com/arr2016/standardised-loss-factors/); [retained #150 receipt](2026-11-16-issue150-windows-native-receipt.md), [source register](../SOURCES.md) R1/R3 | Publisher-indexed text inspected on 28 November. Exceedance direction and complete 11-row table reconciled with the historical correction; not a selected-build default or a validated unconditional tail loss law. Page images unavailable. Retained 25-event report contradicts an attained-peak-only explanation (16/16 disjoint summary values at printed resolution); private originals not independently accessed here. |
| S9 | [ARR Project 3, Stage 3, P3/S3/013, 3 December 2015](https://arr.ga.gov.au/arr-guideline/revision-projects/revision-project-reports/project-3-temporal-patterns-of-rainfall/ARR_Project_3_Stage3_Temporal_Patterns_Report.pdf), Part 3 §7.3 pp.43–44 (PDF indices 94–95) | Direct page-image and text verification. Report is explicitly preliminary testing, not a native probability law. Empirical counterexample to unconditional monotonicity. |
| S10 | [ARR Project 6, Stage 3 Phase 4, P6/S3/016B, 23 October 2014](https://arr.ga.gov.au/arr-guideline/revision-projects/project-list/projects/project-6/downloads/ARR_Project6_Phase-4_Report.pdf), §§4.2.1 p.16, 5.3 p.27, 6.7 p.42, 6.9 pp.47–48/Fig. 6-22 (PDF indices 26, 37, 52, 57–58) | Printed pp.16, 27, 42 and 48 page images checked directly; p.47 discussion checked in indexed text. Study sampling and calibration exclusions constrain the target population; §6.7 states median normalisation although figure captions refer to mean. No primary figure/table bytes copied or parameters adopted. |

### 5.1. Author primary-source follow-up — 28 November 2026

**ARF and spatial support [S5].** Table 2.4.1 notes distinguish the 0.01–0.50
empirical fitting interval from the recommended extension to 0.0005. Equations
(2.4.1)/(2.4.2) define the fractional AEP range; (2.4.3) joins durations 12–24 h
and (2.4.4) interpolates area 1–10 km². The small-area note appears to cite the
wrong interpolation equation; the formula and its heading distinguish the two.
The upper area/duration limits are 30,000 km²/168 h, with additional short-duration
area restrictions. The total upstream area at the design site governs ARF;
regional coefficients are not subarea multipliers. §4.3.2 directs more extreme
rainfall to Book 8 using the 0.05% areal-depth anchor. §6.3.2 p.109 changes
spatial-pattern guidance below 1% AEP and recommends nonuniform rainfall for
catchments over 20 km². These are separate conditions, not permission to extend
v1's uniform rainfall model and ordinary ARF guard. The equation cross-reference
and endpoint qualifications belong in #192; no arithmetic requalification here.

**Temporal-pattern support [S5/S9].** Book 2 §5.3.2 p.79 selects rainfall bursts
above the 1-EY depth. Table 2.5.4 p.86 uses 14.4% and 3.2% group boundaries;
§5.9.7 p.96 defines the very-rare *point* set by the ten rarest regional patterns,
not a fourth universal numeric threshold. §5.6 pp.88–90 and Table 2.5.7
specify area/duration ensembles, with regional borrowing when data are sparse.
§5.7.3 p.92 favours continuous simulation for very frequent events and suggests
local or continuous-sequence patterns if event modelling is warranted. §5.9.4
p.94 acknowledges irregular transitions and offers ensemble adjustments.
These recommendations do not prove conditional membership/weights for all p,
exact edge ownership, or a universal native rule. The preliminary Project 3
sensitivity study, §7.3 pp.43–44, specifically found reversals between 20% and
10% design flows; choosing the rarer members of the frequent pool improved
smoothness in its tests. This is evidence against treating rainfall-depth
monotonicity as stochastic ordering of discharge across changing TP pools.
A smoothing remedy is a separate physical choice, not evidence for a bound.

**Loss table and scope [S8/S10].** Book 5 Figure 5.3.26 and Table 5.3.13 provide
exceedance-oriented median-scaled storm IL/CL. The current indexed v4.2 table has
11 rows (0–100 by tens); all 22 printed numeric cells agree with Ladson's
historical corrected table. The v4.1 indexed table also agrees. Thus the
previous historical missing-value concern does not imply a missing cell in the
v4.2 indexed table. This verifies the published tabulation, not the native
6.52 table, interpolation or endpoint semantics. Project 6 §6.7 p.42 describes
median scaling and regional averaging of quantiles, despite mean-scaling
wording in figure captions. The 0/100 rows are finite empirical endpoints;
treating them as physically hard population limits is an extra assumption.
Book 5 §§3.6.3 and 3.7.1 support fixed CL and no systematic AEP adjustment as
reasonable design choices absent contrary evidence, while documenting limits
to dependence research. Project 6 §6.9 notes sparse severe rainfall and a
burst-versus-storm severity mismatch. Lack of a systematic trend is not proof
of conditional independence throughout the tails. §3.7.4/3.7.5 identifies
wetness/seasonality as further population considerations.

**Crucial original-study selection issue [S10].** Project 6 §4.2.1 p.16
selected a partial series of approximately one rainfall event per record year,
with emphasis on floods rarer than 50%; loss fitting used 3 h and 24 h bursts.
Section 5.3 p.27 excluded no-surface-runoff events (IL only known to exceed a
rainfall-depth bound) and some low-runoff/uncertain fits. Thus the regional
quantile curve is based on a screened sample, not the unconditional joint law
of losses over the entire rainfall population. A loss table can still be a
reasonable design approximation when calibrated/validated for the intended
range, but it cannot identify the frequency of zero runoff, particularly in
the very-frequent tail. Preserve the historical exclusion as informative
missingness/censoring, not a project execution failure or proof of a zero atom.
For a future physical study, retain all rainfall-selected events, identify
actual no-runoff outcomes using the gauged/baseflow convention, preserve
censored loss information and estimate or bound the conditional response with
its selection and dependence uncertainty. More random draws from a fitted
loss table do not cure the original selection limitation.

**Pre-burst and unavailable runs [S5/S8].** Book 5 Fig. 5.3.5 p.28 differentiates
storm and burst initial loss. Book 2 §5.9.9 p.97 allows ignoring immaterial
pre-burst; for PB below storm IL it subtracts PB, whereas PB beyond storm IL
calls for pre-burst timing, sensitivity analysis or full-storm treatment.
The v1 rejection of PB > IL is a project restriction, not evidence of no flow.
It can be outcome-informative: the wettest admissible states may disproportionately
fail this restriction. Keep their planned weight unresolved and do not interpret
a success-only curve as unbiased. No clamp or new storm method adopted.

**Physical applicability consequence.** The retained sources support a candidate
restricted-event method, not a complete tail law. Any proposed frequent extension
must address the rainfall selection and censored loss issue above, and any rare
extension must address the separate spatial/TP changes; neither is solved by
new IFD ordinates alone. No catchment-specific tail bound is established. For
example, an assumed frequent-tail mean exceedance upper limit u would imply
an omitted contribution at most 0.50*u; a 0.001 absolute tolerance would need
u <= 0.002 before other sources of error. This is an illustrative sensitivity
relation, not a new engineering tolerance or evidence that the bound holds.
The selected candidate in [#239](https://github.com/Chain-Frost/pyrorb/pull/239)
remains unadmitted (matched originals/sites/IFD/TP/loss chain missing). The
preparation-only PR has since merged at main `9a9b45c02204b75f95c87ef250014f6479a73187`.
Its [physical-source protocol and local handoffs](2026-11-25-issue148-physical-source-protocol.md#7-local-agent-handoffs-nonexecuting-only)
retain five blocked preflight lanes and `simulation_authorised=false`. The
[28 November #148 receipt](https://github.com/Chain-Frost/pyrorb/issues/148#issuecomment-7223978756)
records the failed remote attempt to recover original model/site identities;
source custodian A and source agent B remain the next evidence owners. Do not
infer annual flood qualification from synthetic convergence or use the draft
declaration as authentication.
The sibling [#238](https://github.com/Chain-Frost/pyrorb/pull/238) owns ARF
arithmetic/retained-input precision; no duplicated qualification or policy change.

## 6. Future software and review gates

#190 owns the native result policy only after #150 authenticates F6. No new
tail algorithm is sufficiently specified for production. A separate, owner-approved
read-only reporting addition could expose per-site/duration original K, W_pos,
W_zero, W_miss by cause and separately W_rare/W_frequent, explicit denominator
and strict inequality, threshold-specific surrogate bounds and a research-only
conditional view with missing-mass handling as above. Check existing coverage
first; retain all current IDs and output contracts. It must not label a conditional
or bounded surrogate an annual AEP or adopt the ARR boundary approximation.
Any new reporting schema/method requires its own reviewed #190 scope; native
reproduction and hydrological applicability have independent statuses.

**Remaining evidence and local-agent handoff (read-only):** On a local checkout of
Chain-Frost/pyrorb, read AGENTS.md and this record. The relevant Book 2/5 v4.2
text, equations, tables and selection/dependence evidence have been personally
reviewed in §5.1; do not restart that literature review. Remaining source custody
work is to obtain the exact publisher PDF bytes, record SHA-256/edition and compare
the relevant rendered pages/tables/figures with the indexed text and the original
reports; reconcile the median/mean caption and cross-reference anomalies, and
any official correction or later applicable edition (owners #192/#193). If the
complete files cannot be fetched, the public indexed-text and original-report
image evidence still supports the bounded negative findings; report the precise
visual/hash limitation. Check local ARR/BOM source identities for
one proposed catchment/site/duration only if already retained and approved for
read-only use; state whether appropriate tail source coverage and independently
observed annual flood evidence exist, without deriving new storms or running
routing. Specify whether threshold-specific frequent/rare bounds are physically
defensible and what joint occurrence/annual-flood link is missing. #228 owns this
scientific decision; #192/#193 own ARF/source-version qualification; #148 owns
catchment validation and uncertainty. If available, inspect the original January
2010 RORB Version 6 User Manual chapter 8 and cumulative RORBwin v6.52 release
notes §1.6 only to distinguish historical statement from selected-build evidence;
do not reopen #150's nonexecuting stop decision without new authenticated evidence.
Provide only privacy-safe source identities, hashes where approved, page/equation
locators, independently authored conclusions and limitations; no private paths,
raw records, manuals or confidential catchment details in public GitHub. Do not
launch native software, generate an MC cohort, change software, merge or publish
a release. If any source remains unavailable, document exactly what was not
verified and the owner above.

**Review and validation:** independent reviewer to challenge the probability
coordinate, both denominators, bounds/quantile non-identification, event/annual
mapping, citations and conditional outer-bin applicability; reconcile findings
on the exact PR head and record a separate qualified hydrology review or retain
evidence-blocked status. Author's direct source review is not independent review.
No production/test/fixture/workflow/plan/default changes and no new native/MC runs.
Relative links and source claims checked at author stage (see PR verification).
Two earlier automated code-review receipts at 7ef88f789233 found no findings;
no detailed independent literature review or primary-source retrieval evidence was
returned. The prior Windows quality run 45614929765 passed that old head only.
The 28 November author follow-up at `dd415e7122cce2e117e009abccbe32475cb9580b`
received [automated technical review without findings](https://github.com/Chain-Frost/pyrorb/pull/236#issuecomment-7223982702).
It did not establish independent hydrological acceptance or source-byte custody.
The [quality run for that head](https://github.com/Chain-Frost/pyrorb/actions/runs/46038537826)
was still in progress when reconciliation began. Current-main reconciliation
preserves the reviewed research findings and adds the merged #148 protocol
reference; review and validation receipts must identify the resulting head.
No unrelated scientific gates closed. Keep #228 open for physical evidence,
remaining source-image/hash verification and independent scientific disposition;
#9/#150/#148/#190 remain separate.

## 7. Subsequent evidence and integration boundary — 28 November 2026

The [#148 Prompt B custody receipt](https://github.com/Chain-Frost/pyrorb/issues/148#issuecomment-7224109980)
supersedes the earlier archive-access blocker, not the scientific admission gate.
Nine distinct archived objects were rehashed by that review. The archived IFD
and areal temporal patterns support a 24 h candidate in principle; the 18 h
archived duration is a cross-check, not an admitted duration envelope. Actual
storm median IL, fixed CL and calibration remain unestablished (the Data Hub
loss entries are NaN); physical site/area and approved transform and joint-law
binding remain outstanding. No replacement of missing losses with the saved
deterministic pair is justified. This record relies on the linked redacted
receipt for custody findings, not a second author rehash.

The [#228 Prompt D candidate-specific desk review](https://github.com/Chain-Frost/pyrorb/issues/228#issuecomment-7224138099)
and [#148 Prompt E design review](https://github.com/Chain-Frost/pyrorb/issues/148#issuecomment-7224179801)
retain the preceding scientific stop. For a completely known restricted-domain
ledger with nominal width 0.49, conditional survival targets 1%, 2% and 5%
correspond to target interior contributions 0.0049, 0.0098 and 0.0245,
respectively. The attained strict survival can be smaller because of atoms
and ties. These are conditional research targets, not annual flood AEPs.
No tail law, catchment admission, protocol freeze or simulation authority follows.

The previous reconciled head `7f1d59f58aba6686dfc4b2644b50960e884d16c1`
passed [technical review](https://github.com/Chain-Frost/pyrorb/pull/236#issuecomment-7224136054)
and [Windows quality](https://github.com/Chain-Frost/pyrorb/actions/runs/46039693704).
Main then advanced to `ec395112a8d7fea026ed22585beecaec536ef7cd` through the documentation-only #235 integration.
Reconciliation retains all concurrent main changes, including #232 reader
ownership and updated programme status. Review/CI for the new head must be
verified separately. Integrating this bounded research record does not admit
full annual flood frequency, close #228/#148/#9, change production, or permit
native or Monte Carlo execution. Exact Book 2/5 publisher PDF visual/byte
verification and independent hydrological acceptance remain outstanding.
