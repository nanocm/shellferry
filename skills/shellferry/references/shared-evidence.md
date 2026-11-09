# Shared evidence and reuse

The repository distributes recipes, permitted source snapshots, exact patches,
resource URLs and hashes, prerequisites, test reports, and Containerfiles. These
let another user reuse the conversion analysis and reproduce its test. Downloads
come from the pinned sources or the user's own optional cache; the author's
local cache is never required.

## Match evidence

```sh
python scripts/catalog.py evidence bun-ubuntu22 --os-id ubuntu --os-version 22.04
```

Matching checks the software, version, target, distribution, recipe bytes,
original scripts, resource pins, and builder/verifier code hashes. Read the
returned prerequisites, image identity, and scope before reusing the decisions.
A record with mismatched inputs remains historical reference.

Obtain records from a trusted repository revision. They record a publisher's test
of a particular artifact and are not cryptographic signatures. The query status
`prior-evidence-only` refers to that earlier test.

## Apply evidence to a new build

- Reuse applicable analysis while checking downloaded hashes and patch matches
  during the new build.
- Deliver build-only work as `not-run`. Matching evidence can accompany that
  status without becoming a fresh verification result.
- Run the final archive in a disconnected environment when the user requests
  verification. Changed inputs or a different environment require a fresh test
  before claiming that combination is verified.
- Require current matching evidence for every recipe in the published verified
  catalog. Optional user testing does not change that publication rule.

## Add or update records

```sh
python scripts/evidence.py record --bundle ./bundle --report ./validation.json
```

The command checks bundled files against the report's bindings and accepts only
successful disconnected archive tests. It writes `references/evidence/records/`
and `index.json` without installation binaries. New reports include the test time
and recipe/builder/verifier hashes. The original 28 reports lack complete code
identities and retain `historical-unbound-code`; leave missing hashes and
timestamps unset.

An `image: localhost/...` value names an image on the original test host. Rebuild
it from the included Containerfile and record the new image identity and actual
package versions. Use an official distribution image directly when it supplies
the required baseline.

Before publication, remove credentials, personal paths, and private service
addresses while preserving environment details, provenance, and licensing notes.
Test first use from an independent directory and empty download cache. If
prebuilt bundles are published, attach the archive, SHA-256, recipe, builder
identity, and verification report to a release after checking redistribution
terms.
