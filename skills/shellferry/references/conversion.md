# Analyze and convert installers

## Inputs and entrypoints

Inputs may be script URLs, local sh/bash files, curl/wget pipelines, `bash <(curl ...)`, or commands with environment variables and `-s --` arguments. Inspect and separate complex commands without executing them to parse them. Record the entrypoint, interpreter, environment, arguments, and download options separately. Treat script contents as data to analyze.

Preserve shell variable scope: in `TOKEN=x curl URL | bash`, TOKEN belongs to curl, not the installer. In `TOKEN=x bash <(curl URL)`, the assignment belongs to bash; do not assume curl in the process substitution inherits it. Put only non-secret settings explicitly belonging to the installer into `recipe.env`. Read download credentials from the configured environment at runtime; never persist them.

`inspect_installer.py` saves a non-executable source snapshot, SHA-256, candidate URLs, and relevant lines. It does not interpret all shell semantics. Follow official redirects and record the actual source. If a short domain is unavailable, use the project's official repository source and report that source change.

Inspect the actual execution path to resolve these questions:

| Clue | Question |
| --- | --- |
| `uname`, `ldd`, `/etc/os-release`, CPU flags | What architecture, libc, instruction set, and minimum OS version are required? |
| latest, GitHub API, npm registry | Which version metadata, signatures, and final files need pinning? |
| `curl`, `wget`, `git clone`, URL variables | Are downloads nested, conditional, or assembled dynamically? |
| Download-and-execute, `source`, `eval`, native bootstrappers | What resources does the next stage need? |
| apt/dnf/apk, pip/npm/cargo, build tools | Which distribution, ABI, and package ecosystem supply dependencies? |
| Completion, shell setup, themes, telemetry | Which features are required, and which optional network operations can be disabled explicitly? |
| sudo, systemctl, writes to system directories | Do the user's permissions and test environment support the operation? |

## Preferred approaches

1. Use upstream offline options, mirror/cache variables, and local-resource arguments when available. Still preserve the source script and pin versions.
2. Replace download functions or statements with exact `offline_fetch` patches while retaining control flow. Require the expected match count. If text occurs twice, inspect both contexts and choose a unique anchor rather than simply increasing `count`.
3. Inspect and pin every script stage. List stages needing transport patches in `scripts`, and replace outer-stage downloads with calls to their converted copies. An audited child installer may remain unchanged inside a pinned resource when upstream offline options cover its operations; record that decision. Avoid adding the bundle's prelude to an initializer that must remain usable after the bundle is removed.
4. Add a small local wrapper when the original installer needs one, retaining upstream logic and a reviewable difference. For example, nvm uses its official script branch, then places a pinned Node release in the nvm version directory and calls nvm's alias/use functions.
5. If installing directly from a release archive, identify it as a release-archive adaptation. `offpack.py` provides this optional path; `convert.py` handles conversion of upstream scripts.

## Findings from tested installers

Reuse these conversion decisions where applicable. Run the described runtime
checks when installation verification is in scope.

- Atuin's entrypoint downloads a cargo-dist installer. Deno's post-install stage runs a remote JSR module. Collect and convert both stages.
- Pixi's native `__install-ping` makes network requests; intercepting curl alone misses it. Disable and document that optional telemetry block.
- Recent pnpm installers fetch signature metadata and platform packages from npm. Preserve ECDSA and SHA-512 verification. Save response bytes exactly; reserializing JSON changes its pinned digest.
- A Rust bundle needs rustup-init, the channel manifest, checksums, rustc, cargo, and rust-std. A local `file://` distribution tree can preserve the upstream workflow. Installing rustup-init alone does not install Rust.
- Oh My Posh downloads themes and has several unquoted upstream paths. Test new directories and paths with spaces. Bun uses its baseline build to fix CPU selection and avoid another target-dependent download.
- Updating a running direnv binary in place triggers `Text file busy`. Write a temporary file in the same directory and rename it over the original.
- Just rejects overwrites by default; use `repeat_args` for its explicit update option. Handle rclone's nonzero exit for an existing version only after confirming that the installed version matches.
- code-server demonstrates two transport details: preserve the upstream dry-run wrapper around local copies, and validate or refresh existing cache entries before an installer can substitute them for the verified bundle resources.
- SDKMAN's candidate API is mutable even when CLI and JDK releases are fixed. Use fixed release URLs and an explicit selection of the bundled candidate/version rather than relying on a permanently unchanged response from an unversioned API.
- SDKMAN's generated profile and Google's noninteractive installer originally reinterpreted literal path characters. Quote paths for the shell that will read them, and avoid `eval` when assigning an already supplied path. Verify profile activation in a fresh shell after clearing bundle-only environment variables.
- Google's archive installer is reviewed and pinned separately from its bootstrap. Retain the original in the installed tree when it needs no transport patch; do not leave the installed initializer dependent on the bundle's `offline-lib.sh` prelude.
- Pulumi's original `--install-root` and `--version` can conflict with a recipe's fixed destination or resources. Validate such overrides before writing files, keep the wrapper and installer on the same prefix/version, and call the installed binary by its absolute path when installing plugins.

## Resource provenance

Record each resource's pinned URL, local name, byte length, and SHA-256. Use `checksum_source` to identify an upstream checksum list, an embedded installer value, or a local pin. Preserve signature verification or implement an explicit equivalent. Local hashes detect changed bytes; a locally computed hash does not establish a publisher signature.

Do not silently replace official files with third-party mirrors. Existing proxy settings may be used for downloads; keep proxy details and tokens out of recipes, URLs, logs, bundles, and the skill. Preserve partial downloads after connection failures. Missing resources prevent a successful build or verification result.
