# Shellferry

**Turn online shell installers into portable, verified offline bundles.**

[中文](README.zh-CN.md) · [Install](docs/installation.md) · [Verified recipes](skills/shellferry/references/validation-matrix.md) · [Contribute](CONTRIBUTING.md)

[![Checks](https://github.com/nanocm/shellferry/actions/workflows/ci.yml/badge.svg)](https://github.com/nanocm/shellferry/actions/workflows/ci.yml)

Give Shellferry an installation command and a target machine. It collects the scripts, binaries, and dependencies needed during installation, then builds a bundle you can carry to a server with unreliable or no internet access.

```text
Input:   curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
Target:  Ubuntu 22.04 · x86_64 · ordinary user
Output:  zoxide.tar.gz + SHA-256 + installation instructions + verification report
Test:    Podman/Docker --network none
```

Shellferry is an **agent skill with Python helpers**, with 106 pinned recipes for 105 software packages. An agent handles unfamiliar installation logic; the helpers apply exact patches, verify hashes, package files, and run installation checks. Known recipes also work directly from the command line.

The skill instructions and technical references are maintained in English. Explanations and generated installation guidance follow the user's language.

## Install

Choose one installation method. You can install from GitHub or use a [release archive](https://github.com/nanocm/shellferry/releases) for [local installation](docs/installation.md#local-checkout-or-release-archive).

### Codex or Claude Code with `npx`

Requires Node.js 22.20+. Choose your agent:

```sh
# Codex
npx skills add nanocm/shellferry --skill shellferry --agent codex --global

# Claude Code
npx skills add nanocm/shellferry --skill shellferry --agent claude-code --global
```

To install into the current project, omit `--global`. To target both agents, use `--agent codex claude-code`. [Local paths, updates, and removal](docs/installation.md#skills-cli-npx) use the same Skills CLI.

### Claude Code plugin

Run inside Claude Code:

```text
/plugin marketplace add nanocm/shellferry
/plugin install shellferry@shellferry
```

Invoke the plugin as `/shellferry:shellferry`. Installing the standalone skill through `npx` instead gives `/shellferry`.

### Codex built-in installer

Ask Codex:

```text
$skill-installer install https://github.com/nanocm/shellferry/tree/main/skills/shellferry
```

Invoke it as `$shellferry`. The installer in your Codex version chooses its skill directory; [the guide](docs/installation.md#codex-built-in-installer) covers current and legacy locations.

### Local checkout or release archive

Open a terminal in the repository or extracted release and choose your host:

```sh
# Codex
python3 install.py

# Claude Code
python3 install.py --host claude
```

Windows PowerShell uses `python` instead of `python3`. This method works offline with Python 3.10+ and the complete package. It supports managed updates and backups. See the [installation guide](docs/installation.md) for all options.

## Use

In Codex:

```text
Use $shellferry to convert this installer into an offline bundle.
Target: Ubuntu 22.04, x86_64, ordinary user.
Include resources needed by every install stage and verify with Podman offline.

curl -fsSL https://bun.sh/install | bash
```

You receive an archive, its SHA-256 checksum, a local installer, and a report tied to the exact artifact tested. Transfer the archive to the destination and follow its generated installation instructions.

In Claude Code, start the same request with `/shellferry` for a standalone skill or `/shellferry:shellferry` for the plugin. Preparing bundles requires Python and local execution access; verification also needs Podman or Docker.

## What it does

- **Follows the installer.** Handles version lookups, platform selection, nested scripts, native bootstrappers, themes, and installation-time shell setup.
- **Preserves reviewable changes.** Keeps original scripts and exact patches. A changed upstream script or unexpected patch count requires review.
- **Pins resources.** Records URLs and SHA-256 values, distinguishing official checksums from locally computed pins.
- **Tests the actual archive.** Extracts it into a fresh location, installs as a normal user with `--network none`, and checks functionality and repeat installation.
- **Shares prior work.** Recipes, environment details, failure fixes, and hash-bound evidence travel with the repository. Other users do not need the author's download cache.

For a new installer, the agent traces system packages, compilation steps, and programs that download further resources, then creates and tests an adaptation for the requested target.

## Requirements

| Where | Requirements |
| --- | --- |
| Preparation machine | Python 3.10+, access to the selected upstream resources; a filesystem-capable agent for new adaptations |
| Verification machine | Linux with a working Podman or Docker engine and a matching container image; Windows can use WSL2 |
| Destination machine | Commands and libraries declared by the selected recipe; no agent or Python is required by the generated shell wrapper |

For example, `bun-ubuntu22` carries private copies of `unzip` and its library. The generic `bun` recipe expects `unzip` already installed. Read a recipe's prerequisites before selecting it.

## Build a known recipe without an agent

This example downloads zoxide, builds an archive, and tests it on Ubuntu 22.04:

```sh
python3 skills/shellferry/scripts/catalog.py list
python3 skills/shellferry/scripts/catalog.py show zoxide
python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide
python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz

# Image preparation may use the network. The installation test does not.
podman pull docker.io/library/ubuntu:22.04
python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \
  --engine podman --image docker.io/library/ubuntu:22.04 \
  --output dist/zoxide.validation.json
```

On Windows, building works with native Python. Run the verification command inside WSL using the corresponding Linux paths. For Docker, use `docker pull` and `--engine docker`.

On the destination, for this zoxide example:

```sh
sha256sum -c zoxide.tar.gz.sha256
tar -xzf zoxide.tar.gz
sh zoxide/install.sh --check
sh zoxide/install.sh
export PATH="$HOME/.local/bin:$PATH"
eval "$(zoxide init bash)"
```

## Tested scope

**105 distinct software packages have passed Linux x86_64 offline installation tests.** Each of the 106 current recipes has evidence matching its recipe, source pins, builder, and verifier. Tests exercise the final archive, ordinary-user installation, a path containing spaces, a local function, and repeat installation. The additional Bun environment recipe counts as one software package.

| Area | Recipes |
| --- | --- |
| Runtimes and package tools | Bun, Deno, pnpm, Yarn + Node.js, nvm + Node.js, rustup + Rust |
| Python and environments | uv, Ruff, Pixi, Poetry, PDM, Micromamba |
| Shell and terminal | Starship, Atuin, zoxide, fzf, skim, Oh My Zsh, Bash-it, Bats |
| Development and data | just, Go Task, xmake, cargo-dist, cargo-auditable, Dolt, rqlite |
| Cloud and operations | Helm, Flux, OpenTofu, k3d, Istio CLI, Porter, Trivy, Syft |
| Version managers | fnm, mise, Volta, pyenv, rbenv, GHCup, opam, Perlbrew |
| SDKs, editor and cloud CLI | SDKMAN! + Temurin JDK, .NET SDK, code-server, Pulumi + random provider, Google Cloud CLI + bundled Python |

These are selected examples; the [full matrix](skills/shellferry/references/validation-matrix.md) lists all versions, functional checks, environments, and reports. The 106 recipes comprise **101 shell-installer, three source-installer, and two Python-installer adaptations**. Most new tests use Ubuntu 22.04; some original recipes use Ubuntu 26.04. [Known limitations](skills/shellferry/references/known-limitations.md) records prerequisites and excluded candidates, including Miniforge's explicit rejection of paths containing spaces.

Installing a manager does not include every runtime or project dependency it can download later. The current fnm/mise tests cover manager functionality; npm, Python, Cargo, and Conda project dependencies need their own collected resources. ARM64, macOS, Alpine, systemd services, and kernel modules are not covered by the published Linux x86_64 campaign.

## Reuse prior verification

```sh
python3 skills/shellferry/scripts/catalog.py evidence zoxide \
  --os-id ubuntu --os-version 22.04
```

Evidence matching checks the recipe, source pins, operating-system identity, builder, and verifier. A match lets the agent reuse the recorded conversion decisions within their prerequisites. It does **not** mean a newly built archive has already been executed. An explicitly requested fresh offline test still runs.

Downloads have an optional local cache. A fresh user can build from the pinned official URLs without it. The repository carries small scripts and evidence, not the author's binaries or container images. [Read the evidence model](skills/shellferry/references/shared-evidence.md).

## Repository layout

```text
skills/shellferry/       Installable, self-contained skill
  SKILL.md              Agent workflow
  assets/catalog/       Pinned recipes and installer snapshots
  scripts/              Inspection, conversion, packaging, evidence, verification
  references/           Detailed guidance and recorded test evidence
install.py              Local install/update/status/uninstall
tools/                   Repository checks and release packaging
docs/                    Installation and release instructions
plugin.json              Portable Agent Plugins metadata
.claude-plugin/          Claude Code plugin and marketplace manifests
```

The plugin manifest is packaging metadata, not a claim that the project is listed in a plugin directory. Shellferry needs local execution capabilities; a chat-only host cannot build and test these artifacts.

## Development

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
python3 tools/package.py
```

Unit tests use no network. Linux runs the shell regressions; other systems skip those checks. The optional GitHub Actions integration workflow performs a fresh download and Docker offline test for selected recipes. See [CONTRIBUTING.md](CONTRIBUTING.md).

Installation compatibility checks use the real Skills CLI and, when available, Claude Code. They install an extracted release into isolated directories, compare the full skill payload, and check relocated evidence. See [installation verification](docs/installation.md#installation-verification).

## License

Shellferry's own code and documentation are [MIT licensed](LICENSE). Bundled upstream scripts and embedded fragments retain their original licenses; attribution and license texts are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Downloaded software keeps its upstream license.

Some separate installer repositories have no established redistribution grant. Those complete scripts are fetched at build time and excluded from this source distribution; the [source notices](skills/shellferry/THIRD_PARTY_NOTICES.md) identify them. Review their terms before redistributing generated bundles.
