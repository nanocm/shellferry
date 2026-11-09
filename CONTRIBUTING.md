# Contributing

Useful contributions include new installer adaptations, fixes demonstrated by an
offline test, clearer installation instructions, and portable verification
evidence. Keep changes scoped to the actual software/environment being supported.

## Documentation language

Write the canonical `SKILL.md`, agent-facing references, and contributor guides
in English. Maintain `README.md` in English and `README.zh-CN.md` in Simplified
Chinese, keeping installation commands and feature claims consistent. The skill
responds in the user's language; English instructions do not require English
responses. Preserve upstream source, license text, and recorded evidence in their
original form.

## Development checks

Python 3.10+ and the standard library are sufficient:

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
```

The repository checker validates recipes, source pins, evidence file bindings,
plugin metadata, relative Markdown links, and accidental local-machine paths.
It does not replace a functional installation test.

## Add or update a recipe

1. Inspect the official entry script without executing it on the host. Record the
   version, script digest, target OS/CPU/libc, parameters, and installation scope.
2. Follow nested scripts and bootstrap programs. Identify installation-time
   dependencies and any optional network behavior.
3. Add a recipe below `skills/shellferry/assets/catalog/`. Use relative source
   paths, exact patches with expected counts, fixed resource URLs and SHA-256.
   Add required third-party notices when copying upstream material.
4. Define at least one real local functional check in addition to `--version`.
   Preserve upstream overwrite protection and require explicit update options
   where appropriate.
5. Build the final archive and test it without network access on the target
   environment. Record missing prerequisites honestly. Do not silently install
   extra dependencies into a test image to hide a packaging gap.
6. Record evidence and review it for personal paths, credentials, and private URLs:

```sh
python3 skills/shellferry/scripts/evidence.py record \
  --bundle work/example --report dist/example.validation.json
```

Add a concise functional summary and adaptation type to
`skills/shellferry/references/coverage-descriptions.json`, then run
`python3 tools/coverage.py` to regenerate the matrix and coverage inventory.
The check requires matching evidence for every catalog recipe and counts software
names rather than environment variants. Keep unsuccessful candidates outside the
passed catalog and document reproducible limitations separately.

See the [recipe schema](skills/shellferry/references/recipe-schema.md) and
[conversion guidance](skills/shellferry/references/conversion.md).

## Evidence rules

Keep reports tied to the exact archive, manifest, checksum list, recipe, builder,
and verifier. Preserve historical evidence as historical. Do not invent missing
timestamps or tool hashes. Evidence is a publisher's reproducible claim, not a
signature or proof about every platform.

If tooling changes invalidate strict evidence matching, refresh the affected
record with a new actual run. Unrelated historical results need not be rerun
merely to retain their historical documentation.

## What to include in a pull request

- The concrete installer or failure being addressed.
- The exact software version and target environment.
- Required resources and any behavior change.
- The commands run and observed validation results.
- Updated attribution for newly included upstream files.

Do not commit binary download caches, generated installation archives, credentials,
virtual environments, or container image layers. Use release assets for published
bundles only after their distribution terms and provenance are accounted for.
