# PyRORB naming and compatibility

## Current identity

| Surface | Name |
| --- | --- |
| Product display name | **PyRORB** |
| GitHub repository | [Chain-Frost/pyrorb](https://github.com/Chain-Frost/pyrorb) |
| Python distribution metadata | `pyrorb` |
| Python import package | `runoff_routing` |
| Bootstrap development version | `0.0.0.dev0` |

Install from a source checkout as described in the [quickstart](QUICKSTART.md). PyPI publication is deferred. Changing the local distribution metadata does not publish a package or establish ownership of a PyPI project name. Existing `python -m runoff_routing.<module>` entry points remain available; this identity change does not introduce or rename CLI commands.

PyRORB implements selected RORB rainfall–runoff procedures. It is an independent project and is not endorsed by RORB's authors or custodians. The name does not expand its documented engine capabilities or scientific acceptance.

## Stable compatibility identifiers

The product rename leaves the `runoff_routing` import namespace, engine IDs and numerical profiles, stored engine selections, schemas and JSON `format` identifiers unchanged. Existing `python-runoff-routing-*` format strings remain the supported values; changing their spelling would require a separately scoped compatibility decision and migration.

Installed-package version lookup uses the distribution name `pyrorb`. The package-code fingerprint retains the exact historical domain bytes `b"python-runoff-routing:package-code-v1\x00"` and the `package-code-v1-sha256:` revision prefix. Source changes still produce new fingerprints. The native-capture manifest's `generator.name` remains `python-runoff-routing` as a legacy provenance identifier. Preserve deterministic sampling domains and protocol identifiers independently of display branding.

## Current links and historical evidence

Maintained navigation uses `https://github.com/Chain-Frost/pyrorb`. Dated work records, research notes, curated fixtures, source identities and hashes remain historical evidence. Existing commit-pinned source links and action-run receipts retain their recorded URLs, including the former repository name. Do not apply a repository-wide text replacement to those records, formats or provenance bytes.

The [compatibility contract](COMPATIBILITY.md) and [development guide](DEVELOPMENT.md) govern changes beyond current product identity.
