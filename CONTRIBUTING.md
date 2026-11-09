# Contributing

Contribute an installer adaptation, a fix for a reproduced failure, clearer
instructions, or portable test evidence. Describe the software and environment
your change supports.

## Documentation language

Write `SKILL.md`, agent references, and contributor guides in English. Keep
`README.md` and `README.zh-CN.md` consistent in commands and feature claims.
Write the READMEs for people choosing and using the skill; write `SKILL.md` as
execution instructions, with explicit branches, inputs, and completion criteria.
The skill responds in the user's language. Preserve upstream sources, license
text, and recorded evidence in their original form.

## Development checks

Python 3.10+ and the standard library are sufficient:

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
```

The repository checker validates recipes, source pins, evidence bindings,
plugin metadata, relative Markdown links, and accidental local-machine paths.
Run checks relevant to the change. Documentation edits need these consistency
checks; changed installation behavior also needs a functional test.

## Add or update a recipe

Users can build bundles without running installation tests. An entry in the
published **verified catalog** requires a successful offline test and evidence
matching its current recipe, resources, builder, and verifier.

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
5. Build the final archive and test it without network access in a matching
   environment. Declare any dependencies supplied by the test image as target
   prerequisites, or include them in the bundle.
6. Record evidence and review it for personal paths, credentials, and private URLs:

```sh
python3 skills/shellferry/scripts/evidence.py record \
  --bundle work/example --report dist/example.validation.json
```

Add a concise functional summary and adaptation type to
`skills/shellferry/references/coverage-descriptions.json`, then run
`python3 tools/coverage.py` to regenerate the matrix and coverage inventory.
The check requires matching evidence for every catalog recipe and counts distinct
software names. Keep failed candidates outside the verified catalog and retain
their reproducible reports separately.

See the [recipe schema](skills/shellferry/references/recipe-schema.md) and
[conversion guidance](skills/shellferry/references/conversion.md).

## Evidence rules

Bind reports to the exact archive, manifest, checksum list, recipe, builder,
and verifier. A report records the publisher's run for that artifact and
environment. Historical evidence can guide a new build; only a fresh test can
establish the new archive's installation result. Keep build-only results at
`not-run` and leave missing historical timestamps or tool hashes unset.

If tooling changes invalidate evidence matching, run the affected test and
record new evidence. Preserve the original reports as historical records.

## What to include in a pull request

- The concrete installer or failure being addressed.
- The exact software version and target environment.
- Required resources and any behavior change.
- The commands run and observed validation results.
- Updated attribution for newly included upstream files.

Do not commit binary download caches, generated installation archives, credentials,
virtual environments, or container image layers. Use release assets for published
bundles only after their distribution terms and provenance are accounted for.
