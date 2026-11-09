# Shared evidence and reuse

The repository can carry small upstream snapshots, recipes, patches, resource URLs/digests, prerequisite descriptions, reports, documented fixes, and Containerfiles. These reduce repeated analysis. A first-time user must be able to build from official sources without the author's cache or large local bundles. If prebuilt bundles are published later, attach them to releases with their SHA-256, recipe, builder, and verification report. Local files are not public assets until published.

## Match evidence

```sh
python scripts/catalog.py evidence bun-ubuntu22 --os-id ubuntu --os-version 22.04
```

Matching checks the software/version/target, distribution, recipe's exact byte digest, original scripts, all resource pins, and builder/verifier code digests. Results list prerequisites, image digests, and scope. Check that the destination meets those prerequisites. Any mismatch makes the record historical reference rather than matching evidence.

Records state that a publisher tested a particular artifact; they are not cryptographic signatures. Obtain them from a trusted repository revision. `status: prior-evidence-only` always describes a previous test, not execution of a newly downloaded file or newly built bundle.

Run a fresh disconnected test when the user requests one. When reproducing a fixed adaptation with accepted historical evidence, reuse prior analysis while still checking downloaded hashes and current patch matches. A changed builder or environment cannot inherit an old successful report.

## Add or update records

```sh
python scripts/evidence.py record --bundle ./bundle --report ./validation.json
```

The command checks every bundled file against the report's bindings and accepts only successful disconnected archive tests. It writes `references/evidence/records/` and `index.json` without installation binaries. New reports record the verification time and recipe/builder/verifier digests. The original 28 reports lack complete code identities and remain `historical-unbound-code`; do not invent missing hashes or timestamps.

An `image: localhost/...` value is the test host's local tag, not a public image others can pull. Rebuild from the included Containerfile and record the new image digest and actual package versions. Use the official unmodified distribution image when sufficient, avoiding repeated package-manager queries.

Before publication, check for tokens, personal paths, and private service addresses while preserving necessary environment details, third-party provenance, and licensing notes. First-use tests should use an independent directory and empty download cache, with no hidden dependency on the original task's outputs.
