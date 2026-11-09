# Disconnected verification and evidence

## Reproducible environments

Prefer Podman or Docker with an image matching the target distribution and architecture. Image preparation may use the network; the actual test must use `--pull=never --network=none`. Record the image ID/digest, distribution, installed commands, and user. The original catalog campaign used Ubuntu 26.04.1 x86_64 with extra tools listed in the validation matrix. Libraries present only in the test image must not conceal missing target dependencies.

`verify.py` uses ordinary UID 1000, a fresh HOME, a prefix containing spaces, a read-only bundle mount, and no extra capabilities or host home/credentials. It checks integrity, prerequisites, first installation, functional smoke tests, repeat installation, and download-command guards. It copies the bundle into a temporary container directory for testing, discards temporary artifacts afterward, and saves the report outside the bundle.

Use actual mapped paths when crossing Windows and WSL. A working directory may be a junction; resolve it or use `wslpath` to confirm the location. Do not pass Windows paths directly to Linux container volume arguments.

## Adapt tests to installer behavior

- Root with `cap-drop=all` can fail when tar restores another UID's ownership. An ordinary user better represents home-directory installation.
- Explicit root tests may be appropriate for requested system-wide installation. Record that difference and leave host permissions unchanged.
- Preserve upstream overwrite protection. Use `repeat_args` for the official overwrite/update option. Handle other nonzero exits only after checking the corresponding state against upstream semantics.
- Smoke tests need real functional assertions. A manager's version output does not establish that its managed runtime is installed.
- Guards detect ignored curl failures. Analyze native network behavior separately or use syscall tracing when needed. `network=none` establishes that the tested operation completes without external connectivity.

## Failure cases

For new mechanisms or adaptations, test the relevant failure cases: incorrect script/resource digests, changed patch counts, unknown URLs, damaged bundles, wrong platforms, missing commands, or existing installations. The 20-software campaign also checked that Just rejects a default overwrite and leaves the installed binary's digest unchanged.

A successful report must bind the manifest and SHA256SUMS digests. Checking that an archive exists is insufficient. Rerun the affected test after changing scripts or resources, whether before or after packaging.

## Deliverables

Generate a `.tar.gz` and an external `.sha256`, then pass the archive to `verify.py`. It checks archive members, extracts into a fresh directory, tests installation, and binds `archive_sha256` in the report. Test the final archive rather than only the build directory. For multiple applications, retain separate reports before summarizing results.

Provide the target platform, baseline dependencies, installation directory and commands, necessary behavior changes, and actual tested scope. Deliver completed bundles with an accurate account of any untested architectures or systems; untested environments do not count as passed.
