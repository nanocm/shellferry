# Validation matrix

**105 distinct software packages, 106 recipes.** Each recipe has matching evidence for its current inputs and builder/verifier code. Results describe the exact pinned version, prerequisites, and functional scope below.

Tests run through Podman in WSL2 with `--network none`, user `1000:1000`, a clean HOME, a prefix containing spaces, read-only bundle mounts, and dropped capabilities. The verifier extracts each final archive into a fresh directory, checks integrity, installs, runs functional assertions, and repeats installation. Passing establishes completion without external connectivity. Detecting all attempted native network calls requires separate tracing.

Most new cases use Ubuntu 22.04. Some baseline cases use Ubuntu 26.04. Prepared images include the tools listed in their Containerfiles; target machines must meet each recipe's prerequisites. Python, Rust, or C build tools are present only where declared. Managers, cloud clients, and cluster tools are tested within the local scope stated below.

Installation testing is optional when building a user bundle. These published catalog entries require passing evidence; a new build retains its own status. See [verification modes](verification.md) and [evidence reuse](shared-evidence.md).

| Recipe | Version | Path | Environment | Functional check | Evidence |
| --- | --- | --- | --- | --- | --- |
| [actionlint](../assets/catalog/actionlint/recipe.json) | 1.7.12 | shell-installer | ubuntu 22.04 | Lint a local GitHub Actions workflow without external shellcheck or pyflakes | [passed](evidence/records/3ec33ff12096bcf0aebecd8b/report.json) |
| [air](../assets/catalog/air/recipe.json) | 1.67.4 | shell-installer | ubuntu 22.04 | Generate and inspect an Air project configuration | [passed](evidence/records/f3d07521b5561a50a749fc7a/report.json) |
| [arkade](../assets/catalog/arkade/recipe.json) | 0.12.0 | shell-installer | ubuntu 22.04 | Generate Bash completions (no additional application downloads) | [passed](evidence/records/945d61c598ac1983262fa60b/report.json) |
| [atuin](../assets/catalog/atuin/recipe.json) | 18.24.5 | shell-installer | ubuntu 26.04 | Complete both installer stages and generate Bash initialization. | [passed](evidence/records/207cdff2bd14303fa3f492b3/report.json) |
| [babashka](../assets/catalog/babashka/recipe.json) | 1.13.229 | shell-installer | ubuntu 22.04 | Evaluates a Clojure reduction and asserts the result is 10. | [passed](evidence/records/74692413103a50c821a397c8/report.json) |
| [bash-it](../assets/catalog/bash-it/recipe.json) | 3.2.0 | source-installer | ubuntu 22.04 | Loads Bash-it, enables general aliases and lists enabled configuration. | [passed](evidence/records/5180ef0a81b82deaa8e89d1e/report.json) |
| [basher](../assets/catalog/basher/recipe.json) | commit-7c3d238ce263 | shell-installer | ubuntu 22.04 | Links and executes a local package without fetching dependencies. | [passed](evidence/records/4afd372d927ae9c4a73f4a3d/report.json) |
| [bats](../assets/catalog/bats/recipe.json) | 1.14.0 | source-installer | ubuntu 22.04 | Executes a local Bats test and asserts a passing test result. | [passed](evidence/records/1213a1045cc503631599d062/report.json) |
| [bpkg](../assets/catalog/bpkg/recipe.json) | 1.1.4 | shell-installer | ubuntu 22.04 | Parses a local JSON object with its installed JSON command. | [passed](evidence/records/c66762588ecd9ddebe358f03/report.json) |
| [bun](../assets/catalog/bun/recipe.json) | 1.4.4 | shell-installer | ubuntu 26.04 | Evaluate a local JavaScript expression. | [passed](evidence/records/16550574ff23fa9427a0d991/report.json) |
| [bun-ubuntu22](../assets/catalog/bun-ubuntu22/recipe.json) | 1.4.4 | shell-installer | ubuntu 22.04 | Run JavaScript, check default-prefix installation and generate completions with bundled unzip. | [passed](evidence/records/309de85cf1b8688e4dff94ee/report.json) |
| [cargo-auditable](../assets/catalog/cargo-auditable/recipe.json) | 0.7.7 | shell-installer | ubuntu 22.04 | Compile and run a local Rust program; assert .dep-v0 metadata | [passed](evidence/records/f83897a7e0fc8d8614b03df6/report.json) |
| [cargo-binstall](../assets/catalog/cargo-binstall/recipe.json) | 1.26.2 | shell-installer | ubuntu 22.04 | Self-install a copied executable and compare bytes | [passed](evidence/records/44e7811397990c237689ffd9/report.json) |
| [cargo-dist](../assets/catalog/cargo-dist/recipe.json) | 0.34.0 | shell-installer | ubuntu 22.04 | Initialize a local Cargo project and generate a release plan | [passed](evidence/records/b0fe131f79063dfd242b38c6/report.json) |
| [cargo-insta](../assets/catalog/cargo-insta/recipe.json) | 1.49.0 | shell-installer | ubuntu 22.04 | Render a local snapshot using Cargo metadata | [passed](evidence/records/40f82d5ccb927a522aa6db81/report.json) |
| [cargo-leptos](../assets/catalog/cargo-leptos/recipe.json) | 0.3.11 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate syntax | [passed](evidence/records/db8bc56704adb3fafd688cb4/report.json) |
| [cargo-mommy](../assets/catalog/cargo-mommy/recipe.json) | 0.3.1 | shell-installer | ubuntu 22.04 | Build and run a local Rust program through the Cargo wrapper | [passed](evidence/records/0fca33eb10ca209487444955/report.json) |
| [chezmoi](../assets/catalog/chezmoi/recipe.json) | 2.74.0 | shell-installer | ubuntu 26.04 | Render a template reading the target OS. | [passed](evidence/records/105007f6c94693372d57aa96/report.json) |
| [chsrc](../assets/catalog/chsrc/recipe.json) | 0.2.7 | shell-installer | ubuntu 22.04 | List built-in package-source targets without modifying sources | [passed](evidence/records/4b32c2e6814c18e0eab5b524/report.json) |
| [clj-kondo](../assets/catalog/clj-kondo/recipe.json) | 2026.10.26 | shell-installer | ubuntu 22.04 | Lints a local Clojure namespace and asserts zero errors. | [passed](evidence/records/f8b55859c231c3b5f8ef5ed0/report.json) |
| [clojure-lsp](../assets/catalog/clojure-lsp/recipe.json) | 2026.10.15-11.42.38 | shell-installer | ubuntu 22.04 | Formats a local Clojure source file with external classpath discovery disabled. | [passed](evidence/records/bdf456c49189a156d1ebbb27/report.json) |
| [code-server](../assets/catalog/code-server/recipe.json) | 4.145.2 | shell-installer | ubuntu 22.04 | Start the editor on loopback and verify its HTTP health endpoint and workbench using bundled Node. | [passed](evidence/records/bf9b8b370e7bc07f9d0db9e7/report.json) |
| [dagger](../assets/catalog/dagger/recipe.json) | 0.21.11 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate its syntax; engine execution requires separate images. | [passed](evidence/records/43514990ef2c31aa4d183079/report.json) |
| [deno](../assets/catalog/deno/recipe.json) | 2.9.8 | shell-installer | ubuntu 26.04 | Run the local JSR second stage and execute JavaScript. | [passed](evidence/records/57baf4989916038629f16f1a/report.json) |
| [direnv](../assets/catalog/direnv/recipe.json) | 2.38.2 | shell-installer | ubuntu 26.04 | Authorize .envrc and load a local variable. | [passed](evidence/records/5c664f2a746f4b812ac606cf/report.json) |
| [dolt](../assets/catalog/dolt/recipe.json) | 2.7.2 | shell-installer | ubuntu 22.04 | Initialize a local repository, create a table, and execute SQL. | [passed](evidence/records/4fe2f2bea958f73008805cf4/report.json) |
| [dotnet](../assets/catalog/dotnet/recipe.json) | 10.0.403 | shell-installer | ubuntu 22.04 | Create, restore without NuGet feeds, compile and run a C# console app; assert LINQ, JSON and ICU culture data | [passed](evidence/records/fcc9a067527e1918deff13c9/report.json) |
| [dprint](../assets/catalog/dprint/recipe.json) | 0.64.3 | shell-installer | ubuntu 22.04 | Formats JSON using a bundled pinned WebAssembly plugin. | [passed](evidence/records/2b2f0dcd75f61b04bba0fd4c/report.json) |
| [dust](../assets/catalog/dust/recipe.json) | 1.2.7 | shell-installer | ubuntu 22.04 | Measure a local directory and report its file | [passed](evidence/records/d4b2a4d7724a79a9f5475593/report.json) |
| [elan](../assets/catalog/elan/recipe.json) | 4.2.4 | shell-installer | ubuntu 22.04 | Generates Bash completions; Lean toolchains excluded. | [passed](evidence/records/e352c981090d0efc3ec378aa/report.json) |
| [flux](../assets/catalog/flux/recipe.json) | 2.10.0 | shell-installer | ubuntu 22.04 | Export a GitRepository manifest locally (no cluster access) | [passed](evidence/records/9df49a7af50c6b4936ee3212/report.json) |
| [flyctl](../assets/catalog/flyctl/recipe.json) | 0.5.5 | shell-installer | ubuntu 22.04 | Generate Bash completions (no Fly.io authentication or deployment) | [passed](evidence/records/496fd3dbf5f46232393d41c7/report.json) |
| [fnm](../assets/catalog/fnm/recipe.json) | 1.39.0 | shell-installer | ubuntu 26.04 | Generate the manager shell environment; managed Node runtimes are outside scope. | [passed](evidence/records/386fb34733774cd33dc657e7/report.json) |
| [fzf](../assets/catalog/fzf/recipe.json) | 0.75.0 | shell-installer | ubuntu 22.04 | Filter local input and validate generated Bash initialization. | [passed](evidence/records/8680a1c3024ade0859d69631/report.json) |
| [garden](../assets/catalog/garden/recipe.json) | 0.14.20 | shell-installer | ubuntu 22.04 | Create a local Garden project and inspect its configuration | [passed](evidence/records/633ad8ce4b029cba4149111e/report.json) |
| [ghcup](../assets/catalog/ghcup/recipe.json) | 0.2.6.2 | shell-installer | ubuntu 22.04 | Lists GHC releases from pinned local metadata; Haskell toolchains excluded. | [passed](evidence/records/dd80310370a51a2ca18359b3/report.json) |
| [git-standup](../assets/catalog/git-standup/recipe.json) | 2.3.2 | source-installer | ubuntu 22.04 | Report a commit from a local Git repository | [passed](evidence/records/8f39de6c72100478bc271cb8/report.json) |
| [golangci-lint](../assets/catalog/golangci-lint/recipe.json) | 2.15.0 | shell-installer | ubuntu 22.04 | Format Go source supplied on standard input | [passed](evidence/records/e0cbaa64b0b6e53713178745/report.json) |
| [google-cloud-cli](../assets/catalog/google-cloud-cli/recipe.json) | 592.0.0 | shell-installer | ubuntu 22.04 | Run the official archive installer with bundled Python; verify profile/completion, local configuration and component listing | [passed](evidence/records/70f710a543e846dfc4daebe7/report.json) |
| [goose](../assets/catalog/goose/recipe.json) | 3.29.0 | shell-installer | ubuntu 22.04 | Apply a SQLite schema migration and inspect its applied status | [passed](evidence/records/66f1564175c3d4fa73f9e57c/report.json) |
| [goreleaser](../assets/catalog/goreleaser/recipe.json) | 2.20.0 | shell-installer | ubuntu 22.04 | Generate and inspect a GoReleaser project configuration | [passed](evidence/records/91f1f21f7b931dc6bfbf1756/report.json) |
| [grype](../assets/catalog/grype/recipe.json) | 0.121.2 | shell-installer | ubuntu 22.04 | Render effective configuration (vulnerability database and scanning excluded) | [passed](evidence/records/ff8c0d9cb404583416db0358/report.json) |
| [helm](../assets/catalog/helm/recipe.json) | 3.22.1 | shell-installer | ubuntu 26.04 | Verify the release, inspect the version and Helm environment. | [passed](evidence/records/8265b0a99b16b76b36be4410/report.json) |
| [infracost](../assets/catalog/infracost/recipe.json) | 0.10.47 | shell-installer | ubuntu 22.04 | Set and read local currency configuration (pricing API excluded) | [passed](evidence/records/3cb6141ed12964fce49e2cd0/report.json) |
| [istioctl](../assets/catalog/istioctl/recipe.json) | 1.31.4 | shell-installer | ubuntu 22.04 | Render the default Istio manifest locally (no cluster installation) | [passed](evidence/records/76cbd2898f975744acbad487/report.json) |
| [jet](../assets/catalog/jet/recipe.json) | 0.7.27 | shell-installer | ubuntu 22.04 | Converts local JSON to keywordized EDN and checks the value. | [passed](evidence/records/e29b2f55c53d2bb20c945846/report.json) |
| [jfrog-cli](../assets/catalog/jfrog-cli/recipe.json) | 2.131.0 | shell-installer | ubuntu 22.04 | Collect local build environment metadata (no Artifactory server) | [passed](evidence/records/25e1b3f66c3e6d8bd9ad1d2e/report.json) |
| [just](../assets/catalog/just/recipe.json) | 1.59.0 | shell-installer | ubuntu 26.04 | Execute a local justfile task and preserve default overwrite protection. | [passed](evidence/records/ea9f1e349ec955d193c67fb7/report.json) |
| [k0s](../assets/catalog/k0s/recipe.json) | 1.37.2+k0s.1 | shell-installer | ubuntu 22.04 | Generate a local cluster configuration (no cluster startup) | [passed](evidence/records/9ae96db7f34daa96b6f68593/report.json) |
| [k3d](../assets/catalog/k3d/recipe.json) | 5.9.0 | shell-installer | ubuntu 22.04 | Generate and inspect a local k3d cluster configuration (no Docker cluster) | [passed](evidence/records/b82ec7005060f33465637593/report.json) |
| [k3sup](../assets/catalog/k3sup/recipe.json) | 0.13.14 | shell-installer | ubuntu 22.04 | Generate Bash completions (no remote Kubernetes deployment) | [passed](evidence/records/cf8a2e6b932ff05e926ae3a2/report.json) |
| [kubescape](../assets/catalog/kubescape/recipe.json) | 4.0.20 | shell-installer | ubuntu 22.04 | Generate Bash completions (cluster scans and control downloads excluded) | [passed](evidence/records/f243769d153066aea991806d/report.json) |
| [kustomize](../assets/catalog/kustomize/recipe.json) | 5.8.3 | shell-installer | ubuntu 22.04 | Build a local ConfigMap manifest with a name prefix | [passed](evidence/records/7c75bbd8b09a21ee15455c8e/report.json) |
| [linkerd](../assets/catalog/linkerd/recipe.json) | edge-26.11.1 | shell-installer | ubuntu 22.04 | Add Linkerd injection annotations to a local manifest without cluster access | [passed](evidence/records/157ce9944cc475474827ed08/report.json) |
| [mcfly](../assets/catalog/mcfly/recipe.json) | 0.9.4 | shell-installer | ubuntu 22.04 | Generate Bash initialization and validate syntax | [passed](evidence/records/40993c23b449eeb0d4b7e82d/report.json) |
| [micromamba](../assets/catalog/micromamba/recipe.json) | 2.10.0 | shell-installer | ubuntu 22.04 | Creates an empty offline environment and runs a local command within it. | [passed](evidence/records/3f99711b88658e56f6495bfc/report.json) |
| [minijinja-cli](../assets/catalog/minijinja-cli/recipe.json) | 3.1.0 | shell-installer | ubuntu 22.04 | Render a template with local JSON data | [passed](evidence/records/d34418dd905fabe85189916b/report.json) |
| [mise](../assets/catalog/mise/recipe.json) | 2026.11.5 | shell-installer | ubuntu 26.04 | Run a local command through the manager; managed runtimes are outside scope. | [passed](evidence/records/b7bf56192251e41d5000bbb9/report.json) |
| [near-cli](../assets/catalog/near-cli/recipe.json) | 0.31.1 | shell-installer | ubuntu 22.04 | Create and read local connection configuration in offline mode | [passed](evidence/records/b83de031031891431205d40e/report.json) |
| [nvm](../assets/catalog/nvm/recipe.json) | 0.40.3-node26.13.0 | shell-installer | ubuntu 26.04 | Install Node 26, execute JavaScript and npm with the bundled Ubuntu library. | [passed](evidence/records/2ba74cea6b6f35bd94c2d6ae/report.json) |
| [oh-my-posh](../assets/catalog/oh-my-posh/recipe.json) | 32.0.0 | shell-installer | ubuntu 26.04 | Load a bundled theme and generate shell initialization. | [passed](evidence/records/e78c4f00c9af367c07459d78/report.json) |
| [oh-my-zsh](../assets/catalog/oh-my-zsh/recipe.json) | commit-cca3bdfbef8c | shell-installer | ubuntu 22.04 | Loads the Git plugin and checks the gst alias. | [passed](evidence/records/eb1c64eebf99bd728310ec4a/report.json) |
| [opam](../assets/catalog/opam/recipe.json) | 2.6.1 | shell-installer | ubuntu 22.04 | Lints a complete local .opam package definition without a repository or compiler. | [passed](evidence/records/ea1d1614efbe17b3ce76c516/report.json) |
| [opentofu](../assets/catalog/opentofu/recipe.json) | 1.13.9 | shell-installer | ubuntu 22.04 | Format and validate local HCL without external providers; retain GPG verification | [passed](evidence/records/2a53cdabcde72d5f282d6e2b/report.json) |
| [oranda](../assets/catalog/oranda/recipe.json) | 0.6.5 | shell-installer | ubuntu 22.04 | Serve and retrieve a local HTML page over loopback | [passed](evidence/records/f3531535280a22736f975371/report.json) |
| [pdm](../assets/catalog/pdm/recipe.json) | 2.29.7 | python-installer | ubuntu 22.04 | Sets and reads local manager configuration and generates completions; offline CPython 3.10 wheelhouse. | [passed](evidence/records/9b03e7f3b892e7f7b6e86ac8/report.json) |
| [perlbrew](../assets/catalog/perlbrew/recipe.json) | 1.02 | shell-installer | ubuntu 22.04 | Initializes shell integration, prints environment and runs bundled patchperl. | [passed](evidence/records/00fb148245ab16000fa6332e/report.json) |
| [pixi](../assets/catalog/pixi/recipe.json) | 0.84.1 | shell-installer | ubuntu 26.04 | Initialize a local project; Conda environments are outside scope. | [passed](evidence/records/694fb74a85770e888599896c/report.json) |
| [pnpm](../assets/catalog/pnpm/recipe.json) | 12.18.0 | shell-installer | ubuntu 22.04 | Verify upstream signatures and execute local package scripts. | [passed](evidence/records/3d870c35dc1734c01cf358ef/report.json) |
| [poetry](../assets/catalog/poetry/recipe.json) | 2.5.1 | python-installer | ubuntu 22.04 | Creates a local project and validates its pyproject.toml; offline CPython 3.10 wheelhouse. | [passed](evidence/records/b8890f3ebff7d5ea35df6132/report.json) |
| [porter](../assets/catalog/porter/recipe.json) | 1.6.1 | shell-installer | ubuntu 22.04 | Install the exec mixin from a temporary loopback mirror and create a local project | [passed](evidence/records/cb1ba62204e01b3ff56c23ac/report.json) |
| [posit-air](../assets/catalog/posit-air/recipe.json) | 0.13.0 | shell-installer | ubuntu 22.04 | Format a local R source file | [passed](evidence/records/065cee3d59bde258de863f54/report.json) |
| [prek](../assets/catalog/prek/recipe.json) | 0.5.10 | shell-installer | ubuntu 22.04 | Validate a local pre-commit configuration | [passed](evidence/records/2ec68362ea9bd594ebb9112f/report.json) |
| [pulumi](../assets/catalog/pulumi/recipe.json) | 3.274.1 | shell-installer | ubuntu 22.04 | Install the random provider and run a local YAML resource lifecycle with a file backend; verify completion | [passed](evidence/records/38a142101d38e2ebc9e6f1e4/report.json) |
| [pyenv](../assets/catalog/pyenv/recipe.json) | 2.8.14 | shell-installer | ubuntu 22.04 | Sets and reads a local system-Python selection, then regenerates shims. | [passed](evidence/records/8e45455bea8b07ab1e937109/report.json) |
| [railway](../assets/catalog/railway/recipe.json) | 5.71.0 | shell-installer | ubuntu 22.04 | Generate Bash completions (cloud deployment excluded) | [passed](evidence/records/cc76443173e88bb716934bcd/report.json) |
| [rbenv](../assets/catalog/rbenv/recipe.json) | 1.3.2 | shell-installer | ubuntu 22.04 | Generates shell initialization and rebuilds the shim directory; Ruby excluded. | [passed](evidence/records/7d99402b2fd623327e0a3fb0/report.json) |
| [rclone](../assets/catalog/rclone/recipe.json) | 1.76.0 | shell-installer | ubuntu 26.04 | Copy and compare local files. | [passed](evidence/records/0e5aa1f5acbdb072a788b59f/report.json) |
| [rqlite](../assets/catalog/rqlite/recipe.json) | 10.6.6 | shell-installer | ubuntu 22.04 | Start a local node and query SQLite over container loopback. | [passed](evidence/records/daad20bc5eafb89058a6db4a/report.json) |
| [ruff](../assets/catalog/ruff/recipe.json) | 0.17.4 | shell-installer | ubuntu 26.04 | Lint a local Python file. | [passed](evidence/records/e2d2555ca173978f3e482047/report.json) |
| [rustup](../assets/catalog/rustup/recipe.json) | 1.29.3-rust1.90.0 | shell-installer | ubuntu 26.04 | Install the Rust 1.90 toolchain and compile metadata. | [passed](evidence/records/5af06fd50fbf486ab314683e/report.json) |
| [samply](../assets/catalog/samply/recipe.json) | 0.13.1 | shell-installer | ubuntu 22.04 | Load a synthetic profile and retrieve its JSON over loopback | [passed](evidence/records/e2cdc9aa5609f5ad6a50373c/report.json) |
| [scala-cli](../assets/catalog/scala-cli/recipe.json) | 1.18.0 | shell-installer | ubuntu 22.04 | Discovers local cache and configuration directories; JDK and Scala compiler excluded. | [passed](evidence/records/97b2bf860b4586af83b8d58f/report.json) |
| [sdkman](../assets/catalog/sdkman/recipe.json) | 5.24.0 | shell-installer | ubuntu 22.04 | Initializes SDKMAN script/native CLI, installs the full Temurin JDK through the original Java hook, exercises native current/default and sdk use, then compiles and executes a Java program from a fresh shell without bundle environment variables. | [passed](evidence/records/94f3b7abaa59cb7be4b787ea/report.json) |
| [secretspec](../assets/catalog/secretspec/recipe.json) | 0.21.1 | shell-installer | ubuntu 22.04 | Generate and validate the project configuration JSON schema | [passed](evidence/records/50d4f65c9b958b7045b6ea46/report.json) |
| [sheldon](../assets/catalog/sheldon/recipe.json) | 0.8.5 | shell-installer | ubuntu 22.04 | Lock an empty local plugin configuration and generate shell source | [passed](evidence/records/ebf67ccd1282d5bf540cf521/report.json) |
| [skim](../assets/catalog/skim/recipe.json) | 5.9.0 | shell-installer | ubuntu 22.04 | Filter piped candidates and assert exact match | [passed](evidence/records/865570ffba9bea1578661ee8/report.json) |
| [sql-studio](../assets/catalog/sql-studio/recipe.json) | 0.1.53 | shell-installer | ubuntu 22.04 | Open a local SQLite database and retrieve its web UI over loopback | [passed](evidence/records/0ce12dd712dd9a197c3e4cd5/report.json) |
| [stack](../assets/catalog/stack/recipe.json) | 3.11.1 | shell-installer | ubuntu 22.04 | Generates Bash command completion; GHC and project dependencies excluded. | [passed](evidence/records/428aee037b2d6bc67525aa4b/report.json) |
| [starship](../assets/catalog/starship/recipe.json) | 1.27.0 | shell-installer | ubuntu 26.04 | Generate Bash initialization and validate its syntax. | [passed](evidence/records/a9e642fa3d47c40f3e69beaa/report.json) |
| [svix-cli](../assets/catalog/svix-cli/recipe.json) | 2.9.1 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate syntax | [passed](evidence/records/efb8b141cd6a3ccf11f5e3fe/report.json) |
| [syft](../assets/catalog/syft/recipe.json) | 1.57.0 | shell-installer | ubuntu 22.04 | Generate an SBOM from pinned local Python requirements and assert package/version | [passed](evidence/records/b083357d3d7a661e85c261d1/report.json) |
| [systemfd](../assets/catalog/systemfd/recipe.json) | 0.4.6 | shell-installer | ubuntu 22.04 | Pass a Unix listening socket to a child process | [passed](evidence/records/49c85f5f41d5fce2827db46d/report.json) |
| [task](../assets/catalog/task/recipe.json) | 3.54.0 | shell-installer | ubuntu 26.04 | Run a local Taskfile. | [passed](evidence/records/612880e7f03216d2374b257d/report.json) |
| [tfswitch](../assets/catalog/tfswitch/recipe.json) | 1.20.0 | shell-installer | ubuntu 22.04 | Check accepted and rejected Terraform version constraints from a local project. | [passed](evidence/records/d4b27fb958821b311cb08f1f/report.json) |
| [tilt](../assets/catalog/tilt/recipe.json) | 0.37.8 | shell-installer | ubuntu 22.04 | Generate Bash completions (Docker and Kubernetes runtime excluded) | [passed](evidence/records/62c4e59949319d98a4a9042c/report.json) |
| [trivy](../assets/catalog/trivy/recipe.json) | 0.76.2 | shell-installer | ubuntu 22.04 | Scan a local directory for secrets with database updates disabled | [passed](evidence/records/37be948eba648006359a7613/report.json) |
| [uutils-findutils](../assets/catalog/uutils-findutils/recipe.json) | 0.11.0 | shell-installer | ubuntu 22.04 | Find a local file by name and type | [passed](evidence/records/4cbe7b7ad74ed6b76c0ed9ca/report.json) |
| [uv](../assets/catalog/uv/recipe.json) | 0.13.7 | shell-installer | ubuntu 26.04 | Create a local project without downloading an interpreter. | [passed](evidence/records/2a14f966bd63206e915fbd1a/report.json) |
| [volta](../assets/catalog/volta/recipe.json) | 2.0.2 | shell-installer | ubuntu 22.04 | Generates Bash command completions; manager only, Node runtimes excluded. | [passed](evidence/records/8aa424e2d05ad21899f7d7cf/report.json) |
| [worktrunk](../assets/catalog/worktrunk/recipe.json) | 0.81.0 | shell-installer | ubuntu 22.04 | Generate Bash integration and validate syntax; Git >=2.43 needed for worktree operations | [passed](evidence/records/7560d762497ebb7ac1f7e1fd/report.json) |
| [xh](../assets/catalog/xh/recipe.json) | 0.26.3 | shell-installer | ubuntu 22.04 | Generate an offline JSON POST request | [passed](evidence/records/c3734d919a7c292e1006b13a/report.json) |
| [xmake](../assets/catalog/xmake/recipe.json) | 3.1.2 | shell-installer | ubuntu 22.04 | Builds and executes a local C application; no external package dependencies. | [passed](evidence/records/5217d75d77e998f584bc4357/report.json) |
| [yarn](../assets/catalog/yarn/recipe.json) | 1.22.22 | shell-installer | ubuntu 22.04 | Runs a local package script with bundled Node.js and verifies its numeric output. | [passed](evidence/records/7633f42b7020453d3dca47be/report.json) |
| [zinit](../assets/catalog/zinit/recipe.json) | 3.17.1 | shell-installer | ubuntu 22.04 | Loads a local plugin and invokes the function it defines. | [passed](evidence/records/1bc45da8853bd753f077e9b0/report.json) |
| [zoxide](../assets/catalog/zoxide/recipe.json) | 0.10.0 | shell-installer | ubuntu 22.04 | Add and query a local directory. | [passed](evidence/records/1f82f07f38f3cb5a8c095fb5/report.json) |

## Evidence and reproduction

[coverage.json](coverage.json) records every matching report, image identity, prerequisite, and scope note. [Scope and prerequisites](known-limitations.md) describes functional coverage, installer adaptations, and failed candidates. The index retains historical records; current matches require the recorded code and recipe hashes.

Check the catalog, or reproduce a recorded installation test with a prepared matching image:

```sh
python3 tools/coverage.py --check --minimum 105

python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide
python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz
python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \
  --engine podman --image docker.io/library/ubuntu:22.04 --output dist/zoxide.validation.json
```

The catalog includes converted online shell installers, source installers with their companion trees, and Python installer adaptations. These paths are labeled separately. Version and environment changes require new evidence before entering the verified catalog. Unprepared project dependencies, remote services, other CPU architectures, macOS, Alpine, full systemd behavior, and kernel features are outside the recorded scope unless a row explicitly includes them.
