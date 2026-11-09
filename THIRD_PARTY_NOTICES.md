# Third-party notices

Shellferry's original code and documentation use the [MIT license](LICENSE).
Bundled upstream installer scripts and copied or adapted recipe fragments retain
their original licenses. The project license does not replace those terms.

The complete notices travel with every installed skill:

- [Source attribution and licensing notes](skills/shellferry/THIRD_PARTY_NOTICES.md)
- [Verbatim upstream license texts](skills/shellferry/LICENSES/)
- [Machine-readable provenance and SHA-256 inventory](skills/shellferry/third-party.json)

Upstream-derived portions retain their original GPL, LGPL, EPL, MPL, and
permissive licenses. The installed skill's notices identify each scope and the
catalog records explicit modifications; the project MIT grant covers only
Shellferry's original work.

Several independent installer sources, including pnpm, cargo-binstall, Yarn,
Poetry, Micromamba, Scala CLI, k0s, Pulumi's hosted installer, and Google Cloud's
hosted bootstrap stages, have no established complete-installer
redistribution grant in the reviewed source. Their complete scripts are excluded
from the repository and installed skill. Recipes fetch and verify them at build
time; publishing generated bundles containing them requires a separate review.

This repository and the skill release archive contain no downloaded application
binaries. Generated offline bundles can carry additional application and
dependency licenses; their redistribution requires a separate review.
