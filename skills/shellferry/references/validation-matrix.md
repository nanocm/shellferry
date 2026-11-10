# Validation matrix

**105 distinct software packages, 106 recipes.** Each recipe has matching evidence for its current inputs and builder/verifier code. Results describe the exact pinned version, prerequisites, and functional scope below.

Tests run through Podman in WSL2 with `--network none`, user `1000:1000`, a clean HOME, a prefix containing spaces, read-only bundle mounts, and dropped capabilities. The verifier extracts each final archive into a fresh directory, checks integrity, installs, runs functional assertions, and repeats installation. Passing establishes completion without external connectivity. Detecting all attempted native network calls requires separate tracing.

Most new cases use Ubuntu 22.04. Some baseline cases use Ubuntu 26.04. Prepared images include the tools listed in their Containerfiles; target machines must meet each recipe's prerequisites. Python, Rust, or C build tools are present only where declared. Managers, cloud clients, and cluster tools are tested within the local scope stated below.

Installation testing is optional when building a user bundle. These published catalog entries require passing evidence; a new build retains its own status. See [verification modes](verification.md) and [evidence reuse](shared-evidence.md).

| Recipe | Version | Path | Environment | Functional check | Evidence |
| --- | --- | --- | --- | --- | --- |
| [actionlint](../assets/catalog/actionlint/recipe.json) | 1.7.12 | shell-installer | ubuntu 22.04 | Lint a local GitHub Actions workflow without external shellcheck or pyflakes | [passed](evidence/records/8fbc126a48d1a77a6b5bc007/report.json) |
| [air](../assets/catalog/air/recipe.json) | 1.67.4 | shell-installer | ubuntu 22.04 | Generate and inspect an Air project configuration | [passed](evidence/records/c05c79b7f6d0e6e5ac721340/report.json) |
| [arkade](../assets/catalog/arkade/recipe.json) | 0.12.0 | shell-installer | ubuntu 22.04 | Generate Bash completions (no additional application downloads) | [passed](evidence/records/c04312cbc22fe9adbccaa602/report.json) |
| [atuin](../assets/catalog/atuin/recipe.json) | 18.24.5 | shell-installer | ubuntu 26.04 | Complete both installer stages and generate Bash initialization. | [passed](evidence/records/c5b51e02469ed0b4cbfd4e4f/report.json) |
| [babashka](../assets/catalog/babashka/recipe.json) | 1.13.229 | shell-installer | ubuntu 22.04 | Evaluates a Clojure reduction and asserts the result is 10. | [passed](evidence/records/0efbee8cb6fb62e6bbf9fbfa/report.json) |
| [bash-it](../assets/catalog/bash-it/recipe.json) | 3.2.0 | source-installer | ubuntu 22.04 | Loads Bash-it, enables general aliases and lists enabled configuration. | [passed](evidence/records/6a85f03977a46f3621eadf76/report.json) |
| [basher](../assets/catalog/basher/recipe.json) | commit-7c3d238ce263 | shell-installer | ubuntu 22.04 | Links and executes a local package without fetching dependencies. | [passed](evidence/records/71331eb9cf7cb8997cf4c22d/report.json) |
| [bats](../assets/catalog/bats/recipe.json) | 1.14.0 | source-installer | ubuntu 22.04 | Executes a local Bats test and asserts a passing test result. | [passed](evidence/records/e2421149d4f79c9deea2c6de/report.json) |
| [bpkg](../assets/catalog/bpkg/recipe.json) | 1.1.4 | shell-installer | ubuntu 22.04 | Parses a local JSON object with its installed JSON command. | [passed](evidence/records/28ff142a81c291d603f36032/report.json) |
| [bun](../assets/catalog/bun/recipe.json) | 1.4.4 | shell-installer | ubuntu 26.04 | Evaluate a local JavaScript expression. | [passed](evidence/records/f88ca59b91b5ec7c08ccdeee/report.json) |
| [bun-ubuntu22](../assets/catalog/bun-ubuntu22/recipe.json) | 1.4.4 | shell-installer | ubuntu 22.04 | Run JavaScript, check default-prefix installation and generate completions with bundled unzip. | [passed](evidence/records/23c0c71d3a58ce76acbf5356/report.json) |
| [cargo-auditable](../assets/catalog/cargo-auditable/recipe.json) | 0.7.7 | shell-installer | ubuntu 22.04 | Compile and run a local Rust program; assert .dep-v0 metadata | [passed](evidence/records/f8b75fa5901375a9e2efd87e/report.json) |
| [cargo-binstall](../assets/catalog/cargo-binstall/recipe.json) | 1.26.2 | shell-installer | ubuntu 22.04 | Self-install a copied executable and compare bytes | [passed](evidence/records/127eecc180adc68d8afb4725/report.json) |
| [cargo-dist](../assets/catalog/cargo-dist/recipe.json) | 0.34.0 | shell-installer | ubuntu 22.04 | Initialize a local Cargo project and generate a release plan | [passed](evidence/records/da78bef7b5486c2d47140585/report.json) |
| [cargo-insta](../assets/catalog/cargo-insta/recipe.json) | 1.49.0 | shell-installer | ubuntu 22.04 | Render a local snapshot using Cargo metadata | [passed](evidence/records/758bcf45ebf6102ea792968a/report.json) |
| [cargo-leptos](../assets/catalog/cargo-leptos/recipe.json) | 0.3.11 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate syntax | [passed](evidence/records/7edb5964bff27ef6e1c38349/report.json) |
| [cargo-mommy](../assets/catalog/cargo-mommy/recipe.json) | 0.3.1 | shell-installer | ubuntu 22.04 | Build and run a local Rust program through the Cargo wrapper | [passed](evidence/records/95a8079f1900d797f98655c5/report.json) |
| [chezmoi](../assets/catalog/chezmoi/recipe.json) | 2.74.0 | shell-installer | ubuntu 26.04 | Render a template reading the target OS. | [passed](evidence/records/be7f941103258e127a761b3d/report.json) |
| [chsrc](../assets/catalog/chsrc/recipe.json) | 0.2.7 | shell-installer | ubuntu 22.04 | List built-in package-source targets without modifying sources | [passed](evidence/records/5487cd4133b7877a422abc09/report.json) |
| [clj-kondo](../assets/catalog/clj-kondo/recipe.json) | 2026.10.26 | shell-installer | ubuntu 22.04 | Lints a local Clojure namespace and asserts zero errors. | [passed](evidence/records/c4ba38dc86cc1867e2ef00ae/report.json) |
| [clojure-lsp](../assets/catalog/clojure-lsp/recipe.json) | 2026.10.15-11.42.38 | shell-installer | ubuntu 22.04 | Formats a local Clojure source file with external classpath discovery disabled. | [passed](evidence/records/fae4e77e192eed57c401aa43/report.json) |
| [code-server](../assets/catalog/code-server/recipe.json) | 4.145.2 | shell-installer | ubuntu 22.04 | Start the editor on loopback and verify its HTTP health endpoint and workbench using bundled Node. | [passed](evidence/records/b3cd25995088796a1dcc878f/report.json) |
| [dagger](../assets/catalog/dagger/recipe.json) | 0.21.11 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate its syntax; engine execution requires separate images. | [passed](evidence/records/a0d8b1312751537fb2eaa579/report.json) |
| [deno](../assets/catalog/deno/recipe.json) | 2.9.8 | shell-installer | ubuntu 26.04 | Run the local JSR second stage and execute JavaScript. | [passed](evidence/records/039146831a98c11266ac53a0/report.json) |
| [direnv](../assets/catalog/direnv/recipe.json) | 2.38.2 | shell-installer | ubuntu 26.04 | Authorize .envrc and load a local variable. | [passed](evidence/records/7a169941fc3ac8d3aa43c003/report.json) |
| [dolt](../assets/catalog/dolt/recipe.json) | 2.7.2 | shell-installer | ubuntu 22.04 | Initialize a local repository, create a table, and execute SQL. | [passed](evidence/records/97c91b6be534a7e02fdd88f1/report.json) |
| [dotnet](../assets/catalog/dotnet/recipe.json) | 10.0.403 | shell-installer | ubuntu 22.04 | Create, restore without NuGet feeds, compile and run a C# console app; assert LINQ, JSON and ICU culture data | [passed](evidence/records/7e6026f8780748b3b91d36af/report.json) |
| [dprint](../assets/catalog/dprint/recipe.json) | 0.64.3 | shell-installer | ubuntu 22.04 | Formats JSON using a bundled pinned WebAssembly plugin. | [passed](evidence/records/62434f262dfa33b38f1ce172/report.json) |
| [dust](../assets/catalog/dust/recipe.json) | 1.2.7 | shell-installer | ubuntu 22.04 | Measure a local directory and report its file | [passed](evidence/records/cac7a594330a0923d2bb0808/report.json) |
| [elan](../assets/catalog/elan/recipe.json) | 4.2.4 | shell-installer | ubuntu 22.04 | Generates Bash completions; Lean toolchains excluded. | [passed](evidence/records/31ae4aacdcbf470864ce4a82/report.json) |
| [flux](../assets/catalog/flux/recipe.json) | 2.10.0 | shell-installer | ubuntu 22.04 | Export a GitRepository manifest locally (no cluster access) | [passed](evidence/records/5fe77467bca4b40b7154fc17/report.json) |
| [flyctl](../assets/catalog/flyctl/recipe.json) | 0.5.5 | shell-installer | ubuntu 22.04 | Generate Bash completions (no Fly.io authentication or deployment) | [passed](evidence/records/392992bfeb5f5c94c81fd316/report.json) |
| [fnm](../assets/catalog/fnm/recipe.json) | 1.39.0 | shell-installer | ubuntu 26.04 | Generate the manager shell environment; managed Node runtimes are outside scope. | [passed](evidence/records/37d083cea9dc0badb1838b80/report.json) |
| [fzf](../assets/catalog/fzf/recipe.json) | 0.75.0 | shell-installer | ubuntu 22.04 | Filter local input and validate generated Bash initialization. | [passed](evidence/records/8d4bb81bc750868c11a69dae/report.json) |
| [garden](../assets/catalog/garden/recipe.json) | 0.14.20 | shell-installer | ubuntu 22.04 | Create a local Garden project and inspect its configuration | [passed](evidence/records/ee17f039e6efd8a5164357fb/report.json) |
| [ghcup](../assets/catalog/ghcup/recipe.json) | 0.2.6.2 | shell-installer | ubuntu 22.04 | Lists GHC releases from pinned local metadata; Haskell toolchains excluded. | [passed](evidence/records/08d4cd5f13529778ef08184c/report.json) |
| [git-standup](../assets/catalog/git-standup/recipe.json) | 2.3.2 | source-installer | ubuntu 22.04 | Report a commit from a local Git repository | [passed](evidence/records/daf513fbc2e9b1151514e0b8/report.json) |
| [golangci-lint](../assets/catalog/golangci-lint/recipe.json) | 2.15.0 | shell-installer | ubuntu 22.04 | Format Go source supplied on standard input | [passed](evidence/records/896bec78cf4e538f171bfced/report.json) |
| [google-cloud-cli](../assets/catalog/google-cloud-cli/recipe.json) | 592.0.0 | shell-installer | ubuntu 22.04 | Run the official archive installer with bundled Python; verify profile/completion, local configuration and component listing | [passed](evidence/records/39bcab30d2fcc7dfa01b038f/report.json) |
| [goose](../assets/catalog/goose/recipe.json) | 3.29.0 | shell-installer | ubuntu 22.04 | Apply a SQLite schema migration and inspect its applied status | [passed](evidence/records/8e93a53b89337fddb9f1500f/report.json) |
| [goreleaser](../assets/catalog/goreleaser/recipe.json) | 2.20.0 | shell-installer | ubuntu 22.04 | Generate and inspect a GoReleaser project configuration | [passed](evidence/records/5a28b67f3355fb6851b253d7/report.json) |
| [grype](../assets/catalog/grype/recipe.json) | 0.121.2 | shell-installer | ubuntu 22.04 | Render effective configuration (vulnerability database and scanning excluded) | [passed](evidence/records/65921d2f5b0a5dc19901dd6a/report.json) |
| [helm](../assets/catalog/helm/recipe.json) | 3.22.1 | shell-installer | ubuntu 26.04 | Verify the release, inspect the version and Helm environment. | [passed](evidence/records/017cb2e1a123d2f44d603dde/report.json) |
| [infracost](../assets/catalog/infracost/recipe.json) | 0.10.47 | shell-installer | ubuntu 22.04 | Set and read local currency configuration (pricing API excluded) | [passed](evidence/records/65e037655fce7cc7b8799a15/report.json) |
| [istioctl](../assets/catalog/istioctl/recipe.json) | 1.31.4 | shell-installer | ubuntu 22.04 | Render the default Istio manifest locally (no cluster installation) | [passed](evidence/records/5b5e108bbdef53fc4db19846/report.json) |
| [jet](../assets/catalog/jet/recipe.json) | 0.7.27 | shell-installer | ubuntu 22.04 | Converts local JSON to keywordized EDN and checks the value. | [passed](evidence/records/e0d501e1708606cae2cbe04e/report.json) |
| [jfrog-cli](../assets/catalog/jfrog-cli/recipe.json) | 2.131.0 | shell-installer | ubuntu 22.04 | Collect local build environment metadata (no Artifactory server) | [passed](evidence/records/3e937a214c23fa79e841f8d5/report.json) |
| [just](../assets/catalog/just/recipe.json) | 1.59.0 | shell-installer | ubuntu 26.04 | Execute a local justfile task and preserve default overwrite protection. | [passed](evidence/records/07aa625a4e02ad1ee0f45e4f/report.json) |
| [k0s](../assets/catalog/k0s/recipe.json) | 1.37.2+k0s.1 | shell-installer | ubuntu 22.04 | Generate a local cluster configuration (no cluster startup) | [passed](evidence/records/fe0906596266fc216951e8de/report.json) |
| [k3d](../assets/catalog/k3d/recipe.json) | 5.9.0 | shell-installer | ubuntu 22.04 | Generate and inspect a local k3d cluster configuration (no Docker cluster) | [passed](evidence/records/f99156b3a6d75001ba1df6b9/report.json) |
| [k3sup](../assets/catalog/k3sup/recipe.json) | 0.13.14 | shell-installer | ubuntu 22.04 | Generate Bash completions (no remote Kubernetes deployment) | [passed](evidence/records/8f79c6795ade2cae5418d29c/report.json) |
| [kubescape](../assets/catalog/kubescape/recipe.json) | 4.0.20 | shell-installer | ubuntu 22.04 | Generate Bash completions (cluster scans and control downloads excluded) | [passed](evidence/records/fd6a36a0bb131c5ed405d5e9/report.json) |
| [kustomize](../assets/catalog/kustomize/recipe.json) | 5.8.3 | shell-installer | ubuntu 22.04 | Build a local ConfigMap manifest with a name prefix | [passed](evidence/records/6c0be2276790432363977f86/report.json) |
| [linkerd](../assets/catalog/linkerd/recipe.json) | edge-26.11.1 | shell-installer | ubuntu 22.04 | Add Linkerd injection annotations to a local manifest without cluster access | [passed](evidence/records/ef27510f1c0270f7700fd0f2/report.json) |
| [mcfly](../assets/catalog/mcfly/recipe.json) | 0.9.4 | shell-installer | ubuntu 22.04 | Generate Bash initialization and validate syntax | [passed](evidence/records/e7ab807a634ece938bf3106b/report.json) |
| [micromamba](../assets/catalog/micromamba/recipe.json) | 2.10.0 | shell-installer | ubuntu 22.04 | Creates an empty offline environment and runs a local command within it. | [passed](evidence/records/ca6aa77d0b443139754c4cde/report.json) |
| [minijinja-cli](../assets/catalog/minijinja-cli/recipe.json) | 3.1.0 | shell-installer | ubuntu 22.04 | Render a template with local JSON data | [passed](evidence/records/c9a9a6e421af79c394dd7eae/report.json) |
| [mise](../assets/catalog/mise/recipe.json) | 2026.11.5 | shell-installer | ubuntu 26.04 | Run a local command through the manager; managed runtimes are outside scope. | [passed](evidence/records/43e857fcba8b29a579f508f4/report.json) |
| [near-cli](../assets/catalog/near-cli/recipe.json) | 0.31.1 | shell-installer | ubuntu 22.04 | Create and read local connection configuration in offline mode | [passed](evidence/records/0e4bfacf252ea207fe24c7cf/report.json) |
| [nvm](../assets/catalog/nvm/recipe.json) | 0.40.3-node26.13.0 | shell-installer | ubuntu 26.04 | Install Node 26, execute JavaScript and npm with the bundled Ubuntu library. | [passed](evidence/records/0e6c8f86de75da3b5e61a217/report.json) |
| [oh-my-posh](../assets/catalog/oh-my-posh/recipe.json) | 32.0.0 | shell-installer | ubuntu 26.04 | Load a bundled theme and generate shell initialization. | [passed](evidence/records/1abc3625d556b42a23c0b46e/report.json) |
| [oh-my-zsh](../assets/catalog/oh-my-zsh/recipe.json) | commit-cca3bdfbef8c | shell-installer | ubuntu 22.04 | Loads the Git plugin and checks the gst alias. | [passed](evidence/records/afd7a28cab02ae7528c5933c/report.json) |
| [opam](../assets/catalog/opam/recipe.json) | 2.6.1 | shell-installer | ubuntu 22.04 | Lints a complete local .opam package definition without a repository or compiler. | [passed](evidence/records/7b387487dce433c2bddbb1bf/report.json) |
| [opentofu](../assets/catalog/opentofu/recipe.json) | 1.13.9 | shell-installer | ubuntu 22.04 | Format and validate local HCL without external providers; retain GPG verification | [passed](evidence/records/9c0b70f64efcc84d186e4861/report.json) |
| [oranda](../assets/catalog/oranda/recipe.json) | 0.6.5 | shell-installer | ubuntu 22.04 | Serve and retrieve a local HTML page over loopback | [passed](evidence/records/d210e6f38568d64809addb7f/report.json) |
| [pdm](../assets/catalog/pdm/recipe.json) | 2.29.7 | python-installer | ubuntu 22.04 | Sets and reads local manager configuration and generates completions; offline CPython 3.10 wheelhouse. | [passed](evidence/records/a0db76b3a12cd7e35d602a4f/report.json) |
| [perlbrew](../assets/catalog/perlbrew/recipe.json) | 1.02 | shell-installer | ubuntu 22.04 | Initializes shell integration, prints environment and runs bundled patchperl. | [passed](evidence/records/48c57d8629d2d34d00c79646/report.json) |
| [pixi](../assets/catalog/pixi/recipe.json) | 0.84.1 | shell-installer | ubuntu 26.04 | Initialize a local project; Conda environments are outside scope. | [passed](evidence/records/81facf74d3a9279a4604c7a4/report.json) |
| [pnpm](../assets/catalog/pnpm/recipe.json) | 12.18.0 | shell-installer | ubuntu 22.04 | Verify upstream signatures and execute local package scripts. | [passed](evidence/records/1e1231c631dfb50451d5d1e1/report.json) |
| [poetry](../assets/catalog/poetry/recipe.json) | 2.5.1 | python-installer | ubuntu 22.04 | Creates a local project and validates its pyproject.toml; offline CPython 3.10 wheelhouse. | [passed](evidence/records/faa843d0f0da218b80f5a591/report.json) |
| [porter](../assets/catalog/porter/recipe.json) | 1.6.1 | shell-installer | ubuntu 22.04 | Install the exec mixin from a temporary loopback mirror and create a local project | [passed](evidence/records/2a3946abe017accbe8924279/report.json) |
| [posit-air](../assets/catalog/posit-air/recipe.json) | 0.13.0 | shell-installer | ubuntu 22.04 | Format a local R source file | [passed](evidence/records/e169504aec87a99080e6b9e8/report.json) |
| [prek](../assets/catalog/prek/recipe.json) | 0.5.10 | shell-installer | ubuntu 22.04 | Validate a local pre-commit configuration | [passed](evidence/records/2676bbd78defec18bb6014eb/report.json) |
| [pulumi](../assets/catalog/pulumi/recipe.json) | 3.274.1 | shell-installer | ubuntu 22.04 | Install the random provider and run a local YAML resource lifecycle with a file backend; verify completion | [passed](evidence/records/f210cce8bcda813001260c13/report.json) |
| [pyenv](../assets/catalog/pyenv/recipe.json) | 2.8.14 | shell-installer | ubuntu 22.04 | Sets and reads a local system-Python selection, then regenerates shims. | [passed](evidence/records/a22668aa08aebaec8bad2147/report.json) |
| [railway](../assets/catalog/railway/recipe.json) | 5.71.0 | shell-installer | ubuntu 22.04 | Generate Bash completions (cloud deployment excluded) | [passed](evidence/records/b26b22123a553ed659bee64a/report.json) |
| [rbenv](../assets/catalog/rbenv/recipe.json) | 1.3.2 | shell-installer | ubuntu 22.04 | Generates shell initialization and rebuilds the shim directory; Ruby excluded. | [passed](evidence/records/6b209575e043e2fe90fa023d/report.json) |
| [rclone](../assets/catalog/rclone/recipe.json) | 1.76.0 | shell-installer | ubuntu 26.04 | Copy and compare local files. | [passed](evidence/records/76ec1b7812865e6fa42e7e7a/report.json) |
| [rqlite](../assets/catalog/rqlite/recipe.json) | 10.6.6 | shell-installer | ubuntu 22.04 | Start a local node and query SQLite over container loopback. | [passed](evidence/records/ab80d1b014eafc6ad111401f/report.json) |
| [ruff](../assets/catalog/ruff/recipe.json) | 0.17.4 | shell-installer | ubuntu 26.04 | Lint a local Python file. | [passed](evidence/records/f87c850ce4b874018c79be4f/report.json) |
| [rustup](../assets/catalog/rustup/recipe.json) | 1.29.3-rust1.90.0 | shell-installer | ubuntu 26.04 | Install the Rust 1.90 toolchain and compile metadata. | [passed](evidence/records/ca8bba143d830cb28dabd28a/report.json) |
| [samply](../assets/catalog/samply/recipe.json) | 0.13.1 | shell-installer | ubuntu 22.04 | Load a synthetic profile and retrieve its JSON over loopback | [passed](evidence/records/657c13b1521bb1e1b40341d0/report.json) |
| [scala-cli](../assets/catalog/scala-cli/recipe.json) | 1.18.0 | shell-installer | ubuntu 22.04 | Discovers local cache and configuration directories; JDK and Scala compiler excluded. | [passed](evidence/records/25a07084b2e016df74bc017a/report.json) |
| [sdkman](../assets/catalog/sdkman/recipe.json) | 5.24.0 | shell-installer | ubuntu 22.04 | Initializes SDKMAN script/native CLI, installs the full Temurin JDK through the original Java hook, exercises native current/default and sdk use, then compiles and executes a Java program from a fresh shell without bundle environment variables. | [passed](evidence/records/3025d2b886821c4145e6a973/report.json) |
| [secretspec](../assets/catalog/secretspec/recipe.json) | 0.21.1 | shell-installer | ubuntu 22.04 | Generate and validate the project configuration JSON schema | [passed](evidence/records/4761964c1f6f7ef1ec3a053a/report.json) |
| [sheldon](../assets/catalog/sheldon/recipe.json) | 0.8.5 | shell-installer | ubuntu 22.04 | Lock an empty local plugin configuration and generate shell source | [passed](evidence/records/7a453b986b54e670a7c26102/report.json) |
| [skim](../assets/catalog/skim/recipe.json) | 5.9.0 | shell-installer | ubuntu 22.04 | Filter piped candidates and assert exact match | [passed](evidence/records/806756b504f65db6533ecf86/report.json) |
| [sql-studio](../assets/catalog/sql-studio/recipe.json) | 0.1.53 | shell-installer | ubuntu 22.04 | Open a local SQLite database and retrieve its web UI over loopback | [passed](evidence/records/9720a9181e8761a9bd10ecb3/report.json) |
| [stack](../assets/catalog/stack/recipe.json) | 3.11.1 | shell-installer | ubuntu 22.04 | Generates Bash command completion; GHC and project dependencies excluded. | [passed](evidence/records/d7224e953c018a770e2121bc/report.json) |
| [starship](../assets/catalog/starship/recipe.json) | 1.27.0 | shell-installer | ubuntu 26.04 | Generate Bash initialization and validate its syntax. | [passed](evidence/records/b266a9199d4b2eb5b3c683d1/report.json) |
| [svix-cli](../assets/catalog/svix-cli/recipe.json) | 2.9.1 | shell-installer | ubuntu 22.04 | Generate Bash completion and validate syntax | [passed](evidence/records/d4d62a9d11eb4bc0d61d511c/report.json) |
| [syft](../assets/catalog/syft/recipe.json) | 1.57.0 | shell-installer | ubuntu 22.04 | Generate an SBOM from pinned local Python requirements and assert package/version | [passed](evidence/records/61245211b8a75bc5117ba707/report.json) |
| [systemfd](../assets/catalog/systemfd/recipe.json) | 0.4.6 | shell-installer | ubuntu 22.04 | Pass a Unix listening socket to a child process | [passed](evidence/records/90c026639661ef24c5edf7a6/report.json) |
| [task](../assets/catalog/task/recipe.json) | 3.54.0 | shell-installer | ubuntu 26.04 | Run a local Taskfile. | [passed](evidence/records/6c95e528d4a15e71636b2a2a/report.json) |
| [tfswitch](../assets/catalog/tfswitch/recipe.json) | 1.20.0 | shell-installer | ubuntu 22.04 | Check accepted and rejected Terraform version constraints from a local project. | [passed](evidence/records/36d64c5647955a4c6a8dcac8/report.json) |
| [tilt](../assets/catalog/tilt/recipe.json) | 0.37.8 | shell-installer | ubuntu 22.04 | Generate Bash completions (Docker and Kubernetes runtime excluded) | [passed](evidence/records/3df5eead5c44e8ccfb0f8eca/report.json) |
| [trivy](../assets/catalog/trivy/recipe.json) | 0.76.2 | shell-installer | ubuntu 22.04 | Scan a local directory for secrets with database updates disabled | [passed](evidence/records/2bfc97108432aa784703afb5/report.json) |
| [uutils-findutils](../assets/catalog/uutils-findutils/recipe.json) | 0.11.0 | shell-installer | ubuntu 22.04 | Find a local file by name and type | [passed](evidence/records/803e2f26a8dbb1b19009eeb0/report.json) |
| [uv](../assets/catalog/uv/recipe.json) | 0.13.7 | shell-installer | ubuntu 26.04 | Create a local project without downloading an interpreter. | [passed](evidence/records/2cd5f9d1cc609500cbf34329/report.json) |
| [volta](../assets/catalog/volta/recipe.json) | 2.0.2 | shell-installer | ubuntu 22.04 | Generates Bash command completions; manager only, Node runtimes excluded. | [passed](evidence/records/88d4ce17fa53dc6cba9dae38/report.json) |
| [worktrunk](../assets/catalog/worktrunk/recipe.json) | 0.81.0 | shell-installer | ubuntu 22.04 | Generate Bash integration and validate syntax; Git >=2.43 needed for worktree operations | [passed](evidence/records/641ff1a6914a7f3e9973b71d/report.json) |
| [xh](../assets/catalog/xh/recipe.json) | 0.26.3 | shell-installer | ubuntu 22.04 | Generate an offline JSON POST request | [passed](evidence/records/ce6594ade9f7aec76ce4421e/report.json) |
| [xmake](../assets/catalog/xmake/recipe.json) | 3.1.2 | shell-installer | ubuntu 22.04 | Builds and executes a local C application; no external package dependencies. | [passed](evidence/records/44620e35d5807e637f0f3820/report.json) |
| [yarn](../assets/catalog/yarn/recipe.json) | 1.22.22 | shell-installer | ubuntu 22.04 | Runs a local package script with bundled Node.js and verifies its numeric output. | [passed](evidence/records/37730aa13f69c6770d5a7191/report.json) |
| [zinit](../assets/catalog/zinit/recipe.json) | 3.17.1 | shell-installer | ubuntu 22.04 | Loads a local plugin and invokes the function it defines. | [passed](evidence/records/945404f5289fa16acb6e763d/report.json) |
| [zoxide](../assets/catalog/zoxide/recipe.json) | 0.10.0 | shell-installer | ubuntu 22.04 | Add and query a local directory. | [passed](evidence/records/cdce6bcf23cf34d15bcac80d/report.json) |

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
