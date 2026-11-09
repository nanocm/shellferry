# Verified scope and known limitations

The [validation matrix](validation-matrix.md) covers 105 software packages in
106 recipes: 101 shell installers, three source-tree installers, and two Python
installers. Bun has two environment recipes and counts once. Every current
recipe has matching evidence for its inputs and builder/verifier code.

These records describe Linux x86_64 tests on Ubuntu 22.04 or 26.04, with each
recipe's declared prerequisites. Use the notes below to select the scope needed
on the destination. Building a new bundle is independent of running a new test;
the [verification guide](verification.md) defines both delivery modes.

## Functional scope and prerequisites

- Runtime managers such as fnm, mise, pyenv, rbenv, GHCup, opam, Perlbrew, Elan,
  and Scala CLI have explicitly stated local manager checks. Their future
  interpreter/compiler downloads are separate dependencies. The nvm recipe
  includes Node; rustup includes its pinned Rust toolchain; Yarn includes Node.
- Cloud and cluster clients exercise local configuration, manifest generation,
  completion, or another stated operation. Offline clusters and authenticated
  cloud deployments require their own resources and tests.
- Grype's test covers local configuration. Trivy runs the offline secret scan
  described in its recipe. Vulnerability analysis requires a separately collected
  database.
- Poetry and PDM include pinned Python 3.10 Linux wheels and run their official
  Python installers through an authored shell entrypoint. The recipes require
  Python 3.10 with venv/ensurepip. Project dependencies remain a separate scope.
- Cargo tools that compile a local test project require the declared Cargo/Rust
  and C toolchain. Worktrunk's test covers shell integration generation;
  worktree operations require Git 2.43 or later.
- Loopback servers are permitted with external networking disabled. rqlite,
  SQL Studio, Samply, and Oranda exercise local servers. Porter's native mixin
  installer reads collected files through a temporary loopback server; its
  recipe declares Python as a prerequisite.
- SDKMAN! includes Temurin JDK 21.0.13+9 and tests Java compilation/execution,
  `sdk use/default/current`, profile activation and completion. Its offline
  installer selects only the bundled Java candidate; other SDKs and Maven/Gradle
  project dependencies require separate collection.
- .NET SDK 10.0.403 includes its runtime, compiler, reference packs and templates.
  Its test clears NuGet feeds and builds a dependency-free C# project. Additional
  packages/workloads are not included. Ubuntu 22.04 must provide the documented
  runtime libraries, including ICU; the Containerfile lists them explicitly.
- code-server includes Node and tests the local HTTP health endpoint and editor
  workbench. Extensions, browser interaction and remote tunnels are not covered.
- Pulumi includes the random provider and YAML runtime; its test creates, reads
  and destroys a local resource using a file backend. Other providers and cloud
  infrastructure need separate dependencies and verification.
- Google Cloud CLI includes its Python runtime, bq and gsutil. Tests cover
  initialization, shell completion, local configuration and installed-component
  listing. Account authentication, cloud APIs and additional components are
  outside this recipe. The fixed component snapshot supports installation;
  ordinary installed CLI commands do not require the bundle directory.

## Installer adaptations

| Installer | Observed problem | Adaptation |
| --- | --- | --- |
| dust | New prefix triggered sudo; repeat installation could hit `Text file busy` | Create the selected directory; install a temporary binary and rename it |
| chsrc | The EXIT trap removed the directory after successful installation | Clear its cleanup marker only after a successful install |
| git-standup, k3d, xmake | Upstream command construction lost quotes around paths with spaces | Preserve argument boundaries while retaining the upstream installation steps |
| k3sup, arkade | Official checksum sidecar names used `bin/`, but downloads were placed in the working directory | Compare the published checksum with the actual downloaded file at its local location |
| sheldon | A mutable GitHub API response made an exact metadata pin unsuitable for new users | Pin the selected release asset list and fixed resource URLs |
| xmake | Optional build statistics invoked a downloader during the functional test | Set upstream's supported `XMAKE_STATS=false` |
| code-server | Command reparsing lost path boundaries; the first transport patch bypassed dry-run; existing cache entries could substitute unverified bytes | Preserve argument vectors and dry-run; refresh cache from the verified bundle |
| SDKMAN! | Unversioned candidate metadata could change and invalidate otherwise fixed releases | Keep the selected Java candidate and exact version validation as explicit local selection data |
| SDKMAN!, Google Cloud CLI | Generated shell initialization or noninteractive path assignment could reinterpret literal path characters | Quote generated profile assignments and assign the supplied path directly |
| Google Cloud CLI | Copying a converted initializer into the installed tree left a dependency on the bundle | Verify and preserve the original archive initializer in place |
| Pulumi | Native destination/version overrides could diverge from the wrapper's fixed install plan | Reject inconsistent overrides before writes and invoke the installed CLI by absolute path |

Each fix is recorded as an exact recipe patch or small authored wrapper and
tested in the final archive. Upstream checksums and signatures are retained
where applicable, including OpenTofu and Yarn.

Additional code-server tests verify that `--dry-run` creates neither an install
prefix nor a cache, and that incorrect preexisting cache bytes are replaced.
The [supplemental report](evidence/supplemental/code-server/report.json) binds
the tested bundle and [test script](evidence/supplemental/code-server/edge-checks.sh).
SDKMAN's [literal-prefix tests](evidence/supplemental/sdkman-prefixes/manifest.json)
include fresh-shell Java compilation after loading the generated profile.
Google's [post-install checks](evidence/supplemental/google-cloud-cli/report.json)
cover literal path characters, overwrite refusal and independent use of the
installed initializer. Pulumi's [argument checks](evidence/supplemental/pulumi/report.json)
verify that conflicting options fail before writes or invocation of a preexisting
CLI. These reports remain separate from the standard archive verification records.

Pulumi's hosted installer and Google's hosted bootstrap stages are pinned by
their content hashes, without a stable source-commit URL or established license
for distributing their complete source. They are fetched during a build; if
those endpoints change, the build stops for review. The binary releases and
Google component snapshot use fixed versions.

## Failed candidate

Miniforge 26.9.4-2 rejects installation prefixes containing spaces. It failed
the required path test before installation and is excluded from the verified
catalog. The [report](evidence/failures/miniforge-26.9.4-2/report.json) and
[log](evidence/failures/miniforge-26.9.4-2/validation.log) retain that result.
Installation at a path accepted by the upstream installer has not been tested
here.

## Recreate test images

Image preparation may use the network. Final tests use `--pull=never --network
none`, user 1000:1000, and a clean HOME regardless of an image's default user.
Build only the baseline needed by the selected recipe:

```sh
podman build -t localhost/offline-install-test:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.ubuntu22 .
podman build -t localhost/shellferry-misc:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.misc-ubuntu22 .
podman build -t localhost/shellferry-misc-full:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.misc-full-ubuntu22 .
podman build -t localhost/shellferry-rust-test:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.rust-ubuntu22 .
podman build -t localhost/offline-install-test:ubuntu22-gpg \
  -f skills/shellferry/references/evidence/Containerfile.gpg-ubuntu22 .
podman build -t localhost/shellferry-dotnet-test:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.dotnet-ubuntu22 .
podman build -t localhost/shellferry-sdkman:ubuntu22 \
  -f skills/shellferry/references/evidence/Containerfile.sdkman-ubuntu22 .
```

The Containerfiles describe how to prepare each baseline. Package repositories
can change, so record the rebuilt image's identity and actual package versions
in its report. Published reports retain their original image identity. The
Ubuntu 26 baseline is described by [Containerfile.ubuntu26](evidence/Containerfile.ubuntu26).
