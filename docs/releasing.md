# Preparing a release

The proposed project identity is **Shellferry**, repository slug `shellferry`,
skill name `shellferry`, and invocation `$shellferry`. The name describes ferrying
installers and resources to disconnected machines. The initial GitHub name search
found no exact repository-name match; it is not a trademark clearance.

## Local release preparation

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
python3 tools/package.py
python3 tools/check_installation.py --archive dist/shellferry-0.1.0.zip --require-claude
```

The release archive contains the installer, installable skill, README files,
license notices, and plugin metadata. It excludes caches, compiled Python files,
Git history, and generated software bundles. The package command emits an
external SHA-256 file.

Before publishing:

- Review the project name and license choice.
- Check third-party notices and any explicitly documented unresolved provenance.
- Test installation from the archive into an empty skills directory.
- Verify a known recipe from an empty download cache; run its final archive in a
  network-disabled container and attach the report.
- Review the documentation's scope and evidence claims against actual records.
- Ensure the checkout contains only this project's files.

## GitHub

Create the repository only when publication is requested. Add its actual URL as
the Git remote, then push reviewed source. GitHub CI is included but is not
considered executed until a real hosted run succeeds.

After creating the public repository, test the README's remote Skills CLI,
Claude marketplace, and Codex installer commands against that repository. Remove
the first-release notices only when these commands work. Local-path checks do
not test GitHub fetching.

Set `VERSION`, `plugin.json`, and `.claude-plugin/plugin.json` to the same release version. Create a tag only
after required checks pass, and attach the source/skill archive with its checksum.
Do not describe the package as listed in an official plugin directory merely
because it has a plugin manifest.

## Migration from the prototype

`offline-install` was the local prototype name. Shellferry keeps the validated
conversion helpers and portable recipes, but adds repository-level installation,
documentation, packaging, and checks. Existing prototype installations are left
alone. Users should choose one active skill name to avoid duplicate discovery.
