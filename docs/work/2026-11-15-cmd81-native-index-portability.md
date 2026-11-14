# CMD #81 — checkout-stable native fixture index

15 November 2026. This is a portable-fixture authentication correction, **not** a numerical, native-output, or tolerance update.

## Problem

The published self-contained CMD native fixture index in tests/fixtures/regression-v1/native-cmd/index.json recorded the local tests/fixtures/regression-v1/.gitattributes as 24 bytes (CRLF) with SHA-256 b613efadf1c3e99164f2a056d629036edca471f0daa7014a6601cea18dfc959a. The actual committed Git blob is **23 LF bytes**, SHA-256 d7c77edacaaf917faea1f44e0572516c55beb9e07be196a49f7b4d281c9c3fd3. The existing root attributes pinned native-cmd/** bytes, but did not pin the nested attributes file itself. Consequently, on Linux (or Windows without autocrlf) the documented --full-index preflight could fail at the first indexed file.

## Narrow correction

- Add a root-level -text attribute specifically for tests/fixtures/regression-v1/.gitattributes, ensuring the **committed 23-byte LF blob** is checked out without platform conversion.
- Update only that entry in the published 227-file native CMD index: 24 CRLF bytes -> 23 LF bytes and the matching SHA-256. The index itself is byte-preserved under the existing native-cmd/** rule.
- Refresh the parent register's pinned index hash from 2d7285feb413dea281dbe886042d399ce7ae869d626133de4424557cf5be0c17 to 6a6456e5a08a25059eec9a1c88febee7464da7ac98f60d6305232604097a75fe. The index remains 47,636 bytes, and the register remains 553,165 bytes.
- Add a synthetic/fixture-level preflight test checking the exact committed nested attributes bytes and the full index authentication. No candidate snapshot, numerical comparison, original native report, typed input, scalar selector, reference, code kernel or accepted case status is changed.

The old verification receipts remain accurate for their original published revisions; they must not be relabelled as receipts for this modified index. [Public PR #80](https://github.com/Chain-Frost/python-runoff-routing/pull/80) already merged the scalar-runner software; this correction is in the self-contained dataset introduced by PR #82, not another runner.

## Cross-platform Git attribute check (Linux)

A separate **Linux Git mechanics** reproduction was performed without downloading the whole repository: a temporary Git checkout containing the same root `-text` rule and the exact 23-byte nested `.gitattributes` payload preserved SHA-256 `d7c77edacaaf917faea1f44e0572516c55beb9e07be196a49f7b4d281c9c3fd3` under both `core.autocrlf=true` and `core.autocrlf=input`. `git check-attr text` confirmed that text conversion is disabled. No native RORB run or candidate execution occurred.

**This does not establish a fresh Linux Python 3.14 full-repository replay.** That complete cross-platform checkout remains a separate follow-up; the exact-head Windows/Python 3.14 installed-wheel preflight already authenticates all 227 published index entries and 50 CMD cases. The change is strictly an index byte/checkout-control repair.

## Cross-platform cached verification

Use Python 3.14 and an isolated interpreter with the public checkout or a separately installed runner wheel; no native executable and no external custody root are needed for the bundled CMD snapshot. On Linux:

~~~sh
python3.14 -m runoff_routing.regression_dataset preflight tests/fixtures/regression-v1/register.json --set cmd-eligible --full-index --output /tmp/cmd-preflight.json
python3.14 -m runoff_routing.regression_dataset compare tests/fixtures/regression-v1/register.json --set cmd-eligible --snapshot --output /tmp/cmd-snapshot.json
~~~

The first should verify 50 eligible case references and all 227 indexed native files. The second is a deliberately **incomplete** aggregate (48 pass, two zero-flow peak times incomplete; exit 1) despite 19,550 printed ordinate comparisons and 50 peak/volume matches. The cached snapshot is version-qualified prior computation, not a new production engine run or acceptance of physical conservation. Native RORB execution and private PR #67 observations are separate.

Current evidence: the exact old/new index/header SHA-256 values were independently calculated, and public original fixtures were inspected through the connected Git repository. Fresh exact-head Windows CI, Linux installed-wheel/checkout reproduction and independent review are required before merging this patch.
