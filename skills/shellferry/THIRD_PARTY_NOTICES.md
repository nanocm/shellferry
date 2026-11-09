# Third-party source notices

Shellferry's original code and documentation are MIT-licensed. The upstream installer source files in `assets/catalog/`, and upstream code copied or adapted into recipe patches, retain their own licenses. The project MIT license does not replace these licenses. Copyleft source and adapted fragments retain their GPL, LGPL, EPL, or MPL terms as identified in the inventory.

This notice covers source distributed with the skill. The source repository and installed skill contain no downloaded software binaries or generated offline bundles. Distributing a generated bundle can create additional obligations for the applications and dependencies inside it; this source notice is not a complete license inventory for those bundles.

The full, verbatim upstream license texts are in [LICENSES/](LICENSES/). [third-party.json](third-party.json) records the source URLs, fixed commits for license documents, SHA-256 digests, and file-level provenance. License reference commits and installer snapshots are recorded separately: a license file obtained at a release tag does not establish that a hosted installer endpoint served the script from that tag. Original copyright and attribution comments in installer snapshots are preserved.

## Installer sources and recipe fragments

Paths below are relative to `assets/catalog/`. Each row also covers copied or adapted upstream code in the corresponding `recipe.json`. Small wrappers authored for Shellferry remain under the project MIT license; they are identified separately in the machine-readable inventory.

| Catalog and upstream source | License and preserved notices |
| --- | --- |
| `atuin/sources/install.sh` | [Atuin MIT](LICENSES/atuin-LICENSE.txt) |
| `atuin/sources/atuin-installer.sh` | The generated script explicitly declares MIT; [cargo-dist 0.31 template MIT](LICENSES/cargo-dist-0.31-LICENSE-MIT.txt), with [Atuin MIT](LICENSES/atuin-LICENSE.txt) project notice |
| `bun/sources/install.sh`, `bun-ubuntu22/sources/install.sh` | [Bun upstream license declaration and notices](LICENSES/bun-LICENSE.txt); see the Bun note below |
| `chezmoi/sources/chezmoi.sh` | [chezmoi MIT](LICENSES/chezmoi-LICENSE.txt), [godownloader MIT](LICENSES/godownloader-LICENSE.txt), [shlib Unlicense](LICENSES/shlib-LICENSE.txt); script copyright 2017 Nick Galbreath and 2018 Tom Payne |
| `deno/sources/install.sh` | [deno_install MIT](LICENSES/deno-install-LICENSE.txt); original installer copyright comments preserved |
| `direnv/sources/direnv.sh` | [direnv MIT](LICENSES/direnv-LICENSE.txt) |
| `fnm/sources/install.sh` | [fnm GPL version 3](LICENSES/fnm-LICENSE.txt); includes derived fnm recipe patch fragments, excluded from the project MIT grant |
| `helm/sources/helm.sh` | [Helm Apache-2.0](LICENSES/helm-LICENSE.txt) and [Glide MIT](LICENSES/glide-LICENSE.txt) for the acknowledged installer ancestry |
| `just/sources/install.sh` | [just CC0-1.0](LICENSES/just-LICENSE.txt) |
| `mise/sources/install.sh` | [mise MIT](LICENSES/mise-LICENSE.txt) |
| `nvm/sources/nvm.sh` | [nvm MIT](LICENSES/nvm-LICENSE.txt) |
| `oh-my-posh/sources/install.sh` | [Oh My Posh MIT](LICENSES/oh-my-posh-COPYING.txt) |
| `pixi/sources/install.sh` | [pixi BSD-3-Clause](LICENSES/pixi-LICENSE.txt) |
| `rclone/sources/rclone.sh` | [rclone MIT](LICENSES/rclone-COPYING.txt) |
| `ruff/sources/install.sh` | The generated script explicitly declares MIT; [cargo-dist 0.31 template MIT](LICENSES/cargo-dist-0.31-LICENSE-MIT.txt), with [Ruff MIT](LICENSES/ruff-LICENSE.txt) project notice |
| `rustup/sources/rustup.sh` | rustup [MIT](LICENSES/rustup-LICENSE-MIT.txt) or [Apache-2.0](LICENSES/rustup-LICENSE-APACHE.txt) |
| `starship/sources/install.sh` | [Starship ISC](LICENSES/starship-LICENSE.txt) |
| `task/sources/install.sh` | [Task MIT](LICENSES/task-LICENSE.txt), [godownloader MIT](LICENSES/godownloader-LICENSE.txt), and [shlib Unlicense](LICENSES/shlib-LICENSE.txt) |
| `uv/sources/install.sh` | The generated script explicitly declares MIT; [cargo-dist 0.32 template MIT](LICENSES/cargo-dist-0.32-LICENSE-MIT.txt), with uv [MIT](LICENSES/uv-LICENSE-MIT.txt) or [Apache-2.0](LICENSES/uv-LICENSE-APACHE.txt) project notices |
| `zoxide/sources/install.sh` | [zoxide MIT](LICENSES/zoxide-LICENSE.txt), plus Rustup-derived code under [MIT](LICENSES/rustup-zoxide-origin-LICENSE-MIT.txt) or [Apache-2.0](LICENSES/rustup-zoxide-origin-LICENSE-APACHE.txt) |

## Templates and inherited code

- The uv installer identifies cargo-dist 0.32.0; the Ruff and Atuin second-stage installers identify cargo-dist 0.31.0. The cargo-dist shell template explicitly selects MIT. Both versioned template license texts are retained, including the copyright notice for Axo Developer Co.
- The chezmoi installer credits Nick Galbreath, Tom Payne, `client9/shlib`, and `goreleaser/godownloader`. The Task installer identifies godownloader and labels its embedded shlib code as public domain. The relevant MIT and Unlicense texts are retained.
- The Helm installer identifies the MIT-licensed Glide installer as its basis. The Glide notice credits Matt Butcher and Matt Farina, Hewlett Packard Enterprise Development LP, and Google.
- The zoxide installer identifies Rustup code from commit `4c1289b2c3f3702783900934a38d7c5f912af787`. The Rustup MIT and Apache license files from that exact commit are included separately from those for the current rustup catalog entry.

## fnm source and modifications

The fnm installer is distributed under its upstream GPL version 3 license. The unmodified source snapshot is included as `assets/catalog/fnm/sources/install.sh`; `assets/catalog/fnm/recipe.json` explicitly records each old and replacement fragment used to create the offline variant. The changes pin the release, substitute the local resource-copy operation for downloading, and check for the local copy command. These fnm-derived fragments and resulting modified installer retain the upstream GPL terms. They are not relicensed by Shellferry's MIT license. Upstream provenance and the source snapshot digest are recorded in `third-party.json`.

## pnpm installer fetched at build time

The complete `pnpm/get.pnpm.io` installer does not have an established license grant in the source reviewed on 2026-11-09. It is therefore **not vendored** in the repository or installed skill. The pnpm application's license is not used as a substitute for permission covering this separate installer repository.

The recipe fetches the installer when a user prepares a bundle, from the fixed commit URL below, and requires the recorded digest:

```text
https://raw.githubusercontent.com/pnpm/get.pnpm.io/7c26e549143daf5cf072a38c428170ad8eccaf2d/install.sh
SHA-256: 53d3ad6ef67d49d6951f3326bd3180e5c504c8f695bcdf73bb61ec7a4d4c9407
```

The recipe adds an independently authored `download()` override immediately before the installer's final entrypoint. It does not copy the original download function into the repository. The installer identifies some initial helper code as originating in Homebrew; [the Homebrew installer BSD-2-Clause notice](LICENSES/homebrew-install-LICENSE.txt) is retained for that portion only. It does not establish a license for the remainder of the pnpm installer. Shellferry does not publish generated pnpm offline bundles.

## Bun upstream notice

Bun's upstream `LICENSE.md` begins with the declaration “Bun itself is MIT-licensed.” The file also contains notices and redistribution information about dependencies included in Bun binaries. The actual upstream text is preserved in full, without inventing a separate copyright owner or replacing it with a generic MIT template. The catalog distributes the installer script; the source repository and installed skill do not distribute Bun binaries. Anyone redistributing a generated Bun bundle must assess the notices and obligations applicable to that binary, including its bundled dependencies.

## Updating this inventory

When adding or updating an upstream installer, retain its copyright and attribution comments, identify its license and any embedded template or copied-code licenses, add the applicable original license text, and update the source URL and digest in `third-party.json`. If redistribution permission for a complete installer has not been established, do not add its source to the repository based only on the application's name or license.

## Expansion to 105 software packages

The complete inventory now covers 120 components and 144 license/notice files.
[third-party.json](third-party.json) identifies each distributed source or
recipe fragment, its applicable components, fixed license-document sources, and
SHA-256 values. The added attributions are listed in
[THIRD_PARTY_EXPANSION.md](THIRD_PARTY_EXPANSION.md).

The following upstream-derived portions are outside the project's MIT grant:

- fnm, Air, golangci-lint: GPL version 3.
- chsrc installer: GPL-3.0-or-later; its embedded xy.h retains its MIT terms.
- GHCup: LGPL-3.0, with the referenced GPL text retained.
- opam: LGPL-2.1 with the upstream linking exception.
- babashka, clj-kondo, jet: EPL-1.0.
- Garden: MPL-2.0. OpenTofu's installer explicitly declares Apache-2.0; its
  repository also contains MPL-2.0 text. Both are retained with their scopes.

Complete installer redistribution permission remains unestablished for the
separate pnpm, cargo-binstall, Yarn Classic, Poetry, Micromamba, Scala CLI, and
k0s, Pulumi hosted installer, and Google Cloud hosted bootstrap sources listed
under `external_sources`. They are fetched at build
time and are not vendored here. Where adaptation needs an identification anchor,
the repository retains only the minimal anchor and independently authored
replacement. This does not grant permission to redistribute generated bundles
containing the complete installers.

Generated cargo-dist scripts explicitly select MIT for the template. Different
template versions have separate fixed-source license records. Other inherited
code includes godownloader and shlib, Deno installer ancestry in dprint/Goose/Fly,
Starship ancestry in Railway, and supports-hyperlinks ancestry in Oh My Zsh.
Original notices and full license texts are retained in the inventory.
