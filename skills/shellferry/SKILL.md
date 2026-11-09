---
name: shellferry
description: Convert curl/wget installation commands and sh/bash installers, including later download stages, into portable offline installation bundles. Use for air-gapped deployment, remote machines with unreliable internet, and installer dependency collection. Inspect upstream scripts, pin resources, preserve installation behavior, and verify the bundle in a network-disabled container.
---

# Shellferry

Deliver a bundle that installs offline on the requested target, installation commands, and verifiable test results. Convert the actual upstream installer, preserving its original source, exact patches, and dependency provenance. Direct installation from release archives is also available; identify that choice when using it.

Use the user's language for explanations and generated installation guidance unless they request otherwise. Keep commands, paths, identifiers, and recorded upstream output unchanged.

## Identify the target and choose a path

- Start with the user's command, script, URL, or software name. Treat commands as text to inspect: download or read the script first. Do not execute `curl | sh`, `eval`, command substitutions, or unfamiliar installers on the preparation host.
- Identify the target OS, CPU, distribution/version, libc, permissions, installation directory, software version, and original arguments. Use existing conversation context or an authorized target machine when available. The preparation machine's Windows/WSL environment does not describe a remote target. Ask for missing information that affects binary selection while continuing entrypoint analysis.
- Run `scripts/catalog.py list` to find an existing adaptation. The catalog includes pinned recipes for 105 software packages and environment variants such as `bun-ubuntu22`, which bundles extraction tools. Check `catalog.py evidence <recipe> --os-id ubuntu --os-version 22.04` and read the matching record's prerequisites. Reuse reviewed conversion decisions when software, version, and environment match. Local caches are optional; a new user must be able to build without the author's cache. See [validation-matrix.md](references/validation-matrix.md) and [known-limitations.md](references/known-limitations.md).
- For an existing adaptation, read only that recipe and applicable evidence. If the user requests the latest release, check the version and entrypoint digest once, in parallel where independent; analyze changes before reusing the adaptation. Avoid rereading every reference or rediscovering pinned dependencies. For new adaptations, read [conversion.md](references/conversion.md); for recipe fields, [recipe-schema.md](references/recipe-schema.md); for package managers and dependencies, [dependencies.md](references/dependencies.md). Evidence rules are in [shared-evidence.md](references/shared-evidence.md).

## Conversion requirements

1. Pin the original scripts, software version, target architecture, metadata, and SHA-256 of every resource. Record checksum provenance. Distinguish locally computed pins from verified upstream checksums or signatures. Preserve upstream verification or explicitly implement an equivalent check.
2. Follow nested scripts, native bootstrappers, version APIs, configuration templates, themes, post-install initialization, and optional telemetry. Counts of `curl`/`wget` calls and URL regexes are clues, not complete dependency analysis. Track manager binaries, managed runtimes, Rust toolchains, and project caches separately. When the user needs a working runtime, collect and execute that runtime.
3. Replace network steps with exact patches and expected match counts. `convert.py` supplies `offline_fetch URL [DEST]`, which maps only known URLs to bundled files and fails on unknown URLs. If upstream text or patch anchors change, review the difference before updating the adaptation.
4. Preserve arguments, install locations, overwrite protection, verification, permissions, and shell initialization semantics. Record necessary behavior changes. Retain initialization, dependencies, and features the user needs. Optional network behavior may be disabled with an explanation; demonstrated defects such as incorrect path quoting may receive minimal fixes.
5. Use relative resource paths and `{bundle}`, `{prefix}`, `{home}` placeholders. Do not reference the preparation host's cache, temporary directories, or workspace. List extra commands, libraries, and permission requirements. A dependency present in a test image may still be missing on the destination.

## Build and verify

Write task outputs to the workspace. Keep code, small examples, and reference material in the skill; put download caches, container images, and large installation bundles elsewhere.

```sh
# Snapshot the entrypoint and collect analysis clues without executing it.
python <skill>/scripts/inspect_installer.py --source https://example.com/install.sh --output ./analysis

# Inspect an existing adaptation's version, platform, prerequisites, and scope.
python <skill>/scripts/catalog.py show bun
python <skill>/scripts/catalog.py build bun --output ./bun-offline

# Build a reviewed recipe for a new installer or version.
python <skill>/scripts/convert.py build ./recipe.json --output ./software-offline

# Export the final archive first, then test that artifact once.
python <skill>/scripts/convert.py archive ./software-offline --output ./software-offline.tar.gz
python <skill>/scripts/verify.py ./software-offline.tar.gz --engine podman --image <prepared-image> --output ./validation.json
```

Native Windows Python can download and package resources. Run Linux container verification through WSL with Podman/Docker, translating paths to their actual Linux locations. Running `verify.py` in Linux is the most direct route.

Parallelize independent downloads and environment checks; keep build, archive, and verification in dependency order. Include functional, completion, and default-directory requirements in the first adaptation and test. Repeat checks when failures, changed artifacts, or new conditions justify them. If the user explicitly requests a fresh Podman test, run it; historical evidence does not count as a new execution.

## Completion criteria

Follow [verification.md](references/verification.md). Prefer an ordinary user, clean HOME, read-only bundle mount, and `--network none`. Do not mount the host HOME, credentials, or container socket. Environment preparation may use the network; installation and functional tests must run disconnected.

- Pass integrity, platform, and prerequisite checks. Integrity failures must exit before installation writes.
- Install from a clean environment, check the version, and exercise at least one real local function. Repeat installation successfully or use the upstream installer's explicit update option while preserving default overwrite protection.
- Test a path containing spaces. Every installation stage must read resources from the bundle. Detect common download-command attempts even when the upstream script ignores their failures.
- Native binaries may still attempt network calls. A disconnected test proves the tested operation completes without external connectivity; it does not establish zero network syscalls.
- State the actual tested environment. Container results do not establish compatibility with other CPUs, older glibc, macOS, full systemd services, or kernel modules. Continue useful builds and checks when the available environment covers only part of the target.

Deliver the archive, SHA-256, report, target and prerequisites, installation commands, and necessary behavior changes. Reports must bind the artifact's manifest and checksum-list digests so old results cannot be assigned to changed bundles. Retain failed results and concrete missing prerequisites; do not list them as passed.

## Maintain adaptations

After an adaptation passes, add its small recipe, permitted upstream snapshots, and findings to the catalog, retaining the pinned version and tested scope. Remove machine-specific `source` paths and pin resource URLs and SHA-256 values. Store authored wrappers under the recipe's `sources/` directory. Revalidate version upgrades. Add rules in response to reproduced problems and keep software-specific constraints scoped to that software.
