# Preparing a release

Publish Shellferry from [nanocm/shellferry](https://github.com/nanocm/shellferry).
Keep `VERSION`, `plugin.json`, and `.claude-plugin/plugin.json` at the same
version. The commands below use `0.1.0`; substitute the version being prepared.

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

- Review third-party notices, source provenance, and redistribution terms.
- Test installation from the archive into an empty skills directory.
- Build a known recipe from an empty download cache, run its final archive in a
  network-disabled container, and retain the report. This release check exercises
  the complete workflow; end users may choose build-only operation.
- Review the documentation's scope and evidence claims against actual records.
- Ensure the checkout contains only this project's files.

## GitHub

When publication is authorized, push the reviewed source and wait for the
applicable GitHub checks on the release commit to pass.

Test the README's remote Skills CLI, Claude marketplace, and Codex installer
commands against the repository or release tag in isolated directories. Compare
the complete installed payload and query relocated evidence. Record the source
revision and actual remote-fetch results separately from local archive checks.

After required checks pass, tag the tested commit and attach the source/skill
archive, checksum, and reports. Preserve published tags and assets; later changes
belong in a new release. Describe marketplace availability according to where
the package has actually been published.

## Migration from the prototype

`offline-install` was the local prototype name. Shellferry carries forward its
conversion helpers and recipes, with repository installation, documentation,
packaging, and checks. The installer leaves existing prototype directories in
place. Keep one active skill name per agent to avoid duplicate discovery.
