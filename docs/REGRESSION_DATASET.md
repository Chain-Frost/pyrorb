# Public independent regression controls v1

Tracked by roadmap #1 and private data issue #56; engine/result type ownership remains public #74. These **ten small original authored fixtures** are permission-cleared, standalone, SHA-256-pinned and analytically checkable. They require no private repository and no native RORB executable. See [register.json](../tests/fixtures/regression-v1/register.json), whose full \`authored\` selection is separate from its three-case smoke subset.

| Feature | Analytic oracle (not CMD evidence) |
| --- | --- |
| Zero runoff | Q = 0 |
| Exact equilibrium | Q = 5 m³/s, K = 2 hours, S(0) = 36,000 m³, I = 5 m³/s |
| Linear recession | Q(t) = 10 exp(-t/2) m³/s |
| Prescribed pulse | Q(1) = 4(1-exp(-1/2)); thereafter exponential recession |
| Junction and reversed order | exact component-wise addition, no storage |
| Initial loss equality | 10 mm consumed exactly, zero excess |
| Initial loss crossing | 1 mm on 1 km² in 1 hour = 1000/3600 m³/s, no routing |
| Initial storage | Q(t) = 2 exp(-t) m³/s |
| Full recession | Q(t) = 3 exp(-t/2) for ten complete samples |

Four further specifications are present as **gaps**: invalid negative storage time, unsupported control, nonlinear refinement/conservation and repeated-event state isolation. The complete public \`all\` selection intentionally returns non-success until they have executable oracles and typed-result coverage. Analytic no-routing controls are **not** claims about CMD time phase, loss processing or routing. Expected values are independently derived mathematical references, not solver-generated snapshots.

## Source and installed-wheel commands (Windows / Python 3.14)

On a checkout containing the companion CLI:

\`\`\`powershell
py -3.14 -m pip install -e .
New-Item -ItemType Directory -Force .local | Out-Null
py -3.14 -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set smoke --engine python --output .local/public-smoke-001.json
py -3.14 -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set authored --engine python --output .local/public-authored-001.json
py -3.14 -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set all --engine python --output .local/public-all-gaps-001.json
\`\`\`

For comparison, the future engine adapter must produce an **independently computed candidate CSV** in the existing PR #58 S5 ordinate format. Never use copied oracle rows as model predictions. Then:

\`\`\`powershell
py -3.14 -m runoff_routing.regression_dataset diagnose tests/fixtures/regression-v1/register.json --case pub-linear-recession --engine python --csv .local/engine-ordinates.csv --implementation <40-character-Git-SHA> --output .local/recession-001.json
py -3.14 -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set linear --engine python --csv .local/engine-ordinates.csv --implementation <40-character-Git-SHA> --output .local/linear-001.json
py -3.14 -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set authored --engine python --csv .local/engine-ordinates.csv --implementation <40-character-Git-SHA> --output .local/full-001.json
\`\`\`

For installed wheel, install the wheel **outside** the repository, verify \`python -c "import runoff_routing; print(runoff_routing.__file__)"\` points into the isolated install, pass \`--wheel <wheel-path>\`, and retain its SHA-256. The comparison report captures actual package import origin, source revision, wheel hash, dataset hash, candidate CSV hash, per-field mismatches, expected/actual populations, Python and platform. Native CMD still requires a separately provisioned user executable only when explicitly selected as a computation engine under #74; this cache comparator never starts it.

The runner never writes goldens and uses exclusive-create output; a missing candidate row, extra physical column, changed native/analytic reference token, shift or truncated horizon, or invalid scalar prevents an aggregate pass. Public installation/ordinary tests do not import the private research repository. The general improved-engine conservation/stability/refinement budgets and #53 native reporting metrics remain **open**; CMD printed allowance cannot substitute for their independent engineering justification.
