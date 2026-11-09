---
name: shellferry
description: Convert curl/wget commands and sh/bash installers into portable offline installation bundles, including later download stages. Use for air-gapped deployment, remote machines with unreliable internet, and installer dependency collection. Pin resources, preserve upstream installation behavior, and optionally test the final archive in a network-disabled container.
---

# Shellferry

Produce an offline installation archive for the requested target, its SHA-256, and installation instructions. Preserve the upstream installer, exact patches, and resource provenance. Use the user's language for explanations; retain commands, paths, identifiers, and upstream output as written.

## Choose the target and recipe

1. Treat the supplied command as text. Download or read its scripts for inspection; do not execute an unfamiliar installer, `curl | sh`, `eval`, or command substitution on the preparation host.
2. Establish the target OS, CPU, distribution/version, libc, permissions, install directory, software version, and original arguments. Use conversation context or an authorized target machine. Ask for missing details that affect resource selection while continuing independent analysis. The preparation host does not define the target.
3. Run `scripts/catalog.py list` and inspect a matching recipe. The catalog covers 105 software packages, including variants such as `bun-ubuntu22` with bundled extraction tools. Query `catalog.py evidence <recipe> --os-id <id> --os-version <version>` and read the matching prerequisites. Reuse applicable decisions; the author's cache is never required.
4. For a known recipe, read that recipe and its evidence. If the user requests latest, check the release and entrypoint digest once; review changes before updating pins. For a new installer, read [conversion.md](references/conversion.md), then [recipe-schema.md](references/recipe-schema.md) when writing the recipe. Use [dependencies.md](references/dependencies.md) for system packages, runtimes, and project dependencies. Consult the [matrix](references/validation-matrix.md) and [scope notes](references/known-limitations.md) for tested behavior.

## Decide whether to run installation tests

- Default to building and packaging. A request to convert an installer does not require Docker or Podman.
- Run a fresh offline installation test when the user requests verification or it is part of the agreed task. Honor an explicit build-only or skip-verification request.
- If a requested test cannot run, deliver any completed bundle and state what prevented testing. Keep the result `not-run`; the requested verification remains incomplete. Do not substitute host installation or historical evidence for that test.
- Hash checks, source pins, exact patch counts, and declared prerequisites apply to every build. Optional verification refers to executing the installation and functional tests.
- Adding an entry to the published verified catalog requires a successful test and matching evidence. See [shared-evidence.md](references/shared-evidence.md).

## Convert the installer

- Pin source scripts, versions, metadata, target architecture, and every resource's SHA-256. Identify locally computed pins separately from publisher checksums or signatures. Preserve upstream verification or implement an explicit equivalent.
- Trace nested scripts, native bootstrappers, version APIs, templates, shell initialization, and optional telemetry. URL searches and downloader counts are inspection aids. Collect managed runtimes and project dependencies when requested; include a functional test for the required runtime.
- Replace network operations with exact patches and expected match counts. `offline_fetch URL [DEST]` accepts only mapped resources and rejects unknown URLs. A changed source hash or patch anchor requires review.
- Preserve arguments, install locations, overwrite protection, permissions, and initialization. Record necessary behavior changes. Disable optional network behavior through upstream options where possible; fix demonstrated defects with scoped patches.
- Use relative bundle paths and `{bundle}`, `{prefix}`, `{home}` placeholders. List required commands, libraries, and permissions. Dependencies in a prepared test image remain prerequisites unless the bundle supplies them.

## Build

Keep outputs in the task workspace and downloads outside the skill. Reuse an existing download cache when available; use `--cache-dir` for a task-local cache. The skill contains code, small source snapshots, recipes, and evidence.

For a catalog recipe:

```sh
python <skill>/scripts/catalog.py show zoxide
python <skill>/scripts/catalog.py build zoxide --output ./zoxide
python <skill>/scripts/convert.py archive ./zoxide --output ./zoxide.tar.gz
```

For a new adaptation:

```sh
python <skill>/scripts/inspect_installer.py --source https://example.com/install.sh --output ./analysis
# Analyze the snapshot and write recipe.json before building.
python <skill>/scripts/convert.py build ./recipe.json --output ./software-offline
python <skill>/scripts/convert.py archive ./software-offline --output ./software-offline.tar.gz
```

Python 3.10+ can download, patch, and package on the preparation host, including native Windows. Parallelize independent downloads; keep build and archive steps sequential. Missing resources, hash mismatches, and failed patches prevent a complete build.

## Verify when requested

Read [verification.md](references/verification.md). Pass the final archive to the verifier:

```sh
python <skill>/scripts/verify.py ./software-offline.tar.gz --engine podman --image <prepared-image> --output ./validation.json
```

The automated verifier supports Podman and Docker on Linux. Windows can use WSL with translated paths. Use a matching image, ordinary user, clean HOME, read-only bundle mount, and disabled external networking. Do not mount host credentials or a container socket. Test integrity and prerequisites, installation, a real local function, a path containing spaces, and repeat installation with upstream overwrite behavior preserved.

Retest after changes to the tested inputs or a relevant failure. Record the actual environment and scope. Container success establishes the tested operation without external connectivity; other architectures, systemd, kernel features, and absence of all attempted network calls need separate evidence.

## Deliver and retain evidence

Always deliver the archive, checksum, target, prerequisites, installation commands, and behavior changes. For build-only work, state **built; installation not tested** and retain `validation_status: not-run` in the manifest. Do not invent a successful report.

When tests run, include the actual report and logs. The external report binds the archive, manifest, checksum list, recipe, builder, and verifier; leave the tested bundle and its `not-run` manifest unchanged. Preserve failures as failures. Matching historical evidence supports reuse of conversion decisions and remains separate from the new artifact's test status.

After a successful test, a maintained adaptation may enter the catalog with its small recipe, permitted sources, findings, and evidence. Keep resource URLs portable, preserve licensing notices, and require new evidence for changed versions or targets.
