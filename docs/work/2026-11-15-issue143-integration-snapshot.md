# Temporary #143 integration snapshot — DO NOT MERGE

This synthetic verification tree overlays unmerged implementation files on main
without merging any owner PR into main, and resolves only their overlapping
files for testability. It is **not** a reference implementation or release.

- Main base `4d7c48a562920767ed00fa23b6da7a17089d201d`
- #138 `576b4904d727124e6538bd58421cd05360595458`
- #140 `4dcad73e39652d67355296ced7be45f3327eb98e`
- #141 `d5f13a6639b78b4d3c40d7729b9be4331f9360bc`
- #139 `eba65891ad8b81995684532c7eeac5c0bd6a0022`
- #142 `a0e41a9077fa42d960a35199f832f40cede54fa1`
- #143 `2814a7aab9de3de32cc2297b855bb603b6c922aa`

The shared code path `rorb_codec.py` incorporates #138's typed enum
construction atop #139's external PyRomb writer; `test_rorb_roundtrip.py`
combines each owner's expected behavior. `pyproject.toml` retains both the
runtime canonical ryan-reader pin and the opt-in PyRomb writer pin. General
README navigation is combined for test use only. All other implementation
source objects retain their respective owner branch Git blobs unchanged.

No native executable is installed or launched by the approved CI. Source/wheel
checks against this tree demonstrate provisional software integration only.
