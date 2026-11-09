# Offline installation testing

## Select the mode

Installation testing is optional for user bundles. Build and package by default;
run a fresh test when requested or already agreed. Publishing an adaptation in
the verified catalog requires a passing test with matching evidence.

Every build checks source and resource hashes and exact patch matches. Every
delivery declares target prerequisites. The generated `install.sh --check`
checks integrity, platform constraints, and required commands without installing
the application. These checks remain available when installation testing is
skipped.

| Outcome | Delivery status |
| --- | --- |
| Build complete; installation test skipped | Built; installation not tested (`not-run`) |
| Requested test could not start | Bundle available; verification incomplete (`not-run`), with the cause stated |
| Test ran and failed | Verification failed; include the actual report and logs |
| Test passed | Verified for the recorded archive, environment, and functional scope |

The bundle manifest stays at `validation_status: not-run`, including after a
test. The external report records the actual result and binds the unchanged
archive. Prior catalog evidence remains separate from this result.

## Run the selected test

Create the final `.tar.gz` and its external `.sha256`, then pass the archive to
the verifier:

```sh
python scripts/verify.py ./software-offline.tar.gz \
  --engine podman --image <prepared-image> --output ./validation.json
```

Use Docker or Podman on Linux with an image matching the target distribution and
architecture. Image preparation may use the network; test execution uses
`--pull=never --network=none`. Record the image identity, distribution, commands,
and user. Tools supplied by a prepared image are target prerequisites unless the
bundle also supplies them.

`verify.py` checks archive members, extracts into a fresh directory, and mounts
the bundle read-only. The default test runs as UID 1000 with a clean HOME, a
prefix containing spaces, dropped capabilities, and no host credentials or
container socket. It copies the bundle into a temporary container directory,
then checks integrity and prerequisites, installs, runs functional assertions,
and repeats installation. Download-command guards catch calls even when the
installer ignores their failures. Reports and logs are saved outside the bundle.

On Windows, run this step through WSL. Resolve junctions and use actual Linux
paths in container mounts; confirm mappings with `wslpath` when needed.

## Match tests to installer behavior

- Use an ordinary user for home-directory installation. Root tests with dropped
  capabilities can fail when tar tries to restore another user's ownership.
  For requested system-wide installation, select the appropriate user and
  record the difference.
- Preserve default overwrite protection. Use `repeat_args` for an official
  overwrite or update option. Accept another nonzero result only after checking
  the resulting state against upstream semantics.
- Exercise a real local function. For a bundled runtime, execute that runtime;
  a manager's version output covers only the manager.
- Test relevant failure cases for changed mechanisms: incorrect digests,
  changed patch counts, unknown URLs, damaged bundles, wrong platforms, missing
  prerequisites, and existing installations. For overwrite protection, verify
  that rejection leaves the installed file unchanged.
- Use tracing when the task requires evidence about attempted native network
  calls. Network isolation establishes operation without external connectivity;
  the command guards cover `curl`, `wget`, `fetch`, and `aria2c`.

Retest after changes to the tested inputs or a relevant failure. Keep separate
reports for separate applications. Record scope requiring a VM or actual target,
such as systemd or kernel behavior, separately from container userspace tests.

## Deliver the result

Provide the archive, checksum, target, prerequisites, installation location and
commands, and necessary behavior changes. For a test run, also provide its report,
log, and observed scope. Reports bind the archive, manifest, SHA256SUMS, recipe,
builder, and verifier.

For build-only work, state that installation was not tested. The generated
`INSTALL.txt` mentions `validation.json`; that report exists only after a verifier
run completes. Do not create a passing report for skipped or failed tests. If a
requested test remains blocked, deliver the completed bundle and identify the
remaining verification work.
