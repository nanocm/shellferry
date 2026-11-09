# Preparing a release

The project is **Shellferry**, repository
[nanocm/shellferry](https://github.com/nanocm/shellferry), skill name `shellferry`,
and invocation `$shellferry`.

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

Push reviewed source to the existing public repository when publication is
requested. Wait for the applicable GitHub checks on the release commit; only
successful hosted runs establish hosted CI results.

Test the README's remote Skills CLI, Claude marketplace, and Codex installer
commands against the repository or release tag in isolated directories. Compare
the complete installed payload and query relocated evidence. Local-path checks
do not test GitHub fetching.

Set `VERSION`, `plugin.json`, and `.claude-plugin/plugin.json` to the same release version. Create a tag only
after required checks pass, and attach the source/skill archive with its checksum.
Do not describe the package as listed in an official plugin directory merely
because it has a plugin manifest.

## Migration from the prototype

`offline-install` was the local prototype name. Shellferry keeps the validated
conversion helpers and portable recipes, but adds repository-level installation,
documentation, packaging, and checks. Existing prototype installations are left
alone. Users should choose one active skill name to avoid duplicate discovery.
