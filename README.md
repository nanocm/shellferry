# Shellferry

Turn online shell installers into portable offline bundles.

[中文](README.zh-CN.md) · [Installation guide](docs/installation.md) · [Verified software](skills/shellferry/references/validation-matrix.md) · [Contributing](CONTRIBUTING.md)

[![Checks](https://github.com/nanocm/shellferry/actions/workflows/ci.yml/badge.svg)](https://github.com/nanocm/shellferry/actions/workflows/ci.yml)

A `curl | sh` command can download another script, query a release API, fetch binaries, and set up a runtime. On a server with unreliable internet, any of those steps can fail. Shellferry collects the resources on a connected machine and rewrites the installer to read them from a local bundle.

Give it the command and the target machine:

```text
Command: curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
Target:  Ubuntu 22.04, x86_64, ordinary user
Output:  zoxide.tar.gz, SHA-256, local installer, installation instructions
```

Shellferry is a skill for Codex and Claude Code, with Python helpers for downloads, exact script patches, checksums, and packaging. It includes **106 pinned recipes covering 105 software packages**, with recorded offline installation tests. New adaptations need an agent with local file and command access.

**Docker and Podman are optional.** Shellferry builds and packages by default, using Python 3.10+ and access to the selected resources. Request an offline installation test to receive a container test report for that exact archive. The destination machine runs the bundled installer directly.

## Install

Choose one method for each agent.

### With npx

Requires Node.js 22.20+:

```sh
# Codex
npx skills add nanocm/shellferry --skill shellferry --agent codex --global

# Claude Code
npx skills add nanocm/shellferry --skill shellferry --agent claude-code --global
```

Use `--agent codex claude-code` to install for both. Omit `--global` for the current project. The [installation guide](docs/installation.md#skills-cli-npx) covers release pinning, updates, and removal.

### Claude Code plugin

Run inside Claude Code:

```text
/plugin marketplace add nanocm/shellferry
/plugin install shellferry@shellferry
```

Invoke the plugin with `/shellferry:shellferry`. The standalone skill installed through npx uses `/shellferry`.

### Codex built-in installer

Ask Codex:

```text
$skill-installer install https://github.com/nanocm/shellferry/tree/main/skills/shellferry
```

Then invoke `$shellferry`.

### Local or offline installation

Download a [release archive](https://github.com/nanocm/shellferry/releases), extract it, and run:

```sh
python3 install.py                 # Codex
python3 install.py --host claude   # Claude Code
```

On Windows, use `python`. This method needs Python 3.10+ and the complete release archive. [More installation options](docs/installation.md#local-checkout-or-release-archive).

## Use

In Codex:

```text
Use $shellferry to turn this command into an offline installation bundle.
Target: Ubuntu 22.04, x86_64, ordinary user.
Collect the resources needed by every installation stage. Build only; skip the installation test.

curl -fsSL https://bun.sh/install | bash
```

For a fresh test, replace the last instruction with `Also verify the final archive with Podman and networking disabled.` In Claude Code, use `/shellferry` or `/shellferry:shellferry` as appropriate. Responses and installation instructions follow your language.

Shellferry preserves the upstream installer and records the patches that replace its downloads. It pins resource URLs and hashes, follows later installation stages, and includes the target's prerequisites in the delivery. Existing recipes reuse that analysis; unfamiliar installers are reviewed and adapted for the requested target.

## Build and optionally verify

Known recipes also work from the command line. These commands build a zoxide bundle without a container:

```sh
python3 skills/shellferry/scripts/catalog.py list
python3 skills/shellferry/scripts/catalog.py show zoxide
python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide
python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz
```

The archive and its `.sha256` file are ready to transfer. Without an installation test, report the result as **built, installation not tested** (`not-run`). Resource hashes and patch matches are checked during every build.

To test that archive on Ubuntu 22.04:

```sh
# Optional. Preparing the image may use the network; the test runs disconnected.
podman pull docker.io/library/ubuntu:22.04
python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \
  --engine podman --image docker.io/library/ubuntu:22.04 \
  --output dist/zoxide.validation.json
```

The test extracts the archive, installs as an ordinary user in a clean HOME, exercises a local function, and repeats installation. It checks paths with spaces and catches common download commands. A successful report records the archive hash and the environment used.

Windows can download and package with native Python. Run the optional Linux test through WSL with the corresponding Linux paths. Docker users can substitute `docker pull` and `--engine docker`.

## Install on the destination

Transfer the archive and checksum. For the zoxide example:

```sh
sha256sum -c zoxide.tar.gz.sha256
tar -xzf zoxide.tar.gz
sh zoxide/install.sh --check
sh zoxide/install.sh
export PATH="$HOME/.local/bin:$PATH"
eval "$(zoxide init bash)"
```

The destination needs the commands and libraries declared by the recipe. For example, `bun-ubuntu22` carries a private unzip tool and its library; `bun` expects unzip to be installed. An agent, Python, or a container engine is not required by the generated shell wrapper, though individual software may require Python or other runtimes.

## Verified software

The catalog covers runtimes such as Bun and Deno; shell tools such as zoxide, fzf, and Starship; package tools such as uv, Poetry, and pnpm; and development tools including .NET SDK, SDKMAN! with a JDK, code-server, and Pulumi.

All **105 software packages** have recorded Linux x86_64 offline installation tests. The 106 recipes include 101 shell-installer adaptations, three source installers, and two Python installers. Bun has two environment recipes and counts once. Each current recipe has matching evidence for its inputs and builder/verifier code.

The [validation matrix](skills/shellferry/references/validation-matrix.md) lists every version, environment, functional check, and report. Tests use Ubuntu 22.04 or 26.04. Runtime managers, cloud clients, and project dependencies have different scopes; the [scope and prerequisites](skills/shellferry/references/known-limitations.md) explain what each test covers.

You can look up prior evidence without downloads or containers:

```sh
python3 skills/shellferry/scripts/catalog.py evidence zoxide \
  --os-id ubuntu --os-version 22.04
```

Matching evidence lets you reuse the recorded conversion decisions. A newly built archive keeps its own test status. Recipes and reports travel with the repository; downloads use an optional local cache. See [how evidence is matched](skills/shellferry/references/shared-evidence.md).

## Development and license

The installable skill is in `skills/shellferry/`. Its scripts handle conversion, packaging, and verification; `assets/catalog/` holds recipes and installer snapshots. Repository checks run with:

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
python3 tools/package.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for new recipes and [installation verification](docs/installation.md#installation-verification) for testing agent installation channels.

Shellferry's own code and documentation use the [MIT license](LICENSE). Upstream scripts and fragments retain their licenses, documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The repository includes recipes and evidence; application binaries are downloaded when building a bundle. Check their upstream terms before redistributing a generated bundle.
