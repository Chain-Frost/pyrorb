# Issue #138 — typed domain and effective event edits (15 Nov 2026)

- **Scope:** immutable S1 numeric/text closed-choice boundaries, mode-discriminated editable losses and a single reusable effective-event derivation in `project_batch`. Cross-owner interface posted in issue #138.
- **Original implementation base:** `0675d75b05dba7728b389fdd8af743060b4469b2`. Dedicated branch `feat/issue138-typed-effective-model-20261115`; review PR linked from the issue.
- **Retention:** existing S1 JSON schema 1 and project schema 2 wire codes, source files, immutable regression evidence and numerical engines unmodified. Existing explicit engine choices and schema-1 engine-less meaning remain intact.
- **Tests:** new targeted boundary/edit tests; GitHub quality CI source/installed-wheel runs are the independent acceptance receipt once available. No local checkout/native executable was available in this session; do not claim locally executed numerical or wheel verification.
- **Boundary:** #140 owns PAR/source binding and persisted project edits; #141 owns runnable export; #139 owns the PyRomb writer; #142 owns imported ryan-tools native report grammar and generic statuses. No changes to those owners' modules or the native regression catalogue.
- **Next action:** independent code/quality review of the PR, then integrate the shared resolved-model and source-binding contracts with #140/#141; remaining acceptance cannot be declared from an enum-only diff.
